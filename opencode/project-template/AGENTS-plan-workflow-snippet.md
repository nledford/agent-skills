## Durable Plan Workflow

Project-local plans use the canonical contract in
[`docs/implementation-plans/README.md`](docs/implementation-plans/README.md).
Prefer direct implementation when scope, safety, and validation are adequate;
complexity may justify a recommendation, never automatic plan creation.

The Lead or ERB may recommend top-level `/consult-plan` for bounded read-only
Plan Orchestrator advice, stating the reason, trade-off, and proposed scope. The
human controls the route. Only an explicit human `/create-plan` request creates
and persists a plan, and it is plan-only. Use `.erb/plans/<slug>.md` for one plan
and `.erb/plans/<subject>/<NN>-<slug>.md` only for separately managed series.

An explicit `/update-plan <exact-plan-path>` request may update one active plan
in place and is plan-only. It requires one canonical path, never infers its
target from `.erb/plan-state.json`, does not change state, and does not execute
TODOs. Completed plans remain immutable. New checklist entries remain unchecked,
and checked entries reset to unchecked when changed, invalidated, or no longer
supported by fresh evidence.

Every TODO and Verification entry has one finite atomic purpose and focused
evidence, follows all prerequisites in document order, discloses known ask-gated
or destructive operations and their contained targets, and has no self- or
future-step dependency, cycle, mutually waiting step, or unbounded progress
loop. Planning-time permission disclosure is not approval; execution reclassifies
the operation against current runtime policy. `/update-plan` may re-sequence the
smallest affected set when dependency correctness requires it.

Execution-only `/start-plan` accepts an existing valid canonical plan path or,
without a path, the selection in `.erb/plan-state.json`. The state file stores
only the repository-relative plan path. Derive active status and current work
from the plan: a plan remains active while a TODO or Verification checkbox is
unchecked, and the first unchecked checkbox is current. A fully checked plan
reports that it has already been implemented and stops.

An explicit valid plan path repairs missing, invalid, or stale state. The latest
explicit selection wins. The pointer is not concurrency control and does not
prevent the user from starting another plan.

Active plan bodies are immutable by default and during execution except for
evidenced checkbox advancement. Only a current explicit `/update-plan` request
authorizes an in-place prose or structure update. Separately, a current explicit
split-or-replace request may create at least two successors and retire one
unambiguous source after the source and all successors are re-read. No registry
or retained contract history is required.

The Plan Orchestrator is the exclusive durable-plan and state writer. The
Engineering Review Board remains separate, optional, and read-only advisory. The
Worker cannot edit plans or `.erb/plan-state.json`, stage, or commit. Each new
Worker Task receives a self-contained packet with numbered acceptance criteria;
the Plan Orchestrator derives the full TODO obligation set, partitions it into
active-slice, evidenced-complete, and unresolved work, and assigns one bounded
active slice at a time. Worker status is evidence: `COMPLETED` closes only the
slice, and `BLOCKED` requires a genuine blocker that prevents every safe slice
action. Plan and Task scope never satisfy an `ask` permission. Known denial or
rejected approval stops without a correction; pending approval retains one
waiting child; approval alone does not prove execution; and unknown execution
stops without replay. Only after those permission-state and replay-safety gates
may the Orchestrator resume the same Task child for one evidence-first correction
when no criterion changes classification. Strict criterion-level progress
creates a smaller residual slice and resets that consecutive no-progress
allowance; a second unsupported no-progress return becomes an execution-channel
failure and leaves the TODO unchecked. Every correction is delta-focused and
independently actionable, preserves relevant completed state without repeating
it, stops when prior result or replay safety is uncertain, and includes exact
gaps, required results, scope, validation, constraints, and stop conditions. The
Orchestrator checks the TODO only after every canonical obligation and TODO-level
integration validation are evidenced.

After the Plan Orchestrator creates and validates a plan, an explicit current
human commit request may authorize the Engineering Lead to stage and commit only
the canonical plan Markdown. This exception grants no plan edit, state, or
execution authority and excludes `.erb/plan-state.json`. Use one freshly derived
literal canonical path per approval-gated `git add --` command; never use
expansion syntax, shell composition, or redirection.

OpenCode agent-definition changes take effect only after a full restart.
