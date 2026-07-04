---
name: behavior-driven-development
description: Apply Behavior-Driven Development to software changes. Use when implementing or clarifying user-visible behavior, acceptance criteria, business workflows, Gherkin scenarios, executable specifications, or feature tests before or during implementation.
---

# Behavior-Driven Development

Use BDD to turn user intent into concrete, observable behavior before choosing
implementation details. Treat it as a collaboration and specification practice,
not as a requirement to write `.feature` files for every change.

## When to Use

Use BDD when the work involves:

- User-visible behavior, product rules, workflows, permissions, or outcomes.
- Ambiguous acceptance criteria that need examples before implementation.
- Cross-functional expectations from product, domain experts, QA, support, or
  existing behavior contracts.
- Acceptance, integration, end-to-end, or contract tests that should describe
  behavior in business-readable terms.
- Bug fixes where the failure should be captured as an externally observable
  regression.

Do not force BDD for:

- Trivial documentation edits, formatting-only changes, mechanical renames, or
  dependency bumps with no behavior change.
- Purely technical refactors whose behavior is already well covered.
- Low-level implementation details that are better specified with unit tests.

## Workflow

1. Identify the behavior.
   - Restate the user's request as observable outcomes: who does what, under
     which conditions, and what changes from the user's or system's perspective.
   - Prefer domain language from the request, product docs, tests, and code.
   - Separate behavior from mechanism: describe effects, not classes, tables,
     routes, selectors, or algorithms unless they are part of the public contract.

2. Create examples before implementation when useful.
   - Write a short Given/When/Then sketch even if no `.feature` file is needed.
   - Cover the main success path, important alternatives, and meaningful failure
     cases.
   - Keep scenarios specific and testable; avoid broad statements such as
     "works correctly" or "handles errors".

3. Choose the executable layer.
   - Use acceptance tests for product-level flows.
   - Use integration or contract tests for API, storage, messaging, or boundary
     behavior.
   - Use end-to-end tests only when browser, device, or full-system behavior is
     essential evidence.
   - Use unit tests for small domain rules that do not need business-readable
     acceptance coverage.

4. Implement to satisfy the examples.
   - Let scenarios guide scope; avoid adding behavior that is not described or
     needed.
   - Keep test names, assertions, docs, and user-facing text aligned with the
     behavior vocabulary.
   - Update scenarios when implementation reveals a better business rule, but do
     not weaken them to fit an accidental design.

5. Verify and report.
   - Run the tests that execute the described behavior.
   - State which scenarios or examples are covered and which are deferred.
   - Call out any ambiguity that remains in product or domain expectations.

## Architecture Boundaries

- BDD should stay mechanism-neutral, but architecture affects where examples are
  executed. In Clean, Hexagonal, or Onion designs, drive scenarios through a
  public API, inbound adapter, use case, or application service rather than
  private classes, database rows, or framework internals.
- Load [`hexagonal-architecture`](../hexagonal-architecture/SKILL.md) when
  acceptance behavior must be mapped to ports, adapters, or external actors. Load
  [`clean-architecture`](../clean-architecture/SKILL.md) for use-case,
  interactor, presenter, or interface-adapter boundaries. Load
  [`onion-architecture`](../onion-architecture/SKILL.md) for domain/application
  rings around a protected domain model.
- Do not put ports, repositories, controller names, ORM details, or layer names
  in Given/When/Then steps unless those mechanisms are part of the public
  contract.

## Given/When/Then Thinking

Use this structure to sharpen behavior even outside Gherkin files:

```text
Given <important context or state>
When <the actor performs the meaningful action>
Then <the observable outcome should occur>
And <additional outcome, only when it belongs to the same behavior>
```

Good:

```text
Given a member has an expired invitation
When they try to accept it
Then the system rejects the invitation
And explains that a new invitation is required
```

Poor:

```text
Given the invitation row has expires_at in the past
When the controller calls InvitationService.accept()
Then it returns Error::Expired
```

The poor version may be useful as a unit test note, but it is not a
business-readable behavior specification.

## Scenario Quality Checklist

- The scenario title names the behavior, not the implementation.
- The actor, context, action, and expected outcome are clear.
- Steps are declarative and business-readable.
- Details are specific enough to test but not brittle.
- Every scenario can map to an automated test or a deliberate manual check.
- Scenarios avoid duplicate coverage unless each duplicate protects a distinct
  rule, role, or boundary.

## Common Pitfalls

- Writing UI scripts instead of behavior: avoid clicks, selectors, HTTP status
  codes, and database fields unless those are the contract being specified.
- Hiding assertions in vague wording: every `Then` should be observable.
- Adding ceremony after the fact: if examples did not influence scope or tests,
  BDD was probably unnecessary.
- Over-covering the obvious: one clear scenario is better than many variants
  that do not change the business outcome.
