# Engineering Agent Governance

Use this guide to choose the correct runtime role, command, and handoff when
maintaining the repository's OpenCode definitions. The agent and command files
remain authoritative; this page is a source map and does not grant permissions
or extend a Task allowlist. [`opencode/manifest.json`](../opencode/manifest.json)
lists the tracked definitions.

## Keep Runtime Concepts Separate

| Concept | Purpose | Authority |
| --- | --- | --- |
| Skill | Reusable procedure loaded by an agent for a task. | A skill name is not a runtime agent ID and grants no edit, delegation, review, or approval authority. |
| Agent | Runtime role defined under [`opencode/agents/`](../opencode/agents/). | Its `mode`, permission map, exact registered ID, and the runtime Task allowlist control what it can do. Never derive an ID from a skill name or job title. |
| Command | Top-level entry point defined under [`opencode/commands/`](../opencode/commands/). | Its `agent` field selects a primary agent. A command routes work but does not add authority to that agent. |

## Roles and Limits

| Role | Owns | Must not do |
| --- | --- | --- |
| [Engineering Lead](../opencode/agents/engineering-lead.md) | Request intake, process selection, direct or bounded delivery, integration, validation, and independent-review handoff. | Invoke the ERB as a Task child, claim a Board decision without its output, or write a durable plan directly. |
| [Engineering Review Board](../opencode/agents/engineering-review-board.md) | Independent read-only review, specialist selection, evidence synthesis, severity, and stage decisions. Invoke it as a separate primary agent. | Edit the repository, implement a fix, change plan metadata, or turn `ready` review evidence into human approval. |
| [Plan Orchestrator](../opencode/agents/plan-orchestrator.md) | Safe lean-plan creation and updates, trusted planned-work state, planned execution, integration, validation, and native planned-work TODOs. | Act as a Task child, delegate to anything other than the Worker, or claim ERB advisory evidence is approval. |
| [Implementation Worker](../opencode/agents/implementation-worker.md) | One bounded implementation unit assigned by the Lead or Plan Orchestrator, plus focused validation and an evidence report. It is the only implementation subagent. | Edit durable plans or `.start-work/**`, delegate, commit, push, deploy, broaden scope, or perform destructive migrations. |
| Review and research specialists | Bounded, decision-relevant analysis for the Lead or ERB using exact runtime-visible IDs. | Implement changes, simulate the ERB, approve plans, or treat advisory output as final authority. |

The Lead may complete narrow unplanned work directly. When it delegates
implementation, it uses only `implementation-worker`; durable plan or
`.start-work` work routes to the top-level Plan Orchestrator rather than a Task
child. The ERB and its specialists stay on the review side of that boundary.

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

## Handoffs

For ordinary work, start with the Engineering Lead. A direct request may proceed
under its Trivial or Bounded process. Durable planning, trusted state, planned
execution, and planned-work TODOs route to the top-level Plan Orchestrator.

The canonical planned-work sequence is documented in
[`implementation-plans/README.md`](implementation-plans/README.md):

1. The Plan Orchestrator acquires trusted provisional state and writes the draft.
2. A separate ERB session may provide independent advisory review.
3. The Plan Orchestrator executes bounded worker units and records only observed
   plan and state evidence.

An ERB decision is independent review evidence. It is not implementation
authority or approval.

## Command Ownership

All tracked commands use `subtask: false`. The temporary command inventory and
definitions remain unchanged until the command migration; do not infer current
Plan Orchestrator authority from a legacy command route.

| Command | Primary agent | Job |
| --- | --- | --- |
| [`/prepare-work`](../opencode/commands/prepare-work.md) | Engineering Lead | Classify a request and create a draft through the Coordinator when needed. |
| [`/convert-tapestry-plan`](../opencode/commands/convert-tapestry-plan.md) | Engineering Lead | Revalidate and convert a legacy source plan through the Coordinator. |
| [`/normalize-plan`](../opencode/commands/normalize-plan.md) | Engineering Lead | Move legacy plan structure into the canonical layout through a verified two-phase process. |
| [`/review-plan`](../opencode/commands/review-plan.md) | Engineering Review Board | Review canonical plans without editing them. |
| [`/record-plan-review`](../opencode/commands/record-plan-review.md) | Engineering Lead | Verify and persist an ERB plan record through the Coordinator. |
| [`/revise-plan`](../opencode/commands/revise-plan.md) | Engineering Lead | Apply material plan corrections through the Coordinator and return to review. |
| [`/approve-plan`](../opencode/commands/approve-plan.md) | Engineering Lead | Record explicit human approval through the Coordinator after matching ERB evidence. |
| [`/execute-plan`](../opencode/commands/execute-plan.md) | Engineering Lead | Execute an approved plan through bounded workers and persist lifecycle history through the Coordinator. |
| [`/review-implementation`](../opencode/commands/review-implementation.md) | Engineering Review Board | Review completed planned work against its approved plan and evidence. |
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
  and next handoff. A `ready` plan review still requires persistence and explicit
  human approval.
- Reconcile plan-lifecycle changes across the canonical plan guide and the
  [project template](../opencode/project-template/AGENTS-plan-workflow-snippet.md).
  Update the manifest when tracked definitions change.
- Run `just validate-opencode`, `just validate`, and `just check` as applicable,
  then send material governance changes to a separate ERB session for review.
