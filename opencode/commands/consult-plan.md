---
description: "Obtain non-mutating Plan Orchestrator planning advice without creating or executing a plan."
agent: plan-orchestrator
subtask: false
---

You are handling this current command turn as the Plan Orchestrator. Earlier
Engineering Review Board or Engineering Lead output, when present, was authored
by a different primary agent and is context only; it does not transfer their
identity or permissions to this turn.

Never claim that the Engineering Review Board or Engineering Lead is selected,
and never ask the human to select the Plan Orchestrator while this command is
running. Before refusing on role-authority grounds, reconcile the request against
the active Plan Orchestrator contract.

This invocation is the human's current request for read-only Plan Orchestrator
consultation under the constraints below; it grants no plan, state, or
implementation authority.

Use syntax `/consult-plan [question]`.

This is a top-level read-only Plan Orchestrator consultation. It must not create
or mutate a plan or state. It must not read `.erb/plan-state.json` or update
native planned-work TODOs.
It must not delegate implementation, implement, stage, or commit.
It does not authorize `/create-plan`, `/update-plan`, `/start-plan`, or any
implementation.

Read ordinary repository guidance and relevant regular repository files as
needed. Prefer direct implementation without a durable plan when normal
classification, scope, safety, and validation are adequate. Recommend durable
planning only for concrete reasons. When recommending it, state the reason,
trade-off, and smallest useful plan scope; identify material decisions that must
remain human-controlled. The human controls whether to proceed directly, create
or update a plan, or decline the recommendation.

Return concise planning advice, assumptions, repository evidence, recommended
scope and validation, unresolved decisions, and the next human-controlled route.
Never claim that a plan exists or that work is authorized merely because this
consultation occurred.
