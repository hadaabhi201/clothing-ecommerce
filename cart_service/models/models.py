
from pydantic import BaseModel, Field, computed_field

from common.inventory_client import InventoryClient


class AddItemRequest(BaseModel):
    item_id: str
    quantity: int


class CartItem(BaseModel):
    item_id: str
    name: str
    quantity: int = Field(..., gt=0, description="Quantity must be a positive integer")
    price: float


class Cart(BaseModel):
    items: list[CartItem] = []

    @computed_field(return_type=float)
    @property
    def total_cost(self) -> float:
        """Calculate the total cost of all items in the cart."""
        return sum(item.quantity * item.price for item in self.items)

    async def add_item(self, item_id: str, quantity: int, client: InventoryClient) -> None:
        item_data = await client.find_item(item_id)
        if item_data is None:
           raise ValueError(f"Item with id '{item_id}' does not exist.")
        if int(item_data.get("stock", 0)) < quantity:
            raise ValueError(f"Item '{item_id}' does not have enough stock.")

        existing = next((i for i in self.items if i.item_id == item_id), None)
        if existing:
            existing.quantity += quantity
            existing.price = item_data.get("price", existing.price)
            existing.name = item_data.get("name", existing.name)
        else:
            self.items.append(
                CartItem(
                    item_id=item_id,
                    name=item_data.get("name", "Unknown"),
                    quantity=quantity,
                    price=item_data.get("price", 0.0),
                )
            )
