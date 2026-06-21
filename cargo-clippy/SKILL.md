---
created: 2026-06-02
modified: 2026-06-02
reviewed: 2026-06-02
name: cargo-clippy
description: >
  Chidori guidance for Rust Clippy through cargo clippy. Use when Rust,
  Clippy, lint, cargo clippy, CI warnings, lint fixes, cargo clippy --fix,
  or Rust code quality work requires choosing, running, interpreting, or
  documenting targeted Clippy checks.
user-invocable: false
allowed-tools: Bash, Read, Grep, Glob
---

# Cargo Clippy

Use this skill to choose, run, interpret, and document Rust Clippy checks in a
way that is targeted, reproducible, and proportionate to the task scope. Clippy
is a Rust lint tool; in this repository it complements, but never replaces,
`cargo check`, formatting, tests, browser checks, security review, or
domain-level behavior verification.

Primary references:

- Official Clippy usage: <https://doc.rust-lang.org/clippy/usage.html>
- Official Clippy configuration: <https://doc.rust-lang.org/clippy/configuration.html>
- Official Clippy CI guidance:
  <https://doc.rust-lang.org/clippy/continuous_integration/index.html>

## Repository baseline

- Run commands from the repository root unless a narrower crate directory is
  explicitly required.
- Chidori centralizes validation in root `just` recipes. Prefer `just clippy`,
  `just clippy-ci`, `just clippy-package <package>`, or
  `just clippy-fix <package>` before choosing raw Cargo commands.
- The workspace uses Rust edition 2024 and workspace `rust-version = "1.96.0"`.
  Use the same Rust toolchain for Clippy as for compilation and CI.
- The repo's standard Rust check lane uses
  `SQLX_OFFLINE=true cargo check --workspace --all-targets --features chidori/ssr`.
  Mirror that feature posture for Chidori-wide Clippy unless the task or a repo
  recipe requires a different feature set.
- Do not assume `--all-features` is always the right Chidori command. It is a
  useful generic CI pattern only when the repository's feature graph supports it
  for the requested target.

## When to use Clippy

Use Clippy when it provides code-quality or completion evidence for Rust work:

- after modifying Rust source files;
- before considering Rust implementation work complete;
- when investigating idiomatic Rust, suspicious code, avoidable clones, error
  handling, performance footguns, maintainability issues, or confusing control
  flow;
- before opening, finalizing, or handing off a PR that changes Rust behavior;
- after significant refactors, especially across crate, API, domain, or async
  boundaries;
- with package-scoped commands for localized changes in large workspaces;
- with stricter CI-style settings when the user asks for final verification, the
  repository requires warnings-as-errors, or the changed surface is broad.

## When not to use Clippy

Avoid wasteful or unsafe Clippy use:

- Do not treat Clippy as a replacement for tests, `cargo check`, formatting, or
  behavior verification.
- Do not run broad, long-running commands such as full CI wrappers unless the
  scope clearly requires them.
- Do not repeatedly run workspace-wide Clippy while iterating on a small crate if
  a package-scoped command is available.
- Do not run Clippy after purely non-Rust documentation changes unless repo
  policy or an affected Rustdoc example requires it.
- Do not run `cargo clippy --fix` without first checking the working tree and
  understanding that it may modify many files. `--fix` applies
  machine-applicable suggestions and implies `--all-targets`.
- Do not enable the entire `clippy::restriction` group globally. Cherry-pick
  individual restriction lints that fit the repository's policy.
- Do not blindly silence lints. Use targeted attributes and explain non-obvious
  suppressions.

## Recommended command strategy

Choose the narrowest useful command, then broaden only when the evidence needs
to cover more targets, crates, or features.

### 1. Fast local baseline

```sh
just clippy-package <package>
```

Use for quick feedback when work is localized to one Cargo package. This recipe
uses `-- --no-deps` so it does not lint workspace path dependencies pulled in by
that package.

### 2. Specific package

```sh
just clippy-package <package>
```

Use when the change is isolated to one crate. Add target or feature flags that
match the changed code, for example:

