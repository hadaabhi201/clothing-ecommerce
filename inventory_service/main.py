from fastapi import FastAPI
from inventory_service.routers import inventory
from inventory_service.core.db_init import init_inventory
from contextlib import asynccontextmanager

@asynccontextmanager

async def lifespan(app: FastAPI):
    init_inventory()  # seed db on startup
    yield
    # Shutdown logic (optional)

app = FastAPI(title="Inventory Service",lifespan=lifespan)
app.include_router(inventory.router, prefix="", tags=["Inventory"])