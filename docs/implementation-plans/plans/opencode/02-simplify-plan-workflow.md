---
plan_id: opencode-02
series: opencode
sequence: 2
title: Simplify the OpenCode Plan Workflow
status: draft
revision: 6
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
updated: 2026-07-15
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
repository-owned standard-library helper at
`opencode/workflow-tools/start_work_state.py` owns that pointer and one
cooperative, repository-wide planned-work execution lock. OpenCode setup exposes
the helper only through the managed
`~/.config/opencode/workflow-tools -> <checkout>/opencode/workflow-tools` link;
runtime starts in the active OpenCode workspace and passes only literal `.` as
`--repo-root`, and no target-local helper is discovered or executed. Python runs
with isolated startup so workspace modules, user site packages, and Python
environment variables cannot participate in helper import startup.

Setup and every related dry-run, verification, doctor, uninstall, rollback, or
restoration operation fail closed unless the configured machine-local root and
all mutable ancestors are real, stable, non-symlink directories outside source
checkouts and active target workspaces. Mutations remain bound to the validated
configuration-root directory descriptor and exact device/inode identity rather
than following a substituted path.

`/start-work`, `/convert-tapestry-plan`, and equivalent ordinary Plan
Orchestrator conversation share one transition protocol. After parsing the human
route intent without parsing a human-supplied plan or Tapestry locator, the route
calls the trusted installed helper with a fixed allowlisted operation and the
literal active-workspace root. The helper proves that `.` is exactly the active
OpenCode workspace root and, when needed, safely bootstraps an empty
`.start-work` parent before atomically creating `.start-work/lock` as the
exclusion point. It generates a cooperative owner token and atomically installs
provisional `owner.json` metadata with `plan_path: null` before acquisition can
succeed. Only then may the route parse and validate a locator or load pointer,
source, allocation inventory, plan bytes and hash, checkboxes, worktree, or
execution evidence. The matching owner finalizes metadata with the canonical
plan path, and the lock is held through plan-only writes and pointer updates as
well as direct or delegated execution. Read-only self-explanation that performs
no target mutation does not acquire it.

The lock serializes Plan Orchestrator sessions and all direct or delegated
implementation performed for their plans; it does not block unrelated
filesystem writes or serialize all repository mutation. Fresh under-lock
evidence remains authoritative, only accepted plan checkboxes establish
completion, and overlapping concurrent changes stop for reconciliation.

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
- Require `/start-work`, `/convert-tapestry-plan`, and equivalent ordinary Plan
  Orchestrator conversation to use one shared state-transition protocol, with
  read-only self-explanation exempt only when it performs no plan, state, or
  repository mutation.
- Invoke only the trusted installed
  `~/.config/opencode/workflow-tools/start_work_state.py` with isolated Python,
  a fixed allowlisted operation literal, and literal `--repo-root .` from the
  active OpenCode workspace root. Manage its repository-owned source directory
  as a third paired OpenCode setup link and never accept an arbitrary runtime
  target path or discover or execute a target-local helper.
- Treat human requests, instructions, plan paths, and Tapestry locators only as
  data after complete provisional child-lock acquisition; never splice them into
  helper-launch shell text. Validate any machine-derived owner token or canonical
  plan path against its closed ASCII grammar before a later helper/API operation
  and preserve it as one argument.
- Bind setup, dry-run, verify, doctor, uninstall, rollback, and restoration to a
  fail-closed machine-local configuration root: all mutable ancestors through
  `~/.config/opencode` are stable real directories outside source checkouts and
  target workspaces, and link mutations are descriptor-relative under the same
  revalidated root identity.
- Permit only exact active-workspace-root validation and safe empty-parent
  bootstrap before atomically creating `.start-work/lock`; install complete
  provisional ownership, then freshly load and validate pointer, source,
  allocation inventory, exact plan bytes and hash, checkbox state, worktree, and
  execution evidence required by the route.
- Install bounded provisional lock metadata atomically before returning
  acquisition success, then permit only the matching owner token to atomically
  finalize `plan_path` from `null` to the validated canonical repository-relative
  plan path. Treat every missing, partial, malformed, or unknown-field
  `owner.json` in an existing child lock as stale/corrupt state requiring guarded
  human recovery.
- Bootstrap the target's two exact narrow `.gitignore` entries after complete
  provisional child-lock acquisition and before pointer persistence, using
  ordinary edit tools and failing closed on symlinked, unsafe, broad, or
  conflicting ignore policy.
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
- Add a target-repository executable helper, arbitrary helper discovery, a custom
  OpenCode tool, a copied helper install, or a broad Bash allow for helper
  invocation. The only executable source is the trusted checkout's fixed
  `opencode/workflow-tools/start_work_state.py`, reached through its managed
  whole-directory link and normal runtime approval.
- Accept or interpolate a human-provided runtime repository target, plan path,
  Tapestry locator, request, instruction, or repository text in a helper-launch
  shell string; concatenate helper commands; or add redirection, pipes, command
  substitution, or extra shell operations to the fixed invocation.
- Add plan lifecycle state, full execution history, a last-completed TODO cache,
  prompts, diffs, or evidence payloads to runtime resume state.
- Add a general repository mutation lock, claim exactly-once execution, suppress
  unrelated Lead or external work, or grant the Lead, ERB, or Worker lock or
  resume-state authority.
- Add timeout expiry or lock stealing, timestamps used for expiry, or same-OS-user
  hostile-process tamper resistance to the cooperative coordination mechanism.
- Treat an existing child lock with missing or corrupt provisional metadata as
  unheld, auto-release a provisional lock after any mutation or uncertain
  outcome, or permit a nonmatching owner to finalize or release it.
- Treat creation of an empty `.start-work` parent as exclusion, read target plan
  or state content before complete provisional child-lock acquisition,
  recursively create arbitrary state parents, or rewrite a target's unrelated
  `.gitignore` policy during project-template bootstrap or first use.
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
- `tools/opencode_manager.py` currently models only `agents` and `commands` as
  the two managed definition kinds. Its setup, verification, rollback, uninstall,
  CLI help, and tests describe that pair, while the manifest schema contains only
  `agents`, `commands`, and `support_files`. This plan extends that existing
  whole-directory-link model with one explicit runtime-helper inventory and one
  `workflow-tools` link rather than adding a custom OpenCode tool. The current
  setup evidence does not establish stable no-symlink ownership for every
  mutable configuration-root ancestor or descriptor-relative mutation across
  setup, dry-run, verify, doctor, uninstall, rollback, and restoration; revision
  6 makes those controls and their substitution tests mandatory.
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
  advanced `HEAD` to `d6e56e67009ca5a4ddda4edc6dc189ea3b3412e8`, the
  revision-3 plan commit advanced it to
  `f8fa6b0c6608b81b987db9aad01c4b50c28cf4cf`, and the revision-4 plan commit
  advanced it to `34da83afbb5807689166590447bfab2a283eaf9c`. The revision-5
  plan commit then advanced `HEAD` to
  `dfc6c7f7306ca6db1e458a807dd42730a10d6d9f`. The worktree was clean at the
  revision-5 review. At revision-6 intake, `HEAD` still matched `dfc6c7f` and the
  only worktree change was the subsequently persisted matching revision-5 ERB
  record in this plan. Supplied equivalent range evidence covers the complete
  baseline-to-HEAD interval: the planning commits changed only durable plan
  files, `d6e56e6` changed exactly the four source files named below, and
  `f8fa6b0`, `34da83a`, and `dfc6c7f` each changed only this plan. Review and
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
- No checked-in `opencode/workflow-tools/start_work_state.py`,
  `tests/test_start_work_state.py`, or tracked `/.start-work/` runtime-state
  contract exists in the observed source. There is no `opencode/workflow-tools/`
  directory or runtime-helper manifest key. Current setup manages only
  `~/.config/opencode/agents` and `~/.config/opencode/commands`. No runtime-helper
  tests exist yet, and no machine-local configuration or secrets were inspected
  for revision 6.
- The specialist inspection supplied by the human reports that
  `just validate-opencode` and all 58 focused OpenCode manager tests passed before
  initial planning. That is historical prompt-contract evidence, not current
  runtime proof or preserved evidence for `d6e56e6`; this Coordinator did not
  rerun implementation checks. Because all later commits through `dfc6c7f` affect
  only durable plans, rerunning the focused manager suite and
  `just validate-opencode` at then-current `HEAD` before slice 1 validates the
  same source behavior.
- The latest persisted ERB record exactly matches this path, `opencode-02`,
  revision 5, and baseline, and records `ready-with-revisions` at
  `2026-07-14T22:40:00-04:00`. It follows the preserved revision-2 through
  revision-4 records. No approval exists. The supplied `change-verifier` reports
  R4-1 through R4-3 closed and revision 5 otherwise execution-ready. The supplied
  `security-critic` identifies the shell-safe helper invocation, machine-local
  configuration-root ownership, and provisional child-lock ownership gaps now
  addressed as R5-1 through R5-3. No required human product or workflow decision
  remains.

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

## Revision 5 Finding Dispositions

1. **R4-1 accepted — one shared state-transition protocol.** `/start-work`,
   `/convert-tapestry-plan`, and equivalent ordinary Plan Orchestrator
   conversation use the fixed trusted installed helper, complete child-lock
   acquisition, and only then freshly load the route's pointer, source,
   allocation, plan, checkbox, worktree, and execution evidence. Revision 6
   further requires that human locators are not parsed or passed at launch and
   that provisional ownership completes before those reads. Plan-only writes and
   pointer updates remain under the same lock as direct or delegated execution.
   Read-only self-explanation with no target mutation is the only exemption.
