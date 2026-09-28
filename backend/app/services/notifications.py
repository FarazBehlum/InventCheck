from sqlalchemy import select

from app.database.models import Alert


class NotificationService:
    """In-app sink; future delivery channels can consume qualifying observations here."""

    def evaluate(self, session, watch, offers):
        created = 0
        for offer in offers:
            if (
                offer.product.id != watch.product_id
                or offer.price is None
                or offer.price > watch.target_price
            ):
                continue
            if offer.inventory_status not in ("In stock", "Limited stock"):
                continue
            key = f"{watch.id}:{offer.id}:{offer.price:.2f}"
            if session.scalar(select(Alert.id).where(Alert.dedup_key == key)) is not None:
                continue
            session.add(
                Alert(
                    watchlist_id=watch.id,
                    dedup_key=key,
                    provenance=offer.provenance,
                    expires_at=offer.expires_at,
                    message=f"{offer.product.name}: ${offer.price:.2f} at {offer.store.name} (target ${watch.target_price:.2f}).",
                )
            )
            session.flush()
            created += 1
        session.commit()
        return created
