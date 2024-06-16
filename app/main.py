from fastapi import FastAPI
from app.routers import clients, products, orders

app = FastAPI()

app.include_router(clients.router, prefix="/clients", tags=["clients"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])