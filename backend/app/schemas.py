from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

RetailerId = Literal["walmart", "target", "homedepot", "lowes", "bestbuy"]
RETAILER_IDS = ["walmart", "target", "homedepot", "lowes", "bestbuy"]
Inventory = Literal["In stock", "Limited stock", "Out of stock", "Unknown"]
Provenance = Literal["demo", "live"]
Radius = Annotated[
    Literal[5, 10, 25, 50],
    BeforeValidator(
        lambda value: int(value) if isinstance(value, str) and value.isdigit() else value
    ),
]


class Record(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProductOut(Record):
    id: str
    name: str
    brand: str
    model_number: str
    upc: str
    gtin: str
    image_url: str
    provenance: Provenance


class Location(BaseModel):
    zip_code: str
    city: str
    state: str
    latitude: float
    longitude: float


class StoreOut(Location):
    model_config = ConfigDict(from_attributes=True)
    id: str
    retailer_id: RetailerId
    store_identifier: str
    name: str
    address: str
    provenance: Provenance


class Match(BaseModel):
    product: ProductOut
    confidence: int = Field(ge=0, le=100)
    reason: str


class Offer(BaseModel):
    id: str
    product: ProductOut
    retailer_id: RetailerId
    retailer_name: str
    store: StoreOut
    price: Decimal | None = Field(default=None, ge=0)
    regular_price: Decimal | None = Field(default=None, ge=0)
    discount: float | None
    currency: Literal["USD"] = "USD"
    price_scope: Literal["store"] = "store"
    inventory_status: Inventory
    inventory_quantity: int | None = Field(default=None, ge=0)
    observed_at: datetime
    expires_at: datetime | None = None
    distance: float = Field(ge=0)
    product_url: str | None = None
    confidence: int
    match_reason: str
    provenance: Provenance
    cached: bool = False


class ProviderStatus(BaseModel):
    retailer_id: RetailerId
    status: str
    message: str


class SearchOut(BaseModel):
    query: str
    location: Location
    radius: int
    mode: Provenance
    offers: list[Offer]
    providers: list[ProviderStatus]


class WatchInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product_id: str = Field(min_length=1, max_length=80)
    target_price: Decimal = Field(gt=0, le=1000000, max_digits=9, decimal_places=2)
    zip_code: str = Field(pattern=r"^\d{5}$")
    radius: Radius = 25
    retailers: list[RetailerId] = Field(min_length=1, max_length=5)

    @field_validator("retailers")
    @classmethod
    def unique_retailers(cls, value):
        return list(dict.fromkeys(value))


class WatchPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target_price: Decimal | None = Field(
        default=None, gt=0, le=1000000, max_digits=9, decimal_places=2
    )
    zip_code: str | None = Field(default=None, pattern=r"^\d{5}$")
    radius: Radius | None = None
    retailers: list[RetailerId] | None = Field(default=None, min_length=1, max_length=5)

    @model_validator(mode="after")
    def no_explicit_nulls(self):
        if any(getattr(self, key) is None for key in self.model_fields_set):
            raise ValueError("Watchlist settings cannot be null")
        return self


class AlertPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    read: bool | None = None
    dismissed: bool | None = None
