# MVP Release Record

Use this document to record the first production release after the Render smoke
test passes.

Do not mark the release complete until every required field is filled.

## 1. Release Identity

```text
Version: 0.1.0
Tag: v0.1.0
Name: MVP Release
Date:
Released by:
```

## 2. Deployment Provider

```text
Provider: Render
Database service:
Backend service:
Frontend service:
```

## 3. Deployment URLs

```text
Frontend URL:
Backend URL:
Backend API URL:
Backend docs URL:
```

Expected formats:

```text
Frontend URL: https://<frontend-domain>
Backend URL: https://<backend-domain>
Backend API URL: https://<backend-domain>/api/v1
Backend docs URL: https://<backend-domain>/docs
```

## 4. Artifacts

Record the exact deployed artifacts:

```text
Git commit:
Git tag:
Backend Render deploy ID:
Frontend Render deploy ID:
Database migration revision:
Rollback backend target:
Rollback frontend target:
```

For migration revision, run after migration:

```text
alembic current
```

## 5. Verification Results

Pre-deployment verification:

```text
Backend Ruff:
Backend tests:
Frontend ESLint:
Frontend tests:
Frontend production build:
```

Expected local baseline:

```text
Backend Ruff: passed
Backend tests: 40 passed
Frontend ESLint: passed
Frontend tests: 3 passed
Frontend production build: passed
```

Deployment verification:

```text
Backend health:
Database readiness:
Frontend availability:
Render smoke test:
Backend log review:
```

## 6. Smoke Test Result

Use:

```text
docs/RENDER_SMOKE_TEST.md
```

Record:

```text
Smoke test account:
Smoke test date:
Smoke test result:
Issues found:
Fixes applied:
```

## 7. Changelog

```text
Added:
- Initial MVP backend and frontend.
- Expense tracking.
- Behavioral analytics.
- Savings insights and alerts.
- Goal tracking.
- Savings simulator.
- Deployment documentation.

Changed:
- N/A for first release.

Fixed:
- N/A for first release.

Security:
- JWT authentication.
- Production config validation.
- Security headers.
- Trusted host validation.
- Explicit CORS allow-lists.
- Request body size limit.

Deployment:
- Render selected as first provider.
- Backend Docker deployment path documented.
- Frontend static site deployment path documented.
- Production smoke test documented.

Known Issues:
- Docker Compose verification not run locally because Docker CLI is unavailable.
- ML, Pandas, Redis, banking, UPI, email, and SMS integrations are intentionally deferred.
```

## 8. Rollback Plan

If release fails after deployment:

1. Restore previous frontend deployment if frontend-only issue.
2. Restore previous backend deployment if backend issue.
3. Keep migrated database unless a tested rollback migration exists.
4. Review Render logs before manual database changes.

Record:

```text
Rollback owner:
Rollback trigger:
Rollback backend target:
Rollback frontend target:
Database rollback required: no, unless tested migration exists
```

## 9. Release Completion Checklist

Mark complete only when:

- Backend health is green.
- Database readiness is green.
- Frontend loads over HTTPS.
- Render smoke test passes.
- Render backend logs show no repeated server errors.
- Deployment URLs are recorded.
- Migration revision is recorded.
- Rollback targets are recorded.
- Post-launch monitoring has started.
- Render post-launch monitoring has started with `docs/RENDER_POST_LAUNCH_MONITORING.md`.
