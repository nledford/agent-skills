# Tokio Runtime, Coordination, And Cancellation

Use this reference after loading the parent `rust-async-web` skill when a task
needs detailed Tokio runtime, task, coordination, cancellation, or graceful
shutdown guidance.

## Runtime And Tasks

- Tokio schedules futures, timers, I/O resources, and tasks. An `async fn` does
  not run until a runtime polls its future.
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
- Tokio's blocking-thread limit is intentionally high because blocking calls can
  wait for long periods. Explicitly limit CPU-bound fan-out with a semaphore or
  use a specialized executor; do not treat that limit as CPU parallelism policy.
- A started `spawn_blocking` task cannot be aborted. Keep long-lived blocking
  work on dedicated threads or workers with an explicit stop protocol.
- Instrument async services with tracing around request IDs, task starts and
  stops, retries, timeouts, cancellation, queue depth, and adapter calls. Load
  [`observability-engineering`](../../observability-engineering/SKILL.md) when
  those signals become durable operator-facing telemetry.

## Checklist

- Do not block runtime threads with CPU-heavy work, synchronous I/O, or long
  lock holds. Use async APIs or `spawn_blocking` when appropriate.
- Give every spawned task an ownership story: cancellation, shutdown, error
  reporting, tracing context, and whether its `JoinHandle` is awaited,
  supervised, or deliberately detached.
- Use `JoinSet`, task trackers, semaphores, or bounded queues when spawning many
  related tasks so concurrency and shutdown stay explicit.
- Apply timeouts or cancellation tokens at external boundaries where unbounded
  waiting would leak resources or stall requests.
- Treat `tokio::select!` cancellation as real control flow. Dropped branches
  must be safe to cancel or explicitly protected.
- Prefer bounded channels for backpressure. Choose `mpsc`, `oneshot`, `watch`,
  or `broadcast` according to fan-out and state semantics.
- Choose `std::sync`, `tokio::sync`, or message passing based on whether work
  crosses `.await` points.
- Avoid holding non-async mutex guards or borrowed request data across `.await`.
  Keep database transactions narrow unless a wider consistency boundary is
  deliberate.

## Coordination Primitives

- `tokio::select!` races cancellation, channel operations, timeouts, signals,
  and child completion. Select only over futures that are safe to drop or are
  intentionally pinned or protected.
- `tokio::time::timeout` bounds external waits. Convert elapsed time into an
  application or domain error at the boundary.
- Use `sleep` for one-off delays and `interval` for recurring work. Avoid real
  sleeps in tests; use Tokio time controls where practical.
- Use bounded `mpsc` for work queues. Capacity is part of overload policy;
  unbounded channels require a documented memory bound elsewhere.
- Use `oneshot` for one reply or acknowledgement, `watch` for latest-state
  notifications, and `broadcast` when many subscribers need each event and lag
  handling is acceptable.
- Use `Semaphore` for concurrency limits around outbound calls, CPU handoff,
  queue consumers, or scarce resources. Spawning alone is not a limit.
- Use `tokio::sync::Mutex` or `RwLock` when a guard must cross `.await`, and keep
  critical sections short. Prefer ownership transfer or message passing when
  shared mutation is only coordinating work.
- Standard `std::sync::Mutex` or `RwLock` is acceptable when the critical
  section is short, never crosses `.await`, and performs no blocking I/O.
- Use `Notify` for lightweight wakeups without data. Use channels when the
  signal carries work, state, or errors.

## Cancellation And Graceful Shutdown

- Tokio cancellation is cooperative: dropping a future or taking another
  `select!` branch stops polling it, but blocking work and external systems are
  not forcibly cleaned up.
- Use `tokio_util::sync::CancellationToken` to fan cancellation out to tasks
  that should stop together.
- Pass cancellation through application services and adapters that own
  cancellable I/O. Keep it out of pure domain objects unless it is domain
  language.
- Graceful shutdown usually means stopping acceptance, signalling cancellation,
  closing senders, deliberately draining or rejecting queued work, and joining
  tasks with a bounded timeout.
- Ordinary runtime shutdown may wait indefinitely for started blocking work.
  `Runtime::shutdown_timeout` stops waiting after its timeout, but does not stop
  that work; design it to finish or be managed independently.
- Dropping a `JoinHandle` detaches the task. Own, join, intentionally abort, or
  supervise every spawned task.
- Cancellation does not forcibly stop `spawn_blocking`, synchronous file or
  process calls, driver operations that ignore cancellation, or remote side
  effects already sent. Design idempotency, timeouts, and cleanup around those
  facts.

```rust
loop {
    tokio::select! {
        _ = token.cancelled() => break,
        maybe_job = jobs.recv() => match maybe_job {
            Some(job) => handle(job).await?,
            None => break,
        },
    }
}
```
