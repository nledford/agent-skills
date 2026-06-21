---
name: git-commit
description: Write high-quality git commits and commit messages. Use when the user asks to commit changes, split a working tree into logical commits, improve commit messages, prepare reviewer-friendly history, or apply Conventional Commits guidance in any plain git repository.
---

# Git Commit Quality

Use this skill to produce clean, maintainable, reviewer-friendly `git`
history. Prefer several well-scoped commits over one large mixed-purpose commit
when the working tree contains separable changes.

## Core Principles

- Make each commit atomic: one coherent change, one reason, one review unit.
- Make commits logical: related files and tests belong together; unrelated work
  does not.
- Make commits reviewable: a reviewer should understand the intent from the
  commit message and confirm it from the diff.
- Make history useful later: future readers should understand what changed and
  why without reverse-engineering every line.
- Follow local repository conventions over generic advice when they are clear.
- Do not create commits unless the user or active workflow authorizes commits;
  otherwise propose grouping and draft messages.

## Workflow

1. Detect repository conventions.
   - Inspect recent history, for example `git log --oneline -10`.
   - Check project docs such as contributing guides, commit templates, hook
     configuration, or release notes when present.
   - Prefer existing style, casing, type names, scopes, ticket references, and
     body/footer conventions.
   - Do not introduce a new convention into an established repository without a
     clear reason.

2. Inspect the working tree.
   - Review `git status --short` before staging.
   - Review unstaged changes with `git diff` and staged changes with
     `git diff --staged`.
   - Identify generated files, lockfiles, snapshots, vendored files,
     dependency updates, local machine files, editor state, and other artifacts
     that need extra care.
   - Never stage secrets, credentials, private keys, environment files with real
     values, generated junk, or unrelated artifacts.

3. Choose commit groups.
   - Commit after a coherent unit of work is complete.
   - Avoid committing unrelated changes together.
   - Avoid committing broken code unless the repository explicitly uses
     checkpoint or WIP commits.
   - Separate formatting-only changes from behavior changes when practical.
   - Separate refactors from feature or bug-fix changes when practical.
   - Separate dependency updates from code changes when practical.
   - Separate tests from implementation when that improves reviewability; keep
     them together when the tests are the best evidence for the same behavior
     change.
   - Use partial staging, such as `git add -p`, when a file contains unrelated
     edits that belong in different commits.

4. Validate before committing.
   - Run the most relevant available formatter, linter, typecheck, build, or
     test command when practical.
   - If full validation is too expensive, run focused checks for the changed
     area and remember the limitation for the final summary.
   - Before every commit, check `git diff --staged` and confirm only intended
     files are staged.

5. Write the commit message.
   - Use a concise subject line; aim for about 50 characters when practical and
     avoid exceeding 72 without a good reason.
   - Use imperative mood where appropriate: `Add`, `Fix`, `Refactor`, `Remove`,
     `Document`, `Update`.
   - Explain what changed and why. The diff shows how.
   - Add a body when context, rationale, tradeoffs, side effects, migration
     notes, or notable implementation details matter.
   - Separate subject, body, and footers with blank lines.
   - Wrap body text around 72 characters when practical.
   - Avoid vague subjects such as `updates`, `misc`, `fix stuff`, `changes`,
     `wip`, or `temp` in durable history.

6. Report the result.
   - Summarize what was committed and why the grouping was chosen.
   - Include commit hashes when available.
   - State validation performed and any validation limitations.

## Conventional Commits

Conventional Commits is a recommended structured format when a repository uses
it or when no local convention conflicts with it. It is not an unconditional
requirement.

Format:

