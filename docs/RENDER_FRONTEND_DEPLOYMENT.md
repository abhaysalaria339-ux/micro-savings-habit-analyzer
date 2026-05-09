# Render Frontend Deployment

Use this guide to deploy the React frontend as a Render Static Site.

Complete first:

```text
docs/RENDER_BACKEND_DEPLOYMENT.md
```

Do not deploy the frontend until the backend health checks pass.

## 1. Frontend Service Settings

Create a Render Static Site for the frontend.

Recommended settings:

| Setting | Value |
| --- | --- |
| Service name | `micro-savings-frontend` |
| Service type | Static Site |
| Root directory | `frontend/` |
| Build command | `npm ci && npm run build:production` |
| Publish directory | `frontend/dist/` |

If Render treats `frontend/` as the root directory, use:

| Setting | Value |
| --- | --- |
| Build command | `npm ci && npm run build:production` |
| Publish directory | `dist/` |

## 2. Frontend Environment

Set this Render static site environment variable:

```env
VITE_API_BASE_URL=https://<backend-domain>/api/v1
```

Required:

- Use the deployed backend domain.
- Include `/api/v1`.
- Do not use localhost.
- Do not include a trailing slash after `/api/v1`.

## 3. Backend CORS Confirmation

Before deploying the frontend, update the backend Render service:

```env
BACKEND_CORS_ORIGINS=["https://<frontend-domain>"]
```

Then redeploy or restart the backend if Render requires it for environment
changes.

The frontend origin must match exactly, including `https://`.

## 4. React Router Rewrite

Add a Render static site rewrite rule:

```text
Source: /*
Destination: /index.html
Action: Rewrite
```

This prevents browser refreshes on protected routes from returning 404.

## 5. Frontend First Deploy

Deploy the static site after:

- Backend health endpoint passes.
- Database readiness endpoint passes.
- `VITE_API_BASE_URL` is configured.
- CORS origin is configured on the backend.
- Rewrite rule exists.

Expected:

- Build succeeds.
- Static site deploys over HTTPS.
- Login and register pages load.
- Protected routes redirect unauthenticated users to login.

## 6. Frontend Verification

Open:

```text
https://<frontend-domain>
```

Verify:

- Login page loads.
- Register page loads.
- Refreshing `/dashboard` does not return 404.
- Browser network requests target `https://<backend-domain>/api/v1`.
- No CORS errors appear.

Then continue to:

```text
docs/SMOKE_TEST_PLAN.md
docs/RENDER_SMOKE_TEST.md
```

## 7. Common Frontend Deployment Errors

Blank page:

- Check Render build logs.
- Confirm publish directory is correct.
- Confirm `npm run build:production` completed successfully.

API calls go to localhost:

- Check `VITE_API_BASE_URL`.
- Rebuild the static site after changing the variable.

CORS error:

- Confirm backend `BACKEND_CORS_ORIGINS` exactly matches the frontend domain.
- Restart or redeploy backend after changing environment variables.

404 on refresh:

- Add or fix the Render rewrite rule from `/*` to `/index.html`.

Login/register fail:

- Check backend health endpoints.
- Check browser network tab for the failing API response.
- Check backend logs for validation, database, or CORS errors.

## 8. Completion Criteria

This step is complete when:

- Render frontend static site is created.
- `VITE_API_BASE_URL` points to the deployed backend API.
- Backend CORS allows the frontend domain.
- React Router rewrite is configured.
- Frontend loads over HTTPS.
- Refreshing client-side routes works.
- Browser requests reach the deployed backend.