2. **R4-2 accepted with a concrete trusted distribution model.** Place
   the sole helper source at `opencode/workflow-tools/start_work_state.py`, add an
   exact manifest runtime-helper inventory containing only
   `workflow-tools/start_work_state.py`, and manage
   `~/.config/opencode/workflow-tools` as a third paired whole-directory link
   beside `agents` and `commands`. All routes invoke only that installed fixed
   path under normal runtime approval. Revision 6 supersedes the earlier
   arbitrary-target invocation mechanics with isolated Python and literal
   `--repo-root .` from the active workspace. First planned use adds the two exact
   narrow target ignore entries through ordinary edit tools after child-lock
   acquisition; target-local helpers and unsafe or conflicting ignore policy fail
   closed.
3. **R4-3 accepted — safe parent bootstrap and child-lock exclusion.** Before
   exclusion, permit only fixed route selection and helper launch, minimum active
   canonical regular workspace-root validation, and non-recursive creation or
   revalidation of an empty real `.start-work` parent. Atomic
   `.start-work/lock` creation is the actual exclusion point and first
   exclusion-protected mutation. Revision 6 requires immediate provisional
   metadata before acquisition success. All target plan, state, source,
   allocation, worktree, and execution reads follow that acquisition. Empty
   interruption residue is reusable; symlinked or non-directory parents,
   unsupported children, corrupt state, and losing race contenders fail closed.

## Revision 6 Finding Dispositions

1. **R5-1 accepted — fixed isolated active-workspace helper invocation.** Every
   runtime route starts at the active OpenCode workspace root and uses exactly
   `python3 -I "$HOME/.config/opencode/workflow-tools/start_work_state.py"
   <literal-operation> --repo-root .`, where the operation is a checked-in
   allowlisted literal and `.` is one literal argument. Human-derived targets,
   locators, requests, instructions, and repository text never enter shell
   construction. The helper proves `.` is exactly the active workspace root;
   rejects nested, mismatched, aliased, symlinked, unrelated, or alternate roots;
   and remains standard-library-only. Any later machine-derived token or plan
   path is grammar-validated and preserved as one argument, preferably through
   structured API/argv tests. Runtime approval remains required.
2. **R5-2 accepted — bound machine-local configuration-root ownership.** Setup,
   dry-run, verify, doctor, uninstall, rollback, and restoration validate every
   mutable path component through `~/.config/opencode` as a stable real directory
   outside source checkouts and target workspaces. A supported missing final
   `opencode` directory is created only beneath a validated safe parent, then
   opened and bound. Every link mutation and rollback is descriptor-relative with
   no-follow behavior where supported, root/device/inode identity is revalidated
   before every mutation position and success report, destination ownership is
   re-lstat'd immediately before mutation, and partial rollback touches only
   transaction-proven links under the still-bound root.
3. **R5-3 accepted — provisional then final child-lock ownership.** Immediately
   after atomic child-directory creation, the helper generates the 64-lowercase-
   hex token and atomically writes bounded `.start-work/lock/owner.json` with
   `plan_path: null`; it returns acquisition success only after that write.
   Missing, partial, malformed, or unknown-field metadata in an existing child
   lock is stale/corrupt and requires guarded human recovery. After under-lock
   locator/allocation/source/plan validation determines the canonical plan path,
   only the matching owner may atomically finalize the same record. Exact
   duplicate finalization may be idempotent; token/path conflicts fail closed.
   Known-clean provisional release is allowed only before any plan, ignore,
   pointer, checkbox, sidebar, delegation, or implementation mutation and after
   proving no child remains; every uncertain or later outcome retains the lock.

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
spelling for a plan. Except for exact active-workspace-root validation and
optional empty state-parent bootstrap, all source, plan-root, destination, and
allocation checks occur freshly after complete provisional shared child-lock
acquisition.

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

### Trusted runtime helper, resume pointer, and planned-work lock

Keep the sole helper source in the trusted OpenCode checkout at
`opencode/workflow-tools/start_work_state.py`, with focused executable tests in
`tests/test_start_work_state.py`. Add a manifest `runtime_helpers` inventory
containing exactly `workflow-tools/start_work_state.py`; it is separate from
`agents`, `commands`, and `support_files` and is not an OpenCode custom tool.
Validation requires that exact regular, non-symlink source inside the trusted
checkout and rejects extra helper entries, unexpected helper files, symlinked
source components, or source resolution outside `opencode/workflow-tools/`.

Extend OpenCode setup's existing all-or-nothing whole-directory link set to:

```text
~/.config/opencode/agents         -> <checkout>/opencode/agents
~/.config/opencode/commands       -> <checkout>/opencode/commands
~/.config/opencode/workflow-tools -> <checkout>/opencode/workflow-tools
```

Before setup, dry-run, verify, doctor, uninstall, rollback, restoration, or any
success report, derive the machine-local destination from the configured home or
configuration base and validate every mutable path component through
`~/.config/opencode`. Each existing component must be a real directory, never a
symlink, and its resolved identity must remain outside this repository checkout,
every other source checkout, and the active target workspace. Reject a symlinked,
non-directory, aliased, repository-contained, target-contained, identity-changing,
or missing-with-unsafe-parent root before any destination mutation. Do not assume
that spelling `~/.config/opencode` establishes ownership.

If the final `opencode` directory is absent and creation is supported, first
apply the same ownership, containment, no-symlink, and stable-identity checks to
all existing parents, create only that final directory, then open and bind it
before considering a link mutation. Hold a directory descriptor for the validated
configuration root after preflight. Create, remove, roll back, and restore links
relative to that descriptor with no-follow semantics where the platform supports
them. Record the root path plus device and inode, and revalidate both path identity
and descriptor identity before every possible mutation position and immediately
before reporting success.

Setup preflights all three destinations and never overwrites a real file,
directory, broken or foreign link, or mismatched destination. Immediately before
each mutation, re-lstat and ownership-check the `agents`, `commands`, and
`workflow-tools` entry relative to the still-bound root. Any root or destination
substitution, alias, disappearance, or identity mismatch stops the transaction.
Rollback or restoration may touch only an entry proven to be the exact link
created or removed by that transaction beneath the same bound root; it never
follows a moved root or recreates/removes through a substituted parent. Report
partial rollback precisely and leave unrelated sentinels untouched.

Verification requires every destination to resolve to its exact expected checkout
source and the manifested helper to remain a regular non-symlink file visible
through the `workflow-tools` link. Uninstall removes the all-three set only when
every link still has exact managed ownership under the bound root; it leaves
foreign or target-repository content untouched. Helper source changes take effect
through the managed link without copying files into the config directory or a
target repository.

Every mutating Plan Orchestrator route starts from the active OpenCode repository
workspace root and invokes only this fixed shell form:

```text
python3 -I "$HOME/.config/opencode/workflow-tools/start_work_state.py" <literal-operation> --repo-root .
```

`<literal-operation>` denotes one fixed allowlisted operation selected by the
checked-in route, never user or repository content. The runtime Bash prompt must
prescribe the exact quoting above and prohibit concatenation, redirection, pipes,
substitution, and extra shell operations. It must pass literal `.` as one
`--repo-root` argument and never accept or interpolate a human-provided target,
plan path, Tapestry locator, request, instruction, or repository string. The
invocation remains subject to normal runtime approval; do not add a broad Bash
allow.

Python isolated startup (`-I`) prevents current-workspace imports, user site
packages, and Python environment variables from participating in helper startup;
the helper remains standard-library-only. It resolves `.` and proves that the
result is exactly the active OpenCode workspace root, not a nested directory,
symlinked or aliased spelling, unrelated path, mismatched root, or alternate
target. Store no absolute path in pointer or lock metadata. Never invoke
`tools/start_work_state.py`, a helper found relative to the active workspace, the
checkout source path relative to that workspace, or any same-name workspace-local
file.

If a later fixed-literal helper operation carries a machine-derived owner token
or canonical plan path, first validate the value against exactly 64 lowercase
hex characters or the canonical repository-relative plan-path grammar,
respectively, and preserve it as one argv element. Prefer direct helper/API tests
that construct `subprocess` argv arrays. No token, path, user content, target
absolute path, or repository text may enter shell interpolation. Human-supplied
plan and Tapestry locators are parsed and validated only after complete
provisional child-lock acquisition through edit/read/helper-safe structured
operations; they are never helper-launch arguments.

The target repository uses exactly these two narrow local-state ignore entries:

```text
/.start-work/resume.json
/.start-work/lock/
```

Do not ignore `/.start-work/` broadly. Project-template guidance documents the
two lines but project bootstrap does not create or overwrite a target
`.gitignore`. On first planned-work use, after complete provisional child-lock
acquisition and before pointer persistence, the Plan Orchestrator verifies that a
regular, non-symlink target `.gitignore` contains each exact line once and no
broad or conflicting custom `.start-work` rule. If the file is safely absent or
only the required lines are missing, add the exact lines with ordinary edit tools
as an explicit plan-owned infrastructure change and report them in plan scope. If
the file or any component is symlinked or unsafe, or ignore policy is broad,
ambiguous, or conflicting, stop for the human rather than rewriting unrelated
policy. The helper refuses pointer persistence until this contract is valid. A
plan-only route may create or update the lean plan and these exact ignore lines,
but performs no implementation work.

