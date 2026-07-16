## Durable implementation-plan workflow

Use the smallest canonical layout. One plan is `.erb/plans/<slug>.md`, with no
subject directory or numeric prefix. Only genuinely separately managed plans use
`.erb/plans/<subject>/<NN>-<slug>.md`; multiple TODOs alone do not justify a
series. A series uses one safe lowercase subject and zero-padded max-plus-one
numbers across live files and registered history from `01` through `99` without
gap or deleted-sequence reuse. Stop on collision, exhaustion, containment
uncertainty, symlinks, or unsafe parents.

New plans use exactly the closed shape in
`docs/implementation-plans/TEMPLATE.md`: no frontmatter, lifecycle fields,
review records, history, provenance, metadata, or additional headings. TODO and
Verification sections contain predeclared numbered checkboxes. After creation,
plan content is immutable except for changing an existing `[ ]` marker to `[x]`
after observed evidence. Do not add, remove, rewrite, reorder, or renumber plan
content. Complete every TODO before beginning or checking any dedicated
Verification step; individual TODO validation may run before that TODO is
checked.

Former plans under `docs/implementation-plans/plans/` are immutable legacy
artifacts, are not execution inputs, do not affect new-root allocation, and are
never automatically migrated. Stop for a human decision when a discovery or
legacy artifact requires material work, validation, or design outside a closed
plan.

The Engineering Lead owns classification, direct unplanned implementation,
integration, validation, and handoffs. Prefer direct implementation whenever
scope and safety permit. When planning advice would help, the Lead or ERB may
recommend top-level `/consult-plan` with the reason, trade-off, and proposed
scope. Consultation is a separate read-only Plan Orchestrator primary route; it
creates and mutates no plan or state, acquires no planned-work ownership,
delegates and implements nothing, authorizes no work, and is never a Task child.
The human's decision to require, decline, or override the recommendation controls
the route.

Only an explicit human `/create-plan` request creates and persists a plan, and it
is plan-only. It registers each new immutable contract with all checkboxes
unchecked. Execution-only `/start-work` accepts an existing valid registered
canonical plan or a validated no-argument active pointer with explicit human
confirmation. `/convert-tapestry-plan` remains plan-only and preserves its
source. Existing plans cannot be updated in place; a human may authorize a new
plan. The Plan Orchestrator is the only durable plan and trusted-state writer.
The Implementation Worker cannot edit durable plans, read or mutate
`.start-work/**`, invoke its trusted helper, stage, commit, delegate, deploy, or
broaden its assigned unit.

Repository users may choose to add `.erb/plans/` to their own `.gitignore`. Do
not require or automatically add that rule merely because plans use this root.
Before trusted-state persistence, keep these exact narrow rules once and stop on
broader, duplicate, ambiguous, or conflicting `.start-work` rules:

```text
/.start-work/resume.json
/.start-work/lock/
```

The trusted state uses schema version 2; version-1 pointers and former-root paths
are rejected without automatic migration. The Plan Orchestrator acquires trusted
provisional ownership before every mutating lifecycle route and uses only the
installed linked helper for state transitions. After exact acquisition,
`/start-work` invokes the internal `begin-execution` preflight. Known
pre-execution validation failures release only their matching newly acquired
lock and return sanitized error codes. `lock-held` recovery requires explicit
human confirmation that no planned mutator remains and is never automatic.

A planned-work commit is permitted only for an explicit current human request.
The Plan Orchestrator may then commit an appropriately complete, validated,
coherent unit during implementation or after it completes. Derive and separately
enumerate exact repository-relative paths from fresh worktree evidence, quote
each as one literal shell word, use `git add --`, and recheck staged and resulting
worktree state. Never use expansion syntax, amend, bypass hooks or signing, or
mutate remotes, refs, branches, history, or worktrees. Runtime approval is an
additional check, not proof that a path is safe. The Worker remains forbidden
from staging or committing. Fully restart OpenCode before definition changes
grant authority; the running session remains unchanged.
