import re
from decimal import Decimal


def normalize(value):
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def gtin(value):
    digits = re.sub(r"[\s-]", "", value)
    if not digits.isdigit() or len(digits) not in (8, 12, 13, 14):
        return None
    check = (
        10
        - sum(int(d) * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(digits[:-1]))) % 10
    ) % 10
    return digits.zfill(14) if check == int(digits[-1]) else None


def match_product(query, product, sku):
    code = gtin(query)
    if code and code == gtin(product.upc):
        return 100, "Exact UPC / GTIN"
    if normalize(query) == normalize(sku):
        return 100, "Exact retailer SKU"
    if normalize(query) == normalize(product.model_number):
        return 95, "Exact model; variant kept separate"
    tokens = set(normalize(query).split())
    title = set(normalize(f"{product.brand} {product.name} {product.model_number}").split())
    if tokens and tokens <= title:
        return 75, "Title match — verify model and variant"
    return 0, ""


def discount(price, regular):
    if price is None or regular is None or regular <= 0 or price < 0 or price > regular:
        return None
    return float(((regular - price) / regular * 100).quantize(Decimal("0.1")))
