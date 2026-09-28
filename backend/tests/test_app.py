import asyncio
from datetime import timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.adapters.base import ProviderError
from app.adapters.demo import PRODUCTS
from app.config import Settings
from app.database.models import Alert, PriceCheck, now
from app.database.session import purge_expired
from app.main import create_app
from app.utils.location import distance_miles, locations, resolve_zip
from app.utils.matching import discount, gtin, match_product


@pytest.fixture
def app(tmp_path):
    return create_app(
        Settings(database_url=f"sqlite:///{tmp_path / 'test.sqlite3'}", demo_mode=True),
        migrate=False,
    )


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


def search(client, **extra):
    return client.get(
        "/api/search", params={"q": "FW-D20", "zip_code": "53703", "radius": 25, **extra}
    )


def save(client, **extra):
    return client.post(
        "/api/watchlist",
        json={
            "product_id": "demo-drill",
            "target_price": "85.00",
            "zip_code": "53703",
            "radius": 25,
            "retailers": ["walmart", "target"],
            **extra,
        },
    )


def test_identifiers_and_variant_matching():
    assert gtin("012345678905") == "00012345678905"
    assert gtin("00012345678905") == gtin("012345678905")
    assert gtin("012345678906") is None
    assert gtin("not-a-code") is None
    assert match_product("012345678905", PRODUCTS[0], "X")[0] == 100
    assert match_product("FW-D20", PRODUCTS[3], "X")[0] == 0
    assert match_product("drill", PRODUCTS[0], "X")[0] == 75
    assert match_product("FW-D20", PRODUCTS[0], "X")[0] == 95


def test_money_and_distance():
    assert discount(Decimal(75), Decimal(100)) == 25
    for price, regular in [(None, 100), (10, None), (10, 0), (11, 10), (-1, 10)]:
        assert discount(price, regular) is None
    assert distance_miles(0, 0, 0, 0) == 0
    assert distance_miles(0, 0, 0, 1) == pytest.approx(69.09, abs=0.1)


def test_nationwide_location_data():
    assert len({row.state for row in locations().values()}) == 51
    assert resolve_zip("02108").zip_code == "02108"
    assert resolve_zip("99501").state == "AK"
    assert resolve_zip("96813").state == "HI"


def test_demo_search_and_cache(client, app):
    response = search(client)
    assert response.status_code == 200, response.text
    result = response.json()
    assert len(result["offers"]) == 10
    assert len(result["providers"]) == 5
    assert all(o["provenance"] == "demo" for o in result["offers"])
    assert len({o["inventory_status"] for o in result["offers"]}) == 4
    assert all(o["product_url"] is None for o in result["offers"])
    with app.state.session_factory() as session:
        count = session.scalar(select(func.count()).select_from(PriceCheck))
    cached = search(client).json()
    assert all(o["cached"] for o in cached["offers"])
    assert cached["offers"][0]["observed_at"] == result["offers"][0]["observed_at"]
    with app.state.session_factory() as session:
        assert session.scalar(select(func.count()).select_from(PriceCheck)) == count


def test_search_skus_and_groups(client):
    result = search(client, q="drill").json()
    assert {o["product"]["id"] for o in result["offers"]} == {"demo-drill", "demo-drill-bare"}
    result = search(client, q="DEMO-WALMART-DRILL").json()
    assert len(result["offers"]) == 2
    assert {o["retailer_id"] for o in result["offers"]} == {"walmart"}
    result = search(client, q="00012345678905").json()
    assert all(o["confidence"] == 100 for o in result["offers"])


@pytest.mark.parametrize(
    "params",
    [{"q": " "}, {"zip_code": "123"}, {"zip_code": "00000"}, {"radius": 7}, {"retailers": "fake"}],
)
def test_api_validation(client, params):
    assert search(client, **params).status_code == 422


def test_unknown_and_empty_results(client):
    assert search(client, q="nonexistent widget").json()["offers"] == []
    assert search(client, zip_code="59001", radius=5).json()["offers"] == []
    offers = search(client, q="coffee").json()["offers"]
    assert any(o["price"] is None and o["discount"] is None for o in offers)


def test_adapter_partial_failure(client, app, monkeypatch):
    async def broken(_):
        raise ProviderError("rate_limited", "Rate limit reached. Try later.")

    monkeypatch.setattr(app.state.search.adapters["target"], "search_product", broken)
    data = search(client).json()
    assert len(data["offers"]) == 8
    assert any(s["status"] == "rate_limited" for s in data["providers"])


