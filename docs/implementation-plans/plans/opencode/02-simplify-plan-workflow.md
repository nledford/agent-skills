---
plan_id: opencode-02
series: opencode
sequence: 2
title: Simplify the OpenCode Plan Workflow
status: draft
revision: 4
review_decision: pending
reviewed_at:
approved_at:
approved_revision:
depends_on: []
baseline_commit: 9bd28e3a15c237e1fb4cf6e1996da36b687db5e8
execution_owner: plan-orchestrator
source_format: native
source_plan:
created: 2026-07-14
updated: 2026-07-14
completed_at:
---

# OPENCODE-02 — Simplify the OpenCode Plan Workflow

## Executive Summary

Replace the current review-and-approval lifecycle with a lean plan contract for a
solo operator. New plans retain canonical series paths and collision-safe
sequence allocation, but their contents are limited to a title, `TL;DR`, Context,
Objectives, Guardrails, Deliverables, Definition of Done, numbered checkbox
TODOs, and Verification. They carry no frontmatter, lifecycle state, revision,
approval, review, amendment, attribution, alternative, or execution history.

Replace the `planning-coordinator` definition and ID with one dedicated top-level
`plan-orchestrator`; the manifest keeps 23 agents rather than adding another
role. The Plan Orchestrator writes, updates, self-checks, and executes lean plans,
including direct planned implementation or bounded delegation only to
`implementation-worker`. It owns plan checkboxes, native sidebar TODOs,
integration, validation, and completion reporting. Its self-check is an internal
quality pass, never ERB review, approval, readiness, or sign-off.

Unify new requests, lean-plan updates, legacy succession, and execution under
`/start-work [<request-or-plan-path>] [instructions]`. Keep
`/convert-tapestry-plan`, but conversion executes only when the human also asks
for execution. Independent `/review-plan` and `/review-implementation` sessions
remain optional, read-only ERB advice. The Engineering Lead stays the default
primary for ordinary unplanned work, but neither the Lead nor the ERB may write,
update, execute, or implement planned work; both route that work to
`/start-work`.

Execution uses native `todowrite` as a transient, five-item sliding window over
the plan's numbered TODOs. Prompt-contract tests verify that checked-in
instructions require ordering, status, content-length, resume, failure, and final
clearing behavior; they do not prove runtime agent or native UI compliance.

No-path resume uses a disposable, ignored `/.start-work/resume.json` pointer to a
fully self-checked lean plan, never a progress record or proof of authorship. A
checked-in standard-library helper owns that pointer and one cooperative,
repository-wide planned-work execution lock. The lock serializes Plan
Orchestrator sessions and all direct or delegated implementation performed for
their plans; it does not block unrelated filesystem writes or serialize all
repository mutation. The Plan Orchestrator acquires it before reading or relying
on resume or plan state, freshly revalidates all execution evidence under the
lock, holds it while any planned mutation outcome is uncertain, and stops for
reconciliation when concurrent work overlaps plan-owned files. The plan and
current repository evidence remain authoritative, and only accepted plan
checkboxes establish completion.

The helper applies one 1 MiB, strict-UTF-8, stable-read boundary to every lean,
legacy, explicit, pointer-resumed, or Tapestry plan before hashing or agent use.
Tapestry-named paths and commands remain untrusted claims and cannot trigger a
secondary read or execution before validation. Final integration uses a closed
active-workflow inventory and a repository-only lint, test, and validation lane;
`just check` remains separate because its current recipe includes machine-global
symlink verification.

## Problem and Context

The repository currently treats plans as lifecycle records. Creation, persisted
review, revision, approval, execution state, normalization, and histories are
split across a Coordinator, nine plan-lifecycle commands, metadata-heavy
templates, governance prose, and validator constants. That ceremony conflicts
with the human-selected workflow: a plan is an editable execution contract, not
an approval or audit ledger.

The target workflow must support ordinary requests such as “roll these changes
into the plan” without a revision transition or special authorization. Review is
separate advice. Execution may start from a valid lean plan without a review or
approval record, but still stops for a real unresolved decision, unsafe action,
missing dependency, scope conflict, or failed acceptance evidence.

Canonical filenames remain useful for organization and allocation. Existing
verbose plans are therefore grandfathered as immutable legacy artifacts whose
filenames still count toward the series maximum. They are not executable in
place; the Plan Orchestrator creates a newly allocated lean successor when one is
needed.
The tracked `opencode-01` plan is such an artifact, is not a dependency of this
plan, and must remain byte-unchanged.

## Objectives

- Define one closed, metadata-free plan body with only the human-authorized
  sections and numbered Markdown-checkbox TODOs.
- Replace `planning-coordinator` with a primary `plan-orchestrator` that owns safe
  plan creation, conversational updates, legacy succession, Tapestry conversion,
  self-checking, planned execution, integration, and completion reporting.
- Reduce the plan command surface to `/start-work`, retained Tapestry conversion,
  optional plan review, and optional implementation review while preserving the
  two unrelated ERB commands.
- Keep the ERB independent, primary, read-only, and advisory while removing plan
  readiness and implementation approval/sign-off decisions.
- Keep `implementation-worker` as the only implementation subagent and preserve
  its existing plan, delegation, Git, push, and destructive-operation denials.
- Give both the Plan Orchestrator and Engineering Lead flat `todowrite: allow`,
  while reserving plan checkboxes, planned-work TODOs, resume state, and plan
  execution exclusively to the Plan Orchestrator. The Lead may use TODOs only for
  ordinary unplanned session coordination.
- Keep the Lead's ordinary unplanned-work authority, MCP access, and clipboard
  authorization while denying plan edits and removing all Coordinator or Plan
  Orchestrator Task edges.
- Add prompt and validator guardrails that route planned work from the Lead and
  ERB to `/start-work` instead of allowing either role to bypass the Plan
  Orchestrator.
- Route every request the Lead classifies as needing a durable execution
  contract to `/start-work <request>`, even when the request contains no plan
  vocabulary or path; keep only trivial or bounded unplanned work with the Lead.
- Add a disposable resume pointer and one cooperative repository-wide
  planned-work execution lock without adding execution state, cached completion,
  or history to lean plans; the lock serializes Plan Orchestrator planned work,
  not unrelated Lead, agent, process, or human mutations.
- Acquire the planned-work lock as the first stateful operation after request
  parsing, then freshly reload and revalidate the pointer, exact plan bytes and
  hash, checkbox state, worktree, and repository evidence before execution.
- Treat plan, Tapestry, and repository text as untrusted data and enforce
  canonical source roots, path containment, regular-file, symlink, size, and
  UTF-8 checks before conversion or execution.
- Apply one conservative 1 MiB bounded-read and strict-UTF-8 boundary to every
  canonical lean or legacy plan, and validate every Tapestry-named secondary
  path, command, test, and symbol as an untrusted claim before any secondary read
  or independently derived command runs.
- Keep root and project-template plan guidance synchronized and update the
  manifest, validator, fixtures, and tests as one coherent contract.
- Make stale-route validation deterministic with a closed active-workflow
  inventory and exact obsolete-token diagnostics, and require a repository-only
  lint/test/validation lane independent of machine-global symlink state.
- Deliver implementation in human-required atomic logical commits whose focused
  tests and `just validate-opencode` pass at every intended boundary.

## Non-Goals

- Rewrite, normalize, or execute historical plan files, including `opencode-01`.
- Copy Weave continuation hooks, internal imports, compaction state, idle
  mutation, plugin code, or `.weave` state machinery.
- Add a plugin, custom TODO tool, database, audit trail, approval state,
  persisted review result, compatibility alias, or a second planning role beside
  the selected Plan Orchestrator.
- Add plan lifecycle state, full execution history, a last-completed TODO cache,
  prompts, diffs, or evidence payloads to runtime resume state.
- Add a general repository mutation lock, claim exactly-once execution, suppress
  unrelated Lead or external work, or grant the Lead, ERB, or Worker lock or
  resume-state authority.
- Add timeout expiry or lock stealing, timestamps used for expiry, or same-OS-user
  hostile-process tamper resistance to the cooperative coordination mechanism.
- Change unrelated specialist agents, unrelated behavior in the retained
  audit/regression commands or legacy cleanup checklist, or skills. Their stale
  lifecycle routes are in scope for targeted repair only.
- Change skills, dependencies, credentials, providers, configured MCP access,
  live machine-local OpenCode configuration, or external repositories.
- Push, deploy, rewrite Git history, amend commits, or mutate the existing legacy
  plan. Ordinary atomic commits for the four validated implementation slices are
  required by the human decision recorded in this revision.

## Applicable Project Guidance

- `AGENTS.md` requires the repository README, skill taxonomy, cross-reference
  map, and engineering governance guide to be read before repository-doc changes.
  It requires `just validate` for routing or link changes and `just check` for
  tooling, tests, scripts, or validator changes. The current `Justfile` makes
  `just check` include machine-global `verify`; this plan therefore keeps it as a
  configured-maintainer-workstation check and defines an equivalent mandatory
  repository-only lint/test/validation lane for every implementation environment.
- `README.md` makes `opencode/manifest.json` the reviewed inventory, treats the
  linked checkout as live after OpenCode restart, and keeps credentials and live
  configuration outside the repository.
- `docs/engineering-agent-governance.md` owns role authority, exact runtime Task
  IDs, one-level delegation, command ownership, and ERB independence.
- Until this plan is implemented, `docs/implementation-plans/README.md` and
  `TEMPLATE.md` require this transition plan's current frontmatter and lifecycle
  sections. The implementation replaces that contract only for new plans.
- Root and project-template implementation-plan README/template files are
  validator-enforced byte-for-byte copies.

## Current-State Evidence

- The implementation baseline remains
  `9bd28e3a15c237e1fb4cf6e1996da36b687db5e8`. Revision-3 planning began at
  `4ed8bb61703e04cca0e9650292587d76ff4bef4a`, the separately owned source unit
  advanced `HEAD` to `d6e56e67009ca5a4ddda4edc6dc189ea3b3412e8`, and the
  revision-3 plan commit advanced it to
  `f8fa6b0c6608b81b987db9aad01c4b50c28cf4cf`. The revision-3 ERB review and this
  revision-4 assignment both identify `f8fa6b0` as current `HEAD`. Supplied range
  evidence covers the full baseline-to-HEAD interval: the intervening planning
  commits changed only the two durable plan files, `d6e56e6` changed exactly the
  four source files named below, and `f8fa6b0` changed only this plan. Review and
  execution must continue to account for that source drift rather than treating
  the metadata baseline or an earlier assignment start as the current checkout.
- The `opencode` series contained only
  `01-agent-definitions-improvement-program.md` when sequence `02` was allocated.
  Both `opencode-01` and `opencode-02` are tracked at current `HEAD`.
  `opencode-01` is a legacy draft at revision 3; its filename still makes the
  predecessor sequence `01`, and this plan does not depend on its content or
  identity.
- At the initial revision read, `git status --short` reported the target plan plus
  four separately owned modified files:
  `docs/engineering-agent-governance.md`,
  `opencode/agents/engineering-lead.md`, `tests/test_opencode_manager.py`, and
  `tools/opencode_manager.py`. The target delta contains the persisted revision-2
  ERB record. The other four files are a human-selected concurrent work unit and
  are not source to fold into this revision.