The helper rejects every unsupported file or directory below `.start-work/`; for
example, `.start-work/history.json` remains visible to Git and makes state
validation fail. Reject symlinked state roots or components. `resume.json` is a
disposable, untrusted locator and contract identifier—never authoritative
progress, authentication, a credential, or proof of Plan Orchestrator
authorship—and has exactly this schema:

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
complete self-check and the target ignore contract passes, including plan-only
creation. Retain it on explicit pause, blocker, failure, or cancellation. Clear
it only after every plan TODO and final validation succeed and native TODOs are
cleared, and only when the pointer still names the same plan and hash. A hash
mismatch never auto-executes: no-path resume stops for the human, while an
explicit safe path may replace the pointer only after complete provisional lock
acquisition, matching-owner finalization, and a complete self-check. If the
pointed-to plan has been deleted, no-path resume fails closed; an explicit valid
path may safely replace the stale pointer under the same rules.

All routes that create, allocate, update, convert, write, resume, or execute a
plan use this shared state-transition protocol:

1. Select only the checked-in route's fixed allowlisted acquisition operation.
   Do not parse a human plan or Tapestry locator and do not read plan, source,
   state, allocation, worktree, or execution content.
2. From the active OpenCode workspace root, invoke exactly `python3 -I
   "$HOME/.config/opencode/workflow-tools/start_work_state.py"
   <literal-operation> --repo-root .` with literal argv boundaries and normal
   runtime approval. No human or repository content participates in the shell
   string.
3. Permit the helper only the minimum read-only validation needed to prove that
   literal `.` resolves to the exact active canonical regular workspace root.
   Reject nested, mismatched, aliased, symlinked, unrelated, alternate, or
   outside-root ambiguity. If `.start-work` is absent, create only that one parent
   non-recursively; if a contender creates it first, revalidate and continue.
4. Require `.start-work` to be a real directory inside the active workspace.
   Atomically create `.start-work/lock` as the child exclusion point. The winner
   immediately generates a collision-resistant 64-lowercase-hex owner token and
   atomically installs bounded provisional `.start-work/lock/owner.json` with
   `version: 1`, that token, and `plan_path: null`. Acquisition succeeds and the
   token may be returned only after the complete provisional file is installed.
   Exactly one contender succeeds; every loser fails immediately as held without
   reading target plan, source, state, allocation, worktree, or execution content.
5. Under the acquired child lock, reject unsupported state children; then parse
   and validate only the route locator and freshly load the pointer, source,
   allocation inventory, or plan evidence needed to determine the canonical
   repository-relative plan path. Only the matching owner token may atomically
   replace provisional metadata with the final closed record. Then freshly load
   or revalidate every pointer, source, allocation inventory, exact plan byte/hash
   snapshot, checkbox, worktree, and execution item required by that route. Never
   use a pre-lock snapshot.
6. Validate or bootstrap the exact target ignore contract before pointer
   persistence. Complete plan self-checks before execution.
7. Hold the child lock through plan-only plan writes and pointer changes and
   through all direct or delegated execution until every planned mutation outcome
   is known.

Read-only self-explanation or advisory discussion that performs no plan, state,
or repository mutation does not acquire the lock. Ordinary Plan Orchestrator
conversation is otherwise not a bypass. Tapestry conversion acquires before
parsing its source locator, reading the source, or scanning allocation inventory,
and new-plan creation acquires before inspecting series allocation.

An interruption after parent creation but before child-lock creation may leave an
empty `.start-work` directory. That empty real parent is valid bootstrap residue
and a later acquisition may reuse it. On bootstrap or pre-mutation ignore
validation failure, release a provisional child lock only when the owner token
still matches, no mutation occurred, and no child can still mutate; a final lock
uses the ordinary matching-owner known-outcome rule. Then remove the parent only
if it is safely verified as the same empty real directory; otherwise leave the
empty parent for safe reuse. A non-directory or symlinked parent, unsupported
child, existing lock directory, or corrupt lock state fails closed. A crash after
child creation but before complete provisional metadata leaves stale/corrupt
state; the directory is never treated as unheld or automatically released. A
crash after provisional metadata leaves a held provisional lock. Parent creation
is not exclusion: child-lock creation is the first exclusion-protected mutation,
and all target plan, state, source, allocation, worktree, and execution reads
occur only after complete provisional ownership is installed.

The child lock is one cooperative, repository-wide planned-work execution lock.
It serializes all Plan Orchestrator sessions and their direct or delegated plan
implementation because distinct plans may overlap files. It does not serialize
ordinary repository work, prevent filesystem writes, or grant authority over
unrelated Lead, ERB, human, agent, or process activity.

Lock metadata lives only at `.start-work/lock/owner.json` and is one bounded,
strict-UTF-8, duplicate-rejecting JSON object. Immediately after child-directory
creation, acquisition atomically writes exactly this provisional schema:

```json
{
  "version": 1,
  "owner_token": "<64 lowercase hex>",
  "plan_path": null
}
```

After under-lock pointer, allocation, source, and plan validation determines the
canonical repository-relative plan path, only the matching owner may atomically
replace the provisional file with exactly this final schema:

```json
{
  "version": 1,
  "owner_token": "<same 64 lowercase hex>",
  "plan_path": "docs/implementation-plans/plans/<series>/<NN>-<slug>.md"
}
```

Use atomic file replacement and bounded stable reads for both writes and every
ownership check. Empty, partially written, malformed, oversized, duplicate- or
unknown-field, unsupported-version, invalid-token, invalid-null-transition,
unsafe-path, symlinked, missing, or non-regular `owner.json` beneath an existing
child lock is stale/corrupt state. It is never treated as unheld and is never
released automatically; guarded human stale recovery remains required. Store only
the repository-relative final plan path and write no target absolute path or
timestamp used for expiry.

Finalization accepts only a canonical validated plan path and the same owner
token. Repeating finalization with that token and identical path may be
idempotent; a different token, different path, second transition, or attempt to
return to `null` fails closed. Generate the owner token for cooperative
coordination, not as a credential; only its matching owner may finalize or
release the lock. Same-OS-user hostile-process tamper resistance is out of scope.
Acquisition fails immediately when held and never waits, retries, expires, or
steals by timeout.

The Plan Orchestrator holds the lock through every direct planned mutator,
delegated Worker, child process, timeout, cancellation path, and Task. The Worker
does not acquire, finalize, release, or mutate lock state. The matching owner may
release a known-clean provisional lock only when the route failed before any
plan, ignore, pointer, checkbox, sidebar, delegation, implementation, or other
planned mutation and no child can still mutate. After finalization, release after
normal completion, explicit pause, blocker, failure, cancellation, or a plan-only
return only when every planned mutation outcome is known and no child can still
mutate. Retain either phase whenever mutation occurred, mutation status is
uncertain, or any direct or delegated outcome is uncertain, not only when Worker
status is uncertain. Abrupt process termination must not auto-release it. A stale
lock may be cleared only after explicit human confirmation that no Plan
Orchestrator, Worker, child process, or planned mutator remains active; corrupt or
uncertain lock state fails closed.

Unrelated Lead or external work may continue while the planned-work lock is held
and must stay out of the plan's commits. The Plan Orchestrator's under-lock drift
checks compare plan-owned files and acceptance evidence before each mutation. If
concurrent work overlaps an owned file or invalidates evidence, stop for
reconciliation; do not absorb or overwrite it. Unrelated drift alone neither
blocks that work nor gives the Plan Orchestrator authority over it.

On no-path resume, after complete provisional lock acquisition, fresh pointer
validation, and matching-owner finalization, display the resolved canonical plan
path and the checked and unchecked numbered TODO state. Obtain explicit human
confirmation before any plan edit, checkbox write, delegation, implementation
mutation, or planned sidebar mutation. A pointer alone never authorizes execution.

Before the first unchecked TODO on every resume—and especially after a blocker,
failure, cancellation, process loss, or stale-lock recovery—reconcile current
acceptance evidence while holding the lock. If the effect is already satisfied,
rerun required validation and then check the TODO without repeating the effect;
if partially applied, repair or continue safely; if definitely unapplied,
execute it; and if unknown or non-idempotent, stop for the human. Do not claim
exactly-once execution. External effects carry at-least-once risk and require
operation-specific idempotency or explicit human reconciliation when evidence
cannot prove the outcome.

Plan Orchestrator and the trusted installed helper are the only state writers.
Lead and Worker edit permissions explicitly deny the repository-relative pattern
`.start-work/**`; ERB remains read-only, and Lead, ERB, and Worker receive no
pointer, lock, release, stale-recovery, or resume-state authority. Validate
effective actions against `.start-work/resume.json` and lock metadata for all
four roles rather than checking only for textual rule presence.

### `/start-work` and Tapestry conversion

`/start-work [<request-or-plan-path>] [instructions]` is the single create, update,
and execute entry point, owned by `plan-orchestrator`:

- With no path or request, select the route's fixed acquisition operation and use
  the isolated literal-dot installed-helper invocation from the active workspace.
  Acquire the child lock and complete provisional ownership before reading the
  pointer, resume only the freshly validated pointer, finalize `owner.json` with
  the resolved canonical path, display that path and
  checked/unchecked TODOs, and require explicit human confirmation before
  mutation. Never infer an active plan from filenames, TODO state, recent edits,
  or repository scans.
- For a new request, do not splice or parse request content into helper launch.
  Acquire the child lock and provisional owner first, then inspect the request,
  current repository evidence, and series allocation; select a valid series,
  allocate the canonical path, finalize ownership, write a lean plan, self-check
  it, and execute by default. If series choice has material organizational
  consequences, stop for the human rather than guessing.
