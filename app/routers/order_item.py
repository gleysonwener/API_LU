from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas
from ..database import get_db

router = APIRouter()

@router.post("/order_items/{order_id}", response_model=schemas.OrderItem)
def create_order_item(order_id: int, order_item: schemas.OrderItemCreate, db: Session = Depends(get_db)):
    return crud.create_order_item(db=db, order_id=order_id, order_item=order_item)

@router.get("/order_items/{item_id}", response_model=schemas.OrderItem)
def read_order_item(item_id: int, db: Session = Depends(get_db)):
    db_order_item = crud.get_order_item(db=db, item_id=item_id)
    if db_order_item is None:
        raise HTTPException(status_code=404, detail="Order Item not found")
    return db_order_item

@router.put("/order_items/{item_id}", response_model=schemas.OrderItem)
def update_order_item(item_id: int, order_item_update: schemas.OrderItemUpdate, db: Session = Depends(get_db)):
    db_order_item = crud.update_order_item(db=db, item_id=item_id, order_item_update=order_item_update)
    if db_order_item is None:
        raise HTTPException(status_code=404, detail="Order Item not found")
    return db_order_item

@router.delete("/order_items/{item_id}", response_model=schemas.OrderItem)
def delete_order_item(item_id: int, db: Session = Depends(get_db)):
    db_order_item = crud.delete_order_item(db=db, item_id=item_id)
    if db_order_item is None:
        raise HTTPException(status_code=404, detail="Order Item not found")
    return db_order_item