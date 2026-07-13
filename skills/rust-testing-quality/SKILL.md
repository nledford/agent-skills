---
name: rust-testing-quality
description: Rust testing and quality-gate guidance. Use when writing, updating, running, filtering, or reporting Rust unit, integration, end-to-end, property-style, compile-fail, or Rustdoc tests; when applying TDD or BDD to Rust changes; or when using cargo fmt, cargo check, cargo test, cargo test --doc, cargo clippy, cargo-nextest, Bacon/bacon.toml feedback loops, and CI-oriented Rust validation.
---

# Rust Testing And Quality

Use this skill to build fast feedback loops and credible final evidence for
Rust changes. Prefer repository recipes when they encode toolchain versions,
services, features, databases, or CI parity.

Load [`rust-engineering`](../rust-engineering/SKILL.md) when the test task also
changes core Rust implementation. Do not require it for test-only or review-only
work.

## Workflow

1. Inspect `Cargo.toml`, workspace layout, `rust-toolchain`, `bacon.toml`,
   `.config/nextest.toml`, CI files, Justfile/Makefile/scripts, README/AGENTS
   docs, and existing tests.
2. Define expected behavior before editing. Use TDD for behavior changes and
   BDD-style Given/When/Then acceptance criteria for externally visible flows.
3. Pick the narrowest useful test level, write or update a failing test when
   practical, then implement the smallest change that passes it.
4. Iterate with package or test filters. Broaden to workspace and CI-like lanes
   only after the local loop is stable.
5. Report exact commands, scope, pass/fail result, and any skipped validation.

## Test Level Selection

- Unit tests: pure functions, domain rules, error mapping, parsers, algorithms,
  state transitions, and edge cases.
- Integration tests: public crate APIs, adapters, persistence boundaries,
  service wiring, feature combinations, and cross-module behavior.
- End-to-end tests: externally observable workflows where unit or integration
  tests cannot prove behavior.
- Property-style tests: invariants over many inputs, parsers/serializers,
  ordering, idempotence, and round trips.
- Rustdoc tests: public examples readers will copy. Remember `cargo nextest`
  does not run doctests.
- Compile-fail tests or doctests: macro contracts, type-state APIs, trait-bound
  errors, and misuse that should not compile.

## Async Rust And Tokio Tests

- Use `#[tokio::test]` when the test must await async application services,
  adapters, channels, timers, spawned tasks, or Tokio I/O. Keep pure domain tests
  synchronous and independent from Tokio.
- Test async application services at hexagonal boundaries with fake outbound
  ports for repositories, clients, queues, clocks, and external services. The
  fake should model success, domain-relevant failures, timeout/cancellation, and
  ordering only where those are part of the behavior.
- Test real async adapters with integration tests against the actual framework,
  database, queue, filesystem, or client contract. Do not use adapter tests as a
  substitute for narrow domain tests.
- For BDD-style flows, drive the public API, inbound adapter, or use case. Avoid
  Given/When/Then steps that depend on private tasks, Tokio channels, or database
  rows unless those mechanisms are the public contract.
- Test cancellation by creating a `CancellationToken`, starting the work, sending
  cancellation or closing the relevant channel, then awaiting the `JoinHandle` or
  `JoinSet` result. Assert externally visible cleanup, not just that a branch was
  reached.
- Test timeouts, retries, intervals, and backoff with Tokio time controls such as
  `#[tokio::test(start_paused = true)]`, `tokio::time::pause`, and
  `tokio::time::advance` when the repository's Tokio features support them.
  Avoid real sleeps and arbitrary retry delays in tests.
- Coordinate tests with channels, barriers, or observable state instead of racing
  the scheduler. Bound all spawned work, close senders, abort only with intent,
  and join tasks before the test exits.
- Use the runtime flavor intentionally. `current_thread` can make single-threaded
  scheduling assumptions visible; the multithreaded runtime is better evidence
  for `Send` server/worker code.
- Avoid nested runtimes in tests. If production code needs explicit runtime
  construction, keep it behind a sync boundary and test the async core directly.

## Command Strategy

Use the repo's documented command first. When direct Cargo commands are
appropriate, start narrow and then broaden:

```sh
cargo fmt
cargo fmt --check
cargo check -p <package> --all-targets
cargo test -p <package> <test_name>
cargo test --doc -p <package>
cargo nextest run -p <package>
cargo clippy -p <package> --all-targets -- -D warnings
```

Final or CI-like checks often need broader scope:

```sh
cargo check --workspace --all-targets
cargo test --workspace
cargo test --doc --workspace
cargo nextest run --workspace
cargo clippy --workspace --all-targets --all-features -- -D warnings
```

