# Micro-Savings Habit Analyzer Backend

FastAPI backend for the Micro-Savings Habit Analyzer.

## Requirements

- Python 3.11+
- PostgreSQL

## Local Setup

From the backend folder:

```powershell
cd "D:\Codex Project\backend"
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
copy .env.example .env
```

Update `.env` if your PostgreSQL username, password, host, port, or database name differs.

Default database URL:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/micro_savings
```

## Database Setup

Create the local PostgreSQL database:

```sql
CREATE DATABASE micro_savings;
```

Apply migrations:

```powershell
.venv\Scripts\alembic upgrade head
```

Check current migration:

```powershell
.venv\Scripts\alembic current
```

Expected latest revision after Step 29:

```text
20260508_0003
```

## Run The API

```powershell
.venv\Scripts\python -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
GET http://127.0.0.1:8000/api/v1/health
```

## Test Commands

Run syntax verification:

```powershell
.venv\Scripts\python -m compileall app migrations tests
```

Run tests:

```powershell
.venv\Scripts\python -m pytest
```

Current expected result:

```text
19 passed
```

## Docker Runtime

Build the backend image from the backend folder:

```powershell
docker build -t micro-savings-backend .
```

Run the API container:

```powershell
docker run --rm -p 8000:8000 --env-file .env micro-savings-backend
```

Production container platforms can override:

```text
HOST=0.0.0.0
PORT=8000
WEB_CONCURRENCY=1
UVICORN_LOG_LEVEL=info
```

The backend image starts through:

```text
scripts/start.sh
```

Apply migrations from the image:

```powershell
docker run --rm --env-file .env micro-savings-backend sh scripts/migrate.sh
```

Run a specific Alembic command through the migration script:

```powershell
docker run --rm --env-file .env micro-savings-backend sh scripts/migrate.sh current
```

## Docker Compose

Run PostgreSQL, migrations, and the API together:

```powershell
docker compose up --build
```

Open:

```text
http://127.0.0.1:8000/docs
```

Stop the stack:

```powershell
docker compose down
```

Remove the local PostgreSQL volume:

```powershell
docker compose down -v
```

## Main API Groups

- `/api/v1/auth`
- `/api/v1/expenses`
- `/api/v1/analytics`
- `/api/v1/insights`
- `/api/v1/alerts`
- `/api/v1/goals`
- `/api/v1/simulator`
- `/api/v1/dashboard`
- `/api/v1/ml`

## Quick Auth Flow

Register:

```http
POST /api/v1/auth/register
```

```json
{
  "email": "test@example.com",
  "password": "strongpass123",
  "full_name": "Test User"
}
```

Login:

```http
POST /api/v1/auth/login
```

```json
{
  "email": "test@example.com",
  "password": "strongpass123"
}
```

Use the returned token:

```http
Authorization: Bearer <access_token>
```

## Common Errors

### `No module named pytest`

Use the local virtual environment:

```powershell
.venv\Scripts\python -m pytest
```

### `relation "users" does not exist`

Run migrations:

```powershell
.venv\Scripts\alembic upgrade head
```

### PostgreSQL connection refused

Confirm PostgreSQL is running and `DATABASE_URL` is correct.

### Browser CORS error

Add the frontend origin to:

```env
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

### `JWT_SECRET_KEY` validation error

Use a secret key with at least 32 characters.
