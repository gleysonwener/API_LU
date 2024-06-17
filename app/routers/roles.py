from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.database import SessionLocal
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# lista todos os grupos de usuários
@router.get("/roles/", response_model=list[schemas.Role])
def list_roles(db: Session = Depends(get_db)):
    roles = crud.get_role(db)
    return roles


# cria novo grupo de usuário
@router.post("/roles/", response_model=schemas.Role)
def create_role(name: str, db: Session = Depends(get_db)):
    existing_role = crud.get_role_by_name(db, name)
    if existing_role:
        raise HTTPException(status_code=400, detail="Role already exists")
    
    role = crud.create_role(db, name=name)
    return role


# associa um usuário a um grupo de usuários
@router.post("/roles/{role_id}/assign/user/{user_id}/")
def assign_user_to_role(
    role_id: int = Path(..., title="The ID of the role to assign to the user"),
    user_id: int = Path(..., title="The ID of the user to assign to the role"),
    db: Session = Depends(get_db)
):
    role = crud.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.role_id = role.id  # Assuming 'role_id' is the foreign key in 'User' model

    db.commit()
    return {"message": "User assigned to role successfully"}

# Endpoint para listar usuários de um grupo específico
@router.get("/roles/{role_id}/users/", response_model=List[schemas.User])
def list_users_in_role(role_id: int, db: Session = Depends(get_db)):
    role = crud.get_role_by_id(db, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail=f"Role with id {role_id} not found")

    users = crud.get_users_by_role_id(db, role_id)
    return users