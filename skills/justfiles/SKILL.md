---
name: justfiles
description: Create, refactor, audit, and explain Justfiles for the just command runner. Use when writing or changing Justfile recipes, variables, parameters, groups, imports/modules, aliases, shells/scripts, safety gates, or project workflow commands. Do not use when only running existing recipes without assessing or changing Justfile design, or for hosted CI/release-provider or Docker/OCI/Compose semantics beyond the Just wrappers that invoke them.
---

# Justfiles

## Purpose

Use this skill to design Justfiles that make project workflows discoverable,
repeatable, safe, and easy for humans and AI agents to run.

`just` is a command runner, not a build system. Use it to name and orchestrate
project commands such as setup, test, lint, format, build, run, docs, database,
container, CI, release, and deployment workflows. Do not use it as a replacement
for Make-style file freshness, a package manager, a secret store, a production
orchestrator, or large application logic.

Prefer a Justfile when the project needs a small, inspectable command surface
that works across tools and languages. Prefer external scripts when logic is
long, stateful, hard to quote, or needs unit tests. Prefer package-manager
scripts for package-local workflows that should remain inside that package.

## Source and version rules

- Treat the official manual, upstream repository, and local `just --version` as
  authoritative. Use community examples only as heuristics.
- Do not invent syntax. Verify uncommon features against current docs before
  using them.
- Prefer stable, widely available syntax. Before using modules, `[script]`,
  argument metadata, alternate-shell attributes, or other advanced behavior,
  load
  [`references/version-and-advanced-syntax.md`](references/version-and-advanced-syntax.md)
  and confirm the repository's declared or installed minimum version.
- Inspect `shell()` expressions before `--dry-run`; support for non-executing dry
  runs is version-sensitive.

## Agent workflow

1. Inspect before editing:
   - Root `Justfile`, `.justfile`, `justfile`, and files under `just/**`.
   - External scripts wrapped by recipes, commonly `scripts/**` or
     `scripts/just/**`.
   - Current command surface with `just --list --unsorted` and `just --summary`.
   - Local version with `just --version` when using version-sensitive syntax.
2. Clarify the workflow contract: recipe users, expected inputs, prerequisites,
   side effects, environment variables, safety level, and verification command.
3. Keep public recipes human-first: names should describe workflows, doc comments
   should explain intent, and defaults should help users discover commands.
4. Use the smallest safe implementation:
   - Simple one-liners stay inline.
   - Shell-specific or multi-line logic uses a shebang/script recipe or external
     script.
   - Reusable or testable logic moves to an external script with a thin recipe
     wrapper.
5. Preserve behavior while refactoring. Prefer aliases, wrapper recipes, or
   documented deprecations over silent renames of established commands.
6. Validate parse, listing, formatting, dry runs, and affected recipes before
   reporting completion.

## Structure and organization

- Put high-value public workflows near the top or make them prominent through
  groups and doc comments.
- Use lowercase kebab-case recipe names such as `test-backend`, `db-reset`, or
  `release-preview`. Prefer verbs for actions and nouns for information recipes:
  `build`, `test-web`, `docs-open`, `db-status`.
- Use short variables for shared constants, not hidden configuration systems.
  Keep names lowercase with underscores, for example `root := justfile_directory()`.
- Use parameters for deliberate user choices. Give safe defaults when they are
  genuinely safe.
- Use aliases for common abbreviations only when they improve ergonomics without
  hiding intent: `alias t := test`.
- Mark helpers private with `[private]` or a leading `_`; keep them out of normal
  listings unless users should call them directly.
- Avoid surprising side effects in default, list, status, check, or info recipes.
  Destructive, remote, production, or credentialed recipes must be explicit.

## Comments, docs, and listings

- A comment immediately above a recipe appears in `just --list`. Use concise
  imperative summaries: `# Run backend tests.`
- When combining doc comments with attributes, put the doc comment first and the
  attributes immediately above the recipe.
