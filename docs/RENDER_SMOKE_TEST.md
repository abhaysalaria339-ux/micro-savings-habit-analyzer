# Render Production Smoke Test

Use this checklist after the Render backend and frontend are deployed.

Complete first:

```text
docs/RENDER_BACKEND_DEPLOYMENT.md
docs/RENDER_FRONTEND_DEPLOYMENT.md
```

## 1. Required URLs

Record the deployed URLs:

```text
Frontend URL: https://<frontend-domain>
Backend URL: https://<backend-domain>
Backend API URL: https://<backend-domain>/api/v1
```

Do not start the smoke test until these URLs are known.

## 2. Backend Health Checks

Verify:

```text
GET https://<backend-domain>/api/v1/health
GET https://<backend-domain>/api/v1/health/db
```

Expected:

```text
Both return HTTP 200.
Database readiness returns database=reachable.
```

If either endpoint fails, stop and check:

- Render backend logs.
- `DATABASE_URL`.
- Migration status.
- `BACKEND_ALLOWED_HOSTS`.

## 3. Frontend Availability Checks

Open:

```text
https://<frontend-domain>
```

Verify:

- Page loads over HTTPS.
- Login screen appears.
- Register screen appears.
- Browser console has no startup errors.
- Refreshing `/dashboard` does not return 404.

If refresh fails, fix the Render rewrite:

```text
Source: /*
Destination: /index.html
Action: Rewrite
```

## 4. Smoke Test Account

Use a dedicated test account:

```text
Email: smoke-test+<date>@example.com
Password: SmokeTest123!
```

Do not use real financial data.

## 5. Core User Journey

Run this flow:

1. Register the smoke test user.
2. Confirm redirect to dashboard.
3. Log out.
4. Log back in.
5. Add expense: `4.50`, `Coffee`, `Morning coffee`.
6. Add expense: `6.00`, `Snacks`, `Afternoon snack`.
7. Add expense: `9.00`, `Transport`, `Short ride`.
8. Confirm expenses appear in history.
9. Open dashboard and confirm metrics render.
10. Open insights and confirm insights or empty states render.
11. Open goals.
12. Create goal: `Emergency fund`, target `1000.00`, current `100.00`.
13. Update goal progress.
14. Open simulator.
15. Calculate a `10%` reduction on `300.00`.

## 6. Render Log Checks

During and after the test, review backend logs for:

- HTTP 500 responses.
- CORS failures.
- Trusted host rejections.
- Database errors.
- Authentication errors.
- Missing request IDs.

Expected:

```text
No repeated server errors.
Request logs include request_id, path, route, status_code, and duration_ms.
```

## 7. Pass Criteria

The smoke test passes when:

- Backend health checks are green.
- Frontend loads over HTTPS.
- Auth flow works.
- Expense creation works.
- Dashboard renders.
- Insights and alerts render.
- Goal creation and progress update work.
- Simulator returns a projection.
- No blank pages appear.
- No CORS errors appear.
- Render backend logs show no repeated server errors.

## 8. Failure Triage

Use this order:

1. Backend health endpoints.
2. Render backend logs.
3. Render frontend build logs.
4. Browser network errors.
5. `VITE_API_BASE_URL`.
6. `BACKEND_CORS_ORIGINS`.
7. `BACKEND_ALLOWED_HOSTS`.
8. Migration status.

## 9. Cleanup

After smoke testing:

- Leave the smoke test user only if needed for future release checks.
- Delete test expenses if production data should remain clean.
- Record the smoke test result in the release record.
- Complete `docs/MVP_RELEASE_RECORD.md`.

## 10. Completion Criteria

This step is complete when:

- Render production smoke test passes.
- Any failed check has a recorded fix.
- Release record includes smoke test status.
- Post-launch monitoring begins using `docs/POST_LAUNCH_MONITORING.md`.
