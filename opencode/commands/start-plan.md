---
description: Execute or resume an existing lean implementation plan
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

This invocation is the human's current request to execute or resume an existing
plan under the Plan Orchestrator contract, subject to the path, state, and
lifecycle validation below.

Use syntax `/start-plan [<plan-path>] [instructions]` to execute or resume an
existing canonical lean plan. `/start-plan` accepts only an explicit existing
canonical lean plan path or a no-argument state pointer. It rejects free-form new
requests and immutable legacy inputs. It does not create, succeed, convert, or
conversationally update plans. Direct human-authorized plan creation to
`/create-plan` and an in-place active-plan amendment to
`/update-plan <exact-plan-path>`.

The only durable workflow state is `.erb/plan-state.json`, with exactly this
shape and no additional fields:

```json
{"plan_path":".erb/plans/<path>.md"}
```

The exact schema is `{"plan_path":".erb/plans/<path>.md"}`.

Treat `plan_path` as untrusted input. It must be a repository-relative canonical
path matching either `.erb/plans/<slug>.md` or
`.erb/plans/<subject>/<NN>-<slug>.md`; reject absolute paths, traversal,
symlinks, non-regular files, alternate roots, and any path outside the current
repository. Accept exactly 1 MiB and reject limit-plus-one data for both the
state file and selected plan.

When the human supplies a path, validate that plan first, then write the exact
canonical path to `.erb/plan-state.json` and re-read both files before any
execution mutation. An explicit valid path replaces missing, invalid, or stale
state. Without an explicit path, read the state file and validate its exact
schema and selected plan. Without an explicit path, missing, invalid, or stale
state requires an explicit plan path; explain the issue and stop without
implementation.

The plan body must match the canonical lean template: exact ordered headings,
fixed Context labels, at least one numbered TODO checkbox, and at least one
numbered Verification checkbox. Display the resolved canonical path and its
checked and unchecked numbered TODOs and dedicated Verification checkboxes.

Derive lifecycle state from the plan body, never from fields in the state file:

- Active means at least one unchecked TODO or Verification checkbox remains.
- The current step is the first unchecked checkbox in document order.
- Complete means every TODO and Verification checkbox is checked.

If complete, say exactly: `This plan has already been implemented.` Then stop.
Do not delegate, implement, validate again, rewrite state, or mutate checkboxes.
Leave the state pointer selected so a later no-argument invocation reports the
same completed result.

If active, resume at the current step. Execute TODOs in document order before
dedicated Verification steps. Before each mutable phase, re-read the plan and
fresh worktree evidence. Delegate at most one bounded implementation TODO at a
time to `implementation-worker`; the Worker may not edit the plan or state file.
Check a TODO only after observed implementation or individual-validation
evidence authorizes it. Check a Verification step only after its own observed
evidence. A blocked, failed, or uncertain step remains unchecked and current.

When fresh evidence shows that the plan contract requires a material update,
leave the current checkbox unchecked, stop execution, and report the exact
mismatch plus the smallest proposed amendment. Direct the human to a separate
`/update-plan <exact-plan-path>` request. Do not update the plan in this command;
a later explicit `/start-plan` request is required to resume after amendment.

Use the Plan Orchestrator's self-contained delegation and
corrective-continuation contract. A Worker return does not end the current TODO.
Reconcile every acceptance criterion against fresh source, diff, and validation
evidence, and continue the same Task child for safe in-scope corrections until
the TODO is complete or a genuine blocker requires a human decision.
Each resumed correction prompt must enumerate the evidence gaps, blocked
criteria, required corrections, and validation to rerun. Never send only a TODO
status sentence or a deictic reference to findings that the prompt does not
contain.

The pointer selects a plan; it is not an exclusivity mechanism. The last valid
explicit selection wins. Never block because another plan is selected or may be
running. Do not attempt to detect, coordinate, serialize, or recover concurrent
plan execution.

Additional instructions may narrow validation or implementation choices, but
they may not change the selected plan body, skip unchecked steps, or expand the
Plan Orchestrator's authority. Active plan bodies are immutable during this
command except for evidenced `[ ]` to `[x]` checkbox advancement.
