from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas
from .auth import (
    DUMMY_PASSWORD_HASH,
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from .database import engine, get_db


app = FastAPI(
    title="Task Management API",
    description="API para gerenciamento de tarefas com FastAPI, SQLAlchemy e SQLite.",
    version="1.0.0",
)


# Create DB tables on startup
models.Base.metadata.create_all(bind=engine)


@app.get("/", tags=["Root"])
def read_root() -> dict:
    """Endpoint raiz que retorna uma mensagem de boas-vindas."""

    return {"message": "Bem-vindo(a) à Task Management API"}


@app.post(
    "/tasks/",
    response_model=schemas.TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"],
)
def create_task(
    task_in: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> models.Task:
    """Cria uma nova tarefa do usuário autenticado."""

    task = models.Task(
        title=task_in.title, description=task_in.description, user_id=current_user.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get("/tasks/", response_model=List[schemas.TaskResponse], tags=["Tasks"])
def list_tasks(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(10, ge=1, le=100, description="Limite de registros"),
    completed: Optional[bool] = Query(
        None, description="Filtrar por status de conclusão (true/false)"
    ),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> List[models.Task]:
    """Lista tarefas do usuário autenticado, com paginação e filtro de conclusão."""

    query = db.query(models.Task).filter(models.Task.user_id == current_user.id)
    if completed is not None:
        query = query.filter(models.Task.completed == completed)
    tasks = query.order_by(models.Task.id).offset(skip).limit(limit).all()
    return tasks


@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse, tags=["Tasks"])
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> models.Task:
    """Busca uma tarefa do usuário autenticado pelo ID."""

    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.user_id == current_user.id)
        .first()
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return task


@app.put("/tasks/{task_id}", response_model=schemas.TaskResponse, tags=["Tasks"])
def update_task(
    task_id: int,
    task_in: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> models.Task:
    """Atualiza campos de uma tarefa do usuário autenticado."""

    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.user_id == current_user.id)
        .first()
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    data = task_in.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(task, key, value)

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> None:
    """Remove uma tarefa do usuário autenticado pelo ID."""

    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.user_id == current_user.id)
        .first()
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    db.delete(task)
    db.commit()
    return None


# ==== Autenticação ====

@app.post("/auth/register", response_model=schemas.UserResponse, tags=["Auth"])
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)) -> models.User:
    """Registra um novo usuário com senha hash e valida unicidade."""

    user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="User with given credentials already exists"
        )
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=schemas.Token, tags=["Auth"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> schemas.Token:
    """Efetua login por formulário OAuth2 e retorna token JWT."""

    user = (
        db.query(models.User).filter(models.User.username == form_data.username).first()
    )
    # Caminho de verificação constante para evitar vazamento temporal
    hashed = user.hashed_password if user else DUMMY_PASSWORD_HASH
    password_ok = verify_password(form_data.password, hashed)
    if user is None or not password_ok:
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = create_access_token({"sub": user.username})
    return schemas.Token(access_token=token, token_type="bearer")


@app.get("/auth/me", response_model=schemas.UserResponse, tags=["Auth"])
def read_me(current_user: models.User = Depends(get_current_user)) -> models.User:
    """Retorna o usuário atual para o token fornecido."""

    return current_user
