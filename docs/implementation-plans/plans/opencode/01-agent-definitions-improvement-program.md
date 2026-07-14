---
plan_id: opencode-01
series: opencode
sequence: 1
title: OpenCode Agent Definitions Improvement Program
status: draft
revision: 3
review_decision: pending
reviewed_at:
approved_at:
approved_revision:
depends_on: []
baseline_commit: 9bd28e3a15c237e1fb4cf6e1996da36b687db5e8
execution_owner: engineering-lead
source_format: native
source_plan:
created: 2026-07-14
updated: 2026-07-14
completed_at:
---

# OPENCODE-01 — OpenCode Agent Definitions Improvement Program

## Executive Summary

Close the audited lifecycle, authority, evidence-handling, and permission-validation
gaps in the repository-managed OpenCode definitions without changing the current
23-agent inventory. The work adds one Lead-owned command,
`/record-implementation-review`, so an independent completed-work review can be
bound to a current-HEAD, one-parent implementation commit, persisted through
`planning-coordinator`, and returned to an executable state when corrections are
required. A pure read-only plan module and CLI will compute lifecycle,
dependency, attempt, commit-identity, and exact target-plan-delta results; the
Coordinator remains the only plan writer.

The plan keeps the Engineering Review Board (ERB) as a separate read-only
primary, retains Coordinator-only durable plan writes, and leaves all existing
agent filenames and runtime IDs intact. It preserves the maintainer-authorized
Lead clipboard and configured MCP-prefix rules exactly. LSP-assisted navigation
remains available. Operator documentation will state that a trusted language
server can start as a process outside Bash permission checks, so machine-local
LSP and download configuration remains an explicit trust boundary.

## Problem and Context

The current definitions encode most governance in prompts and permission maps,
but several important relationships are not durable or validator-enforced.
`/execute-plan` always returns `/review-implementation`, including when execution
records a blocker, while the review command can return Request Changes without a
command that persists the Board record and reopens execution. Approval and
revision wording can also duplicate ERB plan-review history. Separately, the
validator accepts any manifested primary as a command owner, permits primary
agents to add arbitrary manifested subagents, and does not protect the Worker's
full destructive-command deny suffix.

The audit also found that `security-critic` and `technical-researcher` discuss
secrets but do not require sanitized evidence or prohibit transmitting sensitive
values to external sources. The same boundary is not carried through completed
implementation review, Lead recording, Coordinator persistence, or durable
history. Lifecycle and dependency rules are still prompt contracts rather than a
read-only executable oracle. All 23 agents expose LSP navigation, yet the tracked
guidance does not tell operators that language-server launch and download
behavior is governed by machine-local trust rather than the agents' Bash rules.

Commit `9bd28e3a15c237e1fb4cf6e1996da36b687db5e8` has already added explicit
maintainer-authorized Lead access to `pbcopy *` and the configured MCP prefixes.
That commit is baseline evidence, not output of this plan. This program must add
regression coverage without removing, narrowing, or reinterpreting that access.

## Objectives

- Give completed implementation review a durable, Lead-mediated record and an
  explicit transition for Approve, Approve With Follow-ups, and each Request
  Changes disposition.
- Bind every completion and implementation review to a never-reused attempt ID,
  a full current-HEAD one-parent non-merge commit reference, and its exact parent.
- Require dependencies to have a reviewed latest completion, not merely a
  `completed` top-level status.
- Enforce the existing agent modes, command owners, one-level Task graph, and
  exclusive Lead access to `planning-coordinator` and `implementation-worker`.
- Remove approval and revision wording that can create duplicate ERB plan-review
  entries; validate exact operation-to-history and decision-to-transition
  relationships.
- Carry one sanitized, non-exfiltrating evidence boundary from specialists and
  the ERB through review, recording, Coordinator handoff, CLI output, and durable
  Implementation Review History, backed by end-to-end synthetic mutation tests.
- Protect the Worker's current deny rules for commit, push, hard reset, clean,
  `rm`, `sudo`, and plan-path shell access with a deterministic OpenCode
  v1.18-compatible last-match oracle.
- Preserve the Lead's human-authorized `pbcopy *`, `playwright_*`,
  `chrome-devtools_*`, `serena_*`, `context7_*`, `gh_grep_*`, and `github_*`
  rules and reject removal or action downgrade of every rule.
- Add a pure read-only lifecycle/dependency API and CLI that validates structured
  records, exact transitions, commit identity, dependency state, and the only
  permitted target-plan lifecycle delta without writing a plan.
- Document the selected trusted-LSP exception without claiming process-free
  review or inventing a per-agent LSP sandbox.
- Keep repository docs, the project template, the manifest, validation, and tests
  synchronized.

## Non-Goals

- Split, merge, create, rename, or retire an agent; all 23 current agent IDs stay.
- Rewrite specialist prompts for stylistic consistency or change their models,
  reasoning settings, or review domains.
- Modify first-party or third-party skills, skill inventory, or machine-local
  runtime installs.
- Pin or install OpenCode, models, language servers, MCP servers, providers, or
  plugins.
- Change credentials, provider settings, live `opencode.jsonc`, or other
  machine-local configuration.
- Disable LSP globally, promise process-free review, or simulate a platform
  feature that isolates LSP per agent.
- Weaken explicit human plan approval, ERB independence, Coordinator-only plan
  writes, Worker scope limits, or the one-level Task topology.
- Introduce another planning, approval, implementation, or review authority.

## Applicable Project Guidance

- `AGENTS.md` requires the repository README, skill taxonomy, cross-reference
  map, and engineering governance guide to be read before repository-doc changes.
  It also requires `just validate` for link or routing-doc changes and `just
  check` when tooling, tests, or validation behavior changes.
- `README.md` defines `opencode/manifest.json` as the reviewed inventory, treats
  the checked-out definitions as live after OpenCode restart, and keeps
  credentials and live configuration outside the repository.
- `docs/engineering-agent-governance.md` owns role authority, exact runtime IDs,
  one-level Task boundaries, command ownership, and independent-review handoffs.
- `docs/implementation-plans/README.md` and `TEMPLATE.md` define canonical plan
  identity, lifecycle metadata, review persistence, approval, and synchronized
  project-template copies.
- The Planning Coordinator is the only writer under
  `docs/implementation-plans/**`. The ERB remains read-only and must run as a
  separate primary. If implementation is delegated, the Lead may use only
  `implementation-worker`.
- Project-neutral wording and exact filename-stem runtime IDs must be preserved.

## Current-State Evidence

- Revision-3 baseline inspection confirmed `HEAD` at
  `9bd28e3a15c237e1fb4cf6e1996da36b687db5e8` on 2026-07-14. Fresh
  `git status --short` reported only the untracked canonical plan directory.
  The supplied path-safety evidence states that the plan root, plans directory,
  `opencode` series directory, and target plan are non-symlinks and resolve under
  `docs/implementation-plans/`.
- The intervening baseline commit is `9bd28e3 feat(opencode): authorize lead tool
  access`. It changed `docs/engineering-agent-governance.md`,
  `opencode/agents/engineering-lead.md`, `tools/opencode_manager.py`, and
  `tests/test_opencode_manager.py`. Treat those changes as pre-existing baseline
  work, not execution output for this plan.
- The current Lead permission map allows `pbcopy *`, `playwright_*`,
  `chrome-devtools_*`, `serena_*`, `context7_*`, `gh_grep_*`, and `github_*`.
  Governance names that access as explicit human authorization.
  `tools/opencode_manager.py` has dedicated Lead clipboard and MCP constants and
  rejects a missing configured MCP prefix. Existing tests prove the valid set and
  one incomplete-prefix case, but do not table-drive removal and action downgrade
  for `pbcopy` and every prefix.
- `opencode/manifest.json` lists 23 agents and 11 commands. The definition
  frontmatter has exactly two primaries, `engineering-lead` and
  `engineering-review-board`; the other 21 agents are subagents. Every current
  agent has LSP permission enabled.
- `engineering-lead` is the only current Task parent for
  `planning-coordinator` and `implementation-worker`. The ERB has its own review
  roster, while every subagent has a deny-only Task baseline and no delegation
  edge.
- `tools/opencode_manager.py::_validate_task_delegation` rejects recursive
  subagent delegation and unknown targets, but it accepts any primary-to-subagent
  allow edge. `_validate_command_agents` checks only that a command owner is a
  manifested primary. Neither function compares modes, owners, or primary
  allowlists to the repository's canonical topology.
- `tests/test_opencode_manager.py` proves generic primary ownership is currently
  accepted through its `reviewer` fixture. Existing tests cover unknown command
  owners, subagent command ownership, recursive delegation, permission baseline
  ordering, core edit ownership, and plan redirection; they do not mutate the
  canonical two-primary roster, exact command-owner map, or complete primary
  Task graph.
