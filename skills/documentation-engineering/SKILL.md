---
name: documentation-engineering
description: Documentation engineering guidance. Use when creating, editing, refactoring, or reviewing Markdown docs, README files, API docs, code comments, docstrings, examples, Rustdoc, pydoc, Javadoc, JSDoc/TSDoc, perldoc/POD, documentation tests, or developer-facing instructions. Do not use for code-only changes unless docs or comments are part of the change. For reusable SKILL.md contracts, use create-agent-skill.
---

# Documentation Engineering

Use this skill to make documentation concise, accurate, discoverable, and easy to
maintain. Documentation should help the next reader act correctly; it is not a
place for filler, release diary, or generic best-practice dumps.

## Use When

- Creating or editing README files, Markdown docs, architecture notes, API docs,
  code comments, docstrings, Rustdoc, pydoc, Javadoc, JSDoc/TSDoc,
  perldoc/POD, examples, tutorials, runbooks, troubleshooting guides,
  contributor docs, or agent instructions.
- Reviewing documentation for accuracy after code, config, workflow, schema, or
  public API changes.
- Moving long explanations, examples, templates, or references out of activation-
  critical files into progressively loaded docs.

Do not use this skill for code-only changes with no reader-facing documentation
impact. When a request explicitly limits work to in-code documentation, treat
standalone Markdown, README, runbook, and release-note changes as out of scope
unless they are needed only as source-of-truth evidence or the user widens the
request. Use language-specific skills for documentation syntax and executable
examples when code APIs also change. For reusable agent-skill contracts, load
[`create-agent-skill`](../create-agent-skill/SKILL.md) and use this skill as its
documentation-quality companion.

## Workflow

1. Identify the audience and job: user, operator, contributor, API caller,
   maintainer, reviewer, or future agent.
2. Find the source of truth before writing: code, tests, schemas, CLI output,
   configs, generated docs, current README, design docs, and repo instructions.
3. Put content in the right place. Keep authoritative setup/usage in README or
   docs; keep API contracts with the code; keep long examples in linked
   references; keep comments next to non-obvious implementation decisions.
4. Write the smallest useful doc that lets the reader act. Prefer commands,
   examples, constraints, and failure modes over broad explanation.
5. Validate links, commands, examples, code fences, API names, file paths, and
   generated output where practical.
6. Report what changed, what was verified, and any docs that may still drift with
   code or release behavior.

## Markdown and Structure Rules

- Use headings that match reader tasks. Avoid clever titles.
- Put prerequisites, quick start, common commands, and safety warnings before
  advanced details when they affect first use.
- Keep tables small and scannable. Use lists for decision rules and checklists.
- Use fenced code blocks with language tags when syntax matters.
- Link to canonical local docs rather than duplicating policy in multiple places.
- Remove stale screenshots, copied examples, and placeholders unless they are
  actively maintained by a test or documented generation step.

## In-Code Documentation

- Public API docs should state purpose, inputs, outputs, errors, side effects,
  panics, safety requirements, examples, and version or stability expectations
  only where those facts affect callers.
- Inspect the repository's existing documentation toolchain, build tasks,
  formatter or linter configuration, generated-doc inputs, and local style
  before selecting a syntax or validation command.
- Rustdoc examples should compile or intentionally use `no_run`, `compile_fail`,
  or `ignore` with a reason. Run `cargo test --doc` or the repository's stronger
  doctest lane when public examples change.
- Python docstrings should explain behavior not obvious from names and type
  hints. Include parameters, returns, raises, and examples only when they help
  callers use a public API correctly; run the configured doctest, pytest,
  Sphinx, or documentation lane when examples can execute.
- Javadoc should match the supported Java API and the repository's doclint or
  build-tool conventions. Document type parameters, thrown exceptions, nullness,
  lifecycle, and side effects only when callers need those facts.
- JSDoc/TSDoc should complement rather than repeat static types. Follow the
  configured JSDoc, TypeDoc, ESLint, TypeScript, or package-script conventions,
  and validate examples through the existing project lane.
- perldoc/POD should follow the module's public contract and local POD layout.
  Use `podchecker`, configured distribution tests, or the repository's existing
  documentation check when available.
- Keep comments focused on why code is shaped a certain way, not what the next
  line literally does.

## Missing And Excess Documentation

- Look for unsupported knowledge at public or extension boundaries, safety and
  concurrency constraints, non-obvious invariants, error and side-effect
  behavior, compatibility workarounds, and algorithms whose rationale is not
  recoverable from the code.
- Do not add comments merely to increase documentation coverage. A missing
  comment needs a named reader, a material knowledge gap, and a realistic use or
  maintenance consequence.
- Prefer clearer names, types, or code structure when they can remove the need
  for a comment without hiding an important decision.
- Do not document generated output directly when its maintained source or
  template is the proper edit target.

## Examples

- Prefer one realistic, minimal example over many variants.
- When the format supports executable examples and the example is part of the
  caller contract, prefer an embedded documentation test maintained beside the
  API. Do not force prose-only guidance into a test-shaped example.
- Keep examples deterministic: fixed seeds, stable clocks, sanitized paths, no
  live secrets, no credentialed URLs, no ambient `.env` assumptions.
- Test examples when the repository has doctests, parser or doclint checks,
  distribution tests, snapshot tests, CLI smoke tests, or docs generation
  checks. Prefer the repository-native command instead of adding a new tool only
  for one documentation edit.
- Update examples with the API they demonstrate. Do not leave compatibility notes
  for versions the repository no longer supports unless the doc explicitly covers
  migration.

## Avoid AI-Sounding Prose

- Cut vague praise, motivational intros, and filler phrases.
- Use concrete nouns and verbs from the repository domain.
- Remove copied boilerplate and AI-sounding prose that could describe unrelated
  code without changing meaning.
- Replace generic claims like "robust and scalable" with specific behavior,
  limits, commands, or tradeoffs.
- Do not invent benefits, guarantees, metrics, compatibility, or future work that
  the code and tests do not support.
- Keep tone direct. Dense, accurate docs beat polished but empty paragraphs.

## Review Checklist

- The doc has a clear audience and task.
- Claims match code, tests, configs, commands, or current behavior.
- Local links and referenced files exist.
- Commands are runnable from the stated working directory and do not expose
  secrets or perform surprise destructive actions.
- Examples are minimal, deterministic, sanitized, and maintainable.
- Docs do not duplicate or contradict more authoritative local instructions.
- Comments/docstrings explain caller contracts or non-obvious reasoning.
- In-code formats follow repository conventions and executable examples have
  observed test, parser, linter, generator, or explicitly skipped evidence.

## Anti-Patterns

- Long background sections before the reader can run or decide anything.
- Copying library docs into the repository instead of linking or summarizing the
  project-specific part.
- Adding comments to compensate for unclear names or tangled code when a small
  refactor would be clearer.
- Updating docs without checking the code, commands, paths, or tests they cite.
- Treating documentation-only edits as exempt from link, command, or example
  validation when such checks are available.
