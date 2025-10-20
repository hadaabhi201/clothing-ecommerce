import asyncio
from typing import Any, Dict, Optional
import httpx
from common.config import inventory_api_setting

class InventoryClient:
    """
    Async client for Inventory Service.
    Expects Inventory API:
      - GET /categories -> {"categories":[{"id":1,"name":"..."}]}
      - GET /categories/{category_id}/items -> {"category": {... or name}, "items":[...]}
      - GET /categories/{category_id}/items/{item_id} -> Item JSON
    """
    def __init__(self):
        self.base_url = inventory_api_setting.INVENTORY_BASE_URL
        self.timeout = inventory_api_setting.HTTP_TIMEOUT_SECONDS
        self.retries = inventory_api_setting.HTTP_RETRIES
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)
    
    async def aclose(self) -> None:
        await self._client.aclose()
    
    async def _get(self, url: str) -> httpx.Response:
        last_exc: Optional[Exception] = None
        for attempt in range(self.retries - 1):
            try:
                r = await self._client.get(url)
                r.raise_for_status()
                return r
            except Exception as e:
                last_exc = e
                await asyncio.sleep(0.1 * (2 ** attempt))
        raise last_exc    
    
    async def find_item(self,  item_id: str) -> Dict[str, Any]:
        response = await self._get(f"/items/{item_id}")
        return response.json()

    async def is_available(self, item_id: str, quantity: int) -> bool:
        item = await self.find_item(item_id)
        return int(item.get("stock", 0)) >= quantity