- `opencode/commands/execute-plan.md` routes its completion report to
  `/review-implementation <path>` even though the same command permits a
  `blocked` lifecycle update. `review-implementation.md` returns Approve,
  Approve With Follow-ups, or Request Changes but provides no structured durable
  record or next command.
- `approve-plan.md` instructs the Coordinator to add “a matching ERB
  review-history and approval record” after `/record-plan-review` already wrote
  the matching ERB record. `revise-plan.md` says to append “amendment/review
  history,” which can create a second review entry before another independent
  ERB review occurs.
- `security-critic.md` covers secret handling as a review subject, and
  `technical-researcher.md` prohibits invented citations and versions. Neither
  prompt mandates redaction, synthetic examples, data minimization, or a ban on
  putting repository secrets into search, fetch, citation, or report content.
- `implementation-worker.md` currently ends its Bash rules with denies for
  `git commit *`, `git push *`, `git reset --hard *`, `git clean *`, `rm *`,
  `sudo *`, and `*docs/implementation-plans*`. The validator checks only the
  final plan-path rule and does not preserve the complete deny suffix.
- The root implementation-plan README and template are byte-compared with their
  copies under `opencode/project-template/`. The validator also checks selected
  template metadata and headings, so lifecycle-template changes must update both
  copies and their validator expectations together.
- `opencode/config/opencode.merge-fragment.jsonc` currently contains only a
  schema reference and `default_agent`. It is documented as a merge reference,
  not live configuration.
- The supplied `technical-researcher` memo verified OpenCode v1.18 behavior for
  filename-stem IDs, last-match permissions, `reasoningEffort` provider options,
  command routing, and LSP process launch. Official v1.18 source also confirms
  that a terminal space-plus-wildcard suffix is optional, so a pattern such as
  `git commit *` matches both `git commit` and `git commit <arguments>`. The
  installed OpenCode version and the effective machine-local LSP/MCP
  configuration were not verified.
- `tools/opencode_plan.py` and `tests/test_opencode_plan.py` do not exist at this
  baseline. Runtime lifecycle, dependency, commit identity, duplicate/conflict,
  and target-plan-delta behavior therefore has no named pure executable oracle.
- No canonical plan directory existed under `docs/implementation-plans/plans/`
  at allocation time, so this series starts at sequence `01` with no dependency.
- The two persisted 2026-07-14 ERB reviews match this plan's canonical path and
  `opencode-01` identity. They remain historical evidence for revisions 1 and 2,
  each at baseline `f80ae0d22a7dfebafdbb679c13e4ea5a5860b014` with decision
  `ready-with-revisions`; rebaselining revision 3 does not rewrite either record.
- Planning-time `just validate-opencode` was not run because this Coordinator's
  Bash policy denies `just`; execution-time validation remains mandatory below.

## Proposed Design

### Canonical topology and ownership contract

Represent repository authority as explicit validator constants rather than
deriving authority from whatever the manifest happens to contain:

- a canonical mode map for all 23 existing filename-stem IDs, with only
  `engineering-lead` and `engineering-review-board` marked primary;
- an exact command-owner map, extended only by the new Lead-owned
  `record-implementation-review.md` command;
- exact primary Task allowlists matching the current Lead and ERB edges, while
  retaining the existing rule that subagents cannot delegate; and
- an explicit invariant that only `engineering-lead` may target
  `planning-coordinator` or `implementation-worker`.

Validation must fail if the manifest and those maps diverge, a mode flips, a
command changes owner, an edge is added or removed, or another role gains access
to the Coordinator or Worker. Diagnostics should name the violated contract
without copying prompt content or sensitive values.

### Durable post-implementation review and commit identity

Add `opencode/commands/record-implementation-review.md` with
`agent: engineering-lead` and `subtask: false`; add it to the manifest and the
governance command table. `/review-implementation` remains ERB-owned and
read-only.

Every successful initial or corrected completion appends an immutable attempt to
`Execution Record`. `attempt_id` is a positive base-10 integer: the first attempt
is `1`, each later attempt uses the greatest historical attempt ID plus one, and
IDs are never reset, reused, or renumbered across revisions. Each attempt records
the exact plan path, plan ID, revision, baseline commit, ISO-8601 completion time,
`implementation_reference: commit:<40-lowercase-hex-current-HEAD>`, and
`implementation_parent: <40-lowercase-hex>`.

A completion is reviewable only when current `HEAD` is that full,
unabbreviated implementation commit, the commit has exactly one parent, is not a
merge, and contains the complete implementation scope intended for review. The
reference and parent must resolve to commits, `HEAD^` must equal
`implementation_parent`, and the `HEAD^..HEAD` change must be content-bearing.
The implementation commit is immutable after the attempt is recorded.

This plan does not grant commit authority. `/execute-plan` must stop before a
review-ready completion unless the human explicitly requested one coherent
implementation commit. Without that authorization, the Coordinator records a
non-material execution blocker with the resolution condition “human explicitly
authorizes the one coherent implementation commit”; the Lead must not commit
automatically. This is an execution gate governed by Git policy, not an open
product, architecture, or security decision.

The ERB uses its already-allowed `git show HEAD`, `git show HEAD^`, and
`git diff HEAD^ HEAD` forms to inspect the implementation commit. If the approved
plan baseline predates `HEAD^`, the Lead must make the content-bearing
baseline-to-current evidence required by the Board contract available without
granting the Board permission to run newly changed repository code; the Board
cannot return `ready` without that evidence. No raw patch, binary bundle,
artifact path, hash-helper output, or evidence blob crosses session or command
boundaries.

`/review-implementation` copies the latest attempt's exact path, plan ID,
revision, baseline, `attempt_id`, completion time, implementation reference, and
implementation parent into one structured record. The record also contains the
decision, Request Changes disposition when applicable, review time, sanitized
findings or owned follow-ups, and
`next_command: /record-implementation-review <path>`.

The recording command requires exact equality between current `HEAD`, the
`commit:` reference, `HEAD^`, the recorded parent, and the latest attempt. It
rejects a stale, partial, older-attempt, cross-attempt, mismatched, or conflicting
record. Before mutable worktree or Git identity checks, it first compares the
complete candidate record with the already-persisted record for that attempt. A
byte-equivalent record is an idempotent no-op with no history, metadata, or
`updated` change; any changed field is a conflict.

No prompt may claim it can infer that review text was self-authored. Before
recording, the Lead must procedurally verify that the complete record came from a
separate top-level `engineering-review-board` session and report that check in
the Coordinator handoff. This is an origin check by the Lead, not a runtime
authorship detector.

Add `Implementation Review History` to the canonical template and backfill the
heading when a plan lacks it. This self-hosting plan received the empty section
in revision 2, before its first completed-work review.

### Commit/worktree cleanliness and exact plan delta

The implementation commit is the only implementation-content boundary. At
completion, independent review, and review recording, reject every staged,
unstaged, untracked, ignored, unsupported, or unattributed non-plan change
outside that commit. Outside the exact target plan path, reject any changed plan
under `docs/implementation-plans/plans/**`; there is no blanket plan-subtree
exclusion.

The exact target plan may differ from its `HEAD` version only by the
schema-valid, Coordinator-authored lifecycle delta expected for the authorized
transition. The allowed surface is the transition's top-level review, approval,
execution, or implementation-review metadata plus the corresponding append-only
history entry. Reject body edits, another plan, an unexpected metadata or history
mutation, unsupported file types, symlink entries or aliases, and any change not
justified by the latest authorized transition. Coordinator lifecycle changes are
not implementation content and must never be included in or relabeled as the
implementation commit.

The read-only validator described below compares the committed target plan with
the worktree plan and replays each authorized post-`HEAD` lifecycle append. It
must accept exactly one fixture containing the expected target-plan delta and
reject fixtures for a changed second plan, an unrelated target-plan body edit,
an unsupported or symlink entry, and an unexpected lifecycle mutation.

### Read-only lifecycle and dependency oracle

Add a pure module and CLI at `tools/opencode_plan.py`, with focused tests in
`tests/test_opencode_plan.py`. It may read plans, sanitized JSON records, Git
object identity, and worktree metadata. It must never write a plan or other
repository file, invoke network/MCP/clipboard tools, or print raw sensitive
values. The Lead runs it before asking the Coordinator to persist a lifecycle
change and again after persistence. The ERB receives no permission to run this
new repository code.

The CLI surface is fixed:

