from fastapi import APIRouter, HTTPException
from tinydb import TinyDB, Query

from inventory_service.models import (
    Category, CategoryList, Item, ItemsInCategory, ItemDetail
)


from inventory_service.db import get_db

router = APIRouter()


db = get_db()

@router.get("/categories", response_model=CategoryList)
def get_categories():
    """
    Retrieve all categories in the inventory.
    """
    categories =[Category(id=c["id"], name=c["name"]) for c in db.all()]
    return CategoryList(categories=categories)

@router.get("/categories/{category_id}/items", response_model=ItemsInCategory)
def get_items(category_id: int):
    """
    Retrieve all items in the category.
    """
    CategoryQ = Query()
    cat = db.get(CategoryQ.id == category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return ItemsInCategory(
        category=Category(id=cat["id"], name=cat["name"]),
        items=[Item(**i) for i in cat["items"]],
    )

@router.get("/categories/{category_id}/items/{item_id}", response_model=Item)
def get_item_detail(category_id: int, item_id: str):
    """
    Retrieve details of a specific item in a category.
    """
    CategoryQ = Query()
    cat = db.get(CategoryQ.id == category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    item_data = next((item for item in cat["items"] if item["id"] == item_id), None)
    if not item_data:
        raise HTTPException(status_code=404, detail="Item not found")

    return Item(**item_data)
