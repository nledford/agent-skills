---
description: "Obtain non-mutating Plan Orchestrator planning advice without creating or executing a plan."
agent: plan-orchestrator
subtask: false
---

Use syntax `/consult-plan [question]`.

This is a top-level read-only Plan Orchestrator consultation. It does not
acquire planned-work ownership and must not create or mutate a plan or trusted
state. It must not read `.start-work/**`, invoke a workflow-state helper, update
native planned-work TODOs.
It must not delegate implementation, implement, stage, or commit.
It does not authorize `/create-plan`, `/start-work`, or any implementation.

Read ordinary repository guidance and relevant regular repository files as
needed. Prefer direct implementation without a durable plan when normal
classification, scope, safety, and validation are adequate. Recommend durable
planning only for concrete reasons. When recommending it, state the reason,
trade-off, and smallest useful plan scope; identify material decisions that must
remain human-controlled. The human controls whether to proceed directly, create
a plan, or decline the recommendation.

Return concise planning advice, assumptions, repository evidence, recommended
scope and validation, unresolved decisions, and the next human-controlled route.
Never claim that a plan exists or that work is authorized merely because this
consultation occurred.