```text
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

Common types:

- `feat`: add user-facing or externally visible functionality.
- `fix`: correct broken behavior.
- `docs`: documentation-only changes.
- `test`: add or update tests without production behavior changes.
- `refactor`: restructure code without changing behavior.
- `chore`: routine maintenance that does not fit a more specific type.
- `build`: build system, dependency, or packaging changes.
- `ci`: continuous integration configuration or scripts.
- `style`: formatting or style-only changes with no behavior change.
- `perf`: performance improvement.

Use scopes to name the affected area when helpful and consistent with the
project, for example `fix(parser): handle empty input`.

Breaking changes:

- Add `!` after the type or scope, such as `feat(api)!: require signed tokens`.
- Add a `BREAKING CHANGE:` footer explaining what changed and how users should
  adapt.
- Use either form when local convention allows it; use both when extra clarity
  helps.

Examples:

```text
feat(auth): add passkey enrollment
fix(import): preserve file timestamps
docs: document backup restore workflow
test(parser): cover quoted delimiter edge cases
refactor(cache): isolate eviction policy
perf(search): avoid duplicate index scans
```

Breaking-change examples:

```text
feat(api)!: require explicit pagination limits

BREAKING CHANGE: list endpoints now reject requests without a `limit`
parameter. Set `limit` explicitly to preserve previous behavior.
```

```text
refactor(config): remove legacy environment aliases

The aliases obscured precedence rules and made invalid configurations look
valid. Keep only the documented variable names.

BREAKING CHANGE: `OLD_CACHE_URL` and `OLD_DB_URL` are no longer read.
Use `CACHE_URL` and `DATABASE_URL` instead.
```

## Message Examples

Poor subjects and better alternatives:

| Poor | Better |
| --- | --- |
| `updates` | `Update image cache expiration rules` |
| `fix stuff` | `Fix retry loop for transient upload errors` |
| `misc changes` | Split into focused commits with specific subjects |
| `WIP` | `Add draft import queue behind feature flag` if WIP commits are allowed |
| `changed auth` | `Fix session renewal after password reset` |

Subject-only commit:

```text
docs: fix typo in installation guide
```

Commit with body:

```text
fix(cache): prevent stale entries after rename

Renaming an item updated the primary record but left the old cache key in
place. Invalidate both the old and new keys so subsequent reads cannot return
stale metadata.
```

Commit with body and footers:

```text
refactor(import): stream large CSV files

The previous importer loaded entire files into memory before validation.
Streaming keeps memory usage bounded and lets validation report the first
failing row earlier.

Refs: DATA-214
```

Non-Conventional style can be equally valid when local history uses it:

```text
Stream large CSV imports

Keep memory usage bounded by validating records as they are read instead of
loading the full file before processing.
```

## Splitting a Mixed Working Tree

When the working tree contains separable changes, split them into logical
commits. Example:

```text
Changed files:
- src/importer.rs              # new streaming importer behavior
- tests/importer_large.rs      # coverage for large files
- src/importer.rs              # unrelated whitespace cleanup
- README.md                    # document importer limits
- Cargo.lock                   # dependency update from parser upgrade
```

Prefer commits like:

1. `style(import): normalize importer formatting`
   - Only formatting or whitespace cleanup.
2. `build(parser): update CSV parser dependency`
   - Dependency manifest and lockfile changes, plus required compatibility
     adjustment if inseparable.
3. `feat(import): stream large CSV files`
   - Implementation and focused behavior tests for the new importer behavior.
4. `docs(import): document CSV size limits`
   - Documentation update once the behavior is established.

If implementation and tests are easiest to review together, keep them in the
same behavior commit. If tests document a separate regression or require a
distinct review, commit them separately with a `test:` message.

## Pre-Commit Checklist

- Local convention checked.
- Working tree inspected.
- Commit grouping chosen and unrelated edits kept out.
- Secrets, local files, generated junk, and unintended artifacts excluded.
- Lockfiles, generated files, snapshots, vendored files, and dependencies are
  included only when intentional and explained by the commit.
- Relevant validation run, or limitation recorded.
- Staged diff reviewed.
- Commit message explains what changed and why.
- Final response will summarize commits, hashes, validation, and limitations.

## When to Ask the User

Ask for clarification only when the desired grouping is genuinely ambiguous or
risky, for example:

- The working tree contains unrelated user changes and it is unclear what may be
  committed.
- A generated file, lockfile, snapshot, vendored file, or dependency update looks
  accidental.
- The repository convention conflicts with the user's requested message style.
- The user requested a single commit, but the changes are clearly separable and
  mixing them would make review or revert materially worse.

Otherwise, proceed with the safest coherent grouping and explain the choice.
