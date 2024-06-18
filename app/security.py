from datetime import datetime, timedelta
import os
from typing import Any, Union
from passlib.context import CryptContext
from jose import jwt, JWTError
from dotenv import load_dotenv

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from .database import SessionLocal
from . import models
from .schemas import TokenData
from fastapi.security import HTTPBearer
from typing import List

from .models import User
import logging

oauth2_scheme = HTTPBearer()

load_dotenv()

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

SECRET_KEY = os.getenv('SECRET_KEY', 'sadasddsadsasad')
JWT_ALGORITHM = os.getenv('ALGORITHM', 'HS512')
ACCESS_TOKEN_EXPIRE_HOURS = 24

def criar_token_jwt(subject: Union[str, Any]) -> str:
    expire = datetime.utcnow() + timedelta(
        hours=ACCESS_TOKEN_EXPIRE_HOURS
    )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.JWTError:
        return None

# def get_current_user(db: Session = Depends(SessionLocal), token: str = Depends(oauth2_scheme)):
#     payload = decode_token(token.credentials)
#     if payload is None:
#         raise HTTPException(status_code=401, detail="Invalid token")
#     username: str = payload.get("sub")
#     user = db.query(models.User).filter(models.User.username == username).first()
#     if user is None:
#         raise HTTPException(status_code=401, detail="User not found")
#     return user


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

        
def get_current_user(db: Session = Depends(SessionLocal), token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    username: str = payload.get("sub")
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user



def get_user_com_funcao(funcoes: List[str] = []):
    def inner(usuario_logado: User = Depends(get_current_user)) -> User:
        if not len(funcoes):
            return usuario_logado
        
        for funcao in funcoes:
            if funcao in usuario_logado.funcoes.split(','):
                return usuario_logado

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="O usuário não possui permissão para realizar essa ação!"
        )
    return inner
