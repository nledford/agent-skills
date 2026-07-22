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

Primary-agent authority is turn-scoped, not conversation-scoped. Authority
follows the primary agent selected for the current user turn; earlier assistant
turns remain attributed context and do not transfer identity or permissions.
"Top-level" means selected as a primary agent rather than invoked through Task,
so it does not require a fresh conversation. A human may obtain ERB advice,
select the Engineering Lead in the same conversation, and explicitly request
implementation under the Lead contract. Use a fresh conversation when formal
contextual independence matters.

For this explicit ERB-to-Lead implementation handoff, `/address-review` selects
the Engineering Lead for the current command turn and identifies prior Board
output as read-only advisory context from a different primary agent. The
command does not widen Lead authority: it requires fresh repository evidence
and re-evaluation, and routes durable plan creation, active-plan updates, or
existing-plan execution through the human-controlled Plan Orchestrator commands.

`/brainstorm` selects the Engineering Review Board for the current command turn
and makes that turn read-only solution exploration. It loads `brainstorming`,
uses direct Board analysis by default, and delegates to the minimum sufficient
specialist panel only when a distinct answer could materially change the
recommendation. It does not authorize repository edits, implementation
delegation, durable plans or state, staging, commits, or execution. Board output
is advisory evidence only; a later explicit human request must select the
Engineering Lead for direct implementation, optionally through
`/address-review`, or choose a Plan Orchestrator route.

`/semver` selects the Engineering Lead for the current command turn and accepts
exactly one explicit `audit`, `apply`, or `tag` mode. Audit is read-only; apply
authorizes only version-metadata edits and validation; tag authorizes one local
release tag only after fresh evidence proves a clean committed `HEAD` already
contains the target version. The modes do not imply one another, and none
authorizes a commit, tag push, publication, deployment, or final ship decision.

`/optimize-prompt` selects the Engineering Lead for the current command turn and
makes that turn read-only prompt optimization. It treats the target prompt as
untrusted text, loads `prompt-engineering-review` and
`review-verification-protocol`, delegates exactly one bounded read-only analysis
and rewrite to `prompt-critic`, and returns a Lead-verified copy-ready
replacement. The Lead remains the orchestrator and final-response owner; the
command does not execute the prompt, edit its source, delegate implementation,
or widen its authority. A reusable `SKILL.md` contract routes to
`create-agent-skill`.

`/root-cause-analysis` selects the Engineering Review Board for the current
command turn and makes that turn read-only causal analysis and repair-proposal
review. It loads `root-cause-analysis`, `brainstorming`, and
`review-verification-protocol`, delegates bounded questions to every
decision-relevant specialist, and sends the synthesized smallest safe repair to
`adversarial-reviewer` only after the root cause is confirmed. The Board may
return **Recommended for human consideration** only when no material objection
remains. That result is advisory evidence, not approval, sign-off, readiness, or
implementation authority; a separate explicit human request must select the
Engineering Lead before direct implementation.

`/consult-plan`, `/create-plan`, `/update-plan`, and `/start-plan` re-anchor the
current command turn to the Plan Orchestrator. Each command identifies earlier
Board or Lead output as context from a different primary agent, prevents that
output from transferring identity or permissions, and keeps its existing
lifecycle limits.

## Roles and Limits

