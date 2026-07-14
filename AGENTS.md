# Agent Instructions

This repository is the canonical local source for reusable agent skills. Before
editing skills or repository documentation, read [`README.md`](README.md),
[`docs/skill-taxonomy.md`](docs/skill-taxonomy.md), and
[`docs/cross-reference-map.md`](docs/cross-reference-map.md).

Use the [engineering agent governance guide](docs/engineering-agent-governance.md)
for OpenCode role authority, command ownership, Task boundaries, and handoffs.

## First-Party Skill Rules

- Edit only first-party skills as repository source.
- Treat lockfile-owned or `.gitignore`-ignored directories under `skills/` as
  third-party runtime installs, not first-party project assets.
- Before changing an ambiguous skill directory, run `just list-first-party`,
  `just list-third-party`, or `just inspect <skill>`.
- Do not force-add ignored third-party skill directories or copy raw third-party
  artifacts into first-party skills without explicit review.

## Skill and Docs Maintenance

- Every first-party `skills/<name>/SKILL.md` must be listed in
  [`docs/skill-taxonomy.md`](docs/skill-taxonomy.md).
- Update [`docs/cross-reference-map.md`](docs/cross-reference-map.md) when a
  relationship changes routing, delegation, validation, or required handoffs.
- Use [`docs/skill-review-checklist.md`](docs/skill-review-checklist.md) when
  creating, editing, or reviewing first-party skills.
- Keep first-party skill guidance project-neutral and reusable across
  repositories.

## Validation

- Run `just validate` after skill metadata, taxonomy, cross-reference, or link
  changes.
- Run `just check` for broader repository changes or before handoff when tooling,
  tests, scripts, or validation behavior may be affected.

## Durable Plan Workflow

Project-local implementation plans use the canonical contract in
[`docs/implementation-plans/README.md`](docs/implementation-plans/README.md).
The Planning Coordinator is the exclusive durable-plan writer and the Engineering
Review Board is read-only. Keep OpenCode's live configuration machine-local;
repository files are reviewed definitions and templates, not credentials or a
replacement for a user's `opencode.jsonc`.
