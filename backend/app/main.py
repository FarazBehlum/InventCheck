import asyncio
import json
import logging
from contextlib import asynccontextmanager
from datetime import UTC, timedelta
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import delete, select, text

from app.adapters import adapters as make_adapters
from app.adapters.demo import DEMO_ZIPS
from app.config import Settings
from app.database.models import (
    Alert,
    Base,
    PriceCheck,
    Product,
    Store,
    Watch,
    now,
)
from app.database.session import database, purge_expired
from app.schemas import (
    RETAILER_IDS,
    AlertPatch,
    ProductOut,
    Radius,
    RetailerId,
    SearchOut,
    StoreOut,
    WatchInput,
    WatchPatch,
)
from app.services.notifications import NotificationService
from app.services.search import SearchService
from app.services.seed import seed
from app.utils.location import distance_miles, locations, resolve_zip
from app.utils.matching import discount


class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps(
            {
                "level": record.levelname,
                "event": record.getMessage(),
                "retailer": getattr(record, "retailer", None),
                "duration_ms": getattr(record, "duration_ms", None),
            }
        )


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("inventcheck")
logger.handlers = [handler]
logger.setLevel(logging.INFO)


def utc(value):
    return value.replace(tzinfo=UTC) if value and value.tzinfo is None else value


def record(row):
    values = {}
    for column in row.__table__.columns:
        value = getattr(row, column.name)
        values[column.name] = utc(value) if hasattr(value, "tzinfo") else value
    return values


