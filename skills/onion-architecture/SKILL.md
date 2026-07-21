---
name: onion-architecture
description: Onion Architecture guidance centered on explicit concentric domain, application, and infrastructure rings with dependencies pointing inward. Use when the main design question is ring membership, domain/application separation, or keeping infrastructure at the edge, especially when the project names Onion Architecture. Use hexagonal-architecture when inbound/outbound ports around external actors are primary, clean-architecture for use-case/interactor and interface-adapter policy flow, and architecture-review for a read-only audit. Do not use for simple CRUD, prototypes, or framework-convention-first apps where added layers reduce clarity.
---

# Onion Architecture

Use Onion Architecture to keep the domain model and application policy at the
center of the system while infrastructure, frameworks, persistence, UI, and
external services remain outside. Dependencies point inward; outer layers adapt
to inner policy.

Onion Architecture is a dependency strategy, not a folder naming scheme. Apply it
only where domain rules, lifespan, testability, or infrastructure volatility make
the extra boundaries worth their cost.

## Use When

Apply this skill when the work involves:

- A domain model with meaningful invariants, state transitions, value objects,
  aggregates, policies, or domain services.
- Application services or use cases that should coordinate workflows without
  depending on web, UI, database, queue, or SDK types.
- Persistence or integration details that should not shape domain APIs.
- Multiple delivery mechanisms invoking the same domain behavior.
- Tests that should exercise domain/application behavior without real
  infrastructure.
- A user or codebase explicitly uses Onion Architecture terminology.

Do not force it for:

- Simple CRUD with little domain behavior.
- Prototypes, scripts, migrations, one-off automations, or short-lived tools.
- Codebases where framework conventions are intentionally the architecture.
- Features that do not yet have enough policy, infrastructure volatility, or
  test pressure to justify concentric layers.
- Pass-through repositories, services, or interfaces that only rename one
  framework call.

## Dependency Rule

- Inner layers must not depend on outer layers.
- Domain types must not mention frameworks, ORMs, request/response objects,
  database rows, UI components, queue payloads, SDK models, or transport errors.
- Application services may depend on domain types and inner abstractions for
  needed capabilities.
- Infrastructure implements inner abstractions at the edge.
- Data crossing inward should be shaped for domain/application needs, not copied
  directly from HTTP bodies, database rows, form state, or vendor payloads.

## Typical Rings

Names vary by language and repository. Preserve local vocabulary when the
dependency direction is healthy.

- **Domain model:** entities, value objects, aggregates, domain services,
  policies, invariants, calculations, state transitions, and domain events.
- **Application layer:** use cases, application services, command/query handlers,
  transaction orchestration, authorization handoff, and ports or repository
  abstractions needed by the workflow.
- **Interface adapters:** controllers, presenters, serializers, persistence
  mappers, queue adapters, API clients, and DTO translation.
- **Infrastructure/frameworks:** web frameworks, ORMs, databases, queues, cloud
  SDKs, filesystems, UI frameworks, dependency injection, process startup, and
  configuration wiring.

## Workflow

1. **Confirm the architecture earns its cost.** Identify domain rules, expected
   lifetime, delivery mechanisms, infrastructure dependencies, and testing pain.
   Recommend a simpler design when those pressures are weak.
2. **Inspect the current shape.** Read modules, dependency direction, tests,
   framework conventions, and where domain decisions live. Do not rename a
   healthy architecture for terminology alone.
3. **Choose a small boundary.** Apply Onion Architecture to one bounded context,
   feature area, service, package, or workflow before proposing broad
   reorganization.
4. **Move domain decisions inward.** Put invariants and state changes in domain
   types or domain services, not controllers, ORM models, serializers, jobs, UI
   components, or SQL snippets by default.
5. **Keep application orchestration separate.** Let application services call
   domain behavior, coordinate transactions, invoke ports, and produce results.
   Do not let them absorb rules that belong in the domain model.
6. **Define abstractions from inner needs.** Create repositories, gateways,
   clocks, ID generators, clients, or messaging ports only when application or
   domain policy needs a boundary.
7. **Map at the edge.** Translate request DTOs, database rows, SDK objects,
   framework errors, and transport responses at adapter boundaries.
8. **Wire outside-in.** Construct concrete infrastructure in composition roots,
   dependency-injection wiring, factories, framework setup, or process startup.

When implementation begins, load the matching language engineering skill and any
data skill needed for persistence, schema, query, or transaction work.

## Verification And Reporting

Before reporting completion, check the changed behavior, ring boundaries, and
inward dependencies; then run broader repository checks when the change warrants
them. Report failures, skipped checks, and residual risk from unverified edge
adapters, mappings, or composition wiring.

## Testing Guidance

- Test domain entities, value objects, aggregates, and domain services directly.
- Test application services with fake or in-memory repositories, gateways,
  clocks, ID generators, and external-service ports.
- Test adapters against real framework, database, serialization, queue, or SDK
  contracts.
- Add dependency-direction checks when the language or build system can enforce
  them cheaply.
- Use end-to-end tests for critical wiring only where narrower tests cannot prove
  the behavior.

## Relationship To Other Skills

- **DDD:** Onion Architecture is often a good fit when
  [`domain-driven-design`](../domain-driven-design/SKILL.md) has identified a
  domain model worth protecting. DDD supplies the language and invariants; Onion
  supplies dependency direction around them.
- **Clean Architecture:** Clean and Onion overlap heavily. Load
  [`clean-architecture`](../clean-architecture/SKILL.md) when use cases,
  interactors, presenters, and interface-adapter responsibilities are the clearer
  framing. Prefer Onion when the domain model and concentric domain/application
  rings are the main concern.
- **Hexagonal Architecture:** Load
  [`hexagonal-architecture`](../hexagonal-architecture/SKILL.md) when external
  actors, inbound/outbound ports, adapters, swappable infrastructure, or headless
  core execution dominate the design.
- **BDD:** Use [`behavior-driven-development`](../behavior-driven-development/SKILL.md)
  to describe observable behavior at the public API, use-case, or application
  boundary without exposing private layers.
- **TDD:** Use [`test-driven-development`](../test-driven-development/SKILL.md)
  to drive domain rules and application workflows before real infrastructure
  exists.

## Language Notes

- **Rust:** use crate/module boundaries, visibility, traits, enums, and newtypes
  to make inward dependencies explicit. Keep Tokio, SQLx, Axum, Leptos, and SDK
  types outside the domain model.
- **Python:** use modules, dataclasses, protocols, explicit constructors, and
  thin adapters. Keep Pydantic, ORM, FastAPI, Django, Click, or SDK types at
  boundaries unless the project intentionally treats them as its product shell.
- **JavaScript/TypeScript:** use module boundaries, discriminated unions, runtime
  validation at trust boundaries, and adapter modules. Keep framework, generated
  client, request, response, and UI component types out of core domain APIs.

## Anti-Patterns

- Treating Onion Architecture as folders named `domain`, `application`, and
  `infrastructure` while dependencies still point outward.
- Creating repository or service interfaces for every class without a real
  domain, infrastructure, or testing need.
- Letting ORM entities, active records, DTOs, API payloads, or generated SDK
  types become the domain model by default.
- Placing all behavior in application services while domain entities only store
  data.
- Hiding business policy in mappers, repositories, SQL, controllers, UI
  components, or framework hooks.
- Applying the same layer count to every feature regardless of complexity.

## Successful Use

The final design names the protected domain model, application services, inner
abstractions, adapters, mapping points, dependency direction, tests per boundary,
and any deliberate decision to keep part of the codebase simpler.
