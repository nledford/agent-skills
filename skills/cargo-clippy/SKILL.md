---
name: cargo-clippy
description: >
  Rust Clippy guidance through cargo clippy. Use when Rust linting, Clippy
  warnings, CI lint failures, cargo clippy --fix, or Rust code-quality work
  requires choosing, running, interpreting, or documenting targeted Clippy
  checks.
user-invocable: false
---

# Cargo Clippy

Use this skill to choose, run, interpret, and document Rust Clippy checks in a
way that is targeted, reproducible, and proportionate to the task scope. Clippy
is a Rust lint tool; it complements, but never replaces, `cargo check`,
formatting, tests, security review, or behavior verification.

Primary references:

- Official Clippy usage: <https://doc.rust-lang.org/clippy/usage.html>
- Official Clippy configuration: <https://doc.rust-lang.org/clippy/configuration.html>
- Official Clippy CI guidance:
  <https://doc.rust-lang.org/clippy/continuous_integration/index.html>

## Repository Inspection

Before choosing a command, inspect the current repository:

- `just --list`, `make help`, package scripts, CI files, or README docs for
  existing lint lanes;
- workspace `Cargo.toml` files for packages, features, `rust-version`, and
  `[lints]` policy;
- `clippy.toml` or `.clippy.toml` for configured lint behavior;
- project docs for feature posture, generated code, database offline modes, or
  platform-specific requirements.

Prefer repository recipes when they encode feature flags, toolchain versions,
environment setup, or CI parity. Use direct Cargo commands when no recipe exists
or when the task is specifically about Clippy behavior.

## When to Use Clippy

Use Clippy when it provides code-quality or completion evidence for Rust work:

- after modifying Rust source files;
- before handing off Rust implementation work;
- when investigating idiomatic Rust, avoidable clones, error handling,
  performance footguns, confusing control flow, or maintainability issues;
- after significant refactors, especially across crate, API, domain, async, FFI,
  or unsafe boundaries;
- with package-scoped commands for localized changes in large workspaces;
- with strict CI-style settings when final verification or repository policy
  requires warnings as errors.

## When Not to Use Clippy

- Do not treat Clippy as a replacement for tests, `cargo check`, formatting, or
  behavior verification.
- Do not repeatedly run workspace-wide Clippy while iterating on a small crate if
  a package-scoped command is available.
- Do not run Clippy after purely non-Rust documentation changes unless Rustdoc
  examples or repository policy require it.
- Do not run `cargo clippy --fix` without checking the working tree first; it may
  modify many files.
- Do not enable the whole `clippy::restriction` group globally. Cherry-pick
  individual restriction lints that express a deliberate policy.
- Do not blindly silence lints. Use targeted attributes and explain non-obvious
  suppressions.

## Command Strategy

Choose the narrowest useful command, then broaden only when evidence needs to
cover more packages, targets, or features.

```sh
cargo clippy
cargo clippy -p <package>
cargo clippy --workspace --all-targets
cargo clippy --workspace --all-targets --all-features -- -D warnings
```

Useful variations:

```sh
cargo clippy -p <package> -- --no-deps
cargo clippy --message-format=json -p <package>
cargo clippy -- -W clippy::pedantic
cargo clippy -- -W clippy::nursery
cargo clippy -- -W clippy::<specific_restriction_lint>
```

Use `--all-features` only when the repository's feature graph supports it for
the requested target. Match documented CI features when final confidence matters.

## Automatic Fixes

Use `cargo clippy --fix` as a refactoring aid, not as a substitute for review.

1. Confirm the working tree state before running it.
2. Prefer package-scoped fixes for localized work.
3. Re-read the diff after fixes.
4. Run formatting if needed.
5. Re-run the narrowest relevant Clippy command and affected tests.

## Lint Levels and Configuration

- `allow` suppresses a lint.
- `warn` reports a lint as a warning.
- `deny` reports a lint as an error and returns a non-zero exit code.
- `forbid` cannot be overridden by `allow`; reserve it for deliberate repository
  policy.

Use source-level attributes when a command-line setting is not the right scope:

```rust
#![warn(clippy::all, clippy::pedantic)]

#[allow(clippy::too_many_arguments)]
fn boundary_adapter(/* ... */) {}
```

Prefer the narrowest scope: item before module, module before crate. For
non-obvious suppressions, add a short reason near the attribute. When available
and appropriate, `#[expect(clippy::lint_name, reason = "...")]` can be better
than `#[allow(...)]` because it reports stale suppressions.

Persistent policy belongs in existing repository docs, `Cargo.toml` `[lints]`,
or Clippy config files. Do not introduce repository-wide policy because one task
needed a local exception.

## Special Code Surfaces

- Generated code: avoid hand-editing generated files. Suppress at the generation
  boundary or adjust the generator when practical.
- FFI, unsafe, platform, or wire-format code: prioritize correctness and stable
  layout over stylistic rewrites. Use targeted allows with reasons.
- Macros: inspect expansion impact before applying mechanical changes.
- Examples, benchmarks, and tests: lint findings may be valid, but readability
  or fixture clarity can justify targeted allows.
- Intentionally non-idiomatic compatibility code: document the invariant or
  compatibility reason rather than making a behavior-changing stylistic fix.

## Lint Remediation Policy

When Clippy reports findings:

1. Read and understand the lint before changing code.
2. Prefer behavior-preserving, idiomatic fixes.
3. Add or update tests when a lint fix could affect behavior.
4. For behavior-changing fixes, explain the risk before applying the change
   unless the task explicitly authorizes that change.
5. Use targeted `#[allow(clippy::...)]` only when the code is intentional or the
   lint is a false positive.
6. Add a short reason near non-obvious `allow` or `expect` attributes.
7. Re-run the narrowest relevant Clippy command after fixes.
8. Do not consider the task complete while relevant Clippy errors, test failures,
   compilation errors, or formatting failures remain unresolved or unexplained.

## Reporting Expectations

When Clippy is part of a task summary, report:

- the exact command run and its scope;
- whether `-D warnings` was used;
- whether failures were Clippy lints or rustc warnings;
- any targeted `allow` or `expect` attributes added and why;
- any Clippy command intentionally not run because a narrower or different check
  was more appropriate.
