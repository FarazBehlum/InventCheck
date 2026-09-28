from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import JSON, DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def now():
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    brand: Mapped[str] = mapped_column(String(80))
    model_number: Mapped[str] = mapped_column(String(80))
    upc: Mapped[str] = mapped_column(String(14))
    gtin: Mapped[str] = mapped_column(String(14))
    image_url: Mapped[str] = mapped_column(String(300))
    provenance: Mapped[str] = mapped_column(String(10), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Retailer(Base):
    __tablename__ = "retailers"
    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    website: Mapped[str] = mapped_column(String(200))


class Store(Base):
    __tablename__ = "stores"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    retailer_id: Mapped[str] = mapped_column(ForeignKey("retailers.id"))
    store_identifier: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(150))
    address: Mapped[str] = mapped_column(String(200))
    city: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(2))
    zip_code: Mapped[str] = mapped_column(String(5))
    latitude: Mapped[float]
    longitude: Mapped[float]
    provenance: Mapped[str] = mapped_column(String(10))
    __table_args__ = (UniqueConstraint("retailer_id", "store_identifier", "provenance"),)


class Listing(Base):
    __tablename__ = "retailer_listings"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    retailer_id: Mapped[str] = mapped_column(ForeignKey("retailers.id"))
    sku: Mapped[str] = mapped_column(String(80))
    product_url: Mapped[str | None] = mapped_column(String(500))
    __table_args__ = (UniqueConstraint("retailer_id", "sku"),)


class PriceCheck(Base):
    __tablename__ = "price_checks"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    listing_id: Mapped[str] = mapped_column(ForeignKey("retailer_listings.id"))
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"))
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    regular_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    inventory_status: Mapped[str] = mapped_column(String(30))
    inventory_quantity: Mapped[int | None]
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    provenance: Mapped[str] = mapped_column(String(10), index=True)
    __table_args__ = (UniqueConstraint("listing_id", "store_id", "observed_at"),)


class Watch(Base):
    __tablename__ = "watchlist"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    target_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    zip_code: Mapped[str] = mapped_column(String(5))
    radius: Mapped[int]
    retailers: Mapped[list] = mapped_column(JSON)
    provenance: Mapped[str] = mapped_column(String(10), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    last_attempted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_successful_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    check_status: Mapped[str] = mapped_column(String(100), default="Not checked")


class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    watchlist_id: Mapped[int] = mapped_column(ForeignKey("watchlist.id", ondelete="CASCADE"))
    dedup_key: Mapped[str] = mapped_column(String(250), unique=True)
    message: Mapped[str] = mapped_column(String(400))
    provenance: Mapped[str] = mapped_column(String(10), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    read: Mapped[bool] = mapped_column(default=False)
    dismissed: Mapped[bool] = mapped_column(default=False)
