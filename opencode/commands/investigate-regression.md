---
description: Investigate a potential bug or regression with the Engineering Review Board
agent: engineering-review-board
subtask: false
---

Investigate this potential bug or regression:

$ARGUMENTS

Establish expected behavior, observed behavior, reproduction evidence, last-known-good baseline, suspected range, environment, frequency, and available logs or tests. Inspect the relevant repository state and select the minimum sufficient specialist panel.

Prioritize whether the behavior is a genuine regression, introducing change, root cause, blast radius, smallest durable repair, required regression coverage, and remaining uncertainty. Distinguish confirmed root cause, probable root cause, and competing hypotheses; do not treat correlation as causation.

Do not modify the repository or a durable plan. If the remedy needs durable
planned work, return it to top-level `/start-work`.

Return:

- Root Cause Confirmed
- Probable Root Cause
- Investigation Incomplete

Include evidence, suspect change, failure path or interleaving, blast radius, proposed repair, tests, validation plan, skipped validation, and residual risk.
