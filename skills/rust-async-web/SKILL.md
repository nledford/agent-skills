---
name: rust-async-web
description: Async Rust and Rust web/full-stack guidance. Use when working with Tokio, async tasks, cancellation, timeouts, backpressure, channels, shared state, synchronization, Axum handlers/extractors/state/middleware, Leptos components/server functions/SSR/hydration/WASM, or Axum-Leptos full-stack applications. Use rust-persistence-sql for SQLx/database work and rust-testing-quality for test lanes.
---

# Rust Async And Web

Use this skill for async Rust services and full-stack Rust applications. Keep
runtime, HTTP, UI, and persistence boundaries explicit so domain logic remains
testable without the framework. Use
[`hexagonal-architecture`](../hexagonal-architecture/SKILL.md) when handlers,
jobs, server functions, message consumers, persistence, or external clients need
formal ports/adapters or shared application use cases.

## Workflow

1. Inspect the runtime and stack: `Cargo.toml` features, `tokio` runtime setup,
   Axum routers, Leptos app/hydration configuration, server functions, WASM
   build target, middleware, tracing, and existing test recipes.
2. Define externally observable behavior with BDD-style acceptance criteria.
   Keep domain invariants in framework-independent types where practical.
3. Design task ownership, cancellation, timeouts, backpressure, shared state,
   and error propagation before adding handlers or components.
4. Implement narrow vertical slices: domain logic, adapter/handler/server
   function, UI or response behavior, and tests.
5. Verify the server side, client/WASM side, and hydration/SSR behavior with the
   repository's commands.

## Async And Tokio Checklist

- Do not block the async runtime with CPU-heavy work, synchronous I/O, or long
  lock holds. Use async APIs or `spawn_blocking` when appropriate.
- Every spawned task has an ownership story: cancellation, shutdown, error
  reporting, tracing context, and whether its `JoinHandle` is awaited,
  supervised, or deliberately detached.
- Use `JoinSet`, task trackers, semaphores, or bounded queues when spawning many
  related tasks so concurrency and shutdown stay explicit.
- Use `tokio::time::timeout` or cancellation tokens at external boundaries
  where unbounded waiting would leak resources or stall requests.
- Treat `tokio::select!` cancellation as real control flow. Dropped branches
  must be safe to cancel or explicitly protected.
- Prefer bounded channels for backpressure. Choose `mpsc`, `oneshot`, `watch`,
  or `broadcast` according to fan-out and state semantics.
- Use `Arc` for shared ownership, and choose `std::sync`, `tokio::sync`, or
  message passing based on whether work crosses `.await` points.
- Avoid holding non-async mutex guards, database transactions, or borrowed
  request data across `.await` unless the type and invariant explicitly support
  it.

## Axum

- Keep routers, handlers, extractors, state, and middleware thin. Move domain
  decisions into services or domain modules that can be tested without HTTP.
- Use typed extractors for inputs and `State`/substates for application state.
  Store shared state in `Arc` when it must be cloned into handlers.
- Convert domain and adapter errors into HTTP responses at the edge. Avoid
  leaking database, framework, or internal error details to clients.
- Validate payload size, content type, authentication, authorization, and input
  shape before invoking domain behavior.
- Prefer Tower middleware or extractors for cross-cutting HTTP concerns such as
  tracing, auth, timeouts, compression, and request ids.
- Tests should cover handler behavior through routers where HTTP semantics
  matter and through pure functions where they do not.

## Leptos And Axum-Leptos

- Decide whether behavior belongs in CSR, SSR, server functions, actions,
  resources, or ordinary backend routes. Keep security-sensitive work on the
  server.
- Server functions are trust boundaries. Validate input, authorization, and
  idempotency server-side even when the client UI already checks them.
- Components should keep state derivation clear. Avoid burying domain rules in
  signal plumbing when a normal Rust function or type can own the rule.
- SSR and hydration must render compatible markup. Avoid browser-only APIs,
  nondeterministic values, or time-dependent output during server rendering
  unless guarded for the target.
- WASM code should avoid unavailable server APIs and large unnecessary
  dependencies. Check crate features and target-specific modules.
- Axum-Leptos integrations should keep router state, server function context,
  static assets, fallback handling, and error pages explicit.

## Commands

Prefer repository scripts for full-stack apps because they often manage CSS,
WASM, assets, environment, and services. Useful direct checks include:

```sh
cargo check -p <server-package> --all-targets
cargo check -p <client-package> --target wasm32-unknown-unknown
cargo test -p <package>
cargo clippy -p <package> --all-targets -- -D warnings
```

For final confidence, run the repository's broader Rust, browser, and service
tests when the change affects hydrated UI, routing, server functions, or HTTP
behavior.

## Common Pitfalls

- Detached tasks that hide panics, ignore shutdown, or continue using stale
  state after a request is gone.
- Unbounded channels or queues that turn overload into memory growth.
- Mapping every error to `500` or every auth failure to the same response without
  preserving observability.
- Calling SQL or external services directly from UI components instead of a
  server-side boundary.
- Hydration mismatches caused by random ids, current time, locale, feature
  differences, or browser-only APIs during SSR.
- Sharing mutable state because it is convenient rather than because the domain
  requires shared mutation.

## Review Checklist

- Async work has bounded lifetime, cancellation, timeout, and backpressure.
- Handler/component/server-function boundaries are thin and testable.
- Domain invariants are not duplicated across UI, HTTP, and persistence layers.
- Errors are actionable internally and safe externally.
- Shared state and locks cannot deadlock, block the runtime, or leak across
  unrelated requests.
- Server-rendered and client-hydrated output agree for the changed behavior.
- Tests cover the behavior at the lowest useful layer plus at least one
  framework boundary when routing, extraction, hydration, or server functions
  are part of the change.
