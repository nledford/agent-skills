---
name: documentation-engineering
description: Documentation engineering guidance. Use when creating, editing, refactoring, or reviewing Markdown docs, README files, API docs, code comments, examples, rustdoc, pydoc/docstrings, changelog-like guidance, or developer-facing instructions. Do not use for code-only changes unless docs or comments are part of the change.
---

# Documentation Engineering

Use this skill to make documentation concise, accurate, discoverable, and easy to
maintain. Documentation should help the next reader act correctly; it is not a
place for filler, release diary, or generic best-practice dumps.

## Use When

- Creating or editing README files, Markdown docs, architecture notes, API docs,
  code comments, rustdoc, pydoc/docstrings, examples, tutorials, runbooks,
  troubleshooting guides, contributor docs, or agent instructions.
- Reviewing documentation for accuracy after code, config, workflow, schema, or
  public API changes.
- Moving long explanations, examples, templates, or references out of activation-
  critical files into progressively loaded docs.

Do not use this skill for code-only changes with no reader-facing documentation
impact. Use language-specific skills for docstring/rustdoc syntax when code APIs
also change.

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

## API Docs, Rustdoc, and Pydoc

- Public API docs should state purpose, inputs, outputs, errors, side effects,
  panics, safety requirements, examples, and version or stability expectations
  only where those facts affect callers.
- Rustdoc examples should compile or intentionally use `no_run`, `compile_fail`,
  or `ignore` with a reason. Run doctests when public examples change.
- Python docstrings should explain behavior not obvious from names and type
  hints. Include parameters, returns, raises, and examples only when they help
  callers use a public API correctly.
- Keep comments focused on why code is shaped a certain way, not what the next
  line literally does.

## Examples

- Prefer one realistic, minimal example over many variants.
- Keep examples deterministic: fixed seeds, stable clocks, sanitized paths, no
  live secrets, no credentialed URLs, no ambient `.env` assumptions.
- Test examples when the repository has doctests, markdown tests, snapshot tests,
  CLI smoke tests, or docs generation checks.
- Update examples with the API they demonstrate. Do not leave compatibility notes
  for versions the repository no longer supports unless the doc explicitly covers
  migration.

## Avoid AI-Sounding Prose

- Cut vague praise, motivational intros, and filler phrases.
- Use concrete nouns and verbs from the repository domain.
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

## Anti-Patterns

- Long background sections before the reader can run or decide anything.
- Copying library docs into the repository instead of linking or summarizing the
  project-specific part.
- Adding comments to compensate for unclear names or tangled code when a small
  refactor would be clearer.
- Updating docs without checking the code, commands, paths, or tests they cite.
- Treating documentation-only edits as exempt from link, command, or example
  validation when such checks are available.
