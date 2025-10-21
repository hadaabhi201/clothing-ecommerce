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


class UpdateItemRequest(BaseModel):
    quantity: int = Field(..., ge=0, description="Quantity must be a non-negative integer")


class Cart(BaseModel):
    items: list[CartItem] = []

    @computed_field  # type: ignore[misc]
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

    async def remove_item(self, item_id: str) -> None:
        """
        Removes an item from the cart.
        Raises ValueError if the item is not found.
        """
        item_to_remove = next((item for item in self.items if item.item_id == item_id), None)
        if item_to_remove:
            self.items.remove(item_to_remove)
        else:
            raise ValueError(f"Item with id '{item_id}' not found in cart.")

    async def update_item_quantity(self, item_id: str, new_quantity: int) -> None:
        """
        Updates the quantity of an item in the cart. If the new quantity is 0,
        the item is removed. Raises ValueError if the item is not found.
        """
        existing_item = next((item for item in self.items if item.item_id == item_id), None)
        if existing_item:
            if new_quantity == 0:
                self.items.remove(existing_item)
            else:
                existing_item.quantity = new_quantity
        else:
            raise ValueError(f"Item with id '{item_id}' not found in cart.")
