# Render Backend Deployment

Use this guide to deploy the FastAPI backend on Render and run production
database migrations.

Complete first:

```text
docs/DEPLOYMENT_PROVIDER_DECISION.md
docs/RENDER_ENVIRONMENT_SETUP.md
```

## 1. Backend Service Settings

Create a Render Web Service for the backend.

Recommended settings:

| Setting | Value |
| --- | --- |
| Service name | `micro-savings-backend` |
| Runtime | Docker |
| Dockerfile path | `backend/Dockerfile` |
| Root directory | Repository root or `backend/`, depending on Render setup |
| Start command | `sh scripts/start.sh` |
| Health check path | `/api/v1/health` |

If Render uses the repository root as the Docker build context, confirm the
Dockerfile path points to:

```text
backend/Dockerfile
```

If Render uses `backend/` as the service root, confirm the Dockerfile path is:

```text
Dockerfile
```

## 2. Backend Environment

Configure the backend environment using:

```text
docs/RENDER_ENVIRONMENT_SETUP.md
```

Minimum required values:

```env
APP_ENV=production
APP_DEBUG=false
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<render-postgres-host>:5432/<database>
JWT_SECRET_KEY=<strong-random-secret-at-least-32-characters>
BACKEND_CORS_ORIGINS=["https://<frontend-domain>"]
BACKEND_ALLOWED_HOSTS=["<backend-domain>"]
LOG_FORMAT=json
```

Do not continue if any value still contains placeholder text.

## 3. Backend First Deploy

Deploy the backend service after environment variables are configured.

Expected startup behavior:

- Container builds successfully.
- `sh scripts/start.sh` starts Uvicorn.
- Backend binds to Render's `PORT`.
- Startup validation accepts production settings.

The database readiness endpoint may fail before migrations run. This is expected
only until the migration command completes successfully.

## 4. Migration Execution

Run migrations before using the backend for real traffic:

```text
sh scripts/migrate.sh
```

Use the same environment variables as the backend web service.

Expected result:

```text
Alembic upgrade head completes without errors.
```

If Render provides a one-off shell for the backend service, run the command
there. If using a separate migration job, reuse the backend image and the same
environment values.

## 5. Backend Health Verification

After migrations complete, verify:

```text
GET https://<backend-domain>/api/v1/health
GET https://<backend-domain>/api/v1/health/db
```

Expected:

```text
Both return HTTP 200.
Database readiness returns database=reachable.
```

Do not deploy the frontend until both backend health checks pass.

## 6. Backend Log Checks

Review Render backend logs for:

- Startup validation errors.
- Missing environment variables.
- Database connection errors.
- Migration errors.
- Trusted host rejections.
- CORS errors.
- Repeated HTTP 500 responses.

Expected request log fields:

```text
request_id
method
path
route
status_code
duration_ms
client_host
```

## 7. Rollback Guidance

If backend deploy fails before migration:

1. Fix environment or build settings.
2. Redeploy backend.
3. Do not deploy frontend.

If migration fails:

1. Keep backend unavailable for production use.
2. Review migration logs.
3. Fix `DATABASE_URL` or migration issue.
4. Re-run `sh scripts/migrate.sh`.
5. Do not manually change production data unless the failure is understood.

If backend fails after migration:

1. Roll back to the previous backend service revision if one exists.
2. Keep the migrated database.
3. Do not downgrade schema unless a tested rollback migration exists.

## 8. Completion Criteria

This step is complete when:

- Render backend web service is created.
- Backend environment variables are configured.
- Backend image deploys successfully.
- `sh scripts/migrate.sh` completes successfully.
- `/api/v1/health` returns HTTP 200.
- `/api/v1/health/db` returns HTTP 200.
- Backend logs show no startup, migration, or database errors.
