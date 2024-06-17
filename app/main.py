from fastapi import FastAPI
from app.routers import clients, products, orders, users, permissions, roles

app = FastAPI()

app.include_router(users.router, prefix="/auth", tags=["auth"])
app.include_router(roles.router, prefix="/roles", tags=["roles"])
app.include_router(permissions.router, prefix="/permissions", tags=["permissions"])
app.include_router(clients.router, prefix="/clients", tags=["clients"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
# app.include_router(auth.router, prefix="/auth", tags=["auth"])