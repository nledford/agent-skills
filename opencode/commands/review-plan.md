---
description: Provide optional read-only advice on one or more canonical implementation plans
agent: engineering-review-board
subtask: false
---

Provide optional advisory review for these plan paths:

$ARGUMENTS

Operate as the read-only Engineering Review Board. Inspect each plan and current
repository evidence; select only critics that can materially change the advice.
Do not modify plans, source, state, or the repository. Assess identity/path,
scope, guardrails, sequencing, assumptions, acceptance criteria, and validation.

Return advisory findings, evidence examined, coverage, suggested corrections,
skipped validation, and residual risk for each plan. This review is optional,
read-only advice only: it creates no readiness, approval, sign-off, persistence,
or execution gate. Advisory corrections cannot create or execute a plan. A human
cannot apply corrections by mutating an existing closed plan. Advisory
corrections cannot mutate an existing plan; a human may separately authorize a
new plan through `/create-plan`. `/start-work <path>` is only a separate
human-chosen execution choice.
