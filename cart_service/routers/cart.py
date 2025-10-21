from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from cart_service.dependency import get_inventory_client, get_user_cart
from cart_service.models import AddItemRequest, Cart
from common.inventory_client import InventoryClient

router = APIRouter()


@router.get("/cart/{user_id}", response_model=Cart)
async def view_cart(user_cart: Cart = Depends(get_user_cart)) -> Cart:
    """
    Retrieve current cart contents
    """
    return user_cart


@router.post("/cart/{user_id}/add")
async def add_to_cart(
    user_id: str,
    data: AddItemRequest,
    inventory_client: InventoryClient = Depends(get_inventory_client),
    user_cart: Cart = Depends(get_user_cart),
) -> dict[str, Any]:
    """
    Add items to the cart for a user.
    """
    try:
        await user_cart.add_item(data.item_id, data.quantity, inventory_client)
        return {"message": "Item added", "cart": user_cart}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve)) from ve
