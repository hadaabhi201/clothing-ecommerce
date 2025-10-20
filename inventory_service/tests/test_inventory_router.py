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
    assert data["categories"] != []  # ensure data seeded
    assert data["categories"][0]["name"] == "Footwear"

@pytest.mark.asyncio
async def test_get_items(fake_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/categories/1/items")

    assert response.status_code == 200
    data = response.json()
    # category id should be 1
    assert data["category"]["id"] == 1

    # items list should have exactly 2 entries
    assert len(data["items"]) == 2

@pytest.mark.asyncio
async def test_get_items_exceoption(fake_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/categories/15/items")

    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Category not found"}

@pytest.mark.asyncio
async def test_get_item_detail(fake_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/categories/1/items/1-1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == '1-1'
    assert data["name"] == "Sneaker"

@pytest.mark.asyncio
async def test_get_item_detail_exceoption(fake_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/categories/15/items/123")

    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Category not found"}

@pytest.mark.asyncio
async def test_find_item_by_id_success(fake_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/items/1-1")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == '1-1'
    assert data["name"] == "Sneaker"

@pytest.mark.asyncio
async def test_find_item_by_id_not_found(fake_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/items/not-here")
    assert r.status_code == 404
    assert r.json()["detail"] == "Item not found"