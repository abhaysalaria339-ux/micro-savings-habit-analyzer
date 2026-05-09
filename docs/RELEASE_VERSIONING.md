# Release Versioning Notes

Use this guide to name and record production releases.

The goal is simple release traceability: every deployment should answer what was
released, when it was released, how it was verified, and how to roll it back.

## 1. Version Format

Use semantic versioning:

```text
MAJOR.MINOR.PATCH
```

For this MVP:

```text
0.1.0
```

Version meaning:

- `MAJOR`: breaking API or data model changes after public launch.
- `MINOR`: new user-facing features or API capabilities.
- `PATCH`: bug fixes, docs, security hardening, or deployment-only changes.

## 2. Git Tag Format

Use this tag format:

```text
v0.1.0
```

Examples:

```text
v0.1.0
v0.1.1
v0.2.0
```

Create a tag only after verification passes and the release candidate is ready
for deployment.

## 3. MVP Release Candidate

The first production release candidate should be:

```text
Version: 0.1.0
Tag: v0.1.0
Name: MVP Release
```

This release includes:

- FastAPI backend.
- PostgreSQL database.
- JWT authentication.
- Expense tracking.
- Analytics and behavior analysis.
- Savings insights and alerts.
- Savings simulator.
- Goal tracking.
- React frontend.
- Deployment documentation.

## 4. Release Record Template

Record each release with this format:

```text
Version:
Tag:
Date:
Released by:

Backend artifact:
Frontend artifact:
Database migration revision:

Verification:
- Backend lint:
- Backend tests:
- Frontend lint:
- Frontend tests:
- Frontend production build:
- Smoke test:

Deployment URLs:
- Frontend:
- Backend:

Rollback target:

Notes:
```

Keep release records in the project management tool, repository release notes,
or deployment provider notes.

For the first MVP release record, use:

```text
docs/MVP_RELEASE_RECORD.md
```

## 5. Changelog Discipline

For each release, summarize changes under these headings:

```text
Added
Changed
Fixed
Security
Deployment
Known Issues
```

Keep entries user-relevant and operationally useful. Avoid listing every small
internal refactor unless it affects behavior, deployment, security, or rollback.

## 6. Migration Tracking

Before releasing, record the current Alembic revision:

```text
alembic current
```

After migration, confirm:

```text
alembic current
```

The release record should include the final migration revision.

## 7. Version Bump Rules

Use `PATCH` for:

- Bug fixes.
- Security header or middleware hardening.
- Deployment documentation updates.
- Log formatting changes.
- Small UI fixes.

Use `MINOR` for:

- New dashboard sections.
- New insights or alert types.
- New API endpoints.
- New frontend workflows.

Use `MAJOR` later for:

- Breaking API contracts.
- Incompatible database changes after real users exist.
- Authentication behavior changes that require user action.

## 8. Release Gate

Do not tag or deploy a release unless these pass:

```powershell
cd backend
.venv\Scripts\python -m ruff check app tests
.venv\Scripts\python -m pytest
```

```powershell
cd frontend
npm run lint
npm run test
npm run build:production
```

After deployment, complete:

```text
docs/SMOKE_TEST_PLAN.md
```