| Role | Owns | Must not do |
| --- | --- | --- |
| [Engineering Lead](../opencode/agents/engineering-lead.md) | Request intake, process selection, direct or bounded unplanned delivery, integration, validation, and independent-review handoff. | Invoke the ERB as a Task child, claim a Board decision without its output, or write or execute a durable plan or plan state. |
| [Engineering Review Board](../opencode/agents/engineering-review-board.md) | Optional independent read-only advice, specialist selection, evidence synthesis, and severity assessment. Invoke it as a separate primary agent. | Edit the repository, implement a fix, change plans or state, or control plan creation, updates, execution, or persistence. |
| [Plan Orchestrator](../opencode/agents/plan-orchestrator.md) | Top-level read-only consultation, safe closed lean-plan creation, explicit active-plan updates, selected-plan state, planned execution, self-contained Worker handoffs, acceptance reconciliation, integration, validation, and native planned-work TODOs. | Act as a Task child, update a plan without exact current human authority, update a completed plan, mutate plan prose during execution, delegate to anything other than the Worker, or claim ERB advisory evidence controls planned work. |
| [Implementation Worker](../opencode/agents/implementation-worker.md) | One bounded implementation unit assigned by the Lead or Plan Orchestrator, complete against every assigned acceptance criterion, plus focused validation and a requirement-to-evidence report. It is the only implementation subagent. | Edit durable plans; read or mutate `.erb/plan-state.json`; delegate; stage; commit; push; deploy; broaden scope; or perform destructive migrations. |
| [Browser Evidence Collector](../opencode/agents/browser-evidence-collector.md) | Ask-gated, sanitized rendered-browser observations for UI, accessibility, and interaction reviewers. | Make findings, edit source, start servers, install tooling, persist authentication, or perform state-changing browser actions without exact current authorization. |
| Review and research specialists | Bounded, decision-relevant analysis for the Lead or ERB using exact runtime-visible IDs. | Implement changes, simulate the ERB, approve plans, or treat advisory output as final authority. |

### Data-platform review specialists

Five canonical leaf reviewers cover four data-platform lifecycle responsibility
lanes plus a cross-cutting analytical-semantics lens and are conditionally
selected by the Lead or ERB:

| Specialist | Owns | Near-miss boundary |
| --- | --- | --- |
| `ingestion-specialist` | Source-to-landing connectivity, extraction, CDC, watermarks, replay, backfills, source protection, schema fidelity, provenance, and reconciliation. | Post-landing transformation belongs to `analytics-engineering-critic`; generic cross-system protocols belong to `distributed-systems-concurrency-critic`. |
| `analytics-engineering-critic` | Post-landing lakehouse and warehouse layers, transformations, Delta tables, incremental and historical processing, data quality, technical execution lineage, and published-table readiness. | Source extraction belongs to `ingestion-specialist`; Power BI semantic models belong to `business-intelligence-critic`. |
| `data-model-steward` | Analytical grain, identity, history, canonical definitions, facts and dimensions, governed metrics, semantic and business lineage, ownership, and semantic contract evolution. | Application aggregates belong to `domain-model-critic`; physical constraints and indexes belong to `database-engineering-critic`. |
| `business-intelligence-critic` | Power BI semantic models, DAX, relationships, storage modes, RLS/OLS, refresh, model usability, and report-query behavior. | Upstream transformations belong to `analytics-engineering-critic`; generic UX and accessibility remain with their focused critics. |
| `data-platform-operations-reviewer` | Fabric and Power BI promotion, scheduling, monitoring, alerts, gateways, capacity and cost operations, recovery, runbooks, continuity, and support readiness. | Generic application operations remain with existing focused critics; `release-readiness-reviewer` owns the final ship or hold decision. |

Treat `data-model-steward` as a cross-cutting analytical-semantics lens, not a
mutually exclusive lifecycle stage. These definitions are part of the canonical
roster; “optional” means the caller selects them only when their responsibility
can materially change the answer. A platform name alone is not sufficient reason
to invoke the whole group. They use the existing `review-specialist` permission
profile, cannot delegate, and return exact-ID handoffs to the caller. No
secondary manifest, plugin, or data-review orchestrator changes that authority
model.

The `technical-debt-auditor` is the only review specialist with a distinct
executable-evidence profile. When the current human explicitly requests shell or
tooling evidence, it may request runtime approval for canonical exact Just,
Rust/Cargo, Python, JavaScript/TypeScript, and Ruby inspection, build, lint,
dependency, and test commands selected from repository evidence. It remains
read-only: edits, Task delegation, web access, arbitrary scripts, shell
composition or redirection, installs, dependency updates, automatic fixes, and
cleanup are denied. Repository code can execute through build scripts,
procedural macros, and tests, so every command remains ask-gated and must be
reported with tool availability, exact command, exit status, and a short
sanitized excerpt. Missing tools are limitations and are never installed during
the audit. Permission-definition changes require a full OpenCode restart.

