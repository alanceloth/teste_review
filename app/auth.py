"""Autenticação e utilitários de segurança.

Variáveis de ambiente suportadas:
- SECRET_KEY: chave secreta JWT obrigatória em produção (>= 32 caracteres).
- APP_ENV (ou ENV): ambiente de execução; quando 'production' falha o startup
  se SECRET_KEY não for fornecida. Em desenvolvimento, uma chave temporária é
  gerada e um aviso é logado.
"""

import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from . import models
from .database import get_db


def _load_secret_key() -> str:
    env = (os.getenv("APP_ENV") or os.getenv("ENV") or "development").lower()
    key = os.getenv("SECRET_KEY")

    def _is_weak(v: str) -> bool:
        return len(v) < 32

    if key and _is_weak(key):
        raise RuntimeError(
            "SECRET_KEY muito curta. Defina uma chave com pelo menos 32 caracteres."
        )

    if key:
        return key

    if env in {"production", "prod"}:
        raise RuntimeError(
            "SECRET_KEY ausente em produção. Defina a variável de ambiente SECRET_KEY."
        )

    tmp = secrets.token_urlsafe(48)
    logging.warning(
        "SECRET_KEY não definida. Usando chave temporária apenas para desenvolvimento. "
        "Defina SECRET_KEY para persistência e segurança."
    )
    return tmp


SECRET_KEY = _load_secret_key()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logging.getLogger("passlib").setLevel(logging.WARNING)
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    """Gera hash seguro para a senha fornecida."""

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica uma senha em texto contra seu hash armazenado."""

    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um token JWT assinado contendo os dados informados."""

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decodifica e valida um token JWT retornando seu payload."""

    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    """Dependency que retorna o usuário autenticado a partir do token Bearer."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# Dummy hash para caminho de comparação constante em checagens de senha
DUMMY_PASSWORD_HASH = pwd_context.hash("dummy-password-please-ignore")
