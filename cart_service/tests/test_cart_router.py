import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from cart_service.models import CartItem
from cart_service.routers.cart import router as cart_router
from common.inventory_client.inventory_client import InventoryClient

# Setup FastAPI app and register router
app = FastAPI()
app.include_router(cart_router)

# --- Shared Mocks ---


class MockInventoryClient(InventoryClient):
    async def find_item(self, item_id: str):
        if item_id == "out_of_stock":
            return {"item_id": item_id, "name": "Shirt", "price": 10.0, "stock": 1}
        return {"item_id": item_id, "name": "Mock Item", "price": 5.0, "stock": 10}


class MockCart:
    def __init__(self):
        self.items = []

    @property
    def total_cost(self):
        return sum(i.quantity * i.price for i in self.items)

    async def add_item(self, item_id, quantity, client):
        item = await client.find_item(item_id)
        if quantity > item["stock"]:
            raise ValueError("Item does not have enough stock")
        self.items.append(
            CartItem(item_id=item_id, name=item["name"], quantity=quantity, price=item["price"])
        )

    def model_dump(self, mode="json"):
        return {
            "items": [
                {
                    "item_id": item.item_id,
                    "name": item.name,
                    "quantity": item.quantity,
                    "price": item.price,
                }
                for item in self.items
            ]
        }


@pytest.fixture(autouse=True)
def mock_cart_and_client(monkeypatch):
    monkeypatch.setattr("cart_service.routers.cart.cart", MockCart())
    monkeypatch.setattr("cart_service.routers.cart.client", MockInventoryClient())


# --- Tests ---


@pytest.mark.asyncio
async def test_add_item_with_mock_cart():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/cart/add", json={"item_id": "abc123", "quantity": 3})
        assert res.status_code == 200
        data = res.json()
        assert data["message"] == "Item added"
        assert data["cart"]["items"][0]["item_id"] == "abc123"


@pytest.mark.asyncio
async def test_add_item_insufficient_stock():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/cart/add", json={"item_id": "out_of_stock", "quantity": 5})
        assert res.status_code == 400
        assert res.json()["detail"] == "Item does not have enough stock"


@pytest.mark.asyncio
async def test_view_cart_empty(monkeypatch):
    class MockCart:
        def __init__(self):
            self.items = []

        @property
        def total_cost(self):
            return 0.0

        def model_dump(self, mode="json"):
            return {"items": []}

    monkeypatch.setattr("cart_service.routers.cart.cart", MockCart())

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/cart")
        assert res.status_code == 200
        assert res.json() == {"items": [], "total_cost": 0.0}


@pytest.mark.asyncio
async def test_view_cart_after_adding(monkeypatch):
    class MockCart:
        def __init__(self):
            self.items = [CartItem(item_id="1", name="Shirt", quantity=2, price=10.0)]

        @property
        def total_cost(self):
            return 20.0

        def model_dump(self, mode="json"):
            return {"items": [{"item_id": "1", "name": "Shirt", "quantity": 2, "price": 10.0}]}

    monkeypatch.setattr("cart_service.routers.cart.cart", MockCart())

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/cart")
        assert res.status_code == 200
        data = res.json()
        assert data["total_cost"] == 20.0
        assert len(data["items"]) == 1
        assert data["items"][0]["item_id"] == "1"