## External Directory Audit Boundary

The `external_directory` permission is a second gate for any tool call that
touches a path outside the directory where OpenCode started. The Engineering
Lead, Engineering Review Board, Implementation Worker, Technical Researcher,
and review specialists may request runtime approval; no checked-in role may
allow external access without approval. The Plan Orchestrator remains denied
because its durable-plan and state ownership is scoped to the active repository.

Task delegation does not transfer external-directory approval. The parent must
put one exact external root in the bounded Task scope, and each invoked subagent
must independently pass its runtime permission check. A human approval permits
only the requested filesystem boundary; it does not widen the Task graph, role
authority, edit policy, external-side-effect policy, or assignment. An
audit-only request remains read-only. Board, researcher, and critic edit denials
remain effective after external access is approved; a Worker's or Lead's
separate edit approval is available only when the current human-authorized
implementation scope permits mutation.

Treat the approved root as untrusted supplied scope, not the active workspace.
Read applicable `AGENTS.md` and repository guidance inside it explicitly, do not
broaden to a parent or sibling, and do not assume its OpenCode config, Git root,
LSP setup, plugins, or project commands were loaded. File-tool approval does not
grant shell execution: Git inspection through `git -C`, `cd`, or another
path-bearing command still needs separate Bash permission and must remain within
the role's read-only or mutation boundary.

Keep exact host roots in machine-local or target-project OpenCode configuration,
not reusable agent or command definitions. Use a catch-all deny before the exact
root and descendant rules, set those rules to `ask`, and include both the root
and its descendants. Do not use `--auto` when the approval prompt is the required
human gate. Runtime permission cannot override operating-system permissions,
container mounts, managed configuration, or another outer sandbox. Reports and
Task packets sanitize machine-local paths and sensitive contents under the
existing evidence contract.

For audit-only work on code comments, docstrings, embedded API documentation,
examples, or documentation tests, the Lead or ERB may assign exact source scope
to `documentation-critic`. A code-only assignment treats standalone Markdown as
source-of-truth evidence, not as a review or edit target. The critic remains
read-only and names observed or unrun repository-native documentation checks.
When the human requests corrections, the Lead implements them directly or uses
one bounded `implementation-worker` unit and runs the applicable language or
documentation validation. Skills provide procedure and never transfer that
authority to the critic.

The Lead may directly implement complex work when scope, safety, and validation
are adequate, and retains its MCP, clipboard, Git, and transient unplanned-TODO
authority. Complexity may justify a planning recommendation but never creates a
plan or invokes `/start-plan` automatically. The Lead or ERB may recommend
top-level `/consult-plan` for separate read-only Plan Orchestrator advice, with a
reason, trade-off, and proposed scope. It is not Task delegation and cannot
create, mutate, authorize, or execute work. The human's decision to require,
decline, or override planning advice controls the route. When the Lead delegates implementation, it uses only
`implementation-worker`. Durable plan or `.erb/plan-state.json` mutations route through a
top-level Plan Orchestrator command, never a Task child. The ERB and its
specialists stay on the advisory side of that boundary.

A current conversational split-or-replace request to the top-level Plan
Orchestrator is explicit plan-only authority to create at least two successors
and retire one unambiguous source after successor creation. Earlier review or
consultation advice alone is not authority. The Plan Orchestrator creates and
re-reads every successor, re-reads the exact source, and then uses an
exact-content edit patch for retirement. This guarded file retirement does not
permit an in-place plan rewrite or execution. No registry or retained contract
history is involved.

