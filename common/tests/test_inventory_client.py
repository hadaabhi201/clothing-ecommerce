from unittest.mock import AsyncMock, patch

import pytest
from httpx import Request, RequestError, Response, TimeoutException

from common.config import InventoryAPIConfig
from common.inventory_client import InventoryClient


@pytest.fixture(autouse=True)
def mock_inventory_api_settings(monkeypatch):
    mock_settings = InventoryAPIConfig(
        INVENTORY_BASE_URL="http://mock-inventory-api", HTTP_TIMEOUT_SECONDS=1.0, HTTP_RETRIES=2
    )
    monkeypatch.setattr("common.config.inventory_api_setting", mock_settings)
    return mock_settings


@pytest.mark.asyncio
async def test_find_item_success():
    mock_response = Response(
        200,
        json={"id": "item123", "stock": 10},
        request=Request("GET", "http://mock-inventory-api/items/item123"),
    )

    with patch(
        "common.inventory_client.inventory_client.httpx.AsyncClient.get", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_response

        client = InventoryClient()
        result = await client.find_item("item123")

        assert result == {"id": "item123", "stock": 10}
        mock_get.assert_awaited_once_with("/items/item123")


@pytest.mark.asyncio
async def test_is_available_true():
    mock_response = Response(
        200,
        json={"id": "1-12", "stock": 10},
        request=Request("GET", "http://mock-inventory-api/items/1-12"),
    )

    with patch(
        "common.inventory_client.inventory_client.httpx.AsyncClient.get", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_response

        client = InventoryClient()

        assert await client.is_available("item123", 5) is True


@pytest.mark.asyncio
async def test_is_available_false():
    mock_response = Response(
        200,
        json={"id": "1-12", "stock": 10},
        request=Request("GET", "http://mock-inventory-api/items/1-12"),
    )

    with patch(
        "common.inventory_client.inventory_client.httpx.AsyncClient.get", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_response

        client = InventoryClient()

        assert await client.is_available("item123", 50) is False


@pytest.mark.asyncio
async def test_get_retries_on_failure():
    client = InventoryClient()

    # First call raises an exception, second succeeds
    mock_response = Response(
        200,
        json={"id": "item123", "stock": 10},
        request=Request("GET", "http://mock-inventory-api/items/item123"),
    )

    with patch.object(client._client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = [RequestError("temporary fail"), mock_response]

        result = await client.find_item("item123")

        assert result == {"id": "item123", "stock": 10}
        assert mock_get.call_count == 2


@pytest.mark.asyncio
async def test_get_raises_final_exception(mock_inventory_api_settings):
    client = InventoryClient()

    with patch.object(client._client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = RequestError("All attempts failed")

        with pytest.raises(RequestError, match="All attempts failed"):
            await client.find_item("item123")

        assert mock_get.call_count == mock_inventory_api_settings.HTTP_RETRIES


@pytest.mark.asyncio
async def test_get_timeout_retries_and_fails(mock_inventory_api_settings):
    client = InventoryClient()

    with patch.object(client._client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = TimeoutException("Timeout!")

        with pytest.raises(TimeoutException):
            await client.find_item("item123")

        assert mock_get.call_count == mock_inventory_api_settings.HTTP_RETRIES
