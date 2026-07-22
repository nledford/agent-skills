# Implementation Plans

Use this contract for project-local implementation plans that must survive a
pause, context reset, or OpenCode restart. Prefer direct implementation when
scope, safety, and validation are already adequate. Complexity may justify a
planning recommendation, never automatic plan creation.

## Canonical Paths

Use one plan at:

```text
.erb/plans/<slug>.md
```

Use a series only when work needs separately managed plan documents:

```text
.erb/plans/<subject>/<NN>-<slug>.md
```

A single plan has no subject directory or numeric prefix. A series uses one
contained subject and zero-padded numbers from `01` through `99`. Allocate the
maximum number among live files plus one. Multiple TODOs in one bounded plan do
not justify a series.

## Canonical Format

Plans contain no frontmatter or lifecycle metadata. Use the exact ordered
headings and fixed Context labels in [`TEMPLATE.md`](TEMPLATE.md). TODO and
Verification entries are numbered Markdown checkboxes. Create every checkbox
unchecked.

Active plan prose and structure are immutable by default. During execution, only
an evidenced `[ ]` to `[x]` checkbox change is allowed. Do not add, remove,
rewrite, reorder, or renumber plan content during `/start-plan`.

A current explicit `/update-plan <exact-plan-path>` request may update one active
plan in place without executing it. Completed plans remain immutable. New
checklist entries stay unchecked, unchecked entries never become checked during
an update, and checked entries remain checked only when their obligation and the
surrounding acceptance contract are materially unchanged and fresh evidence
still supports them.

## Checklist Entry Contract

This contract applies whenever a plan is created, reviewed, updated, or
executed.

- Every TODO or Verification entry has one atomic purpose: one finite,
  observable outcome with focused completion evidence. Tightly coupled actions
  may share an entry only when they are inseparable from that outcome; split
  unrelated, multi-phase, or independently verifiable work.
- Every entry must be executable from satisfied external dependencies,
  repository state, and completed earlier entries. Put prerequisites before
  dependents. An entry must not depend on itself or a later checklist entry, and
  the plan must contain no dependency cycle or mutually waiting steps.
- Disclose any known ask-gated or destructive operation and its exact contained
  target in the entry text when repository evidence supports it. If none is
  disclosed, no special permission is expected. This planning disclosure is not
  approval; execution reclassifies the actual operation against current runtime
  policy.
- Give every entry a finite completion or stop condition. Do not encode an
  unbounded retry, polling, or correction loop. Blocked, denied, pending, failed,
  or replay-uncertain work remains unchecked and follows the execution rules
  below.

## Human-Controlled Lifecycle

The workflow has four routes:

1. The Engineering Lead implements directly when normal scope, safety, and
   validation are adequate.
2. An explicit human `/create-plan` request creates and persists a plan only.
   It does not execute TODOs.
3. An explicit human `/update-plan <exact-plan-path>` request updates one active
   plan in place without changing state or executing TODOs.
4. A separate human `/start-plan <existing-plan-path>` request executes an
   existing canonical plan. With no path, `/start-plan` resumes the plan
   selected in `.erb/plan-state.json`.

The Lead or ERB may recommend top-level `/consult-plan` for read-only advice,
stating the reason, trade-off, and proposed scope. The human decides whether to
create, update, or execute a plan.

## Plan State

The only durable workflow state is `.erb/plan-state.json`:

```json
{"plan_path":".erb/plans/<path>.md"}
```

It stores exactly one repository-relative canonical plan path. It does not store
status, current step, history, hashes, ownership, or concurrency data.

Derive state from the selected plan:

- Active means at least one TODO or Verification checkbox is unchecked.
- The current step is the first unchecked checkbox in document order.
- Complete means every TODO and Verification checkbox is checked.

If the plan is complete, `/start-plan` reports: `This plan has already been
implemented.` It then stops without implementation, delegation, validation, or
state mutation.

