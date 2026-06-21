---
name: software-design-practice-selection
description: Choose when to apply BDD, DDD, TDD, Gherkin, combinations of them, or none. Use before substantial implementation or planning when deciding the right amount of methodology for behavior changes, domain modeling, tests, acceptance criteria, or software design work.
---

# Software Design Practice Selection

Use this skill to choose the lightest effective combination of BDD, DDD, TDD,
and Gherkin. The goal is better software decisions, not methodology performance.

## Quick Decision Rules

- Use BDD when user-visible behavior, acceptance criteria, or business workflows
  need examples.
- Use DDD when domain language, invariants, bounded contexts, or long-term model
  clarity matter.
- Use TDD when implementation behavior can be specified and protected with tests.
- Use Gherkin when business-readable `.feature` files or formal Given/When/Then
  artifacts are useful.
- Use none when the change is trivial, mechanical, generated, formatting-only,
  documentation-only, or already sufficiently constrained by existing tests.

Prefer one focused practice over three shallow ones.

## When Not to Use Each Practice

Do not use BDD when:

- The change has no meaningful externally visible behavior.
- The behavior is obvious and already covered.
- Scenario writing would be ceremony after the implementation decision is clear.

Do not use DDD when:

- The domain is simple CRUD or not yet understood.
- New abstractions would not protect real rules.
- A small local function or adapter solves the problem cleanly.

Do not use strict TDD when:

- You are doing throwaway exploration or learning an unknown API.
- The change is documentation, formatting, generated output, or a mechanical
  migration with existing coverage.
- A short test-after check is sufficient and more honest.

Do not use Gherkin when:

- Non-engineers will not review the artifact and code-level tests are clearer.
- The scenarios would be UI scripts, implementation checklists, or duplicated
  test cases.
- The repository does not use `.feature` files and lightweight Given/When/Then
  notes are enough.

## Combination Guide

- BDD + TDD: user-visible behavior change with clear acceptance criteria. Write
  examples first, then drive implementation with focused tests.
- DDD + TDD: domain-heavy internal logic. Model the language and invariants, then
  test-drive the rules at the narrowest useful level.
- BDD + DDD: business behavior and bounded contexts need clarification before
  implementation. Use scenarios to expose vocabulary, roles, and rules.
- BDD + DDD + TDD: complex domain feature with business-facing behavior and
  long-term maintainability concerns. Clarify examples, model the domain, then
  implement in tested behavior slices.
- BDD + Gherkin: acceptance examples should be durable, business-readable, and
  likely automated through Cucumber or similar tooling.
- TDD only: a small behavior change, bug fix, parser rule, validator, API edge
  case, or refactor where product-facing examples add no value.
- DDD only: conceptual modeling or boundary refactoring where implementation is
  not happening yet.
- None: trivial documentation edits, formatting-only changes, dependency bumps
  with no behavior change, generated file refreshes, or mechanical renames where
  existing tests already provide sufficient coverage.

## Selection Workflow

1. Classify the work.
   - Is there user-visible behavior?
   - Is there meaningful domain language or an invariant?
   - Is code behavior changing?
   - Will a business-readable artifact be reviewed or reused?

2. Pick the minimum useful set.
   - Add BDD for behavior examples.
   - Add DDD for language, boundaries, and invariants.
   - Add TDD for executable implementation feedback.
   - Add Gherkin only when formal feature syntax is valuable.

3. State the decision briefly.
   - Name selected practices.
   - Name practices intentionally not used and why.
   - Keep the explanation proportional to the task.

4. Revisit only when facts change.
   - If a simple fix uncovers domain ambiguity, add DDD thinking.
   - If a product rule emerges, add BDD examples.
   - If a bug is reproducible, add TDD/regression coverage.
   - If formal acceptance artifacts become useful, add Gherkin.

## Example Decisions

```text
Use BDD + TDD: the checkout flow changes user-visible discount behavior, and the
acceptance examples can drive integration tests.
```

```text
Use DDD + TDD: the pricing engine has non-trivial invariants, but there is no
new user journey or need for business-readable feature files.
```

```text
Use BDD + DDD + TDD: subscription cancellation affects customer-visible states,
domain lifecycle rules, billing invariants, and regression-sensitive code.
```

```text
Use none: this is a formatting-only Markdown change with no behavior or domain
model impact.
```

## Anti-Pattern Checks

- Are you adding a `.feature` file no one will read or run?
- Are you inventing aggregates or repositories without invariants?
- Are you writing tests that only lock down private implementation details?
- Are you skipping a regression test for a bug that is easy to reproduce?
- Are you applying every practice because it exists rather than because the task
  needs it?
