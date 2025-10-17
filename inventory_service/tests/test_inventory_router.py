import pytest
from tinydb import TinyDB
from httpx import AsyncClient, ASGITransport
import inventory_service.db as dbmod
from inventory_service.main import app  # use the same app the service runs

@pytest.fixture
def fake_db(tmp_path, monkeypatch):
    test_db = TinyDB(tmp_path / "test_inventory.json")

    test_db.insert({
        "id": 1,
        "name": "Footwear",
        "items": [
            {"id": "1-1", "name": "Sneaker", "description": "Running shoe", "price": 59.99, "stock": 10},
            {"id": "1-2", "name": "Loafer", "description": "Casual shoe", "price": 89.99, "stock": 5}
        ]
    })

    # patch get_db so every call uses this test_db
    monkeypatch.setattr("inventory_service.routers.inventory.get_db", lambda: test_db)

    return test_db


@pytest.mark.asyncio
async def test_get_categories(fake_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/categories")

    assert response.status_code == 200
    data = response.json()
    print(data)
    assert data["categories"] != []  # ensure data seeded
    assert data["categories"][0]["name"] == "Footwear"

# TODO - Need to add test for other endpoints too