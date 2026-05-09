# Render Environment Setup

Use this guide to configure production environment variables in Render.

Do not commit real production secrets to the repository.

## 1. Required Render Services

Configure environment variables for:

| Render Service | Purpose |
| --- | --- |
| `micro-savings-backend` | FastAPI web service |
| `micro-savings-migrate` | One-off migration command or job |
| `micro-savings-frontend` | React static site |
| `micro-savings-db` | Render Postgres |

Use the same backend environment values for the backend web service and the
migration job.

## 2. Backend Web Service Environment

Set these variables on the Render backend web service:

```env
APP_NAME=Micro-Savings Habit Analyzer API
APP_ENV=production
APP_DEBUG=false
API_V1_PREFIX=/api/v1
MAX_REQUEST_BODY_BYTES=1048576
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<render-postgres-host>:5432/<database>
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

Notes:

- Replace Render's default `postgres://` URL scheme with `postgresql+asyncpg://`.
- Use the internal Render Postgres host when available.
- Do not use wildcard CORS origins.
- Do not use example JWT secrets.
- Render provides `PORT`; do not set it manually unless needed.

## 3. Migration Job Environment

Use the same values as the backend web service.

Migration command:

```text
sh scripts/migrate.sh
```

Required:

- `DATABASE_URL` must point to the production Render Postgres database.
- `APP_ENV` must be `production`.
- `JWT_SECRET_KEY` must be set even though migrations do not use auth directly,
  because the app settings load it.

## 4. Frontend Static Site Environment

Set this variable on the Render static site:

```env
VITE_API_BASE_URL=https://<backend-domain>/api/v1
```

Build command:

```text
npm ci && npm run build:production
```

Publish directory:

```text
frontend/dist/
```

React Router rewrite:

```text
Source: /*
Destination: /index.html
Action: Rewrite
```

## 5. Domain Placeholders

Replace placeholders with real Render or custom domains:

```text
<frontend-domain> = frontend Render static site URL or custom frontend domain
<backend-domain> = backend Render web service URL or custom backend domain
```

Examples:

```text
BACKEND_CORS_ORIGINS=["https://micro-savings.onrender.com"]
BACKEND_ALLOWED_HOSTS=["micro-savings-api.onrender.com"]
VITE_API_BASE_URL=https://micro-savings-api.onrender.com/api/v1
```

## 6. Secret Handling

Treat these as secrets:

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- PostgreSQL password

Generate `JWT_SECRET_KEY` with at least 32 random characters.

Do not place production secrets in:

- `.env`
- `.env.production.example`
- Git commits.
- Screenshots.
- Issue comments.

## 7. Pre-Deploy Validation

Before deploying, confirm:

- No value contains `<placeholder>` text.
- `APP_DEBUG=false`.
- `APP_ENV=production`.
- `DATABASE_URL` uses `postgresql+asyncpg://`.
- `BACKEND_CORS_ORIGINS` contains the frontend origin.
- `BACKEND_ALLOWED_HOSTS` contains only the backend hostname.
- `VITE_API_BASE_URL` ends with `/api/v1`.
- Frontend rewrite rule exists.
- Render Postgres backup/recovery plan is acceptable.

## 8. Common Render Environment Errors

Backend startup fails:

- Check for missing `JWT_SECRET_KEY`.
- Check unsafe production values rejected by startup validation.
- Check invalid JSON list syntax in `BACKEND_CORS_ORIGINS`.

Database readiness fails:

- Check `DATABASE_URL`.
- Confirm Render Postgres is available.
- Confirm the URL uses `postgresql+asyncpg://`.

Frontend API calls fail:

- Check `VITE_API_BASE_URL`.
- Check CORS origin exactly matches the frontend URL.
- Check backend health endpoints first.

Refresh on frontend route returns 404:

- Add the Render static site rewrite rule from `/*` to `/index.html`.
