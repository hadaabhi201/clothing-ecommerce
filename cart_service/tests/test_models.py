from unittest.mock import AsyncMock
from common.inventory_client.inventory_client import InventoryClient
import pytest

from cart_service.models import Cart, CartItem


# --- Fixtures for testing ---

@pytest.fixture
def mock_inventory_client():
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
def cart_with_item():
    """Provides a Cart with a pre-existing item."""
    return Cart(items=[CartItem(item_id="1-1", name="Mock Item", quantity=2, price=9.99)])


# --- Test cases for Cart.add_item ---

@pytest.mark.asyncio
async def test_add_item_new_to_cart(mock_inventory_client):
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
async def test_add_item_update_existing(cart_with_item, mock_inventory_client):
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
async def test_add_item_not_found(mock_inventory_client):
    """Test adding a nonexistent item raises a ValueError."""
    mock_inventory_client.find_item.return_value = None
    cart = Cart()
    item_id = "unknown-item"
    
    with pytest.raises(ValueError, match=f"Item with id '{item_id}' does not exist."):
        await cart.add_item(item_id, 1, mock_inventory_client)

async def test_add_item_insufficient_stock(mock_inventory_client):
    """Test adding an item with insufficient stock raises a ValueError."""
    cart = Cart()
    item_id = "1-1"
    quantity_to_add = 11  # More than the mock stock of 10
    
    with pytest.raises(ValueError, match=f"Item '{item_id}' does not have enough stock."):
        await cart.add_item(item_id, quantity_to_add, mock_inventory_client)


@pytest.mark.asyncio
async def test_add_item_multiple_items_and_total_cost(mock_inventory_client):
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