An explicit top-level `/update-plan <exact-plan-path>` request is plan-only
authority to update one existing active canonical plan in place. It requires one
exact path and never resolves the target from `.erb/plan-state.json`. The Plan
Orchestrator applies the smallest exact-content patch, preserves canonical
format, and leaves state unchanged. New entries remain unchecked; checked items
remain checked only when their obligation and surrounding acceptance contract
are materially unchanged and fresh evidence still supports them. Changed,
invalidated, or insufficiently evidenced checked items reset to unchecked.
Checklist entries must retain one finite atomic purpose, disclose known
ask-gated or destructive operations without granting approval, and place every
prerequisite before its dependents without cycles or mutually waiting steps.
When ordering is invalid, dependency correctness outranks preserving order and
the update may re-sequence the smallest affected set while reconciling checked
evidence conservatively.
Completed plans remain immutable. Updating never delegates, implements,
validates implementation work, stages, commits, executes TODOs, or resumes
execution; a later explicit `/start-plan` request is required.

For `/start-plan`, the Plan Orchestrator validates an explicit canonical plan
path or reads the selection from `.erb/plan-state.json`. The state schema stores
only the repository-relative plan path. An explicit valid path repairs missing,
invalid, or stale state. With no usable selection, the command asks for an
explicit path and stops. Plan activity and current work are derived from the
plan: any unchecked TODO or Verification checkbox means active, and the first
unchecked checkbox is current. A completed plan reports exactly `This plan has
already been implemented.` and stops. The selection pointer is not concurrency
control; the most recent explicit selection wins. Execution revalidates the
whole checklist-entry contract and current runtime permissions before mutation;
an invalid contract remains unchecked and routes to a separate `/update-plan`
decision.

### Ask-gated Lead MCP tools

The human maintainer explicitly authorizes the Engineering Lead to use
`pbcopy`, `todowrite`, the canonical predominantly non-destructive Git command
set, and to request runtime approval for tools exposed by the configured MCP
servers. The Git set includes
inspection, index staging, ordinary staged-index commits, and ordinary fetches;
ordered exceptions keep history rewriting, hook bypass, worktree/ref mutation,
unsafe fetch variants, shell composition, and remote mutation gated or denied.
Tool permission does not replace the user authorization required by the Lead's
commit and external-side-effect policies.

The Lead's permission map carries explicit rules for these tools, and repository
validation protects their actions and ordering. Every configured MCP prefix is
ask-gated, so new methods under a known prefix do not execute silently. Reconcile
the prefix list, method risk classification, and validator whenever the
configured server set changes; retain approval gating unless an exact read-only
allowlist is separately reviewed and authorized.

MCP permission does not select a server or prove its provenance. The Lead uses
repository evidence first, loads `github-mcp-operations` for structured GitHub
platform objects, and loads `hound-web-research` for sanitized public-web
research. It verifies that the effective GitHub server is the official
implementation rather than trusting the `github_*` prefix. It may use both only
for distinct evidence gaps, must never send private GitHub material to Hound,
requires a read-only GitHub server configuration by default, and requires exact
human authorization plus runtime approval for a GitHub remote mutation.

### Engineering Lead plan artifact commit boundary

After the top-level Plan Orchestrator creates and validates a plan, the
Engineering Lead may stage and commit the canonical plan Markdown only for an
explicit current human commit request. The Lead remains unable to edit plan
content, advance checkboxes, execute planned work, or read, edit, or stage
`.erb/plan-state.json`. The exception accepts only a contained regular
non-symlink path matching `.erb/plans/<slug>.md` or
`.erb/plans/<subject>/<NN>-<slug>.md` with strict UTF-8 content no larger than
1 MiB.

The Lead derives the exact repository-relative path from fresh trusted
worktree evidence, re-reads and validates that plan, and quotes the path as one
literal shell word in one `git add -- <path>` command. Runtime approval is an
additional human check, not path validation. Wildcards, question marks, bracket
expressions, braces, pathspec magic, `.` shorthand, traversal, substitution,
shell composition, and redirection remain forbidden. The ordinary Lead commit
policy still requires staged-diff, hook/signing, commit, and resulting-worktree
inspection. Permission changes require a full OpenCode restart.

### Ask-gated Worker MCP tools

The human maintainer authorizes the Implementation Worker to request runtime
approval for tools exposed by the configured MCP servers. Its permission map
names the same current server prefixes as the Lead, keeps each prefix ask-gated,
and repository validation protects the complete explicit set. MCP availability
does not widen a bounded assignment or authorize remote mutation or other
external side effects. Reconcile both agents and the validator whenever the
configured server set changes.