```sh
python3 tools/opencode_plan.py evaluate-transition --plan <canonical-plan-path> --record <sanitized-json-path>
python3 tools/opencode_plan.py validate-review --plan <canonical-plan-path> --record <sanitized-json-path>
python3 tools/opencode_plan.py validate-dependencies --plan <canonical-plan-path>
python3 tools/opencode_plan.py verify-persisted --plan <canonical-plan-path> --record <sanitized-json-path>
```

Each record file uses this envelope; unknown or missing keys fail closed:

```json
{
  "schema": "opencode-plan-transition-v1",
  "operation": "record-plan-review|approve-plan|revise-plan|record-execution|record-implementation-review",
  "plan_path": "docs/implementation-plans/plans/<series>/<NN>-<slug>.md",
  "plan_id": "<series>-<NN>",
  "revision": 1,
  "baseline_commit": "<40-lowercase-hex>",
  "record": {}
}
```

The operation payloads are exact:

- `record-plan-review`: `reviewed_at`, `review_decision`, `findings` as sanitized
  strings, and `next_command`; `review_decision` is `ready`,
  `ready-with-revisions`, or `not-ready`.
- `approve-plan`: `approved_at`, `approved_revision`,
  `authorized_by: "explicit-human-/approve-plan"`, and the exact persisted
  `reviewed_at` it consumes.
- `revise-plan`: `updated`, `next_revision`, `source_history`,
  `source_recorded_at`, optional `attempt_id`, and `classifications` as sanitized
  strings; `source_history` is `ERB Review History` or
  `Implementation Review History`.
- `record-execution`: `outcome: "completed"|"blocked"`, `recorded_at`, and
  `next_command`. A completed payload also requires `attempt_id`, `completed_at`,
  `implementation_reference`, and `implementation_parent`; a blocked payload
  instead requires `blocker_summary` and `resolution_condition`, both sanitized.
- `record-implementation-review`: `attempt_id`, `completed_at`,
  `implementation_reference`, `implementation_parent`, `decision`, nullable
  `request_changes_disposition`, `reviewed_at`, sanitized `findings`, sanitized
  `follow_ups` objects with `summary`, `owner`, and `verification`, and
  `next_command`.

`decision` is exactly `Approve`, `Approve With Follow-ups`, or `Request Changes`.
The disposition is null for the two approving decisions and exactly
`in-scope-executable`, `in-scope-blocked`, or `material` for Request Changes.
All listed keys are required except the explicitly optional `attempt_id`; extra
keys fail. Plan/review IDs and path must match the plan, revisions and attempt IDs
are positive base-10 integers, commit fields are lowercase 40-hex, and timestamps
are ISO-8601 strings. `findings` and `classifications` are arrays of sanitized
strings. `follow_ups` is empty for `Approve` and `Request Changes` and is a
nonempty array of the specified objects for `Approve With Follow-ups`.
`approved_revision` equals the envelope revision, `next_revision` equals revision
plus one, and every `next_command` must equal the lifecycle matrix rather than
arbitrary input. No new top-level plan metadata field is introduced.

Every subcommand emits one sanitized JSON object using schema
`opencode-plan-result-v1` with only `ok`, `result`, `operation`, `status`,
`completed_at`, `history_destination`, `next_command`, and sanitized
`diagnostics`; non-applicable values are null. `result` is one of `apply`,
`duplicate-no-op`, `valid`, `satisfied`, `blocked`, or `conflict`. Exit status is
zero only for `apply`, `duplicate-no-op`, `valid`, or `satisfied`.

The pure API parses plan-history fixtures, computes the exact transition and
dependency result without writing, validates full current-HEAD/parent identity,
rejects stale or crossed attempts and conflicting records, and validates the
exact target-plan lifecycle delta. `validate-review` must return
`duplicate-no-op` before reading mutable Git/worktree evidence when the candidate
is byte-equivalent to persisted history. `verify-persisted` must prove the
expected record is the latest append, metadata matches the computed result, the
body is unchanged, and no disallowed plan or worktree delta exists. Diagnostics
identify only a sanitized location and failure type.

Keep the compact prompt transition/history blocks and their static mutation
checks in `tools/opencode_manager.py`. Those checks prove only that tracked prompt
associations retain the required text; they do not prove runtime lifecycle or
dependency behavior. Executable claims come from the read-only plan module and
its plan-history fixtures.

### Lifecycle transition contract

Every durable history append refreshes top-level `updated` to the append date.
The transition table is authoritative; append order, not user-supplied
timestamps, determines which attempt and review are latest.

| Trigger | Resulting status | `completed_at` | History destination | Immediate command after persistence | Fields that stay unchanged |
| --- | --- | --- | --- | --- | --- |
| Initial or corrected execution completion | `completed` | Set to the fresh completion time, also stored on the new immutable attempt | `Execution Record` | `/review-implementation <path>` | Revision; plan-review state; approval fields; identity, baseline, dependencies, and owner |
| Execution blocker before completion | `blocked` | Clear top-level value; preserve prior attempt times in history | `Execution Record` | `/execute-plan <path>` after documented resolution, or `/revise-plan <path>` for material change | Revision; plan-review state; approval fields; prior records; identity, baseline, dependencies, and owner |
| `Approve` | `completed` | Preserve the matched attempt's completion time | `Implementation Review History` | None; terminal for this plan | Revision; plan-review `reviewed_at`/`review_decision`; approval fields; attempt and plan identity |
| `Approve With Follow-ups` | `completed` | Preserve the matched attempt's completion time | `Implementation Review History` | `/prepare-work <follow-up request>` for separate classification | Revision; plan-review `reviewed_at`/`review_decision`; approval fields; attempt and plan identity |
| `Request Changes`, in-scope and executable | `in-progress` | Clear top-level value; preserve the matched completion time in history | `Implementation Review History` | `/execute-plan <path>` | Revision; plan-review `reviewed_at`/`review_decision`; approval fields; attempt and plan identity |
| `Request Changes`, in-scope but blocked | `blocked` | Clear top-level value; preserve the matched completion time in history | `Implementation Review History` | `/execute-plan <path>` after the blocker is resolved | Revision; plan-review `reviewed_at`/`review_decision`; approval fields; attempt and plan identity |
| `Request Changes`, material | `blocked` | Clear top-level value; preserve the matched completion time in history | `Implementation Review History` | `/revise-plan <path>` | Revision until revision runs; plan-review `reviewed_at`/`review_decision`; approval fields; attempt and plan identity |

Approve With Follow-ups may contain only non-blocking work with an owner and
verification condition. Anything needed to satisfy the current plan's acceptance
criteria or guardrails is Request Changes. The validator encodes, and mutation
tests exercise, this compact post-record association block rather than an entire
prompt snapshot:

```text
POST_RECORD_TRANSITIONS_V1
Approve|completed|Implementation Review History|none
Approve With Follow-ups|completed|Implementation Review History|/prepare-work <follow-up request>
Request Changes:in-scope-executable|in-progress|Implementation Review History|/execute-plan <path>
Request Changes:in-scope-blocked|blocked|Implementation Review History|/execute-plan <path> after resolution
Request Changes:material|blocked|Implementation Review History|/revise-plan <path>
```

`/execute-plan` sends only a newly `completed` attempt to
`/review-implementation`. A correction creates a new attempt and therefore needs
a new independent review; review evidence from one attempt can never approve or
reopen another attempt at the same plan revision.

### Authoritative dependency gate

For each exact ID in `depends_on`, `/execute-plan` and the Coordinator's
execution update must inspect history as well as frontmatter. A dependency is
satisfied only when all three conditions hold:

1. Its current status is `completed`.
2. Its latest completed attempt has an exact-matching persisted implementation
   review with decision `Approve` or `Approve With Follow-ups`, including the same
   path, plan ID, revision, baseline, attempt ID, completion time, and
   implementation reference and implementation parent.
3. No later completion attempt or `Request Changes` record exists in append
   order.

A dependent plan remains blocked when a dependency is completed but unreviewed,
after any Request Changes record, and after corrected completion until that new
attempt receives and persists an approving review. Fail closed on missing or
ambiguous history. This rule belongs in `/execute-plan`, lifecycle guidance, the
Coordinator execution contract, and validator-backed command associations.

### Review-history provenance

Keep pre-approval review, approval, amendment, execution, and implementation
review as separate histories:

- `/record-plan-review` remains the only command that appends an ERB plan-review
  entry.
- `/approve-plan` appends only an approval entry that references the already
  persisted matching ERB review by its review time and exact identity tuple. It
  must not copy or append that review again.
- `/revise-plan` accepts either the latest exact-matching pre-approval ERB review
  or the latest exact-matching material Request Changes entry. For implementation
  evidence it also validates the latest attempt ID, completion time, and
  implementation reference and parent. It maps that evidence into one amendment,
  increments revision, resets status/review/approval state, and clears top-level
  `completed_at`; the next ERB record appears only after `/review-plan` and
  `/record-plan-review` run again.
