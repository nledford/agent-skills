---
name: rust-code-review
description: Review Rust code with Rust-specific rigor. Use with code-review when changes touch Rust ownership, lifetimes, traits, error contracts, crate boundaries, feature flags, tests, Rustdoc, async, Tokio, Axum, Leptos, SQLx, SeaQuery, SeaORM, Diesel, SQLite, unsafe code, macros, FFI, public APIs, design patterns, anti-patterns, or performance-sensitive behavior. Use sql-engineering, postgresql-sql-engineering, or sqlite-sql-engineering too for database-native schema, SQL, migrations, privileges, or query plans.
---

# Rust Code Review

Use this skill as a specialist lens with
[`code-review`](../code-review/SKILL.md), not as a replacement for it. Keep
findings tied to concrete behavior, contracts, safety, performance, or
maintainability risk.

Before reporting findings, apply
[`review-verification-protocol`](../review-verification-protocol/SKILL.md).

## Use When

- Reviewing Rust source, tests, examples, benchmarks, macros, build scripts, or
  generated Rust contracts.
- Changes involve ownership, borrowing, lifetimes, trait bounds, public APIs,
  crate boundaries, feature flags, error handling, async runtime behavior,
  concurrency, HTTP/UI behavior, database access, SQL, unsafe code, FFI, macros,
  panic behavior, performance, or resource management.
- A Rust CI failure, Clippy finding, nextest failure, doctest failure,
  compile-time macro failure, SQLx prepare failure, Miri/Loom concern, or
  compile error needs review judgment.

## Review Workflow

1. Start with the general `code-review` intent, affected surfaces, and validation
   status.
2. Identify the Rust-specific risk: type contract, ownership, API shape, error
   semantics, async/concurrency behavior, web boundary, persistence boundary,
   unsafe invariant, macro expansion, allocation, or performance.
3. Read the full enclosing module or API, not just the diff hunk.
4. Search for callers, trait impls, feature flags, generated mappings, tests,
   SQL migrations, docs, and CI recipes before claiming a contract is broken or
   unused.
   Use local code navigation for references, implementations, call relationships,
   and diagnostics when semantic evidence helps. Use direct reads/search for exact
   strings, docs, config, logs, fixtures, and generated or macro-expanded code,
   and repository commands for tests, builds, or other validation.
5. Use the relevant implementation skill for deeper context:
   [`rust-engineering`](../rust-engineering/SKILL.md),
   [`rust-testing-quality`](../rust-testing-quality/SKILL.md),
   [`rust-async-web`](../rust-async-web/SKILL.md), or
   [`rust-persistence-sql`](../rust-persistence-sql/SKILL.md).
   Add [`rust-design-patterns`](../rust-design-patterns/SKILL.md) when judging a
   deliberate pattern choice, or
   [`rust-antipatterns`](../rust-antipatterns/SKILL.md) when reviewing a
   smell-focused concern.
   Add [`sql-engineering`](../sql-engineering/SKILL.md),
   [`postgresql-sql-engineering`](../postgresql-sql-engineering/SKILL.md), or
   [`sqlite-sql-engineering`](../sqlite-sql-engineering/SKILL.md) when
   database-native schema, SQL, migrations, privileges, RLS, PRAGMAs, locking,
   or query plans are part of the review.
6. Prefer fixes that make invalid states unrepresentable, preserve public
   contracts deliberately, and keep unsafe obligations small and documented.
7. Verify with the relevant Rust lane or report missing evidence explicitly.

## Rust Review Checklist

Correctness and API:

- Public names, visibility, trait bounds, lifetimes, feature flags, and error
  contracts match the intended caller contract.
- Ownership avoids unnecessary clones, hidden aliasing, stale references, and
  lifetime over-generalization.
- Domain invariants are represented in types, constructors, constraints, or
  state transitions rather than scattered checks.
- `Result`, `Option`, panic, and cancellation behavior are documented or obvious
  from the API.

Async, web, and persistence:

- Async code does not block the runtime, leak tasks, ignore cancellation, hold
  incompatible guards across `.await`, or use unbounded queues without a reason.
