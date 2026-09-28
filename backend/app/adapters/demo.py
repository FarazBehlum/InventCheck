from decimal import Decimal

from app.database.models import now
from app.schemas import Match, ProductOut, StoreOut
from app.utils.location import distance_miles, resolve_zip
from app.utils.matching import gtin, match_product

from .base import InventoryData, PriceData, RetailerAdapter

RETAILERS = [
    ("walmart", "Walmart", "https://www.walmart.com"),
    ("target", "Target", "https://www.target.com"),
    ("homedepot", "Home Depot", "https://www.homedepot.com"),
    ("lowes", "Lowe’s", "https://www.lowes.com"),
    ("bestbuy", "Best Buy", "https://www.bestbuy.com"),
]
# These identifiers and brands are fictional demo fixtures, not retailer catalog records.
PRODUCTS = [
    ProductOut(
        id="demo-drill",
        name="20V cordless drill kit",
        brand="Fieldwork",
        model_number="FW-D20",
        upc="012345678905",
        gtin=gtin("012345678905"),
        image_url="/images/drill.svg",
        provenance="demo",
    ),
    ProductOut(
        id="demo-headphones",
        name="Wireless over-ear headphones",
        brand="Northline",
        model_number="NL-H1",
        upc="012345678912",
        gtin=gtin("012345678912"),
        image_url="/images/headphones.svg",
        provenance="demo",
    ),
    ProductOut(
        id="demo-coffee",
        name="12-cup coffee maker",
        brand="Daybreak",
        model_number="DB-C12",
        upc="012345678929",
        gtin=gtin("012345678929"),
        image_url="/images/coffee.svg",
        provenance="demo",
    ),
    ProductOut(
        id="demo-drill-bare",
        name="20V cordless drill — tool only",
        brand="Fieldwork",
        model_number="FW-D20B",
        upc="012345678936",
        gtin=gtin("012345678936"),
        image_url="/images/drill.svg",
        provenance="demo",
    ),
]
DEMO_ZIPS = [
    "53703",
    "10001",
    "60601",
    "94103",
    "90012",
    "73301",
    "98101",
    "20001",
    "02108",
    "33130",
    "99501",
    "96813",
]
BASE_PRICES = [Decimal("79.00"), Decimal("89.99"), Decimal("39.99"), Decimal("49.00")]
REGULAR_PRICES = [Decimal("129.00"), Decimal("149.99"), Decimal("69.99"), Decimal("79.00")]


class DemoAdapter(RetailerAdapter):
    provenance = "demo"

    def __init__(self, retailer_id):
        self.index = next(i for i, row in enumerate(RETAILERS) if row[0] == retailer_id)
        self.id, self.name, self.website = RETAILERS[self.index]
        self.products = {p.id: p for p in PRODUCTS}
        self.stores = []
        for zip_code in DEMO_ZIPS:
            location = resolve_zip(zip_code)
            for branch in range(2):
                identifier = f"demo-{self.id}-{zip_code}-{branch}"
                self.stores.append(
                    StoreOut(
                        **location.model_dump(exclude={"latitude", "longitude"}),
                        id=identifier,
                        store_identifier=identifier,
                        retailer_id=self.id,
                        provenance="demo",
                        name=f"{self.name} · {'Central' if branch == 0 else 'North'} demo store",
                        address=f"{100 + self.index * 20 + branch} Fictional Demo Lane",
                        latitude=location.latitude + (0.014 + self.index * 0.008 + branch * 0.14),
                        longitude=location.longitude + (0.01 + self.index * 0.004),
                    )
                )

    def sku(self, product_id):
        return f"DEMO-{self.id.upper()}-{product_id.removeprefix('demo-').upper()}"

    async def search_product(self, query):
        matches = []
        for product in self.products.values():
            confidence, reason = match_product(query, product, self.sku(product.id))
            if confidence:
                matches.append(Match(product=product, confidence=confidence, reason=reason))
        return matches

    async def get_product_details(self, product_id):
        return self.products.get(product_id)

    async def get_nearby_stores(self, location, radius):
        return [
            s
            for s in self.stores
            if distance_miles(location.latitude, location.longitude, s.latitude, s.longitude)
            <= radius
        ]

    async def get_store_price(self, product_id, store_id):
        product_index = list(self.products).index(product_id)
        branch = int(store_id[-1])
        price = BASE_PRICES[product_index] + Decimal(self.index * 5 + branch * 3)
        if product_index == 2 and self.index == 4:
            price = None
        return PriceData(
            price=price, regular_price=REGULAR_PRICES[product_index], observed_at=now()
        )

    async def get_inventory(self, product_id, store_id):
        status = ["In stock", "Limited stock", "In stock", "Out of stock", "Unknown"][
            (self.index + int(store_id[-1])) % 5
        ]
        return InventoryData(
            status=status,
            quantity={"In stock": 8, "Limited stock": 2, "Out of stock": 0, "Unknown": None}[
                status
            ],
        )
