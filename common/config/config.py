import os

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class InventoryAPIConfig(BaseModel):
    INVENTORY_BASE_URL: str = os.getenv("INVENTORY_BASE_URL")
    HTTP_TIMEOUT_SECONDS: float = float(os.getenv("HTTP_TIMEOUT_SECONDS"))
    HTTP_RETRIES: int = int(os.getenv("HTTP_RETRIES"))


def load_inventory_api() -> InventoryAPIConfig:
    return InventoryAPIConfig()


inventory_api_setting: InventoryAPIConfig = load_inventory_api()
