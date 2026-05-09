# First Post-MVP Cycle Selection

Use this document to select the first post-MVP improvement cycle.

Current status:

```text
Selection status: pending real-user feedback
```

Do not begin implementation until evidence exists.

## 1. Required Evidence

Before selecting a cycle, collect:

- First-user feedback from `docs/FIRST_USER_FEEDBACK.md`.
- Launch monitoring notes from `docs/RENDER_POST_LAUNCH_MONITORING.md`.
- Release status from `docs/MVP_RELEASE_RECORD.md`.
- Roadmap candidates from `docs/POST_MVP_ROADMAP.md`.

## 2. Selection Options

Choose one:

| Cycle | Select When |
| --- | --- |
| Improve expense entry | Users struggle to add expenses quickly |
| Improve dashboard clarity | Users misunderstand dashboard metrics |
| Improve insight usefulness | Users find insights generic or unactionable |
| Improve goal tracking motivation | Users do not return to update goals |
| Improve trust and explanation | Users distrust behavior score or financial meaning |
| Fix launch bugs | Monitoring or smoke tests show blocking issues |

## 3. Decision Template

```text
Selected cycle:
Decision date:
Decision owner:

Evidence:
- User feedback:
- Monitoring signal:
- Support issue:
- Smoke test issue:

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

## 4. Selection Rules

Only select a cycle when:

- The issue appears repeatedly.
- The issue affects the core behavior loop.
- The fix can fit in one small release.
- The work does not require new infrastructure.
- The work does not pull deferred integrations forward.

## 5. Default Decision Before Feedback

Until feedback exists:

```text
Selected cycle: none
Decision: wait for first-user feedback
Reason: no accepted roadmap item has evidence yet
```

## 6. Implementation Gate

Step 97 can start only after:

- One cycle is selected.
- Accepted work is listed.
- Success metric is defined.
- Verification plan is defined.
- Release target is named.

Suggested first release target after selection:

```text
v0.1.1
```

Implementation readiness:

```text
docs/POST_MVP_RELEASE_PLAN.md
docs/POST_MVP_IMPLEMENTATION_READINESS.md
```

## 7. Completion Criteria

This step is complete when:

- The selection process is documented.
- Current status is explicitly marked pending evidence.
- No implementation work is accepted without feedback.
- Step 97 has a clear gate for release planning.
