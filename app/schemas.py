from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# AUTH

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    funcoes: List[str] = []

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    id: int
    username: str
    email: str
    funcoes: List[str]

class UserFuncoesResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    funcoes: List[str]

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# # PERMISSION
# class PermissionBase(BaseModel):
#     name: str

# class PermissionCreate(PermissionBase):
#     pass

# class Permission(PermissionBase):
#     id: int
#     name: str
    
#     class Config:
#         orm_mode = True

# # ROLES
# class RoleBase(BaseModel):
#     name: str

# class RoleCreate(RoleBase):
#     pass

# class Role(RoleBase):
#     id: int
#     permissions: List[Permission] = []

#     class Config:
#         orm_mode = True




# CLIENTS
class ClientBase(BaseModel):
    name: str
    email: EmailStr

class ClientCreate(ClientBase):
    cpf: str

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    cpf: Optional[str] = None

class Client(ClientBase):
    id: int
    cpf: str

    class Config:
        orm_mode = True

# PRODUCTS
class ProductBase(BaseModel):
    description: str
    sale_value: float
    barcode: str
    section: str
    initial_stock: int
    expiry_date: Optional[datetime] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    description: Optional[str] = None
    sale_value: Optional[float] = None
    barcode: Optional[str] = None
    section: Optional[str] = None
    initial_stock: Optional[int] = None
    expiry_date: Optional[datetime] = None

class Product(ProductBase):
    id: int
    available: Optional[bool] = None 

    class Config:
        orm_mode = True

# ORDER ITEM
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemUpdate(BaseModel):
    product_id: int
    quantity: Optional[int] = Field(None, gt=0)

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    product_id: int
    quantity: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    total_price: float
    

    class Config:
        orm_mode = True

# ORDERS
class OrderBase(BaseModel):
    client_id: int
    status: str

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    client_id: Optional[int] = None
    status: Optional[str] = None
    items: Optional[List[OrderItemUpdate]] = None

class Order(OrderBase):
    id: int
    client_id: int
    status: str
    items: List[OrderItem] = []
    total_order_price: float = Field(..., alias="total_order_price")

    class Config:
        orm_mode = True