An explicit valid plan path replaces missing, invalid, or stale state. Without
an explicit path, unusable state requires the user to provide a plan path. The
latest valid explicit selection wins. This pointer is not an exclusivity or
concurrency mechanism; attempts to run multiple plans are not coordinated or
blocked.

Repositories may ignore `/.erb/plan-state.json` or a broader local plan
directory according to project policy. Missing ignore rules never block plan
creation or execution.

## Creation

Validate the request against repository evidence and the checklist-entry
contract, choose the smallest layout, write the plan with all boxes unchecked,
and re-read it. Then write the selected canonical path to
`.erb/plan-state.json` and re-read both files. Stop without implementation.

A current explicit split-or-replace request may create at least two successors
and retire one unambiguous source. Create and re-read every successor, re-read
the exact source, and only then delete the source with an exact-content edit
patch. If successor creation or verification fails, keep the source. No registry,
retained contract history, or additional deletion confirmation is required.

## Active Plan Updates

`/update-plan <exact-plan-path>` requires one explicit canonical plan path. It
never infers the target from `.erb/plan-state.json`, and it does not select the
updated plan. Accept only a plan with at least one unchecked TODO or Verification
checkbox. A completed plan remains immutable; additional work requires a new
human-authorized `/create-plan` request.

Re-read and validate the exact plan plus fresh repository evidence immediately
before mutation. Apply the smallest exact-content edit patch that satisfies the
human's instructions, keep the same path and canonical format, then re-read and
validate the whole result against the checklist-entry contract. If the patch no
longer matches fresh content, stop instead of overwriting unexpected changes.

Reconcile checklist evidence conservatively:

- New TODO and Verification entries are unchecked.
- An unchecked entry never becomes checked during an update.
- A checked entry stays checked only when its obligation and the surrounding
  acceptance contract remain materially unchanged and fresh evidence still
  supports it.
- A changed, invalidated, or insufficiently evidenced checked entry resets to
  unchecked.
- When ordering violates the checklist-entry contract, re-sequence the smallest
  affected set. Dependency correctness outranks preserving existing order. Keep
  all TODOs before dedicated Verification steps and keep entries sequentially
  numbered within each checklist.
- Reordering alone does not justify retaining checked state. Apply the same
  evidence rules after every move, and report the old-to-new ordering plus the
  reason for each move.

Do not write `.erb/plan-state.json`, delegate, implement, run implementation
validation, stage, commit, execute TODOs, or update native planned-work TODOs in
this route. Report the applied changes and every retained or reset checked item.
A later explicit `/start-plan <existing-plan-path>` request is required to
execute or resume the updated plan.

## Plan Artifact Commits

After the Plan Orchestrator creates and validates a plan, an explicit current
human commit request may authorize the selected Engineering Lead to stage and
commit only the canonical plan Markdown. This exception does not authorize the
Lead to create, edit, advance, or execute a plan. It excludes
`.erb/plan-state.json`.

The Lead re-reads the exact contained regular non-symlink plan, derives its
repository-relative path from fresh trusted worktree evidence, and stages one
literal path with `git add -- <path>`. Runtime approval is an additional human
check, not proof that a path is safe. Wildcards, question marks, bracket
expressions, braces, pathspec magic, `.` shorthand, traversal, substitution,
shell composition, and redirection remain forbidden.

## Execution And Resume

Validate the selected path, canonical plan format, and the whole checklist-entry
contract before mutation. Resume the first unchecked checkbox. Finish TODOs in
document order before Verification steps.

Check a TODO only after observed implementation or individual-validation
evidence. Check a Verification step only after its own observed evidence. A
blocked, failed, or uncertain step remains unchecked and is still current.
Re-read the plan and fresh worktree evidence before each mutable phase.

If fresh evidence shows that the plan contract needs a material update, leave
the current checkbox unchecked, stop execution, and report the exact mismatch
plus the smallest proposed amendment. The human may then choose
`/update-plan <exact-plan-path>`. Never update the plan during `/start-plan`;
resume only after a later explicit `/start-plan` request.

