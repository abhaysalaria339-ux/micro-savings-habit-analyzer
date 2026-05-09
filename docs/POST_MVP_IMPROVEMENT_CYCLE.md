# Post-MVP Improvement Cycle

Use this guide after collecting first-user feedback.

The goal is to plan one focused improvement cycle, not a large roadmap.

## 1. Inputs

Use these inputs:

```text
docs/FIRST_USER_FEEDBACK.md
docs/MVP_RELEASE_RECORD.md
docs/RENDER_POST_LAUNCH_MONITORING.md
```

Required before planning:

- Feedback from initial users is categorized.
- Launch monitoring has no unresolved critical incidents.
- Release record is complete.
- Blocking bugs are known.

## 2. Cycle Goal

Choose one primary goal for the next cycle:

```text
Improve expense entry
Improve dashboard clarity
Improve insight usefulness
Improve goal tracking motivation
Improve trust and explanation
Fix launch bugs
```

Do not choose more than one primary goal for the first post-MVP cycle.

## 3. Planning Template

```text
Cycle name:
Cycle dates:
Primary goal:

Evidence:
- User feedback:
- Monitoring signal:
- Support issue:

Accepted work:
1.
2.
3.

Deferred work:
1.
2.

Rejected work:
1.
2.

Success metric:
Verification plan:
Release target:
```

## 4. Work Selection Rules

Accept work when:

- It appears in repeated feedback.
- It fixes a blocker or high-friction flow.
- It improves behavior insight clarity.
- It reduces user confusion or trust concerns.
- It can be completed in a small cycle.

Defer work when:

- It is useful but not repeatedly requested.
- It requires new infrastructure.
- It requires external providers.
- It depends on more user data.

Reject work when:

- It conflicts with the product focus.
- It turns the app into a generic expense tracker.
- It creates heavy maintenance for low value.
- It pulls in integrations before the MVP workflow is validated.

## 5. Recommended First Cycle Candidates

Choose from these only if feedback supports them:

| Candidate | When To Pick |
| --- | --- |
| Faster expense entry | Users struggle to add expenses quickly |
| Clearer dashboard labels | Users do not understand metrics |
| Better insight wording | Users find suggestions generic |
| Behavior score explanation | Users distrust or misunderstand scoring |
| Goal progress polish | Users do not feel motivated by goals |
| Bug fix cycle | Launch issues block core flows |

## 6. Deferred By Default

Keep these deferred unless strong evidence appears:

- Banking integrations.
- UPI integrations.
- Email or SMS alerts.
- ML model implementation.
- Redis/background jobs.
- Large redesign.
- Microservice migration.

## 7. Engineering Guardrails

For the first post-MVP cycle:

- Keep the modular monolith.
- Do not introduce new infrastructure unless required.
- Preserve API compatibility.
- Add tests for changed backend behavior.
- Keep frontend changes focused on the selected goal.
- Update deployment docs only if release behavior changes.

## 8. Verification Plan

Every accepted improvement must define:

```text
Backend tests:
Frontend tests:
Manual QA:
Smoke test impact:
Release note:
```

Minimum release gate remains:

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

## 9. Completion Criteria

This step is complete when:

- One primary cycle goal is chosen.
- Accepted work is limited to a small set.
- Deferred and rejected items are documented.
- Success metric is defined.
- Verification plan is defined.
- Step 95 can turn the cycle into a post-MVP roadmap.

Roadmap template:

```text
docs/POST_MVP_ROADMAP.md
docs/FIRST_POST_MVP_CYCLE_SELECTION.md
```
