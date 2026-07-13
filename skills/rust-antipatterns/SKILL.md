---
name: rust-antipatterns
description: Rust anti-pattern detection and correction guidance. Use when reviewing or refactoring Rust code for generated-code smells, borrow-checker workarounds, unnecessary clones, Arc<Mutex> misuse, boxed indirection, deref polymorphism, deny-warnings misuse, panic/unwrap at boundaries, async overuse, leaky framework or SQL types, brittle tests, or architecture boundary violations. Do not use for ordinary Rust implementation; use rust-engineering instead.
---

# Rust Anti-Patterns

Use this skill to identify Rust designs that are likely to be ineffective,
counterproductive, brittle, or unidiomatic for the repository's actual needs.
Treat an anti-pattern finding as a risk claim: verify it in context before
reporting or refactoring it.

## Use When

- Reviewing Rust code, generated Rust, macros, public APIs, async services,
  persistence adapters, tests, or refactors for maintainability and correctness
  risks.
- The code works around ownership, lifetimes, trait bounds, async constraints, or
  test setup with broad indirection.
- Architecture boundaries are blurred by framework, ORM, SQL, HTTP, SDK, Tokio,
  or serialization types in core APIs.
- The user asks for Rust smells, anti-patterns, cleanup, or idiomatic review.

For positive pattern selection, use
[`rust-design-patterns`](../rust-design-patterns/SKILL.md). Read-only smell
identification may use this skill independently. When correcting an issue, load
[`rust-engineering`](../rust-engineering/SKILL.md). For requested reviews, pair
this skill with [`rust-code-review`](../rust-code-review/SKILL.md),
[`code-review`](../code-review/SKILL.md), and
[`review-verification-protocol`](../review-verification-protocol/SKILL.md).

## Common Anti-Patterns

- **Clone to satisfy the borrow checker:** `.clone()` is added to silence
  ownership errors without checking allocation, stale data, semantic copying, or
  simpler data flow.
- **Shared mutability by reflex:** `Arc<Mutex<_>>`, `Rc<RefCell<_>>`, global
  state, or channels are used before ownership transfer, message passing, or
  narrower mutation is considered.
- **Boxing or leaking to appease lifetimes:** heap indirection, `'static`
  requirements, `Box::leak`, or broad owned strings hide a simpler lifetime or
  ownership design.
- **Deref polymorphism:** `Deref` is used to emulate inheritance or expose a
  wrapped type's full API when explicit methods or composition would keep the
  contract clearer.
- **Crate-root `deny(warnings)`:** library code denies all warnings in source and
  becomes brittle across compiler, dependency, or lint changes. Prefer CI flags
  or specific lints with reasons.
- **Panic at trust boundaries:** `unwrap`, `expect`, indexing, or panicking
  conversions are reachable from user input, files, network, database rows,
  plugins, or external services.
- **Framework leakage:** Axum, Leptos, SQLx, SeaQuery, serde wire shapes, HTTP,
  request, response, or SDK types appear in core domain APIs without an explicit
  adapter decision.
- **Async everywhere:** pure domain logic, simple CLIs, or CPU-bound algorithms
  become async because nearby adapters use async I/O.
- **Macro overreach:** macros replace ordinary functions, traits, derives, or
  builders and produce poor diagnostics or hidden control flow.
- **Anemic domain structs:** domain types only store data while services,
  handlers, repositories, or adapters hold the business decisions.

## Architecture And Test Smells

- Clean, Hexagonal, or Onion boundaries exist only as folder names while
  dependencies still point outward.
- Ports or repository traits only forward one method to one concrete type with no
  substitution, test, or infrastructure boundary.
- Tests mock the domain model instead of external boundaries.
- Async tests rely on sleeps, detached tasks, unclosed channels, or scheduler
  luck.
- Doctests or compile-fail examples are skipped when a public API or macro
  contract changed.
- SQLite-only tests are used as proof of PostgreSQL behavior, or the reverse.

## Refactoring Prompts

- Can ownership move instead of cloning?
- Can an enum, newtype, constructor, or state transition make the invalid case
  unrepresentable?
- Can a plain function or concrete type replace a trait with one implementation?
- Can async be pushed to the adapter or application boundary?
- Can a panic become a typed domain, caller, or adapter error?
- Can a framework, ORM, SDK, or serialization type be mapped at the edge?
- Can a narrower unit, integration, doctest, or compile-fail test protect the
  intended contract?

## Reporting Rules

- Do not flag a pattern as an anti-pattern by name alone. Cite the concrete
  behavior, contract, performance, safety, test, or architecture risk.
- Treat clones of `Arc`, `Rc`, cheap handles, or intentionally owned values as
  acceptable unless the surrounding code proves a real problem.
- Do not require heavyweight verification such as Miri or Loom for ordinary safe
  Rust; reserve it for unsafe code or custom synchronization.
- Prefer targeted fixes over broad idiomatic rewrites.

## Source Anchors

- Rust Design Patterns, [Anti-patterns](https://rust-unofficial.github.io/patterns/anti_patterns/index.html).
- Rust Design Patterns, [Clone to satisfy the borrow checker](https://github.com/rust-unofficial/patterns/blob/main/src/anti_patterns/borrow_clone.md).
- Rust Design Patterns, [`#![deny(warnings)]`](https://github.com/rust-unofficial/patterns/blob/main/src/anti_patterns/deny-warnings.md).
- Rust Design Patterns, [Deref polymorphism](https://github.com/rust-unofficial/patterns/blob/main/src/anti_patterns/deref.md).
