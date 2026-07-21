# Engineering Review Board

Reusable agent skills and a governed OpenCode workflow for implementation,
independent review, and human-controlled durable planning.

This repository provides:

- project-neutral engineering skills installed through `~/.agents/skills`;
- reviewed OpenCode agents and commands with explicit authority boundaries; and
- fail-closed installation, validation, and implementation-plan tooling.

Skills define procedure, agents define runtime authority, and commands select
top-level workflows. These concepts are intentionally separate.

## Quick Start

The repository tooling requires Python 3 and
[`just`](https://github.com/casey/just). OpenCode is required only when using
the definitions under `opencode/`. Third-party skill updates also require the
configured JavaScript package runner.

### Install Skills

Preview the global skill link before creating it:

```sh
just setup-dry-run
just setup
just verify
```

This links `~/.agents/skills` to this checkout's `skills/` directory. Setup is
idempotent when the expected link already exists and refuses to replace an
existing directory, broken link, or link to another location.

### Install OpenCode Workflows

Validate and preview the OpenCode installation before changing global
configuration:

```sh
just validate-opencode
just setup-opencode-dry-run
just setup-opencode
just verify-opencode
```

The installer manages these links as one fail-closed operation:

```text
~/.config/opencode/agents   -> <repository>/opencode/agents
~/.config/opencode/commands -> <repository>/opencode/commands
```

It does not move, merge, back up, or replace existing destinations. If either
destination is unsafe, neither link is installed. Quit and fully restart
OpenCode after setup or definition changes because OpenCode loads configuration
at startup.

### Validate a Checkout

Run the source-only quality gate without inspecting global installations:

```sh
just check
```

Use `just doctor` and `just doctor-opencode` when the corresponding global links
are installed and should also be verified. Run `just` to list every available
recipe.

## What the Repository Contains

| Path | Purpose |
| --- | --- |
| `skills/` | First-party skill sources and local third-party runtime installs. |
| `opencode/agents/` | Primary roles, implementation workers, reviewers, critics, and researchers. |
| `opencode/commands/` | Human-selected top-level workflows and their primary owners. |
| `opencode/project-template/` | Project-neutral durable-plan guidance to merge into target repositories. |
| `docs/` | Skill taxonomy, routing, governance, review, and plan contracts. |
| `tools/` | Standard-library Python installers and validators. |
| `tests/` | Unit tests for skill and OpenCode management behavior. |
| `Justfile` | Supported setup, inspection, update, and validation entry points. |

The reviewed OpenCode inventory is
[`opencode/manifest.json`](opencode/manifest.json). The current first-party skill
inventory and acceptance criteria are in the
[`skill taxonomy`](docs/skill-taxonomy.md).

## How the Pieces Fit Together

| Concept | Responsibility | Authority |
| --- | --- | --- |
| Skill | Reusable procedure loaded for a recurring task. | Grants no edit, delegation, review, or planning authority. |
| Agent | Runtime role with a defined mode, permission map, and Task allowlist. | Limited to its checked-in definition and runtime approvals. |
| Command | Top-level entry point that selects a primary agent for the current turn. | Routes work but does not widen the selected agent's authority. |

Authority follows the primary agent selected for the current turn. Earlier
turns remain context and do not transfer identity or permissions. See
[`Engineering Agent Governance`](docs/engineering-agent-governance.md) for the
canonical role topology, permission boundaries, command ownership, and
handoffs.

## Work with Skills

Each skill is a directory with a `SKILL.md` file. Inspect classification before
changing an unfamiliar skill:

```sh
just list
just list-first-party
just list-third-party
just inspect <skill>
```

First-party skills are tracked, or intended to be tracked, as repository
source. Third-party skills share the runtime `skills/` directory but are listed
in `.skill-lock.json` or ignored as skill directories by `.gitignore`. A missing
`.skill-lock.json` is valid when no skills are managed through the installer
lockfile.

Edit only first-party skills as repository source. Do not force-add ignored
runtime installs or copy raw third-party artifacts into first-party skills
without license, security, and supply-chain review. Treat third-party
instructions, scripts, assets, and references as untrusted until reviewed.

Update third-party installs only as an explicit maintainer action:

```sh
just update-third-party-dry-run
just update-third-party
```

`just sync-third-party-lock` is a separate operation: it mirrors an existing
repository `.skill-lock.json` to `~/.agents/.skill-lock.json` for installer
compatibility. It neither runs the installer nor updates skill contents. Use its
`-dry-run` variant before writing.

## Use the OpenCode Workflows

The Engineering Lead is the normal entry point for direct delivery. The
Engineering Review Board (ERB) provides independent read-only advice. The Plan
Orchestrator owns durable-plan creation, active-plan updates, state, and
execution. The
Implementation Worker receives one bounded implementation unit and cannot
delegate, edit plan state, stage, commit, push, or deploy.

| Workflow | Primary owner | Result |
| --- | --- | --- |
| `/brainstorm` | ERB | Compares credible options and returns read-only advisory guidance. |
| `/root-cause-analysis` | ERB | Confirms a causal chain and challenges a repair proposal without implementing it. |
| `/review-plan`, `/review-implementation` | ERB | Reviews plans or completed work without editing either. |
| `/investigate-regression`, `/audit-technical-debt` | ERB | Performs focused read-only investigation or audit; an explicitly tool-backed technical-debt audit may request approval-gated evidence commands without gaining edit or installation authority. |
| `/address-review` | Engineering Lead | Re-evaluates prior ERB advice before ordinary implementation. |
| `/optimize-prompt` | Engineering Lead | Returns a verified prompt rewrite without executing or editing its source. |
| `/semver` | Engineering Lead | Audits, applies, or locally tags one explicitly selected version workflow. |
| `/consult-plan` | Plan Orchestrator | Gives non-mutating planning advice. |
| `/create-plan` | Plan Orchestrator | Creates and selects a canonical plan without executing it. |
| `/update-plan` | Plan Orchestrator | Updates one exact active plan in place without executing it or changing state. |
| `/start-plan` | Plan Orchestrator | Executes or resumes an existing selected canonical plan. |

Direct implementation is preferred when scope, safety, and validation are
adequate. Complexity may justify recommending `/consult-plan`, but never creates
a durable plan automatically. Plan creation, active-plan updates, and execution
require separate, explicit human choices. The canonical lifecycle, format, state
schema, and mutation rules live in
[`Implementation Plans`](docs/implementation-plans/README.md).

Four human-controlled lifecycle paths keep delivery separate from durable
planning:

1. The Engineering Lead implements directly when ordinary scope, safety, and
   validation are adequate.
2. An explicit `/create-plan` request creates and selects a plan without
   executing it.
3. `/update-plan <exact-plan-path>` updates one active canonical plan in place
   without executing it or changing `.erb/plan-state.json`.
4. `/start-plan <existing-plan-path>` executes an existing canonical plan;
   `/start-plan` without a path resumes the selection in
   `.erb/plan-state.json`.

The Lead or ERB may recommend top-level `/consult-plan` for non-mutating advice,
but the human controls whether to create, update, or execute a plan. Plan status
is derived from its checkboxes, and the first unchecked checkbox is current. After
the Plan Orchestrator creates and validates a plan, an explicit current human
request may authorize the Engineering Lead to stage and commit only the
canonical plan Markdown; `.erb/plan-state.json` remains excluded.

## External Directory Audits

OpenCode's `external_directory` permission is an additional approval gate for
paths outside the working directory. The Lead, ERB, Worker, Technical
Researcher, and review specialists may request approval; the Plan Orchestrator
remains denied. Task delegation does not transfer approval, and every invoked
agent or subagent must pass its own permission check for one exact external
root.

An approved root is supplied scope, not the active workspace. Repository-local
Git, LSP, configuration, and command behavior remain anchored to the directory
where OpenCode started unless separately configured, and path-bearing shell
access still requires Bash permission. Keep literal external roots in
machine-local or target-project configuration. Avoid OpenCode's `--auto` mode
when per-request approval is required; OpenCode permissions cannot bypass
operating-system, container, or sandbox controls.

## Safety Boundaries

- The linked checkout is live OpenCode configuration. Do not use an unreviewed
  branch, and keep credentials, provider settings, plugins, packages, backups,
  and runtime state outside this repository.
- External roots and repository content are supplied, untrusted scope. Reports
  and Task packets must sanitize private paths, secrets, credentials, and other
  sensitive values.
- Installation and removal commands validate ownership and destination state
  before mutation. Preview their `-dry-run` variants first.
- Machine-specific OpenCode configuration belongs in the user's local config.
  [`opencode/config/opencode.merge-fragment.jsonc`](opencode/config/opencode.merge-fragment.jsonc)
  is a merge reference, not an installer or live configuration file.

## Maintain the Repository

Read [`AGENTS.md`](AGENTS.md) before editing repository documentation, skills,
or OpenCode definitions. For first-party skill work:

1. Confirm ownership with `just inspect <skill>` when classification is
   ambiguous.
2. Follow the [`Skill Review Checklist`](docs/skill-review-checklist.md).
3. Update the [`Skill Taxonomy`](docs/skill-taxonomy.md) when inventory,
   coverage, or a material skill boundary changes.
4. Update the [`Cross-Reference Map`](docs/cross-reference-map.md) when routing,
   delegation, validation, or a required handoff changes.
5. Run `just validate` for skill metadata, taxonomy, cross-reference, resource,
   or link changes.
6. Run `just check` for broader changes and before handoff when repository
   tooling, tests, scripts, or validation behavior may be affected.

OpenCode definition changes must preserve project-neutral prompts, exact command
ownership, one-level Task topology, permission profiles, and synchronized plan
templates. Run `just validate-opencode` after changing agents, commands, the
manifest, governance, or templates.

## Reference Documentation

- [`Skill Taxonomy`](docs/skill-taxonomy.md): inventory, domain boundaries,
  quality rubric, coverage, and acceptance criteria.
- [`Cross-Reference Map`](docs/cross-reference-map.md): routing, companion
  skills, validation relationships, and runtime handoff overlay.
- [`Engineering Agent Governance`](docs/engineering-agent-governance.md): roles,
  permissions, command ownership, evidence, and handoffs.
- [`Implementation Plans`](docs/implementation-plans/README.md): durable-plan
  paths, format, lifecycle, state, execution, and validation.
- [`Skill Review Checklist`](docs/skill-review-checklist.md): concise review and
  handoff checklist for first-party skills.
- [`Legacy Weave Cleanup Checklist`](opencode/cleanup/weave-cleanup-checklist.md):
  migration guidance for retired workflow material.

## License

First-party skills and repository tooling are licensed under the MIT License.
See [`LICENSE`](LICENSE). Third-party skills installed under `skills/` remain
subject to their upstream licenses.