- The concurrent unit adds ordered Engineering Lead Git permissions, generic
  `todowrite: allow`, and matching validation/tests while preserving the
  human-authorized Lead `pbcopy` and configured MCP access. This Coordinator made
  no write to those four files. During the revision they were externally
  committed as `d6e56e6` (`feat(opencode): authorize lead git and todo tools`),
  after which `git status --short` reported only this target plan. The supplied
  revision-3 review evidence subsequently verified that commit's exact four-file
  scope but found no preserved historical test output. Before implementation,
  require a clean worktree after this plan's lifecycle work, reread the
  then-current `HEAD`, reconcile this plan against that source, and run the two
  observed current-source prerequisite checks specified in slice 0.
- `opencode/manifest.json` currently inventories 23 agents and 11 commands. The
  plan-lifecycle commands are `prepare-work`, `review-plan`,
  `record-plan-review`, `revise-plan`, `approve-plan`, `execute-plan`,
  `review-implementation`, `convert-tapestry-plan`, and `normalize-plan`; the
  audit and regression commands remain separate primary entry points.
- The Lead currently has `ask` edit access for plan paths, a plan-path Bash deny,
  direct implementation authority, generic `todowrite: allow` from the concurrent
  commit, and Task access to both Coordinator and Worker. The Worker already
  denies plan edits and plan-path Bash access, delegation, commit, push, and
  destructive operations. The ERB is a separate read-only primary.
- `planning-coordinator` is currently a subagent with exclusive plan-write
  authority and no implementation or delegation authority. No
  `plan-orchestrator` definition or `/start-work` command exists at the supplied
  baseline.
- `PLAN_TEMPLATE_TOKENS` and `PLAN_TEMPLATE_HEADINGS` in
  `tools/opencode_manager.py` require the lifecycle metadata and history sections
  in the synchronized template. `tests/test_opencode_manager.py` builds the same
  verbose fixture and has mutation coverage for those requirements.
- At the preserved implementation baseline, the manager's known permission tools
  did not include `todowrite`, and no committed repository definition contained
  that permission. The supplied OpenCode evidence establishes that
  `todowrite` is flat, each call replaces the whole session list, input order is
  display order, and `todos: []` clears it. Native OpenCode does not enforce this
  plan's five-item, one-active-item, or 30-character rules. The `d6e56e6` source
  commit adds manager recognition and generic Lead permission at current `HEAD`;
  this plan must preserve both.
- `audit-technical-debt.md` still routes remediation to `/prepare-work`;
  `investigate-regression.md` still routes material plan changes through
  `/revise-plan`, the Lead, and the Coordinator; and
  `opencode/cleanup/weave-cleanup-checklist.md` still names `/normalize-plan`,
  Coordinator-only writes, and approval-gated execution. Those retained files
  need targeted routing and authority repairs while preserving unrelated
  behavior.
- No checked-in `tools/start_work_state.py`,
  `tests/test_start_work_state.py`, or tracked `/.start-work/` runtime-state
  contract exists in the observed source.
- The specialist inspection supplied by the human reports that
  `just validate-opencode` and all 58 focused OpenCode manager tests passed before
  initial planning. That is historical prompt-contract evidence, not current
  runtime proof or preserved evidence for `d6e56e6`; this Coordinator did not
  rerun implementation checks. Because all later commits through `f8fa6b0` affect
  only durable plans, rerunning the focused manager suite and
  `just validate-opencode` at then-current `HEAD` before slice 1 validates the
  same source behavior.
- The latest persisted ERB record exactly matches this path, `opencode-02`,
  revision 3, and baseline, and records `ready-with-revisions` at
  `2026-07-14T19:45:00-04:00`. It follows the preserved revision-2 record. No
  approval exists. The worktree was clean at that review; after its record was
  persisted, the Coordinator's revision-4 pre-edit check reported only this target
  plan modified, with `HEAD` still at `f8fa6b0`.

## Revision 3 Finding Dispositions

1. **Accepted — stale retained lifecycle routes.** Target only the stale routing
   and authority lines in `audit-technical-debt.md`,
   `investigate-regression.md`, and the Weave cleanup checklist; preserve their
   unrelated behavior rather than requiring byte equality.
2. **Accepted — resume pointer plus atomic planned-work lock.** Use the selected
   disposable pointer and fail-closed planned-work exclusion described below; do
   not add execution state to plans. Revision 4 records the human's narrower
   cooperative execution scope and supersedes any all-mutation interpretation.
3. **Accepted — legacy/Tapestry source trust boundary.** Enforce canonical roots,
   path/type/size/encoding checks, untrusted-data handling, and synthetic negative
   tests.
4. **Accepted — validation and atomic-commit sequencing.** Use four coherent
   implementation slices, each with its own focused tests and
   `just validate-opencode` evidence before its atomic commit.
5. **Accepted — complex requests can bypass Plan Orchestrator.** Require the Lead
   to send every durable-contract classification to `/start-work <request>`, even
   without plan terminology.
6. **Accepted — prompt tests overstate runtime proof.** Limit static test claims to
   checked-in prompt and permission contracts; report unobserved runtime agent,
   delegation, cancellation, and sidebar checks as skipped.
7. **Accepted with modification — TODO permission ownership.** Preserve generic
   unplanned-session `todowrite: allow` for the Lead and grant it to the Plan
   Orchestrator, but reserve planned-work TODOs, checkboxes, resume state, and
   execution to the Plan Orchestrator. Worker and ERB receive no explicit allow.
8. **Accepted — stale current-state evidence.** Record both plans as tracked at
   current `HEAD` and preserve the separate concurrent four-file work unit as a
   pre-execution prerequisite.

## Revision 4 Finding Dispositions

1. **R3-1 accepted with explicit human modification — planned-work-only
   execution lock and recovery.** Replace every general or unqualified global
   lock claim with one cooperative repository-wide planned-work execution lock.
   It serializes Plan Orchestrator sessions and their direct or delegated planned
   implementation, while unrelated Lead and external work may continue. Acquire
   before reading resume or plan state, reload all evidence under the lock, hold
   through every planned mutator and uncertain outcome, reconcile acceptance
   evidence before each resume, and document at-least-once risk rather than
   exactly-once behavior.
2. **R3-2 accepted — narrow ignored state and untrusted pointer.** Ignore only
   `/.start-work/resume.json` and `/.start-work/lock/`; reject unsupported state
   entries; treat the pointer as an untrusted locator and contract identifier;
   require no-path confirmation; close and bound lock metadata; use
   repository-relative `.start-work/**` permission patterns; and prove effective
   state actions for every role.
3. **R3-3 accepted — complete primary and secondary input boundaries.** Bound
   every canonical lean or legacy plan at 1 MiB before hashing, decoding, parsing,
   or agent use, with strict UTF-8 and file-change detection. Treat every
   Tapestry-named path, command, test, and symbol as an untrusted claim; validate
   secondary paths before reads and derive commands independently from trusted
   repository evidence.
4. **R3-4 accepted — available and deterministic validation.** Replace missing
   historical-output and isolated-worktree assumptions with two observed
   current-source reruns before slice 1; define the complete validator-owned
   active-workflow inventory and obsolete-token set; place retained-route
   mutation tests in slice 3 and activate the full scan in slice 4; make a
   repository-only lane mandatory; and keep `just check` as conditional
   maintainer-workstation verification with bounded, cleanup-safe contention
   tests.

## Proposed Design

### Lean plan contract

Retain the canonical path
`docs/implementation-plans/plans/<series>/<NN>-<slug>.md`, the series regex,
zero-padded `01`–`99` range, maximum-plus-one allocation, gap non-reuse,
collision checks, and exhaustion behavior. Identity comes from the path; it is no
longer repeated inside the plan.

The complete body for every newly created, updated, succeeded, or converted plan
is:

```markdown
# <Title>

## TL;DR

## Context

**Original request:**

**Key repository findings:**

**Dependencies:**

## Objectives

## Guardrails

## Deliverables

## Definition of Done

## TODOs

1. [ ] <bounded implementation step>

## Verification
```

No other metadata or sections are allowed. In particular, omit frontmatter,
plan IDs, statuses, baselines, owners, dates, revision/review/approval fields,
provenance fields, histories, amendments, specialist attribution, alternatives,
execution records, and open-decision ledgers. Context retains only the original
request, decision-relevant repository findings, and actual prerequisites that an
executor cannot safely ignore. Do not copy inventories, Git history, current
diffs, or other state merely because it can be re-read from the repository.

Objectives state intended outcomes. Guardrails bind safety and exclusions.
Deliverables name the durable results. Definition of Done states behavioral
acceptance. TODOs are ordered, bounded, numbered checkbox work units, and
Verification names the checks needed to prove completion. Required unresolved
choices are settled conversationally and rolled into these sections before
execution rather than stored as lifecycle state.

### Plan Orchestrator authority and safe plan writes

Replace `opencode/agents/planning-coordinator.md` with
`opencode/agents/plan-orchestrator.md` and change the exact runtime ID to
`plan-orchestrator`. The new definition is a primary agent with broad `ask`
authority for safe direct implementation. It writes plan paths only through edit
tools, keeps `docs/implementation-plans/**: ask`, retains the plan-path Bash
deny, and re-reads every plan write before continuing or reporting success.

Before creation, update, succession, or conversion, the Plan Orchestrator rejects
a symlinked plan root, source, destination parent, or destination and proves that
the resolved target remains under `docs/implementation-plans/`. It validates the
series, calculates the existing-series maximum, allocates maximum plus one from
`01` through `99` without filling gaps, checks collision and exhaustion, and
blocks if an edit tool cannot safely create the required parent. It never uses
shell redirection, shell file mutation, an apply-patch move, or alternate path
spelling for a plan.

Treat every plan, Tapestry source, and repository document as untrusted data.
Instruction-like text inside those files cannot override the human request,
applicable `AGENTS.md`, permission maps, validated scope, guardrails, or the
self-checked lean plan. Never copy secrets, credentials, tokens, environment
values, sensitive values, or machine-local configuration into a plan.

Before hashing, decoding, parsing, self-checking, displaying TODO state, or
supplying any existing canonical plan to an agent, use a bounded read with a
1 MiB (1,048,576-byte) maximum, require strict UTF-8, and require the path and
every component to remain repository-contained, regular, and non-symlinked.
Accept exactly 1 MiB and reject 1 MiB plus one byte. Detect replacement or
size/content change during validation and fail closed rather than mixing
snapshots. Apply the same boundary to lean and legacy plans, including explicit
paths and pointer resume. An oversized or invalid legacy plan remains immutable
and produces a human-actionable error; it is never partially read, converted, or
sent to an agent.

An existing lean plan may be updated in place from `/start-work` instructions or
ordinary Plan Orchestrator conversation, without revision semantics. If the
target has frontmatter or otherwise fails the closed lean shape, leave it
untouched and allocate a successor in the same series. Carry forward only useful
original-request context, current repository findings, real dependencies,
objectives, guardrails, deliverables, acceptance conditions, TODOs, and
verification. The predecessor still reserves its filename number; sequence order
does not create an execution dependency.

