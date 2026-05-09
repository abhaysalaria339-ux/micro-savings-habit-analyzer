# Post-MVP Roadmap

Use this roadmap after the MVP release, first-user feedback, and post-launch
monitoring checks.

This is a planning document. Do not treat candidate work as accepted until there
is feedback or monitoring evidence.

## 1. Roadmap Inputs

Use:

```text
docs/FIRST_USER_FEEDBACK.md
docs/POST_MVP_IMPROVEMENT_CYCLE.md
docs/MVP_RELEASE_RECORD.md
docs/RENDER_POST_LAUNCH_MONITORING.md
```

Required before finalizing roadmap items:

- Feedback is collected and categorized.
- Launch monitoring is stable.
- MVP release record is complete.
- One primary post-MVP cycle goal is selected.

## 2. Roadmap Buckets

Use these statuses:

| Status | Meaning |
| --- | --- |
| `accepted` | Approved for the next cycle |
| `deferred` | Valuable but not now |
| `rejected` | Not aligned with product direction |
| `investigate` | Needs more evidence |

## 3. Accepted Items

Do not add accepted work until evidence exists.

Template:

```text
Accepted item:
Evidence:
User impact:
Scope:
Backend changes:
Frontend changes:
Tests:
Release note:
```

Recommended limit for first cycle:

```text
1 primary goal
3 accepted work items maximum
```

## 4. Candidate Items Pending Evidence

These are likely post-MVP candidates, but require feedback before acceptance:

| Candidate | Evidence Needed |
| --- | --- |
| Faster expense entry | Users report expense entry friction |
| Dashboard copy improvements | Users misunderstand metrics |
| Insight wording improvements | Users find recommendations generic |
| Behavior score explanation | Users distrust or misunderstand classifications |
| Goal progress polish | Users do not feel motivated by goals |
| Bug fix cycle | Launch or smoke test issues block core workflows |

## 5. Deferred Items

Keep these deferred until MVP usage validates the core workflow:

- Banking API integration.
- UPI integration.
- Email alerts.
- SMS alerts.
- Redis caching or background jobs.
- Pandas-based data processing.
- ML clustering.
- ML classification.
- ML forecasting.
- Microservice migration.

Reason:

```text
These add infrastructure, provider dependency, or model complexity before the
core behavioral insight loop is proven with real users.
```

## 6. Rejected Items

Reject items that move the product away from behavioral finance.

Examples:

- Generic budgeting app redesign.
- Full accounting system.
- Social feed.
- Marketplace or offers engine.
- Investment advice workflows.
- Manual admin-only data editing as a core user feature.

Reason:

```text
They dilute the product focus: habit awareness, micro-spending detection,
savings insight, and behavior improvement.
```

## 7. Investigation Items

Use `investigate` for items that need discovery before implementation:

```text
Investigation:
Question:
Data needed:
User feedback needed:
Technical risk:
Decision deadline:
```

Good investigation candidates:

- Whether users trust the behavior score.
- Whether insights are too generic.
- Whether quick-add presets match real spending patterns.
- Whether goals motivate repeat use.
- Whether dashboard metrics are understandable.

## 8. First Cycle Recommendation

After feedback is collected, choose one:

```text
Cycle A: Improve expense entry
Cycle B: Improve dashboard clarity
Cycle C: Improve insight usefulness
Cycle D: Improve trust and explanation
Cycle E: Fix launch bugs
```

Default recommendation before feedback:

```text
Wait for feedback before selecting the cycle.
```

## 9. Roadmap Review Rules

Review the roadmap:

- After the first 7-14 days of feedback.
- After each production release.
- After any major incident.
- Before accepting provider integrations.

Each review should answer:

```text
What evidence changed?
What became accepted?
What stayed deferred?
What should be rejected?
What is the next single cycle goal?
```

## 10. Completion Criteria

This step is complete when:

- Roadmap buckets are defined.
- Candidate items are documented.
- Deferred integrations remain explicitly deferred.
- Rejected product directions are documented.
- First cycle selection waits for evidence.
- Step 96 can begin only after one cycle goal is selected.

Cycle selection record:

```text
docs/FIRST_POST_MVP_CYCLE_SELECTION.md
docs/POST_MVP_RELEASE_PLAN.md
docs/POST_MVP_IMPLEMENTATION_READINESS.md
```