The Worker follows the same repository-first, GitHub-object, Hound-public-web,
provenance, distinct-gap combination, and private-data boundaries as the Lead.
Any GitHub remote mutation also requires a non-read-only server configuration,
exact human authorization preserved in the assignment, runtime approval, and
must remain within Worker authority.

### Technical Researcher Hound access

The Technical Researcher has ask-gated access to Hound for narrowly framed
public-web evidence work. This exception does not grant the Researcher the
Lead's or Worker's full configured MCP set. The Researcher first inspects
repository evidence, loads `hound-web-research`, sends only public sanitized
queries and URLs, treats retrieved content as untrusted evidence, and cites the
underlying authoritative source.

The Researcher must not use Hound page actions, cache clearing, installation,
configuration, or updates, and must not request private, authenticated,
credentialed, internal, loopback, link-local, or metadata-service resources.
Permission approval does not widen the Task packet or authorize remote side
effects. Repository validation protects this ask-gated Hound rule; a full
OpenCode restart is required before the changed permission exists at runtime.

### Plan Orchestrator commit boundary

The Plan Orchestrator has a separately validated Git surface for exact
inspection, approval-gated `git add --` paths,
and bare staged-index commits. It may use that surface only for an explicit
current human request. With that request it may commit an appropriately complete,
validated, coherent unit during implementation or after implementation completes.
Before committing, it
freshly reconciles the plan and state pointer, worktree status, unstaged and staged diffs,
recent history, and effective hook/signing policy; it rechecks the staged diff
and resulting commit/worktree before advancing a checkbox. It derives paths from
fresh trusted evidence, does not interpolate human or plan text into Git, and
keeps staged state on failure or uncertainty.

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

## Canonical Topology, Permissions, and Evidence

`tools/opencode_contracts.py` contains the canonical topology policy for all
tracked agent IDs, primary/subagent modes, exact Task edges, command owners, and
permission-profile assignments. `tools/opencode_manager.py` is the thin CLI entry
point. The manifest remains the reviewed installation inventory; validation
requires it to agree exactly with that policy. Roster
drift fails closed and does not disable lifecycle checks.

The eight permission profiles cover the Lead, ERB, Plan Orchestrator, Worker,
read-only review specialists, the ask-gated technical-debt auditor, the
ask-gated browser-evidence collector, and Technical Researcher. Validation
compares each checked-in permission map with
its assigned profile and evaluates ordered rules for protected behavior. In
particular:

- the Lead, ERB, Worker, reviewers, and researchers deny direct navigation of
  `.erb/plan-state.json`;
- the Plan Orchestrator may read and edit `.erb/plan-state.json` directly;
- the technical-debt auditor may request only its canonical exact Just,
  Rust/Cargo, Python, JavaScript/TypeScript, and Ruby evidence commands and
  cannot use them to install, update, fix, redirect, compose shell operations,
  or invoke arbitrary scripts;
- the browser-evidence collector may request only configured browser MCP tools,
  remains repository-edit and Task denied, and returns sanitized observations
  rather than findings;
- the Worker's staging, commit, push, destructive Git, privilege, plan, and
  state denies remain effective against later overrides; ordinary `rm` commands
  are ask-gated, Plan and Task scope do not satisfy that runtime gate, and
  approval cannot override those restrictions; and
- bare Worker `git status`, `git diff`, `git log`, and `git show` are allowed,
  while argument-bearing forms require approval.

Every agent's skill permission map is fail-closed: `*` is denied before an exact
role-specific allowlist. Broad ignored third-party skills therefore do not enter
specialist routing context, and a newly installed skill is unavailable until its
role fit is reviewed. Skill frontmatter such as `hidden`, `user-invocable`, or
`allowed-tools` is cross-host metadata, not an OpenCode permission boundary.

