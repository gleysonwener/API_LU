from fastapi import APIRouter, Depends, HTTPException, Form, status
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.database import SessionLocal, engine
from passlib.context import CryptContext
from app.security import criar_token_jwt, get_current_user, oauth2_scheme
import bcrypt
from datetime import datetime, timedelta
from app.models import User, funcoes_validas
from typing import List
import json

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/{user_id}/funcoes/{funcao}", response_model=schemas.UserFuncoesResponse)
async def add_funcao_usuario(user_id: int, funcao: str, db: Session = Depends(get_db)):
    usuario = crud.get_user(db, user_id=user_id)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    # Verifica se a função a ser adicionada está na lista de funções válidas
    if funcao not in funcoes_validas:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"A função {funcao} não é uma função válida")

    # Converte a string de funções em uma lista, se existir
    funcoes_list = usuario.funcoes.split(",") if usuario.funcoes else []

    # Verifica se a função já está atribuída ao usuário
    if funcao in funcoes_list:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"A função {funcao} já está atribuída ao usuário")

    # Adiciona a nova função à lista de funções
    funcoes_list.append(funcao)
    usuario.funcoes = ",".join(funcoes_list)

    db.commit()

    # Retorna o usuário com as funções atualizadas como lista
    return schemas.UserFuncoesResponse(
        id=usuario.id,
        username=usuario.username,
        email=usuario.email,
        is_active=usuario.is_active,
        is_admin=usuario.is_admin,
        funcoes=funcoes_list  # Retorna a lista de funções diretamente
    )




@router.delete("/{user_id}/funcoes/{funcao}")
async def remove_funcao_usuario(
    user_id: int,
    funcao: str,
    db: Session = Depends(get_db)
):
    try:
        usuario = crud.get_user(db, user_id=user_id)
        if usuario is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
        
        # Verifica se usuario.funcoes não é None e não está vazio
        if not usuario.funcoes:
            usuario.funcoes = []

        # Converte a string de funções separadas por vírgula em uma lista
        funcoes_list = usuario.funcoes.split(',') if isinstance(usuario.funcoes, str) else usuario.funcoes

        # Verifica se a função está na lista de funções
        if funcao not in funcoes_list:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"A função {funcao} não encontrada para o usuário")
        
        # Remove a função da lista
        funcoes_list.remove(funcao)

        # Converte a lista de volta para uma string separada por vírgula, se necessário
        usuario.funcoes = ','.join(funcoes_list) if isinstance(usuario.funcoes, str) else funcoes_list

        # Commit no banco de dados para atualizar as alterações
        db.commit()
        
        # Atualize o objeto de usuário após o commit
        db.refresh(usuario)

    except Exception as e:
        # Se houver um erro ao commitar, faça o rollback
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        # Sempre feche a conexão com o banco de dados
        db.close()

    return usuario
