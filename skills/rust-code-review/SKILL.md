---
name: rust-code-review
description: Review Rust code with Rust-specific rigor. Use with code-review when changes touch Rust ownership, lifetimes, traits, error contracts, crate boundaries, feature flags, tests, Rustdoc, async, Tokio, Axum, Leptos, SQLx, SeaQuery, SeaORM, Diesel, SQLite, unsafe code, macros, FFI, public APIs, or performance-sensitive behavior. Use sql-engineering, postgresql-sql-engineering, or sqlite-sql-engineering too for database-native schema, SQL, migrations, privileges, or query plans.
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
5. Use the relevant implementation skill for deeper context:
   [`rust-engineering`](../rust-engineering/SKILL.md),
   [`rust-testing-quality`](../rust-testing-quality/SKILL.md),
   [`rust-async-web`](../rust-async-web/SKILL.md), or
   [`rust-persistence-sql`](../rust-persistence-sql/SKILL.md).
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
- Axum handlers, Leptos components/server functions, and persistence adapters
  are thin enough for domain logic to be tested outside the framework.
- SQLx queries, SeaQuery builders, migrations, transactions, constraints, and
  indexes preserve database invariants and use bound parameters.
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
cargo sqlx prepare --check --workspace
```

Use repository recipes instead when they encode the correct toolchain, features,
services, or target matrix.

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