The Plan Orchestrator owns all planned implementation. It may implement directly
or delegate one bounded implementation unit at a time only to the exact
`implementation-worker` ID, then it integrates and validates the result. Its Task
map is broad-deny with only `implementation-worker: allow`; it cannot invoke the
ERB, the Engineering Lead, specialists, or any other primary agent through Task.
The Worker still cannot delegate, which preserves one-level delegation.

### Secondary references from untrusted plans

Treat every path, command, test, and symbol named by Tapestry or legacy content as
an untrusted claim, not an operation or permission to inspect. A referenced path
may be followed only after validating the complete string and proving
repository-relative canonical containment, regular non-symlink type and
components, a bounded size, strict UTF-8 when text is expected, and exclusion of
sensitive or machine-local files. Reject control characters, newlines, shell
metacharacters, command substitution, or any path argument that cannot be handled
through a structured non-shell tool. No rejected or not-yet-validated string may
trigger a secondary read.

Never execute a command merely because untrusted content names it, and never
splice a named command, test, symbol, or path into a shell string. Derive every
validation command independently from applicable `AGENTS.md`, repository-owned
workflow definitions, and current source evidence. If no trusted structured
operation can verify the claim, record it as unverified or stop; do not broaden
permissions or fall back to a shell. Synthetic tests must prove that unsafe
references produce neither a secondary read nor command execution.

### Resume pointer and planned-work execution lock

Add exactly two ignored local-state entries at the repository root:

```text
/.start-work/resume.json
/.start-work/lock/
```

Do not ignore `/.start-work/` broadly. The helper rejects every unsupported file
or directory below `.start-work/`; for example, `.start-work/history.json`
remains visible to Git and makes state validation fail. Reject symlinked state
roots or components. `resume.json` is a disposable, untrusted locator and
contract identifier—never authoritative progress, authentication, a credential,
or proof of Plan Orchestrator authorship—and has exactly this schema:

```json
{
  "version": 1,
  "plan_path": "docs/implementation-plans/plans/<series>/<NN>-<slug>.md",
  "contract_sha256": "<64 lowercase hex>"
}
```

Reject malformed or oversized JSON, duplicate or unknown fields, unsupported
versions, invalid hashes, noncanonical or unsafe plan paths, and other corrupt
state. The path must be relative, resolve to an existing regular, non-symlink
lean plan below `docs/implementation-plans/plans/`, and contain no absolute or
`..` form, symlinked component, legacy shape, or resolution outside that root.
Use a small fixed pointer-size limit encoded in the helper and tests; selecting
the exact conservative byte threshold is incidental local implementation
judgment, not permission to expand the schema. Never scan for or guess an active
plan.

`contract_sha256` hashes the exact UTF-8 plan bytes after normalizing only valid
numbered TODO checkbox markers (`[ ]`, `[x]`, or `[X]`) to `[ ]`. Checkbox
progress therefore leaves the contract hash stable, while wording, order,
guardrails, acceptance, or verification changes invalidate it. Store no
completed-step field, prompt, instruction, diff, evidence payload, absolute user
path, secret, credential, environment value, token, or model output.

Write or replace the pointer only after the resulting lean plan passes the
complete self-check, including plan-only creation. Retain it on explicit pause,
blocker, failure, or cancellation. Clear it only after every plan TODO and final
validation succeed and native TODOs are cleared, and only when the pointer still
names the same plan and hash. A hash mismatch never auto-executes: no-path resume
stops for the human, while an explicit safe path may replace the pointer only
after lock acquisition and a complete self-check. If the pointed-to plan has
been deleted, no-path resume fails closed; an explicit valid path may safely
replace the stale pointer under the same rules.

Implement pointer and lock behavior in a checked-in standard-library helper,
`tools/start_work_state.py`, with focused executable tests in
`tests/test_start_work_state.py`. The helper atomically creates
`/.start-work/lock/` as the exclusion point for one cooperative,
repository-wide planned-work execution lock. It serializes all Plan Orchestrator
sessions and their direct or delegated plan implementation because distinct
plans may overlap files. It does not serialize ordinary repository work, prevent
filesystem writes, or grant authority over unrelated Lead, ERB, human, agent, or
process activity.

After parsing the human request without reading repository state, lock-directory
creation is the first stateful operation. It occurs before reading or relying on
the pointer, plan bytes, plan hash, checkbox state, worktree, execution evidence,
or any pre-lock repository snapshot. Under the newly established exclusion, the
helper freshly resolves no-path state, validates a parsed explicit locator, or
allocates a new canonical path and then freshly reloads and revalidates the
applicable pointer, canonical plan path, exact bounded plan bytes and hash,
checkbox state, worktree, and repository evidence. Never execute from a pre-lock
snapshot. For no-path resume or new-plan creation, the lock directory is created
before the pointer is read or repository allocation evidence is inspected; lock
metadata is finalized under that exclusion after the canonical plan path is
resolved. Any contender treats an existing lock directory, including an
interrupted incomplete acquisition, as held and fails closed.

Lock metadata is one bounded, strict-UTF-8, duplicate-rejecting JSON object with
exactly this schema:

```json
{
  "version": 1,
  "owner_token": "<64 lowercase hex>",
  "plan_path": "docs/implementation-plans/plans/<series>/<NN>-<slug>.md"
}
```

Reject malformed, oversized, duplicate- or unknown-field, unsupported-version,
invalid-token, unsafe-path, symlinked, or non-regular metadata. Write no timestamp
used for expiry. Generate a collision-resistant owner token for cooperative
coordination, not as a credential; only its matching owner may release the lock.
Same-OS-user hostile-process tamper resistance is out of scope. Acquisition fails
immediately when held and never waits, retries, expires, or steals by timeout.

The Plan Orchestrator holds the lock through every direct planned mutator,
delegated Worker, child process, timeout, cancellation path, and Task. The Worker
does not acquire, release, or mutate lock state. Release after normal completion,
explicit pause, blocker, failure, cancellation, or a plan-only return only when
every planned mutation outcome is known and no child can still mutate. Retain the
lock whenever any direct or delegated planned outcome is uncertain, not only when
Worker status is uncertain. Abrupt process termination must not auto-release it.
A stale lock may be cleared only after explicit human confirmation that no Plan
Orchestrator, Worker, child process, or planned mutator remains active; corrupt or
uncertain lock state fails closed.

Unrelated Lead or external work may continue while the planned-work lock is held
and must stay out of the plan's commits. The Plan Orchestrator's under-lock drift
checks compare plan-owned files and acceptance evidence before each mutation. If
concurrent work overlaps an owned file or invalidates evidence, stop for
reconciliation; do not absorb or overwrite it. Unrelated drift alone neither
blocks that work nor gives the Plan Orchestrator authority over it.

On no-path resume, after lock acquisition and fresh validation, display the
resolved canonical plan path and the checked and unchecked numbered TODO state.
Obtain explicit human confirmation before any plan edit, checkbox write,
delegation, implementation mutation, or planned sidebar mutation. A pointer alone
never authorizes execution.

Before the first unchecked TODO on every resume—and especially after a blocker,
failure, cancellation, process loss, or stale-lock recovery—reconcile current
acceptance evidence while holding the lock. If the effect is already satisfied,
rerun required validation and then check the TODO without repeating the effect;
if partially applied, repair or continue safely; if definitely unapplied,
execute it; and if unknown or non-idempotent, stop for the human. Do not claim
exactly-once execution. External effects carry at-least-once risk and require
operation-specific idempotency or explicit human reconciliation when evidence
cannot prove the outcome.

Plan Orchestrator and the helper are the only state writers. Lead and Worker edit
permissions explicitly deny the repository-relative pattern `.start-work/**`;
ERB remains read-only, and Lead, ERB, and Worker receive no pointer, lock,
release, stale-recovery, or resume-state authority. Do not add a broad automatic
Bash allow merely to invoke the helper. Preserve normal runtime permission policy
unless implementation evidence supports one narrowly validated safe command
rule. Validate effective actions against `.start-work/resume.json` and lock
metadata for all four roles rather than checking only for textual rule presence.

### `/start-work` and Tapestry conversion

`/start-work [<request-or-plan-path>] [instructions]` is the single create, update,
and execute entry point, owned by `plan-orchestrator`:

- With no path or request, acquire the planned-work lock before reading the
  pointer, resume only the freshly validated pointer, display the resolved
  canonical path and checked/unchecked TODOs, and require explicit human
  confirmation before mutation. Never infer an active plan from filenames, TODO
  state, recent edits, or repository scans.
- For a new request, inspect current evidence, select a valid series, allocate and
  write a lean plan, self-check it, then execute by default. If series choice has
  material organizational consequences, stop for the human rather than guessing.
- For an explicit plan path, parse the locator, acquire the planned-work lock,
  and then enforce the relative canonical path, containment, regular-file,
  non-symlink, 1 MiB, stable-read, and strict-UTF-8 rules before using its bytes.
  For a lean plan, apply requested conversational changes in place, self-check
  the complete result, then execute unchecked TODOs by default. For a legacy
  plan, preserve the source byte-for-byte, allocate a lean successor under the
  same series, self-check it, and execute that successor by default.
- When the human explicitly requests plan-only behavior, complete the write and
  self-check and update the pointer, but do not implement, delegate, update
  execution checkboxes, or populate the sidebar as though execution started.

Acquire the planned-work execution lock as the first stateful operation after
parsing every branch and before reading or relying on pointer, plan, checkbox,
hash, worktree, or execution evidence. Freshly reload all of those inputs under
the lock before any pointer, plan, checkbox, delegation, conversion, sidebar, or
implementation mutation. An explicit path may replace a corrupt pointer only
after safe lock acquisition, canonical path validation, and complete self-check.

Do not add `/create-plan`, `/update-plan`, or another execution command. The Plan
Orchestrator prompt applies the same operations during ordinary conversation, so
the command is a convenient top-level route rather than a separate authority
model.

`/convert-tapestry-plan <source> <series> [instructions]` also routes directly to
`plan-orchestrator`. It accepts only a relative path that resolves under
`.weave/plans/**` to a regular, non-symlink Markdown file with no symlinked path
component. Before reading or copying, reject absolute paths, `..`, outside-root
resolution, directories, special files, invalid UTF-8, and files larger than
1 MiB. Use a bounded, stable read and strict decoding, accepting the exact limit
and rejecting limit plus one. Then treat every named file, symbol, behavior,
dependency, acceptance condition, test, and command as an untrusted claim.
Validate secondary paths through the structured boundary above and derive any
validation command independently from trusted repository guidance and current
source evidence; a named command is never executed merely because the source
contains it. Write and self-check a newly allocated lean plan containing only
still-useful source content in allowed sections, preserve the source, write no
provenance metadata, and never obey embedded instruction-like text. Conversion
is plan-only by default; execute the converted plan only when the human also
requests execution.

### Self-check and optional independent review