- `/record-implementation-review` appends only to `Implementation Review
  History`, plus the lifecycle metadata required by its decision.

The validator protects exact operation-to-history associations with a second
compact block:

```text
HISTORY_APPEND_AUTHORITY_V1
/record-plan-review|ERB Review History
/approve-plan|Approval History
/revise-plan|Amendments
/execute-plan|Execution Record
/record-implementation-review|Implementation Review History
/review-plan|none
/review-implementation|none
```

Mutation tests swap each tuple field while retaining the same vocabulary. They
must reject Approve routed to execution, material Request Changes reopened
directly, approval appending `ERB Review History`, revision appending a review
record, and every other wrong association represented by these blocks. Keep
validation limited to authority, provenance, transitions, and non-exfiltration;
do not parse general natural language or snapshot full prompts.

### End-to-end sanitized implementation-review evidence

Use one canonical non-exfiltration boundary in `security-critic`,
`technical-researcher`, `engineering-review-board`, `change-verifier`, every
other implementation-review specialist selected by the Board,
`/review-implementation`, `/record-implementation-review`, the Engineering Lead
evidence packet, `planning-coordinator`, CLI diagnostics, and persisted
`Implementation Review History`.

Raw sensitive values must never enter findings, delegated prompts, command
arguments, clipboard input, MCP or network requests, URLs, queries, citations,
diagnostics, stdout/stderr, Coordinator packets, or durable history. Use only
synthetic placeholders or location/type-only descriptions. The Coordinator may
receive only verified identity metadata, the decision, and sanitized
findings/follow-ups. If a live credential is discovered, stop review, report only
its sanitized location and type, and require removal and rotation before review
continues.

This is an evidence-use restriction, not a permission revocation. Preserve the
Lead's authorized clipboard and MCP rules unchanged.

Use this compact prompt contract wherever static validation applies:

```text
NON_EXFILTRATION_V1
sensitive-value-output|synthetic-placeholder-or-location-and-type-only
forbidden-channel|finding|delegated-prompt|command-argument|clipboard-input|mcp-request|network-request|url|query|citation|diagnostic|stdout|stderr|coordinator-packet|durable-history
coordinator-packet|verified-identity|decision|sanitized-findings-and-follow-ups-only
live-credential|stop|location-and-type-only|remove-and-rotate-before-resume
```

Tests use an obviously synthetic sentinel in temporary fixtures. In addition to
removing safeguards, add contradictory disclosure text for each forbidden
channel while leaving the valid block untouched. Carry the sentinel through
specialist output, ERB output, recording input/output, Lead-to-Coordinator
packets, CLI output, and persisted history, and assert that it is absent from all
results, messages, warnings, errors, stdout, and stderr. No real credential,
secret-shaped local value, live endpoint, or machine-local secret belongs in a
test.

### Protected permission contracts

Treat the Lead's `pbcopy *` Bash allow and all six configured MCP-prefix allows
as human-authorized invariants. Table-driven tests must remove each rule and
change each action to `ask` and `deny`; every case fails. Preserve exactly
`pbcopy *`, `playwright_*`, `chrome-devtools_*`, `serena_*`, `context7_*`,
`gh_grep_*`, and `github_*`. Do not remove, narrow, reorder into ineffectiveness,
or reinterpret this authorization.

Treat the Worker's current seven Bash denies as a final canonical suffix because
OpenCode permission evaluation uses the last matching rule. Validation must
require each deny with its current action and order, rejecting removal, an
`allow`/`ask` mutation, reordering that permits a later match, or a later rule
that weakens one of the denied command families. Preserve the strings exactly:
`git commit *`, `git push *`, `git reset --hard *`, `git clean *`, `rm *`,
`sudo *`, and `*docs/implementation-plans*`.

Add a small deterministic `resolve_v118_permission_action` oracle in
`tools/opencode_manager.py`. It accepts ordered `(pattern, action)` rules plus a
concrete command string, applies the documented v1.18 glob and last-match model,
including the optional terminal ` *` behavior, and returns the final action. It
does not inspect or claim to model the installed runtime.

For each of the seven Worker patterns, table-driven tests exercise representative
matching and non-matching concrete values, the documented bare/argument-bearing
forms where applicable, and a later weakening rule. Static validation still
rejects membership, action, and ordering drift. This oracle proves repository
compatibility with the documented OpenCode v1.18 model, not behavior of the
installed runtime. Machine-enforced acceptance remains limited to this suffix,
the existing plan edit denial, no delegation, network denial, and the protected
Lead rules. Unchanged safe inspection allows receive a manual
no-unrelated-permission-change diff check; do not add a second allowlist.

### Trusted LSP operator boundary

Retain LSP-assisted navigation and all current `lsp` permissions. Update the
repository README and engineering governance guide to state that an LSP tool may
start an operator-configured language-server process and may trigger
server-specific download or network behavior. Bash denial does not block that
path, and read-only therefore does not mean process-free.

Operator guidance must direct users to trust and inspect the effective
machine-local OpenCode/LSP/MCP configuration, server executable or package
source, and download behavior before enabling navigation on sensitive
repositories. Verification should record the installed OpenCode version, the
configured server command/source, and whether a controlled navigation check
starts only expected processes without exposing repository secrets. Do not add a
repository credential, a global LSP disable, or a fictitious per-agent process
sandbox. Keep `opencode/config/opencode.merge-fragment.jsonc` unchanged. It
contains only the schema reference and `default_agent`, while the authoritative
operator trust guidance belongs in README/governance; adding a merge-fragment
comment would duplicate guidance without adding a runtime control.

## Alternatives and Trade-offs

- **Add another agent for review persistence:** rejected. Persistence is a
  Coordinator operation mediated by the Lead; another agent would duplicate
  authority and violate the selected 23-agent disposition.
- **Let the ERB write the implementation-review record:** rejected because it
  breaks the Board's independent read-only boundary. The ERB returns evidence;
  the Lead verifies it and invokes the Coordinator.
- **Store completed-work decisions in `ERB Review History`:** rejected because
  pre-approval plan readiness and post-implementation acceptance have different
  identity, timing, and transitions. A dedicated history section prevents an
  implementation decision from being mistaken for plan approval evidence.
- **Review uncommitted implementation state:** rejected. It would require either
  transporting sensitive implementation content between sessions or allowing the
  ERB to execute newly changed repository code. A full current-HEAD one-parent
  commit plus its recorded parent gives each attempt an identity the Board can
  inspect with already-authorized read-only Git forms.
- **Grant the ERB permission to run the new lifecycle CLI:** rejected. The Lead
  runs the read-only oracle before and after Coordinator persistence; the Board
  stays independent and does not bootstrap trust by executing unreviewed code.
- **Treat dependency `status: completed` as sufficient:** rejected because an
  unreviewed or reopened dependency is not accepted implementation. The gate
  follows the latest completion and its exact implementation review.
- **Rely on prose without validator constants:** rejected. The current audit gap
  exists because permissive structural checks treat manifested authority as
  canonical authority.
- **Snapshot entire prompts in tests:** rejected. Full-text snapshots make safe
  copy edits expensive; compact relationship blocks and field-swapping mutation
  tests protect the intended associations without freezing editorial text.
- **Add operator guidance to the merge fragment:** rejected. The file is a merge
  reference containing only schema/default-agent data; README and governance are
  the tracked sources for the LSP trust boundary, so a config comment would
  duplicate policy without enforcing it.
- **Disable LSP for read-only roles:** rejected by the human-selected trusted-LSP
  exception and because it removes useful navigation. The trade-off is an
  operator-managed process and supply-chain boundary that Bash rules cannot
  contain.

## Dependencies

`depends_on` is empty because no earlier canonical plan exists and the audited
work forms one coordinated repository change. Within this plan, changes to
`tools/opencode_manager.py` and `tests/test_opencode_manager.py` share ownership
and must run serially or under one Worker. Lifecycle prompt, template, manifest,
and governance edits must land as one synchronized unit so validation never
observes a half-updated contract.

No package, OpenCode installation, machine-local setting, or external service is
an implementation dependency. Runtime LSP verification depends on operator
access to the target machine and may remain documented as skipped evidence; it
must not be fabricated from repository state.

Future plans that list dependencies consume the authoritative gate in this
revision. This plan's `depends_on: []` remains unchanged, so the stronger gate
adds no prerequisite to `opencode-01` itself.

## Specialist Contributions

- `prompt-critic` confirmed the approval-history ambiguity and the missing
  executable return path after completed-work review.