```sh
SQLX_OFFLINE=true cargo clippy -p chidori --all-targets --features ssr -- --no-deps
```

### 3. Specific package without linting path dependencies

```sh
just clippy-package <package>
```

Use `-- --no-deps` when the goal is to lint only the selected crate and not
workspace path dependencies pulled in by Cargo.

### 4. Workspace verification

```sh
just clippy
```

Use when the change affects multiple crates or shared APIs. For Chidori's
standard server-side feature posture, prefer:

```sh
SQLX_OFFLINE=true cargo clippy --workspace --all-targets --features chidori/ssr
```

### 5. CI-style strict run

Generic Cargo pattern when all targets and all features are valid for the repo:

```sh
cargo clippy --workspace --all-targets --all-features -- -D warnings
```

Chidori-oriented strict run that mirrors the existing `just check` feature set:

```sh
just clippy-ci
```

The recipe runs:

```sh
SQLX_OFFLINE=true cargo clippy --workspace --all-targets --features chidori/ssr -- -D warnings
```

`-D warnings` turns every warning into an error. That includes Clippy warnings
and rustc warnings such as `dead_code`, so failures may not all be
`clippy::...` lints.

### 6. Apply automatic fixes

```sh
just clippy-fix <package>
```

The recipe refuses to run unless the working tree is clean, then runs a
package-scoped `cargo clippy --fix`. Treat it as a refactoring aid, not as a
substitute for review. Re-read the diff, run formatting if needed, and re-run the
narrowest relevant Clippy command after applying fixes.

### 7. Select additional lint groups intentionally

```sh
cargo clippy -- -W clippy::pedantic
cargo clippy -- -W clippy::nursery
cargo clippy -- -W clippy::<specific_restriction_lint>
```

Use `clippy::pedantic` or `clippy::nursery` for exploratory quality passes or
when the repository has opted into those lints. For `clippy::restriction`, enable
only specific lints that express an explicit policy; never warn, deny, or forbid
the entire group.

## Advanced Clippy guidance

### Lint levels

- `allow` suppresses a lint.
- `warn` reports a lint as a warning.
- `deny` reports a lint as an error and returns a non-zero exit code, useful for
  CI-style verification.
- `forbid` is stronger than `deny` and cannot be overridden by `allow`; use it
  only for deliberate repository policy.
- Command-line levels are passed after Cargo's `--`, for example:

  ```sh
  cargo clippy -- -A clippy::style -W clippy::box_default -D clippy::perf
  ```

### Lint groups

- `clippy::all` is the default Clippy lint group.
- Category groups such as `clippy::correctness`, `clippy::suspicious`,
  `clippy::style`, `clippy::complexity`, `clippy::perf`, and `clippy::cargo`
  are useful for focused policy discussions.
- `clippy::pedantic` is allow-by-default, opinionated, and may need targeted
  suppressions even in production-quality code.
- `clippy::nursery` is allow-by-default and can be useful for trying lints that
  may still evolve.
- `clippy::restriction` is allow-by-default and intentionally restricts language
  choices. Select individual restriction lints only; the whole group contains
  lints that can conflict with each other or with idiomatic Rust.

### Source-level lint configuration

Use normal Rust lint attributes when a command-line setting is not the right
scope:

```rust
#![allow(clippy::style)]
#![warn(clippy::all, clippy::pedantic)]

#[warn(clippy::box_default)]
fn example() {}

#[allow(clippy::too_many_arguments)]
fn boundary_adapter(/* ... */) {}
```

Prefer the narrowest scope: item before module, module before crate. For
non-obvious suppressions, add a short reason near the attribute. When available
and appropriate, `#[expect(clippy::lint_name, reason = "...")]` can be better
than `#[allow(...)]` because it reports stale suppressions.

`Cargo.toml` `[lints.clippy]` can define persistent lint levels for a package.
Only add persistent policy after checking existing repo conventions and
documenting why the policy should apply beyond one task.

### `clippy.toml` and `.clippy.toml`

Clippy also supports `clippy.toml` or `.clippy.toml` for configurable lint
behavior such as disallowed types or MSRV. This is not a general lint-level
replacement, and not every lint is configurable there. The official docs describe
this configuration surface as unstable, so prefer existing repository patterns
and document any new persistent configuration.

