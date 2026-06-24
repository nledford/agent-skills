---
name: domain-driven-design
description: Apply Domain-Driven Design to complex business logic and module boundaries. Use when modeling domains, bounded contexts, aggregates, value objects, repositories, domain services, policies, domain events, ubiquitous language, or refactoring toward clearer domain behavior.
---

# Domain-Driven Design

Use DDD to make important domain behavior explicit, correctly named, and
protected from infrastructure concerns. Apply it where the domain has enough
business meaning to justify modeling; do not turn simple CRUD or unclear ideas
into ceremony prematurely.

## When to Use

Use DDD when the work involves:

- Business rules, invariants, lifecycle transitions, policies, permissions, or
  workflows that need durable names.
- Multiple concepts that are easy to confuse without a shared vocabulary.
- Internal logic whose correctness matters beyond a single endpoint, UI screen,
  job, or database query.
- Refactoring modules so domain behavior is easier to test and maintain.
- Breaking changes that improve domain clarity and the project does not require
  backwards compatibility.

Avoid heavy DDD when:

- The change is a simple adapter, presentation tweak, migration, or one-off
  script with little domain behavior.
- The domain language is not yet known; start with simple code and preserve
  refactoring room.
- Introducing aggregates, repositories, or events would create abstractions with
  no current rule to protect.

## Workflow

1. Discover the language.
   - Extract nouns, verbs, states, roles, and constraints from the user request,
     existing tests, docs, logs, UI copy, APIs, and database names.
   - Prefer terms used by domain experts and product behavior over technical
     convenience names.
   - Record ambiguities as questions or assumptions before encoding them.

2. Find the boundaries.
   - Identify the domain and subdomains involved.
   - Look for bounded contexts where the same word means different things or
     where rules change by workflow, team, product area, or integration.
   - Keep context boundaries visible in module names, APIs, tests, and docs when
     they affect maintainability.

3. Choose tactical patterns only where they earn their keep.
   - Entity: has identity and continuity across changes.
   - Value object: immutable descriptive value whose equality is by value.
   - Aggregate: consistency boundary that protects invariants through one root.
   - Repository: collection-like access to aggregates, hiding persistence shape.
   - Domain service: stateless domain operation that does not belong on one
     entity or value object.
   - Policy/specification: named decision rule that may vary independently.
   - Domain event: fact that something meaningful already happened in the
     domain.

4. Separate domain from delivery and storage.
   - Put invariants and decisions in domain types or services, not controllers,
     resolvers, UI components, SQL snippets, serializers, or job handlers.
   - Let infrastructure translate into and out of domain concepts.
   - Keep persistence models separate from domain models when storage shape would
     leak or weaken invariants.
   - Do not let framework types become part of the core domain API unless the
     project intentionally treats them as domain primitives.

5. Preserve behavior through tests.
   - Test invariants, transitions, policies, and domain events at the narrowest
     useful level.
   - Use integration tests for repository mappings and boundary contracts.
   - Prefer behavior names in tests over implementation names.

## Relationship To Hexagonal Architecture

DDD helps define what belongs inside the business-centered core; Hexagonal
Architecture helps keep that core isolated from external mechanisms. Load
[`hexagonal-architecture`](../hexagonal-architecture/SKILL.md) when domain
modeling turns into decisions about application services, use cases, ports,
adapters, dependency direction, or how controllers, databases, queues, SDKs, and
frameworks interact with the model.

- Repositories in DDD are collection-like access to aggregates; in a hexagonal
  design they are usually outbound ports implemented by persistence adapters, not
  generic database helper layers.
- Application services/use cases orchestrate workflows around domain objects;
  they should not absorb invariants that belong on entities, value objects,
  aggregates, or domain services.
- Hexagonal Architecture is optional. Keep simple CRUD, one-off scripts, and
  immature domains simpler until real boundaries, testability needs, or
  infrastructure leakage justify ports and adapters.

## Modeling Guidance

- Make invalid states unrepresentable when the language and type system allow it.
- Name operations after domain actions, not data mutations: prefer
  `accept_invitation` over `update_invitation_status` when acceptance has rules.
- Keep aggregates small; do not load a whole graph just because objects are
  related.
- Use domain events for meaningful facts, not as generic callbacks.
- Let module boundaries follow cohesive behavior, not database tables by
  default.
- Refactor toward clearer bounded contexts incrementally when it improves tests,
  naming, or ownership.

## Ubiquitous Language Checklist

- Domain terms are consistent across code, tests, API names, docs, and UI copy
  where they describe the same concept.
- Different meanings use different names, even if legacy code conflates them.
- Public errors and validation messages explain domain rules in user-relevant
  language.
- New abstractions protect real invariants or decisions.
- Infrastructure names do not replace domain names in core logic.

## Common Pitfalls

- Anemic models: entities that only store data while services or handlers hold
  all domain decisions.
- Pattern cargo culting: repositories, events, factories, or aggregates added
  before there is behavior for them to protect.
- Leaky persistence: database IDs, joins, or ORM constraints dictating domain
  language without a domain reason.
- Over-preserving compatibility: keeping misleading names or boundaries when the
  project allows breaking changes and clarity is worth the migration.
