import asyncio
import logging
import time
from datetime import timedelta

from sqlalchemy import select

from app.adapters.base import ProviderError
from app.database.models import PriceCheck
from app.schemas import Offer, ProviderStatus, SearchOut
from app.utils.location import distance_miles
from app.utils.matching import discount

logger = logging.getLogger("inventcheck")


class SearchService:
    def __init__(self, settings, adapters):
        self.settings, self.adapters = settings, adapters
        self.cache = {}
        self.lock = asyncio.Lock()
        self.mode = "demo" if settings.demo_mode else "live"

    async def provider(self, adapter, query, location, radius):
        matches = await adapter.search_product(query)
        stores = await adapter.get_nearby_stores(location, radius)
        offers = []
        for match in matches:
            for store in stores:
                price, inventory = await asyncio.gather(
                    adapter.get_store_price(match.product.id, store.id),
                    adapter.get_inventory(match.product.id, store.id),
                )
                if adapter.provenance == "live" and adapter.retention_seconds is None:
                    raise ProviderError(
                        "unavailable", "Live source retention has not been verified."
                    )
                expiry = (
                    price.observed_at + timedelta(seconds=adapter.retention_seconds)
                    if adapter.retention_seconds is not None
                    else None
                )
                offers.append(
                    Offer(
                        id=f"{match.product.id}:{store.id}",
                        product=match.product,
                        retailer_id=adapter.id,
                        retailer_name=adapter.name,
                        store=store,
                        price=price.price,
                        regular_price=price.regular_price,
                        discount=discount(price.price, price.regular_price),
                        inventory_status=inventory.status,
                        inventory_quantity=inventory.quantity,
                        observed_at=price.observed_at,
                        expires_at=expiry,
                        distance=round(
                            distance_miles(
                                location.latitude,
                                location.longitude,
                                store.latitude,
                                store.longitude,
                            ),
                            2,
                        ),
                        confidence=match.confidence,
                        match_reason=match.reason,
                        provenance=adapter.provenance,
                    )
                )
        message = (
            f"{len(offers)} offers"
            if offers
            else (
                "No matching products."
                if not matches
                else "No nearby demo stores. Try ZIP 53703, 10001, or another demo city."
            )
        )
        return offers, ProviderStatus(retailer_id=adapter.id, status="completed", message=message)

    async def one(self, adapter, query, location, radius):
        key = (self.mode, adapter.id, query.strip().lower(), location.zip_code, radius)
        cached = self.cache.get(key)
        if cached and time.monotonic() < cached[0]:
            return [offer.model_copy(update={"cached": True}) for offer in cached[1]], cached[2]
        started = time.monotonic()
        try:
            result = await asyncio.wait_for(
                self.provider(adapter, query, location, radius), self.settings.request_timeout
            )
            ttl = (
                min(self.settings.cache_seconds, adapter.retention_seconds)
                if adapter.retention_seconds is not None
                else self.settings.cache_seconds
            )
            if len(self.cache) >= 256:
                self.cache.pop(next(iter(self.cache)))
            self.cache[key] = (time.monotonic() + ttl, *result)
            return result
        except TimeoutError:
            status, message = "timeout", "Retailer did not respond in time. Try again later."
        except ProviderError as exc:
            status, message = exc.status, exc.message
        except Exception:
            status, message = "malformed_response", "Retailer response could not be processed."
            logger.warning("provider_response_failed", extra={"retailer": adapter.id})
        finally:
            logger.info(
                "provider_check",
                extra={
                    "retailer": adapter.id,
                    "duration_ms": round((time.monotonic() - started) * 1000),
                },
            )
        return [], ProviderStatus(retailer_id=adapter.id, status=status, message=message)

    async def search(self, query, location, radius, retailer_ids, session):
        # Single-user request serialization protects observation/cache writes; providers run concurrently.
        async with self.lock:
            results = await asyncio.gather(
                *(self.one(self.adapters[key], query, location, radius) for key in retailer_ids)
            )
            offers = [offer for group, _ in results for offer in group]
            for offer in offers:
                if offer.cached:
                    continue
                listing_id = f"{offer.retailer_id}:{offer.product.id}"
                existing = session.scalar(
                    select(PriceCheck.id).where(
                        PriceCheck.listing_id == listing_id,
                        PriceCheck.store_id == offer.store.id,
                        PriceCheck.observed_at == offer.observed_at,
                    )
                )
                if existing is None:
                    session.add(
                        PriceCheck(
                            product_id=offer.product.id,
                            listing_id=listing_id,
                            store_id=offer.store.id,
                            price=offer.price,
                            regular_price=offer.regular_price,
                            inventory_status=offer.inventory_status,
                            inventory_quantity=offer.inventory_quantity,
                            observed_at=offer.observed_at,
                            expires_at=offer.expires_at,
                            provenance=offer.provenance,
                        )
                    )
            session.commit()
            return SearchOut(
                query=query,
                location=location,
                radius=radius,
                mode=self.mode,
                offers=offers,
                providers=[status for _, status in results],
            )