@pytest.mark.parametrize("kind", ["timeout", "malformed_response", "credentials_required"])
def test_provider_failure_mapping(client, app, monkeypatch, kind):
    async def broken(_):
        if kind == "timeout":
            raise TimeoutError()
        if kind == "credentials_required":
            raise ProviderError(kind, "Credentials required")
        raise ValueError("Malformed payload")

    monkeypatch.setattr(app.state.search.adapters["walmart"], "search_product", broken)
    data = search(client).json()
    assert any(s["status"] == kind for s in data["providers"])
    assert len(data["offers"]) == 8


def test_watchlist_manual_alert_flow(client):
    created = save(client)
    assert created.status_code == 201, created.text
    item = created.json()
    assert item["product"]["id"] == "demo-drill"
    assert client.post("/api/watchlist/refresh").json()["new_alerts"] > 0
    assert client.post("/api/watchlist/refresh").json()["new_alerts"] == 0
    alerts = client.get("/api/alerts").json()
    assert alerts and all(a["provenance"] == "demo" for a in alerts)
    assert client.patch(f"/api/alerts/{alerts[0]['id']}", json={"read": True}).json()["read"]
    assert (
        client.patch(f"/api/alerts/{alerts[0]['id']}", json={"dismissed": True}).status_code == 200
    )
    assert len(client.get("/api/alerts").json()) == len(alerts) - 1
    updated = client.patch(
        f"/api/watchlist/{item['id']}",
        json={"target_price": "1.00", "radius": 5, "retailers": ["target"]},
    )
    assert updated.status_code == 200
    assert client.post("/api/watchlist/refresh").json()["new_alerts"] == 0
    assert client.delete(f"/api/watchlist/{item['id']}").status_code == 204
    assert client.get("/api/watchlist").json() == []
    assert client.get("/api/alerts").json() == []


def test_watchlist_invalid_settings(client):
    assert save(client, target_price="-1").status_code == 422
    assert save(client, retailers=[]).status_code == 422
    assert save(client, product_id="missing").status_code == 404
    assert save(client, zip_code="00000").status_code == 422
    item = save(client).json()
    assert (
        client.patch(f"/api/watchlist/{item['id']}", json={"target_price": None}).status_code == 422
    )


def test_no_alerts_for_unavailable_stock(client):
    save(client, retailers=["lowes"], radius=5, target_price="999.00")
    assert client.post("/api/watchlist/refresh").json()["new_alerts"] == 0


def test_detail_history_stores(client):
    assert client.get("/api/products/demo-drill").status_code == 200
    assert client.get("/api/products/missing").status_code == 404
    history = client.get("/api/products/demo-drill/history").json()
    assert len(history) > 20 and all(p["provenance"] == "demo" for p in history)
    assert client.get("/api/products/demo-drill/prices").json() == []
    search(client)
    assert len(client.get("/api/products/demo-drill/prices").json()) == 10
    assert len(client.get("/api/stores", params={"zip_code": "53703", "radius": 5}).json()) == 5


def test_persistence_and_mode_separation(tmp_path):
    url = f"sqlite:///{tmp_path / 'persist.sqlite3'}"
    with TestClient(create_app(Settings(database_url=url), migrate=False)) as first:
        save(first)
        first.post("/api/watchlist/refresh")
    with TestClient(create_app(Settings(database_url=url), migrate=False)) as restarted:
        assert len(restarted.get("/api/watchlist").json()) == 1
        assert restarted.get("/api/alerts").json()
    with TestClient(create_app(Settings(database_url=url, demo_mode=False), migrate=False)) as live:
        assert live.get("/api/watchlist").json() == []
        assert live.get("/api/alerts").json() == []
        assert live.get("/api/products/demo-drill").status_code == 404
        data = search(live).json()
        assert data["mode"] == "live" and data["offers"] == []
        assert all(p["status"] == "unavailable" for p in data["providers"])


def test_expired_records_are_purged(client, app):
    save(client)
    client.post("/api/watchlist/refresh")
    with app.state.session_factory() as session:
        check = session.scalar(select(PriceCheck).limit(1))
        check.expires_at = now() - timedelta(seconds=1)
        identifier = check.id
        alert = session.scalar(select(Alert).limit(1))
        alert.expires_at = now() - timedelta(seconds=1)
        alert_id = alert.id
        session.commit()
        purge_expired(session)
        session.expire_all()
        assert session.get(PriceCheck, identifier) is None
        assert session.get(Alert, alert_id) is None


def test_real_timeout_cancels_provider(client, app, monkeypatch):
    app.state.search.settings.request_timeout = 0.02

    async def slow(_):
        await asyncio.sleep(1)

    monkeypatch.setattr(app.state.search.adapters["target"], "search_product", slow)
    data = search(client).json()
    assert any(p["status"] == "timeout" for p in data["providers"])
    assert len(data["offers"]) == 8
