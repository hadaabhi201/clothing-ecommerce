"""
FastAPI routers.
"""

from .inventory import router as inventory_router

__all__ = ["inventory_router"]
