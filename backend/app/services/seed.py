from datetime import timedelta
from decimal import Decimal

from sqlalchemy import select

from app.adapters.demo import BASE_PRICES, PRODUCTS, REGULAR_PRICES, RETAILERS
from app.database.models import Listing, PriceCheck, Product, Retailer, Store, now


def seed(session, adapters, demo_mode):
    for identifier, name, website in RETAILERS:
        if not session.get(Retailer, identifier):
            session.add(Retailer(id=identifier, name=name, website=website))
    session.flush()
    if not demo_mode or session.scalar(
        select(Product.id).where(Product.provenance == "demo").limit(1)
    ):
        session.commit()
        return
    for product in PRODUCTS:
        session.add(Product(**product.model_dump()))
    session.flush()
    timestamp = now().replace(hour=12, minute=0, second=0, microsecond=0)
    for adapter in adapters.values():
        for store in adapter.stores:
            session.add(Store(**store.model_dump()))
        for product in PRODUCTS:
            session.add(
                Listing(
                    id=f"{adapter.id}:{product.id}",
                    product_id=product.id,
                    retailer_id=adapter.id,
                    sku=adapter.sku(product.id),
                    product_url=None,
                )
            )
        session.flush()
        # History is synthetic and labeled demo, never backdated live observations.
        for p_index, product in enumerate(PRODUCTS):
            for store in adapter.stores:
                for day in (28, 21, 14, 7, 3, 1):
                    value = BASE_PRICES[p_index] + Decimal(
                        adapter.index * 5 + int(store.id[-1]) * 3 + day // 3
                    )
                    session.add(
                        PriceCheck(
                            product_id=product.id,
                            listing_id=f"{adapter.id}:{product.id}",
                            store_id=store.id,
                            price=value,
                            regular_price=REGULAR_PRICES[p_index],
                            inventory_status="Unknown",
                            inventory_quantity=None,
                            observed_at=timestamp - timedelta(days=day),
                            provenance="demo",
                            expires_at=None,
                        )
                    )
    session.commit()
