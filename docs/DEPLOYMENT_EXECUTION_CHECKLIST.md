# Deployment Execution Checklist

Use this checklist during the actual production deployment window.

Before starting, complete:

```text
docs/PRE_DEPLOYMENT_AUDIT.md
docs/PRODUCTION_CHECKLIST.md
docs/RELEASE_VERSIONING.md
docs/DEPLOYMENT_PROVIDER_DECISION.md
docs/RENDER_ENVIRONMENT_SETUP.md
docs/RENDER_BACKEND_DEPLOYMENT.md
docs/RENDER_FRONTEND_DEPLOYMENT.md
docs/RENDER_SMOKE_TEST.md
docs/MVP_RELEASE_RECORD.md
```

## 1. Release Inputs

Confirm these values are known before deploying:

| Input | Required Value |
| --- | --- |
| Frontend domain | `https://<frontend-domain>` |
| Backend domain | `https://<backend-domain>` |
| Backend API base URL | `https://<backend-domain>/api/v1` |
| PostgreSQL URL | Managed PostgreSQL connection string |
| Deployment provider | Render |
| Migration command | `sh scripts/migrate.sh` |
| Backend start command | `sh scripts/start.sh` |
| Frontend build command | `npm run build:production` |

Do not continue until all release inputs are confirmed.

## 2. Pre-Release Verification

Run locally or in CI:

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

Expected:

```text
All checks pass.
```

## 3. Production Environment Confirmation

Backend environment:

```env
APP_ENV=production
APP_DEBUG=false
DATABASE_URL=<production-database-url>
JWT_SECRET_KEY=<strong-production-secret>
BACKEND_CORS_ORIGINS=["https://<frontend-domain>"]
BACKEND_CORS_ALLOW_METHODS=["GET","POST","PATCH","DELETE","OPTIONS"]
BACKEND_CORS_ALLOW_HEADERS=["Accept","Authorization","Content-Type"]
BACKEND_ALLOWED_HOSTS=["<backend-domain>"]
LOG_FORMAT=json
```

Frontend environment:

```env
VITE_API_BASE_URL=https://<backend-domain>/api/v1
```

Do not continue if any value still contains an example placeholder.

## 4. Database Provisioning

Confirm:

- Managed PostgreSQL database exists.
- Backups are enabled.
- `DATABASE_URL` uses the production database.
- The backend service can reach the database host.
- PostgreSQL is not publicly exposed unless the provider requires it with
  restricted access controls.

## 5. Backend Image Release

Build and publish the backend using:

```text
backend/Dockerfile
```

Backend runtime command:

```text
sh scripts/start.sh
```

Do not route production traffic yet.

Render-specific backend deployment details:

```text
docs/RENDER_BACKEND_DEPLOYMENT.md
```

## 6. Migration Execution

Run the migration job before enabling the backend service:

```text
sh scripts/migrate.sh
```

Expected:

```text
Alembic upgrades to head without errors.
```

If migration fails:

1. Keep the new backend release offline.
2. Review migration logs.
3. Fix configuration or migration issues.
4. Do not deploy the frontend.

## 7. Backend Activation

Start or promote the backend service.

Verify:

```text
GET https://<backend-domain>/api/v1/health
GET https://<backend-domain>/api/v1/health/db
```

Expected:

```text
Both endpoints return HTTP 200.
Database readiness returns database=reachable.
```

Do not deploy the frontend until backend health is green.

## 8. Frontend Release

Build the frontend with:

```text
VITE_API_BASE_URL=https://<backend-domain>/api/v1
```

Deploy:

```text
frontend/dist/
```

Confirm the static host routes unknown paths to:

```text
index.html
```

Render-specific frontend deployment details:

```text
docs/RENDER_FRONTEND_DEPLOYMENT.md
```

## 9. Smoke Test

Run:

```text
docs/SMOKE_TEST_PLAN.md
docs/RENDER_SMOKE_TEST.md
```

Required pass criteria:

- Register a smoke test user.
- Log in.
- Add expenses.
- View dashboard.
- Create and update a goal.
- View insights and alerts.
- Run the savings simulator.
- Confirm no blank pages or API errors.

## 10. Rollback Checkpoints

Rollback before migration:

- Restore previous backend image or service revision.
- Restore previous frontend deployment if already changed.

Rollback after migration:

- Restore previous backend image or service revision.
- Restore previous frontend deployment.
- Keep the migrated database unless a tested rollback migration exists.
- Review logs before any manual database action.

Rollback after frontend deploy:

- Restore previous static frontend deployment.
- Keep backend active if health checks and API smoke tests are passing.

## 11. Release Completion

The deployment is complete when:

- Backend health checks are green.
- Database readiness is green.
- Frontend loads over HTTPS.
- Smoke test passes.
- Logs show no startup, migration, CORS, auth, or database errors.
- The deployed backend and frontend URLs are recorded in the project handoff notes.
- The release version, tag, migration revision, and rollback target are recorded.
- `docs/MVP_RELEASE_RECORD.md` is completed.
- Post-launch monitoring has started using `docs/POST_LAUNCH_MONITORING.md`.
- Render-specific monitoring has started using `docs/RENDER_POST_LAUNCH_MONITORING.md`.
