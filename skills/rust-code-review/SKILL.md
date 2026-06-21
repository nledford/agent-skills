---
name: rust-code-review
description: Review Rust code with Rust-specific rigor. Use with code-review when changes touch Rust ownership, lifetimes, traits, error contracts, async, concurrency, unsafe code, atomics, FFI, public APIs, macros, or performance-sensitive Rust behavior.
---

# Rust Code Review

Use this skill as a specialist lens with
[`code-review`](../code-review/SKILL.md), not as a replacement for it. Keep the
review grounded in the actual diff and repository behavior. Load only the
reference files needed for the touched surface.

Before reporting findings, apply
[`review-verification-protocol`](../review-verification-protocol/SKILL.md).

## Use When

- Reviewing Rust source, tests, examples, benchmarks, macros, build scripts, or
  generated Rust contracts.
- Changes involve ownership, borrowing, lifetimes, trait bounds, public APIs,
  error handling, async runtime behavior, concurrency, atomics, unsafe code, FFI,
  layout, panic behavior, performance, or resource management.
- A Rust CI failure, Clippy finding, Miri/Loom concern, doctest failure, or
  compile error needs review judgment.

## Review Workflow

1. Start with the general `code-review` intent, affected surfaces, and validation
   status.
2. Identify the Rust-specific risk: type contract, ownership, API shape, error
   semantics, async/concurrency behavior, unsafe invariant, layout, macro
   expansion, allocation, or performance.
3. Read the full enclosing module or API, not just the diff hunk.
4. Search for callers, trait impls, feature flags, generated mappings, tests,
   docs, and CI recipes before claiming a contract is broken or unused.
5. Use the narrowest reference below that matches the risk.
6. Prefer fixes that make invalid states unrepresentable, preserve public
   contracts deliberately, and keep unsafe obligations small and documented.
7. Verify with the relevant Rust lane: `cargo test`, `cargo nextest`,
   `cargo test --doc`, `cargo clippy`, `cargo miri`, `loom`, formatting, or the
   repository recipe that wraps them.

## Reference Routing

| Review surface | Reference |
| --- | --- |
| Ownership, borrowing, lifetimes, clones, iterators | [references/ownership-borrowing.md](references/ownership-borrowing.md) |
| Lifetime variance and region reasoning | [references/lifetime-variance.md](references/lifetime-variance.md) |
| Result, Option, panic, and error contracts | [references/error-handling.md](references/error-handling.md) |
| Async futures, cancellation, runtime boundaries | [references/async-concurrency.md](references/async-concurrency.md) |
| Send, Sync, locks, atomics, shared state | [references/concurrency-primitives.md](references/concurrency-primitives.md) |
| Memory ordering and fences | [references/memory-ordering.md](references/memory-ordering.md) |
| Hand-rolled lock-free primitives | [references/lock-free-patterns.md](references/lock-free-patterns.md) |
| Concurrency model selection | [references/concurrency-models.md](references/concurrency-models.md) |
| Type layout, repr, PhantomData, auto traits | [references/types-layout.md](references/types-layout.md) |
| Trait, API, object-safety, and interface design | [references/interface-design.md](references/interface-design.md) |
| Drop guards, indices, extension traits, preludes | [references/patterns-in-the-wild.md](references/patterns-in-the-wild.md) |
| Unsafe code, validity, provenance, panic safety | [references/unsafe-deep.md](references/unsafe-deep.md) |
| Common Rust mistakes and Clippy-adjacent patterns | [references/common-mistakes.md](references/common-mistakes.md) |

## Rust Review Checklist

- Public API names, trait bounds, lifetimes, visibility, and error contracts are
  intentional and documented where caller obligations are non-obvious.
- Ownership and borrowing avoid unnecessary clones, hidden aliasing, stale
  references, and lifetime over-generalization.
- `Result`, `Option`, panic, and cancellation behavior match the public contract.
- Async code does not block the runtime, hold incompatible guards across
  `.await`, leak tasks, or hide cancellation-unsafe work.
- Concurrent code names the model and synchronization edges it relies on.
- Unsafe code has a small boundary, clear invariants, safety comments, and tests
  or tooling proportional to risk.
- Atomics use the weakest ordering that proves the required happens-before
  relationship, not decorative `SeqCst`.
- Tests, doctests, Clippy, Miri, Loom, or other validation cover the risk being
  reviewed, or the missing evidence is reported as residual risk.

## Reporting Rules

- Report Rust findings through the `code-review` finding format and severity
  scale.
- Cite the concrete type, function, trait impl, module, test, or command.
- Do not flag idiomatic alternatives as defects unless the current code creates
  a real behavior, contract, safety, performance, or maintainability risk.
- Do not require heavyweight Miri/Loom evidence for ordinary safe Rust. Reserve
  those gates for unsafe, atomics, hand-rolled synchronization, or concurrency
  primitives where normal tests cannot prove the invariant.
