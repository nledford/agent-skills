---
name: rust-engineering
description: Core Rust engineering guidance. Use when adding or changing Rust crates, modules, public APIs, domain logic, ownership and lifetime structure, traits, generics, error types, feature flags, workspaces, refactors, design patterns, or declarative/procedural macros. Use api-design for public service/SDK/CLI contracts, observability-engineering for telemetry/logging signal design, rust-testing-quality for test and CI lanes, rust-async-web for Tokio/Axum/Leptos work, rust-persistence-sql for SQLx, SeaQuery, and database adapter work, and rust-code-review for requested reviews.
---

# Rust Engineering

Use this skill for project-neutral Rust implementation and refactoring. Keep the
guidance grounded in the repository's existing architecture, toolchain, and
public contracts.

## Workflow

1. Inspect the local shape first: `Cargo.toml`, workspace members, crate
   boundaries, feature flags, `rust-toolchain`, CI recipes, README/AGENTS docs,
   and nearby modules.
2. State the behavior or domain change in concrete terms. Use BDD-style
   examples for user-visible behavior and DDD language for boundaries,
   invariants, and aggregate-like rules.
3. Choose the smallest crate/module/API boundary that can own the behavior.
   Keep framework, database, and transport concerns outside core domain logic
   unless the crate is explicitly an adapter. Load
   [`hexagonal-architecture`](../hexagonal-architecture/SKILL.md) for
   ports/adapters and external actors, [`clean-architecture`](../clean-architecture/SKILL.md)
   for use-case and interface-adapter boundaries, or
   [`onion-architecture`](../onion-architecture/SKILL.md) for domain/application
   rings.
4. Design the API before filling in code: visibility, ownership, lifetimes,
   trait bounds, error type, feature gating, and caller obligations.
5. Implement in small steps. Prefer clear safe Rust, narrow mutation, explicit
   invariants, and tests close to the behavior.
6. Refactor after tests pass: simplify ownership, collapse accidental
   abstraction, remove duplicated conversions, and make invalid states harder to
   express.
7. Verify with the repository recipe or an appropriately scoped Cargo lane.

## Core Rust Checklist

- Ownership expresses real responsibility. Use `&T`, `&mut T`, owned values,
  `Cow`, `Rc`, or `Arc` deliberately; do not add clones to satisfy the compiler
  without checking allocation, aliasing, and lifetime implications.
- Lifetimes describe relationships already present in the data model. Avoid
  over-generalized lifetimes, self-referential structures, and references stored
  where owned values would simplify the design.
- Traits and generics buy reuse, substitution, or testability. Keep bounds close
  to the item that needs them and avoid generic APIs when one concrete type is
  the honest contract.
- Error handling distinguishes caller errors, domain errors, I/O failures, and
  programmer bugs. Library-like crates should expose typed errors; application
  edges may add context and convert to user-facing responses.
- Keep core domain APIs synchronous unless the domain behavior itself requires
  asynchrony. Push async I/O, Tokio runtime details, channels, and task handles
  to application services, ports, adapters, or process wiring.
- Modules reveal boundaries. Public modules should be stable enough for callers;
  private modules can optimize for clarity and local cohesion.
- Collections and iterators match the semantics: ordering, uniqueness, lookup
  cost, allocation, and borrowing behavior should be intentional.
- Smart pointers have a reason: `Box` for indirection or trait objects, `Rc` for
  single-threaded sharing, `Arc` for cross-thread sharing, `Mutex/RwLock` for
  mutation behind sharing, and `Pin` only when pinning invariants matter.
- `unsafe` is isolated, justified, documented with safety invariants, and tested
  with risk-appropriate tools.

## Project Setup

- Prefer one crate until independent release, feature, dependency, or compile
  boundaries justify a workspace member.
- Use workspace dependencies and lints when they reduce drift. Do not introduce
  workspace-wide policy for a local experiment.
- Feature flags should be additive. Keep defaults intentional, avoid mutually
  exclusive features unless the crate already has a clear policy, and test the
  feature combinations CI claims to support.
- Keep dependencies narrow. Inspect direct and transitive impact with
  `cargo tree` before adding broad crates for small needs.
- Put generated code, build scripts, FFI bindings, examples, benches, and tests
  in conventional locations unless the repository already documents otherwise.

Useful inspection commands:

```sh
cargo metadata --no-deps
cargo tree -p <package>
cargo check -p <package> --all-targets
cargo fmt
```

## Pattern Routing

- Load [`rust-design-patterns`](../rust-design-patterns/SKILL.md) when the Rust
  change needs a deliberate pattern choice: newtypes, enums, builders, RAII
  guards, traits as ports, compose-structs, contained unsafe modules, custom
  traits for complex bounds, or macros.
- Load [`rust-antipatterns`](../rust-antipatterns/SKILL.md) when reviewing or
  refactoring generated-code smells: clone-to-satisfy-borrow-checker,
  reflexive `Arc<Mutex<_>>`, deref polymorphism, panic at trust boundaries,
  async overuse, framework leakage, or brittle Rust tests.

