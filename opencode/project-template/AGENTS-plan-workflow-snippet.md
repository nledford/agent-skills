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

Execution-only `/start-plan` accepts an existing valid canonical plan path or,
without a path, the selection in `.erb/plan-state.json`. The state file stores
only the repository-relative plan path. Derive active status and current work
from the plan: a plan remains active while a TODO or Verification checkbox is
unchecked, and the first unchecked checkbox is current. A fully checked plan
reports that it has already been implemented and stops.

An explicit valid plan path repairs missing, invalid, or stale state. The latest
explicit selection wins. The pointer is not concurrency control and does not
prevent the user from starting another plan.

Existing plan bodies are immutable except for evidenced checkbox advancement. A
current explicit split-or-replace request may create at least two successors and
retire one unambiguous source after the source and all successors are re-read.
No registry or retained contract history is required.

The Plan Orchestrator is the exclusive durable-plan and state writer. The
Engineering Review Board remains separate, optional, and read-only advisory. The
Worker cannot edit plans or `.erb/plan-state.json`, stage, or commit.

After the Plan Orchestrator creates and validates a plan, an explicit current
human commit request may authorize the Engineering Lead to stage and commit only
the canonical plan Markdown. This exception grants no plan edit, state, or
execution authority and excludes `.erb/plan-state.json`. Use one freshly derived
literal canonical path per approval-gated `git add --` command; never use
expansion syntax, shell composition, or redirection.

OpenCode agent-definition changes take effect only after a full restart.
