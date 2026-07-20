---
description: Provide optional read-only advice on completed implementation work
agent: engineering-review-board
subtask: false
---

Provide optional advisory review for the completed implementation associated with:

$ARGUMENTS

Read the relevant plan, current repository, referenced commits or diff, and
supplied validation evidence. Do not modify the repository, plans, state, or
metadata.

Use `change-verifier` to map objectives, guardrails, non-goals, implementation steps, acceptance criteria, and required validation to concrete evidence. Select the minimum additional specialist panel for the actual change surface. Use `adversarial-reviewer` after the primary review when an independent hidden-flaw challenge materially improves confidence.

Return Board summary, baseline and scope, specialist coverage,
requirement-to-evidence matrix, guardrail assessment, advisory findings,
validation evidence, skipped validation, and residual risk. This review is
optional, read-only advice only: it creates no readiness, approval, sign-off,
persistence, or execution gate. Follow-up repair may be direct, may amend one
active plan through `/update-plan <exact-plan-path>`, may create new planned work
through `/create-plan`, or may separately execute existing work through
`/start-plan <path>`.
