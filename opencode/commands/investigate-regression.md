---
description: Investigate a potential bug or regression with the Engineering Review Board
agent: engineering-review-board
subtask: false
---

Investigate this potential bug or regression:

$ARGUMENTS

Load `systematic-debugging` and `review-verification-protocol`.

Establish expected behavior, observed behavior, reproduction evidence, last-known-good baseline, suspected range, environment, frequency, and available logs or tests. Inspect the relevant repository state and select the minimum sufficient specialist panel.

Reproduce and narrow the active symptom before proposing a cause. Prioritize
whether the behavior is a genuine regression, introducing change, failure path,
blast radius, required regression coverage, and remaining uncertainty. Keep
competing hypotheses explicit and do not treat correlation as causation. Do not
recommend a repair while the direct cause remains unverified; hand off to `root-cause-analysis` only after the direct cause is understood and recurrence
prevention or a systemic control gap is the remaining question.

Do not modify the repository or a durable plan. Return repair guidance for
direct Lead implementation only when the direct cause is confirmed and the
repair is safely bounded. For a probable or incomplete result, return the next
discriminating experiment instead of a repair. When the human wants durable
repair planning, recommend top-level `/create-plan`; `/start-plan
<existing-plan-path>` is only a separate human-chosen execution of an existing
plan.

Return:

- Root Cause Confirmed
- Probable Root Cause
- Investigation Incomplete

Include evidence, suspect change, failure path or interleaving, blast radius,
tests, validation plan, skipped validation, and residual risk. Include a proposed
repair only for **Root Cause Confirmed**; otherwise include the next experiment
and the evidence it would distinguish.
