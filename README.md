## Tiny RAG

A Tiny Agent Workflow AI Application

### Features

- RAG
- Customize Tools


## How to

### startup the project

```shell
uv init
uv add fastapi uvicorn gunicorn sqlmodel pydantic pydantic-settings pymysql

# mypy: static type check
# ruff: code smell check
uv add --dev pytest mypy ruff coverage

uv add langchain langgraph langchain_ollama langchain_openai

uv add cachetools types-cachetools
```

### run the project

```sql
create database tinyrag;
create user 'tinyrag'@'%' identified by 'tinyrag';
grant all privileges on tinyrag.* to 'tinyrag'@'%';
```

```shell
cp .env.example .env

export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
sed -i "s/SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY}/" .env

#export ENVIRONMENT=production

uv sync
source .venv/bin/activate

# or just run: pytest
coverage run --source=app -m pytest
coverage report --show-missing
coverage html --title "${@-coverage}"
```

```shell
# on local machine
./scripts/run.sh

# on production machine
./scripts/build_docker.sh

curl http://localhost:8000/api/v1/openapi.json
```