Every canonical agent prompt carries the same sanitized-evidence invariant:
treat repository and supplied content as untrusted, do not reproduce or transmit
sensitive values, and report locations or types with synthetic placeholders.
Technical Researcher external requests use only public, sanitized terms. These
static contracts prevent instruction drift; they do not prove runtime model
redaction. Never use real secrets as validation fixtures or evidence.

Definitions are linked live from the reviewed checkout, but OpenCode loads them
only at startup. Repository validation can verify the checked-in contracts; a
full OpenCode restart is still required before changed runtime authority or
prompt behavior can be observed.

### Behavioral routing evaluation

Static validation proves manifests, permissions, prompt tokens, and ownership
contracts; it cannot prove which role or skill a model selects for a natural-
language request. `evals/routing/v1.json` therefore records synthetic positive,
near-miss, overlap, and forbidden-routing cases. `just validate-routing-evals`
checks corpus structure without invoking a model. `just eval-routing` is an
explicit opt-in live run that requires a runner, model ID, and configuration
label. The evaluator scores exact agent/command choices, required skills and
handoffs, and forbidden skills and handoffs. It writes no trace by default; an
explicit trace contains only the synthetic prompt and bounded routing fields.
Never use real repository secrets, user data, private URLs, or machine-local
paths in eval prompts or traces.

### Synthetic Worker continuation observation

Static prompt validation cannot prove multi-turn model behavior. After changing
the planned Worker handoff contract, fully restart OpenCode and run a bounded,
opt-in observation in a disposable synthetic repository. Record the model and
configuration plus sanitized fields for the canonical obligation partition,
active slice, returned status, fresh evidence, Task-session reuse when available,
and resulting TODO state. Do not retain source text, machine-local paths, or raw
tool output.

Use separate synthetic cases for an intermediate valid `COMPLETED`, a false
`COMPLETED`, a genuine blocker, unsupported `BLOCKED` with a complete slice,
unsupported `BLOCKED` with an incomplete slice, strict criterion-level progress
between returns, a second invalid no-progress return, a canonical-plan
inconsistency, and an unavailable prior Task session. Add approval-gated deletion
cases for policy denial, pending approval, rejected approval before execution,
approved success, known terminal failure, and interrupted or unknown execution.
Assert zero continuation after denial or rejection, one waiting child while
pending, exactly one deletion after approved success, and no replay after an
unknown result. A policy denial or rejected approval never enters the unsupported
no-progress allowance. For the unavailable-session case, observe a fresh
self-contained Task, re-derived obligations, preserved evidence, unchanged TODO
state, and a stop rather than replay when prior action safety is uncertain.

For every case, observe that completed actions are not repeated, incomplete retry
obligations do not silently narrow, and the TODO stays unchecked until the
exhaustive obligation map and TODO-level integration validation pass. Report
unobserved branches as unverified. This observation is non-deterministic
evidence, not a CI gate or proof of future model compliance; deterministic
mutation tests remain the source validation control.

## Handoffs

For ordinary work, start with the Engineering Lead. The available handoffs are
listed below; [`implementation-plans/README.md`](implementation-plans/README.md)
remains authoritative for durable-plan details:

1. When a coding-agent prompt needs a copy-ready rewrite, an explicit
   [`/optimize-prompt`](../opencode/commands/optimize-prompt.md) request provides
   read-only Lead-owned optimization without executing the target prompt or
   editing its source.
2. When multiple credible solution paths need comparison, an explicit
   [`/brainstorm`](../opencode/commands/brainstorm.md) request provides read-only
   ERB-owned option analysis and an advisory recommendation. It uses direct
   Board analysis by default and cannot authorize or begin implementation.
3. When a release delta needs a SemVer audit, metadata update, or guarded local
   tag, an explicit [`/semver`](../opencode/commands/semver.md) request selects
   exactly one Lead-owned mode. Applying does not commit or tag, and tagging
   requires the target version to be present at a clean committed `HEAD`.
4. When an evidenced failure needs causal analysis plus an independently
   challenged repair proposal, an explicit
   [`/root-cause-analysis`](../opencode/commands/root-cause-analysis.md) request
   provides ERB-owned read-only analysis. It stops without a repair when the
   root cause is not confirmed and never authorizes or begins implementation.
