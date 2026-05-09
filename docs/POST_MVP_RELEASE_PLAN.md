# Post-MVP Release Plan

Use this document to plan the first post-MVP release after a cycle is selected.

Current status:

```text
Release plan status: blocked pending selected cycle
```

Expected first post-MVP release target:

```text
v0.1.1
```

## 1. Required Inputs

Complete before filling this plan:

```text
docs/FIRST_USER_FEEDBACK.md
docs/POST_MVP_ROADMAP.md
docs/FIRST_POST_MVP_CYCLE_SELECTION.md
docs/POST_MVP_IMPLEMENTATION_READINESS.md
```

## 2. Release Identity

```text
Release version:
Release name:
Target date:
Owner:
Selected cycle:
```

## 3. Evidence

Record why this release exists:

```text
User feedback:
Monitoring signal:
Smoke test issue:
Support issue:
Roadmap item:
```

Do not proceed if evidence is blank.

## 4. Scope

Accepted work:

```text
1.
2.
3.
```

Out of scope:

```text
1.
2.
3.
```

Deferred:

```text
1.
2.
3.
```

## 5. Technical Plan

Backend:

```text
Files:
Behavior changes:
Tests:
Migration required: yes | no
```

Frontend:

```text
Files:
UI changes:
Tests:
Manual QA:
```

Deployment:

```text
Environment changes:
Migration command:
Smoke test impact:
Rollback target:
```

## 6. Verification Gate

Required before release:

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

Manual QA:

```text
Focused flow:
Regression flow:
Smoke test:
```

## 7. Release Notes Template

```text
Version:
Date:

Added:

Changed:

Fixed:

Security:

Deployment:

Known Issues:
```

## 8. Rollback Plan

```text
Rollback trigger:
Backend rollback:
Frontend rollback:
Database rollback required:
Rollback owner:
```

Do not roll back database schema unless a tested rollback migration exists.

## 9. Completion Criteria

This release plan is complete when:

- Selected cycle is recorded.
- Evidence is recorded.
- Accepted work is limited and scoped.
- Backend and frontend files are identified.
- Tests and manual QA are defined.
- Rollback target is defined.
- Release notes are drafted.
