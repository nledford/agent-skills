---
name: cargo-nextest
description: >
  Rust cargo-nextest guidance. Use when selecting, running, filtering,
  diagnosing, or reporting Rust test runs that use cargo-nextest, nextest
  profiles, retries, partitions, or configuration. Do not use for doctests;
  nextest does not run Rustdoc examples.
user-invocable: false
---

# cargo-nextest

Use this skill to run and interpret Rust tests through
[`cargo-nextest`](https://nexte.st/) in a way that is targeted, reproducible, and
aligned with the repository's own test lanes. Nextest is a test runner for Cargo
tests; it does not replace Rustdoc tests, browser tests, integration environment
setup, or behavior-level validation.

## When to Use This Skill

Use this skill when you need to:

- choose between a direct `cargo nextest run` command and an existing repository
  recipe or script;
- diagnose nextest filtering, retries, timeouts, partitions, profiles, or output;
- update or review `.config/nextest.toml`;
- report nextest evidence in a task summary;
- understand why a nextest run differs from `cargo test`.

Use a broader Rust testing skill when authoring tests, `systematic-debugging`
when a test is failing for an unknown reason, and `rustdoc-guidance` for doctests
or Rust API examples.

## Repository Inspection

Before choosing commands, inspect the current repository:

- `just --list`, `make help`, package scripts, CI files, or README docs for
  existing test lanes;
- `.config/nextest.toml` for profiles, retries, slow-timeout settings, and
  partition behavior;
- workspace `Cargo.toml` files for packages, features, and test targets;
- docs that describe required services, environment variables, fixtures, or
  database setup.

Prefer repository recipes when they own setup, cleanup, service startup,
feature flags, or CI parity. Use direct `cargo nextest` commands for narrow local
iteration only when no repository command covers the case or when the task is
specifically about nextest itself.

## Command Strategy

Run commands from the workspace root unless the repository documents a narrower
working directory.

Common direct commands:

```sh
cargo nextest run
cargo nextest run -p <package>
cargo nextest run -E 'package(<package>)'
cargo nextest run -E 'test(<test-name-substring>)'
cargo nextest run --profile <profile>
```

When direct commands are appropriate:

1. Keep the filter as narrow as the debugging loop allows.
2. Match the repository's normal feature flags and environment.
3. Avoid service-backed or database-backed tests unless required setup and
   cleanup are explicit.
4. Re-run the repository's broader test lane before claiming broad confidence.

## Service and Environment Caveats

Nextest runs each test in a separate process. That improves isolation, but it can
also expose missing setup for:

- databases or migrations;
- service containers or local daemons;
- test fixtures and temporary directories;
- unique run IDs, schemas, ports, buckets, queues, or namespaces;
- environment variables normally supplied by CI or a repository recipe.

Treat missing environment failures in direct nextest commands as setup failures
until the evidence shows a code regression. Prefer fixing the invocation over
weakening tests.

## Filtering, Retries, and Flakes

- Expression filters such as `test(...)`, `package(...)`, and `binary(...)` can
  narrow a run.
- Retries can characterize flakiness but must not hide nondeterminism without a
  root-cause fix.
- Use partitioning only when the repository or CI lane already defines how
  partitions are split and reported.
- Compare repeated runs under the same profile before declaring a failure flaky.

## Doctests

Nextest does not run doctests. Use `cargo test --doc`, `cargo test --doc -p
<package>`, or the repository's Rustdoc recipe when documentation examples
matter.

## Configuration Changes

Edit `.config/nextest.toml` only when the task concerns test-runner policy such
as profiles, retries, timeouts, partitions, output, or status levels. Keep
policy centralized and update repository docs or recipes when user-visible test
lanes change.

## Reporting Expectations

When summarizing nextest work, include:

- the exact repository recipe or direct `cargo nextest` command;
- package, test, filter, profile, and feature scope;
- whether services or environment were recipe-owned or caller-owned;
- pass/fail result and the first relevant failure evidence;
- broader test lanes not run and why;
- any flake characterization and whether a root cause was found.
