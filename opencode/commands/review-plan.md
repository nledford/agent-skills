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
or execution gate. Advisory corrections cannot create, update, or execute a
plan. A human may separately authorize an in-place update of one active plan
through `/update-plan <exact-plan-path>`, create a new plan through
`/create-plan`, or direct the top-level Plan Orchestrator to perform guarded
conversational replacement of one unambiguous canonical plan with at least two
successors. The review itself never supplies any mutation authority.
`/start-plan <path>` is only a separate human-chosen execution choice.
