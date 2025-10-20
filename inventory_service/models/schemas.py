from typing import List
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
    items: List[Item]

class CategoryList(BaseModel):
    categories: List[Category] 

class ItemsInCategory(BaseModel):
    category: Category
    items: List[Item]
    