- For an explicit plan path, invoke the same fixed isolated literal-dot helper
  form without parsing or passing the locator, acquire the child lock and
  provisional owner, and only then parse and enforce the relative canonical path,
  containment, regular-file, non-symlink, 1 MiB, stable-read, and strict-UTF-8
  rules before using its bytes or finalizing ownership.
  For a lean plan, apply requested conversational changes in place, self-check
  the complete result, then execute unchecked TODOs by default. For a legacy
  plan, preserve the source byte-for-byte, allocate a lean successor under the
  same series, finalize ownership to the successor, self-check it, and execute
  that successor by default.
- When the human explicitly requests plan-only behavior, complete the write and
  self-check and update the pointer, but do not implement, delegate, update
  execution checkboxes, or populate the sidebar as though execution started.

Every branch uses the shared protocol above. The fixed isolated helper launch,
active-workspace root validation, and possible empty-parent bootstrap are the only
pre-lock steps; child-lock creation followed by complete provisional ownership is
the acquisition boundary. Parse and freshly load all route inputs under that lock
before finalization or any pointer, plan, checkbox, delegation, conversion,
sidebar, or implementation mutation. An explicit path may replace a corrupt
pointer only after safe complete provisional child-lock acquisition, canonical
path validation, matching-owner finalization, complete self-check, and
target-ignore validation.

Do not add `/create-plan`, `/update-plan`, or another execution command. The Plan
Orchestrator prompt applies the exact shared acquisition, fresh-load, hold, and
release protocol during equivalent ordinary conversation, so the command is a
convenient top-level route rather than a separate authority model. Read-only
self-explanation is exempt only when it performs no plan, state, or repository
mutation.

`/convert-tapestry-plan <source> <series> [instructions]` also routes directly to
`plan-orchestrator`. Select the checked-in conversion acquisition literal and use
the fixed isolated literal-dot installed-helper form without parsing or passing
the source locator, series, or instructions. Acquire the child lock and complete
provisional ownership first. Under that lock, parse the source locator and
series, accept only a relative path that resolves under `.weave/plans/**` to a
regular, non-symlink Markdown file with no symlinked path component, and scan
allocation only afterward. Before reading or copying, reject absolute paths,
`..`, outside-root resolution, directories, special files, invalid UTF-8, and
files larger than 1 MiB. Use a bounded, stable read and strict decoding, accepting
the exact limit and rejecting limit plus one. Determine and validate the newly
allocated canonical plan path, finalize ownership with the matching token, and
then treat every named file, symbol, behavior, dependency, acceptance condition,
test, and command as an untrusted claim.
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

The resulting sorted manifest contains exactly 23 agents, 6 commands, and the
separate one-item `runtime_helpers` inventory described above.
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
6. On resume, permit only the fixed isolated literal-dot helper launch, exact
   active-workspace-root validation, and possible empty parent bootstrap before
   acquiring the child lock; read the pointer, finalize ownership to its validated
   canonical path, and read the plan and acceptance evidence freshly only after
   complete provisional acquisition, then reconcile the first unchecked step
   before rebuilding the whole window. Treat checked items
   as accepted only after required current evidence remains valid. Use the
   pointer only as an untrusted locator and contract identifier, never
   authentication or proof of authorship. Do not treat the pointer or stale
   sidebar as durable progress, infer completion from either, or reconstruct old
   completed entries merely for display. For no-path resume, wait for the
   required human confirmation before writing this planned sidebar.
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
- **Use the `.start-work` parent itself as the lock or read state while creating
  it:** rejected. The parent is reusable bootstrap structure and may be created
  concurrently; atomic child-lock creation is the only exclusion point, and no
  target plan, state, source, allocation, worktree, or execution content is read
  before complete provisional ownership is installed.
- **Install or discover a helper in each target repository:** rejected. A target
  can be unrelated or hostile. One reviewed checkout source is exposed through
  the exact managed `workflow-tools` link, and every runtime invocation starts at
  and validates the active workspace through literal `--repo-root .` without
  accepting a target path.
- **Copy one helper file into machine-local configuration or register it as a
  custom OpenCode tool:** rejected. A paired whole-directory link preserves the
  current install ownership model, keeps updates live, and avoids a copied or
  arbitrarily discoverable executable.
- **Trust a path-only `~/.config/opencode` preflight:** rejected. A mutable
  machine-local path can be symlinked or substituted between checks. Bind a
  validated configuration-root descriptor, record device/inode identity, and
  perform no-follow descriptor-relative mutations with immediate identity and
  destination ownership revalidation.
- **Create the child lock without provisional metadata or derive the plan path
  before acquisition:** rejected. New requests and no-path resume may not yet
  know a path, while a directory without complete ownership metadata is
  ambiguous. Atomically install `plan_path: null` ownership first, then parse and
  validate route locators and finalize with the matching token.
- **Broadly ignore `/.start-work/` or rewrite ignore policy during project
  bootstrap:** rejected. The template documents only the two narrow entries;
  first use adds missing exact entries under complete provisional ownership or
  stops on unsafe, broad, or conflicting policy.
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
- **Add automatic Bash permission for the state helper:** rejected. Keep the
  exact fixed installed-path invocation runtime-approval-gated; do not add a
  broad or target-local helper allow rule.
- **Let the Plan Orchestrator invoke ERB or specialist Tasks:** rejected. Optional
  independent review stays top-level, and planned implementation delegation has
  one exact child: `implementation-worker`.

## Dependencies

`depends_on` is empty. `opencode-01` reserves sequence `01` but is neither an
execution prerequisite nor a source plan for this work. The implementation is
one coordinated repository change delivered in four validated atomic commits:
prompt, command, trusted runtime helper, three-link installer, manifest,
validator, test, and synchronized documentation changes must agree before
rollout. The 23-agent and 6-command targets do not count the separate one-item
runtime-helper inventory.

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
Root and project-template README/template pairs must be updated together. Agent,
command, and runtime-helper manifest inventory changes land in their owning
slices. No package, service, plugin, or external repository is an implementation
dependency. Implementation does not modify live OpenCode configuration; rollout
uses the existing setup command to add the exact managed `workflow-tools` link
and must verify all three links before the new routes are used.

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
- `change-verifier` found revision-3 findings R3-2 through R3-4 closed and
  isolated the remaining shared-route acquisition gap addressed by R4-1.
- `adversarial-reviewer` observed `just validate-opencode` and `just validate`
  passing, identified the trusted helper distribution and fresh-target parent
  bootstrap gaps addressed by R4-2 and R4-3, and reported the focused manager
  suite and runtime-helper scenarios as unrun.
- `change-verifier` found R4-1 through R4-3 closed in revision 5 and found that
  revision otherwise execution-ready.
- `security-critic` identified R5-1 through R5-3: runtime helper shell
  construction still admitted an arbitrary target, machine-local configuration
  root ownership was not bound across every mutation, and child-lock acquisition
  lacked atomic provisional owner metadata for unknown-path routes. No helper
  runtime tests or machine-local configuration inspection accompanied that
  review.

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
- A target-local same-name helper can be hostile, and a copied machine-local
  helper can drift from reviewed source. Invoke only the fixed installed path
  using `python3 -I`, a checked-in literal operation, and literal
  `--repo-root .`; forbid human or repository content in shell construction;
  validate the one-item manifest inventory and regular checkout source; and keep
  setup, dry-run, verify, doctor, uninstall, rollback, restoration, and reporting
  fail-closed across all three managed directory links.
- A workspace name can contain shell-shaped bytes, and ambient Python startup can
  import hostile workspace or user code. Exact quoting, isolated startup,
  literal-dot argv, closed operation literals, grammar checks for later
  machine-derived arguments, and tests over spaces, quotes, leading hyphens,
  semicolons, newlines, backticks, and `$()`-shaped names must prove that no
  marker command or target-local executable/module runs.
- A machine-local configuration root or destination can be swapped after
  preflight. Validate every mutable ancestor as a stable real directory outside
  source and target workspaces, bind the root descriptor/device/inode, mutate
  descriptor-relatively with no-follow behavior, re-lstat each destination before
  each position, and limit rollback/restoration to exact transaction-proven links
  under the still-bound root. Never follow a moved root or disturb unrelated
  sentinels.
- Fresh repositories have no `.start-work` parent or ignore entries. Treat an
  empty real parent as reusable bootstrap residue, not exclusion; use atomic
  child-lock creation for exclusion; add only missing exact ignore lines after
  complete provisional ownership; and stop rather than following symlinks or
  rewriting broad, custom, or conflicting ignore policy.
- The planned-work lock can remain after a crash or any uncertain direct or
  delegated mutation. This is the intended safety trade-off: do not expire or
  steal it, and require explicit human confirmation after checking that no Plan
  Orchestrator, Worker, child, or other planned mutator remains. The owner token
  coordinates release but is not a credential, and hostile same-user tampering is
  out of scope.
- A crash between child-directory creation and complete provisional `owner.json`
  leaves ambiguous stale state. Never infer that such a directory is unheld;
  bounded stable metadata reads, atomic provisional/final replacement,
  token-matched finalization/release, and guarded human stale recovery make the
  ambiguity fail closed. Release provisional ownership only after proving the
  route made no plan, ignore, pointer, checkbox, sidebar, delegation, or
  implementation mutation and no child can still act.
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
- any mutating `/start-work`, `/convert-tapestry-plan`, or equivalent ordinary
  conversation route bypasses the shared helper protocol, or a route other than
  mutation-free self-explanation proceeds without complete provisional child-lock
  acquisition;
- a runtime helper launch differs from `python3 -I
  "$HOME/.config/opencode/workflow-tools/start_work_state.py"
  <literal-operation> --repo-root .`, uses a non-allowlisted operation, accepts or
  interpolates a human target, locator, request, instruction, or repository
  string, loses argv boundaries, adds concatenation/redirection/pipes/substitution
  or extra shell operations, lacks normal runtime approval, permits ambient
  workspace/user Python imports, or executes a target-local executable/module;