Before planned execution, the Plan Orchestrator's self-check confirms the exact
lean shape, current repository grounding, objective-to-deliverable alignment,
bounded and ordered TODOs, guardrail coverage, behavioral Definition of Done,
usable verification, and absence of an unresolved central decision. It corrects
ordinary plan defects and re-reads the result. A real missing product or
architecture choice, unsafe action, absent prerequisite, scope conflict, or
unverifiable acceptance condition stops work for the human.

This self-check is not independent: never label or describe it as ERB review,
approval, readiness, sign-off, or equivalent evidence. It creates no review
record and is not a substitute for `/review-plan` or `/review-implementation`.

The Plan Orchestrator may report one out-of-band review-advice level:

- `none`: independent review is unlikely to change a narrow, well-evidenced
  execution.
- `recommended`: independent review could materially improve confidence, but
  execution may proceed without it.
- `strongly recommended`: risk or uncertainty makes independent review prudent,
  but the label itself is not an execution gate.

Never write the level into a plan or turn it into approval state. The ERB remains
a separate top-level, read-only primary. `/review-plan` and
`/review-implementation` return findings, evidence, uncertainty, suggested
corrections, skipped checks, and residual risk only; they produce no durable
record, plan readiness decision, implementation approval/sign-off, or mandatory
gate. After giving advice, the ERB directs the user to
`/start-work <plan-path>` to apply changes or execute, while stating that review
was optional.

### Lead, ERB, and Worker guardrails

The Engineering Lead remains the default primary for ordinary unplanned request
intake, classification, bounded implementation, integration, and validation. Set
its plan-path edit rule to `deny` while preserving the plan-path Bash denial,
human-authorized `pbcopy`, every configured MCP permission, root `ask` behavior,
generic unplanned-session `todowrite: allow`, and access to
`implementation-worker` for non-plan bounded work. Remove the
`planning-coordinator` Task edge and do not add a `plan-orchestrator` edge. Add an
explicit `.start-work/**` edit denial. Keep unrelated valid research and critic
edges unless another existing invariant requires their change.

The Lead prompt must say that it never writes, updates, executes, or implements a
plan or uses its TODO authority for plan checkboxes, planned-work TODOs, resume
state, or plan execution. When a request asks it to create, update, execute, or
implement planned work, supplies a plan path, or is classified as needing a
durable execution contract, it stops and directs the user to
`/start-work <request-or-plan-path>` instead of bypassing the Plan Orchestrator.
This applies even when a complex request has no plan vocabulary. Only trivial or
bounded unplanned work remains direct Lead work.

The ERB stays read-only and must never execute or implement a plan. Remove its
plan `Ready`/`Ready With Revisions`/`Not Ready` decisions, implementation
`Approve`/`Approve With Follow-ups`/`Request Changes` decisions, structured
durable review-record language, and any suggestion that review gates execution.
Its plan and implementation commands remain optional advice, followed by the
same `/start-work <plan-path>` route when the human wants changes or execution.

Update the Worker prompt so it may receive one bounded implementation unit from
the Lead for unplanned work or from the Plan Orchestrator for planned work. It
reports acceptance and validation evidence to its caller, but cannot edit plans,
change checkboxes, sidebar, or resume state, delegate, commit, push, deploy,
perform destructive migrations, or broaden scope. Give it an explicit
`.start-work/**` edit denial and no explicit `todowrite: allow`; ERB likewise
receives no explicit allow.

### Command and manifest inventory

Delete `/prepare-work`, `/record-plan-review`, `/revise-plan`, `/approve-plan`,
`/normalize-plan`, and `/execute-plan` without aliases. Add only `/start-work`.
Retain `/convert-tapestry-plan`, optional `/review-plan`, optional
`/review-implementation`, `/audit-technical-debt`, and
`/investigate-regression`. Update only the retained audit/regression lines that
route to deleted lifecycle commands or Coordinator/approval concepts; preserve
all unrelated audit and regression behavior.

The resulting sorted manifest contains exactly 23 agents and 6 commands.
`plan-orchestrator.md` replaces `planning-coordinator.md`, so the agent count does
not change. Command ownership is:

- `plan-orchestrator`: `start-work`, `convert-tapestry-plan`;
- `engineering-review-board`: `review-plan`, `review-implementation`,
  `audit-technical-debt`, `investigate-regression`.

Every command keeps `subtask: false`. In the cleanup checklist, replace only the
stale `/normalize-plan`, Coordinator-write, and approval-gate guidance with the
new conversion, Plan Orchestrator, `/start-work`, and optional-review model;
preserve unrelated inventory, provenance, safety, and verification guidance.

### Native TODO sliding window

Add flat `todowrite: allow` to the Plan Orchestrator's permission map and retain
the concurrent unit's flat Lead allow, recognizing the tool in validator policy.
Only the Plan Orchestrator has planned-work sidebar authority. The Lead's allow
is limited by prompt and deterministic validator tests to generic unplanned
session coordination. Worker and ERB receive no explicit allow. Keep the Lead's
`pbcopy`, every configured MCP prefix, plan-path Bash denial, and all unrelated
permission behavior unchanged.

The Plan Orchestrator treats plan checkboxes as the durable work contract and
native TODOs as a transient view:

1. Every `todowrite` call supplies the complete visible list because the call
   replaces, rather than patches, session TODOs.
2. Display at most five items and exactly zero or one `in_progress` item.
3. At start, select the current executable unchecked step, mark it
   `in_progress`, and follow it with up to four `pending` steps.
4. During execution, show the most recently accepted `completed` item first, the
   current `in_progress` item second, and then the next `pending` items, capped at
   five.
5. Each content string is `<step>. <summary>`, retains the original plan step
   number after earlier items leave the window, and limits `<summary>` to 30
   characters excluding the numeric prefix.
6. On resume, acquire the planned-work lock first, freshly reload the plan and
   acceptance evidence, and reconcile the first unchecked step before rebuilding
   the whole window. Treat checked items as accepted only after required current
   evidence remains valid. Use the pointer only as an untrusted locator and
   contract identifier, never authentication or proof of authorship. Do not treat
   the pointer or stale sidebar as durable progress, infer completion from either,
   or reconstruct old completed entries merely for display. For no-path resume,
   wait for the required human confirmation before writing this planned sidebar.
7. On a blocker or failed attempt, leave the current plan checkbox unchecked,
   keep at most that step `in_progress`, retain only the latest accepted
   completion when relevant, and report the blocker. Never batch or infer
   completions.
8. Only the Plan Orchestrator checks a plan TODO after the step's acceptance
   evidence and all required validation succeed. Worker completion reports are
   input evidence, not authority to update the plan or sidebar.
9. After the final step succeeds, briefly replace the sidebar with only that
   final `completed` item, then call `todowrite` with `todos: []` before the final
   report. No active, pending, or stale completed item remains.

OpenCode does not enforce the list-size, active-count, or summary-length rules.
Focused tests verify that checked-in prompts require them and reject
contradictory or missing clauses; those tests do not prove agent compliance,
delegation, cancellation, atomic exclusion, or native UI behavior.

## Alternatives and Trade-offs

- **Keep direct Lead plan ownership from revision 1:** rejected by the human.
  Planned work needs a dedicated top-level owner so ordinary Lead delivery and
  plan execution cannot bypass one another.
- **Retain the Coordinator, persisted review, or approval as optional modes:**
  rejected. Keeping lifecycle concepts would preserve the same ceremony and
  ambiguity under different wording.
- **Add the Plan Orchestrator beside the Coordinator:** rejected. The selected
  role replaces the old definition and ID, preserving the 23-agent total.
- **Split create, update, and execute back into separate commands:** rejected.
  `/start-work` and ordinary Plan Orchestrator conversation own all three
  operations, with explicit plan-only behavior when execution should stop.
- **Store review-advice levels or ERB findings in plans:** rejected. Review is
  out-of-band and advisory; durable storage would recreate state and gating.
- **Rewrite existing plans into the lean shape:** rejected. Historical files are
  left intact, continue to reserve their numbers, and receive successors only on
  demand.
- **Keep removed commands as aliases:** rejected. A minimal command surface is a
  stated objective, and aliases would perpetuate obsolete workflows.
- **Copy Weave's rolling-window machinery:** rejected. Native `todowrite` already
  provides replace-in-order and clear behavior; prompt policy and tests cover the
  repository-specific limits without plugin state.
- **Resume by scanning plans or storing the last completed step:** rejected.
  Scanning guesses authority, and a progress cache would compete with plan
  checkboxes. The human selected one disposable path-and-contract-hash pointer.
- **Use per-plan locks or timeout-based lock stealing:** rejected. Plans can
  overlap files, and elapsed time cannot prove an active planned mutator has
  stopped. One repository-wide planned-work execution lock fails closed until
  its owner releases it or a human explicitly confirms stale-lock recovery is
  safe.
- **Serialize every repository mutation:** rejected by the human. The selected
  lock is cooperative and covers Plan Orchestrator sessions plus their direct and
  delegated planned implementation only. Unrelated Lead or external work may
  continue; overlap with plan-owned files is handled by under-lock drift stops,
  not by claiming a filesystem-wide enforcement boundary.
- **Claim exactly-once TODO effects:** rejected. Checkboxes and acceptance
  evidence support safe reconciliation, but external effects retain at-least-once
  risk and require operation-specific idempotency or human resolution when the
  outcome is unknown.
- **Forbid all Lead TODO use:** rejected with modification. The concurrent work's
  generic Lead `todowrite: allow` remains, but prompt and validator boundaries
  prohibit its use for any planned-work checklist, checkbox, state, or execution.
- **Give the Plan Orchestrator plan-path Bash access:** rejected. Edit-tool writes
  are sufficient and preserve the existing defense-in-depth boundary, at the
  cost of blocking when an edit tool cannot create a required parent safely.
- **Add broad automatic Bash permission for the state helper:** rejected. Keep
  normal runtime policy and justify only a narrowly validated safe invocation
  rule if implementation evidence shows one is necessary.
- **Let the Plan Orchestrator invoke ERB or specialist Tasks:** rejected. Optional
  independent review stays top-level, and planned implementation delegation has
  one exact child: `implementation-worker`.

## Dependencies

`depends_on` is empty. `opencode-01` reserves sequence `01` but is neither an
execution prerequisite nor a source plan for this work. The implementation is
one coordinated repository change delivered in four validated atomic commits:
prompt, command, state helper, manifest, validator, test, and synchronized
documentation changes must agree before rollout.

The separately owned changes in `docs/engineering-agent-governance.md`,
`opencode/agents/engineering-lead.md`, `tests/test_opencode_manager.py`, and
`tools/opencode_manager.py` remain an operational prerequisite, not a canonical
plan dependency because no durable plan identity was supplied. They were
externally committed as `d6e56e67009ca5a4ddda4edc6dc189ea3b3412e8` during this
plan's revision 3. The supplied ERB evidence verifies its intended four-file
scope, but no historical test output was preserved. Before slice 1, require a
clean worktree, reread the then-current `HEAD` and all target files, reconcile
this plan with the committed Lead permission/TODO behavior, rerun the exact
focused manager suite and `just validate-opencode` commands from slice 0 against
current source, and preserve their observed output in the implementation
handoff. Stop on either failure or if reconciliation changes scope, design,
acceptance, or verification materially.

