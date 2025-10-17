from typing import List
import random
from faker import Faker
from inventory_service.models import Item, CategoryWithItems
from inventory_service.providers.fake_apparel_provider import ApparelProvider
from inventory_service.db import get_db

db = get_db()


def build_category(cid: int, name: str, items_per_cat: int = 5) -> CategoryWithItems:
    fake = Faker()
    fake.add_provider(ApparelProvider)

    items: List[Item] = []
    for iid in range(1, items_per_cat + 1):
        item_id = f"{cid}-{iid}"
        item_name = fake.item_name(name)
        items.append(
            Item(
                id=item_id,
                name=item_name,
                description=fake.item_description(name, item_name),
                price= fake.item_price(name),
                stock=random.randint(5, 50),
            )
        )
    return CategoryWithItems(id=cid, name=name, items=items)

def init_inventory(seed: int = 42):
    random.seed(seed)
    Faker.seed(seed)

    db.drop_tables()

    categories = list(ApparelProvider.types_by_category.keys())
    payload = []
    for cid, cat_name in enumerate(categories, start=1):
        cat_model = build_category(cid, cat_name)
        payload.append(cat_model.model_dump())  # Pydantic v2 dict

    db.insert_multiple(payload)
    print(f"Inventory initialized with {len(payload)} categories and {len(payload)*5} items.")
    return db

if __name__ == "__main__":
    init_inventory()