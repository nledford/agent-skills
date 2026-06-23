# Failure Heuristics

Use these prompts after reproducing or clearly characterizing the symptom. They
are diagnostic prompts, not substitutes for evidence.

## Failing Unit Tests

- Run the single failing test with full failure output.
- Read the assertion, fixture/setup, and implementation under test.
- Check whether expected behavior is a stable contract or stale expectation.
- Prefer a targeted logic fix plus a regression assertion over broad refactors.

## Failing Integration Tests

- Identify the boundary: API, database, filesystem, network, cache, queue,
  browser, auth, external service, or process.
- Verify service readiness, test data, configuration, migrations, ports, and
  request/response shape before assuming application logic is wrong.
- Inspect both sides of the boundary and any serialization/deserialization layer.

## Flaky Tests

- Re-run narrowly to estimate frequency and look for timing, ordering, shared
  state, clock, random seed, port, filesystem, database, cache, or concurrency
  coupling.
- Prefer deterministic synchronization, isolated fixtures, stable clocks/seeds,
  and explicit readiness checks over sleeps or retries.
- If retries are part of the correct system behavior, test the retry semantics
  explicitly rather than using retries to hide a test race.

## Async and Concurrency Bugs

- Look for missing awaits/joins, task cancellation, lock ordering, holding locks
  across awaits, non-atomic check-then-act sequences, shared mutable state,
  channel closure, backpressure, timeout semantics, and scheduler assumptions.
- Reproduce with constrained concurrency or repeated runs, then add deterministic
  coordination where possible.

## State Management Bugs

- Trace state initialization, transitions, invalid states, reset/cleanup paths,
  cache invalidation, lifecycle events, and stale closures/references.
- Compare the domain state machine or invariant against the actual transitions.

## Data Mapping or Serialization Bugs

- Check field names, casing, enum representation, optional/null/default behavior,
  timezone/locale/encoding, precision loss, unknown fields, and version skew.
- Verify round-trip behavior and boundary contracts with realistic samples.

## Boundary Condition Bugs

- Test empty, single, many, max/min, null/none, duplicate, missing, invalid,
  overflow, Unicode, timezone, permission, and ordering cases.
- Confirm whether inclusive/exclusive bounds and default values match the domain.

## Configuration and Environment Bugs

- Compare the failing command/environment to a known-good one: env vars, config
  files, secrets, feature flags, working directory, profile, target, OS, shell,
  container, network, clock, locale, and permissions.
- Treat environment drift as a hypothesis, not a conclusion, until verified.

## Dependency or Version Issues

- Inspect lockfiles, toolchain files, package manager output, release notes,
  feature flags, transitive dependency changes, generated metadata, and API
  deprecations.
- Prefer pinning, adapting to documented changes, or regenerating artifacts over
  broad downgrades without evidence.

## Performance Regressions

- Define the metric and threshold: latency, throughput, CPU, memory, allocations,
  I/O, query count, bundle size, paint time, or lock contention.
- Reproduce under comparable conditions and collect before/after measurements.
- Profile before optimizing; fix the measured bottleneck, not a guessed one.

## UI Behavior Regressions

- Reproduce the user path and capture visible behavior, console errors, network
  requests, accessibility state, viewport/device details, and hydration/rendering
  differences.
- Inspect event handlers, state updates, async loading, validation messages,
  focus/keyboard behavior, routing, and API contracts.

## Database, Query, and Migration Issues

- Check schema, migrations, constraints, indexes, transaction boundaries,
  isolation, query parameters, type mapping, row counts, nullability, seed data,
  and generated/offline query metadata.
- Use query plans or measured timings for performance claims.
- Do not change schema or data migrations without tests and contract evidence.

## Build, Lint, Type-Check, and Compilation Failures

- Preserve the first relevant diagnostic and file/line span.
- Identify whether the failure is syntax, type contract, missing import/export,
  feature flag, generated artifact, dependency/toolchain, lint policy, formatting,
  or target/platform specific.
- Fix the cause rather than silencing diagnostics. Suppress lints only with the
  repository's approved mechanism and a specific justification.