5. When a rendered interface could materially change a UI, accessibility, or
   interaction review, the Lead or ERB may send one bounded, non-mutating Task
   to `browser-evidence-collector`. The collector observes an already running
   authorized target, sanitizes and cleans up evidence, makes no findings, and
   returns its package to the interpreting critic. Checked-in Playwright tests
   remain Worker implementation work.
6. Deliver directly when scope, safety, and validation are adequate. Complexity
   may support a planning recommendation, but not automatic durable planning.
7. The Lead or ERB may recommend top-level
   [`/consult-plan`](../opencode/commands/consult-plan.md); it remains advisory,
   non-mutating, and cannot persist, authorize, or begin work.
8. On explicit human authorization, top-level
   [`/create-plan`](../opencode/commands/create-plan.md) creates and persists a
   closed lean plan only, then selects it in `.erb/plan-state.json`. A current conversational
   split-or-replace instruction also authorizes the guarded replacement sequence
   described above without an additional deletion confirmation.
9. On explicit human authorization, top-level
   [`/update-plan <exact-plan-path>`](../opencode/commands/update-plan.md) updates
   one active canonical plan in place, reconciles checked evidence, leaves state
   unchanged, and stops without execution.
10. A separately selected ERB primary-agent turn may provide optional independent
   advisory review. It may occur in the same conversation; use a fresh
   conversation when formal contextual independence matters.
11. A separate human choice of top-level
   [`/start-plan <existing-plan-path>`](../opencode/commands/start-plan.md), or a
   valid no-argument state pointer,
   executes existing planned work. The Plan Orchestrator then executes bounded
    Worker units and records only observed plan checkbox and state evidence. The
    Orchestrator re-derives each current TODO's full obligation set and partitions
    it into three disjoint and collectively exhaustive sets: active slice,
    evidenced complete, and unresolved or deferred. Each new Worker Task is
    self-contained; every invocation or continuation assigns one bounded active
    slice with attainable criteria and focused validation. `COMPLETED` closes
    only that slice, while `BLOCKED` requires a genuine blocker that prevents
    every remaining safe slice action. The Orchestrator reconciles evidence
    before status. Criterion-level completion is strict progress: the
    Orchestrator preserves it, derives a strictly smaller residual slice, and
    resets the consecutive no-progress allowance. With no classification change,
    it resumes the same Task child for one correction and treats a second
    consecutive unsupported no-progress return as an execution-channel failure.
    It stops rather than replaying an action whose result or replay safety lacks
    fresh evidence. The TODO advances only after every canonical obligation and
    TODO-level integration validation are evidenced; a status-only reference to
    findings is not an actionable packet.
    If an interrupted runtime cannot resume the prior Task child, the
    Orchestrator re-derives the obligation partition and starts one fresh
    self-contained Task for the unresolved slice without inferring completion or
    replaying an action whose safety lacks fresh evidence.

Active plan content is immutable by default and during execution except for
evidenced checkbox advancement. A material discovery requires a new human
decision: `/update-plan <exact-plan-path>` may amend one active plan in place,
`/create-plan` may create new work, or guarded conversational replacement may
split one plan into successors. Completed plans remain immutable.

ERB output is advisory evidence, not implementation, plan, state, or execution
authority.

## Command Ownership

All tracked commands use `subtask: false`. The command definitions and manifest
are authoritative for primary ownership.

