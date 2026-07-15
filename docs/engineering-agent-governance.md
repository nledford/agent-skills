# Engineering Agent Governance

Use this guide to choose the correct runtime role, command, and handoff when
maintaining the repository's OpenCode definitions. The agent and command files
remain authoritative; this page is a source map and does not grant permissions
or extend a Task allowlist. [`opencode/manifest.json`](../opencode/manifest.json)
lists the tracked definitions.

## Keep Runtime Concepts Separate

| Concept | Purpose | Authority |
| --- | --- | --- |
| Skill | Reusable procedure loaded by an agent for a task. | A skill name is not a runtime agent ID and grants no edit, delegation, review, or plan/state authority. |
| Agent | Runtime role defined under [`opencode/agents/`](../opencode/agents/). | Its `mode`, permission map, exact registered ID, and the runtime Task allowlist control what it can do. Never derive an ID from a skill name or job title. |
| Command | Top-level entry point defined under [`opencode/commands/`](../opencode/commands/). | Its `agent` field selects a primary agent. A command routes work but does not add authority to that agent. |

## Roles and Limits

| Role | Owns | Must not do |
| --- | --- | --- |
| [Engineering Lead](../opencode/agents/engineering-lead.md) | Request intake, process selection, direct or bounded unplanned delivery, integration, validation, and independent-review handoff. | Invoke the ERB as a Task child, claim a Board decision without its output, or write or execute a durable plan or trusted planned-work state. |
| [Engineering Review Board](../opencode/agents/engineering-review-board.md) | Optional independent read-only advice, specialist selection, evidence synthesis, and severity assessment. Invoke it as a separate primary agent. | Edit the repository, implement a fix, change plans or state, or control plan creation, updates, execution, or persistence. |
| [Plan Orchestrator](../opencode/agents/plan-orchestrator.md) | Top-level read-only consultation, safe closed lean-plan creation, trusted planned-work state, planned execution, integration, validation, and native planned-work TODOs. | Act as a Task child, mutate a created plan beyond evidenced existing checkboxes, delegate to anything other than the Worker, or claim ERB advisory evidence controls planned work. |
| [Implementation Worker](../opencode/agents/implementation-worker.md) | One bounded implementation unit assigned by the Lead or Plan Orchestrator, plus focused validation and an evidence report. It is the only implementation subagent. | Edit durable plans; read or mutate `.start-work/**`; invoke the trusted planned-work helper; delegate; stage; commit; push; deploy; broaden scope; or perform destructive migrations. |
| Review and research specialists | Bounded, decision-relevant analysis for the Lead or ERB using exact runtime-visible IDs. | Implement changes, simulate the ERB, approve plans, or treat advisory output as final authority. |

The Lead may directly implement complex work when scope, safety, and validation
are adequate, and retains its MCP, clipboard, Git, and transient unplanned-TODO
authority. Complexity may justify a planning recommendation but never creates a
plan or invokes `/start-work` automatically. The Lead or ERB may recommend
top-level `/consult-plan` for separate read-only Plan Orchestrator advice, with a
reason, trade-off, and proposed scope. It is not Task delegation and cannot
create, mutate, authorize, or execute work. The human's decision to require,
decline, or override planning advice controls the route. When the Lead delegates implementation, it uses only
`implementation-worker`. Durable plan or `.start-work` mutations route through a
top-level Plan Orchestrator command, never a Task child. The ERB and its
specialists stay on the advisory side of that boundary.

### Maintainer-authorized Lead tools

The human maintainer explicitly authorizes the Engineering Lead to use
`pbcopy`, `todowrite`, every tool exposed by the configured MCP servers, and the
canonical predominantly non-destructive Git command set. The Git set includes
inspection, index staging, ordinary staged-index commits, and ordinary fetches;
ordered exceptions keep history rewriting, hook bypass, worktree/ref mutation,
unsafe fetch variants, shell composition, and remote mutation gated or denied.
Tool permission does not replace the user authorization required by the Lead's
commit and external-side-effect policies.

The Lead's permission map carries explicit rules for these tools, and repository
validation protects their actions and ordering. Routine reviews, audits, and
refactors must not remove, downgrade, broaden, or override this baseline.
Evidence-backed concerns may be reported for a human decision, but only a new
explicit human instruction may change the authorization. Reconcile the MCP
prefix list and validator when the configured server set changes.

### Maintainer-authorized Worker MCP tools

The human maintainer explicitly authorizes the Implementation Worker to use
every tool exposed by the configured MCP servers. Its permission map names the
same current server prefixes as the Lead, and repository validation protects
the complete explicit set. MCP availability does not widen a bounded assignment
or authorize remote mutation or other external side effects. Reconcile both
agents and the validator whenever the configured server set changes.

### Plan Orchestrator commit boundary

While it retains planned-work ownership, the Plan Orchestrator has a separately
validated Git surface for exact inspection, approval-gated `git add --` paths,
and bare staged-index commits. It may use that surface only for an explicit
current human request. With that request it may commit an appropriately complete,
validated, coherent unit during implementation or after implementation completes.
Before committing, it
freshly reconciles the pointer, plan, worktree status, unstaged and staged diffs,
recent history, and effective hook/signing policy; it rechecks the staged diff
and resulting commit/worktree before advancing a checkbox. It derives paths from
fresh trusted evidence, does not interpolate human or plan text into Git, and
keeps the lock and staged state on failure or uncertainty.

