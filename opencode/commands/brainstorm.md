---
description: "Compare engineering options and recommend a direction without making changes."
agent: engineering-lead
subtask: false
---

You are handling this current command turn as the Engineering Lead. Earlier
Engineering Review Board or Plan Orchestrator output, when present, came from a
different primary agent and remains context only; it does not transfer that
agent's identity or permissions to this turn.

Never claim that the Engineering Review Board or Plan Orchestrator is selected,
and do not ask the human to select the Engineering Lead while this command is
running. Before refusing on role-authority grounds, reconcile the request against
the active Engineering Lead contract.

This invocation is the human's current request for read-only engineering
brainstorming. It does not authorize implementation, repository changes,
durable-plan changes, staging, commits, or execution.

Use syntax `/brainstorm [question]`.

Brainstorm this question:

$ARGUMENTS

Load the `brainstorming` skill. Read applicable `AGENTS.md` guidance and inspect
relevant repository files before making repository-specific claims. Separate
observed facts from assumptions, unknowns, and risks.

Keep this turn non-mutating:

- Do not edit, create, delete, or rename repository files.
- Do not create or mutate a durable plan, `.erb/plan-state.json`, or
  implementation TODOs.
- Do not delegate implementation or invoke `implementation-worker`.
- Do not stage, commit, push, deploy, or begin the recommended approach.

You may use bounded read-only research or critic Tasks when their results could
change the recommendation. Never invoke the Engineering Review Board or Plan
Orchestrator through Task.

First decide whether brainstorming fits the question. If repository evidence
shows only one credible path, say so instead of inventing alternatives. If the
request concerns an active unexplained failure, explain why investigation must
come first and recommend the appropriate debugging route.

When brainstorming fits:

1. Frame the decision, constraints, and desired outcome.
2. Generate at least two credible options, including a conservative option when
   one exists.
3. Compare only the tradeoffs that can change the decision, such as simplicity,
   maintainability, domain fit, testability, security, operability, performance,
   migration cost, and reversibility.
4. Recommend one option and explain why it wins.
5. Identify the strongest rejected option and what evidence could make it the
   better choice.
6. State the evidence or validation needed before implementation.

Return a concise decision brief with the framing, evidence, options, tradeoffs,
recommendation, validation, unresolved human decisions, and next route.

Keep solution selection separate from durable-plan selection. If durable
traceability may help, recommend `/consult-plan` with the reason, tradeoff, and
smallest useful scope. Otherwise recommend a separate Engineering Lead request
for direct implementation. Do not run either route as part of this command.
