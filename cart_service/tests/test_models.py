import pytest
from cart_service.models import Cart
from cart_service.models import CartItem

class MockInventoryClient:
    async def find_item(self, item_id):
        if item_id == "in_stock":
            return {
                "item_id": item_id,
                "name": "Shirt",
                "price": 10.0,
                "stock": 10
            }
        elif item_id == "low_stock":
            return {
                "item_id": item_id,
                "name": "Hat",
                "price": 5.0,
                "stock": 1
            }
        else:
            return {
                "item_id": item_id,
                "name": "Unknown",
                "price": 0.0,
                "stock": 0
            }

@pytest.mark.asyncio
async def test_add_item_to_cart_success():
    cart = Cart()
    client = MockInventoryClient()

    await cart.add_item("in_stock", 2, client)

    assert len(cart.items) == 1
    item = cart.items[0]
    assert item.item_id == "in_stock"
    assert item.name == "Shirt"
    assert item.quantity == 2
    assert item.price == 10.0
    assert cart.total_cost == 20.0

@pytest.mark.asyncio
async def test_add_same_item_twice_increases_quantity():
    cart = Cart()
    client = MockInventoryClient()

    await cart.add_item("in_stock", 1, client)
    await cart.add_item("in_stock", 2, client)

    assert len(cart.items) == 1
    item = cart.items[0]
    assert item.quantity == 3
    assert item.name == "Shirt"
    assert item.price == 10.0
    assert cart.total_cost == 30.0

@pytest.mark.asyncio
async def test_add_item_insufficient_stock():
    cart = Cart()
    client = MockInventoryClient()

    with pytest.raises(ValueError) as e:
        await cart.add_item("low_stock", 5, client)

    assert "does not have enough stock" in str(e.value)
    assert len(cart.items) == 0
