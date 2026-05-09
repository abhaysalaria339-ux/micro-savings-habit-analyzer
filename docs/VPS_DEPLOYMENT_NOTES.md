# VPS Deployment Notes

Use this document only if the MVP will be self-hosted on a VPS.

The recommended first deployment path remains:

```text
docs/MANAGED_PAAS_DEPLOYMENT.md
```

Self-hosting gives more control, but it also makes the solo developer
responsible for server security, backups, TLS, updates, monitoring, and recovery.

## 1. Suitable VPS Layout

Run the application as three services:

| Service | Recommended Runtime |
| --- | --- |
| Frontend | Nginx static site or frontend Docker container |
| Backend | Backend Docker container |
| Database | Managed PostgreSQL preferred, local PostgreSQL only if necessary |

Use managed PostgreSQL with the VPS when possible. Local PostgreSQL on the VPS
adds backup and recovery responsibility.

## 2. Minimum Server Requirements

For an MVP:

- 1-2 vCPU.
- 1-2 GB RAM.
- 20 GB disk.
- Ubuntu LTS or equivalent stable Linux distribution.
- Docker and Docker Compose plugin installed.
- Firewall allowing only SSH, HTTP, and HTTPS.

## 3. Required Production Domains

Use separate hostnames:

```text
Frontend: https://<frontend-domain>
Backend: https://<backend-domain>
```

Backend environment must include:

```env
APP_ENV=production
APP_DEBUG=false
DATABASE_URL=<production-database-url>
JWT_SECRET_KEY=<strong-random-secret-at-least-32-characters>
BACKEND_CORS_ORIGINS=["https://<frontend-domain>"]
BACKEND_ALLOWED_HOSTS=["<backend-domain>"]
LOG_FORMAT=json
```

Frontend build must use:

```env
VITE_API_BASE_URL=https://<backend-domain>/api/v1
```

## 4. Reverse Proxy Requirements

Put a reverse proxy in front of the backend.

Required behavior:

- Terminate HTTPS.
- Redirect HTTP to HTTPS.
- Forward backend traffic to the backend container.
- Preserve `Host` headers so trusted host validation works.
- Keep request body limits aligned with `MAX_REQUEST_BODY_BYTES`.
- Serve frontend static files with fallback to `index.html`.

Do not expose the backend container directly to the public internet without TLS.

## 5. Deployment Order

Use this order:

1. Provision the VPS.
2. Configure firewall rules.
3. Install Docker and Docker Compose.
4. Configure DNS for frontend and backend domains.
5. Configure TLS certificates.
6. Create production `.env` values on the server.
7. Start PostgreSQL or connect to managed PostgreSQL.
8. Build and start the backend container privately.
9. Run `sh scripts/migrate.sh`.
10. Start or reload the reverse proxy.
11. Build and deploy the frontend with the production API URL.
12. Run `docs/SMOKE_TEST_PLAN.md`.

## 6. Backup Requirements

Before launch, define:

- PostgreSQL backup schedule.
- Backup storage location outside the VPS.
- Restore procedure.
- JWT secret rotation procedure.
- Server snapshot schedule if the provider supports it.

Do not consider the VPS deployment production-ready without database backups.

## 7. Maintenance Checklist

Run regularly:

- Apply operating system security updates.
- Renew or verify TLS certificates.
- Review backend error logs.
- Verify database backups.
- Check disk usage.
- Run smoke tests after each deployment.

## 8. When To Avoid VPS

Avoid VPS for the first launch if:

- There is no backup process.
- There is no TLS automation.
- The database would live only on the same disk as the app.
- You cannot monitor failed services.
- You want the fastest low-maintenance MVP deployment.

In those cases, use the managed PaaS path.
