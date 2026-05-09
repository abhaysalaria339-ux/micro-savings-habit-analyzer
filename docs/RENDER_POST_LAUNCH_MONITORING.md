# Render Post-Launch Monitoring

Use this guide after the Render production smoke test passes.

Complete first:

```text
docs/RENDER_SMOKE_TEST.md
docs/MVP_RELEASE_RECORD.md
```

## 1. First Hour Checks

For the first hour after launch, check every 15 minutes:

- Backend health: `GET https://<backend-domain>/api/v1/health`
- Database readiness: `GET https://<backend-domain>/api/v1/health/db`
- Frontend availability: `https://<frontend-domain>`
- Render backend logs.
- Render frontend events.
- New HTTP 500 responses.
- CORS or trusted host errors.
- Login and registration errors.

Expected:

```text
Health checks stay green.
No repeated server errors appear.
Frontend remains available over HTTPS.
```

## 2. First Day Checks

On launch day:

- Review backend logs at least twice.
- Confirm no repeated `request_failed` events.
- Confirm no database connection errors.
- Confirm Render service resource warnings are clear.
- Confirm frontend routes refresh correctly.
- Confirm release record is complete.
- Confirm rollback targets are still available.

## 3. Backup Verification

For Render Postgres, confirm:

- Database plan includes the required backup/recovery capability.
- Recovery window is known.
- Latest backup or recovery capability is visible in Render.
- Restore process is understood before real user growth.

Record in the release notes:

```text
Backup status:
Recovery window:
Restore test scheduled:
```

Do not treat production as stable without a backup and recovery plan.

## 4. Log Review

Review backend logs for:

- Startup errors.
- Migration errors.
- Database errors.
- CORS failures.
- Trusted host rejections.
- HTTP 500 responses.
- Slow request patterns.
- Repeated auth failures.

Expected log fields:

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

- JWTs.
- Passwords.
- Request bodies.
- Sensitive query strings.

## 5. Alert Thresholds

Manually investigate if any of these happen:

- Backend health fails once.
- Database readiness fails once.
- Any repeated HTTP 500 response appears.
- Login or registration fails for a valid test user.
- Frontend loads a blank page.
- Render reports service crashes or restart loops.
- Database backup or recovery status is unclear.

## 6. Incident Response

If an incident occurs:

1. Identify affected service: frontend, backend, or database.
2. Check Render service status and logs.
3. Check the latest deployment event.
4. Roll back frontend if the issue is frontend-only.
5. Roll back backend if the issue is backend-only and not migration-related.
6. Do not roll back the database unless a tested rollback migration exists.
7. Record the incident in the release notes.

Incident record:

```text
Incident time:
Affected service:
User impact:
Root cause:
Fix:
Follow-up:
```

## 7. Daily Operating Routine

For the first week:

- Check frontend availability once daily.
- Check backend health once daily.
- Check database readiness once daily.
- Review backend errors once daily.
- Confirm backup/recovery status once daily.
- Record any user-reported issues.

After the first week, move to the routine in:

```text
docs/POST_LAUNCH_MONITORING.md
```

Collect first-user feedback with:

```text
docs/FIRST_USER_FEEDBACK.md
```

## 8. Completion Criteria

This step is complete when:

- First-hour checks are green.
- Backup/recovery status is confirmed.
- Release record includes monitoring start time.
- No unresolved launch-blocking incidents remain.
- Daily first-week monitoring routine is scheduled.
