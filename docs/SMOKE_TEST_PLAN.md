# End-To-End Smoke Test Plan

Use this plan after local full-stack startup, preview deployment, or production
deployment.

## 1. Test Scope

This smoke test verifies the core MVP user journey:

- Account registration.
- Login.
- Expense creation and history.
- Dashboard analytics.
- Goal creation and progress.
- Savings insights and alerts.
- Savings simulator.

## 2. Test Data

Use a dedicated test account:

```text
Email: smoke-test+<date>@example.com
Password: SmokeTest123!
```

Use these sample expenses:

| Amount | Category | Description |
| --- | --- | --- |
| `4.50` | `Coffee` | `Morning coffee` |
| `6.00` | `Snacks` | `Afternoon snack` |
| `9.00` | `Transport` | `Short ride` |

Use this sample goal:

```text
Name: Emergency fund
Target amount: 1000.00
Current amount: 100.00
```

## 3. Backend Health Checks

Verify:

```text
GET <backend-url>/api/v1/health
GET <backend-url>/api/v1/health/db
```

Expected:

```text
Both return HTTP 200.
Database readiness returns database=reachable.
```

## 4. Frontend User Journey

1. Open the frontend URL.
2. Register the smoke test user.
3. Confirm the app redirects to the dashboard.
4. Log out.
5. Log back in with the same user.
6. Add the three sample expenses.
7. Confirm expenses appear in recent expenses.
8. Open dashboard and confirm metric panels render.
9. Open insights and confirm alerts or empty states render.
10. Create the sample savings goal.
11. Update goal progress.
12. Open simulator and calculate a 10% reduction on `300.00`.

## 5. Pass Criteria

The smoke test passes when:

- No blank pages appear.
- No unhandled browser errors appear.
- Auth token persists after login.
- Expense creation updates expense history.
- Dashboard, insights, goals, and simulator screens render without API errors.
- Forms show validation or success feedback.
- Backend health checks remain green.

## 6. Failure Triage

Use this order:

1. Check frontend API URL: `VITE_API_BASE_URL`.
2. Check backend CORS: `BACKEND_CORS_ORIGINS`.
3. Check backend host allow-list: `BACKEND_ALLOWED_HOSTS`.
4. Check backend logs for authentication, migration, or database errors.
5. Check browser console for API failures.
6. Confirm migrations ran with `sh scripts/migrate.sh`.

## 7. Cleanup

After testing:

- Delete smoke test expenses if the environment should stay clean.
- Leave the smoke test user only in staging or preview environments.
- Do not use real financial data for smoke tests.
