---
name: rust-async-web
description: Async Rust and Rust web/full-stack guidance. Use when working with Tokio, async tasks, cancellation, timeouts, backpressure, channels, shared state, synchronization, Axum handlers/extractors/state/middleware, Leptos components/server functions/SSR/hydration/WASM, or Axum-Leptos full-stack applications. Use api-design for endpoint contracts, observability-engineering for durable telemetry, rust-persistence-sql for SQLx/database work, and rust-testing-quality for test lanes.
---

# Rust Async And Web

Use this skill for async Rust services and full-stack Rust applications. Keep
runtime, HTTP, UI, and persistence boundaries explicit so domain logic remains
testable without the framework. Use
[`hexagonal-architecture`](../hexagonal-architecture/SKILL.md) when handlers,
jobs, server functions, message consumers, persistence, or external clients need
formal ports/adapters or shared application use cases.

Do not use this skill for API-contract-only work such as endpoint/resource
shape, request/response/error envelopes, versioning, pagination, idempotency, or
OpenAPI/AsyncAPI/protobuf artifacts; use [`api-design`](../api-design/SKILL.md)
for those contracts. Do not use it for observability-only work such as
log/metric/trace schemas, context-propagation standards, labels/cardinality,
dashboards, alerts, SLOs, or telemetry sampling; use
[`observability-engineering`](../observability-engineering/SKILL.md). Add this
skill only when the task also changes Tokio, Axum, Leptos, SSR, hydration, WASM,
task, or runtime behavior.

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

## Security Review Prompts

Load [`security-review`](../security-review/SKILL.md) when async/web work
touches auth, authorization, sessions or cookies, CORS/CSRF/CSP, redirects,
SSR/hydration trust boundaries, server functions, uploads/downloads, path
handling, request/response redaction, secrets, external-service calls,
telemetry that may leak sensitive data, or artifact handling. Use
[`threat-modeling`](../threat-modeling/SKILL.md) before or during new auth
middleware, request/SSR/server-function boundaries, background workers, queues,
webhooks, external-service integrations, or sensitive data flows. Use
[`dependency-supply-chain-review`](../dependency-supply-chain-review/SKILL.md)
when Tokio/Axum/Leptos or toolchain dependency changes, generated assets, CI
bootstrap, installers, or binaries raise provenance or advisory questions. Pair
security-sensitive reviews with
[`security-review-evidence`](../security-review-evidence/SKILL.md) when evidence
includes sanitized HTTP traces, logs/spans, browser or server-function payloads,
screenshots, generated assets, or test artifacts.

## When To Choose Async Rust

- Use async deliberately for I/O-bound or high-concurrency work: network
  servers and clients, database calls, queues, workers, orchestration layers,
  file or process I/O with async APIs, and fan-out/fan-in workflows.
- Do not make code async by default. Synchronous Rust is usually clearer for
  CPU-bound algorithms, pure domain logic, simple CLIs, low-concurrency tools,
  and code where blocking APIs are sufficient.
- Async changes API shape. It affects trait boundaries, dependency injection,
  lifetimes, `Send + 'static` requirements for spawned work, cancellation,
  error propagation, and which tests need a runtime.
- Keep blocking libraries behind explicit boundaries. In an async service, wrap
  unavoidable blocking or CPU-heavy work with `tokio::task::spawn_blocking`, a
  dedicated thread pool, or a separate worker process instead of blocking Tokio
  runtime threads.
- Distinguish concurrency from parallelism. Async lets many tasks wait on I/O;
  it does not make CPU-heavy work faster unless that work is moved to real
  parallel execution.

## Architecture Boundaries

- Keep domain logic pure, deterministic, and preferably synchronous. Avoid
  leaking Tokio types, channels, timers, task handles, database pools, request
  types, or framework state into the domain model.
- Put async I/O at application, infrastructure, adapter, or port boundaries.
  Application services/use cases may orchestrate async repositories, clients,
  queues, clocks, and external services while domain objects enforce rules.
- Use ports/traits for async dependencies only where the boundary earns it:
  repositories, external clients, queues, clocks, id generators, and background
  job interfaces. Do not force async into every layer because one adapter is
  async.
- Keep Tokio-specific details in infrastructure adapters and process wiring:
  runtime flavor, channels, task spawning, cancellation tokens, signal handling,
  tracing setup, and adapter-specific retry/timeout policy.
- For async traits, prefer the simplest option the repository supports. Native
  `async fn` in traits can work for static dispatch when the MSRV and auto-trait
  bounds fit; use explicit future return types, boxed futures, or `async-trait`
  when object safety, dyn dispatch, or tighter `Send` control matters.
- Use BDD examples at the system, inbound adapter, or use-case boundary; TDD
  domain rules with sync unit tests; test async application services with fakes;
  and test real adapters with `#[tokio::test]` integration tests.

## Tokio Runtime And Tasks

- Tokio is the async runtime that schedules futures, timers, I/O resources, and
  tasks. An `async fn` does not run until a runtime polls its future.
- Use `#[tokio::main]` for application binaries and `#[tokio::test]` for async
  tests. Use an explicit `tokio::runtime::Runtime` or `Builder` only for sync
  entry points, custom runtime configuration, embedding, or tests that need
  precise runtime control.
- Do not create a nested runtime from code already running inside Tokio. Pass a
  handle, restructure the boundary, or keep runtime construction at process
  edges.
- Use `tokio::spawn` for independent async work that must run concurrently.
  Spawned futures and outputs must be `Send + 'static`.
- Await `JoinHandle`s and handle `Result<T, JoinError>`; panics, aborts, and
  cancellations are not normal successful task results. Detached
  fire-and-forget tasks need an explicit justification, observability, and
  shutdown path.