- Use `[doc('...')]` only when the visible description should differ from nearby
  source comments. Use `[doc]` to suppress noisy helper documentation.
- Mention parameters, examples, prerequisites, environment variables, side
  effects, and safety concerns near the recipe when they affect correct use.
- Keep `just --list` scannable. Put long tutorials in project docs and link or
  reference them from a short recipe comment.
- Make the default useful. For broadly compatible Justfiles, use a default recipe
  that lists workflows. If the project pins `just` 1.52+, `set default-list :=
  true` is also available.

## Groups

Use groups for non-trivial Justfiles unless there is a clear reason not to. They
make `just --list`, `just --groups`, and agent inspection more navigable.

- Group by workflow or domain: `setup`, `quality`, `dev`, `docs`, `db`,
  `containers`, `ci`, `release`, `deploy`, `maintenance`, `internal`.
- Keep group names stable, short, and user-facing. Avoid clever names.
- Put helper recipes in `internal` or mark them private.
- A recipe may belong to multiple groups when it is useful in both views, but do
  not over-tag.

```just
root := justfile_directory()

# List available workflows.
[group('help')]
default:
    @just --list --unsorted

alias t := test

# Format source files.
[group('quality')]
fmt:
    cargo fmt --all

# Run lints.
[group('quality')]
lint: fmt
    cargo clippy --all-targets --all-features -- -D warnings

# Run tests; pass extra Cargo arguments after `--`.
[group('quality')]
test *args='':
    cargo test {{ args }}

# Run the local verification lane.
[group('quality')]
verify: lint test

# Preview deployment without changing remote state.
[group('ops')]
deploy-plan env='staging':
    "{{ root }}/scripts/just/deploy" plan '{{ env }}'

# Deploy to the selected environment.
[confirm]
[group('ops')]
deploy env='staging': (deploy-plan env)
    "{{ root }}/scripts/just/deploy" apply '{{ env }}'

[group('internal')]
[private]
_need tool:
    command -v '{{ tool }}' >/dev/null
```

## Advanced Structure And Shells

Start with one root Justfile and portable one-line recipes. Load
[`references/version-and-advanced-syntax.md`](references/version-and-advanced-syntax.md)
when splitting with imports/modules, changing shells, adding shebang recipes, or
using version-sensitive syntax. Keep complex, stateful, or testable logic in an
external script with a thin recipe wrapper.

## Safety and human-agent collaboration

- Public recipes should be deterministic, minimally interactive by default, and
  safe to run in local development.
- Add dry-run, preview, check, status, or info recipes before destructive apply
  recipes: `deploy-plan` before `deploy`, `db-reset-preview` before
  `db-reset-danger`.
- Use `[confirm]` for destructive or remote operations, but do not rely on a
  prompt as the only safety control. Also validate environment, target, branch,
  credentials, and production safeguards in scripts or recipe logic.
- Never print secrets. Dotenv-loaded values are environment variables referenced
  as `$NAME`, not Just variables like `{{NAME}}`.
- Treat `just --evaluate` output as sensitive because it prints variable values,
  including values derived from the environment or command expressions. Evaluate
  only named, known non-sensitive variables when needed; otherwise skip it and
  report why. Redact captured output.
- Make CI and agent workflows explicit: recipes for setup, fast checks, full
  verification, formatting, linting, generated-code refresh, and drift checks
  should be easy to discover.

## Workflow ownership routing

- Load [`script-engineering`](../script-engineering/SKILL.md) when interpreter
  availability, script-language selection, external script design, or script
  testing is material; keep this skill focused on recipe syntax, discoverability,
  parameters, orchestration, and Just-specific validation.

- Load [`ci-release-engineering`](../ci-release-engineering/SKILL.md) when a
  change affects hosted pipeline triggers, jobs, permissions, artifacts, or
  automated release behavior; keep this skill focused on the Just recipe the
  pipeline invokes.
- Load [`container-engineering`](../container-engineering/SKILL.md) when a
  change affects Dockerfile, OCI image, or Compose semantics; keep this skill
  focused on container command wrappers and recipe design.

