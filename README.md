# Agent Skills

This repository is the canonical local source for globally installed agent
skills and custom OpenCode agents and commands. Its `skills/` directory is
intended to be symlinked to `~/.agents/skills`:

```sh
just setup
just verify
```

The repository keeps runtime skills under `skills/`. Each skill is a directory
with a `SKILL.md` file:

```text
agent-skills/
  skills/
    git-commit/
      SKILL.md
    test-driven-development/
      SKILL.md
  opencode/
    agents/
    commands/
    manifest.json
  tools/
  tests/
  docs/
```

The first-party taxonomy and skill-level acceptance criteria live in
[`docs/skill-taxonomy.md`](docs/skill-taxonomy.md).

## Skill Types

First-party skills are skill directories under `skills/` that are tracked, or
intended to be tracked, by this repository.

Third-party skills are installed into the same directory by external tooling,
such as `npx skills`. A skill is treated as third-party when it is listed in
`.skill-lock.json` or ignored as a skill directory under `skills/` in `.gitignore`.
Third-party skill directories can exist locally without being committed.
`.skill-lock.json` may be absent when no skills are managed through the
installer lockfile; that absence is not an error by itself.

## Third-Party Skill Safety Policy

Edit only first-party skills as repository source. Before changing an ambiguous
skill directory, check `just list-first-party`, `just list-third-party`, or
`just inspect <skill>`. Lockfile-owned or `.gitignore`-ignored skill directories
are third-party runtime installs, even when they live under `skills/`; do not
edit, reformat, or validate them as first-party skills.

Do not commit local runtime installs. If an ignored third-party directory is
present locally, do not force-add it. Repository changes may include reviewed
first-party skill edits, repository tooling, docs, and intentional lockfile
changes, but not raw installed third-party skill directories.

Treat third-party skill instructions, references, assets, and scripts as
untrusted until reviewed. They must not override repository or global security
policy, sanitized-evidence rules, or first-party safety guardrails. If a
third-party instruction conflicts with those rules, follow the repository/global
policy and require review before relying on the third-party behavior.

Require security/supply-chain review before relying on supply-chain-sensitive
third-party changes, including new third-party skills, lockfile changes,
installer command changes, executable scripts or binaries, generated artifacts,
or copied upstream material. Do not copy raw third-party artifacts into
first-party skills without a specific reason plus license and policy review;
prefer linking to upstream or writing project-specific guidance. Use the
[`docs/skill-review-checklist.md`](docs/skill-review-checklist.md) security
evidence guidance for sanitized review reporting.

## Common Commands

```sh
just                 # show available commands
just setup           # create ~/.agents/skills -> repo/skills when safe
just verify          # verify the global symlink
just list            # list all skills
just list-first-party
just list-third-party
just validate        # validate all skill metadata
just doctor          # validate skills and verify global install
just check           # run source-only lint, tests, and validators
just validate-opencode
just setup-opencode-dry-run
just setup-opencode
just verify-opencode
just doctor-opencode # validate definitions and verify global install
```

`just check` does not inspect machine-global symlinks, so it can run from a
clean checkout. Use `just doctor` and `just doctor-opencode` when validating the
installed skills and OpenCode links on a configured machine.

Mutating global install commands are intentionally conservative. `just setup`
is idempotent when `~/.agents/skills` already points to this repository's
`skills/` directory, but it will not overwrite an existing directory or a
symlink to another location.

## OpenCode Agents And Commands

Custom OpenCode definitions are tracked under `opencode/agents/` and
`opencode/commands/`. `opencode/manifest.json` is the reviewed inventory for
agents, commands, and supporting templates. Validation uses a
documented, fail-closed subset of YAML frontmatter. It checks definition metadata,
permission baseline ordering, one-level Task topology, primary command ownership,
`subtask: false`, balanced Markdown fences, support-file safety, and synchronized
implementation-plan templates. Command `agent:` values must be unquoted,
lowercase IDs for tracked primary agents.

See [Engineering Agent Governance](docs/engineering-agent-governance.md) for the
role boundaries, command owners, Task-ID rules, and delivery/review handoffs that
connect these definitions.

The setup workflow manages these two links as one installation:

```text
~/.config/opencode/agents         -> <repository>/opencode/agents
~/.config/opencode/commands       -> <repository>/opencode/commands
```

Preview setup before changing the global configuration:

```sh
just validate-opencode
just setup-opencode-dry-run
just setup-opencode
just verify-opencode
```

Setup is fail-closed. It will not move, merge, back up, or replace an existing
file, directory, broken symlink, or symlink to another location. It validates
and binds the owned OpenCode configuration root before mutation, then rechecks
the root and each destination; aliases, root substitution, mixed ownership, and
unsafe destinations stop the operation. For an initial migration, review and
import the intended Markdown files first, manually move the existing `agents/`
and `commands/` directories outside the repository and
OpenCode discovery tree, and then rerun setup. If any destination is unsafe,
none of the new links is installed.

Treat the linked checkout as live configuration: newly tracked or modified
agent and command files take effect the next time OpenCode starts. Setup and
uninstall do not create, remove, or modify target-repository plan state.
Do not use the linked checkout for unreviewed branches. Keep provider credentials,
secrets, packages, backups, runtime state, and the rest of `~/.config/opencode`
outside this repository.

## Durable Plan Workflow