Within execution, `tools/opencode_manager.py` and
`tests/test_opencode_manager.py` have shared ownership across multiple slices and
must remain under one serial owner or strictly sequential bounded assignments.
Root and project-template README/template pairs must be updated together. Agent
and command manifest inventory changes land in their owning slices. No package,
service, live OpenCode configuration, plugin, or external repository is an
implementation dependency.

The planned-work execution lock serializes this plan's direct and delegated
mutations, but it is cooperative rather than a dependency on exclusive repository
use. Unrelated Lead or external work may proceed and must remain outside the
plan's commits. Any overlap with a plan-owned file invalidates the current drift
evidence and stops the Plan Orchestrator for reconciliation.

## Specialist Contributions

- `technical-researcher` established native `todowrite` replacement, order,
  clear, and status behavior; confirmed that OpenCode does not enforce the
  requested five-item, one-active-item, or summary-length limits; and separated
  useful prompt policy from Weave-specific plugin machinery.
- `architecture-strategy-critic` recommended direct Lead plan writes, retirement
  of the Coordinator, retention of Worker and independent ERB boundaries,
  removal of lifecycle-only commands, and preservation of path, delegation, Git,
  destructive-action, validation, and machine-local configuration safeguards.
  The human superseded its direct-Lead ownership and Tapestry-removal
  recommendations by selecting a dedicated Plan Orchestrator and retaining
  `/convert-tapestry-plan`; the boundary and safety recommendations remain useful.

## Risks and Guardrails

- Removing lifecycle metadata must not be replaced with hidden status fields,
  filename conventions, persisted review records, or command aliases.
- Lean plans can become vague if context and acceptance are over-pruned. Keep
  decision-relevant findings and real dependencies while excluding recoverable
  inventories and history.
- The Plan Orchestrator combines plan authorship and planned implementation.
  Bound that authority with series validation, max-plus-one allocation, gap
  non-reuse, collision/exhaustion checks, symlink containment, edit-tool-only
  plan writes, rereading, plan-path Bash denial, evidence-gated checkboxes, and
  Task delegation only to `implementation-worker`.
- The Plan Orchestrator's self-check can be mistaken for independent review.
  Prompts, commands, docs, validator rules, and tests must prohibit ERB review,
  approval, readiness, and sign-off labels for that internal check.
- Legacy detection must fail closed. Never mutate or execute a verbose plan as if
  it were lean, and never infer a dependency from sequence order.
- Pointer state can be stale, corrupt, or attacker-shaped. Keep it minimal,
  ignored, size-bounded, schema-closed, canonical-path checked, hash-bound, and
  disposable; never treat it as authentication or authorship, infer progress, or
  auto-execute after a mismatch. Ignore only the two exact state entries and fail
  on every unsupported `.start-work/` child.
- The planned-work lock can remain after a crash or any uncertain direct or
  delegated mutation. This is the intended safety trade-off: do not expire or
  steal it, and require explicit human confirmation after checking that no Plan
  Orchestrator, Worker, child, or other planned mutator remains. The owner token
  coordinates release but is not a credential, and hostile same-user tampering is
  out of scope.
- The planned-work lock is cooperative, not a filesystem enforcement mechanism.
  It serializes Plan Orchestrator work only; unrelated mutations can occur. Fresh
  under-lock drift checks stop on overlapping owned files, while unrelated work
  continues and stays out of plan commits.
- Crashes can occur after an effect but before checkbox persistence, so exactly
  once cannot be guaranteed. Reconcile acceptance evidence before each resumed
  unchecked TODO, rerun validation for already-satisfied effects, and stop for the
  human when a non-idempotent or external outcome is unknown.
- Tapestry, plan, and repository text can contain traversal, invalid bytes,
  oversized input, sensitive-looking values, or instruction-like prose. Validate
  source root, containment, type, symlinks, the uniform 1 MiB limit, stable
  bounded reads, and strict UTF-8 before hashing, parsing, or agent use. Treat
  content only as data under higher-priority human and repository policy.
- Tapestry-named secondary paths and commands can turn passive content into an
  unsafe operation. Reject unsafe strings before any secondary read, use only
  structured non-shell path operations, and derive commands independently from
  trusted repository evidence. Tests must prove rejected references cause no
  read or execution.
- Optional review must not become an implicit gate through wording such as
  “ready,” “approved,” “signed off,” or “required before execution.”
- `/start-work` defaults to execution for new requests and lean or legacy plan
  paths. The command and prompt must recognize explicit plan-only intent and stop
  before source edits, Worker delegation, checkbox completion, or execution TODO
  state.
- The Lead and ERB could bypass ownership through helpful implementation. Their
  prompts, plan edit permissions, command routing, Task topology, and mutation
  tests must direct planned work to `/start-work`, including complex requests
  classified as needing a durable contract without explicit plan language.
- Lead TODO permission could become a second planned-work path. Preserve its
  generic unplanned coordination use while rejecting Lead plan checkbox, planned
  TODO, state, implementation, and execution authority; Worker and ERB receive no
  explicit TODO allow.
- Native TODO state is session-scoped and replace-all. Never use it as history,
  claim it persists plan truth, or let stale completed items survive a successful
  final report.
- Prompt tests can protect repository instructions but cannot prove runtime
  agent behavior, delegation, cancellation, lock exclusion, or OpenCode UI
  enforcement. Keep claims bounded to checked-in clauses and helper tests.
- Concurrency tests can hang or leak fixtures if they rely on timing. Use bounded
  barriers and joins, explicit child results, parent-side `finally` cleanup, and
  no sleep-based race assertions; a stalled child must fail within the bound and
  leave no process or lock fixture.
- A broad stale-token search can misclassify historical evidence or miss active
  guidance. Keep the validator inventory and obsolete-token set closed and
  diagnostic, enable retained-route mutations before the final inventory scan,
  and exclude durable plan history, fixtures, and historical records explicitly.
- Preserve exact surviving runtime Task IDs, one-level delegation, ERB
  independence, Lead `pbcopy` and configured MCP permissions, Worker denials,
  Git safety, destructive-action stops, and machine-local configuration rules.
- Keep unrelated specialist prompts, unrelated audit/regression/cleanup behavior,
  skill files, dependencies, and live config untouched.
- Atomic commit slices reduce review and recovery risk but require each group to
  be internally consistent. Add its focused tests and validator changes in the
  same slice; never create a follow-up commit solely to repair a knowingly broken
  earlier boundary.

### Execution stop conditions

Stop planned execution if:

- either required current-source prerequisite rerun fails or its output is not
  preserved in the implementation handoff, the worktree is not clean, or the
  then-current `HEAD` and target files have not been reread and reconciled;
- repository drift after execution starts overlaps an owned file or invalidates
  acceptance evidence, or execution would modify `opencode-01`; unrelated drift
  alone must not be folded into plan commits or treated as lock-protected;
- any proposed new-plan shape adds a section or metadata outside the closed
  contract;
- implementation would retain or recreate approval, sign-off, lifecycle state,
  revision transitions, persisted review, normalization, or compatibility
  aliases;
- safe Plan Orchestrator writes require plan-path Bash access, cannot prove
  containment, collide, exhaust a series, or cannot create the destination
  parent with an available edit tool;
- lock-directory acquisition is not the first stateful operation after request
  parsing, any pointer, plan, checkbox, hash, worktree, or execution snapshot was
  read or relied on before acquisition, or post-acquisition evidence was not
  freshly reloaded and revalidated;
- pointer or lock state is malformed, oversized, symlinked, non-regular, corrupt,
  uncertain, outside the repository root, contains unknown or duplicate fields,
  or cannot fail closed; any unsupported `.start-work/` child exists; a held lock
  cannot be acquired immediately; a non-owner would release it; a timestamp would
  drive expiry; or stale-lock cleanup lacks explicit human confirmation that no
  Plan Orchestrator, Worker, child, or planned mutator remains;
- any direct or delegated planned mutation outcome is uncertain but the lock
  would be released, the Worker would acquire/release/mutate lock state, or the
  design would claim to block unrelated filesystem writes or serialize all
  repository work;
- no-path resume lacks a valid matching pointer, a hash mismatch would
  auto-execute, the canonical path and checked/unchecked state are not shown for
  explicit human confirmation before mutation, an explicit path cannot pass full
  canonical-path and self-check validation, or state would store completion,
  prompts, diffs, evidence, absolute user paths, secrets, environment values,
  tokens, or model output;
- any canonical lean or legacy plan is hashed, decoded, parsed, displayed, or
  supplied to an agent before a stable bounded read proves regular non-symlink
  containment, at most 1 MiB, and strict UTF-8; a changing file is accepted; or
  an invalid legacy source would be mutated;
- a legacy plan would be rewritten or executed rather than succeeded;
- the manifest would add a second planning agent, omit the dedicated primary Plan
  Orchestrator, or differ from 23 agents and 6 commands;
- the Plan Orchestrator could delegate to any ID other than
  `implementation-worker`, or the Worker could delegate again;
- the Lead could edit, update, execute, or implement a plan, use TODOs or state for
  planned work, retain a Coordinator or Plan Orchestrator Task edge, or fail to
  route any durable-contract classification to `/start-work`;
- the ERB could execute or implement planned work, become a Task child, regain a
  plan readiness or implementation approval/sign-off decision, persist review
  state, or make review an execution prerequisite;
- the self-check would be described as independent review, approval, readiness,
  sign-off, or ERB evidence;
- `/start-work` cannot distinguish no-path pointer resume, new requests, explicit
  canonical lean paths, legacy paths, conversational updates, default execution,
  and explicit plan-only behavior;
- `/convert-tapestry-plan` would be removed, mutate its source, or execute without
  an explicit human execution request, or would read a source before enforcing
  the `.weave/plans/**` containment, regular-file, symlink, stable 1 MiB, and
  strict UTF-8 boundary;
- a Tapestry-named path, command, test, or symbol would trigger a secondary read
  or command before string and path validation; a command would run merely
  because source content named it; or a control character, newline, shell
  metacharacter, command substitution, sensitive/machine-local path, or
  non-structured argument would be accepted;
- resume would repeat an already-satisfied effect without revalidation, fail to
  repair a partial effect, execute when outcome is unknown or non-idempotent, or
  claim exactly-once behavior instead of stopping for human reconciliation;
- TODO prompt/tests cannot distinguish start, transition, resume,
  blocked/failure, final completion, and clearing, or static prompt tests would
  claim to prove runtime writing, execution, self-checking, delegation,
  cancellation, atomic exclusion, or sidebar behavior;
- Lead or Plan Orchestrator loses its intended flat `todowrite: allow`, Worker or
  ERB gains an explicit allow, Lead/Worker gains `.start-work/**` edit access, or
  effective-action tests allow Lead, Worker, or ERB to mutate resume or lock
  state;
- retained-route mutation tests are absent from slice 3, the complete active
  inventory scan is enabled before authoritative docs migrate in slice 4, its
  inventory or obsolete-token set is open-ended, diagnostics omit the exact file
  and token, or plans/fixtures/history enter the scan;
- contention tests use sleeps or unbounded waits, omit explicit child results or
  parent-side `finally` cleanup, or leave a child process or lock fixture after a
  bounded failure;