## Security and supply-chain routing

- Load [`dependency-supply-chain-review`](../dependency-supply-chain-review/SKILL.md)
  when recipes change dependency updates, package-manager setup, install scripts,
  curl-piped commands, one-off CLIs, CI/bootstrap tooling, generated code,
  container/toolchain pins, or other provenance/advisory surfaces.
- Load [`threat-modeling`](../threat-modeling/SKILL.md) when recipes introduce new
  credentialed remote operations, deployment/release/data-export flows,
  background jobs, external-service trust boundaries, or privileged/destructive
  command surfaces that need actors, assets, and data flows mapped.
- Load [`security-review`](../security-review/SKILL.md) for concrete recipe logic
  that handles secrets, auth, command execution, paths, production targets, or
  other implemented trust boundaries.
- Use [`security-review-evidence`](../security-review-evidence/SKILL.md) when
  recipe validation collects sensitive command output, logs, or artifacts.

## Refactoring and maintenance

Audit an existing Justfile for:

- Duplicate commands that should become variables, helper recipes, or scripts.
- Ambiguous names such as `run2`, `new-test`, or `fix`.
- Hidden dependencies on local tools, directories, services, or environment.
- Unsafe defaults, unguarded destructive operations, production targets, or
  secret exposure.
- Recipe bodies that should be external scripts.
- Missing doc comments, groups, aliases, or default/list discoverability.
- Quoting bugs, unportable shell assumptions, and path assumptions.
- Recursive `just` calls that accidentally recompute variables or rerun setup.

Refactor in behavior-preserving steps. Keep command names stable when other
docs, CI, hooks, or users may call them. After edits, inspect list output because
that is the user and agent interface.

## Methodology alignment

- BDD: organize public recipes around observable workflows users ask for, such as
  `setup`, `test`, `release-preview`, or `deploy-plan`.
- DDD: when workflows map to domain concepts, group them by bounded context or
  domain lifecycle rather than by implementation detail.
- TDD: make test, lint, format, and verification recipes fast, repeatable, and
  easy to run while iterating. Prefer narrow recipes plus a documented full lane.

Apply these pragmatically; do not force methodology labels into simple command
runner maintenance.

## Common pitfalls

- Treating Justfiles like Makefiles with file targets or freshness semantics.
- Forgetting ordinary recipes execute line-by-line, so multi-line shell state may
  not persist unless using continuations, shebang/script recipes, or a script.
- Leaving `{{parameter}}` unquoted when spaces or shell metacharacters are
  possible.
- Using `.env` values as `{{JUST_VARIABLES}}` instead of shell `$VARIABLES`.
- Hiding important workflows in private helpers or external scripts without
  public wrapper recipes.
- Adding interactive prompts to default CI or agent recipes.
- Depending on newest `just` features without checking the local/pinned version.
- Letting imports/modules make the command surface harder to discover.
- Refactoring recipe names without updating docs, CI, hooks, and scripts.

## Acceptance checklist

Before finishing Justfile work, verify:

- `just --version` is compatible with any syntax you added.
- `just --list --unsorted`, `just --groups`, and `just --summary` show a clear,
  navigable command surface.
- `just --show <recipe>` and, after checking version and `shell()` expressions,
  `just --dry-run <recipe> [args...]` match intended behavior for changed recipes.
- Named, known non-sensitive variables resolve with `just --evaluate <variable>`
  when that check is needed; blanket evaluation is avoided when values may be
  sensitive.
- `just --fmt --check` passes when the repository uses `just` formatting; note
  that formatting behavior is not part of `just`'s compatibility guarantee.
- Affected recipes or their wrapped scripts were actually run when safe, or their
  non-execution is explicitly justified.
- Documentation, CI, hooks, and references to renamed or moved recipes are
  updated.
- Destructive, remote, production, and secret-sensitive workflows have preview,
  confirmation, environment validation, and redacted output.
