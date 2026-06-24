---
name: hexagonal-architecture
description: Hexagonal Architecture / Ports and Adapters guidance. Use when designing or refactoring application and domain boundaries, use cases, application services, inbound or outbound ports, adapters, dependency inversion, Clean/Onion-style core isolation, or tests that should run without real infrastructure. Do not use for simple CRUD, prototypes, or one-off scripts where indirection costs more than it protects.
---

# Hexagonal Architecture

Use Hexagonal Architecture, also called Ports and Adapters, to keep business
rules independent from delivery mechanisms and infrastructure. DDD helps define
what belongs inside the business-centered core; Hexagonal Architecture keeps
that core isolated from external mechanisms.

## Use When

Apply this skill when the work involves:

- A complex or long-lived domain with meaningful business rules.
- DDD-style entities, value objects, aggregates, repositories, domain services,
  domain events, bounded contexts, or ubiquitous language.
- Multiple delivery mechanisms such as HTTP APIs, CLIs, jobs, message consumers,
  scheduled tasks, or UI flows invoking the same behavior.
- External systems that should be swappable or testable behind seams: databases,
  ORMs, message brokers, HTTP clients, cloud SDKs, file systems, clocks, ID
  generators, payment gateways, email senders, or vendor APIs.
- Tests that should exercise domain behavior or use cases without real
  infrastructure.
- Refactors where framework, persistence, SDK, or transport types are leaking
  into domain APIs.

Do not force it for:

- Simple CRUD apps with little domain behavior.
- Prototypes, throwaway scripts, short-lived automation, or tiny tools.
- Codebases where framework conventions are intentionally the architecture.
- Features that do not yet justify ports and adapters unless they are likely to
  grow across delivery or infrastructure boundaries.
- Trivial functions where a port would only forward parameters to one concrete
  implementation.

## Dependency Rule

- The domain/application core must not depend directly on frameworks, databases,
  ORMs, message brokers, HTTP clients, cloud SDKs, UI layers, or vendor APIs.
- External systems interact with the core through ports and adapters.
- Ports are contracts at the application boundary. Adapters implement or invoke
  those contracts outside the core.
- Dependency inversion points inward: adapters depend on ports/core, not the
  reverse.
- Keep transport, persistence, SDK, framework, and serialization types out of
  domain model APIs. Map them at adapter boundaries.

## Workflow

1. **Confirm the architecture earns its cost.** Name the business behavior,
   expected lifetime, delivery mechanisms, external dependencies, and testing
   needs. If the change is simple CRUD, keep it simple and leave refactoring
   seams rather than adding unused ports.
2. **Identify the core.** Put business invariants and decisions in domain
   entities, value objects, aggregates, and domain services. Put workflow
   orchestration in application services or use cases.
3. **Define inbound entry points.** Controllers, routes, CLIs, jobs, schedulers,
   message consumers, and UI actions are inbound adapters. They should translate
   input, authorize and validate at the trust boundary, call an application use
   case or inbound port, and map the result to transport output.
4. **Define outbound ports only for real boundaries.** Persistence, messaging,
   external API clients, clocks, ID generators, payment gateways, email senders,
   file systems, and SDK integrations are outbound capabilities. Create a port
   when the core needs the capability but should not know the mechanism.
5. **Implement adapters outside the core.** Database repositories, HTTP clients,
   queue publishers, mailers, filesystem adapters, SDK wrappers, and telemetry
   integrations implement outbound ports. Keep their DTOs, rows, errors,
   retries, transactions, and vendor details at the edge.
6. **Map deliberately.** Convert request/response DTOs, ORM rows, JSON payloads,
   SDK objects, database errors, and framework errors to application/domain
   types at boundaries. Do not let mapping logic smuggle business policy into
   adapters.
7. **Test by boundary.** Test domain behavior directly. Test use cases with fake
   or in-memory outbound adapters. Test adapters against their real framework,
   database, broker, or SDK contract. Add end-to-end tests only for behavior that
   narrower tests cannot prove.

## Layer Responsibilities

- **Domain objects:** enforce invariants, state transitions, calculations,
  policies, and domain events. They should be framework-independent.
- **Application services/use cases:** coordinate a workflow, transaction boundary,
  authorization decision handoff, port calls, and domain operations. They should
  not contain low-level persistence or transport code.
- **Inbound adapters:** HTTP handlers, controllers, CLIs, jobs, schedulers,
  message consumers, UI event bridges, and server functions.
- **Outbound adapters:** repository implementations, database gateways, external
  service clients, queue publishers/producers, email senders, file stores,
  payment clients, clocks, ID generators, cache clients, and cloud SDK wrappers.

## Testing Guidance

- Prefer domain unit tests for invariants and state transitions.
- Use application/use-case tests with fake outbound ports for workflow behavior,
  failure paths, and side effects.
- Use contract tests when multiple adapters must satisfy the same port.
- Use integration tests for real adapters: database mappings, SQL constraints,
  message serialization, HTTP client behavior, SDK error mapping, and framework
  wiring.
- Avoid mocking the domain model. Mock or fake slow, nondeterministic, external,
  or infrastructure boundaries.

## Relationship To Other Design Skills

- **DDD:** DDD defines the model, invariants, repositories, bounded contexts, and
  language inside the core. Hexagonal Architecture protects that model from
  infrastructure leakage.
- **BDD:** BDD scenarios describe behavior at the system or use-case boundary.
  Step definitions should usually drive a public API, inbound adapter, or use
  case rather than internal classes or database rows.
- **TDD:** TDD can drive domain objects and use cases before real infrastructure
  exists by substituting fake adapters for outbound ports.
- **Clean Architecture / Onion Architecture:** these share the inward dependency
  rule and core isolation goal. Do not treat the names as identical blueprints;
  adapt the vocabulary to the repository while preserving dependency direction.

## Anti-Patterns

- Domain objects depend on ORM annotations, framework base classes, SDK models,
  request objects, response objects, or database row shapes when avoidable.
- Controllers, handlers, components, jobs, or step definitions contain business
  rules that belong in domain objects or use cases.
- Repositories or adapters decide business policy instead of translating between
  infrastructure and domain/application contracts.
- Infrastructure errors, transaction handles, query builders, HTTP clients, or
  serialization types leak into core APIs.
- A port is created for every trivial function without a real boundary,
  alternate implementation, testing need, or external mechanism to isolate.
- Domain models are anemic: all behavior lives in services while entities only
  store data.
- Simple CRUD is over-engineered with excessive abstractions before business
  rules, multiple mechanisms, or testability needs justify them.

## Successful Use

The final design names the core behavior, application use cases, inbound
adapters, outbound ports, concrete adapters, mapping points, dependency
direction, tests per boundary, and any deliberate choice to keep a simpler
non-hexagonal structure.
