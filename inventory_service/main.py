from fastapi import FastAPI
from inventory_service.routers import inventory
from inventory_service.core.db_init import init_inventory

app = FastAPI(title="Inventory Service")

@app.on_event("startup")
def startup_event():
    init_inventory()  # seed db on startup

app.include_router(inventory.router, prefix="", tags=["Inventory"])