- Use `JoinSet` or a task tracker for related dynamic task groups so fan-out,
  result collection, error handling, and shutdown are supervised in one place.
- Use `tokio::task::spawn_local` inside a `LocalSet` when `!Send` futures are
  genuinely required. Prefer `Send` futures and `tokio::spawn` for server and
  worker code unless a local-only dependency forces the constraint.
- Use `spawn_blocking` for blocking I/O or CPU-heavy work that must coexist with
  async code. Cancellation does not forcibly stop an already-running blocking
  closure, so give long blocking work its own cooperative stop signal when it
  needs graceful shutdown.
- Instrument async services with `tracing` spans/events around request ids,
  task starts/stops, retries, timeouts, cancellation, queue depth, and adapter
  calls. Preserve useful span context when spawning tasks; load
  [`observability-engineering`](../observability-engineering/SKILL.md) when those
  signals become durable operator-facing telemetry.

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
- Avoid holding non-async mutex guards or borrowed request data across `.await`.
  Keep database transactions narrow, and do not hold them across unrelated,
  slow, or externally-cancellable awaits unless that is the intended consistency
  boundary.

## Tokio Coordination Primitives

- `tokio::select!` races cancellation, channel receive/send, timeouts, signals,
  and child task completion. Treat the losing branches as cancelled; only select
  over futures that are safe to drop or intentionally pinned/protected.
- `tokio::time::timeout` bounds external waits. Convert elapsed time into a
  domain/application error at the boundary rather than letting calls hang
  indefinitely.
- `tokio::time::sleep` is for one-off delays; `interval` is for recurring work.
  Avoid real sleeps in tests; use Tokio time controls where practical.
- Use bounded `mpsc` for work queues and producer/consumer pipelines. Capacity is
  part of the overload policy; unbounded channels require a documented memory
  bound elsewhere.
- Use `oneshot` for a single reply or shutdown acknowledgement, `watch` for
  latest-state notifications such as config or shutdown state, and `broadcast`
  when many subscribers need each event and lag handling is acceptable.
- Use `Semaphore` for concurrency limits around outbound calls, CPU handoff,
  queue consumers, or scarce resources. Do not use spawning alone as a limit.
- Use `tokio::sync::Mutex` or `RwLock` when a guard must be held across `.await`;
  keep critical sections short. Prefer message passing or ownership transfer
  when mutable shared state is only coordinating work.
- Standard `std::sync::Mutex`/`RwLock` can be acceptable in async code when the
  critical section is short, never crosses `.await`, and does not perform
  blocking I/O. This is often clearer for protecting small in-memory state.
- Use `Notify` for lightweight one-to-many wakeups when no data needs to be
  transferred. Use channels when the signal carries work, state, or errors.

## Cancellation And Graceful Shutdown

- Tokio cancellation is cooperative: dropping a future or taking a different
  `select!` branch stops polling that future, but arbitrary blocking work and
  external systems are not forcibly cleaned up for you.
- Use `tokio_util::sync::CancellationToken` to fan cancellation out to tasks that
  should stop together. Clone tokens for background workers, request-scoped
  subwork, long-running tasks, fan-out/fan-in orchestration, and graceful
  shutdown.
- Pass cancellation tokens through application services and adapters that own
  cancellable I/O. Do not pass them into pure domain objects unless cancellation
  is part of the domain language.
- Combine cancellation with `tokio::select!`, `tokio::signal`, channel closure,
  `timeout`, and task joining. Shutdown usually means: stop accepting work,
  signal cancellation, close senders, drain or reject queued work deliberately,
  then await task handles with a bounded timeout.
- Dropping a `JoinHandle` detaches the task; it does not create clean shutdown
  semantics. Spawned tasks must be owned, joined, aborted with intent, or
  supervised by a tracker/`JoinSet`.
- Cancellation does not forcibly stop `spawn_blocking` work, synchronous file or
  process calls, driver operations that ignore cancellation, or remote side
  effects already sent. Design idempotency, timeouts, and cleanup around those
  facts.

```rust
loop {
    tokio::select! {
        _ = token.cancelled() => break,
        maybe_job = jobs.recv() => match maybe_job {
            Some(job) => handle(job).await?,
            None => break, // all senders closed
        },
    }
}
```

## Axum

- Keep routers, handlers, extractors, state, and middleware thin. Move domain
  decisions into services or domain modules that can be tested without HTTP.
- Use typed extractors for inputs and `State`/substates for application state.
  Store shared state in `Arc` when it must be cloned into handlers.
- Convert domain and adapter errors into HTTP responses at the edge. Avoid
  leaking database, framework, or internal error details to clients. Use
  [`api-design`](../api-design/SKILL.md) when status codes, error envelopes,
  route shapes, or request/response payloads are contract decisions.
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

- Introducing async where synchronous code is simpler and sufficient.
- Coupling domain models, value objects, or invariants to Tokio types.
- Confusing async concurrency with CPU parallelism.
- Creating nested runtimes instead of keeping the runtime at process edges.
- Detached tasks that hide panics, ignore shutdown, or continue using stale
  state after a request is gone.
- Ignoring `JoinHandle` results or losing task errors.
- Missing cancellation paths for background workers, request fan-out, or
  long-running orchestration.
- Blocking the async runtime with sync I/O, CPU-heavy work, thread sleeps, or
  long critical sections.
- Holding locks, transactions, or borrowed request data across unrelated awaits.
- Unbounded channels or queues that turn overload into memory growth.
- Mixing blocking and async I/O without an explicit adapter or `spawn_blocking`
  boundary.
- Surprising `Send + 'static` requirements from `tokio::spawn` after borrowing
  request-local data.
- Hiding async trait allocation, object-safety, or `Send` tradeoffs behind a port
  abstraction without documenting the reason.
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
