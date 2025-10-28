from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

from . import models, schemas
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
def create_task(task_in: schemas.TaskCreate, db: Session = Depends(get_db)) -> models.Task:
    """Cria uma nova tarefa."""

    task = models.Task(title=task_in.title, description=task_in.description)
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
) -> List[models.Task]:
    """Retorna uma lista paginada de tarefas, com filtro opcional por conclusão."""

    query = db.query(models.Task)
    if completed is not None:
        query = query.filter(models.Task.completed == completed)
    tasks = query.order_by(models.Task.id).offset(skip).limit(limit).all()
    return tasks


@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse, tags=["Tasks"])
def get_task(task_id: int, db: Session = Depends(get_db)) -> models.Task:
    """Busca uma tarefa pelo seu ID."""

    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return task


@app.put("/tasks/{task_id}", response_model=schemas.TaskResponse, tags=["Tasks"])
def update_task(
    task_id: int, task_in: schemas.TaskUpdate, db: Session = Depends(get_db)
) -> models.Task:
    """Atualiza campos de uma tarefa existente."""

    task = db.query(models.Task).filter(models.Task.id == task_id).first()
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
def delete_task(task_id: int, db: Session = Depends(get_db)) -> None:
    """Remove uma tarefa pelo ID."""

    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    db.delete(task)
    db.commit()
    return None

