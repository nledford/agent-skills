---
name: typescript-javascript-antipatterns
description: TypeScript and JavaScript anti-pattern detection and correction guidance. Use when reviewing or refactoring generated or hand-written JS/TS for any, unsafe assertions, missing runtime validation, unawaited promises, framework or UI leakage, singleton service bags, import-time side effects, Math.random misuse, over-mocked tests, brittle E2E tests, dependency sprawl, or architecture boundary violations.
---

# TypeScript And JavaScript Anti-Patterns

Use this skill to find JS/TS designs that make runtime behavior, tests,
security, type contracts, or architecture boundaries unreliable. Verify the
concrete risk before reporting a smell as a defect.

## Use When

- Reviewing JS/TS source, tests, CLIs, framework handlers, frontend code,
  generated-client usage, package changes, or generated code.
- Runtime behavior contradicts compile-time types or trust-boundary validation is
  missing.
- Async work, imports, globals, mocks, dependency wiring, or framework coupling
  makes behavior hard to reason about.
- The user asks for JS/TS smells, anti-patterns, cleanup, or idiomatic review.

For positive pattern selection, use
[`typescript-javascript-design-patterns`](../typescript-javascript-design-patterns/SKILL.md).
For broader workflow and tooling, use
[`javascript-typescript-engineering`](../javascript-typescript-engineering/SKILL.md).
Read-only smell identification may use this skill independently or with the
review skills below. When fixing JS/TS code, tests, manifests, or tooling, load
[`javascript-typescript-engineering`](../javascript-typescript-engineering/SKILL.md).
For a requested review or audit, also load
[`code-review`](../code-review/SKILL.md) and
[`review-verification-protocol`](../review-verification-protocol/SKILL.md)
before reporting findings.

## Common Anti-Patterns

- **`any` as design escape hatch:** important contracts are erased with `any`,
  `unknown as T`, double assertions, or broad non-null assertions without runtime
  checks.
- **Type-only validation:** JSON, forms, query strings, environment variables,
  local storage, files, plugin data, or network responses enter typed code
  without parsing.
- **Unawaited async work:** promises are started but not awaited, returned,
  cancelled, caught, or intentionally supervised.
- **Detached side effects:** timers, event listeners, subscriptions, workers, or
  background promises have no cleanup or ownership story.
- **Framework leakage:** route, request, response, UI component, hook, ORM,
  generated-client, or SDK types become core domain APIs without an intentional
  adapter boundary.
- **Singleton service bags:** global registries, mutable containers, or hidden
  module state replace explicit dependencies and make tests order-dependent.
- **Import-time side effects:** modules start I/O, read mutable environment,
  register global handlers, connect to services, or mutate runtime state on
  import.
- **Boolean and optional-field state machines:** multiple flags or nullable
  fields represent states that should be discriminated unions.
- **`Math.random()` for IDs or secrets:** weak randomness is used for tokens,
  public IDs, filenames, fixtures that imply security, or collision-sensitive
  values.
- **Dependency sprawl:** packages are added for trivial platform behavior or
  one-off scripts.
- **Over-mocked tests:** tests assert implementation calls while replacing the
  behavior they claim to protect.
- **E2E as unit test substitute:** browser tests cover pure domain rules,
  storage invariants, or parser logic that narrower tests could prove faster.

## Architecture And Method Smells

- Clean, Hexagonal, or Onion boundaries are named but framework, UI, generated
  client, or SDK types still flow inward.
- Interfaces only mirror one concrete object and add no boundary, fake, or
  alternate implementation.
- DDD terminology is applied to data bags without invariants or behavior.
- BDD scenarios describe selectors, implementation routes, mocks, or database
  rows instead of observable outcomes.
- TDD tests freeze private call order or snapshots instead of behavior.

## Refactoring Prompts

- Can `unknown` be parsed into a validated type at the boundary?
- Can a discriminated union replace booleans or mutually exclusive optional
  fields?
- Can a parameter, factory, or composition root replace a singleton or hidden
  import-time dependency?
- Can a framework, generated-client, or SDK type be mapped to an application
  type at the edge?
- Can promise ownership be made explicit with `await`, return, cancellation,
  cleanup, or a supervised task group?
- Can a unit or integration test replace a brittle E2E path?
- Can Web Crypto, Node.js crypto, or a project-standard ID library replace weak
  randomness? Use Bun crypto only when the repository explicitly runs on Bun.

## Reporting Rules

- Do not flag dynamic JavaScript by itself. Tie the issue to runtime validation,
  security, concurrency, testability, type-contract, or architecture risk.
- Respect framework-convention-first code when the behavior is simple and the
  project intentionally keeps logic in framework handlers.
- Prefer narrow fixes: add validation, clarify a union, move one adapter, or
  make one async ownership path explicit.
- State which checks would validate the fix: unit tests, integration tests,
  typecheck, lint, build, or Playwright where browser behavior matters.
