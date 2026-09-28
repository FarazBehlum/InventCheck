from .base import ProviderError, RetailerAdapter
from .demo import RETAILERS


class UnavailableAdapter(RetailerAdapter):
    provenance = "live"

    def __init__(self, retailer_id):
        self.id, self.name, self.website = next(row for row in RETAILERS if row[0] == retailer_id)

    def unavailable(self):
        raise ProviderError(
            "unavailable", "Live access is not configured or verified. No demo data is substituted."
        )

    async def search_product(self, query):
        return self.unavailable()

    async def get_product_details(self, product_id):
        return self.unavailable()

    async def get_nearby_stores(self, location, radius):
        return self.unavailable()

    async def get_store_price(self, product_id, store_id):
        return self.unavailable()

    async def get_inventory(self, product_id, store_id):
        return self.unavailable()
