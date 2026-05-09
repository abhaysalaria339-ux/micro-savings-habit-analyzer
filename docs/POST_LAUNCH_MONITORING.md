# Post-Launch Monitoring Checklist

Use this checklist after the first production deployment.

For Render-specific launch monitoring, use:

```text
docs/RENDER_POST_LAUNCH_MONITORING.md
```

The MVP does not require a complex observability stack yet. Start with platform
health checks, structured backend logs, database backups, and a simple incident
response routine.

## 1. Critical Signals

Monitor these first:

| Signal | Healthy State |
| --- | --- |
| Backend health | `/api/v1/health` returns HTTP 200 |
| Database readiness | `/api/v1/health/db` returns HTTP 200 |
| Frontend availability | Frontend loads over HTTPS |
| Error rate | No repeated HTTP 500 responses |
| Authentication | Register, login, and `/auth/me` work |
| Database backups | Latest backup completed successfully |
| Disk usage | Below provider warning threshold |

## 2. Backend Logs

Review backend logs for:

- `request_failed` events.
- Repeated HTTP 500 responses.
- Database connection errors.
- Migration errors.
- CORS rejections.
- Trusted host rejections.
- Authentication spikes or repeated invalid login attempts.

Expected production log metadata:

```text
request_id
method
path
route
status_code
duration_ms
client_host
```

Logs must not contain:

- Request bodies.
- JWT values.
- Passwords.
- Query strings with sensitive data.

## 3. Daily Checks

Run once per day after launch:

- Open the frontend.
- Check backend health.
- Check database readiness.
- Review backend error logs.
- Confirm the latest database backup completed.
- Check provider resource warnings.

## 4. Weekly Checks

Run once per week:

- Run the smoke test in `docs/SMOKE_TEST_PLAN.md`.
- Review slow or repeated API errors.
- Confirm TLS certificates are valid.
- Confirm database backups are restorable according to provider tooling.
- Review dependency update notices.
- Confirm no real `.env` files were committed.

## 5. After Each Release

After every deployment:

1. Confirm backend health.
2. Confirm database readiness.
3. Run the smoke test.
4. Review logs for 15-30 minutes.
5. Confirm the release record is complete.
6. Confirm rollback target is still available.

Use:

```text
docs/DEPLOYMENT_EXECUTION_CHECKLIST.md
docs/RELEASE_VERSIONING.md
```

## 6. Incident Response

For production incidents, use this order:

1. Identify whether frontend, backend, or database is failing.
2. Check backend health endpoints.
3. Check recent deployment history.
4. Review backend logs using `request_id` where available.
5. Check database connectivity and provider status.
6. Roll back frontend or backend if the issue started after deployment.
7. Avoid manual database changes unless the failure is understood.

Record:

- Incident time.
- Affected service.
- User-visible impact.
- Root cause.
- Fix applied.
- Follow-up prevention task.

## 7. Backup And Recovery

Minimum production expectations:

- Managed PostgreSQL backups are enabled.
- Backup frequency is known.
- Retention period is known.
- Restore process is documented.
- A restore test is scheduled before real user growth.

Do not treat a deployment as production-stable without a working backup plan.

## 8. Security Watchlist

Watch for:

- Unexpected CORS origins.
- Repeated unauthorized requests.
- Spikes in failed login attempts.
- Large request payload rejections.
- Host header rejection spikes.
- Any leaked secrets in logs or issue reports.

If a secret is exposed:

1. Rotate the secret immediately.
2. Redeploy affected services.
3. Invalidate old sessions if JWT exposure is suspected.
4. Review logs for suspicious activity.

## 9. When To Add More Tooling

Add dedicated monitoring tools when:

- Real users depend on the application daily.
- Manual log review becomes too slow.
- You need uptime alerts.
- You need error grouping.
- You need performance traces.
- You need user-facing incident communication.

Until then, platform health checks, structured logs, backups, and smoke tests are
enough for the MVP.
