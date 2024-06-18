from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime, Numeric, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from passlib.context import CryptContext
import bcrypt
import pydantic

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base = declarative_base()


funcoes_validas = ["admin", "usuario_regular"]

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    # funcoes = Column(String, default="{}")
    funcoes = Column(String)
    
    def verify_password(self, password: str):
        return pwd_context.verify(password, self.hashed_password)

    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)

    # @validator('funcoes')
    def valida_funcao_existem(cls, v):
        if not isinstance(v, list):
            raise ValueError(f'As funções de um usuário deve ser uma lista!')
        for funcao in v:
            if not isinstance(funcao, str) or funcao not in funcoes_validas:
                raise ValueError(f'A função {funcao} não é um função válida!')
        return v

    # @validator('funcoes')
    def remove_funcoes_duplicadas(cls, v):
        return list(set(v))
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "funcoes": self.funcoes.split(",") if self.funcoes else []
        }

    @staticmethod
    def from_dict(data):
        return User(
            username=data.get('username'),
            email=data.get('email'),
            hashed_password=data.get('hashed_password'),
            is_active=data.get('is_active', True),
            is_admin=data.get('is_admin', False),
            funcoes=",".join(data.get('funcoes', []))
        )


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    cpf = Column(String, unique=True, index=True)
    orders = relationship("Order", back_populates="client")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    status = Column(String)
    total_order_price = Column(Numeric(10, 2), default=0.0)
    client = relationship("Client", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

    # calc total price order
    def update_total_order_price(self):
        total = sum(item.total_price for item in self.items)
        self.total_order_price = total

    def as_dict(self):
        return {
            "id": self.id,
            "client_id": self.client_id,
            "status": self.status,
            "total_order_price": float(self.total_order_price),
            "items": [item.as_dict() for item in self.items]
        }

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    order = relationship("Order", back_populates="items")
    product = relationship("Product")

    @property
    def total_price(self):
        return self.quantity * self.product.sale_value

    def as_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "total_price": self.total_price,
            "created_at": self.created_at,
        }

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    sale_value = Column(Float)
    barcode = Column(String)
    category = Column(String)
    initial_stock = Column(Integer)
    expiry_date = Column(DateTime)
    available = Column(Boolean, default=True)
    order_items = relationship("OrderItem", back_populates="product")
