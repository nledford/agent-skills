---
name: test-driven-development
description: Apply Test-Driven Development to implementation and bug fixes. Use when adding or changing behavior, fixing defects, writing regression tests, choosing test levels, or using Red-Green-Refactor to guide autonomous coding work.
---

# Test-Driven Development

Use TDD to specify behavior with executable tests before relying on an
implementation. Be disciplined when behavior is important, but proportionate:
strict Red-Green-Refactor is not required for every mechanical or exploratory
change.

## When to Use

Use TDD when:

- Adding or changing production behavior.
- Fixing a bug that can be reproduced with a regression test.
- Implementing domain rules, parsers, validation, permissions, state machines,
  or error handling.
- Refactoring risky code where tests can preserve behavior.
- Clarifying an API or contract through examples.

Use lighter test-first or test-after work when:

- Spiking unknown APIs, investigating feasibility, or doing throwaway
  exploration.
- Making documentation-only, formatting-only, generated, or mechanical changes.
- Updating code that is already strongly covered and where a new test would only
  duplicate existing evidence.

## Red-Green-Refactor

1. Red: write the smallest meaningful failing test.
   - Name the behavior being specified.
   - Assert externally relevant outcomes, not private implementation details.
   - For bugs, make the test fail for the observed defect before fixing it.
   - Confirm the failure is for the expected reason when practical.

2. Green: make the test pass with the smallest correct change.
   - Implement only enough behavior to satisfy the current test and nearby
     obvious invariants.
   - Avoid broad refactors while tests are failing.
   - Keep the code understandable; "smallest" does not mean intentionally bad.

3. Refactor: improve design after tests pass.
   - Remove duplication, clarify names, and simplify structure while preserving
     behavior.
   - Run the relevant tests after each meaningful refactor step.
   - Stop when the design is clear enough for the current scope.

Repeat the cycle for each behavior slice.

## Choosing the Test Level

- Unit: pure logic, domain rules, parsing, formatting, validation, edge cases.
- Integration: interactions with databases, filesystems, queues, external
  boundaries, framework wiring, or multiple modules.
- Acceptance: business-readable behavior or product workflows.
- Contract: API, message, schema, plugin, or service-boundary compatibility.
- Regression: a previously observed bug that must not return.
- Property: invariants across many generated inputs.
- End-to-end: user journeys where the full stack or browser behavior is the
  point of confidence.

Prefer the narrowest level that gives trustworthy feedback. Add broader tests
only when narrower tests cannot prove the behavior that matters.

## TDD With Hexagonal Boundaries

Load [`hexagonal-architecture`](../hexagonal-architecture/SKILL.md) when test
design depends on ports, adapters, use cases, or infrastructure-independent
domain behavior.

- Drive domain entities, value objects, aggregates, and domain services with
  narrow unit tests.
- Drive application services or use cases with fake or in-memory outbound
  adapters so workflows can be tested without real databases, brokers, SDKs, or
  clocks.
- Add contract tests when multiple adapters must satisfy the same port.
- Test real adapters with integration tests against the target framework,
  database, filesystem, message broker, or external API contract.
- Avoid over-mocking the core; substitute external boundaries, not the domain
  behavior being specified.

## Test Quality Rules

- Test behavior, not private methods, incidental call order, or internal data
  shapes unless those are the contract.
- Keep tests fast, deterministic, isolated, and readable.
- Avoid excessive mocking; mock slow or external boundaries, not the domain you
  are trying to specify.
- Use realistic fixtures sparingly and keep them understandable.
- Assert meaningful outcomes and important side effects.
- Cover edge cases that encode real rules, not arbitrary permutations.
- Keep test names specific enough to explain the behavior when they fail.

## Completion Rules

Before considering work complete:

- The new or changed tests pass.
- Related existing tests still pass or failures are explained as pre-existing or
  intentionally out of scope.
- Compilation, typechecking, linting, formatting, and other verification failures
  introduced by the change are resolved.
- Temporary debug output, skipped tests, weakened assertions, and test-only hacks
  are removed unless explicitly justified.

Do not claim a fix works because the code looks right; report the verification
that actually ran.

## Common Pitfalls

- Writing a large test after implementation and calling it TDD.
- Over-mocking collaborators so the test proves the mock setup rather than the
  behavior.
- Freezing implementation details that should remain refactorable.
- Refactoring while tests are red and losing the reason for failure.
- Ignoring failing lint, type, build, or unrelated test signals that may indicate
  the change is incomplete.
