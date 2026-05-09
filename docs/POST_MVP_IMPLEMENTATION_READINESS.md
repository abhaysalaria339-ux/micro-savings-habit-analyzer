# Post-MVP Implementation Readiness

Use this document before implementing the first post-MVP improvement.

Current status:

```text
Implementation status: blocked pending evidence-backed selection
```

## 1. Why Implementation Is Blocked

Implementation cannot begin yet because:

- Real-user feedback has not been recorded.
- No post-MVP cycle has been selected.
- No accepted roadmap item exists.
- Step 97 release planning has not been completed.

Building a feature now would be guesswork and would violate the roadmap rules.

## 2. Required Inputs

Before implementation starts, complete:

```text
docs/FIRST_USER_FEEDBACK.md
docs/POST_MVP_ROADMAP.md
docs/FIRST_POST_MVP_CYCLE_SELECTION.md
```

Then prepare:

```text
docs/POST_MVP_RELEASE_PLAN.md
```

## 3. Implementation Gate

Implementation can start only when all are true:

- One cycle is selected.
- Accepted work items are listed.
- Evidence is recorded.
- Backend changes are scoped.
- Frontend changes are scoped.
- Tests are identified.
- Manual QA is defined.
- Release target is defined.

Expected first post-MVP release target:

```text
v0.1.1
```

## 4. Accepted Work Template

Use this before coding:

```text
Accepted item:
Evidence:
User impact:
Backend files:
Frontend files:
Tests:
Manual QA:
Release note:
Rollback note:
```

## 5. Engineering Rules

For the first post-MVP implementation:

- Keep changes small.
- Preserve existing API compatibility.
- Keep the modular monolith.
- Do not add new infrastructure.
- Do not implement ML yet.
- Do not add banking, UPI, email, or SMS integrations yet.
- Add tests for changed backend behavior.
- Run frontend lint, tests, and production build.

## 6. Completion Criteria

This readiness step is complete when:

- The implementation blocker is documented.
- Required inputs are listed.
- The implementation gate is explicit.
- No runtime code is changed without an accepted roadmap item.