## API and Observability Routing

- Load [`api-design`](../api-design/SKILL.md) when Rust changes define or alter a
  public service, SDK, CLI, serialization, error, pagination, webhook/event, or
  generated-client contract. Keep this skill focused on ownership, types,
  modules, and implementation mechanics.
- Load [`observability-engineering`](../observability-engineering/SKILL.md) when
  Rust changes add or change durable logs, metrics, traces, request/correlation
  IDs, instrumentation fields, or operator-facing diagnostics.

## Security Review Routing

Load [`security-review`](../security-review/SKILL.md) when Rust changes touch
implemented auth or session handling, crypto/randomness, credentials, secrets or
`.env`, filesystem paths, command/process execution, `unsafe`, FFI, plugin
boundaries, HTTP clients, SQL binding, or other trust boundaries. Use
[`dependency-supply-chain-review`](../dependency-supply-chain-review/SKILL.md)
for Cargo dependency bumps, `Cargo.lock` churn, `build.rs`, proc macros, native
crates, toolchain/bootstrap pins, provenance, or advisory questions. Use
[`threat-modeling`](../threat-modeling/SKILL.md) before or during new auth,
service-to-service, FFI/plugin, unsafe, external-client, or sensitive data-flow
boundaries. Pair security-sensitive reviews with
[`security-review-evidence`](../security-review-evidence/SKILL.md) for sanitized
logs, telemetry, build artifacts, dependency reports, or test output.

## Refactoring Guidance

- Protect current behavior first with focused tests, characterization tests, or
  BDD-style acceptance criteria.
- Separate mechanical moves from semantic changes when possible.
- Decide whether the refactor is defensive or simplifying. Add types and
  adapters to protect real invariants; delete indirection when it only forwards
  parameters or preserves obsolete paths.
- Move code toward domain language: named value types, explicit state
  transitions, and constructors that enforce invariants.
- Simplify ownership by changing data flow before adding lifetimes, reference
  cycles, or interior mutability.
- Simplify errors by removing duplicate variants, preserving actionable context,
  and keeping conversion points near adapter boundaries.
- Replace groups of mutually exclusive `Option<T>` fields with enums when only
  one mode is valid.
- Remove dead feature flags completely: call sites, `cfg`s, conditional return
  types, monitoring scaffolding, docs, tests, and dependency gates.
- Move tests with code during module splits, and keep intermediate states
  compiling.
- For performance refactors, measure or reproduce the bottleneck before changing
  algorithms, allocation patterns, locking, or async task structure.

## Macros

- Prefer functions, traits, derives, builders, or generics before macros.
- Use `macro_rules!` for small syntax/repetition patterns with predictable
  expansion. Keep patterns minimal and diagnostics readable.
- Use procedural macros only when compile-time code generation materially
  improves the caller experience. Keep parsing, validation, and generated code
  covered by tests.
- Review macro hygiene, spans, error messages, generated visibility, feature
  gates, and compile-time cost.
- Test caller-facing macro behavior with ordinary tests, doctests,
  `compile_fail` examples, or a compile-test harness when the failure mode is a
  type-system contract.

## Common Crate Guidance

- `serde` / `serde_json`: keep serialization formats explicit at API, storage,
  and message boundaries. Use derives for stable data shapes, custom serializers
  only when the wire contract requires them, and tests for compatibility-sensitive
  JSON.
- `anyhow`: appropriate at application edges, CLIs, and task orchestration where
  context matters more than typed recovery. Library-like crates and domain APIs
  should expose typed errors callers can handle.
- `tokio`: use `rust-async-web` for runtime, task, cancellation, backpressure,
  Axum, and Leptos details. Introduce async deliberately for I/O-bound or
  high-concurrency work; do not hide blocking work inside async functions.
- `reqwest`: keep HTTP clients at adapter boundaries, configure timeouts, handle
  status codes deliberately, avoid logging secrets, and test request/response
  mapping without real network calls when practical.
- `rand` and ID crates: use
  [`random-data-identifiers`](../random-data-identifiers/SKILL.md) for secure
  randomness, deterministic seeds, UUIDs, and collision-resistant identifiers.

## Anti-Patterns

- Fighting borrow errors by cloning, leaking, boxing, or adding `Arc<Mutex<_>>`
  before revisiting ownership.
- Adding abstractions because they are common in other languages rather than
  because this code has multiple real implementations.
- Exposing framework, SQL, HTTP, or serialization types from core domain APIs
  without a deliberate adapter boundary.
- Making feature flags subtractive or environment-sensitive.
- Treating Clippy suggestions, design patterns, or public docs as substitutes
  for behavior tests and explicit contracts.

## Acceptance Criteria

Successful Rust engineering work has:

- a clear behavior or domain reason for the change;
- crate/module/API boundaries that match repository conventions;
- ownership, lifetimes, traits, errors, and features chosen intentionally;
- tests or examples covering the changed behavior or invariant;
- relevant Cargo verification run or a clear explanation of what could not run.
