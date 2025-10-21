from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from cart_service.dependency import get_inventory_client, get_user_cart
from cart_service.models import Cart, CartItem
from cart_service.routers.cart import router as cart_router

app = FastAPI()
app.include_router(cart_router)


@pytest.fixture
def mock_user_cart_dependency() -> Cart:
    """Provides an empty cart for testing."""
    return Cart(items=[])


@pytest.fixture
def mock_inventory_client_dependency() -> AsyncMock:
    """Provides a mocked InventoryClient for testing."""
    mock_client = AsyncMock()
    mock_client.find_item.return_value = {
        "item_id": "1-1",
        "name": "Mock Item",
        "price": 9.99,
        "stock": 10,
    }
    mock_client.is_available.return_value = True
    return mock_client


@pytest.fixture
async def mock_add_item_method() -> AsyncGenerator[AsyncMock, None]:
    """
    Fixture that patches the Cart.add_item method with an AsyncMock.
    The patch is automatically undone after the test finishes.
    """
    with patch.object(Cart, "add_item", new_callable=AsyncMock) as mock_method:
        yield mock_method


@pytest.fixture(autouse=True)
async def override_dependencies(
    mock_inventory_client_dependency: AsyncMock,
) -> AsyncGenerator[None, None]:
    """
    Fixture to set up and tear down dependency overrides for testing.
    We only need to override get_inventory_client here.
    """
    app.dependency_overrides[get_inventory_client] = lambda: mock_inventory_client_dependency
    app.dependency_overrides[get_user_cart] = lambda user_id: Cart(
        items=[]
    )  # Default empty cart for tests
    yield
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_add_to_cart_success(mock_add_item_method: AsyncMock) -> None:
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
async def test_add_to_cart_item_does_not_exist(mock_inventory_client_dependency: AsyncMock) -> None:
    """Test adding an item that does not exist."""
    user_id = "testuser"
    payload = {"item_id": "unknown-item", "quantity": 1}

    # Configure mock client to return None, simulating not found
    mock_inventory_client_dependency.find_item.return_value = None

    # Patch Cart.add_item to raise a ValueError
    with patch.object(
        Cart,
        "add_item",
        new=AsyncMock(side_effect=ValueError("Item with id 'unknown-item' does not exist.")),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(f"/cart/{user_id}/add", json=payload)

    assert response.status_code == 400
    assert "Item with id 'unknown-item' does not exist." in response.json()["detail"]


@pytest.mark.asyncio
async def test_view_cart_empty(mock_user_cart_dependency: Cart) -> None:
    """Test viewing an empty cart."""
    user_id = "testuser"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/cart/{user_id}")

    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total_cost"] == 0.0


@pytest.mark.asyncio
async def test_view_cart_with_items(mock_user_cart_dependency: Cart) -> None:
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


@pytest.mark.asyncio
async def test_remove_from_cart_success() -> None:
    """Test removing an item from the cart successfully."""
    user_id = "testuser"
    item_id_to_remove = "1-1"

    # Patch the Cart.remove_item method to simulate success
    with patch.object(Cart, "remove_item") as mock_remove_method:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.delete(f"/cart/{user_id}/remove/{item_id_to_remove}")

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == f"Item '{item_id_to_remove}' removed"

    # Assert that the remove_item method was called once with the correct item_id
    mock_remove_method.assert_called_once_with(item_id_to_remove)


@pytest.mark.asyncio
async def test_remove_from_cart_item_not_found() -> None:
    """Test removing an item not present in the cart."""
    user_id = "testuser"
    item_id_to_remove = "non-existent-item"

    # Patch the Cart.remove_item method to raise a ValueError
    with patch.object(
        Cart, "remove_item", new=AsyncMock(side_effect=ValueError("Item not found."))
    ) as mock_remove_method:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.delete(f"/cart/{user_id}/remove/{item_id_to_remove}")

    assert response.status_code == 404
    assert "Item not found." in response.json()["detail"]

    # Assert that the remove_item method was called once
    mock_remove_method.assert_called_once_with(item_id_to_remove)


@pytest.mark.asyncio
async def test_update_item_in_cart_success() -> None:
    """Test updating an item's quantity in the cart successfully."""
    user_id = "testuser"
    item_id_to_update = "1-1"
    payload = {"quantity": 5}

    with patch.object(Cart, "update_item_quantity", new=AsyncMock()) as mock_update_method:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.put(f"/cart/{user_id}/update/{item_id_to_update}", json=payload)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == f"Item '{item_id_to_update}' updated"

    mock_update_method.assert_awaited_once_with(item_id_to_update, payload["quantity"])


@pytest.mark.asyncio
async def test_update_item_in_cart_item_not_found() -> None:
    """Test updating an item not present in the cart."""
    user_id = "testuser"
    item_id_to_update = "non-existent-item"
    payload = {"quantity": 5}

    with patch.object(
        Cart,
        "update_item_quantity",
        new=AsyncMock(side_effect=ValueError("Item not found in cart.")),
    ) as mock_update_method:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.put(f"/cart/{user_id}/update/{item_id_to_update}", json=payload)

    assert response.status_code == 404
    assert "Item not found in cart." in response.json()["detail"]

    mock_update_method.assert_awaited_once_with(item_id_to_update, payload["quantity"])


@pytest.mark.asyncio
async def test_update_item_in_cart_to_zero_quantity() -> None:
    """Test updating an item's quantity to 0, which should remove it."""
    user_id = "testuser"
    item_id_to_update = "1-1"
    payload = {"quantity": 0}

    with patch.object(Cart, "update_item_quantity", new=AsyncMock()) as mock_update_method:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.put(f"/cart/{user_id}/update/{item_id_to_update}", json=payload)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == f"Item '{item_id_to_update}' updated"

    mock_update_method.assert_awaited_once_with(item_id_to_update, payload["quantity"])
