
from pydantic import BaseModel


class Category(BaseModel):
    id: int
    name: str


class Item(BaseModel):
    id: str
    name: str
    description: str
    price: float
    stock: int


class CategoryWithItems(Category):
    items: list[Item]


class CategoryList(BaseModel):
    categories: list[Category]


class ItemsInCategory(BaseModel):
    category: Category
    items: list[Item]
