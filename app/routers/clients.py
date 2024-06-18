from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas
from ..database import get_db, SessionLocal
from app.security import get_current_user, get_user_com_funcao
from sqlalchemy.exc import IntegrityError

import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# desprotegida
# @router.get("/", response_model=List[schemas.Client])
# def read_clients(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     clients = crud.get_clients(db, skip=skip, limit=limit)
#     return clients

# protegida
# @router.get("/", response_model=List[schemas.Client])
# def read_clients(current_user: str = Depends(get_current_user), skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     # clients = crud.get_clients(db, skip=skip, limit=limit)
#     return clients
# Rota para ler clientes com filtros opcionais

# desprotegida
@router.get("/", response_model=List[schemas.Client])
def read_clients(
    name: str = Query(None, description="Filtrar cliente pelo nome"),
    email: str = Query(None, description="Filtrar cliente pelo email"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Client)
    
    if name:
        query = query.filter(models.Client.name.ilike(f"%{name}%"))
        
    if email:
        query = query.filter(models.Client.email.ilike(f"%{email}%"))

    clients = query.all()
    
    return clients

# protegida
@router.get("/", response_model=List[schemas.Client])
def read_clients(
    name: str = Query(None, description="Filtrar cliente pelo nome"),
    email: str = Query(None, description="Filtrar cliente pelo email"),
    db: Session = Depends(get_db), current_user: str = Depends(get_current_user)
):
    query = db.query(models.Client)
    
    if name:
        query = query.filter(models.Client.name.ilike(f"%{name}%"))
        
    if email:
        query = query.filter(models.Client.email.ilike(f"%{email}%"))
  
    clients = query.all()
    
    return clients



# desprotegida
@router.post("/", response_model=schemas.Client)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    db_client = crud.create_client(db, client=client)
    return db_client

# # protegida
# @router.post("/", response_model=schemas.Client)
# def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
#     db_client = crud.create_client(db, client=client)
#     return db_client


# @router.post("/", response_model=schemas.Client)
# def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
#     # Verificar se o email já está em uso
#     existing_email = db.query(models.Client).filter(models.Client.email == client.email).first()
#     if existing_email:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

#     # Verificar se o CPF já está em uso
#     existing_cpf = db.query(models.Client).filter(models.Client.cpf == client.cpf).first()
#     if existing_cpf:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CPF already registered")

#     # Se tudo estiver válido, criar o cliente
#     try:
#         db_client = crud.create_client(db, client=client)
#         return db_client
#     except IntegrityError:
#         db.rollback()
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create client")



@router.post("/", response_model=schemas.Client)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    # Verificar se o email já está em uso
    existing_email = db.query(models.Client).filter(models.Client.email == client.email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email already registered")

    # Verificar se o CPF já está em uso
    existing_cpf = db.query(models.Client).filter(models.Client.cpf == client.cpf).first()
    if existing_cpf:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CPF already registered")

    # Se tudo estiver válido, criar o cliente
    try:
        db_client = crud.create_client(db, client=client)
        return db_client
    except IntegrityError as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e.orig):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CPF or email already registered")
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create client")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    

# desprotegida
@router.get("/{client_id}", response_model=schemas.Client)
def read_client(client_id: int, db: Session = Depends(get_db)):
    db_client = crud.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client

# protegida
@router.get("/{client_id}", response_model=schemas.Client)
def read_client(client_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    db_client = crud.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client

# desprotegida
@router.put("/{client_id}", response_model=schemas.Client)
def update_client(client_id: int, client_update: schemas.ClientUpdate, db: Session = Depends(get_db)):
    updated_client = crud.update_client(db, client_id, client_update)
    if updated_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return updated_client

# protegida
@router.put("/{client_id}", response_model=schemas.Client)
def update_client(client_id: int, client_update: schemas.ClientUpdate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    updated_client = crud.update_client(db, client_id, client_update)
    if updated_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return updated_client

# desprotegida
@router.delete("/{client_id}", response_model=dict)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    db_client = crud.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    crud.delete_client(db, client_id=client_id)
    return {"message": f"Client {client_id} deleted successfully"}

# protegida
@router.delete("/{client_id}", response_model=dict)
def delete_client(client_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    db_client = crud.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    crud.delete_client(db, client_id=client_id)
    return {"message": f"Client {client_id} deleted successfully"}