- literal `.` is not one argv value or cannot be proved to be exactly the active
  OpenCode workspace root; a nested, mismatched, aliased, symlinked, unrelated,
  alternate, or changing root is accepted; or a later machine-derived token or
  path does not match its closed ASCII grammar and remain one argument;
- a pre-lock operation exceeds fixed route selection, fixed helper launch,
  minimum active canonical regular workspace-root validation, or safe
  non-recursive empty-parent bootstrap; a human plan/Tapestry locator is parsed or
  passed to helper launch; the parent is treated as exclusion; any pointer,
  source, allocation inventory, plan, checkbox, hash, worktree, or execution
  snapshot is read or relied on before complete provisional child-lock
  acquisition; or post-acquisition evidence is not freshly loaded and revalidated;
- `.start-work` is symlinked, outside the target, or not a directory; first-use
  acquisition cannot safely create or revalidate that one parent; child-lock
  creation is not atomic; a losing contender reads target content instead of
  failing immediately; an empty interrupted parent cannot be reused safely; or
  cleanup removes a parent that is not verified empty and safe;
- pointer or lock state is malformed, oversized, symlinked, non-regular, corrupt,
  uncertain, outside the repository root, contains unknown or duplicate fields,
  or cannot fail closed; `.start-work/lock/owner.json` is missing, empty, partial,
  unstable, or treated as unheld; acquisition returns before the exact bounded
  provisional record with `plan_path: null` is atomically installed; any
  unsupported `.start-work/` child exists; a held lock cannot be acquired
  immediately; a non-owner would finalize or release it; finalization accepts a
  noncanonical path, different token/path, or second transition; a timestamp
  would drive expiry; or stale-lock cleanup lacks explicit human confirmation
  that no Plan Orchestrator, Worker, child, or planned mutator remains;
- any direct or delegated planned mutation outcome is uncertain but the lock
  would be released, the Worker would acquire/release/mutate lock state, or the
  design would claim to block unrelated filesystem writes or serialize all
  repository work;
- a provisional lock is released after any plan, ignore, pointer, checkbox,
  sidebar, delegation, implementation, or other planned mutation, without proving
  no child can still mutate, or while any outcome is uncertain; or ordinary
  release after finalization lacks the matching owner and known outcomes;
- plan-only creation or update releases before all plan, exact-ignore, and pointer
  writes are complete; execution releases while a direct or delegated mutator can
  still act; or unrelated external writes are claimed to be blocked;
- pointer persistence is possible before the target `.gitignore` has each exact
  narrow state entry once; project bootstrap overwrites target ignore policy; a
  broad `/.start-work/`, symlinked/unsafe ignore file, or conflicting custom rule
  is silently rewritten instead of stopping for the human;
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
  Orchestrator, differ from 23 agents and 6 commands, or contain any runtime
  helper other than the single `workflow-tools/start_work_state.py` entry;
- setup, dry-run, verify, doctor, uninstall, rollback, or restoration does not
  reject a symlinked, non-directory, aliased, repository-contained,
  target-contained, identity-changing, or missing-with-unsafe-parent
  configuration root or mutable ancestor before destination mutation; a missing
  final `opencode` directory is created without safe-parent checks or more than
  that final directory is created; or no validated root descriptor/device/inode
  remains bound;
- any `agents`, `commands`, or `workflow-tools` create/remove/rollback/restoration
  mutation is path-following rather than no-follow descriptor-relative where
  supported; root path/descriptor identity or destination ownership is not
  revalidated immediately before every mutation position and success report; a
  substituted, moved, missing, or mismatched parent/destination is followed; a
  rollback touches an entry not proven to be the transaction's exact link;
  partial rollback is hidden; or an unrelated sentinel changes;
- setup, verify, or uninstall does not manage the exact `agents`, `commands`, and
  `workflow-tools` link set fail-closed; the helper source or directory can be a
  symlink or resolve outside the trusted checkout; rollback leaves a newly
  created managed link without reporting it; uninstall removes foreign content;
  or target repository content/state changes during setup, rollback, or uninstall;
- any Plan Orchestrator route invokes a target-local, copied, discovered, or
  repository-relative helper instead of the fixed
  `~/.config/opencode/workflow-tools/start_work_state.py`, omits isolated startup
  or literal active-workspace `--repo-root .`, stores an absolute target path in
  state, registers a custom tool, or receives a broad automatic Bash allow;
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
  an explicit human execution request, read its source or scan allocation before
  complete provisional child-lock acquisition, or read a source before enforcing
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
- helper-invocation tests omit active workspace directories containing spaces,
  quotes, leading hyphens, semicolons, newlines, backticks, or `$()`-shaped text;
  do not assert literal-dot argv and zero marker/target-local execution; or fail
  to reject nested, mismatched, aliased, symlinked, unrelated, or alternate roots;
- provisional-lock tests omit unknown-path new requests, no-path/explicit/legacy/
  conversion finalization, token-mismatch finalize/release, crash positions
  before and after provisional metadata, exact duplicate versus conflicting
  finalization, mutation-aware provisional release, atomic replacement, or proof
  that every second contender loses without reading target content;
- configuration-root tests omit mutable-ancestor symlinks to byte-snapshotted
  unrelated repositories/targets, safe and unsafe missing-final-root parents, or
  root/destination swaps before every create/remove/rollback/restoration position;
  or an unsafe case changes a sentinel or a successful case escapes the bound
  root descriptor;
- route tests omit any of `/start-work`, `/convert-tapestry-plan`, or equivalent
  ordinary conversation, or fail to cover immediate held-lock failure, absence of
  pre-lock state/source/allocation reads, fresh post-lock reload, plan-only
  release, execution retention, and unrelated external writes remaining
  unblocked;
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

### 2. Plan Orchestrator, trusted helper installation, and resume infrastructure

**Objective:** Replace the Coordinator with the dedicated primary Plan
Orchestrator, distribute one trusted runtime helper through the existing managed
link model, bind machine-local configuration-root ownership, and add safe
fresh-target resume and two-phase exclusion infrastructure.

**Scope and stable interfaces:** Replace
`opencode/agents/planning-coordinator.md` with
`opencode/agents/plan-orchestrator.md`; update the Lead, ERB, and Worker boundary
clauses; update the repository `.gitignore`; add
`opencode/workflow-tools/start_work_state.py` and
`tests/test_start_work_state.py`; add the exact one-item `runtime_helpers`
manifest inventory; and extend `tools/opencode_manager.py`, its tests, and
applicable `README.md`, `Justfile`, governance, and project-template guidance for
the third managed `workflow-tools` link, descriptor-bound configuration-root
ownership, and target ignore bootstrap. Include permission, Task, state, helper,
installer, fixture, mutation, cleanup, and reporting validation in this group.
Preserve the concurrent Lead TODO/Git work, the 23-agent inventory, current
command inventory until slice 3, and all unrelated permissions.

**Acceptance criteria:**

- The manifest still has 23 agents; `plan-orchestrator` is primary, replaces the
  old ID, has plan edit `ask`, plan-path Bash denial, flat `todowrite: allow`, and
  Task access only to `implementation-worker`. A separate `runtime_helpers` list
  contains exactly `workflow-tools/start_work_state.py`; agent and command counts
  are unchanged by that inventory.
- The sole helper source is a regular non-symlink file inside the trusted
  `opencode/workflow-tools/` directory. Validation rejects a missing, extra,
  symlinked, outside-root, or unexpected runtime helper and never classifies it as
  an agent, command, support file, or OpenCode custom tool.
- Setup, dry-run, verify, doctor, uninstall, rollback, restoration, CLI help, and
  reporting manage `agents`, `commands`, and `workflow-tools` as one exact
  three-link set. Starting from the configured home/config base, every mutable
  component through `~/.config/opencode` must be a stable real directory outside
  source checkouts and target workspaces. Tests reject symlinked, non-directory,
  aliased, repository-contained, target-contained, identity-changing, and
  missing-with-unsafe-parent roots before mutation; safe missing-final-root
  creation creates only `opencode`, opens it, and binds its path/device/inode.
- All link creates, removes, rollbacks, and restorations are descriptor-relative
  under that still-bound root with no-follow behavior where supported. Tests
  re-lstat root identity and destination ownership before every mutation position
  and success report; swap the root or destination parent before each create,
  remove, rollback, and restoration position; and prove substitution stops without
  following a moved root. Rollback/restoration touches only exact transaction-
  proven links, reports partial cleanup, and leaves unrelated sentinels untouched.
- Installer tests also cover idempotent exact and relative links,
  all-destination preflight, real/foreign/broken/mismatched destinations, visible
  helper source, mixed ownership, dry runs, and uninstall that removes only exact
  managed links. Mutable-ancestor symlink fixtures point to byte-snapshotted
  unrelated repositories and targets; every unsafe case leaves those bytes and
  sentinels unchanged, and successful operations remain under the originally
  bound root.
- Every Plan Orchestrator state operation names only the fixed installed helper
  path, remains runtime-approval-gated, and uses exactly `python3 -I
  "$HOME/.config/opencode/workflow-tools/start_work_state.py"
  <literal-operation> --repo-root .` from the active workspace. Operation names
  are checked-in allowlisted literals; literal `.` is one argv value; no human
  target, plan/Tapestry locator, request, instruction, or repository text enters
  shell construction; and the runtime prompt forbids concatenation, redirection,
  pipes, substitution, and extra operations.
