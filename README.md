# Micro-Savings Habit Analyzer

Full-stack workspace for the Micro-Savings Habit Analyzer.

## Services

- `backend`: FastAPI API
- `frontend`: React frontend served by Nginx
- `db`: PostgreSQL
- `backend-migrate`: one-shot Alembic migration runner

## Full-Stack Docker Compose

From the project root:

```powershell
cd "D:\Codex Project"
copy .env.example .env
docker compose up --build
```

Open:

```text
Frontend: http://127.0.0.1:5173
Backend docs: http://127.0.0.1:8000/docs
```

Stop the stack:

```powershell
docker compose down
```

Remove the local PostgreSQL volume:

```powershell
docker compose down -v
```

Run the automated full-stack verification script:

```powershell
.\scripts\verify-docker-compose.ps1
```

Run verification and stop containers afterward:

```powershell
.\scripts\verify-docker-compose.ps1 -TearDown
```

## Environment Safety

Commit only example environment files:

```text
.env.example
.env.production.example
backend/.env.example
backend/.env.production.example
frontend/.env.example
frontend/.env.production.example
```

Do not commit real `.env` files. They may contain database passwords, JWT secrets,
or deployed API URLs.

## Continuous Integration

GitHub Actions workflow:

```text
.github/workflows/ci.yml
```

The CI pipeline runs:

```text
Backend: Ruff, compileall, pytest
Frontend: ESLint, Vitest, production build
```

## Production Checklist

Before deploying, review:

```text
docs/PRODUCTION_CHECKLIST.md
docs/DEPLOYMENT_TARGETS.md
docs/DEPLOYMENT_PROVIDER_DECISION.md
docs/RENDER_ENVIRONMENT_SETUP.md
docs/RENDER_BACKEND_DEPLOYMENT.md
docs/RENDER_FRONTEND_DEPLOYMENT.md
docs/RENDER_SMOKE_TEST.md
docs/MANAGED_PAAS_DEPLOYMENT.md
docs/DEPLOYMENT_RUNBOOK.md
docs/SMOKE_TEST_PLAN.md
docs/PRE_DEPLOYMENT_AUDIT.md
docs/DEPLOYMENT_EXECUTION_CHECKLIST.md
docs/VPS_DEPLOYMENT_NOTES.md
docs/RELEASE_VERSIONING.md
docs/MVP_RELEASE_RECORD.md
docs/POST_LAUNCH_MONITORING.md
docs/RENDER_POST_LAUNCH_MONITORING.md
docs/FIRST_USER_FEEDBACK.md
docs/POST_MVP_IMPROVEMENT_CYCLE.md
docs/POST_MVP_ROADMAP.md
docs/FIRST_POST_MVP_CYCLE_SELECTION.md
docs/POST_MVP_RELEASE_PLAN.md
docs/POST_MVP_IMPLEMENTATION_READINESS.md
docs/MVP_HANDOFF_REPORT.md
docs/FINAL_READINESS_CONFIRMATION.md
```

Production environment templates:

```text
.env.production.example
backend/.env.production.example
frontend/.env.production.example
```

## Local Development

Backend-only instructions are in:

```text
backend/README.md
```

Frontend-only instructions are in:

```text
frontend/README.md
```
