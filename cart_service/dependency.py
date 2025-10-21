from typing import Dict
from cart_service.models import Cart
from common.inventory_client import InventoryClient

# Simulating a user-based cart store for demonstration.
# In a real application, this would be a database or cache.
_cart_store: Dict[str, Cart] = {}

async def get_inventory_client() -> InventoryClient:
    """
    Provides a singleton instance of the InventoryClient.
    """
    print("Creating InventoryClient...")
    client = InventoryClient()
    try:
        yield client
    finally:
        print("Closing InventoryClient...")
        await client.aclose()


async def get_user_cart(user_id: str) -> Cart:
    """
    Provides a user's cart from the simulated store.
    """
    if user_id not in _cart_store:
        _cart_store[user_id] = Cart(items=[])
    return _cart_store[user_id]