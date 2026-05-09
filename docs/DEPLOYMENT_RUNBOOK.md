# Deployment Runbook

Use this runbook for each production release of the Micro-Savings Habit Analyzer.

For managed platform setup details, use:

```text
docs/MANAGED_PAAS_DEPLOYMENT.md
```

For final readiness review before release execution, use:

```text
docs/PRE_DEPLOYMENT_AUDIT.md
```

For the operator checklist during the deployment window, use:

```text
docs/DEPLOYMENT_EXECUTION_CHECKLIST.md
```

For version tags and release records, use:

```text
docs/RELEASE_VERSIONING.md
```

For post-launch operational checks, use:

```text
docs/POST_LAUNCH_MONITORING.md
```

## 1. Pre-Deployment

Confirm the release is ready:

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

Confirm production settings are ready:

- `DATABASE_URL` points to production PostgreSQL.
- `JWT_SECRET_KEY` is strong and private.
- `BACKEND_CORS_ORIGINS` contains the production frontend URL.
- `VITE_API_BASE_URL` points to the production backend URL with `/api/v1`.

## 2. Backend Release

Build and publish the backend image using the deployment platform's image flow.

Backend web command:

```text
sh scripts/start.sh
```

Required backend environment:

```text
APP_ENV=production
APP_DEBUG=false
DATABASE_URL=<production-database-url>
JWT_SECRET_KEY=<strong-production-secret>
BACKEND_CORS_ORIGINS=["https://<frontend-domain>"]
```

## 3. Database Migration

Run migrations before routing traffic to the new backend release:

```text
sh scripts/migrate.sh
```

Expected result:

```text
alembic upgrade head completes without errors
```

## 4. Frontend Release

Build the frontend with the production backend URL:

```powershell
cd frontend
npm run build:production
```

Deploy:

```text
frontend/dist/
```

If using Docker, pass the backend URL at build time:

```text
docker build --build-arg VITE_API_BASE_URL=https://<backend-domain>/api/v1 -t micro-savings-frontend ./frontend
```

## 5. Post-Deployment Verification

Verify backend health:

```text
GET https://<backend-domain>/api/v1/health
GET https://<backend-domain>/api/v1/health/db
```

Verify frontend behavior:

```text
docs/SMOKE_TEST_PLAN.md
```

Then monitor the release:

```text
docs/POST_LAUNCH_MONITORING.md
```

## 6. Rollback

If the release fails:

1. Stop routing traffic to the new backend release.
2. Restore the previous backend image or service revision.
3. Restore the previous frontend deployment.
4. Review backend and migration logs.
5. Do not roll back database migrations unless a tested rollback migration exists.
