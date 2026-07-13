---
name: typescript-javascript-design-patterns
description: TypeScript and JavaScript design pattern guidance. Use when choosing, implementing, or reviewing patterns such as discriminated unions, branded types, schema validation boundaries, functional core/imperative shell, adapter modules, command/use-case handlers, dependency injection, async orchestration, module boundaries, test builders, or Clean/Hexagonal/Onion expression in JS/TS. Use typescript-javascript-antipatterns for smell-focused audits.
---

# TypeScript And JavaScript Design Patterns

Use this skill to choose JS/TS patterns that fit the runtime, package manager,
framework, and domain. TypeScript can describe contracts inside the program, but
untrusted runtime data still needs parsing and validation at boundaries.

## Use When

- JS/TS code needs clearer domain types, module boundaries, adapter boundaries,
  async orchestration, test seams, or API contracts.
- A refactor should separate framework, UI, generated client, persistence, or
  SDK concerns from core behavior.
- Clean, Hexagonal, Onion, DDD, BDD, or TDD guidance needs JS/TS-specific
  expression.
- Review feedback asks for a more idiomatic TypeScript or JavaScript design.

For smell-focused review, use
[`typescript-javascript-antipatterns`](../typescript-javascript-antipatterns/SKILL.md).
For package manager, runtime, lint, type, build, and test workflow, use
[`javascript-typescript-engineering`](../javascript-typescript-engineering/SKILL.md).

Advice-only pattern choice may use this skill independently. When applying or
implementing a pattern, load
[`javascript-typescript-engineering`](../javascript-typescript-engineering/SKILL.md).

## Selection Rules

1. Inspect local evidence first: runtime, package manager, `tsconfig`, framework,
   linter, tests, generated clients, and existing module style.
2. Prefer explicit modules, functions, plain objects, and types before classes or
   dependency containers.
3. Use classes when identity, lifecycle, invariants, polymorphism, or resource
   ownership make them clearer than functions.
4. Validate untrusted input at runtime. Types do not prove JSON, forms, query
   params, environment variables, files, plugin data, or network responses.
5. Keep framework, UI, HTTP, ORM, generated-client, and SDK types at adapters
   when core behavior should be reusable or testable.

## Patterns To Prefer

- **Discriminated unions:** model states, events, commands, results, and
  mutually exclusive variants with exhaustive handling.
- **Branded or opaque types:** distinguish IDs, slugs, emails, tenant IDs, units,
  or validated strings that would otherwise all be plain `string`.
- **Runtime schema validation:** parse untrusted data at boundaries with the
  repository's chosen validator or explicit checks; map validated data inward.
- **Functional core, imperative shell:** keep business rules, reducers, parsers,
  formatters, and decisions pure where practical; keep I/O, clocks, randomness,
  and framework wiring at the edge.
- **Adapter modules:** isolate HTTP clients, database access, queues, files,
  browser APIs, generated clients, and SDKs behind small modules that translate
  to domain/application types.
- **Command or use-case handlers:** use when a workflow coordinates validation,
  authorization handoff, domain logic, persistence, and side effects.
- **Dependency injection through parameters:** pass collaborators explicitly to
  functions, factories, or composition roots before adding containers.
- **Async orchestration helpers:** centralize retries, timeouts, cancellation,
  concurrency limits, and result collection where those policies matter.
- **Test builders and fixtures:** create readable deterministic test data without
  leaking implementation details into every test.

## Architecture And Methods

- **DDD:** use domain names, discriminated unions, value constructors, domain
  events, and explicit state transitions where they protect real rules.
- **Clean / Hexagonal / Onion:** use modules and small interfaces for outbound
  ports only when adapters, fakes, or multiple implementations need them. Keep
  route handlers, components, server functions, and framework actions thin.
- **BDD:** describe browser, CLI, or API workflows in observable terms before
  choosing Playwright, integration tests, or unit tests.
- **TDD:** drive pure logic with fast tests, application workflows with fakes,
  adapters with integration tests, and browser-visible behavior with Playwright
  only when the browser is the confidence target.

## Review Checklist

- Are untrusted inputs parsed before reaching typed core code?
- Do unions and variants cover the meaningful states without boolean flag drift?
- Are async operations awaited, returned, cancelled, or deliberately supervised?
- Are framework and generated-client types mapped at boundaries where reuse or
  testability matters?
- Are mocks limited to external, slow, nondeterministic, or infrastructure
  boundaries?
- Are package/runtime choices based on local evidence rather than defaults?

## Common Mistakes

- Adding class hierarchies or containers when modules and functions are clearer.
- Trusting TypeScript types for runtime data.
- Creating one interface per object with one implementation and no test seam.
- Putting domain decisions in route handlers, UI components, hooks, generated
  clients, or SDK wrappers.
- Overusing E2E tests for rules that unit or integration tests can prove faster.