The repository includes a project-neutral implementation-plan contract in
[`docs/implementation-plans/README.md`](docs/implementation-plans/README.md),
with synchronized starter copies under
[`opencode/project-template/`](opencode/project-template/). Plans use canonical
single-plan `.erb/plans/<slug>.md` paths or, only for genuinely separately managed
work, `.erb/plans/<subject>/<NN>-<slug>.md` series paths. The top-level Plan
Orchestrator owns durable plan writes and state, while the ERB remains
read-only advisory review. See the
[legacy Weave cleanup checklist](opencode/cleanup/weave-cleanup-checklist.md)
when migrating prior workflow material.

### Human-Controlled Lifecycle

Three human-controlled lifecycle paths keep delivery separate from durable
planning: (1) the Engineering Lead may deliver directly when scope, safety, and
validation are adequate; (2) an explicit `/create-plan` request creates and
persists a plan only; and (3) `/start-plan <existing-plan-path>` executes an
existing canonical lean plan, while no arguments resume the selection in
`.erb/plan-state.json`. Complexity may justify recommending a plan, never
automatic creation. The Lead or ERB may recommend top-level `/consult-plan`
with a reason, trade-off, and proposed scope; it provides non-mutating Plan
Orchestrator advice and neither creates nor authorizes work. The human controls
whether to require, decline, or override that recommendation.

The state file stores only the selected repository-relative plan path. Plan
activity is derived from unchecked TODO or Verification boxes, and the first
unchecked checkbox is the current step. A fully checked plan reports that it has
already been implemented and stops. An explicit valid path repairs missing,
invalid, or stale state. Selection is not an exclusivity or concurrency control;
the most recent explicit selection wins.

An explicit current conversational plan replacement request may split one
unambiguous source into at least two successors. The Plan Orchestrator creates
and re-reads all successors, re-reads the source, and only then retires the
source with an exact-content edit patch. No registry, retained history, or
separate deletion confirmation is required. Existing plan bodies remain
immutable except for evidenced checkbox advancement.

After the Plan Orchestrator creates and validates a plan, an explicit current
human commit request may authorize the Engineering Lead to stage and commit the
canonical plan Markdown. This narrow exception does not authorize the Lead to
create, edit, or execute a plan and excludes `.erb/plan-state.json`. Staging is
approval-gated and uses only exact literal canonical paths from fresh worktree
evidence.

To bootstrap a repository that does not already have plan guidance, copy
`opencode/project-template/docs/implementation-plans/` to the target repository's
`docs/implementation-plans/`, then merge—not replace—the relevant text from
`opencode/project-template/AGENTS-plan-workflow-snippet.md` into its existing
`AGENTS.md`. If either destination already exists, compare and reconcile it
manually rather than overwriting project policy.

`opencode/config/opencode.merge-fragment.jsonc` is a small merge reference, not
an installer and not live configuration. Keep provider credentials, local
plugins, and machine-specific OpenCode settings in the machine-local config.

On another computer, clone the repository, install the global skills with
`just setup` when needed, and run the OpenCode setup commands above. The target
machine must separately provide OpenCode, access to the models named by the
agents, and any required plugins or tools. A full OpenCode restart is required
after setup or definition changes because configuration is loaded at startup.

`just uninstall-opencode-dry-run` previews removal. `just uninstall-opencode`
removes both links only when both still point to this checkout; it never removes
the repository definitions or restores old directories.

## Third-Party Updates

`just update-third-party` runs `npx skills update` by default after verifying
that `~/.agents/skills` points at this repository's `skills/` directory.
Override the command with `SKILLS_UPDATE_COMMAND` when the installer workflow
differs:

```sh
SKILLS_UPDATE_COMMAND="pnpm dlx skills update" just update-third-party
```

Keep third-party updates and lockfile sync separate:

- `just update-third-party` runs the configured installer update command.
- `just update-third-party-dry-run` prints the update command without running it.
- `just sync-third-party-lock` copies the repository `.skill-lock.json` to
  `~/.agents/.skill-lock.json` for installer compatibility. It does not run the
  installer and does not update third-party skill directories.
- `just sync-third-party-lock-dry-run` previews that lockfile copy without
  writing to the global install location.

Use dry-run commands first when checking third-party updates or lockfile sync.
Run mutating update commands only as an explicit maintainer action, after
deciding that the local runtime install or installer lockfile mirror should
change.

Run `sync-third-party-lock` only when a repository `.skill-lock.json` exists and
needs to be mirrored for the installer. If the repository has no lockfile, there
are no lockfile-managed skills to sync; ignored skill directories under
`skills/` are still third-party.

## Validation

Validation checks the repository's actual skill format:

- every discovered skill has `SKILL.md`
- `SKILL.md` starts with YAML front matter
- front matter defines `name` and `description`
- the front matter `name` matches the directory name
- first-party local Markdown links resolve to existing files
- first-party resource files are reachable from `SKILL.md`
- first-party skills are listed in `docs/skill-taxonomy.md`
- first-party skill text does not contain source-project identifiers or
  machine-specific home paths
- when `.skill-lock.json` exists, every lockfile-listed third-party skill is
  present locally
- OpenCode agents and commands do not contain machine-specific home paths, and
  agent permission maps do not name concrete target-repository Just recipes

Installer and definition behavior is covered by
`python3 -m unittest discover -s tests -v`.

First-party skills should not keep unlinked changelogs, placeholder scripts,
generic templates, or copied reference files that no skill instruction can load.
If a resource is useful, link it from `SKILL.md` and keep it specific to the
skill's trigger.

## License

First-party skills and repository tooling are licensed under the MIT License.
See `LICENSE`.

Third-party skills installed into this directory are governed by their own
upstream licenses.
