from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
import logging

logger = logging.getLogger(__name__)

# PRODUCTS
def get_clients(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Client).offset(skip).limit(limit).all()

def create_client(db: Session, client: schemas.ClientCreate):
    db_client = models.Client(name=client.name, email=client.email, cpf=client.cpf)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def get_client(db: Session, client_id: int):
    return db.query(models.Client).filter(models.Client.id == client_id).first()

def update_client(db: Session, client_id: int, client_update: schemas.ClientUpdate):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    
    if db_client:
        for key, value in client_update.dict(exclude_unset=True).items():
            setattr(db_client, key, value)
        
        db.commit()
        db.refresh(db_client)
    
    return db_client

def delete_client(db: Session, client_id: int):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    db.delete(db_client)
    db.commit()

def get_products(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(
        description=product.description,
        sale_value=product.sale_value,
        barcode=product.barcode,
        section=product.section,
        initial_stock=product.initial_stock,
        expiry_date=product.expiry_date,
        available=product.initial_stock > 0  # Definindo o valor de available
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def update_product(db: Session, product_id: int, product_update: schemas.ProductUpdate):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if db_product:
        for key, value in product_update.dict(exclude_unset=True).items():
            setattr(db_product, key, value)
        
        db.commit()
        db.refresh(db_product)
    
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return db_product
    raise HTTPException(404, detail="Product not found")

# ORDERS
def get_orders(db: Session, skip: int = 0, limit: int = 10):
    orders = db.query(models.Order).offset(skip).limit(limit).all()    
    for order in orders:
        total_price = 0.0
        for item in order.items:
            total_price += item.total_price
        order.total_order_price = total_price
    return orders

def get_order(db: Session, order_id: int):
    logger.info(f"Fetching order with ID: {order_id}")
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def create_order(db: Session, order: schemas.OrderCreate):
    # create order
    db_order = models.Order(client_id=order.client_id, status=order.status)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # add items order
    for item in order.items:
        db_item = models.OrderItem(order_id=db_order.id, product_id=item.product_id, quantity=item.quantity)
        db.add(db_item)
    db.commit()

    # update and return order with items
    db.refresh(db_order)
    return db_order

def update_order(db: Session, order_id: int, order_update: schemas.OrderUpdate):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order:
        if order_update.client_id:
            db_order.client_id = order_update.client_id
        if order_update.status:
            db_order.status = order_update.status
        
        # update items order
        if order_update.items:
            for item_update in order_update.items:
                db_item = db.query(models.OrderItem).filter(
                    models.OrderItem.product_id == item_update.product_id,
                    models.OrderItem.order_id == order_id
                ).first()
                if db_item:
                    db_item.quantity = item_update.quantity
                    db_item.updated_at = datetime.utcnow()
        
        # update total price order
        db_order.update_total_order_price()
        db.commit()
        db.refresh(db_order)
    return db_order

def delete_order(db: Session, order_id: int) -> Optional[schemas.Order]:
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order:
        db.delete(db_order)
        db.commit()
        return db_order
    return None

# ORDER ITEM
def create_order_item(db: Session, order_id: int, order_item: schemas.OrderItemCreate):
    db_order_item = models.OrderItem(**order_item.dict(), order_id=order_id)
    db.add(db_order_item)
    db.commit()
    db.refresh(db_order_item)
    return db_order_item

def get_order_item(db: Session, item_id: int):
    logger.info(f"Fetching order item with ID: {item_id}")
    return db.query(models.OrderItem).filter(models.OrderItem.id == item_id).first()

def get_order_item_by_product_id(db: Session, product_id: int):
    logger.info(f"Fetching order item with Product ID: {product_id}")
    return db.query(models.OrderItem).filter(models.OrderItem.product_id == product_id).first()

def update_order_item(db: Session, item_id: int, order_item_update: schemas.OrderItemUpdate):
    db_order_item = db.query(models.OrderItem).filter(models.OrderItem.id == item_id).first()
    if db_order_item:
        for key, value in order_item_update.dict(exclude_unset=True).items():
            setattr(db_order_item, key, value)
        db.commit()
        db.refresh(db_order_item)
    return db_order_item

def delete_order_item(db: Session, item_id: int):
    db_order_item = db.query(models.OrderItem).filter(models.OrderItem.id == item_id).first()
    if db_order_item:
        db.delete(db_order_item)
        db.commit()
        return db_order_item
    return None