- The helper remains standard-library-only, isolated startup imports no workspace
  module or user site, and root validation proves `.` is exactly the active
  workspace. Deterministic directories containing spaces, quotes, leading
  hyphens, semicolons, newlines, backticks, and `$()`-shaped text still pass
  literal `.` as one root argument, execute no marker or target-local
  executable/module, and keep state under that workspace. Nested, mismatched,
  aliased, symlinked, unrelated, and alternate roots fail closed. Later
  machine-derived owner tokens and canonical paths pass only after closed-grammar
  validation and remain one argv element, preferably in structured API/
  `subprocess` argv tests.
- The Lead retains flat `todowrite: allow` only for generic unplanned-session
  coordination, Lead and Worker explicitly deny `.start-work/**` edits, and
  Worker and ERB have no explicit TODO allow. Deterministic tests reject Lead,
  Worker, or ERB planned-work checkbox, TODO, state, execution, or implementation
  authority.
- Plan Orchestrator and the trusted installed standard-library helper are the only
  runtime-state writers; Lead, Worker, and ERB have no lock, release,
  stale-recovery, pointer, or resume authority; no broad automatic Bash allow is
  added to invoke the helper. Effective-action tests exercise Plan Orchestrator,
  Lead, Worker, and ERB against `.start-work/resume.json` and lock metadata rather
  than checking only textual permission clauses.
- `.gitignore` contains exactly `/.start-work/resume.json` and
  `/.start-work/lock/` for this workflow, not `/.start-work/`. The helper rejects
  every unsupported state child; `.start-work/history.json` remains Git-visible
  and invalid. Pointer parsing is schema-closed, size-bounded, UTF-8/JSON safe,
  canonical-path checked, and contract-hash bound, with checkbox-only hash
  normalization and no authentication or authorship claim.
- Project-template guidance documents those two lines but does not overwrite a
  target `.gitignore` during project bootstrap. On first planned-work use, after
  complete provisional child-lock acquisition, the Plan Orchestrator creates a
  safely absent file or adds missing exact entries through ordinary edit tools,
  includes that change in plan-owned scope, and does so before pointer persistence.
  The helper verifies the contract before pointer writes. Symlinked or unsafe
  files and broad, duplicate, ambiguous, or conflicting `.start-work` rules stop
  for the human. Plan-only behavior may make only the plan and required exact
  ignore change.
- Every explicit or pointer-located canonical lean or legacy plan uses a stable
  bounded read before hash, decode, parse, display, or agent use. Tests accept
  exactly 1 MiB; reject limit plus one, invalid UTF-8, and a file whose size or
  content changes during validation; and leave invalid legacy plans untouched
  with a human-actionable error.
- For a fresh active workspace, the helper performs only canonical regular-root
  validation of the literal-dot workspace before state bootstrap, creates
  `.start-work` once non-recursively when absent, revalidates it if a contender
  wins parent creation, requires a real in-root directory, and atomically creates
  `.start-work/lock` as the actual exclusion point. Parent creation is not
  exclusion. No pointer, plan, Tapestry locator/source, allocation inventory,
  worktree, or execution evidence is parsed or read before complete provisional
  child-lock ownership.
- The cooperative repository-wide planned-work child lock fails immediately when
  held and freshly reloads every route input after complete provisional
  acquisition. Immediately after child-directory creation, the helper generates a
  64-lowercase-hex token and atomically installs bounded `owner.json` containing
  only `version`, that token, and `plan_path: null`; it returns acquisition
  success/token only afterward.
  Empty, partial, malformed, missing, unstable, duplicate/unknown-field, or
  otherwise corrupt metadata under an existing child lock is stale and requires
  guarded human recovery rather than automatic release.
- Under provisional ownership, the route parses/validates its locator or
  allocation and derives a canonical repository-relative plan path. Only the
  matching owner may atomically replace provisional metadata with the final same-
  token path. Identical duplicate finalization may be idempotent; token mismatch,
  path mismatch, a second transition, or noncanonical path fails closed. No
  absolute target path or expiry timestamp is stored; no timeout expires or
  steals the lock.
- Matching-owner provisional release is allowed only for a known-clean failure
  before any plan, ignore, pointer, checkbox, sidebar, delegation,
  implementation, or other planned mutation and after proving no child remains.
  Any mutation or uncertainty retains the lock. Normal post-finalization release
  still requires the matching owner and known outcomes.
- Deterministic bootstrap tests cover first acquisition with no parent, two
  contenders racing through parent creation and child-lock acquisition, a crash
  after parent creation but before child creation, a crash after child creation,
  partial write before provisional metadata, a crash after provisional metadata,
  reuse and safe removal of an empty parent, loser immediate failure, symlinked/
  non-directory/outside-root parent rejection, unsupported children after
  acquisition, and proof that all plan/state/source/allocation/worktree reads
  occur only after complete provisional success. Every second contender loses
  without reading target content.
- The Plan Orchestrator holds the lock through direct mutators, Workers, Tasks,
  child processes, timeouts, and cancellation paths. Worker never changes lock
  state. Any uncertain planned mutation retains the lock. Unrelated repository
  work remains possible, while overlapping owned-file drift stops execution for
  reconciliation.
- Executable helper tests cover stale pre-lock snapshots, fresh reload after
  acquisition, exclusive acquisition under a process barrier, owner-only release,
  unknown-path new requests; no-path, explicit-plan, legacy-successor, and
  conversion finalization; token-mismatch finalize/release; exact duplicate and
  conflicting finalization; atomic provisional-to-final replacement; known-clean
  pre-mutation provisional release; prohibited release after mutation or
  uncertainty; process termination after acquisition; direct and delegated
  cancellation; plan-only release after plan/ignore/pointer writes; execution
  retention; unrelated external writes remaining unblocked;
  effect-before-checkbox crashes; stale-lock handling with explicit human
  confirmation; pointer corruption; plan-path containment; hash mismatch;
  clear-on-completion; deletion-safe explicit-path resume; and no duplicate
  dispatch when current evidence already satisfies a TODO.
- Unrelated-target tests prove no local helper requirement, no target-local helper
  execution, state containment beneath the active workspace, exact ignore
  bootstrap before pointer persistence, fail-closed unsafe/conflicting ignore
  handling, and setup/dry-run/verify/doctor/uninstall/rollback/restoration
  isolation from target content and state.
- Every process test uses bounded barriers and joins, explicit child result
  reporting, and parent-side `finally` cleanup without sleep-based race
  assertions. A deliberately stalled child fails within the bound and leaves no
  process or lock fixture.
- Prompt-contract tests verify required checked-in self-check, TODO, state,
  release/retention, delegation, and permission clauses and reject contradictions;
  they do not claim to prove runtime agents, delegation, cancellation, atomic
  exclusion, or sidebar behavior.

**Validation and commit boundary:** Run `tests/test_start_work_state.py`, focused
agent/permission/Task/state/manifest/setup/dry-run/verify/doctor/uninstall/
rollback/restoration manager tests, the complete focused manager suite,
`just validate-opencode`, and `just validate`. Commit the agent replacement,
trusted helper directory, repository ignore rule, runtime-helper inventory,
three-link installer and cleanup behavior, applicable docs, validator changes,
and tests as one group before slice 3.

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
  audit, and regression remain ERB-owned; every command remains `subtask: false`;
  and the separate one-item runtime-helper inventory remains unchanged.
- `/start-work` distinguishes no-path pointer resume, new requests, explicit
  canonical lean paths, immutable legacy paths with successor allocation,
  conversational updates, default execution, and explicit plan-only behavior.
  It uses the fixed isolated literal-dot installed-helper invocation and shared
  protocol, parses no plan locator and reads no resume, allocation, or plan
  content before complete provisional child-lock acquisition, freshly reloads all
  evidence, finalizes ownership with the canonical path, applies the complete
  pointer and target-ignore lifecycle, and on no-path resume shows canonical path
  plus checkbox state and gets explicit human confirmation before any mutation.
- `/convert-tapestry-plan` is plan-only unless execution is explicit, preserves
  its source, acquires through the fixed helper without parsing or passing the
  locator before reading source or allocation inventory, finalizes to the newly
  allocated canonical path, and accepts only regular non-symlink valid UTF-8
  Markdown under `.weave/plans/**` at or below 1 MiB. Absolute, traversal,
  outside-root, directory, special-file, symlink, invalid-encoding, and oversized
  inputs fail before content is read or copied.
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
- Route-specific prompt/helper scenarios cover `/start-work`,
  `/convert-tapestry-plan`, and equivalent ordinary Plan Orchestrator conversation
  for the exact isolated literal-dot shell form, no locator in launch arguments,
  immediate held-lock failure, no pre-lock state/source/allocation snapshot,
  atomic provisional ownership, route-appropriate finalization, fresh post-lock
  reload, lock hold across plan-only writes and pointer updates, plan-only
  release, direct/delegated execution retention, and unrelated external writes
  remaining unblocked. Read-only no-mutation explanation is tested as the sole
  no-lock exemption.
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
  no-path and explicit `/start-work`, shared-route acquisition, trusted installed
  helper, fixed isolated literal-dot invocation, bound machine-local configuration
  root, provisional/final parent-child lock lifecycle, target-ignore behavior,
  optional advisory review, legacy succession, Tapestry trust boundary, TODO
  ownership, and the Lead's complex-request route.
- Deterministic validation rejects active Coordinator authority, deleted
  lifecycle commands, approval gates, prohibited aliases, broad state-helper Bash
  permission, or stale planned-work TODO/state authority outside the Plan
  Orchestrator while allowing the Lead's generic unplanned TODO permission.
