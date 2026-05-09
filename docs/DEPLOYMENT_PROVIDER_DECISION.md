# Deployment Provider Decision

Decision date: 2026-05-09

Selected first deployment provider:

```text
Render
```

## 1. Decision Summary

Use Render for the first MVP production deployment.

Recommended service layout:

| Project Component | Render Service |
| --- | --- |
| PostgreSQL database | Render Postgres |
| FastAPI backend | Render Web Service using `backend/Dockerfile` |
| React frontend | Render Static Site |
| Database migrations | Render one-off job or manual shell command using backend image |

## 2. Why Render Fits This MVP

Render fits the current project because it supports:

- Static frontend hosting.
- Docker-based backend deployment.
- Managed PostgreSQL.
- Environment variables and secrets.
- Managed TLS and custom domains.
- Static site rewrites for React Router.
- Service logs and health checks.
- Rollbacks.

This keeps deployment simple for a solo developer while preserving a clean path
to scale later.

## 3. Backend Mapping

Render service type:

```text
Web Service
```

Backend source:

```text
backend/Dockerfile
```

Start command:

```text
sh scripts/start.sh
```

Health check path:

```text
/api/v1/health
```

Required backend environment:

```env
APP_ENV=production
APP_DEBUG=false
DATABASE_URL=<render-postgres-internal-url>
JWT_SECRET_KEY=<strong-random-secret-at-least-32-characters>
BACKEND_CORS_ORIGINS=["https://<frontend-domain>"]
BACKEND_ALLOWED_HOSTS=["<backend-domain>"]
LOG_FORMAT=json
```

Render provides a `PORT` environment variable for web services. The backend
startup script already supports this.

## 4. Database Mapping

Render service type:

```text
Render Postgres
```

Use the internal database URL for backend-to-database communication when
available.

Before launch:

- Confirm backups are enabled for the selected paid database plan.
- Record the recovery window.
- Confirm the connection string uses the async SQLAlchemy format required by
  the backend:

```text
postgresql+asyncpg://<user>:<password>@<host>:5432/<database>
```

## 5. Migration Mapping

Run migrations before promoting the backend:

```text
sh scripts/migrate.sh
```

Use the same backend image and environment variables as the backend web service.

Do not deploy the frontend until migrations and backend health checks pass.

## 6. Frontend Mapping

Render service type:

```text
Static Site
```

Working directory:

```text
frontend/
```

Build command:

```text
npm ci && npm run build:production
```

Publish directory:

```text
frontend/dist/
```

Required build environment:

```env
VITE_API_BASE_URL=https://<backend-domain>/api/v1
```

React Router rewrite rule:

```text
Source: /*
Destination: /index.html
Action: Rewrite
```

## 7. Launch Order

Use this order:

1. Create Render Postgres.
2. Create backend web service.
3. Configure backend environment variables.
4. Run backend migrations.
5. Start and verify backend health.
6. Create frontend static site.
7. Configure `VITE_API_BASE_URL`.
8. Add React Router rewrite rule.
9. Deploy frontend.
10. Run `docs/SMOKE_TEST_PLAN.md`.
11. Start `docs/POST_LAUNCH_MONITORING.md`.

## 8. Decision Boundaries

This decision does not deploy the application yet.

Before deployment execution, confirm:

- Render account is ready.
- Repository is connected.
- Production domains are chosen.
- Production secrets are generated.
- Database plan includes the backup/recovery needs for the MVP.

Environment setup:

```text
docs/RENDER_ENVIRONMENT_SETUP.md
```

Backend deployment:

```text
docs/RENDER_BACKEND_DEPLOYMENT.md
```

Frontend deployment:

```text
docs/RENDER_FRONTEND_DEPLOYMENT.md
```

## 9. Official References

- Render Web Services: https://render.com/docs/web-services/
- Docker on Render: https://render.com/docs/docker
- Render Static Sites: https://render.com/docs/static-sites/
- Static site rewrites: https://render.com/docs/redirects-rewrites
- Render Postgres: https://render.com/docs/postgresql
- Render Postgres backups: https://render.com/docs/postgresql-backups