- a commit slice knowingly leaves focused tests or `just validate-opencode`
  failing, stages unrelated files, amends or rewrites history, or relies on a
  later repair-only commit;
- the repository-only lint/test/`just validate`/`just validate-opencode` lane
  fails, or `just check` is reported as passing without its maintainer-workstation
  symlink prerequisite;
- a permission change removes/downgrades Lead `pbcopy` or configured MCP access,
  weakens Worker/Git/destructive safeguards, or changes live machine-local
  configuration; or
- root and project-template plan files cannot remain byte-identical.

## Implementation Sequence

### 0. Verify the separately owned prerequisite

**Objective:** Start this plan from a committed, clean, current source baseline
without absorbing the concurrent Lead permission/TODO work into this plan's
history.

**Scope and stable interfaces:** Verify the externally created `d6e56e6` commit
contains exactly the intended changes to `docs/engineering-agent-governance.md`,
`opencode/agents/engineering-lead.md`, `tests/test_opencode_manager.py`, and
`tools/opencode_manager.py` as one atomic work unit. Supplied ERB evidence already
verifies that exact scope, but no historical test output survives. Do not amend,
rewrite, or fold that commit into this plan. Preserve Lead `pbcopy`, configured
MCP access, ordered Git permissions, and generic unplanned-session
`todowrite: allow`.

**Acceptance criteria:**

- The concurrent unit is verified as one atomic commit without amendment or
  history rewriting, and this target plan plus `opencode-01` were not changed by
  that owner.
- The worktree is clean before implementation slice 1 begins.
- The Plan Orchestrator rereads the new `HEAD` and every planned target, compares
  current source to the preserved metadata baseline, and records the observed
  prerequisite command output in the implementation handoff.
- Any material conflict with this revision stops for plan revision and renewed
  review; no implementation slice starts on stale evidence.

**Validation:** From then-current source, before slice 1, run exactly:

```sh
python3 -m unittest discover -s tests -p 'test_opencode_manager.py' -v
just validate-opencode
```

The commits after `d6e56e6` through supplied current `HEAD` change only this
durable plan, so these reruns exercise the same source behavior without an
isolated historical worktree. Preserve their observed output in the
implementation handoff and stop before slice 1 on either failure. This plan
performs no part of the separate four-file implementation.

For slices 1–4, the human requires an ordinary atomic commit after the slice's
focused tests and `just validate-opencode` pass. Stage only that slice's intended
files, inspect the staged diff, record observed validation before moving on, and
do not amend, rewrite history, bypass hooks, or create a later repair-only commit
for a knowingly inconsistent boundary. Keep `tools/opencode_manager.py` and
`tests/test_opencode_manager.py` under serial ownership across all slices.

### 1. Lean plan contract

**Objective:** Establish the closed metadata-free plan format and synchronized
validator contract as a complete first commit.

**Scope and stable interfaces:** Update the root
`docs/implementation-plans/README.md` and `TEMPLATE.md`, their exact
project-template copies, the related authoritative contract guidance needed for
those files, and the corresponding template constants, fixtures, mutation tests,
and byte-sync checks in `tools/opencode_manager.py` and
`tests/test_opencode_manager.py`. Preserve canonical path/series allocation,
legacy succession, Tapestry conversion, and machine-local configuration
boundaries.

**Acceptance criteria:**

- The template contains one title and exactly the authorized sections, with
  numbered checkbox TODOs and no frontmatter or lifecycle/history content.
- Removing a required heading/label or numbered checkbox example fails; adding
  frontmatter, lifecycle metadata, or removed history headings fails.
- Root and project-template README/template pairs are byte-identical and fail
  validation on drift or unsafe symlink substitution.
- Updated guidance keeps legacy plans immutable, retains max-plus-one allocation,
  and does not introduce resume or execution state into a plan.
- Existing non-plan parser, support-file, installer, and Markdown-fence behavior
  remains covered.

**Validation and commit boundary:** Run the focused lean-template and
synchronization tests, the complete focused manager suite,
`just validate-opencode`, and `just validate`. Commit this coherent contract and
its tests together before slice 2.

### 2. Plan Orchestrator and resume infrastructure

**Objective:** Replace the Coordinator with the dedicated primary Plan
Orchestrator and add safe, executable resume and exclusion infrastructure.

**Scope and stable interfaces:** Replace
`opencode/agents/planning-coordinator.md` with
`opencode/agents/plan-orchestrator.md`; update the Lead, ERB, and Worker boundary
clauses; update `.gitignore`; add `tools/start_work_state.py` and
`tests/test_start_work_state.py`; update manifest agent inventory; and add the
permission, Task, state, helper, fixture, and mutation validation required for
this group. Preserve the concurrent Lead TODO/Git work and all unrelated
permissions.

**Acceptance criteria:**

- The manifest still has 23 agents; `plan-orchestrator` is primary, replaces the
  old ID, has plan edit `ask`, plan-path Bash denial, flat `todowrite: allow`, and
  Task access only to `implementation-worker`.
- The Lead retains flat `todowrite: allow` only for generic unplanned-session
  coordination, Lead and Worker explicitly deny `.start-work/**` edits, and
  Worker and ERB have no explicit TODO allow. Deterministic tests reject Lead,
  Worker, or ERB planned-work checkbox, TODO, state, execution, or implementation
  authority.
- Plan Orchestrator and the standard-library helper are the only runtime-state
  writers; Lead, Worker, and ERB have no lock, release, stale-recovery, pointer,
  or resume authority; no broad automatic Bash allow is added to invoke the
  helper. Effective-action tests exercise Plan Orchestrator, Lead, Worker, and ERB
  against `.start-work/resume.json` and lock metadata rather than checking only
  textual permission clauses.
- `.gitignore` contains exactly `/.start-work/resume.json` and
  `/.start-work/lock/` for this workflow, not `/.start-work/`. The helper rejects
  every unsupported state child; `.start-work/history.json` remains Git-visible
  and invalid. Pointer parsing is schema-closed, size-bounded, UTF-8/JSON safe,
  canonical-path checked, and contract-hash bound, with checkbox-only hash
  normalization and no authentication or authorship claim.
- Every explicit or pointer-located canonical lean or legacy plan uses a stable
  bounded read before hash, decode, parse, display, or agent use. Tests accept
  exactly 1 MiB; reject limit plus one, invalid UTF-8, and a file whose size or
  content changes during validation; and leave invalid legacy plans untouched
  with a human-actionable error.
- The cooperative repository-wide planned-work execution lock establishes
  exclusion before any resume or plan read, freshly reloads every input under the
  lock, and fails immediately when held. Its closed bounded metadata has only
  `version`, a 64-lowercase-hex `owner_token`, and canonical `plan_path`; only the
  matching owner releases it; it has no expiry timestamp; no timeout expires or
  steals it; interrupted metadata and corrupt or uncertain state fail closed.
- The Plan Orchestrator holds the lock through direct mutators, Workers, Tasks,
  child processes, timeouts, and cancellation paths. Worker never changes lock
  state. Any uncertain planned mutation retains the lock. Unrelated repository
  work remains possible, while overlapping owned-file drift stops execution for
  reconciliation.
- Executable helper tests cover stale pre-lock snapshots, fresh reload after
  acquisition, exclusive acquisition under a process barrier, owner-only release,
  process termination after acquisition, direct and delegated cancellation,
  effect-before-checkbox crashes, stale-lock handling with explicit human
  confirmation, pointer corruption, plan-path containment, hash mismatch,
  clear-on-completion, deletion-safe explicit-path resume, and no duplicate
  dispatch when current evidence already satisfies a TODO.
- Every process test uses bounded barriers and joins, explicit child result
  reporting, and parent-side `finally` cleanup without sleep-based race
  assertions. A deliberately stalled child fails within the bound and leaves no
  process or lock fixture.
- Prompt-contract tests verify required checked-in self-check, TODO, state,
  release/retention, delegation, and permission clauses and reject contradictions;
  they do not claim to prove runtime agents, delegation, cancellation, atomic
  exclusion, or sidebar behavior.

**Validation and commit boundary:** Run `tests/test_start_work_state.py`, focused
agent/permission/Task/state manager tests, the complete focused manager suite,
and `just validate-opencode`. Commit the agent replacement, helper, ignore rule,
manifest agent inventory, validator changes, and tests as one group before slice
3.

### 3. Command and routing migration

**Objective:** Make `/start-work` the unified planned-work route, retain safe
Tapestry conversion and optional review, and remove lifecycle routes without
leaving stale active guidance.

**Scope and stable interfaces:** Add `opencode/commands/start-work.md`; rewrite
`convert-tapestry-plan.md`, `review-plan.md`, and `review-implementation.md`;
delete `prepare-work.md`, `record-plan-review.md`, `revise-plan.md`,
`approve-plan.md`, `normalize-plan.md`, and `execute-plan.md`; update manifest
command inventory; and make only targeted stale-route/authority edits in
`audit-technical-debt.md`, `investigate-regression.md`, and
`opencode/cleanup/weave-cleanup-checklist.md`. Update the manager, fixtures, and
focused tests for this group. Add retained-route mutation tests now; do not enable
the complete active-workflow inventory scan until authoritative docs migrate in
slice 4. Preserve all unrelated retained-command and cleanup behavior.

**Acceptance criteria:**

- The sorted manifest contains 23 agents and 6 commands. `/start-work` and
  `/convert-tapestry-plan` belong to `plan-orchestrator`; both optional reviews,
  audit, and regression remain ERB-owned; every command remains `subtask: false`.
- `/start-work` distinguishes no-path pointer resume, new requests, explicit
  canonical lean paths, immutable legacy paths with successor allocation,
  conversational updates, default execution, and explicit plan-only behavior.
  It acquires the planned-work lock before reading resume or plan state, freshly
  reloads all evidence, applies the complete pointer lifecycle, and on no-path
  resume shows canonical path plus checkbox state and gets explicit human
  confirmation before any mutation.
- `/convert-tapestry-plan` is plan-only unless execution is explicit, preserves
  its source, and accepts only regular non-symlink valid UTF-8 Markdown under
  `.weave/plans/**` at or below 1 MiB. Absolute, traversal, outside-root,
  directory, special-file, symlink, invalid-encoding, and oversized inputs fail
  before content is read or copied.
- Plan, Tapestry, and repository text is treated as untrusted data. Embedded
  instructions cannot override the human request, `AGENTS.md`, permission maps,
  guardrails, validated scope, or lean plan; sensitive values and machine-local
  configuration are never copied into plans.
- Every Tapestry-named path, command, test, and symbol remains a claim. Synthetic
  absolute, traversal, symlink, oversized, invalid-encoding, sensitive-local,
  newline, semicolon, backtick, and `$()` references are rejected before any
  secondary read or command; spy assertions prove zero secondary reads and zero
  command executions. Validation commands are independently derived from trusted
  repository guidance and source evidence and use structured non-shell handling.
- Audit remediation routes to `/start-work <request>`, regression follow-up routes
  planned changes to `/start-work`, and cleanup guidance uses retained conversion,
  Plan Orchestrator authority, and optional review without deleted lifecycle or
  approval language.