- The complete active inventory scan runs only after all listed authoritative
  files migrate. One mutation per obsolete token proves exact file/token
  diagnostics, and exclusion fixtures prove plans, tests, and historical records
  are not scanned.
- Agent/command counts, owners, exact Task edges, plan/state permissions,
  one-item runtime-helper inventory, descriptor-bound three-link install
  ownership, MCP/clipboard access, Worker restrictions, and synchronized
  templates match this plan.
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
  command owners, removed-command absence, one-level Task graph, and exact
  one-item `runtime_helpers` inventory without custom-tool registration.
- **Trusted helper installation:** regular non-symlink checkout source at
  `opencode/workflow-tools/start_work_state.py`; exact installed `workflow-tools`
  link; all-three setup preflight, idempotency, dry-run, verification, doctor,
  visibility, rollback, restoration, mixed ownership, and uninstall; hostile or
  mismatched destination rejection; no copied helper; and no target repository or
  state mutation from setup, dry-run, verify, doctor, uninstall, rollback, or
  restoration. Cover every mutable configuration-root ancestor, safe versus
  unsafe missing final root, bound root/device/inode identity, no-follow
  descriptor-relative mutation, immediate destination re-lstat, swaps before
  every create/remove/rollback/restoration position, transaction-only cleanup,
  partial rollback reporting, and unchanged byte-snapshotted unrelated targets/
  repositories and sentinels.
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
- **Fixed active-workspace invocation and ignore bootstrap:** exact `python3 -I
  "$HOME/.config/opencode/workflow-tools/start_work_state.py"
  <literal-operation> --repo-root .`, allowlisted literal operations, normal
  approval, exact quoting, and no concatenation, redirection, pipes, substitution,
  extra operations, or human/repository shell content. Use workspaces containing
  spaces, quotes, leading hyphens, semicolons, newlines, backticks, and
  `$()`-shaped text; assert literal-dot argv, no marker or target-local executable/
  module execution, and state containment beneath only the active workspace.
  Reject nested, mismatched, aliased, symlinked, unrelated, and alternate roots.
  Structured test APIs may pass explicit roots and use `subprocess` argv arrays;
  runtime Bash never does. Also cover exact two-line target `.gitignore`
  validation, ordinary-edit addition before pointer persistence, plan-owned
  reporting, project-template non-overwrite, and fail-closed symlinked, unsafe,
  broad, duplicate, ambiguous, or conflicting ignore policy.
- **Pointer and canonical path:** exact closed schema, pointer-size limit, unknown
  field/version/hash rejection, relative canonical lean-plan containment,
  checkbox-only SHA-256 normalization, mismatch stop, corruption handling,
  plan-only pointer write, retention on pause/blocker/failure/cancellation,
  matching clear-on-completion, deletion-safe explicit replacement, rejection of
  unsupported state children, no authentication claim, and no-path display plus
  explicit-human-confirmation ordering before mutation.
- **Parent bootstrap and planned-work child lock:** only exact active-workspace-
  root validation and non-recursive empty-parent creation before exclusion; first
  acquisition in a fresh workspace; two contenders racing at parent and child;
  crash between parent and child; crash after child creation; partial write before
  provisional metadata; crash after complete provisional metadata; empty-parent
  reuse and safe cleanup;
  symlinked/non-directory parent rejection; atomic child-lock exclusion;
  immediate loser failure without target-content reads; unsupported children
  rejected under the child lock; stale pre-lock snapshot rejection; fresh
  under-lock reload; bounded stable `owner.json`; valid 64-hex owner token; exact
  provisional `plan_path: null`; unknown-path new requests; no-path, explicit,
  legacy, and conversion finalization; matching-owner finalize/release;
  token-mismatch finalize/release; duplicate exact and conflicting finalization;
  atomic provisional-to-final replacement; known-clean pre-mutation provisional
  release; prohibited release after mutation/uncertainty; abrupt process
  termination; direct and delegated cancellation retention; no timeout stealing or
  expiry timestamp; explicit-human stale-lock recovery; and missing/empty/partial/
  unknown-field/corrupt-state failure. Spy evidence proves locators, pointer, plan,
  Tapestry source, allocation inventory, worktree, and execution evidence are not
  parsed or read before complete provisional success. Effective tests also prove
  Worker has no lock operation, unrelated external writes are not blocked, and
  overlapping drift stops plan work.
- **Shared route transitions:** `/start-work`, `/convert-tapestry-plan`, and
  equivalent ordinary Plan Orchestrator conversation each use the fixed isolated
  literal-dot helper command and cover no human locator in launch argv, held-lock
  immediate failure, no pre-lock locator parsing or state/source/allocation
  snapshot, provisional ownership, correct finalization, fresh post-lock reload,
  lock hold through plan and pointer writes, plan-only release,
  direct/delegated execution retention, and unrelated external writes remaining
  unblocked. Mutation-free read-only self-explanation is the sole no-lock case.
- **Resume reconciliation and fault injection:** deterministic barriers cover an
  effect-before-checkbox crash, already-satisfied evidence with required
  revalidation and no duplicate dispatch, partial-effect repair, definitely
  unapplied execution, and unknown/non-idempotent human stop. Assertions describe
  at-least-once risk rather than exactly-once behavior.
- **Tapestry trust boundary:** `.weave/plans/**` containment, regular Markdown
  file, complete provisional child-lock acquisition before source/allocation
  reads, non-symlink components, stable 1 MiB maximum, strict UTF-8, source
  preservation, and rejection of absolute, traversal, outside-root, directory,
  special-file, symlink, invalid-encoding, and oversized fixtures before read/copy.
  Secondary-reference spies cover absolute, traversal, symlink, oversized,
  invalid-encoding, sensitive-local, newline, semicolon, backtick, `$()`,
  control-character, and shell-metacharacter references and prove no secondary
  read or command execution.
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
  Markdown-fence, descriptor-bound all-three setup/verify/uninstall,
  23-agent/6-command targets, and unrelated command behavior.

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

The OpenCode installation expands from two managed whole-directory links to the
exact `agents`, `commands`, and `workflow-tools` set. After the final repository
state passes validation, a maintainer previews and runs the existing OpenCode
setup command, which may add only the missing exact `workflow-tools` link when the
other links are already correct. The configured home/config base, every mutable
ancestor, the final configuration root, and each destination must pass the bound
no-symlink/ownership/containment policy; any real, foreign, broken, mismatched,
aliased, substituted, or unsafe-parent state blocks the set without replacement.
Verification must pass for all three under the same revalidated descriptor,
path/device/inode identity before `/start-work` or conversion uses the helper. The
helper is never copied, and source updates become live through the managed link.
Agent and command definition changes still require the documented OpenCode
restart; helper-file changes through an already valid link do not require a copy
step.

Uninstall removes all three destinations only when all still resolve to this
checkout beneath the still-bound root and never removes repository sources,
target repository files, or target `.start-work` state. Setup or uninstall
failure uses descriptor-relative, ownership-revalidated rollback/restoration only
for exact transaction-proven links and reports every destination it cannot safely
restore or remove. A moved or substituted configuration root stops recovery; it
is never followed. Rollback of the repository change uses an ordinary new commit
and, if the new install was already activated, the guarded uninstall/setup
workflow; it never falls back to a target-local helper or deletes target state.

Only `/.start-work/resume.json` and `/.start-work/lock/` are ignored disposable
local state, not tracked migration artifacts; the parent is not broadly ignored.
Project-template bootstrap documents those entries but does not overwrite target
ignore policy. On the first planned-work operation, the trusted installed helper
may leave an empty real `.start-work` parent if interrupted before child-lock
creation; later acquisition reuses it. After complete provisional ownership, the
Plan Orchestrator adds missing exact ignore entries through normal edit tools
before pointer persistence. Unsafe, symlinked, broad, or conflicting ignore state
stops for the human. Any unsupported child remains visible to Git and makes
helper validation fail. A missing pointer means there is no no-path resume; a
corrupt or mismatched pointer stops; and a stale lock requires explicit human
confirmation after verifying that no Plan Orchestrator, Worker, child process, or
other planned mutator remains. Recovery may remove only confirmed-stale local
state through the helper's guarded operation. No timeout or timestamp expires a
lock, and the Worker, Lead, and ERB have no recovery authority. Never derive
progress or authorship from the pointer or reconstruct it from repository scans.

The child lock may be provisional (`plan_path: null`) or final (one canonical
repository-relative path). A crash before complete provisional `owner.json`, an
empty/partial/malformed/unknown-field record, or a conflicting finalization is
stale/corrupt state rather than an unheld lock. A known-clean provisional owner
may release only before any plan, ignore, pointer, checkbox, sidebar, delegation,
or implementation mutation and after proving no child remains. Otherwise retain
the lock for ordinary or guarded stale recovery. Recovery never guesses a path,
changes the owner token, expires the lock, or follows a symlinked/substituted
state component.

After a crash, cancellation, or process loss, keep the lock when any planned
effect is uncertain. Once the human confirms stale recovery, the next owner must
reconcile each first unchecked TODO against current acceptance evidence before
dispatch. Already-satisfied effects are revalidated and checked without repeat;
partial effects are repaired; definitely unapplied work may run; unknown or
non-idempotent effects stop. This recovery contract acknowledges at-least-once
external-effect risk and does not promise exactly-once execution.

Roll out agents, commands, trusted helper source, manifest, validator/tests, docs,
and project-template copies through the four validation-passing atomic commits,
but do not restart OpenCode, run mutating setup, or use the new planned workflow
between slices. Repository implementation does not edit machine-local config
files. After the final coherent state passes all checks, the maintainer runs the
guarded setup/verify flow and then restarts OpenCode for definition changes.
Capture the pre-edit bytes of tracked `opencode-01` and verify the same bytes
before handoff.

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
  Lead/ERB routing guardrails, legacy succession, trusted helper installation,
  fixed isolated active-workspace invocation, and the descriptor-bound exact
  three-link setup/verify/uninstall model.
