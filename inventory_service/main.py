from fastapi import FastAPI
from contextlib import asynccontextmanager
from inventory_service.routers import inventory
from inventory_service.core.db_init import init_inventory

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_inventory()
    yield
    # Shutdown
    # (nothing to clean up now, but could close DB or connections later)

app = FastAPI(title="Inventory Service", lifespan=lifespan)

app.include_router(inventory.router, tags=["Inventory"])