- The Lead's checked-in prompt handles bounded unplanned work directly but routes
  explicit plan paths and every complex durable-contract classification to
  `/start-work <request>`, including requests with no plan terminology.
- Prompt-contract scenarios cover bounded unplanned work, plan-worthy requests
  without plan language, explicit plan paths, unresolved human decisions,
  plan-only behavior, conversion execution opt-in, and optional review. They
  verify required instructions and reject missing or contradictory clauses; they
  do not assert that an agent actually writes, executes, self-checks, delegates,
  or updates native sidebar state.
- Targeted mutation tests for each retained audit, regression, and cleanup route
  fail on its old lifecycle/authority token, pass on the selected `/start-work`
  route, and preserve unrelated behavior. These tests land before the full active
  inventory scan.
- Synthetic negative fixtures cover traversal, symlinks, file type, invalid
  encoding, size, fake sensitive-looking content, instruction-like text, control
  characters, and shell-shaped strings. Machine-enforceable cases execute against
  the helper; content-policy cases verify the prompt contract without any real
  secret.

**Validation and commit boundary:** Run helper trust-boundary tests, focused
command/route/inventory/prompt tests, the complete focused manager suite, and
`just validate-opencode`. Commit command files, manifest command inventory,
targeted retained-route repairs, helper/validator updates, and their tests as one
group before slice 4.

### 4. Final governance reconciliation

**Objective:** Reconcile all remaining active governance and prove one coherent
workflow before rollout.

**Scope and stable interfaces:** Update remaining applicable sections of
`AGENTS.md`, root `README.md`, `docs/engineering-agent-governance.md`, and
`opencode/project-template/AGENTS-plan-workflow-snippet.md`; complete deterministic
stale-reference validation in the manager/tests; reread every changed artifact;
and inspect final status and diffs. Exclude grandfathered durable plans from
active-workflow stale-reference cleanup and keep `opencode-01` byte-identical.

After those authoritative docs migrate, enable one validator-owned active
workflow inventory composed only of these entries:

1. fixed repository files: `.gitignore`, `AGENTS.md`, `README.md`,
   `docs/engineering-agent-governance.md`,
   `docs/implementation-plans/README.md`,
   `docs/implementation-plans/TEMPLATE.md`, and `opencode/manifest.json`;
2. every active `opencode/agents/<name>` and `opencode/commands/<name>` listed by
   the validated post-migration manifest; and
3. every validated manifest `support_files` entry, including the required cleanup
   checklist, merge fragment, and all three project-template workflow files.

The scan's exact obsolete-token set is `planning-coordinator`, `prepare-work`,
`record-plan-review`, `revise-plan`, `approve-plan`, `normalize-plan`,
`execute-plan`, `Ready With Revisions`, `Not Ready`, `Approve With Follow-ups`,
and `Request Changes`. Match command-ID tokens whether they appear as bare IDs,
slash commands, filenames, or paths. Each diagnostic names the exact inventory
file and obsolete token. Explicitly exclude
`docs/implementation-plans/plans/**`, all test fixtures and `tests/**`, Tapestry
source/history, generated artifacts, and historical records; do not replace this
inventory with an unspecified repository-wide or source-wide scan. Separate
structural validation continues to reject approval gates, prohibited aliases,
and out-of-role planned-work state authority where a token scan is insufficient.

**Acceptance criteria:**

- Active docs and definitions agree on the closed plan shape, Plan Orchestrator,
  no-path and explicit `/start-work`, pointer/lock lifecycle, optional advisory
  review, legacy succession, Tapestry trust boundary, TODO ownership, and the
  Lead's complex-request route.
- Deterministic validation rejects active Coordinator authority, deleted
  lifecycle commands, approval gates, prohibited aliases, broad state-helper Bash
  permission, or stale planned-work TODO/state authority outside the Plan
  Orchestrator while allowing the Lead's generic unplanned TODO permission.
- The complete active inventory scan runs only after all listed authoritative
  files migrate. One mutation per obsolete token proves exact file/token
  diagnostics, and exclusion fixtures prove plans, tests, and historical records
  are not scanned.
- Agent/command counts, owners, exact Task edges, plan/state permissions,
  MCP/clipboard access, Worker restrictions, and synchronized templates match
  this plan.
- Prompt-test diagnostics consistently describe checked-in contract coverage,
  not runtime proof. Any unobserved runtime OpenCode, delegation, cancellation,
  or sidebar check is explicitly reported as skipped.
- Each prior atomic slice is internally validated, no unrelated file entered its
  commit, the worktree contains only the intended final-slice changes before its
  commit, and `opencode-01` matches its pre-execution bytes.

**Validation and commit boundary:** Run Final Verification, inspect staged and
baseline-to-current diffs for scope and unsupported claims, and commit the final
governance/docs/validation group atomically. Optional ERB implementation review
remains a human-selected advisory follow-up, not a gate.

## Test Strategy

Use the existing standard-library `unittest` temporary-repository fixtures and
mutation style. Keep tests deterministic and local; do not invoke OpenCode,
network services, MCP servers, live configuration, or Weave.

Required groups are:

- **Lean template:** exact allowed title/section labels, numbered checkboxes,
  forbidden frontmatter/lifecycle/history content, and root/template byte sync.
- **Authority and inventory:** `planning-coordinator` replacement,
  23-agent/6-command manifest, exact primary `plan-orchestrator` ID, selected
  command owners, removed-command absence, and one-level Task graph.
- **Permissions:** Plan Orchestrator broad-ask implementation authority, flat
  `todowrite: allow`, plan edit `ask`, plan-path Bash denial, and Task access only
  to Worker; Lead plan edit `deny`, generic `todowrite: allow`, retained `pbcopy`
  and all MCP prefixes, retained plan-path Bash denial, no planning Task edge,
  and Worker Git/destructive/plan/delegation denials. Lead and Worker state edits
  are denied through repository-relative `.start-work/**`, and Worker/ERB have no
  explicit TODO allow. Effective-action tests exercise resume and lock metadata
  paths for all four roles and prove only Plan Orchestrator/helper writes.
- **Plan operations:** series validation, max-plus-one with gap non-reuse,
  exhaustion/collision stops, absent or uncreatable destination-parent handling,
  symlink/containment checks, rereading, conversational lean updates, legacy
  succession, and lean Tapestry output. Explicit and pointer-located lean and
  legacy fixtures accept exactly 1 MiB, reject limit plus one and invalid UTF-8,
  and fail closed when file size or content changes during validation.
- **Pointer and canonical path:** exact closed schema, pointer-size limit, unknown
  field/version/hash rejection, relative canonical lean-plan containment,
  checkbox-only SHA-256 normalization, mismatch stop, corruption handling,
  plan-only pointer write, retention on pause/blocker/failure/cancellation,
  matching clear-on-completion, deletion-safe explicit replacement, rejection of
  unsupported state children, no authentication claim, and no-path display plus
  explicit-human-confirmation ordering before mutation.
- **Planned-work execution lock:** first-stateful-operation ordering, stale
  pre-lock snapshot rejection, fresh under-lock reload, closed bounded metadata,
  valid 64-hex owner token, concurrent acquisition under a process barrier,
  immediate held-lock failure, matching-owner release, interrupted acquisition,
  abrupt process termination, direct and delegated cancellation retention, no
  timeout stealing or expiry timestamp, explicit-human stale-lock recovery, and
  corrupt-state failure. Effective tests also prove Worker has no lock operation,
  unrelated external writes are not claimed to be blocked, and overlapping drift
  stops plan work.
- **Resume reconciliation and fault injection:** deterministic barriers cover an
  effect-before-checkbox crash, already-satisfied evidence with required
  revalidation and no duplicate dispatch, partial-effect repair, definitely
  unapplied execution, and unknown/non-idempotent human stop. Assertions describe
  at-least-once risk rather than exactly-once behavior.
- **Tapestry trust boundary:** `.weave/plans/**` containment, regular Markdown
  file, non-symlink components, stable 1 MiB maximum, strict UTF-8, source
  preservation, and rejection of absolute, traversal, outside-root, directory,
  special-file, symlink, invalid-encoding, and oversized fixtures before
  read/copy. Secondary-reference spies cover absolute, traversal, symlink,
  oversized, invalid-encoding, sensitive-local, newline, semicolon, backtick,
  `$()`, control-character, and shell-metacharacter references and prove no
  secondary read or command execution.
- **Start-work prompt contract:** no-path resume, new request, lean plan, legacy
  successor, requested conversational changes, default execution, explicit
  plan-only stop, direct implementation, bounded Worker delegation, integration,
  validation, completion reporting, and lock/pointer ordering clauses.
- **Self-check semantics:** closed-shape and evidence checks, unresolved-decision
  stop, and forbidden ERB review/approval/readiness/sign-off descriptions.
- **Review semantics:** all three advice levels are defined out-of-band; plan and
  implementation reviews remain optional/read-only and emit no readiness,
  approval, sign-off, persistence, or execution gate; ERB follow-up uses
  `/start-work` without making review mandatory.
- **Role guardrails:** prompt scenarios distinguish bounded unplanned Lead work,
  plan-worthy requests without plan language, explicit plan paths, and unresolved
  human decisions. Mutations fail when Lead or ERB can implement/execute a plan,
  Lead can write/update one or use TODO/state for planned work, either bypasses
  the Plan Orchestrator, or Worker gains plan/sidebar/state authority.
- **Execution/TODO behavior:** start, transition, resume, blocked/failure,
  evidence-gated checkbox completion, final completed-only write, and final
  clear, including count/order/status/number/length mutations and no-path
  confirmation before the first planned sidebar write.
- **Untrusted content:** synthetic fake-sensitive and instruction-like fixtures
  verify the checked-in prohibition on copying sensitive data or obeying embedded
  instructions. No fixture contains a real secret.
- **Stale-route scope:** retained audit, regression, and cleanup fixtures require
  the new targeted routes while mutation and snapshot coverage preserves their
  unrelated behavior in slice 3. Slice 4 then enables the closed active-workflow
  inventory and exact obsolete-token set, with exact file/token diagnostics and
  explicit plan/test/history exclusion coverage.
- **Compatibility:** retained support-file, frontmatter-parser, manifest,
  Markdown-fence, setup, verify, uninstall, and unrelated command behavior.

Executable helper tests prove only the helper behavior they invoke. Prompt tests
show that checked-in guidance contains required clauses and rejects contradictory
or missing clauses; they do not prove that a runtime agent writes, executes,
self-checks, delegates, handles cancellation, acquires a lock, or updates native
sidebar state. Report runtime OpenCode, delegation, cancellation, and sidebar
checks as skipped unless directly observed.

All contention and fault tests use bounded barrier and join timeouts, explicit
child results, and parent-side `finally` cleanup. They use no sleep as a race
oracle. A deliberately stalled child must fail within the configured bound and
leave neither a live process nor a lock fixture.

## Migration, Compatibility, and Recovery

This is an intentional workflow break with no compatibility aliases. Existing
plan files remain where they are and reserve their sequence numbers. Create a
lean successor only when a legacy plan needs changes or execution; never rewrite
or execute the predecessor. Newly converted Tapestry sources follow the same
allocation rules and remain intact after conversion.

