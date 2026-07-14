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
| [Planning Coordinator](../opencode/agents/planning-coordinator.md) | Every durable plan write under `docs/implementation-plans/**`, including creation, revision, review records, approval records, lifecycle state, and execution history. | Implement source changes, delegate, or make a missing product or architecture decision. |
| [Implementation Worker](../opencode/agents/implementation-worker.md) | One bounded implementation unit assigned by the Lead, plus focused validation and an evidence report. It is the only implementation subagent. | Edit durable plans, delegate, commit, push, deploy, broaden scope, or perform destructive migrations. |
| Review and research specialists | Bounded, decision-relevant analysis for the Lead or ERB using exact runtime-visible IDs. | Implement changes, simulate the ERB, approve plans, or treat advisory output as final authority. |

The Lead may complete narrow work directly. When it delegates implementation,
it uses only `implementation-worker`; when any durable plan field or history must
change, it uses only `planning-coordinator`. The ERB and its specialists stay on
the review side of that boundary.

### Maintainer-authorized Lead tools

The human maintainer explicitly authorizes the Engineering Lead to use
`pbcopy` and every tool exposed by the configured MCP servers. The Lead's
permission map carries explicit MCP server-prefix rules, and repository
validation protects both those rules and the clipboard exception. Routine
reviews, audits, and refactors must not remove, downgrade, or override this
baseline. Evidence-backed concerns may be reported for a human decision, but
only a new explicit human instruction may change the authorization. Reconcile
the prefix list and validator when the configured MCP server set changes.

## Handoffs

For ordinary work, start with the Engineering Lead. A direct request may proceed
under its Trivial or Bounded process; `/prepare-work <request>` performs
classification without implementation and creates a draft through the
Coordinator only when durable planning is warranted.

The canonical planned-work sequence is documented in
[`implementation-plans/README.md`](implementation-plans/README.md):

1. The Lead prepares evidence and the Coordinator writes the draft.
2. A separate ERB session runs `/review-plan <path>`.
3. The Lead persists that record with `/record-plan-review <path>`. Required
   corrections return through `/revise-plan <path>` and another ERB review.
4. A human invokes `/approve-plan <path>` only after a matching persisted ERB
   `ready` record exists.
5. The Lead runs `/execute-plan <path>` through bounded worker units, then a
   separate ERB session runs `/review-implementation <path>`.

An ERB decision is independent review evidence. It is not implementation
authority, and plan readiness never replaces explicit human approval.

## Command Ownership

All tracked commands use `subtask: false` and route to one of the two primary
agents.

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
- Keep implementation and durable-plan persistence separate. Only the worker
  implements delegated units, and only the Coordinator writes plan artifacts.
- Check each command's primary owner, `subtask: false` setting, required evidence,
  and next handoff. A `ready` plan review still requires persistence and explicit
  human approval.
- Reconcile plan-lifecycle changes across the canonical plan guide and the
  [project template](../opencode/project-template/AGENTS-plan-workflow-snippet.md).
  Update the manifest when tracked definitions change.
- Run `just validate-opencode`, `just validate`, and `just check` as applicable,
  then send material governance changes to a separate ERB session for review.
