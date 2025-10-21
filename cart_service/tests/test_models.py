from unittest.mock import AsyncMock

import pytest

from cart_service.models import Cart, CartItem
from common.inventory_client.inventory_client import InventoryClient

# --- Fixtures for testing ---


@pytest.fixture
def mock_inventory_client() -> AsyncMock:
    """Provides a mocked InventoryClient for testing the Cart model."""
    client = AsyncMock(spec=InventoryClient)
    # Default behavior for a successful lookup
    client.find_item.return_value = {
        "item_id": "1-1",
        "name": "Mock Item",
        "price": 9.99,
        "stock": 10,
    }
    return client


@pytest.fixture
def cart_with_item() -> Cart:
    """Provides a Cart with a pre-existing item."""
    return Cart(items=[CartItem(item_id="1-1", name="Mock Item", quantity=2, price=9.99)])


# --- Test cases for Cart.add_item ---


@pytest.mark.asyncio
async def test_add_item_new_to_cart(mock_inventory_client: AsyncMock) -> None:
    """Test adding a new item to an empty cart."""
    cart = Cart()
    item_id = "1-1"
    quantity = 5

    await cart.add_item(item_id, quantity, mock_inventory_client)

    assert len(cart.items) == 1
    added_item = cart.items[0]
    assert added_item.item_id == item_id
    assert added_item.quantity == quantity
    assert added_item.name == "Mock Item"
    assert added_item.price == 9.99

    mock_inventory_client.find_item.assert_awaited_once_with(item_id)


@pytest.mark.asyncio
async def test_add_item_update_existing(
    cart_with_item: Cart, mock_inventory_client: AsyncMock
) -> None:
    """Test adding an existing item to the cart, which updates the quantity."""
    item_id = "1-1"
    quantity_to_add = 3
    initial_quantity = cart_with_item.items[0].quantity

    await cart_with_item.add_item(item_id, quantity_to_add, mock_inventory_client)

    assert len(cart_with_item.items) == 1
    updated_item = cart_with_item.items[0]
    assert updated_item.quantity == initial_quantity + quantity_to_add

    mock_inventory_client.find_item.assert_awaited_once_with(item_id)


@pytest.mark.asyncio
async def test_add_item_not_found(mock_inventory_client: AsyncMock) -> None:
    """Test adding a nonexistent item raises a ValueError."""
    mock_inventory_client.find_item.return_value = None
    cart = Cart()
    item_id = "unknown-item"

    with pytest.raises(ValueError, match=f"Item with id '{item_id}' does not exist."):
        await cart.add_item(item_id, 1, mock_inventory_client)


async def test_add_item_insufficient_stock(mock_inventory_client: AsyncMock) -> None:
    """Test adding an item with insufficient stock raises a ValueError."""
    cart = Cart()
    item_id = "1-1"
    quantity_to_add = 11  # More than the mock stock of 10

    with pytest.raises(ValueError, match=f"Item '{item_id}' does not have enough stock."):
        await cart.add_item(item_id, quantity_to_add, mock_inventory_client)


@pytest.mark.asyncio
async def test_add_item_multiple_items_and_total_cost(mock_inventory_client: AsyncMock) -> None:
    """Test adding multiple items and verifying the total cost."""
    cart = Cart()

    # Add first item
    await cart.add_item("1-1", 2, mock_inventory_client)

    # Configure mock for a second, different item
    mock_inventory_client.find_item.return_value = {
        "item_id": "2-2",
        "name": "Mock T-Shirt",
        "price": 20.00,
        "stock": 50,
    }
    await cart.add_item("2-2", 3, mock_inventory_client)

    assert len(cart.items) == 2
    assert cart.total_cost == (2 * 9.99) + (3 * 20.00)


@pytest.fixture
def cart_with_multiple_items() -> Cart:
    """Provides a Cart with a pre-existing item."""
    return Cart(
        items=[
            CartItem(item_id="1-1", name="Mock Item", quantity=2, price=9.99),
            CartItem(item_id="2-2", name="Another Mock Item", quantity=5, price=5.00),
        ]
    )


# --- Test cases for Cart.remove_item ---


@pytest.mark.asyncio
async def test_remove_item_success(cart_with_multiple_items: Cart) -> None:
    """Test removing an item that exists in the cart."""
    item_id_to_remove = "1-1"
    initial_item_count = len(cart_with_multiple_items.items)

    await cart_with_multiple_items.remove_item(item_id_to_remove)

    assert len(cart_with_multiple_items.items) == initial_item_count - 1
    assert not any(item.item_id == item_id_to_remove for item in cart_with_multiple_items.items)


@pytest.mark.asyncio
async def test_remove_item_not_found(cart_with_multiple_items: Cart) -> None:
    """Test removing an item that does not exist in the cart."""
    item_id_to_remove = "non-existent-item"

    with pytest.raises(
        ValueError,
        match=f"Item with id '{item_id_to_remove}' not found in cart.",
    ):
        await cart_with_multiple_items.remove_item(item_id_to_remove)


# File: cart_service/tests/test_models.py (updated)
# ... (existing code and imports) ...

# --- Test cases for Cart.update_item_quantity ---


@pytest.mark.asyncio
async def test_update_item_quantity_success(cart_with_multiple_items: Cart) -> None:
    """Test updating the quantity of an existing item."""
    item_id_to_update = "1-1"
    new_quantity = 5

    await cart_with_multiple_items.update_item_quantity(item_id_to_update, new_quantity)

    updated_item = next(
        (item for item in cart_with_multiple_items.items if item.item_id == item_id_to_update),
        None,
    )
    assert updated_item is not None
    assert updated_item.quantity == new_quantity


@pytest.mark.asyncio
async def test_update_item_quantity_to_zero_removes_item(cart_with_multiple_items: Cart) -> None:
    """Test updating an item's quantity to 0 removes it from the cart."""
    item_id_to_update = "1-1"
    initial_item_count = len(cart_with_multiple_items.items)

    await cart_with_multiple_items.update_item_quantity(item_id_to_update, 0)

    assert len(cart_with_multiple_items.items) == initial_item_count - 1
    assert not any(item.item_id == item_id_to_update for item in cart_with_multiple_items.items)


@pytest.mark.asyncio
async def test_update_item_quantity_item_not_found(cart_with_multiple_items: Cart) -> None:
    """Test updating the quantity of an item not in the cart."""
    item_id_to_update = "non-existent-item"
    new_quantity = 5

    with pytest.raises(
        ValueError,
        match=f"Item with id '{item_id_to_update}' not found in cart.",
    ):
        await cart_with_multiple_items.update_item_quantity(item_id_to_update, new_quantity)