Adapt `--all-features` to the repository's feature policy. Some workspaces have
platform-specific or mutually incompatible features; match CI when final
confidence matters.

## Bacon Feedback Loops

Use [Bacon](https://dystroy.org/bacon/) for continuous local Cargo feedback only
when the repository adopts it or the task asks to establish that workflow.
Prefer a checked-in `bacon.toml` over undocumented personal commands, and verify
current Bacon syntax before creating or changing the file. Start from
`bacon --init` when generating a new configuration.

For a minimal explicit configuration:

```toml
default_job = "check"

[jobs.check]
command = ["cargo", "check"]

[jobs.test]
command = ["cargo", "test"]
need_stdout = true
```

- Run `bacon` for `default_job` and `bacon test` for the named test job.
- Keep `command` as an executable-token array. Match package, workspace, target,
  and feature flags to the repository instead of copying broad flags blindly.
- Bacon already watches conventional Rust paths. Add `watch` entries only for
  relevant nonstandard inputs, or set `default_watch = false` when the job must
  watch only explicitly listed paths.
- Keep long-running Axum or Leptos process jobs in the framework workflow; use
  [`rust-async-web`](../rust-async-web/SKILL.md) for restart and server/client
  coordination.
- Treat Bacon as an iteration loop, not final evidence. Run the repository's
  direct or CI-equivalent Cargo commands before handoff.

## cargo-nextest

- Use nextest for fast, isolated Rust test execution when the repository uses it
  or when direct Cargo tests are too slow for iteration.
- Inspect `.config/nextest.toml` before changing profiles, retries, timeouts, or
  partitions.
- Filter intentionally:

```sh
cargo nextest run -E 'package(<package>)'
cargo nextest run -E 'test(<test-name-substring>)'
cargo nextest run --profile <profile>
```

- Nextest runs each test in a separate process. Treat missing service, database,
  fixture, environment variable, or port setup as invocation evidence until the
  failure proves a code regression.
- Retries can characterize flakiness; they should not hide it without a root
  cause or explicit repository policy.

## Clippy And Formatting

- `cargo fmt` and `cargo fmt --check` cover formatting only.
- `cargo clippy` complements `cargo check` and tests; it does not replace them.
- Do not run `cargo clippy --fix` without checking the working tree and reading
  the generated diff.
- Use `#[expect(..., reason = "...")]` only when the project's MSRV/toolchain is
  Rust 1.81 or newer and the lint is intentionally inapplicable. For an older
  MSRV, use a narrowly scoped `#[allow(...)]` with an explanatory comment.
  Verify the suppression against the intended lint and supported configuration.
- Do not enable the entire `clippy::restriction` group globally; choose specific
  lints that express project policy.

## Rustdoc Tests

- Add doctests for public examples that should stay accurate across refactors.
- Keep examples deterministic, small, and free of secrets, services, ambient
  `.env`, real databases, timing assumptions, and large setup.
- Use `no_run` for examples that should compile but not execute, `compile_fail`
  for invalid usage, and `ignore` only when no reliable executable form exists.
- Document `# Errors`, `# Panics`, and `# Safety` where callers need those
  contracts.

## Review Checklist

- Tests name the behavior, not the implementation detail.
- Regression tests fail on the old bug and pass for the right reason.
- BDD scenarios cover observable outcomes; unit tests cover domain edge cases
  and invariants.
- Tests are deterministic: no shared global state, order dependence, real clock
  sleeps, uncontrolled ports, or cross-test database contamination.
- Async tests await or supervise all spawned work, close channels deliberately,
  and exercise cancellation/timeout behavior when those contracts changed.
- Feature flags, target-specific code, examples, macros, doctests, and generated
  code are validated when touched.
- CI evidence includes formatting, compile, tests, doctests when relevant,
  linting, and repository-specific checks such as SQLx offline metadata when
  the change touches queries.

## Anti-Patterns

- Only testing the happy path after changing error handling, ownership, or API
  contracts.
- Treating snapshot churn, broad mocks, sleeps, retries, or fixture rewrites as
  proof of correctness.
- Using `#[tokio::test]` for pure domain behavior that would be faster and
  clearer as a synchronous unit test.
- Relying on wall-clock sleeps, scheduler luck, detached tasks, or unclosed
  channels to make async tests pass.
- Running only nextest when doctests or compile-fail examples carry the changed
  contract.
- Silencing Clippy or rustc warnings without explaining why the warning is
  intentionally acceptable.

## Successful Use

The final handoff states what behavior was protected, which command(s) ran, what
scope they covered, and what residual validation risk remains.
