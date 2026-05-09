# Deployment Targets

Use this document to choose the first production hosting path for the Micro-Savings
Habit Analyzer.

Operational release steps are documented in:

```text
docs/DEPLOYMENT_RUNBOOK.md
```

Managed PaaS deployment notes are documented in:

```text
docs/MANAGED_PAAS_DEPLOYMENT.md
```

The selected first deployment provider is documented in:

```text
docs/DEPLOYMENT_PROVIDER_DECISION.md
```

Optional VPS deployment notes are documented in:

```text
docs/VPS_DEPLOYMENT_NOTES.md
```

## Recommended MVP Path

For a solo-developer MVP, use a managed platform with separate services:

```text
Frontend: static React site
Backend: Dockerized FastAPI service
Database: managed PostgreSQL
```

This keeps operations simple while preserving the current clean backend architecture.

## Required Platform Capabilities

The deployment target must support:

- HTTPS for frontend and backend.
- Environment variables for backend and frontend builds.
- A managed PostgreSQL database or private PostgreSQL connection.
- Running Alembic migrations before backend startup or release.
- Docker image deployment for the backend.
- Health checks against `/api/v1/health`.
- Logs for backend startup, request failures, and migration failures.

## Service Mapping

| Project Component | Production Service Type | Required Config |
| --- | --- | --- |
| `frontend` | Static site or Nginx container | `VITE_API_BASE_URL` |
| `backend` | Docker web service | `DATABASE_URL`, `JWT_SECRET_KEY`, `BACKEND_CORS_ORIGINS` |
| `backend-migrate` | Release command or one-off job | `sh scripts/migrate.sh` |
| `db` | Managed PostgreSQL | Database name, user, password, host |

## First Deployment Options

| Option | Best For | Tradeoff |
| --- | --- | --- |
| Render/Railway/Fly-style PaaS | Fast MVP deployment | Less infrastructure control |
| VPS with Docker Compose | Full control and low cost | More manual operations |
| Cloud container services | Later scaling | More setup complexity |

## Decision For This Project

Start with the managed PaaS path unless there is a strong reason to self-host.

The selected first provider is Render.

Use `docs/MANAGED_PAAS_DEPLOYMENT.md` for the first deployment implementation.
Use `docs/DEPLOYMENT_PROVIDER_DECISION.md` for the Render-specific mapping.

Use `docs/VPS_DEPLOYMENT_NOTES.md` only when choosing the VPS option.

The next implementation steps should prepare:

1. Backend production start command.
2. Migration release command.
3. Frontend production build command.
4. Platform-specific deployment notes once a target is chosen.

## Backend Runtime Contract

The backend container starts through:

```text
backend/scripts/start.sh
```

Supported runtime variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `HOST` | `0.0.0.0` | Bind address inside the container |
| `PORT` | `8000` | Web port, usually provided by the platform |
| `WEB_CONCURRENCY` | `1` | Uvicorn worker count |
| `UVICORN_LOG_LEVEL` | `info` | Uvicorn runtime log level |

## Migration Runtime Contract

Run database migrations as a release command or one-off job before starting the
backend web service:

```text
sh scripts/migrate.sh
```

By default, this executes:

```text
alembic upgrade head
```

For maintenance checks, pass Alembic arguments:

```text
sh scripts/migrate.sh current
```

## Frontend Build Contract

The frontend production build command is:

```text
npm run build:production
```

Required build variable:

```text
VITE_API_BASE_URL=https://<backend-domain>/api/v1
```

The build output is:

```text
frontend/dist/
```

Deploy `frontend/dist/` to a static hosting service, or build the frontend Docker
image with:

```text
docker build --build-arg VITE_API_BASE_URL=https://<backend-domain>/api/v1 -t micro-savings-frontend ./frontend
```

## Non-Goals For MVP Deployment

- Kubernetes.
- Microservices.
- Redis.
- Machine learning workers.
- Banking, UPI, email, or SMS integrations.
