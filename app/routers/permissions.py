from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# listar permissões
@router.get("/permissions/", response_model=list[schemas.Permission])
def list_permissions(db: Session = Depends(get_db)):
    permissions = crud.get_permissions(db)
    return permissions


# criar nova permissão
@router.post("/permissions/", response_model=schemas.Permission)
def create_permission(name: str, db: Session = Depends(get_db)):
    existing_permission = crud.create_permission(db, name)
    if existing_permission:
        raise HTTPException(status_code=400, detail="Permission already exists")
    
    permission = crud.create_permission(db, name=name)
    return permission


# associar uma permissão a um grupo de usuários
@router.post("/permissions/{permission_id}/assign/{role_id}/")
def assign_permission_to_role(permission_id: int, role_id: int, db: Session = Depends(get_db)):
    permission = crud.get_permission_by_id(db, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    role = crud.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    if permission in role.permissions:
        raise HTTPException(status_code=400, detail="Permission already assigned to role")
    
    role.permissions.append(permission)
    db.commit()
    return {"message": "Permission assigned to role successfully"}

# lista permissões de um grupo específico
@router.get("/roles/{role_id}/permissions/", response_model=list[schemas.Permission])
def list_permissions_by_role(role_id: int, db: Session = Depends(get_db)):
    permissions = crud.get_permissions_by_role_id(db, role_id)
    if not permissions:
        raise HTTPException(status_code=404, detail="Permissions not found")
    return permissions