- `security-critic` found the absent sanitized-evidence rules and the unprotected
  Worker deny set while confirming that the broader destructive-action controls
  are sound.
- `testing-critic` identified missing canonical checks for owner, mode, and Task
  topology and called for mutation coverage.
- `architecture-strategy-critic` recommended retaining all current agents and
  filling the persistence gap with a command/handoff rather than another agent.
- `technical-researcher` verified the supplied OpenCode v1.18 filename-stem,
  permission-order, provider-option, command-routing, and LSP process behavior;
  it left the installed version and effective local LSP/MCP configuration
  unverified.

## Risks and Guardrails

- A strict canonical topology makes intentional future roster changes require a
  reviewed validator update. That friction is deliberate; inventory changes must
  not gain authority through manifest edits alone.
- Last-match permission behavior can make a deny look present while a later rule
  defeats it. Protect the complete Worker suffix and mutate ordering in tests,
  not just rule membership. Treat the v1.18 oracle as a repository compatibility
  check, never as proof of the installed runtime.
- The Lead clipboard and MCP rules are explicit human authorization. Preserve
  all seven patterns and actions exactly; a routine audit, security review, or
  refactor may not revoke or narrow them.
- Body-token validation can become brittle. Limit checks to authority,
  provenance, non-exfiltration, and the two compact association blocks; do not
  freeze headings or editorial phrasing that validation does not need.
- Commit-only review requires disciplined Git state. Reject a merge, abbreviated
  ID, wrong parent, empty commit, changed `HEAD`, or implementation content left
  outside the commit; do not reinterpret Coordinator lifecycle changes as
  implementation.
- The target-plan exception is intentionally narrow. Replay only schema-valid
  lifecycle transitions, reject all body or second-plan changes, and fail closed
  on ignored, unsupported, unattributed, or symlinked entries.
- Attempt IDs prevent same-revision review reuse only when append order and the
  exact implementation reference and parent are both checked. Never select
  evidence by revision alone or by timestamp sorting.
- A dependency's `completed` status can race ahead of review. Gate on its latest
  completed attempt and matching approving record every time execution starts or
  resumes.
- A Request Changes decision must not silently expand approved scope. The Lead
  may reopen execution only for corrections already covered by the approved
  revision; otherwise `/revise-plan` resets review and human approval.
- Approve With Follow-ups must not hide unmet acceptance criteria. Any change
  needed for plan correctness or a guardrail is Request Changes.
- Prompt safeguards and sanitized diagnostics reduce disclosure risk but cannot
  prove runtime redaction. Tests must use synthetic data, and reviewers must stop
  on a live credential without copying it into findings, commands, clipboard or
  MCP input, Coordinator packets, output, or history.
- LSP permission is a process and supply-chain trust boundary even for read-only
  roles. Keep configuration machine-local, use only operator-trusted servers,
  and report runtime verification gaps plainly.
- Preserve all 23 agent names, exact filename-stem IDs, two-primary arrangement,
  one-level Task graph, ERB independence, and Worker/Coordinator edit boundaries.
- Do not modify `docs/skill-taxonomy.md` or `docs/cross-reference-map.md` unless
  implementation changes skill routing, which this plan forbids.

### Execution stop conditions

Stop implementation and return to the Lead if any of these occurs:

- `HEAD` or relevant files drift materially from the baseline before work starts,
  or unrelated worktree changes overlap an assigned file.
- A proposed transition requires new lifecycle metadata, a second authority, or
  a different agent topology beyond this approved design.
- Correcting a completed-work finding changes approved scope or a central
  product, architecture, behavior, migration, or security decision; use
  `/revise-plan` instead.
- Tests cannot distinguish canonical topology from an arbitrary manifested
  topology, or permission-order mutations cannot be rejected deterministically.
- The implementation cannot bind a reviewable attempt to one full current-HEAD,
  one-parent content-bearing commit and its exact parent, or one attempt can
  consume another attempt's record.
- Human authorization for the one coherent implementation commit is absent;
  record the non-material blocker and stop before review-ready completion.
- A second plan, target-plan body edit, unexpected lifecycle mutation,
  unsupported/symlink entry, or non-plan change exists outside the implementation
  commit.
- Dependency checks cannot distinguish unreviewed completion, Request Changes,
  and corrected-but-unreviewed completion.
- The Lead's `pbcopy *` or any configured MCP-prefix allow would be removed,
  downgraded, narrowed, or reinterpreted.
- Sanitized-evidence tests require inspecting or embedding a real secret.
- Trusted-LSP documentation would need machine-local credentials, an unverified
  platform guarantee, global disablement, or a nonexistent per-agent sandbox.
- Root and project-template plan files cannot remain byte-identical after the
  lifecycle change.

## Implementation Sequence

### 1. Encode the canonical inventory, modes, owners, and Task graph

**Objective:** Make the current 23-agent authority model an explicit validator
contract.

**Scope and stable interfaces:** Update `tools/opencode_manager.py` and the
OpenCode test fixtures in `tests/test_opencode_manager.py`. Preserve the public
CLI, manifest schema, filename-stem IDs, frontmatter subset, two primary IDs, and
all existing Task edges. Include the planned command owner in the canonical map
only when its command file and manifest entry are added in step 2.

**Dependencies:** None, but this unit shares the validator/test files with steps
3 through 5 and therefore must not run concurrently with them.

**Acceptance criteria:**

- Validation accepts the repository's exact 23-agent mode map and current
  primary allowlists.
- A mode flip, added primary, missing primary, added/removed Task edge, arbitrary
  primary owner, or non-Lead edge to Coordinator/Worker fails with a stable
  diagnostic.
- Every tracked command has its canonical owner and literal `subtask: false`.
- Existing one-level delegation and unknown-target checks continue to pass.

**Validation:** Run the focused OpenCode manager test file, including one
mutation case per mode, owner, and Task-edge class; then run
`just validate-opencode`.

### 2. Add commit-only completion identity and the read-only plan oracle

**Objective:** Give each completion one immutable commit identity, make lifecycle
and dependency behavior executable without granting write authority, and prevent
execution against unaccepted dependencies.

**Scope and stable interfaces:** Add
`opencode/commands/record-implementation-review.md`; update
`review-implementation.md`, `execute-plan.md`, `planning-coordinator.md`,
`engineering-lead.md`, `opencode/manifest.json`, governance docs, the canonical
plan README/template, and synchronized files under `opencode/project-template/`.
Add the pure `tools/opencode_plan.py` API/CLI and
`tests/test_opencode_plan.py`. Keep the ERB read-only, keep the new command
Lead-owned, and add no ERB permission to execute the new module.

**Dependencies:** Step 1's owner map design. Apply manifest, command, template,
and docs changes together.

**Acceptance criteria:**

- `/execute-plan` routes only completed work to `/review-implementation`; blocked
  work records a blocker and returns to execution after resolution or to
  `/revise-plan` for material change.
- Without explicit human commit authorization, `/execute-plan` records the
  specified non-material blocker and stops. With authorization, every completion
  appends the next never-reused `attempt_id`, a full
  `commit:<40-hex-current-HEAD>` reference, and the exact
  `implementation_parent` for one non-merge content-bearing commit.
- Completion, review, and recording reject changed `HEAD`, the wrong parent,
  merge or empty commits, and every staged, unstaged, untracked, ignored,
  unsupported, or unattributed non-plan change outside the commit.
- The only worktree exception is the exact target plan's schema-valid,
  Coordinator-authored lifecycle delta. A changed second plan, target-plan body
  edit, unexpected metadata/history mutation, unsupported entry, or symlink
  fails.
- `/review-implementation` copies the complete attempt identity, emits the
  structured record, and always names `/record-implementation-review <path>` as
  its immediate next command.
- The recording command rejects stale, partial, older-attempt, cross-attempt,
  mismatched, or conflicting records. It detects a byte-equivalent persisted
  record first and no-ops without mutable evidence checks. The Lead performs the
  separate-top-level-ERB origin check; no prompt claims automatic authorship
  detection.
- The four fixed `opencode_plan.py` subcommands accept only the documented
  sanitized record schema and canonical plan paths, emit only
  `opencode-plan-result-v1`, never write, and fail closed on unknown fields or
  ambiguous history.
- The Lead runs transition/dependency validation before Coordinator persistence
  and persisted-state validation afterward. Focused fixtures prove exact
  lifecycle results, dependency results, attempt matching, commit/current-HEAD/
  parent identity, duplicate-before-mutable-check ordering, and target-plan delta
  enforcement.
- Two completed attempts at the same plan revision cannot consume one another's
  review evidence; each correction needs a newly matched review.
