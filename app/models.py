from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

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
    section = Column(String)
    initial_stock = Column(Integer)
    expiry_date = Column(DateTime)
    available = Column(Boolean, default=True)
    order_items = relationship("OrderItem", back_populates="product")
