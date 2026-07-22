---
description: Update one existing active implementation plan without executing it
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

This invocation is the human's explicit current authorization to update one
existing active plan in place under the constraints below; it grants no execution
authority.

Use syntax `/update-plan <exact-plan-path> [instructions]` for:

$ARGUMENTS

This command requires one explicit canonical plan path and never infers the
target from `.erb/plan-state.json`. Reject a missing or ambiguous path. Validate
the supplied path as a repository-relative canonical path matching either
`.erb/plans/<slug>.md` or `.erb/plans/<subject>/<NN>-<slug>.md`. Reject absolute
paths, traversal, symlinks, non-regular files, alternate roots, invalid UTF-8,
and content larger than 1 MiB.

Only an active plan with at least one unchecked TODO or Verification checkbox
may be updated. A completed plan remains immutable; direct additional work to a
new human-authorized `/create-plan` request. Review or consultation advice alone
is not update authority.

Re-read the exact plan and fresh repository evidence immediately before
mutation. Validate the existing canonical template. Apply the smallest
exact-content edit patch that satisfies the human's instructions. Keep the same
canonical path and exact ordered headings and fixed Context labels. Do not add
frontmatter, lifecycle metadata, history, provenance, revision, approval,
review, status, dependency, or concurrency fields. Re-read and validate the
entire resulting plan after the edit. If the exact-content patch no longer
matches fresh content, stop instead of overwriting concurrent or unexpected
changes.

Revalidate every TODO and Verification entry against the Plan Orchestrator's
checklist-entry contract. When ordering violates that contract, re-sequence the
smallest affected set. Dependency correctness outranks preserving existing
order. Keep all TODOs before dedicated Verification steps, keep each checklist
sequentially numbered, and report the old-to-new ordering and the reason for each
move.

Reconcile every plan checkbox conservatively:

- New TODO and Verification entries must be unchecked.
- Never change an unchecked checkbox to checked during an update.
- Retain a checked item only when its obligation and the surrounding acceptance
  contract remain materially unchanged and fresh evidence still supports it.
- Reset every changed, invalidated, or insufficiently evidenced checked item to
  unchecked.
- Reordering alone does not justify retaining checked state; apply the same
  evidence rules after every move.

Do not write or change `.erb/plan-state.json`. Do not delegate, implement,
validate implementation work, stage, commit, or execute TODOs. Do not update
native planned-work TODOs. Report the exact plan path; applied changes; checked
items retained or reset; entries added, removed, reordered, or renumbered;
observed validation; skipped checks; unresolved decisions; and residual risk.

A later explicit `/start-plan <existing-plan-path>` request is required to
execute or resume the updated plan.