- Every decision follows the lifecycle matrix, refreshes `updated` on append,
  handles `completed_at` exactly, and leaves plan-review, approval, and revision
  fields unchanged.
- A dependency remains unsatisfied before review, after Request Changes, and
  after a corrected but unreviewed completion; only an approving review matched
  to its latest completion passes the gate.
- Plans that lack `Implementation Review History` receive the heading before the
  first append; this plan already contains the empty backfill.
- Root and project-template README/template files remain byte-identical where the
  validator requires synchronization.

**Validation:** Add command-owner, commit/parent identity, worktree-cleanliness,
exact target-plan-delta, same-revision cross-attempt rejection, duplicate-first
idempotency, conflict, dependency-state, lifecycle-transition, manifest,
template-heading, and root/template drift tests. Include the required changed
second-plan, body-edit, unsupported/symlink, unexpected-lifecycle, and exact
allowed-delta fixtures. Exercise completed → Request Changes →
in-progress/blocked → corrected completion → final review. Run both focused unit
test files and `just validate-opencode`.

### 3. Make plan review, approval, and amendment provenance unambiguous

**Objective:** Prevent duplicate ERB plan-review entries and preserve independent
review timing.

**Scope and stable interfaces:** Update `approve-plan.md`, `revise-plan.md`,
`planning-coordinator.md`, `engineering-lead.md`, lifecycle docs, root/template
history instructions, and synchronized project-template copies. Preserve
revision and approval semantics while allowing the revision command to consume
the latest matching material implementation review.

**Dependencies:** Step 2 establishes the separate implementation-review history.

**Acceptance criteria:**

- Approval writes one Approval History entry that references an already
  persisted, exact-matching `ready` ERB plan review; it does not append another
  ERB review.
- Material revision increments revision, resets current review/approval metadata,
  clears top-level `completed_at`, preserves earlier history, and appends only an
  amendment until the next `/record-plan-review`.
- `/revise-plan` accepts either the latest matching pre-approval ERB record or
  the latest matching material Request Changes record. The latter must match the
  latest completion attempt, implementation reference, and implementation
  parent, and the amendment cites that evidence.
- A material implementation finding after an earlier `ready` plan review resets
  review and approval state; it cannot reuse the earlier readiness record.
- Exact operation/history tuples reject approval that appends ERB Review History
  and revision that appends a new review record, even when all expected words
  remain elsewhere in the prompt.
- Metadata-only lifecycle transitions still leave revision unchanged.

**Validation:** Run focused provenance mutation tests, template synchronization
checks, a material-finding-after-ready transition test, and
`just validate-opencode`.

### 4. Carry sanitized evidence through implementation review and persistence

**Objective:** Keep sensitive values out of every implementation-review handoff,
tool input, diagnostic, output, Coordinator packet, and durable record.

**Scope and stable interfaces:** Update `security-critic.md`,
`technical-researcher.md`, `engineering-review-board.md`,
`change-verifier.md`, `engineering-lead.md`, `planning-coordinator.md`,
`review-implementation.md`, `record-implementation-review.md`, and the narrow
prompt/CLI validation tests needed for the end-to-end boundary. Preserve all
IDs, modes, tools, configured network/clipboard/MCP permissions, source priority,
and review domains.

**Dependencies:** Shared validator/test ownership requires serial execution after
steps 1 through 3.

**Acceptance criteria:**

- Specialist prompts, ERB delegation and output, Lead evidence packets,
  recording commands, Coordinator handoffs, CLI diagnostics, and durable history
  all require minimization, synthetic placeholders, and location/type-only
  reporting.
- Raw sensitive values are forbidden in findings, delegated prompts, command
  arguments, clipboard input, MCP/network requests, URLs, queries, citations,
  diagnostics, stdout/stderr, Coordinator packets, and durable history. A live
  credential stops review until sanitized removal/rotation is complete.
- The Coordinator receives only verified identity metadata, decision, and
  sanitized findings/follow-ups. This restriction does not revoke the Lead's
  human-authorized clipboard or configured MCP access.
- Removing a safeguard or adding contradictory disclosure text for any forbidden
  channel fails while unrelated prose remains accepted.
- The fixed synthetic sentinel is absent end to end from specialist and ERB
  output, recording input/output, Coordinator packets, result collections, CLI
  stdout/stderr, and persisted Implementation Review History.
- Tests and fixtures contain no live secret, credential, private endpoint, or
  copied environment value.

**Validation:** Run the focused synthetic mutation tests and the full OpenCode
manager test file, then `just validate-opencode`.

### 5. Preserve Lead authorizations and enforce the Worker deny suffix

**Objective:** Make the Lead's human-authorized clipboard/MCP access and the
Worker's destructive-action/plan-shell rules non-regressible under documented
last-match evaluation.

**Scope and stable interfaces:** Update permission invariants and the deterministic
`resolve_v118_permission_action` oracle in `tools/opencode_manager.py`, with
table-driven mutations in `tests/test_opencode_manager.py`. Preserve
`engineering-lead.md` and `implementation-worker.md` unless validation exposes a
real mismatch; do not narrow the Lead or widen the Worker.

**Dependencies:** Shared validator/test ownership requires serial execution after
step 4.

**Acceptance criteria:**

- `pbcopy *` and each of `playwright_*`, `chrome-devtools_*`, `serena_*`,
  `context7_*`, `gh_grep_*`, and `github_*` remain `allow`; removal or mutation
  to `ask`/`deny` fails for every pattern.
- The current commit, push, hard-reset, clean, `rm`, `sudo`, and plan-path shell
  denies validate as the required final suffix.
- Removing a deny, changing it to `ask`/`allow`, moving it behind a weakening
  match, or appending a later weakening rule fails validation.
- The pure oracle table-drives all seven Worker patterns, representative
  match/non-match inputs, bare and argument-bearing forms where applicable, and
  later weakening rules under documented v1.18 semantics.
- Machine checks also preserve plan edit denial, no delegation, and network
  denial. They do not introduce a canonical safe-inspection allowlist or claim
  to verify the installed runtime.

**Validation:** Run table-driven removal/action-downgrade tests for every Lead
pattern and membership/action/order/match tests for every Worker pattern.
Manually compare both permission maps and confirm no unrelated authorization
change. Then run the full OpenCode manager test file and
`just validate-opencode`.

### 6. Document and verify the trusted-LSP exception

**Objective:** State the real process boundary while preserving approved LSP
navigation.

**Scope and stable interfaces:** Update `README.md`,
`docs/engineering-agent-governance.md`, and project-template guidance where the
operator boundary must travel to copied repositories. Do not alter agent LSP
permissions. Leave `opencode/config/opencode.merge-fragment.jsonc` unchanged
because README/governance own this operator guidance and the merge fragment adds
no enforcement.

**Dependencies:** Use the supplied v1.18 research result; do not claim the target
machine matches it without runtime evidence.

**Acceptance criteria:**

- Docs say read-only roles may start only operator-configured trusted language
  servers and that Bash denial does not make review process-free.
- Docs keep downloads, server provenance, credentials, providers, LSP/MCP
  settings, and live configuration machine-local.
- Operator verification asks for the installed OpenCode version, effective
  LSP/MCP configuration, server command/source, expected process behavior, and a
  sanitized controlled navigation check.
- No doc promises a per-agent LSP sandbox, disables LSP globally, or implies that
  repository validation proves the machine-local runtime.

**Validation:** Review local links and synchronized template text; run
`just validate-opencode` and `just validate`. Record runtime verification as
skipped unless the operator supplies target-machine evidence.

### 7. Reconcile inventory, docs, and final evidence

**Objective:** Finish with one internally consistent repository contract and a
reviewable evidence packet.

**Scope and stable interfaces:** Re-read all changed agents, commands, manifest,
manager/tests, README/governance, canonical plan docs, and project-template
copies. `docs/cross-reference-map.md` and `docs/skill-taxonomy.md` stay untouched
because no skill route changes.

**Dependencies:** Steps 1 through 6 complete with no unresolved stop condition.

**Acceptance criteria:**

- Manifest inventory is sorted and contains 23 unchanged agent files plus the
  one allowed new command.
- The two primaries, 21 subagents, exact Task graph, command owners, LSP posture,
  and plan-write boundaries match the approved design.
- Lifecycle docs and prompt transitions agree; every review decision has one
  durable history location and one valid next step.
- Completion-attempt identity, dependency gating, lifecycle metadata, history
  authority, commit/parent binding, exact target-plan delta, permission
  protections, and non-exfiltration blocks match their canonical contracts.
- All required checks pass, or the Lead reports the exact failure and does not
  request implementation review.

