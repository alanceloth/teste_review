# Padrões para este projeto

Este repositório segue as seguintes diretrizes para código Python e FastAPI.

## Estilo de Código
- PEP 8 para formatação e organização de código.
- Type hints obrigatórios em funções públicas.
- Imports organizados (padrão: stdlib, terceiros, local) e absolutos quando possível.
- Sem comentários redundantes; prefira nomes claros e docstrings.

## Docstrings
- Use docstrings em todas as funções públicas, classes e endpoints.
- Formato simples, objetivo, em português quando fizer sentido.
- Inclua o que a função faz, parâmetros relevantes e retorno.

## Estrutura
- `app/database.py`: engine, sessão, Base e `get_db`.
- `app/models.py`: modelos SQLAlchemy.
- `app/schemas.py`: schemas Pydantic (v2).
- `app/main.py`: inicialização do FastAPI e rotas.

## Convenções FastAPI
- Utilize `Depends(get_db)` para injeção de sessão.
- Lance `HTTPException(status_code=404)` para recursos não encontrados.
- Configure `response_model` nas rotas que retornam dados.
- Use `status.HTTP_201_CREATED` e `status.HTTP_204_NO_CONTENT` quando aplicável.

## Validação
- Pydantic v2 com `Field` para restrições (min/max_length, etc.).
- `TaskResponse` com `model_config = ConfigDict(from_attributes=True)`.
- `TaskUpdate` deve considerar todos os campos opcionais e usar `exclude_unset`.

## Banco de Dados
- SQLite local (`sqlite:///./tasks.db`).
- Criação das tabelas no startup por `models.Base.metadata.create_all(bind=engine)`.

## Testes (quando aplicável)
- Prefira criar fixtures para sessão em memória.
- Teste de integração usando `TestClient` do FastAPI.