The Plan Orchestrator may delegate one bounded implementation TODO at a time to
the Implementation Worker. It derives that TODO's full canonical obligation set
from the plan and fresh evidence, then partitions the obligations into three
disjoint and collectively exhaustive sets: active slice, evidenced complete,
and unresolved or deferred. The partition is transient and is re-derived after
a restart; it never enters the plan or state file.

Each new Task receives a self-contained packet. Each invocation or continuation
assigns one bounded active slice with attainable acceptance criteria, owned
scope, focused validation, and stop conditions. Unresolved or deferred work is
context only, not active acceptance criteria or a blocker. Relevant completed
state appears under `Satisfied dependencies / preserved state`, marked out of
scope and not to be repeated. A Worker `COMPLETED` report closes only the active
slice; only the Orchestrator may reconcile the full TODO and advance its
checkbox.

Plan and Task scope authorize the bounded work but never satisfy an `ask`
permission. Before delegation, classify each required operation as allowed,
ask-gated, or denied. Do not delegate a known denied operation. For an ask-gated
or destructive operation, the packet names the exact contained target, expected
runtime gate, and evidence needed to distinguish not-started, terminal, and
uncertain execution.

The Orchestrator uses evidence-first return handling. It closes an
evidenced-complete slice regardless of an incorrect status, retries an incomplete
slice when no genuine blocker exists, and stops on a genuine blocker that
prevents every remaining safe slice action. A false `COMPLETED` is handled like
an unsupported `BLOCKED`, but evidence controls the transition.

Permission-state and replay-safety gates run before no-progress handling. A
policy denial or rejected approval for a command known not to have started stops
the current `/start-plan` invocation immediately and never consumes the
unsupported no-progress allowance. Pending approval retains one waiting child
without polling, continuation, or another Task. Approval alone does not prove
execution. A known terminal result is reconciled against fresh evidence; unknown
or interrupted execution stops without replay.

Strict progress means fresh evidence moves at least one unresolved active-slice
criterion to evidenced complete. The Orchestrator preserves those completed
criteria, forms a strictly smaller residual active slice, and resets the
consecutive no-progress allowance. With no criterion classification change, it
allows one same-session correction for the residual slice. A second consecutive
unsupported no-progress terminal return is an execution-channel failure, not a
plan blocker; the TODO stays unchecked. The finite obligation set bounds progress
resets.

Every resumed correction prompt is independently actionable and delta-focused.
It enumerates each evidence gap, the blocked slice criterion, observed versus
required result, exact correction scope, validation to rerun, unchanged
constraints, and stop condition. It omits stale logs and completed actions while
retaining relevant preserved state. A TODO-status sentence or a phrase such as
`these findings` is never a substitute for the findings themselves. Before
checking the TODO, the Orchestrator re-derives the full obligation partition and
runs TODO-level integration validation without beginning a separately listed
Verification step. The Worker cannot edit plans or `.erb/plan-state.json`,
delegate, stage, or commit.

Before every continuation, the Orchestrator stops for reconciliation rather than
repeating an action whose prior result or replay safety cannot be established
from fresh evidence.

If an interrupted runtime cannot resume the prior Task child, the Orchestrator
re-derives the obligation partition and creates one fresh self-contained Task for
the current unresolved slice. It does not infer completion from the lost session
or replay an action whose prior result or replay safety lacks fresh evidence.

## Security And Validation

Treat state paths and plan content as untrusted. Reject absolute paths, traversal,
symlinks, alternate repositories, non-regular files, invalid UTF-8, and content
larger than 1 MiB. Use edit tools instead of shell redirection for plan and state
writes.

Optional ERB review is independent read-only advice, not approval, readiness,
persistence, or execution authority. Report selected plan, current or completed
state, checkbox evidence, validation, skipped checks, unresolved decisions, and
residual risk.
