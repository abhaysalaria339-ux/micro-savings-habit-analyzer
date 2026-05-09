# Production Deployment Checklist

Use this checklist before deploying the Micro-Savings Habit Analyzer.

For release order and rollback steps, use:

```text
docs/DEPLOYMENT_RUNBOOK.md
```

For managed platform setup details, use:

```text
docs/MANAGED_PAAS_DEPLOYMENT.md
```

For post-deployment smoke testing, use:

```text
docs/SMOKE_TEST_PLAN.md
```

For final readiness review before deployment execution, use:

```text
docs/PRE_DEPLOYMENT_AUDIT.md
```

For the deployment window checklist, use:

```text
docs/DEPLOYMENT_EXECUTION_CHECKLIST.md
```

For optional self-hosted deployment notes, use:

```text
docs/VPS_DEPLOYMENT_NOTES.md
```

For post-launch monitoring, use:

```text
docs/POST_LAUNCH_MONITORING.md
```

## 1. Backend Environment

Set these backend variables in the deployment environment:

```env
APP_NAME="Micro-Savings Habit Analyzer API"
APP_ENV=production
APP_DEBUG=false
API_V1_PREFIX=/api/v1
MAX_REQUEST_BODY_BYTES=1048576
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:5432/<database>
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

Template file:

```text
backend/.env.production.example
```

Required production rules:

- `APP_DEBUG` must be `false`.
- `APP_ENV` must be `production`.
- `JWT_SECRET_KEY` must not use any example value.
- `DATABASE_URL` must point to the production PostgreSQL database.
- `BACKEND_CORS_ORIGINS` must contain only trusted frontend origins.
- `BACKEND_CORS_ALLOW_METHODS` and `BACKEND_CORS_ALLOW_HEADERS` must avoid wildcards.
- `BACKEND_ALLOWED_HOSTS` must contain only production backend hostnames.
- `MAX_REQUEST_BODY_BYTES` should stay small for the current JSON-only API.
- The backend fails startup if unsafe production settings are detected.

## 2. Frontend Environment

Build the frontend with the deployed backend API URL:

```env
VITE_API_BASE_URL=https://<backend-domain>/api/v1
```

Template file:

```text
frontend/.env.production.example
```

For Docker builds:

```powershell
docker build --build-arg VITE_API_BASE_URL=https://<backend-domain>/api/v1 -t micro-savings-frontend ./frontend
```

For static hosting builds:

```powershell
cd frontend
npm run build:production
```

Deploy:

```text
frontend/dist/
```

## 3. Database And Migrations

Before starting the backend service:

1. Confirm the production PostgreSQL database exists.
2. Confirm the backend can connect using `DATABASE_URL`.
3. Run Alembic migrations:

```powershell
alembic upgrade head
```

For Docker:

```powershell
docker run --rm --env-file .env micro-savings-backend sh scripts/migrate.sh
```

## 4. Release Verification

After deployment, verify:

```text
GET https://<backend-domain>/api/v1/health
GET https://<backend-domain>/api/v1/health/db
```

Expected:

```json
{"status":"ok"}
```

and:

```json
{"status":"ok","database":"reachable"}
```

Then verify in the frontend:

- Register a test user.
- Log in.
- Add an expense.
- Confirm the expense appears in the list.
- Create a goal.
- Open dashboard, insights, and simulator pages.

## 5. Security Checks

- Do not commit real `.env` files.
- Rotate `JWT_SECRET_KEY` if it was exposed.
- Use HTTPS for frontend and backend.
- Confirm backend responses include security headers.
- Confirm backend logs include request ID, path, route, status code, and duration.
- Confirm backend logs do not include request bodies, JWTs, passwords, or query strings.
- Restrict CORS to production frontend domains.
- Use managed PostgreSQL backups.
- Do not expose PostgreSQL directly to the public internet.

## 6. Rollback Notes

If deployment fails:

1. Stop the new frontend/backend release.
2. Restore the previous container/image version.
3. Check backend logs for startup, migration, or configuration errors.
4. Do not downgrade database migrations unless a tested rollback migration exists.