def create_app(settings=None, migrate=True):
    settings = settings or Settings()
    engine, Session = database(settings.database_url)
    mode = "demo" if settings.demo_mode else "live"
    providers = make_adapters(settings.demo_mode)
    search_service = SearchService(settings, providers)
    notifications = NotificationService()
    refresh_lock = asyncio.Lock()

    @asynccontextmanager
    async def lifespan(app):
        if migrate:
            config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
            config.set_main_option(
                "script_location", str(Path(__file__).resolve().parents[1] / "migrations")
            )
            config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))
            command.upgrade(config, "head")
        else:
            Base.metadata.create_all(engine)
        with Session() as session:
            purge_expired(session)
            seed(session, providers, settings.demo_mode)
        yield
        engine.dispose()

    app = FastAPI(title="InventCheck", version="0.1.0", lifespan=lifespan)
    app.state.session_factory = Session
    app.state.search = search_service
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Content-Type"],
    )

    def db():
        with Session() as session:
            purge_expired(session)
            yield session

    def product_or_404(session, product_id):
        product = session.get(Product, product_id)
        if not product or product.provenance != mode:
            raise HTTPException(404, "Product not found in the current data mode.")
        return product

    def watch_or_404(session, watch_id):
        item = session.get(Watch, watch_id)
        if not item or item.provenance != mode:
            raise HTTPException(404, "Watchlist item not found.")
        return item

    @app.get("/api/health")
    def health(session=Depends(db)):
        session.execute(text("SELECT 1"))
        return {"status": "ok", "mode": mode}

    @app.get("/api/status")
    def status():
        return {
            "mode": mode,
            "demo_zips": DEMO_ZIPS,
            "zip_count": len(locations()),
            "cache_seconds": settings.cache_seconds,
            "retailers": [
                {
                    "id": a.id,
                    "name": a.name,
                    "website": a.website,
                    "status": "demo" if settings.demo_mode else "unavailable",
                    "store_prices": settings.demo_mode,
                    "inventory_quantity": settings.demo_mode,
                    "live_verified": False,
                }
                for a in providers.values()
            ],
            "monitoring": "Manual checks only. No scheduled monitoring.",
        }

    @app.get("/api/search", response_model=SearchOut)
    async def search(
        q: str = Query(min_length=1, max_length=160),
        zip_code: str = Query(pattern=r"^\d{5}$"),
        radius: Radius = 25,
        retailers: list[RetailerId] = Query(default=RETAILER_IDS, min_length=1, max_length=5),
        session=Depends(db),
    ):
        if not q.strip():
            raise HTTPException(422, "Enter a product name or identifier.")
        return await search_service.search(
            q.strip(), resolve_zip(zip_code), radius, list(dict.fromkeys(retailers)), session
        )

    @app.get("/api/products/{product_id}", response_model=ProductOut)
    def product(product_id: str, session=Depends(db)):
        return product_or_404(session, product_id)

    @app.get("/api/products/{product_id}/history")
    def history(product_id: str, session=Depends(db)):
        product_or_404(session, product_id)
        rows = session.execute(
            select(PriceCheck, Store)
            .join(Store, Store.id == PriceCheck.store_id)
            .where(PriceCheck.product_id == product_id, PriceCheck.provenance == mode)
            .order_by(PriceCheck.observed_at)
        ).all()
        return [
            {
                **record(check),
                "retailer_id": store.retailer_id,
                "store_name": store.name,
                "zip_code": store.zip_code,
            }
            for check, store in rows
        ]

    @app.get("/api/products/{product_id}/prices")
    def prices(product_id: str, session=Depends(db)):
        product_or_404(session, product_id)
        rows = session.execute(
            select(PriceCheck, Store)
            .join(Store, Store.id == PriceCheck.store_id)
            .where(
                PriceCheck.product_id == product_id,
                PriceCheck.provenance == mode,
                PriceCheck.observed_at
                >= now() - timedelta(seconds=max(settings.cache_seconds, 60)),
            )
            .order_by(PriceCheck.observed_at.desc())
        ).all()
        found = {}
        for check, store in rows:
            if store.id not in found:
                found[store.id] = {
                    **record(check),
                    "retailer_id": store.retailer_id,
                    "store_name": store.name,
                    "zip_code": store.zip_code,
                    "discount": discount(check.price, check.regular_price),
                }
        return list(found.values())

    @app.get("/api/stores", response_model=list[StoreOut])
    def stores(
        zip_code: str = Query(pattern=r"^\d{5}$"),
        radius: Radius = 25,
        retailers: list[RetailerId] = Query(default=RETAILER_IDS),
        session=Depends(db),
    ):
        location = resolve_zip(zip_code)
        rows = session.scalars(
            select(Store).where(Store.provenance == mode, Store.retailer_id.in_(retailers))
        ).all()
        return [
            s
            for s in rows
            if distance_miles(location.latitude, location.longitude, s.latitude, s.longitude)
            <= radius
        ]

    def watch_record(session, watch):
        return {
            **record(watch),
            "product": ProductOut.model_validate(product_or_404(session, watch.product_id)),
        }

    @app.get("/api/watchlist")
    def watches(session=Depends(db)):
        return [
            watch_record(session, item)
            for item in session.scalars(
                select(Watch).where(Watch.provenance == mode).order_by(Watch.created_at.desc())
            )
        ]

    @app.post("/api/watchlist", status_code=201)
    def save_watch(body: WatchInput, session=Depends(db)):
        product_or_404(session, body.product_id)
        resolve_zip(body.zip_code)
        if len(session.scalars(select(Watch.id).where(Watch.provenance == mode)).all()) >= 100:
            raise HTTPException(422, "The local MVP supports up to 100 saved products.")
        item = Watch(**body.model_dump(), provenance=mode)
        session.add(item)
        session.commit()
        return watch_record(session, item)

    @app.patch("/api/watchlist/{watch_id}")
    def update_watch(watch_id: int, body: WatchPatch, session=Depends(db)):
        item = watch_or_404(session, watch_id)
        if body.zip_code:
            resolve_zip(body.zip_code)
        for key, value in body.model_dump(exclude_unset=True).items():
            setattr(item, key, list(dict.fromkeys(value)) if key == "retailers" else value)
        item.check_status = "Settings changed; check again"
        session.commit()
        return watch_record(session, item)

    @app.delete("/api/watchlist/{watch_id}", status_code=204)
    def remove_watch(watch_id: int, session=Depends(db)):
        item = watch_or_404(session, watch_id)
        session.execute(delete(Alert).where(Alert.watchlist_id == watch_id))
        session.delete(item)
        session.commit()
        return Response(status_code=204)

    @app.post("/api/watchlist/refresh")
    async def refresh(session=Depends(db)):
        async with refresh_lock:
            watches = session.scalars(select(Watch).where(Watch.provenance == mode)).all()
            created = 0
            for item in watches:
                item.last_attempted_at = now()
                product = product_or_404(session, item.product_id)
                result = await search_service.search(
                    product.upc, resolve_zip(item.zip_code), item.radius, item.retailers, session
                )
                matching = [offer for offer in result.offers if offer.product.id == item.product_id]
                successes = [p for p in result.providers if p.status == "completed"]
                if successes:
                    item.last_successful_at = max(
                        (offer.observed_at for offer in matching), default=item.last_successful_at
                    )
                item.check_status = (
                    "Checked"
                    if len(successes) == len(result.providers)
                    else ("Partially checked" if successes else "Unavailable")
                )
                if successes and not matching:
                    item.check_status = "No nearby offers"
                created += notifications.evaluate(session, item, matching)
            session.commit()
            return {"checked": len(watches), "new_alerts": created}

    @app.get("/api/alerts")
    def alerts(session=Depends(db)):
        return [
            record(item)
            for item in session.scalars(
                select(Alert)
                .where(Alert.provenance == mode, Alert.dismissed.is_(False))
                .order_by(Alert.created_at.desc())
            )
        ]

    @app.patch("/api/alerts/{alert_id}")
    def update_alert(alert_id: int, body: AlertPatch, session=Depends(db)):
        item = session.get(Alert, alert_id)
        if not item or item.provenance != mode:
            raise HTTPException(404, "Alert not found.")
        for key, value in body.model_dump(exclude_none=True).items():
            setattr(item, key, value)
        session.commit()
        return record(item)

    return app


app = create_app()
