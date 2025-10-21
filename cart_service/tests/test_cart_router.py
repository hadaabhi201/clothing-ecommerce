
from cart_service.dependency import get_inventory_client, get_user_cart
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, patch

from cart_service.models import Cart, CartItem
from cart_service.routers.cart import router as cart_router

app = FastAPI()
app.include_router(cart_router)

@pytest.fixture
def mock_user_cart_dependency():
    """Provides an empty cart for testing."""
    return Cart(items=[])

@pytest.fixture
def mock_inventory_client_dependency():
    """Provides a mocked InventoryClient for testing."""
    mock_client = AsyncMock()
    mock_client.find_item.return_value = {"item_id": "1-1", "name": "Mock Item", "price": 9.99, "stock": 10}
    mock_client.is_available.return_value = True
    return mock_client

@pytest.fixture
def mock_add_item_method():
    """
    Fixture that patches the Cart.add_item method with an AsyncMock.
    The patch is automatically undone after the test finishes.
    """
    with patch.object(Cart, 'add_item', new_callable=AsyncMock) as mock_method:
        yield mock_method

@pytest.fixture(autouse=True)
def override_dependencies(mock_inventory_client_dependency):
    """
    Fixture to set up and tear down dependency overrides for testing.
    We only need to override get_inventory_client here.
    """
    app.dependency_overrides[get_inventory_client] = lambda: mock_inventory_client_dependency
    app.dependency_overrides[get_user_cart] = lambda: Cart(items=[])  # Default empty cart for tests
    yield
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_add_to_cart_success(mock_add_item_method):
    """Test adding an item to the cart successfully."""
    user_id = "testuser"
    payload = {"item_id": "1-1", "quantity": 2}    
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(f"/cart/{user_id}/add", json=payload)
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Item added"
    
    # Assert that the item was actually added to the mocked cart
    mock_add_item_method.assert_awaited_once()
    
@pytest.mark.asyncio
async def test_add_to_cart_item_does_not_exist(mock_inventory_client_dependency):
    """Test adding an item that does not exist."""
    user_id = "testuser"
    payload = {"item_id": "unknown-item", "quantity": 1}
    
    # Configure mock client to return None, simulating not found
    mock_inventory_client_dependency.find_item.return_value = None
    
    # Patch Cart.add_item to raise a ValueError
    with patch.object(Cart, 'add_item', new=AsyncMock(side_effect=ValueError("Item with id 'unknown-item' does not exist."))):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(f"/cart/{user_id}/add", json=payload)

    assert response.status_code == 400
    assert "Item with id 'unknown-item' does not exist." in response.json()["detail"]


@pytest.mark.asyncio
async def test_view_cart_empty(mock_user_cart_dependency):
    """Test viewing an empty cart."""
    user_id = "testuser"
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/cart/{user_id}")
    
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total_cost"] == 0.0


@pytest.mark.asyncio
async def test_view_cart_with_items(mock_user_cart_dependency):
    """Test viewing a cart with items."""
    user_id = "testuser"
    initial_cart = Cart(items=[CartItem(item_id="1-1", name="Mock Item", quantity=2, price=9.99)])
    
    # Override get_user_cart to provide a cart with items
    app.dependency_overrides[get_user_cart] = lambda user_id: initial_cart
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/cart/{user_id}")
    
    assert response.status_code == 200
    response_data = response.json()
    print(response_data)
    assert len(response_data["items"]) == 1
    assert response_data["items"][0]["item_id"] == "1-1"
    assert response_data["total_cost"] == 19.98

    # Clean up the override
    del app.dependency_overrides[get_user_cart]