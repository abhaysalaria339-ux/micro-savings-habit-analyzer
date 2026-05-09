# First Real-User Feedback Guide

Use this guide after the MVP is live and the first users try the product.

The goal is to learn whether the product helps users understand spending habits,
not to collect every possible feature request.

## 1. Feedback Window

Collect feedback during the first 7-14 days after launch.

Focus on:

- Expense entry friction.
- Dashboard clarity.
- Micro-spending insight usefulness.
- Savings recommendation usefulness.
- Goal tracking motivation.
- Confusing flows.
- Missing information users expected to see.

## 2. User Interview Questions

Ask each tester:

1. What was the first thing you understood from the dashboard?
2. Was adding an expense fast enough?
3. Did any insight make you notice a real spending habit?
4. Were the savings suggestions specific enough to act on?
5. Did the goal screen make progress feel clear?
6. Where did you feel confused or unsure?
7. What would make you return tomorrow?
8. What felt unnecessary?

Avoid leading users toward planned features like ML or banking integrations.

## 3. Feedback Intake Template

Record each feedback item:

```text
Date:
User type:
Screen or flow:
Feedback:
Observed behavior:
Severity: low | medium | high
Category: usability | bug | insight-quality | performance | missing-feature | trust
Decision: accept | defer | reject | investigate
Follow-up:
```

## 4. Feedback Categories

Use these categories:

| Category | Meaning |
| --- | --- |
| `usability` | User could not complete or understand a workflow |
| `bug` | Something failed or behaved incorrectly |
| `insight-quality` | Insight was unclear, generic, or not actionable |
| `performance` | Page, API, or interaction felt slow |
| `missing-feature` | User expected a feature not in the MVP |
| `trust` | User felt unsure about privacy, data, or financial interpretation |

## 5. Prioritization Rules

Prioritize first:

1. Bugs that block registration, login, expense entry, goals, dashboard, or simulator.
2. Confusing flows that stop users from reaching insights.
3. Insight-quality issues that make recommendations feel generic.
4. Trust issues around financial data or behavior scoring.
5. Repeated requests from multiple users.

Defer:

- Banking integrations.
- UPI integrations.
- Email or SMS alerts.
- ML implementation.
- Redis/background jobs.
- Large redesigns without repeated evidence.

## 6. Success Signals

Strong MVP signals:

- Users add multiple expenses without guidance.
- Users understand at least one money leak.
- Users can explain their behavior score.
- Users try the savings simulator.
- Users create or update a goal.
- Users ask to continue using the app with real data.

Weak MVP signals:

- Users treat it as only an expense tracker.
- Users ignore insights.
- Users cannot understand dashboard metrics.
- Users distrust the behavior score.
- Users stop before adding expenses.

## 7. Post-Feedback Summary Template

After collecting feedback, summarize:

```text
Feedback period:
Number of users:
Top repeated pain points:
Top repeated useful moments:
Blocking bugs:
Insight quality issues:
Trust concerns:
Accepted improvements:
Deferred requests:
Rejected requests:
Recommended next sprint:
```

## 8. Completion Criteria

This step is complete when:

- Feedback has been collected from initial users.
- Feedback is categorized.
- Repeated issues are identified.
- Accepted improvements are separated from deferred requests.
- Step 94 planning can prioritize a focused post-MVP improvement cycle.

Next planning step:

```text
docs/POST_MVP_IMPROVEMENT_CYCLE.md
docs/POST_MVP_ROADMAP.md
docs/FIRST_POST_MVP_CYCLE_SELECTION.md
```