- `docs/implementation-plans/{README,TEMPLATE}.md`: become the authoritative
  closed contract and exact starter shape.
- `docs/engineering-agent-governance.md`: update roles, Task topology, command
  ownership, review advice, self-check semantics, execution, and
  Plan-Orchestrator/Lead/Worker/ERB TODO/state boundaries, including the shared
  route protocol, provisional/final lock ownership, fixed installed-helper trust
  boundary, and machine-local configuration-root ownership.
- `opencode/project-template/`: mirror portable workflow guidance and keep both
  plan files byte-identical to root copies. Document the two exact target ignore
  entries without overwriting `.gitignore` during bootstrap.
- Agent and command Markdown: implement Plan Orchestrator ownership, Lead/ERB
  `/start-work` routes, complex-request classification, optional advisory review,
  legacy handling, bounded canonical and Tapestry input trust, untrusted secondary
  references, fixed isolated literal-dot installed-helper invocation, shared
  acquisition protocol, safe parent/child-lock lifecycle, provisional/final owner
  metadata, target ignore bootstrap, pointer lifecycle, the cooperative
  planned-work-only lock, resume reconciliation, and the native TODO prompt
  contract.
- `.gitignore`, `opencode/workflow-tools/start_work_state.py`, and
  `tests/test_start_work_state.py`: define the two exact ignored runtime-state
  entries and executable active-workspace invocation, parent-bootstrap,
  provisional/final ownership, pointer, path, input, fault-recovery, and
  planned-work lock behavior.
- `audit-technical-debt.md`, `investigate-regression.md`, and the Weave cleanup
  checklist: repair only stale lifecycle routes and authority language.
- `opencode/manifest.json`, `tools/opencode_manager.py`,
  `tests/test_opencode_manager.py`, and applicable `Justfile` reporting: own the
  exact one-item runtime-helper inventory, trusted regular source validation,
  descriptor-bound configuration-root and three-link setup/verify/uninstall/
  rollback contract, active-workflow inventory, obsolete-token diagnostics,
  retained-route mutation coverage, effective state-action tests, and
  repository-only integration contract.

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
  no retired command, split-command replacement, or alias; confirm the separate
  `runtime_helpers` inventory contains only
  `workflow-tools/start_work_state.py` and its source is regular, non-symlinked,
  and inside the trusted checkout;
- inspect focused installer evidence for the exact `agents`, `commands`, and
  `workflow-tools` destination/source relationships, all-destination preflight,
  dry-run, verify, doctor, idempotency, helper visibility, hostile/foreign/broken/
  mismatched rejection, rollback/restoration, mixed ownership, and uninstall.
  Confirm every mutable configuration-root ancestor is a stable real directory
  outside source checkouts and target workspaces; safe missing-final creation
  creates and binds only `opencode`; path/device/inode identity and each
  destination are revalidated before every mutation/success position; mutations
  are no-follow descriptor-relative where supported; root/destination swaps fail
  closed; partial rollback is exact; and no unrelated repository, target, or
  sentinel byte changes;
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
- inspect executable helper evidence for the exact `python3 -I
  "$HOME/.config/opencode/workflow-tools/start_work_state.py"
  <literal-operation> --repo-root .` command, literal operation/root argv, normal
  runtime approval, no human or repository shell content, and no concatenation,
  redirection, pipes, substitution, or extra operations. Confirm special-character
  workspace names execute no marker or target-local executable/module and retain
  state locally; nested/mismatched/aliased/symlinked/unrelated/alternate roots
  fail; and later machine-derived token/path values pass closed grammar as one
  argv element;
- inspect helper state evidence for first-use parent creation, parent/child
  contender races, crash-before-child recovery, crashes/partial writes before
  provisional metadata, crash after provisional metadata, empty-parent reuse/
  cleanup, parent type/symlink rejection, unsupported-child failure, no pre-child
  locator parsing or target-content reads, fresh post-lock reload, exact bounded
  provisional `plan_path: null` and final canonical metadata, bounded barrier
  exclusion, every second contender losing without target reads, route-complete
  no-path/explicit/legacy/conversion finalization, duplicate/conflicting
  finalization, token mismatch, matching-owner release, pre-mutation provisional
  release, post-mutation/uncertain retention, direct/delegated termination and
  cancellation retention, plan-only release, execution retention, unrelated
  writes remaining unblocked, stale-lock confirmation, pointer corruption/
  containment/hash/clear/deletion behavior, exact target-ignore bootstrap/failure
  behavior, 1 MiB/UTF-8 changing-file boundaries, effect-before-checkbox
  recovery, and satisfied-evidence duplicate suppression;
- inspect secondary-reference spy evidence for every required unsafe path and
  shell-shaped string and confirm zero secondary reads and zero command
  executions;
- inspect prompt-contract evidence for every `/start-work` branch,
  `/convert-tapestry-plan`, and equivalent ordinary Plan Orchestrator conversation;
  confirm fixed isolated literal-dot invocation, no locator in helper launch,
  shared acquisition, no pre-lock locator parsing or source/state/allocation
  reads, provisional/final ownership, fresh reload, plan-only hold/release,
  execution retention, and read-only no-mutation exemption; also inspect
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
permission boundary. Revision 5 resolves the remaining Board findings with the
shared route protocol, fixed trusted installed-helper path, three-link
distribution model, target ignore bootstrap, and safe first-use parent/child
acquisition. The lock serializes Plan Orchestrator sessions and all direct or
delegated implementation for their plans; it is not a general repository mutation
lock and grants Lead, ERB, and Worker no state authority. Revision 6 closes the
implementation-mechanics findings without changing those selections: helper
runtime is fixed to isolated Python plus literal active-workspace `--repo-root .`,
machine-local link operations are bound to a validated configuration-root
descriptor and stable identity, and child-lock ownership transitions atomically
from provisional `plan_path: null` to one canonical final plan path. There is no
remaining human product, workflow, or architecture decision.

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

plan_path: docs/implementation-plans/plans/opencode/02-simplify-plan-workflow.md
plan_id: opencode-02
revision: 4
baseline_commit: 9bd28e3a15c237e1fb4cf6e1996da36b687db5e8
decision: ready-with-revisions
reviewed_at: 2026-07-14T20:05:00-04:00
findings: Required revisions R4-1 through R4-3 in this Board record.
next_command: /record-plan-review docs/implementation-plans/plans/opencode/02-simplify-plan-workflow.md

plan_path: docs/implementation-plans/plans/opencode/02-simplify-plan-workflow.md
plan_id: opencode-02
revision: 5
baseline_commit: 9bd28e3a15c237e1fb4cf6e1996da36b687db5e8
decision: ready-with-revisions
reviewed_at: 2026-07-14T22:40:00-04:00
findings: Required revisions R5-1 through R5-3 in this Board record.
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

### Revision 5 — 2026-07-14

- Applied R4-1 through R4-3 from the persisted revision-4 ERB
  `ready-with-revisions` record: one shared acquisition/fresh-load/hold protocol
  for `/start-work`, `/convert-tapestry-plan`, and equivalent ordinary Plan
  Orchestrator conversation; the trusted installed
  `~/.config/opencode/workflow-tools/start_work_state.py` distribution path with
  an exact one-item manifest inventory and paired third directory link; and safe
  fresh-target parent bootstrap with atomic child-lock exclusion.
- Added first-use target `.gitignore` bootstrap under the child lock, fixed-path
  explicit-target invocation, hostile target-local helper rejection, all-three
  setup/verify/uninstall/rollback coverage, unrelated-target isolation, and
  deterministic parent race, crash-residue, no-pre-lock-read, plan-only, execution
  retention, and unrelated-write tests. No target-local helper, custom tool,
  broad Bash allow, broad ignore rule, or project-bootstrap overwrite was added.
- Preserved the revision-2, revision-3, and revision-4 ERB records and all prior
  amendments verbatim, retained the implementation baseline and full source-drift
  evidence through `34da83a`, and reset this material revision to draft/pending
  with current review and approval fields clear. `depends_on` remains empty and no
  approval was added.

### Revision 6 — 2026-07-15

- Applied R5-1 through R5-3 from the persisted revision-5 ERB
  `ready-with-revisions` record: fixed isolated active-workspace helper invocation
  with literal `--repo-root .` and closed argv construction; fail-closed,
  descriptor-bound machine-local configuration-root ownership across setup,
  dry-run, verify, doctor, uninstall, rollback, and restoration; and atomic
  provisional-to-final `.start-work/lock/owner.json` ownership.
- Added deterministic shell-shaped workspace, target-local import/executable,
  nested/aliased/mismatched root, mutable configuration-ancestor and destination
  substitution, safe/unsafe missing-root, provisional crash/partial-write,
  route-finalization, token-mismatch, duplicate/conflicting finalization, and
  mutation-aware release coverage. Runtime approval, the standard-library-only
  helper, one-item helper inventory, three-link installation, target ignore
  bootstrap, and planned-work-only lock remain unchanged.
- Preserved the revision-2 through revision-5 ERB records and all prior amendments
  verbatim, retained baseline
  `9bd28e3a15c237e1fb4cf6e1996da36b687db5e8` and complete source-drift evidence
  through `dfc6c7f`, kept `depends_on: []`, and reset this material revision to
  draft/pending with current review and approval fields clear. No approval was
  added.

## Execution Record

None.