For every approval-gated `git add --`, it separately enumerates each
repository-relative dirty path from fresh `git status`/worktree evidence and
quotes it as one literal shell word. Approval is an additional human check, not
proof the path is safe. It must reject `*`, `?`, bracket expressions, braces,
pathspec magic, `.` shorthand, traversal, substitution, and every other
expansion syntax; stop if a dirty path cannot be represented literally under the
command policy. The runtime matcher cannot statically distinguish literal `*` or
`?`, so this operational requirement is mandatory rather than inferred from an
approval prompt.

The canonical active plan path may be staged only after independent validation
of that exact contained plan. This exception does not permit Bash plan mutation
or redirection. Amend, hook/signing bypass, implicit staging, fetch, push, and
all branch, ref, history, worktree, and remote mutation remain forbidden. The
Worker remains forbidden to stage or commit. Load `git-commit`; additionally load
`security-review` and `security-review-evidence` for signing trust, hooks,
secrets, or other Git trust boundaries. These are configuration-time definitions:
quit and fully restart OpenCode before any changed authority exists; the running
session remains unchanged.

## Handoffs

For ordinary work, start with the Engineering Lead. The canonical sequence is
documented in [`implementation-plans/README.md`](implementation-plans/README.md):

1. Deliver directly when scope, safety, and validation are adequate. Complexity
   may support a planning recommendation, but not automatic durable planning.
2. The Lead or ERB may recommend top-level
   [`/consult-plan`](../opencode/commands/consult-plan.md); it remains advisory,
   non-mutating, and cannot persist, authorize, or begin work.
3. On explicit human authorization, top-level
   [`/create-plan`](../opencode/commands/create-plan.md) acquires trusted state
   and creates and persists a closed lean plan only.
4. A separate ERB session may provide optional independent advisory review.
5. A separate human choice of top-level
   [`/start-work <existing-plan-path>`](../opencode/commands/start-work.md), or a
   validated no-argument resume pointer with explicit human confirmation,
   executes existing planned work. The Plan Orchestrator then executes bounded
   Worker units and records only observed plan checkbox and state evidence.

Existing plan content cannot be updated after creation except for evidenced
existing checkbox advancement during execution. Material discoveries require a
new human decision and, when authorized, a new `/create-plan` request. Legacy
conversion is plan-only and requires a separate later
`/start-work <destination>` choice to execute.

ERB output is advisory evidence, not implementation, plan, state, or execution
authority.

## Command Ownership

All tracked commands use `subtask: false`. The command definitions and manifest
are authoritative for primary ownership.

| Command | Primary agent | Job |
| --- | --- | --- |
| [`/consult-plan`](../opencode/commands/consult-plan.md) | Plan Orchestrator | Provide top-level read-only planning advice without acquiring state, creating a plan, or authorizing work. |
| [`/create-plan`](../opencode/commands/create-plan.md) | Plan Orchestrator | On explicit human authorization, create and persist a closed lean plan only; never execute TODOs. |
| [`/start-work`](../opencode/commands/start-work.md) | Plan Orchestrator | Execute or resume only an existing valid canonical lean plan; reject free-form creation and plan-update requests. |
| [`/convert-tapestry-plan`](../opencode/commands/convert-tapestry-plan.md) | Plan Orchestrator | Revalidate a legacy Tapestry source and create the smallest safe lean destination layout; always plan-only, with execution requiring separate `/start-work <destination>`. |
| [`/review-plan`](../opencode/commands/review-plan.md) | Engineering Review Board | Review canonical plans without editing them. |
| [`/review-implementation`](../opencode/commands/review-implementation.md) | Engineering Review Board | Review completed implementation against the relevant plan and evidence without editing either. |
| [`/investigate-regression`](../opencode/commands/investigate-regression.md) | Engineering Review Board | Investigate a suspected regression without modifying the repository. |
| [`/audit-technical-debt`](../opencode/commands/audit-technical-debt.md) | Engineering Review Board | Run a read-only general or focused technical-debt audit. |

## Audit or Refactor Governance

Before changing role or command guidance:

- Start from the manifest, definition frontmatter, permission maps, and current
  runtime-visible Task IDs. Repository prose cannot widen those controls.
- Preserve one-level delegation. Critics and researchers do not delegate; the
  ERB never becomes a child of the Lead.
- Keep delegated Task prompts scannable: use Markdown sections separated by
  blank lines and bullets for multi-item scope, constraints, questions, and
  evidence. Do not compress a delegation packet into one dense paragraph.
- Keep implementation and durable-plan persistence separate. The Worker owns one
  bounded implementation unit; the top-level Plan Orchestrator owns plan and
  trusted state mutations through the linked helper, never copied into a target
  repository or exposed as a custom tool.
- Check each command's primary owner, `subtask: false` setting, required evidence,
  and next handoff. ERB output remains optional, read-only advice.
- Reconcile lean-plan routing changes across the canonical plan guide and the
  [project template](../opencode/project-template/AGENTS-plan-workflow-snippet.md).
  Update the manifest when tracked definitions change.
- Run `just validate-opencode`, `just validate`, and `just check` as applicable,
  then consider a separate ERB session for material governance advice.