**Validation:** Execute the Final Verification section and inspect the resulting
diff for unrelated changes, secret-shaped data, stale command counts, and
root/project-template drift.

## Test Strategy

Use the standard-library `unittest` suite and temporary repository fixtures.
Refactor the generic fixture where needed so the success case models the
canonical 23-agent topology instead of proving that an arbitrary primary is
valid. Keep tests deterministic and table-driven.

Required test groups:

- **Canonical inventory and authority:** mutate each primary mode class, command
  owner class, Lead/ERB Task allowlist, exclusive Coordinator/Worker edge, and
  each protected Lead clipboard/MCP rule through removal and action downgrade.
- **Attempt and implementation identity:** require a full current-HEAD commit and
  exact parent; reject abbreviated IDs, merge or empty commits, wrong/current-HEAD
  drift, and staged, unstaged, untracked, ignored, unsupported, or unattributed
  non-plan changes. Complete attempts 1 and 2 at one revision with different
  commit references/parents; show that attempt 1's review cannot approve, reopen,
  or revise attempt 2.
- **Exact plan delta:** accept one schema-valid target-plan lifecycle delta and
  reject a changed second plan, target-plan body edit, unsupported or symlink
  entry, unexpected metadata/history mutation, and any blanket plan-subtree
  exclusion.
- **Lifecycle and dependencies:** cover initial completion, every review outcome,
  top-level `updated`/`completed_at` behavior, corrected completion, final review,
  exact duplicate detection before mutable evidence checks, conflicts, and
  immutable prior times. Parse plan-history fixtures through the pure API. A
  dependent stays blocked for completed-unreviewed, Request Changes, and
  corrected-unreviewed states, then passes only after the latest attempt has an
  approving matching record.
- **Association and provenance mutations:** swap each decision/status/history/
  command field and operation/history field while retaining all words. Include
  Approve-to-execution, direct material reopening, approval-to-ERB-history, and
  revision-to-review-history failures; test material Request Changes after an
  earlier `ready` plan review.
- **Worker last-match rules:** mutate membership, action, order, and a later
  weakening match for each of the seven protected patterns. Exercise matching and
  non-matching inputs, including bare and argument-bearing forms where applicable,
  through the deterministic v1.18-compatible oracle.
- **Sanitized evidence:** use a fixed synthetic sentinel, remove each safeguard,
  and separately add contradictory disclosure text for every forbidden channel.
  Pass it through specialist output, ERB output, recording input/output,
  Coordinator packets, CLI results/stdout/stderr, and persisted history; assert
  that no stage emits or stores the sentinel.
- **Synchronization and compatibility:** preserve existing manifest, frontmatter,
  Markdown-fence, support-file, template-token, byte-sync, setup, verify, and
  uninstall tests.

During implementation, run:

```sh
python3 -m unittest discover -s tests -p 'test_opencode_manager.py' -v
python3 -m unittest discover -s tests -p 'test_opencode_plan.py' -v
just validate-opencode
```

Before handoff, run the broader gates in Final Verification. Do not use real
credentials, network calls, machine-local config changes, or an installed
language server as unit-test dependencies.

## Migration, Compatibility, and Recovery

This is an additive command and governance change, not an agent migration.
Filename-stem IDs for all 23 agents remain unchanged; the new command ID is
`record-implementation-review`. Existing approved or completed plan history is
preserved. Revision 2 backfills an empty `Implementation Review History` section
in this self-hosting plan. Any other plan encountered without that heading gets
the heading immediately before its first implementation-review append; copied
repositories receive it when they synchronize the project template.

The linked OpenCode checkout takes definition changes on restart. Rollout should
therefore update command, manifest, prompts, validator, tests, and docs as one
reviewed change, run all repository checks, obtain independent ERB review, and
then restart OpenCode on the operator's machine. No installer or config mutation
belongs in this work.

If validation fails, recover by reverting the coordinated repository changes as
one unit rather than weakening constants or deleting historical records. Do not
leave the new command in the manifest without its file, leave docs pointing to
an unavailable command, or remove the new template section while records use it.
Do not retain raw implementation evidence or relabel Coordinator lifecycle
changes as implementation content. Preserve historical plan records during
recovery and return to the last reviewed commit plus schema-valid plan state.
Machine-local LSP configuration remains untouched, so repository rollback does
not need to restore credentials, downloads, or server settings.

## Documentation Impact

- `README.md`: add the trusted-LSP operator boundary, safe machine-local
  configuration guidance, new command in the durable-plan workflow, and the
  updated command count only if the README states one.
- `docs/engineering-agent-governance.md`: add the Lead-owned recording command,
  completed-work transition table, attempt identity, dependency gate, provenance
  rules, commit authorization gate, protected Lead tool invariant, exclusive Task
  ownership, and LSP process/trust wording.
- `docs/implementation-plans/README.md`: extend lifecycle steps through durable
  implementation-review recording, define the commit-only review and read-only
  validation flow, define dependency acceptance, and distinguish blocked
  execution from completed review.
- `docs/implementation-plans/TEMPLATE.md`: add `Implementation Review History`
  with the attempt-bound structured record shape and keep frontmatter unchanged.
- `opencode/project-template/AGENTS-plan-workflow-snippet.md` and both plan-doc
  copies: mirror the portable lifecycle, handoff, and operator-trust guidance;
  keep byte-compared files synchronized.
- `opencode/config/opencode.merge-fragment.jsonc`: no change. README and
  governance carry the operator trust guidance without adding config semantics.

## Final Verification

Run from the repository root after all implementation changes:

```sh
python3 -m unittest discover -s tests -p 'test_opencode_manager.py' -v
python3 -m unittest discover -s tests -p 'test_opencode_plan.py' -v
just validate-opencode
just validate
just check
git diff --check
git status --short
```

Then perform manual evidence checks:

- Count 23 unchanged agent filenames, exactly two primaries, 21 subagents, and
  the expected command inventory with only
  `record-implementation-review.md` added.
- Compare root and project-template implementation-plan README/template files
  byte for byte through the repository validator.
- Trace one Approve, one Approve With Follow-ups, one in-scope Request Changes,
  one blocked execution, and one material Request Changes path from command to
  durable record and next command. Confirm every append refreshes `updated`,
  completion sets a fresh `completed_at`, approving review preserves it, and
  reopening clears only the top-level value.
- Build two attempts at the same plan revision with different full commit
  references and parents. Require current-HEAD equality, reject crossed records
  in both directions, and confirm a byte-equivalent persisted record is a no-op
  before mutable evidence checks.
- Exercise the exact plan-delta fixtures: changed second plan, unrelated target
  body edit, unsupported/symlink entry, unexpected lifecycle mutation, and the
  one allowed Coordinator-authored target-plan delta. Confirm no plan subtree is
  excluded wholesale and no lifecycle change is labeled implementation content.
- Exercise the dependency gate before review, after Request Changes, after
  corrected completion, and after the corrected attempt's approving review.
- Inspect tuple-swapping mutations for every canonical transition and history
  append association, not only presence of the expected vocabulary.
- Inspect mutation coverage for every canonical mode/owner/Task edge and every
  protected Lead rule and Worker deny family, including action downgrades,
  v1.18-compatible match/non-match cases, and later-rule overrides. Manually
  confirm the Lead authorization and Worker's safe inspection allows have no
  unrelated diff; no second allowlist should exist.
- Search the complete implementation-review path for synthetic sentinel leakage,
  raw secret examples, credentials, private endpoints, and machine-local paths;
  report only sanitized locations if anything suspicious appears. Check
  specialist/ERB output, recording I/O, Coordinator packets, durable history,
  result messages, warnings, errors, and captured CLI stdout/stderr.
- Re-read trusted-LSP wording to confirm it permits trusted navigation, discloses
  process/download behavior, and makes no runtime claim unsupported by
  target-machine evidence.
- Confirm `opencode/config/opencode.merge-fragment.jsonc` has no diff.

`just validate-opencode` is the mandatory focused gate. Because Python tooling,
tests, manifest validation, command routing, docs links, and synchronized support
files all change, `just validate` and `just check` are also mandatory before the
Lead requests `/review-implementation`.

## Open Decisions

- **Nonblocking target-machine evidence gap:** the installed OpenCode version and
  effective machine-local LSP/MCP configuration remain unknown. The operator
  must supply or record those facts before anyone claims runtime verification.
  This does not block repository implementation; it blocks claims that the local
  machine matches the supplied v1.18 research or starts only expected servers.

No product, architecture, security, or agent-inventory decision remains for the
executor. Any new central decision stops execution and returns through
`/revise-plan`. Future explicit authorization for the one coherent implementation
commit is a normal execution gate under Git policy, not an unresolved decision.

## ERB Review History

