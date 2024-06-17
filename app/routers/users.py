from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.database import SessionLocal, engine
from passlib.context import CryptContext
from app.security import criar_token_jwt, get_current_user, oauth2_scheme
import bcrypt
from datetime import datetime, timedelta


router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# lista todos os  usuários
@router.get("/users", response_model=list[schemas.User])
def list_users(db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return users

@router.post("/register/")
def register_user(
    username: str = Form(...), 
    email: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_email = crud.get_user_by_email(db, email=email)
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(password)
    
    user = models.User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "User created successfully"}



@router.post("/login/")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=username)
    if not user or not user.verify_password(password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Gerar o token JWT real
    access_token = criar_token_jwt(user.id)
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/auth/refresh")
def refresh_access_token(current_user: models.User = Depends(get_current_user)):
    # Gerar um novo token JWT com base no ID do usuário
    access_token_expires = timedelta(hours=24)
    expire = datetime.utcnow() + access_token_expires
    new_token = criar_token_jwt(current_user.username, expire)

    # Retornar o novo token JWT
    return {"access_token": new_token, "token_type": "bearer"}




# Exemplo de endpoint protegido
@router.get("/users", response_model=list[schemas.User])
def list_users(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    users = crud.get_users(db)
    return users