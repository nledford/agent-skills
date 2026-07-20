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

Validate the request against repository evidence, choose the smallest layout,
write the plan with all boxes unchecked, and re-read it. Then write the selected
canonical path to `.erb/plan-state.json` and re-read both files. Stop without
implementation.

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
validate the whole result. If the patch no longer matches fresh content, stop
instead of overwriting unexpected changes.

Reconcile checklist evidence conservatively:

- New TODO and Verification entries are unchecked.
- An unchecked entry never becomes checked during an update.
- A checked entry stays checked only when its obligation and the surrounding
  acceptance contract remain materially unchanged and fresh evidence still
  supports it.
- A changed, invalidated, or insufficiently evidenced checked entry resets to
  unchecked.
- Preserve numbering and order where practical; after structural changes, keep
  entries sequentially numbered within each checklist.

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

Validate the selected path and canonical plan format before mutation. Resume the
first unchecked checkbox. Finish TODOs in document order before Verification
steps.

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
the Implementation Worker. Each new Task receives a self-contained packet with
the current plan context, owned scope, numbered acceptance criteria, validation,
and stop conditions. One at a time limits active concurrency, not attempts. The
Orchestrator maps every criterion to fresh source, diff, and validation evidence
and resumes the same Task child for safe in-scope corrections before checking
the TODO. The Worker cannot edit plans or `.erb/plan-state.json`, delegate,
stage, or commit.

Every resumed correction prompt is independently actionable. It enumerates each
evidence gap, the blocked acceptance criterion, observed versus required result,
exact correction scope, validation to rerun, unchanged constraints, and stop
condition. A TODO-status sentence or a phrase such as `these findings` is never
a substitute for the findings themselves. The Worker must block rather than
guess when a correction packet omits those details.

## Security And Validation

Treat state paths and plan content as untrusted. Reject absolute paths, traversal,
symlinks, alternate repositories, non-regular files, invalid UTF-8, and content
larger than 1 MiB. Use edit tools instead of shell redirection for plan and state
writes.

Optional ERB review is independent read-only advice, not approval, readiness,
persistence, or execution authority. Report selected plan, current or completed
state, checkbox evidence, validation, skipped checks, unresolved decisions, and
residual risk.