Every actionable entry is persisted through `/record-plan-review` and binds the
exact plan path, ID, revision, and baseline.

plan_path: docs/implementation-plans/plans/opencode/01-agent-definitions-improvement-program.md
plan_id: opencode-01
revision: 1
baseline_commit: f80ae0d22a7dfebafdbb679c13e4ea5a5860b014
decision: ready-with-revisions
reviewed_at: 2026-07-14
findings: RP-01 immutable completion-attempt identity; RP-02 accepted dependency gate; RP-03 correction-loop metadata and revision evidence; RP-04 decision/provenance association tests; RP-05 Worker inspection-permission oracle
next_command: /record-plan-review docs/implementation-plans/plans/opencode/01-agent-definitions-improvement-program.md

plan_path: docs/implementation-plans/plans/opencode/01-agent-definitions-improvement-program.md
plan_id: opencode-01
revision: 2
baseline_commit: f80ae0d22a7dfebafdbb679c13e4ea5a5860b014
decision: ready-with-revisions
reviewed_at: 2026-07-14
findings: R2-01 rebaseline and preserve human-authorized Lead tools; R2-02 add an exact permission-compatible bundle verifier and cross-session handoff; R2-03 extend non-exfiltration through implementation-review persistence; R2-04 narrow the plan-subtree exclusion; R2-05 add executable lifecycle and permission-match oracles or narrow automated claims
next_command: /record-plan-review docs/implementation-plans/plans/opencode/01-agent-definitions-improvement-program.md

## Approval History

No approvals recorded.

## Implementation Review History

No implementation reviews recorded.

## Amendments

### Amendment — 2026-07-14 (revision 1 → 2)

- Evidence: persisted ERB review for
  `docs/implementation-plans/plans/opencode/01-agent-definitions-improvement-program.md`,
  plan ID `opencode-01`, revision `1`, baseline
  `f80ae0d22a7dfebafdbb679c13e4ea5a5860b014`, reviewed 2026-07-14 with decision
  `ready-with-revisions`.
- RP-01 — **accepted with modification:** defined never-reused positive integer
  attempt IDs; exact attempt fields; discriminated `commit:` and
  `patch-sha256:` references; deterministic complete bundle requirements;
  recomputation by both review consumers; stale/conflict/older-attempt rejection;
  exact-duplicate no-op; same-revision cross-attempt tests; and procedural Lead
  verification of a separate top-level ERB source instead of unverifiable
  self-authorship detection.
- RP-02 — **accepted:** made dependency satisfaction require `completed` status,
  an approving implementation review matched to the latest completion, and no
  later completion or Request Changes record. Added blocked-state and correction
  loop acceptance tests.
- RP-03 — **accepted:** added the lifecycle transition matrix, mandatory
  `updated` refresh, exact `completed_at` rules, immutable completion history,
  implementation-review field preservation, dual-source `/revise-plan`
  evidence, material-finding transition coverage, and this plan's empty
  `Implementation Review History` backfill.
- RP-04 — **accepted with modification:** replaced presence-only prompt markers
  with compact transition, append-authority, and non-exfiltration blocks. Added
  tuple-field swaps, additive disclosure contradictions, and sentinel absence
  checks across result collections and CLI output without broad prompt parsing.
- RP-05 — **accepted with modification:** limited machine enforcement to the
  current seven-rule Worker deny suffix, plan edit denial, no delegation, and
  network denial. Added bare/argument-bearing and later-weakening tests using the
  verified optional terminal wildcard behavior; unchanged safe inspection allows
  remain a manual no-unrelated-permission-change diff check.
- Resolved review evidence: retain the human-selected trusted-LSP exception; add
  no agent, top-level status, or frontmatter field; keep
  `opencode/config/opencode.merge-fragment.jsonc` unchanged because tracked
  README/governance guidance owns the operator boundary. Target-machine
  OpenCode/LSP/MCP verification remains nonblocking evidence, not a human
  decision.
- Lifecycle reset: revision incremented from 1 to 2; status remains `draft`;
  `review_decision` reset to `pending`; `reviewed_at`, `approved_at`, and
  `approved_revision` cleared; `completed_at` remains empty. No ERB Review
  History entry was appended or changed.

### Amendment — 2026-07-14 (revision 2 → 3)

- Evidence: latest persisted ERB review at
  `docs/implementation-plans/plans/opencode/01-agent-definitions-improvement-program.md`,
  plan ID `opencode-01`, revision `2`, baseline
  `f80ae0d22a7dfebafdbb679c13e4ea5a5860b014`, reviewed 2026-07-14 with decision
  `ready-with-revisions` and findings `R2-01` through `R2-05` exactly as preserved
  in ERB Review History.
- R2-01 — **accepted:** rebaselined revision 3 to
  `9bd28e3a15c237e1fb4cf6e1996da36b687db5e8`; classified
  `9bd28e3 feat(opencode): authorize lead tool access` and its four changed files
  as pre-existing baseline work; preserved the human-authorized `pbcopy *`,
  `playwright_*`, `chrome-devtools_*`, `serena_*`, `context7_*`, `gh_grep_*`,
  and `github_*` allows; and required table-driven removal and `ask`/`deny`
  downgrade tests for every rule. The revision-1 and revision-2 ERB records keep
  their original revision and `f80ae0d22a7dfebafdbb679c13e4ea5a5860b014`
  baseline.
- R2-02 — **accepted with modification:** removed the uncommitted implementation
  transport and verifier design from the active plan. Reviewable completion is
  now one full current-HEAD, exactly-one-parent, non-merge, content-bearing commit
  with `implementation_reference` and `implementation_parent`; the Board uses its
  existing read-only Git forms and receives no permission to execute newly
  changed repository code. Preserved never-reused attempt IDs, latest-attempt and
  current-HEAD equality, cross-attempt rejection, correction-loop review, exact
  record fields, conflict handling, and duplicate-first idempotency. Added the
  Git-policy gate that records a non-material blocker when explicit human commit
  authorization is absent, and prohibited raw implementation artifacts across
  session or command boundaries.
- R2-03 — **accepted:** extended the sanitized/non-exfiltration boundary through
  implementation-review specialists, `engineering-review-board`,
  `change-verifier`, `/review-implementation`, the Engineering Lead evidence
  packet, `/record-implementation-review`, `planning-coordinator`, CLI output,
  Coordinator packets, and persisted Implementation Review History. Preserved
  authorized Lead tool access, added live-credential stop/removal/rotation rules,
  limited Coordinator input to identity/decision/sanitized findings, and required
  end-to-end synthetic-sentinel mutation coverage.
- R2-04 — **accepted with modification:** removed the blanket plan-subtree
  exclusion. The active design now rejects every non-plan change outside the
  implementation commit, rejects every changed plan except the exact target, and
  permits only the schema-valid Coordinator-authored target-plan lifecycle delta.
  Added required fixtures for a changed second plan, unrelated target-plan body
  edit, unsupported/symlink entry, unexpected lifecycle mutation, and the one
  allowed exact delta; Coordinator lifecycle changes remain separate from
  implementation content.
- R2-05 — **accepted with modification:** specified the pure read-only
  `tools/opencode_plan.py` module, `tests/test_opencode_plan.py`, four exact CLI
  subcommands, sanitized transition-record/result schemas, duplicate-first
  ordering, transition/dependency/commit/plan-delta checks, and Lead pre/post
  persistence use without new ERB execution permission. Kept compact static
  transition/history/non-exfiltration checks in `tools/opencode_manager.py` while
  limiting their claims, and specified a deterministic
  `resolve_v118_permission_action` oracle for all seven protected Worker patterns
  as repository compatibility with the documented v1.18 model, not proof of the
  installed runtime.
- Preserved decisions: all accepted revision-1 findings, the lifecycle matrix,
  dependency gate, history separation, merge-fragment no-change decision,
  23-agent inventory, two-primary topology, one-level Task graph,
  Coordinator-only plan writes, Lead-owned recording command, and trusted-LSP
  exception remain. Target-machine OpenCode/LSP/MCP evidence remains a
  nonblocking runtime-verification gap. No new agent, lifecycle status, or
  top-level metadata field was added, and no required human product,
  architecture, or security decision remains unresolved.
- Lifecycle reset: revision incremented from 2 to 3; status is `draft`;
  `review_decision` reset to `pending`; `reviewed_at`, `approved_at`, and
  `approved_revision` cleared; baseline changed to
  `9bd28e3a15c237e1fb4cf6e1996da36b687db5e8`; `updated` remains 2026-07-14 and
  `completed_at` remains empty. No ERB Review History entry was appended,
  rewritten, or deleted.

## Execution Record

No execution recorded.