### Machine-readable output

Use Cargo's JSON message format when a tool or script needs structured output:

```sh
cargo clippy --message-format=json -p <package>
```

Do not paste large JSON output into user-facing summaries. Distill it to the
lint, location, cause, and remediation.

### Special code surfaces

- Generated code: avoid hand-editing generated files. Suppress at the generation
  boundary or adjust the generator when practical.
- FFI, unsafe, platform, or wire-format code: prioritize correctness and stable
  layout over stylistic rewrites. Use targeted allows with reasons.
- Macros: inspect the expansion impact before applying mechanical changes.
- Examples, benchmarks, and tests: lint findings may be valid, but readability or
  fixture clarity can justify targeted allows.
- Intentionally non-idiomatic code: document the invariant or compatibility
  reason rather than making a behavior-changing stylistic fix.
- Rare generated or huge-code cases may require `#[cfg(not(clippy))]`, but only
  when ordinary lint attributes are insufficient and the tradeoff is documented.

### False positives and accepted patterns

When Clippy appears wrong, first read the lint's explanation and inspect the
surrounding code. If the pattern is intentional or a false positive, prefer a
narrow source-level suppression with a reason. If the same suppression becomes
policy, document it in repository docs or lint configuration rather than copying
unexplained allows across files.

### `clippy-driver`

Use `clippy-driver` only for non-Cargo projects or unusual build systems that
invoke rustc directly. Do not use it as a general replacement for `rustc` in
Cargo projects; Clippy-built artifacts are not guaranteed to be optimized like
normal rustc artifacts.

## Lint remediation policy

When Clippy reports findings:

1. Read and understand the lint before changing code.
2. Prefer behavior-preserving, idiomatic fixes.
3. Add or update tests when the lint fix could affect behavior.
4. For behavior-changing fixes, explain the risk before applying the change
   unless the task explicitly authorizes that change.
5. Use targeted `#[allow(clippy::...)]` only when the code is intentionally
   written that way or the lint is a false positive.
6. Add a short reason near non-obvious `allow` or `expect` attributes.
7. Re-run the narrowest relevant Clippy command after fixes.
8. Do not consider the task complete while relevant Clippy errors, test failures,
   compilation errors, or formatting failures remain unresolved or unexplained.

## BDD, DDD, and TDD guidance

Keep this skill focused on Rust linting and code-quality verification.

### BDD-style command selection examples

```gherkin
Scenario: Localized crate change
  Given a change only touches crates/chidori-domain Rust code
  When Clippy is needed for iteration
  Then run package-scoped Clippy for that crate before broad workspace checks

Scenario: Cross-crate API refactor
  Given a change updates shared Rust APIs used by several workspace crates
  When final verification is needed
  Then run workspace Clippy with the repository's normal feature posture

Scenario: Final CI-style Rust verification
  Given the user asks whether Rust work is ready to hand off
  When Clippy is part of the verification evidence
  Then run strict Clippy with -D warnings and explain rustc warnings can also fail

Scenario: Documentation-only change
  Given only Markdown docs changed and no Rust examples or Rustdoc snippets changed
  When deciding validation
  Then do not run Clippy unless repository policy requires it
```

### DDD boundary

The domain of this skill is Rust linting through Clippy. Do not turn it into a
general Rust testing, CI, architecture, or refactoring skill. Load the more
specific Rust, SQLx, Axum, testing, or methodology skills when those domains are
the primary task.

### TDD posture

If adding executable helper scripts, tests, or examples around Clippy, define the
expected behavior first, implement the smallest helper, then verify it. If only
editing Markdown skill documentation, use acceptance criteria and documentation
review instead of inventing unnecessary tests.

## Reporting expectations

When Clippy is part of a task summary, report:

- the exact command run and its scope;
- whether `-D warnings` was used;
- whether failures were Clippy lints or rustc warnings;
- any targeted `allow` or `expect` attributes added and why;
- any Clippy command intentionally not run because a narrower or different repo
  check was more appropriate.
