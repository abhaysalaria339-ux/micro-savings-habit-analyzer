# Managed PaaS Deployment Notes

Use this guide when deploying the MVP to a managed platform that supports:

- Static frontend hosting.
- Dockerized backend web services.
- Managed PostgreSQL.
- Release commands or one-off jobs.

This guide is platform-neutral. Map each section to the matching service type in
your chosen provider.

## 1. Target Service Layout

Create four production resources:

| Resource | Service Type | Source |
| --- | --- | --- |
| `micro-savings-db` | Managed PostgreSQL | Provider database |
| `micro-savings-backend` | Docker web service | `backend/Dockerfile` |
| `micro-savings-migrate` | Release command or one-off job | Backend image |
| `micro-savings-frontend` | Static site | `frontend/dist/` |

## 2. Database

Create a managed PostgreSQL database.

Required output:

```text
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:5432/<database>
```

Use the provider's private database hostname when available.

## 3. Backend Web Service

Build from:

```text
backend/Dockerfile
```

Working directory or Docker context:

```text
backend/
```

Start command:

```text
sh scripts/start.sh
```

Health check path:

```text
/api/v1/health
```

Required environment variables:

```env
APP_NAME="Micro-Savings Habit Analyzer API"
APP_ENV=production
APP_DEBUG=false
API_V1_PREFIX=/api/v1
MAX_REQUEST_BODY_BYTES=1048576
DATABASE_URL=<production-database-url>
JWT_SECRET_KEY=<strong-random-secret-at-least-32-characters>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["https://<frontend-domain>"]
BACKEND_CORS_ALLOW_METHODS=["GET","POST","PATCH","DELETE","OPTIONS"]
BACKEND_CORS_ALLOW_HEADERS=["Accept","Authorization","Content-Type"]
BACKEND_ALLOWED_HOSTS=["<backend-domain>"]
LOG_LEVEL=INFO
LOG_FORMAT=json
```

Optional runtime variables:

```env
HOST=0.0.0.0
PORT=<provider-port>
WEB_CONCURRENCY=1
UVICORN_LOG_LEVEL=info
```

## 4. Migration Job

Run before the backend receives production traffic:

```text
sh scripts/migrate.sh
```

Use the same backend image and environment variables as the backend web service.

The migration job must complete successfully before the release is considered
healthy.

## 5. Frontend Static Site

Build command:

```text
npm ci
npm run build:production
```

Working directory:

```text
frontend/
```

Publish directory:

```text
frontend/dist/
```

Required build environment variable:

```env
VITE_API_BASE_URL=https://<backend-domain>/api/v1
```

The static host must route unknown paths to:

```text
index.html
```

## 6. Release Order

Use this order:

1. Create managed PostgreSQL.
2. Configure backend environment variables.
3. Build backend service.
4. Run migration job.
5. Start backend service.
6. Verify backend health endpoints.
7. Build frontend with production API URL.
8. Deploy frontend.
9. Run `docs/SMOKE_TEST_PLAN.md`.

## 7. Required Post-Deploy Checks

Verify:

```text
https://<backend-domain>/api/v1/health
https://<backend-domain>/api/v1/health/db
https://<frontend-domain>
```

Then run:

```text
docs/SMOKE_TEST_PLAN.md
```

## 8. Provider Mapping Notes

When configuring a specific provider:

- Use a Docker web service for the backend.
- Use a static site service for the frontend.
- Use a release command or one-off job for migrations.
- Use managed secrets/environment variables, not committed `.env` files.
- Prefer private networking between backend and PostgreSQL when available.
