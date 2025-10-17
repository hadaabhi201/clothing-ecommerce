from faker.providers import BaseProvider
import random

class ApparelProvider(BaseProvider):
    types_by_category = {
        "Tops": ["Tee", "Oxford Shirt", "Polo", "Henley", "Linen Shirt", "Hoodie", "Sweatshirt"],
        "Bottoms": ["Chinos", "Jeans", "Trousers", "Joggers", "Shorts", "Cargo Pants"],
        "Dresses": ["Wrap Dress", "Maxi Dress", "Slip Dress", "Shirt Dress", "A-line Dress"],
        "Outerwear": ["Denim Jacket", "Bomber Jacket", "Puffer Jacket", "Wool Coat", "Trench"],
        "Activewear": ["Training Tee", "Leggings", "Running Shorts", "Track Jacket", "Compression Top"],
        "Footwear": ["Sneakers", "Running Shoes", "Loafers", "Chelsea Boots", "Slides", "Sandals"],
        "Accessories": ["Leather Belt", "Scarf", "Cap", "Beanie", "Sunglasses"],
        "Swimwear": ["Swim Trunks", "One-piece", "Bikini Set", "Rash Guard"],
        "Sleepwear": ["Pajama Set", "Sleep Tee", "Robe", "Slippers", "Short Pajamas"],
        "Kids": ["Graphic Tee", "Joggers", "Hoodie", "Denim", "Sneakers"],
    }

    def item_name(self, category: str) -> str:
        base = random.choice(self.types_by_category[category])
        adj = random.choice(["Classic", "Premium", "Essential", "Urban", "Heritage", "Athletic"])
        return f"{adj} {base}"

    def item_description(self, category: str, name: str) -> str:
        return f"{name} designed for comfort and everyday wear."

    def item_price(self, category: str) -> float:
        return round(random.uniform(15, 150), 2)