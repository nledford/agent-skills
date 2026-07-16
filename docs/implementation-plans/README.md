# Implementation Plans

This directory contains the reusable contract and template for repository-local
durable implementation plans. Plan documents themselves live under `.erb/plans/`.
They are closed execution contracts, not status dashboards, review records, or
automatic routing mechanisms.

## Canonical Location And Layout

Use the smallest layout that safely represents the work:

- One plan: `.erb/plans/<slug>.md`. Do not create a subject directory or numeric
  prefix.
- Multiple genuinely separately managed plans:
  `.erb/plans/<subject>/<NN>-<slug>.md`.

Multiple TODOs within one bounded plan do not justify a multi-plan series. A
multi-plan series uses one lowercase contained subject, sequential zero-padded
numbers `01` through `99`, and max-plus-one allocation across live files and
registered history without gap or deleted-sequence reuse. Stop on collisions,
exhaustion, symlinks, unsafe parents, mixed layouts, traversal, or containment
uncertainty.

Repository users may choose to add `.erb/plans/` to their own `.gitignore`. This
is optional. The Plan Orchestrator must not require or automatically make that
edit merely because plans use this location.

Former canonical plans under `docs/implementation-plans/plans/` are immutable
legacy artifacts. They are not new execution inputs, do not participate in
`.erb/plans/` allocation, and are never moved, rewritten, or automatically
migrated. Work based on one requires a new human decision and, when authorized,
a new canonical plan.

## Closed Lean Format

Every new plan follows [TEMPLATE.md](TEMPLATE.md) exactly: one title, the eight
ordered `##` headings, the three fixed Context labels, numbered TODO checkboxes,
and numbered Verification checkboxes. Do not add frontmatter, metadata,
lifecycle fields, status, history, provenance, approvals, review records,
dependency fields, or extra headings. Keep unresolved material choices in the
conversation; do not add an `Open Decisions` section.

After creation, the body is immutable. During execution the Plan Orchestrator may
only change an existing checkbox marker from `[ ]` to `[x]` after observed
evidence supports that item. It must not add, remove, rewrite, reorder, or
renumber TODOs, Verification steps, headings, or other content. A discovery that
requires material new work, validation, or a design decision outside the closed
plan stops execution for the normal human-decision and durable-plan routing
rules; it never changes the plan in place.

The narrow conversational plan replacement lifecycle below may retire one exact
source plan file after its successors are safely registered. It never authorizes
rewriting the source or successors, and trusted state retains the source's
immutable contract as history.

## Human-Controlled Lifecycle

Prefer direct implementation without a durable plan whenever normal
classification, scope, safety, and validation are sufficient.

Three human-controlled lifecycle paths remain distinct:

1. Top-level `/consult-plan` obtains read-only Plan Orchestrator planning advice.
   It acquires no planned-work ownership, reads or mutates no trusted state,
   creates or changes no plan, delegates and implements nothing, and authorizes
   no later action. The Lead or ERB recommends it only with a concrete reason,
   trade-off, and proposed scope. The human controls whether to require, decline,
   or override that recommendation.
2. An explicit human `/create-plan` request may create and persist one or more new
   plans. Creation is plan-only, leaves every checkbox unchecked, registers each
   immutable plan contract through the trusted helper, and never executes it.
3. Execution-only `/start-work <existing-plan-path>` accepts an existing valid
   registered canonical plan. A no-path resume is allowed only from a validated
   active pointer and requires explicit human confirmation after displaying the
   resolved path and checklist state.

A current explicit request to split or replace one specific canonical plan is
conversational plan replacement authority; no new slash command or additional
deletion confirmation is required. An exact path or the current conversation
must identify one unambiguous source. Review advice alone does not authorize
mutation. The source must be registered, unchanged, unchecked, and inactive, and
the result must contain at least two separately managed successor plans. The Plan
Orchestrator creates, re-reads, and finalizes every successor, then invokes the
trusted helper's `register-replacement` operation. If registration fails, the
source is not deleted and the lock is retained. After registration succeeds,
the source and successors are immediately re-read and checked for drift. After
those checks, the original plan file is retired with an exact-content edit patch
and the plan inventory is re-read, and registered history retains its immutable
contract,
preventing path or sequence reuse. Deletion or verification uncertainty retains
the lock.

Explicit `/convert-tapestry-plan` remains plan-only and preserves its source.
Optional `/review-plan` and completed-work ERB review are read-only advisory
routes, never approval, persistence, or execution gates. Existing plans cannot be
updated to apply review advice; a human may authorize a new plan or guarded
replacement instead.

## Execution And Evidence

The Plan Orchestrator owns the lock, trusted-state transitions, integration,
checkboxes, and planned-work commits. The Implementation Worker receives at most
one bounded unit, cannot edit plans, cannot read or mutate `.start-work/**` or
invoke its trusted helper, and must never stage or commit.

For an executed plan:

1. Validate as needed for an individual TODO, then check that TODO only after
   observed evidence supports completion.
2. Complete and persist every TODO before beginning or checking any dedicated
   Verification step.
3. Check each Verification step only after its own observed evidence supports it.

Native TODO state mirrors the TODO phase first and the Verification phase only
after every TODO is complete. It is transient coordination, not approval or
plan content.

A planned-work commit is permitted only when the human has explicitly and
currently requested one. With that request, the Plan Orchestrator may commit an
appropriately complete, validated, coherent unit during implementation or after
implementation completes. Runtime approvals, exact literal path derivation,
staging reconciliation, hook and signing checks, and history protections still
apply. The Worker remains forbidden from staging or committing. OpenCode agent
permission changes take effect only after a full OpenCode restart.

## Trusted State And Compatibility

Every mutating Plan Orchestrator route acquires the repository-owned helper's
complete provisional child lock before reading locators, allocation, plan,
pointer, worktree, or execution state. Keep these narrow ignore rules exactly
once:

```gitignore
/.start-work/resume.json
/.start-work/lock/
```

After that exact literal acquisition, `/start-work` uses the helper's internal
`begin-execution` operation. An explicit-path preflight validates the registered
contract, finalizes ownership, and activates the pointer as one phase. A no-path
preflight returns the active pointer under provisional ownership so the human
can confirm or decline execution. Known pre-execution validation failures
release only the matching newly acquired lock; failures after pointer,
implementation, or child mutation retain the lock.

`resume.json` schema version 2 registers immutable plan contracts and records at
most one active execution pointer. Version-1 pointers and former-root paths are
rejected fail-closed; there is no automatic migration. Unexpected `.start-work`
entries, malformed state, unregistered plans, body mutations, checkbox reversal,
or Verification progress before persisted TODO completion stop execution and
return a sanitized error code. `lock-held` requires explicit human confirmation
that no planned mutator remains before exact stale recovery; it is never
recovered automatically. Incompatible or unregistered state requires a human
creation, conversion, or migration decision rather than automatic registration.

Use the installed helper only through its allowlisted isolated operations. Never
put human, plan, locator, repository, or instruction text into helper-launch shell
strings, redirects, pipes, substitutions, or compound commands.
