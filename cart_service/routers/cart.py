from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from cart_service.models import AddItemRequest, Cart
from common.inventory_client import InventoryClient

router = APIRouter()

cart = Cart(items=[])
client = InventoryClient()


@router.get("/cart", response_model=Cart)
async def view_cart():
    """
    Retrieve current cart contents
    """
    cart_data = cart.model_dump(mode="json")
    cart_data["total_cost"] = cart.total_cost

    return JSONResponse(content=cart_data)


@router.post("/cart/add")
async def add_to_cart(data: AddItemRequest):
    """
    Add items to the cart
    """
    try:
        await cart.add_item(data.item_id, data.quantity, client)
        return {"message": "Item added", "cart": cart}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve)) from ve
