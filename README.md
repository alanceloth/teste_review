# Task Management API (FastAPI)

API de gerenciamento de tarefas construída com FastAPI, SQLAlchemy e SQLite.

## Tecnologias
- Python 3.10+
- FastAPI
- SQLAlchemy
- Pydantic v2
- Uvicorn

## Estrutura do Projeto
```
app/
  __init__.py
  database.py
  main.py
  models.py
  schemas.py
.gitignore
requirements.txt
README.md
AGENTS.md
.coderabbit.yaml
```

## Setup

1) Clone o repositório
- `git clone <url-do-repo>`
- `cd` na pasta do projeto

2) Crie e ative um ambiente virtual
- Windows (PowerShell):
  - `python -m venv venv`
  - `venv\Scripts\Activate.ps1`
- macOS/Linux (bash/zsh):
  - `python3 -m venv venv`
  - `source venv/bin/activate`

3) Instale as dependências
- `pip install -r requirements.txt`

4) Rode a aplicação
- `uvicorn app.main:app --reload`

A aplicação estará acessível em `http://127.0.0.1:8000`.

### Variáveis de ambiente
- `SECRET_KEY` (obrigatória em produção): chave secreta para assinar JWT. Recomendado mínimo de 32 caracteres.
- `APP_ENV` (opcional): defina como `production` para exigir `SECRET_KEY` no startup. Em desenvolvimento, uma chave temporária é gerada e um aviso é exibido.

## Testando a API
- Documentação interativa (Swagger): `http://127.0.0.1:8000/docs`
- Documentação alternativa (ReDoc): `http://127.0.0.1:8000/redoc`

## Endpoints
- GET `/` — mensagem de boas-vindas
- POST `/tasks/` — cria uma tarefa
- GET `/tasks/` — lista tarefas (params: `skip`, `limit`, `completed`)
- GET `/tasks/{task_id}` — obtém tarefa por ID
- PUT `/tasks/{task_id}` — atualiza tarefa
- DELETE `/tasks/{task_id}` — remove tarefa

## Exemplos (curl)

Criar tarefa:
```
curl -X POST "http://127.0.0.1:8000/tasks/" \
  -H "Content-Type: application/json" \
  -d '{"title": "Estudar FastAPI", "description": "Ler docs oficiais"}'
```

Listar tarefas (10 primeiras):
```
curl "http://127.0.0.1:8000/tasks/?skip=0&limit=10"
```

Filtrar concluídas:
```
curl "http://127.0.0.1:8000/tasks/?completed=true"
```

Obter por ID:
```
curl "http://127.0.0.1:8000/tasks/1"
```

Atualizar tarefa:
```
curl -X PUT "http://127.0.0.1:8000/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{"completed": true, "title": "Estudar FastAPI (revisto)"}'
```

Remover tarefa:
```
curl -X DELETE "http://127.0.0.1:8000/tasks/1"
```

## Notas
- O banco SQLite é criado automaticamente como `tasks.db` na raiz do projeto.
- Campos de criação e atualização seguem validações do Pydantic v2.

## Autenticação (JWT)

O projeto possui autenticação por JWT (OAuth2 password flow) e proteção das rotas de tarefas por usuário.

### Cadastro
```
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"secret123"}'
```

### Login (form-data OAuth2)
```
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=secret123"
```
Resposta:
```
{"access_token":"<JWT>","token_type":"bearer"}
```

### Usuário atual (token Bearer)
```
curl "http://127.0.0.1:8000/auth/me" \
  -H "Authorization: Bearer <JWT>"
```

### Usando token nas rotas de tarefas
Inclua o header `Authorization: Bearer <JWT>`:
```
curl -X POST "http://127.0.0.1:8000/tasks/" \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Pagar contas","description":"Luz e água"}'
```

Observação: se já existir um `tasks.db` de versão anterior, exclua-o para recriar as tabelas com usuários e relacionamentos.
