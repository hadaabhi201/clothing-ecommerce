import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class InventoryAPIConfig(BaseModel):
    INVENTORY_BASE_URL: str = Field(
        default_factory=lambda: os.getenv("INVENTORY_BASE_URL", "http://localhost:8000")
    )
    HTTP_TIMEOUT_SECONDS: float = Field(
        default_factory=lambda: float(os.getenv("HTTP_TIMEOUT_SECONDS", "5.0"))
    )
    HTTP_RETRIES: int = Field(default_factory=lambda: int(os.getenv("HTTP_RETRIES", "3")))


def load_inventory_api() -> InventoryAPIConfig:
    return InventoryAPIConfig()


inventory_api_setting: InventoryAPIConfig = load_inventory_api()
