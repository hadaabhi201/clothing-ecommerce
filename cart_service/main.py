from fastapi import FastAPI

from cart_service.routers import cart

app = FastAPI(title="Cart Service")

app.include_router(cart.router, prefix="", tags=["Cart"])