The runtime ID changes from `planning-coordinator` to `plan-orchestrator`; no
alias or forwarding Task edge remains. The old role was a subagent, while the new
role is a primary selected directly by `/start-work` and
`/convert-tapestry-plan`. Existing invocations of deleted commands fail by
design, and users move to `/start-work` rather than compatibility shims.

Only `/.start-work/resume.json` and `/.start-work/lock/` are ignored disposable
local state, not tracked migration artifacts; the parent is not broadly ignored.
Any unsupported child remains visible to Git and makes helper validation fail. A
missing pointer means there is no no-path resume; a corrupt or mismatched pointer
stops; and a stale lock requires explicit human confirmation after verifying that
no Plan Orchestrator, Worker, child process, or other planned mutator remains.
Recovery may remove only confirmed-stale local state through the helper's guarded
operation. No timeout or timestamp expires a lock, and the Worker, Lead, and ERB
have no recovery authority. Never derive progress or authorship from the pointer
or reconstruct it from repository scans.

After a crash, cancellation, or process loss, keep the lock when any planned
effect is uncertain. Once the human confirms stale recovery, the next owner must
reconcile each first unchecked TODO against current acceptance evidence before
dispatch. Already-satisfied effects are revalidated and checked without repeat;
partial effects are repaired; definitely unapplied work may run; unknown or
non-idempotent effects stop. This recovery contract acknowledges at-least-once
external-effect risk and does not promise exactly-once execution.

Roll out agents, commands, helper, manifest, validator/tests, docs, and
project-template copies through the four validation-passing atomic commits, but
do not restart OpenCode or use the new planned workflow between slices. The
linked definitions take effect after restart, so restart only after the final
coherent state passes all checks. Do not modify live configuration. Capture the
pre-edit bytes of tracked `opencode-01` and verify the same bytes before handoff.

If a slice fails validation before commit, stop and correct that slice without
staging unrelated files. If a committed slice is later found unsafe, stop rollout
and use only authorized ordinary new recovery commits—never amend or rewrite
history—to restore the last coherent validated workflow. Do not restore ceremony
through aliases or alter a legacy plan. If definitions were already loaded,
restore a coherent validated repository state and restart OpenCode again. No
database, persisted review record, plugin state, credential, or external service
needs migration or rollback.

## Documentation Impact

- `AGENTS.md` and `README.md`: replace Coordinator/lifecycle and direct-Lead plan
  language with the dedicated Plan Orchestrator, `/start-work`, optional review,
  Lead/ERB routing guardrails, and legacy succession.
- `docs/implementation-plans/{README,TEMPLATE}.md`: become the authoritative
  closed contract and exact starter shape.
- `docs/engineering-agent-governance.md`: update roles, Task topology, command
  ownership, review advice, self-check semantics, execution, and
  Plan-Orchestrator/Lead/Worker/ERB TODO/state boundaries.
- `opencode/project-template/`: mirror portable workflow guidance and keep both
  plan files byte-identical to root copies.
- Agent and command Markdown: implement Plan Orchestrator ownership, Lead/ERB
  `/start-work` routes, complex-request classification, optional advisory review,
  legacy handling, bounded canonical and Tapestry input trust, untrusted secondary
  references, pointer lifecycle, the cooperative planned-work-only lock, resume
  reconciliation, and the native TODO prompt contract.
- `.gitignore`, `tools/start_work_state.py`, and
  `tests/test_start_work_state.py`: define the two exact ignored runtime-state
  entries and executable pointer, path, input, fault-recovery, and planned-work
  lock behavior.
- `audit-technical-debt.md`, `investigate-regression.md`, and the Weave cleanup
  checklist: repair only stale lifecycle routes and authority language.
- `tools/opencode_manager.py` and `tests/test_opencode_manager.py`: own the exact
  active-workflow inventory, obsolete-token diagnostics, retained-route mutation
  coverage, effective state-action tests, and the repository-only integration
  contract.

`docs/skill-taxonomy.md` and `docs/cross-reference-map.md` require no edit: this
work changes OpenCode runtime governance, not first-party skill inventory or
skill routing.

## Final Verification

From the repository root, first run the focused changed-surface checks:

```sh
python3 -m unittest discover -s tests -p 'test_start_work_state.py' -v
python3 -m unittest discover -s tests -p 'test_opencode_manager.py' -v
```

Then run this mandatory repository-only integration lane, which does not depend
on machine-global installation state:

```sh
just lint
just test
just validate
just validate-opencode
git diff --check
```

Run `just check` separately only on a configured maintainer workstation where
the repository-owned `~/.agents/skills` symlink prerequisite exists. If it is
absent, do not fail the repository-only lane; report exactly
`skipped: just check — ~/.agents/skills repository symlink prerequisite is absent`.

Then:

- re-read root and project-template plan README/template files and confirm the
  validator reports byte equality;
- inspect the manifest and definition directories for exactly 23 agents and 6
  commands, with `plan-orchestrator` present, `planning-coordinator` absent, and
  no retired command, split-command replacement, or alias;
- inspect deterministic stale-reference results over only the fixed active files,
  validated manifest-listed agents/commands, and manifest support files defined
  in slice 4; confirm every obsolete-token diagnostic names its exact file and
  token and that durable plans, tests/fixtures, Tapestry history, and historical
  records remain excluded;
- inspect Plan-Orchestrator/Lead/ERB/Worker permission ordering and confirm plan
  edits, state edits, plan Bash denial, both intended `todowrite` allows, absence
  of Worker/ERB TODO allows, `pbcopy`, MCP, Git, destructive, and Task rules match
  this plan; verify effective state actions on `.start-work/resume.json` and lock
  metadata, not only textual rules;
- inspect executable helper evidence for first-stateful lock ordering, stale
  pre-lock rejection, fresh reload, closed lock metadata, bounded barrier
  exclusion, matching-owner release, direct/delegated termination and
  cancellation retention, stale-lock confirmation, pointer
  corruption/containment/hash/clear/deletion behavior, 1 MiB/UTF-8 changing-file
  boundaries, effect-before-checkbox recovery, and satisfied-evidence duplicate
  suppression;
- inspect secondary-reference spy evidence for every required unsafe path and
  shell-shaped string and confirm zero secondary reads and zero command
  executions;
- inspect prompt-contract evidence for every `/start-work` branch, plan-only stop,
  conversion execution opt-in, self-check distinction, Lead complex-request and
  ERB routing, untrusted content, and TODO transitions; verify diagnostics claim
  only checked-in instruction coverage;
- inspect the four implementation commits and their recorded focused-test plus
  `just validate-opencode` evidence; confirm each commit contains one intended
  logical group, no unrelated files, no amendment/history rewrite, and no
  repair-only follow-up for a knowingly broken boundary;
- confirm the slice-0 implementation handoff contains observed output from the
  current-source focused manager rerun and `just validate-opencode` and that both
  passed before slice 1;
- compare the final bytes of
  `docs/implementation-plans/plans/opencode/01-agent-definitions-improvement-program.md`
  with the pre-edit capture and confirm the implementation made no write to that
  file, live config, credentials, dependencies, skills, unrelated specialist
  prompts, or unrelated audit/regression/cleanup behavior; and
- report target-machine OpenCode, runtime agent behavior, delegation,
  cancellation, restart, and sidebar checks as skipped unless each was actually
  observed.

## Open Decisions

None. The human fixed the lean section set, dedicated Plan Orchestrator,
`/start-work` behavior, Lead/ERB routing boundaries, optional review model,
retained Tapestry conversion, legacy successor behavior, native TODO window,
pointer model, cooperative repository-wide planned-work execution lock, unrelated
work and overlapping-drift boundary, atomic commit slices, and modified dual-TODO
permission boundary. The lock serializes Plan Orchestrator sessions and all
direct or delegated implementation for their plans; it is not a general
repository mutation lock and grants Lead, ERB, and Worker no state authority.

## ERB Review History

plan_path: docs/implementation-plans/plans/opencode/02-simplify-plan-workflow.md
plan_id: opencode-02
revision: 2
baseline_commit: 9bd28e3a15c237e1fb4cf6e1996da36b687db5e8
decision: ready-with-revisions
reviewed_at: 2026-07-14T19:20:00-04:00
findings: Required revisions 1-8 in this Board record.
next_command: /record-plan-review docs/implementation-plans/plans/opencode/02-simplify-plan-workflow.md

plan_path: docs/implementation-plans/plans/opencode/02-simplify-plan-workflow.md
plan_id: opencode-02
revision: 3
baseline_commit: 9bd28e3a15c237e1fb4cf6e1996da36b687db5e8
decision: ready-with-revisions
reviewed_at: 2026-07-14T19:45:00-04:00
findings: Required revisions R3-1 through R3-4 in this Board record.
next_command: /record-plan-review docs/implementation-plans/plans/opencode/02-simplify-plan-workflow.md

## Approval History

None.

## Amendments

### Revision 2 — 2026-07-14

- Recorded the human-selected primary `plan-orchestrator` and unified
  `/start-work` architecture, moved planned execution and TODO ownership from the
  Lead, and added Lead/ERB routing guardrails. No ERB review or approval record
  was added.

### Revision 3 — 2026-07-14

- Applied all eight findings from the persisted revision-2 ERB
  `ready-with-revisions` record: targeted stale-route repairs; the selected
  pointer-plus-repository-lock design; plan/Tapestry trust boundaries; prompt-test
  claim limits; complex-request routing; current tracked/source-drift evidence;
  and validation-passing atomic implementation slices.
- Recorded the finding-7 human modification: preserve generic unplanned-session
  `todowrite: allow` for the Lead and add it for the Plan Orchestrator, while the
  Plan Orchestrator alone owns planned-work TODOs, checkboxes, resume state, and
  execution; Worker and ERB receive no explicit allow.
- Added the separately owned four-file concurrent work unit as a pre-execution
  prerequisite. It was externally committed as `d6e56e6` during this revision
  without Coordinator edits; execution still requires scope/validation evidence,
  a clean worktree, then-current-HEAD reconciliation, and fresh
  baseline-to-current review evidence. Review and approval fields were reset for
  material revision; no approval was added.

### Revision 4 — 2026-07-14

- Applied R3-1 through R3-4 from the persisted revision-3 ERB
  `ready-with-revisions` record: pre-read planned-work lock ordering and fresh
  under-lock validation; narrow ignored state and closed lock metadata; uniform
  canonical-plan and secondary-reference trust boundaries; current-source
  prerequisite reruns; deterministic active-inventory validation; repository-only
  integration checks; and bounded fault/contender tests.
- Recorded the human-selected lock modification: one cooperative repository-wide
  planned-work execution lock serializes Plan Orchestrator sessions and their
  direct or delegated plan implementation, while unrelated Lead and external
  work may continue. The Worker never changes lock state, overlapping owned-file
  drift stops for reconciliation, and the design makes no filesystem-enforcement
  or exactly-once claim.
- Preserved the revision-2 and revision-3 ERB records and amendments, retained the
  implementation baseline and source-drift provenance, and reset this material
  revision to draft/pending with all current review and approval fields clear. No
  approval was added.

## Execution Record

None.
