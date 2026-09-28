from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.schemas import Inventory, Match, ProductOut, StoreOut


class ProviderError(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message
        super().__init__(message)


class PriceData(BaseModel):
    price: Decimal | None
    regular_price: Decimal | None
    observed_at: datetime


class InventoryData(BaseModel):
    status: Inventory
    quantity: int | None


class RetailerAdapter(ABC):
    id: str
    name: str
    website: str
    provenance: str
    # Future live adapters must set a finite retention limit before persisting content.
    retention_seconds: int | None = None

    @abstractmethod
    async def search_product(self, query: str) -> list[Match]: ...
    @abstractmethod
    async def get_product_details(self, product_id: str) -> ProductOut | None: ...
    @abstractmethod
    async def get_nearby_stores(self, location, radius: int) -> list[StoreOut]: ...
    @abstractmethod
    async def get_store_price(self, product_id: str, store_id: str) -> PriceData: ...
    @abstractmethod
    async def get_inventory(self, product_id: str, store_id: str) -> InventoryData: ...
