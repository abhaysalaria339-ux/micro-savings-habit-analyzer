# Pre-Deployment Audit

Use this audit before the first managed platform deployment.

## 1. Audit Scope

This audit covers the current MVP readiness for:

- Backend API deployment.
- PostgreSQL migration execution.
- Frontend production build.
- Security and runtime configuration.
- Release documentation.
- Smoke test readiness.

It does not certify a live production deployment because no cloud environment has
been provisioned yet.

## 2. Backend Readiness

Status: ready for managed PaaS deployment after production environment variables
are configured.

Verified backend areas:

- FastAPI modular monolith structure is in place.
- PostgreSQL connection and Alembic migrations are configured.
- JWT authentication is implemented.
- Expense, analytics, insights, alerts, goals, simulator, dashboard, and ML
  readiness API surfaces are implemented.
- Health and database readiness endpoints are available.
- Production startup command is available at `backend/scripts/start.sh`.
- Production migration command is available at `backend/scripts/migrate.sh`.
- Unsafe production settings fail startup.
- CORS, trusted hosts, security headers, request ID, structured logging, and
  request body size limits are configured.
- Request logs avoid request bodies, JWTs, passwords, and query strings.

Required before deploy:

- Set `DATABASE_URL` to the managed PostgreSQL connection string.
- Set a strong private `JWT_SECRET_KEY`.
- Set `BACKEND_CORS_ORIGINS` to the deployed frontend origin.
- Set `BACKEND_ALLOWED_HOSTS` to the deployed backend hostname.

## 3. Frontend Readiness

Status: ready for static hosting after `VITE_API_BASE_URL` is configured.

Verified frontend areas:

- React + TypeScript + Vite application is implemented.
- Authentication, dashboard, expenses, goals, insights, alerts, and simulator
  screens are connected to the backend API client.
- Protected routes and token persistence are implemented.
- Shared loading, empty, and error states are implemented.
- Responsive layout polish has been applied.
- Production build command is available as `npm run build:production`.

Required before deploy:

- Build with `VITE_API_BASE_URL=https://<backend-domain>/api/v1`.
- Configure the static host to route unknown frontend paths to `index.html`.

## 4. Deployment Readiness

Status: deployment-ready documentation exists; real deployment is still pending.

Available deployment assets:

- `backend/Dockerfile`
- `backend/scripts/start.sh`
- `backend/scripts/migrate.sh`
- `frontend/Dockerfile`
- `frontend/nginx.conf`
- `docker-compose.yml`
- `.github/workflows/ci.yml`
- `docs/PRODUCTION_CHECKLIST.md`
- `docs/MANAGED_PAAS_DEPLOYMENT.md`
- `docs/DEPLOYMENT_RUNBOOK.md`
- `docs/SMOKE_TEST_PLAN.md`

Recommended first deployment path:

1. Managed PostgreSQL.
2. Docker backend web service.
3. One-off backend migration job.
4. Static frontend hosting.
5. Manual smoke test using `docs/SMOKE_TEST_PLAN.md`.

## 5. Verification Status

Run before each release:

```powershell
cd backend
.venv\Scripts\python -m ruff check app tests
.venv\Scripts\python -m pytest
```

```powershell
cd frontend
npm run lint
npm run test
npm run build:production
```

Known local limitation:

- Docker Compose verification cannot run in the current workstation environment
  until Docker Desktop or another Docker-compatible CLI is installed.

## 6. Known Blockers

These must be resolved before a real production launch:

- Choose the managed deployment provider.
- Provision managed PostgreSQL.
- Configure production secrets in the provider dashboard.
- Run the production migration job.
- Deploy backend and frontend services.
- Run the smoke test against the deployed URLs.

## 7. Intentional Deferrals

These are intentionally deferred and should not block the MVP deployment:

- Machine learning model implementation.
- Pandas-based data processing.
- Redis caching or background jobs.
- Banking, UPI, email, and SMS provider integrations.
- Automated browser end-to-end test suite.

## 8. Audit Result

The project is ready to move from local production preparation into deployment
execution.

The deployment execution checklist defines release order, migration command,
environment variable confirmation, smoke test order, and rollback checkpoints.

Deployment execution checklist:

```text
docs/DEPLOYMENT_EXECUTION_CHECKLIST.md
```

MVP handoff summary:

```text
docs/MVP_HANDOFF_REPORT.md
```

Final readiness confirmation:

```text
docs/FINAL_READINESS_CONFIRMATION.md
```
