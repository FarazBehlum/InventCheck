import csv
import math
from functools import lru_cache
from pathlib import Path

from fastapi import HTTPException

from app.schemas import Location


@lru_cache(maxsize=1)
def locations():
    with (Path(__file__).resolve().parents[2] / "data/us_zips.csv").open() as file:
        return {row["zip_code"]: Location(**row) for row in csv.DictReader(file)}


def resolve_zip(zip_code):
    location = locations().get(zip_code)
    if not location:
        raise HTTPException(
            422, "ZIP code is not supported by the bundled US dataset. Try 53703 or another ZIP."
        )
    return location


def distance_miles(lat1, lon1, lat2, lon2):
    a, b = math.radians(lat1), math.radians(lat2)
    delta = (
        math.sin((b - a) / 2) ** 2
        + math.cos(a) * math.cos(b) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    )
    return 3958.7613 * 2 * math.asin(min(1, math.sqrt(delta)))
