from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas
from ..database import get_db
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# list order
@router.get("/", response_model=List[schemas.Order])
def read_orders(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    orders = crud.get_orders(db, skip=skip, limit=limit)
    return orders

# create order
@router.post("/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    db_order = crud.create_order(db, order=order) # criando o pedido no bd
    db_order.update_total_order_price() # atualizando o total
    db.commit()
    db.refresh(db_order) # atualizando o objeto
    return db_order

# list one order
@router.get("/{order_id}", response_model=schemas.Order)
def read_order(order_id: int, db: Session = Depends(get_db)):
    db_order = crud.get_order(db=db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # calc total_order_price based on orderitems
    total_price = sum(item.total_price for item in db_order.items)
    db_order.total_order_price = total_price
    
    return db_order

# update order
@router.put("/{order_id}", response_model=schemas.Order)
def update_order(order_id: int, order_update: schemas.OrderUpdate, db: Session = Depends(get_db)):
    # get order in database
    db_order = crud.get_order(db=db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    # update cliente and status, if exists on update
    if order_update.client_id:
        db_order.client_id = order_update.client_id
    if order_update.status:
        db_order.status = order_update.status

    # list for save on updated items
    updated_items = []

    # updade exists items and add new items
    for item_update in order_update.items:
        logger.info(f"Updating item with Product ID: {item_update.product_id}")
        # verify if item exists in order for product_id
        db_item = next((item for item in db_order.items if item.product_id == item_update.product_id), None)
        
        if db_item:
            # if exists item, update quantity
            db_item.quantity = item_update.quantity
            db_item.updated_at = datetime.utcnow()
            updated_items.append(db_item)
        else:
            # if not exists item, create a new item order
            new_item = schemas.OrderItemCreate(**item_update.dict(), order_id=order_id)
            db_item = crud.create_order_item(db=db, order_id=order_id, order_item=new_item)
            updated_items.append(db_item)

    # remove items if not more in order
    items_to_remove = [item for item in db_order.items if item not in updated_items]
    for item in items_to_remove:
        db_order.items.remove(item)

    # update list of items order
    db_order.items.extend([item for item in updated_items if item not in db_order.items])

    # recalc total price od order after update/create/remove items
    db_order.update_total_order_price()

    # commit changes in database
    db.commit()
    
    # refresh in obj db_order for reflect all changes
    db.refresh(db_order)

    return db_order

# delete order
@router.delete("/{order_id}", response_model=dict)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = crud.delete_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": f"Order {order_id} deleted successfully"}