- Tokio runtime construction stays at process/test edges: no nested runtimes, no
  hidden blocking work inside async APIs, and explicit `spawn_blocking` or worker
  boundaries for unavoidable blocking/CPU-heavy operations.
- Spawned tasks have ownership and supervision: `JoinHandle`, `JoinSet`, or task
  tracker results are observed; detached tasks have a shutdown path,
  instrumentation, and a documented reason.
- Cancellation is cooperative and tested where it is part of the contract:
  cancellation tokens, channel closure, signal handling, timeouts, and task
  joining line up with graceful shutdown behavior.
- Async boundaries follow the architecture: domain logic remains framework- and
  Tokio-independent where practical; application services orchestrate async
  ports; adapters own runtime, channel, retry, timeout, tracing, and driver
  details.
- Async trait choices are justified: native async traits, explicit future return
  types, boxed futures, or `async-trait` match the repository's MSRV,
  object-safety needs, allocation tolerance, dyn-dispatch needs, and `Send`
  requirements.
- Axum handlers, Leptos components/server functions, and persistence adapters
  are thin enough for domain logic to be tested outside the framework.
- SQLx queries, SeaQuery builders, migrations, transactions, constraints, and
  indexes preserve database invariants. Bind runtime query values; construct DDL
  identifiers, migrations, constraints, and indexes safely as static reviewed
  SQL or through a reviewed builder, then review their invariants.
- Query macros behind tests, target-specific code, or features have offline
  metadata prepared and checked with the repository-supported Cargo target and
  feature matrix forwarded after `--`. Require matching `SQLX_OFFLINE=true`
  Cargo checks for every supported configuration; use
  [`rust-persistence-sql`](../rust-persistence-sql/SKILL.md) for the command
  shape and database setup.
- SeaQuery is justified by genuine dynamic query composition and does not hide
  simple static SQL that `sqlx` macros could check.
- PostgreSQL-native and SQLite-native schema, index, privilege, RLS, PRAGMA,
  transaction, and plan concerns are reviewed with the database skills.

Safety, macros, and performance:

- Unsafe code has a small boundary, explicit safety comments, documented
  invariants, and risk-appropriate tests or tooling.
- Atomics and locks prove the needed synchronization without decorative
  `SeqCst`, accidental deadlocks, or runtime blocking.
- Macros have clear expansion, hygiene, diagnostics, feature gates, and
  compile-fail coverage for caller-facing errors.
- Performance changes are tied to a measured bottleneck or a clearly bounded
  complexity/allocation issue.

Testing and documentation:

- Tests cover the changed behavior at the lowest useful layer plus framework or
  database boundaries where those semantics matter.
- Doctests are run when public examples or Rustdoc contracts changed.
- Clippy suppressions are narrow and justified.
- Missing validation is called out as residual risk, not hidden.

Useful verification commands include:

```sh
cargo fmt --check
cargo check --workspace --all-targets
cargo test --workspace
cargo test --doc --workspace
cargo nextest run --workspace
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo sqlx prepare --check --workspace -- --workspace --all-targets --features <supported-feature-set>
SQLX_OFFLINE=true cargo check --workspace --all-targets --features <supported-feature-set>
```

Use repository recipes instead when they encode the correct toolchain, features,
services, or target matrix. When all targets and all features are compatible,
the corresponding metadata command can be
`cargo sqlx prepare -- --all-targets --all-features`; otherwise, forward the
supported target and feature arguments after `--` and use the matching
workspace/check variant.

## Reporting Rules

- Report Rust findings through the `code-review` finding format and severity
  scale.
- Cite the concrete type, function, trait impl, module, migration, query, test,
  or command.
- Do not flag idiomatic alternatives as defects unless the current code creates
  a real behavior, contract, safety, performance, or maintainability risk.
- Do not require heavyweight Miri/Loom evidence for ordinary safe Rust. Reserve
  those gates for unsafe, atomics, hand-rolled synchronization, or concurrency
  primitives where normal tests cannot prove the invariant.
- Do not turn a review into a style rewrite. Prefer focused findings with a
  specific failure mode and a practical fix direction.