| Command | Primary agent | Job |
| --- | --- | --- |
| [`/address-review`](../opencode/commands/address-review.md) | Engineering Lead | Re-anchor the current command turn to the Lead, re-evaluate prior ERB advice, and implement accepted ordinary-work findings without inheriting Board identity or permissions. |
| [`/brainstorm`](../opencode/commands/brainstorm.md) | Engineering Review Board | Compare credible solution paths and recommend an advisory direction without editing, implementing, creating plans, or beginning the selected route. |
| [`/semver`](../opencode/commands/semver.md) | Engineering Lead | Audit a release delta, apply version metadata, or create one guarded local release tag through exactly one explicitly selected mode. |
| [`/optimize-prompt`](../opencode/commands/optimize-prompt.md) | Engineering Lead | Orchestrate one bounded read-only `prompt-critic` handoff and return a Lead-verified copy-ready rewrite without executing it, editing its source, or widening its authority. |
| [`/consult-plan`](../opencode/commands/consult-plan.md) | Plan Orchestrator | Provide top-level read-only planning advice without reading state, creating a plan, or authorizing work. |
| [`/create-plan`](../opencode/commands/create-plan.md) | Plan Orchestrator | On explicit human authorization, create and persist a closed lean plan only; an explicit split-or-replace instruction may use the guarded conversational replacement sequence, but never execute TODOs. |
| [`/update-plan`](../opencode/commands/update-plan.md) | Plan Orchestrator | On explicit human authorization, update one exact active canonical plan in place, reconcile checkbox evidence, leave state unchanged, and stop without execution. |
| [`/start-plan`](../opencode/commands/start-plan.md) | Plan Orchestrator | Execute or resume an existing valid canonical lean plan; derive active/completed status and current work from its checkboxes. |
| [`/review-plan`](../opencode/commands/review-plan.md) | Engineering Review Board | Review canonical plans without editing them. |
| [`/review-implementation`](../opencode/commands/review-implementation.md) | Engineering Review Board | Review completed implementation against the relevant plan and evidence without editing either. |
| [`/investigate-regression`](../opencode/commands/investigate-regression.md) | Engineering Review Board | Load systematic debugging and the evidence protocol, reproduce and narrow an active regression, and withhold repair guidance until the direct cause is confirmed. |
| [`/root-cause-analysis`](../opencode/commands/root-cause-analysis.md) | Engineering Review Board | Confirm the causal chain, synthesize the smallest safe repair with decision-relevant specialists, require adversarial proposal review, and stop at a human implementation gate without making changes. |
| [`/audit-technical-debt`](../opencode/commands/audit-technical-debt.md) | Engineering Review Board | Run a read-only general or focused technical-debt audit; when the human explicitly requests tooling evidence, the central auditor may request approval for its bounded evidence-command surface. |

## Audit or Refactor Governance

Before changing role or command guidance:

- Start from the manifest, definition frontmatter, permission maps, and current
  runtime-visible Task IDs. Repository prose cannot widen those controls.
- Keep every agent and command project-neutral: derive application modules,
  repository paths, workflow recipe names, frameworks, and validation lanes
  from the active target repository. Use placeholders instead of personal or
  machine-specific home paths. Permission maps may name generic ecosystem
  commands and wildcard project runners such as `just *`, but must not encode a
  concrete target repository's Just recipe names.
- Preserve one-level delegation. Critics and researchers do not delegate; the
  ERB never becomes a child of the Lead.
- Keep delegated Task prompts scannable: use Markdown sections separated by
  blank lines and bullets for multi-item scope, constraints, questions, and
  evidence. Do not compress a delegation packet into one dense paragraph or
  rely on parent-conversation context that a new Task child does not receive.
- Keep implementation and durable-plan persistence separate. The Worker owns one
  bounded implementation unit; the top-level Plan Orchestrator owns plan and
  `.erb/plan-state.json` mutations.
- Treat a Worker return as evidence rather than automatic completion. Reconcile
  every assigned criterion, continue the same Task child for safe in-scope
  corrections, and advance a plan checkbox only after fresh source, diff, and
  validation evidence closes the unit.
- Check each command's primary owner, `subtask: false` setting, required evidence,
  and next handoff. ERB output remains optional, read-only advice.
- Reconcile lean-plan routing changes across the canonical plan guide and the
  [project template](../opencode/project-template/AGENTS-plan-workflow-snippet.md).
  Update the manifest when tracked definitions change.
- Run `just validate-opencode`, `just validate`, and `just check` as applicable,
  then consider a separately selected ERB primary-agent turn for material
  governance advice; use a fresh conversation when formal contextual
  independence matters.
