---
created: 2025-12-16
modified: 2026-05-28
reviewed: 2026-05-28
name: cargo-nextest
description: >
  Chidori cargo-nextest guidance. Use when selecting or diagnosing Rust test
  lanes, filtering nextest runs through repo-owned Just recipes, or working with
  nextest behavior in this workspace.
user-invocable: false
allowed-tools: Bash, Read, Grep, Glob
---

# cargo-nextest in Chidori

This skill owns nextest-specific execution caveats for Chidori: profiles,
filters, retries, timeouts, partitioning, output interpretation, run-scoped test
database IDs, and when raw `cargo nextest` is unsafe. Test placement and test
category ownership belong in `docs/agents/testing.md`; agent command-lane
selection belongs in `docs/agents/validation.md`; setup and runbook mechanics
belong in `docs/operations/local-development.md` and the root `Justfile`.

Chidori uses cargo-nextest through root `just` recipes. Do not create another
nextest configuration, bypass the repo recipes for database-backed tests, or
copy generic CI examples into this repository. The single checked-in nextest
configuration is `.config/nextest.toml`.

## When to Use This Skill

Use this skill when you need to:

- Apply nextest-specific caveats after choosing a lane from `docs/agents/validation.md`.
- Diagnose nextest filtering, retries, timeouts, partitioning, or profile
  behavior.
- Interpret nextest output from a root `just` recipe.
- Adjust `.config/nextest.toml` intentionally.

Use `rust-testing` when authoring tests, `systematic-debugging` when a test is
failing unexpectedly, and `rustdoc-guidance` for doctests and Rust API examples.

## Nextest-Backed Lanes

Run commands from the repository root. Use `just --list` and
`docs/agents/validation.md` for the current lane map; this skill explains
nextest-specific caveats after a lane has been selected. Raw `cargo nextest` is
only for focused local iteration when no recipe covers the case, and never for
database-dependent backend coverage unless the required env and cleanup behavior
are explicitly configured.

## Backend Database Rules

Backend recipes that invoke nextest own the service setup and cleanup contract:

- Database-backed tests require `TEST_DATABASE_URL`.
- Backend nextest runs must set a run-scoped
  `CHIDORI_TEST_DATABASE_RUN_ID` before template-cloned PostgreSQL test
  databases are created.
- Parallel or partitioned lanes must use unique run IDs per run/lane.
- Docker-backed backend recipes clean Chidori-managed test databases before and
  after runs so stale databases do not accumulate.

Missing env failures in direct commands are setup failures, not necessarily code
regressions. Prefer fixing the lane invocation instead of weakening tests.

## Filtering and Focused Iteration

If a root recipe exposes a package, test, or profile parameter, use the recipe.
If you must run raw nextest for a narrow local loop:

1. State why the root recipe is insufficient.
2. Confirm the test does not need repo-managed database setup.
3. Keep the command narrow and temporary.
4. Re-run the relevant root recipe before claiming repository confidence.

Useful nextest concepts:

- Expression filters such as `test(...)`, `package(...)`, and `binary(...)` can
  narrow a run.
- Each test runs in its own process, which improves isolation compared with
  in-process `cargo test`.
- Retries can characterize flakiness but must not hide nondeterminism without a
  root-cause fix.

## Doctests

Nextest does not run doctests. In Chidori, use `just test-rustdoc` for Rustdoc
examples rather than ad hoc `cargo test --doc` in final validation.

## Configuration Changes

Only edit `.config/nextest.toml` when the task is explicitly about test-runner
policy, retries, timeouts, partitioning, or output. Keep policy centralized in
that file and update `docs/agents/validation.md` if the public lane behavior
changes.

## Reporting Expectations

When summarizing a nextest-related run, include:

- The exact root recipe or intentionally narrow direct command.
- Whether service-backed env was recipe-owned or caller-owned.
- The affected package/test/filter/profile.
- Pass/fail result and the first relevant failure evidence.
- Any broader lane not run and why.

## References

- Chidori validation lanes: `docs/agents/validation.md`
- Chidori testing strategy: `docs/agents/testing.md`
- Nextest configuration: `.config/nextest.toml`
- Upstream nextest docs: <https://nexte.st/>
