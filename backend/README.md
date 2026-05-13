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

## Seed Synthetic Demo Data

Use this when you need realistic expense history for UI demos, analytics testing,
or future ML feature engineering without waiting for real users.

From the backend folder:

```powershell
.venv\Scripts\python scripts\seed_demo_data.py --users 10 --days 90
```

The script creates demo users with varied behavior profiles:

- Saver
- Neutral
- Spender
- Weekend spender
- Micro-spender

Demo login pattern:

```text
Email: demo.<profile>.<number>@example.local
Password: DemoPass123!
```

Example:

```text
demo.saver.01@example.local
demo.micro.05@example.local
```

If demo users already exist, replace them safely with:

```powershell
.venv\Scripts\python scripts\seed_demo_data.py --users 10 --days 90 --reset-demo-data
```

Safety notes:

- The script only targets `demo.*@example.local` users.
- It refuses to run in `APP_ENV=production` unless `--allow-production` is passed.
- Run Alembic migrations before seeding.

## ML Feature Engineering

The project is ML-ready but does not train models yet. The first ML preparation
module is:

```text
app/ml/features.py
```

It converts a user's expense history into a deterministic feature vector for
future clustering, classification, and forecasting work. Example features include:

- total spend
- average transaction amount
- active spending days
- micro-expense ratio
- repeated pattern count
- category concentration
- weekend spend ratio
- food/snack spend ratio
- subscription spend ratio
- spending frequency
- first-half vs second-half trend ratio

This keeps ML work separate from API behavior until a model is intentionally added.

## ML Spending Profile Prototype

The first model-style capability is an explainable spending profile clustering
prototype:

```text
GET /api/v1/ml/spending-profile?analysis_days=90
```

It uses the ML feature vector to assign one profile:

- Saver
- Neutral
- Spender
- Weekend Spender
- Micro-Spender
- Insufficient data

This prototype is dependency-free and does not train on request. It compares the
user's feature vector against stable profile centroids, then returns:

- profile id
- profile label
- confidence
- summary
- reasons
- recommendations
- feature snapshot

This is enough to validate the ML pipeline and demo behavior before adding
heavier libraries or trained models.

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
