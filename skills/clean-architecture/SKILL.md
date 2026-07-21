---
name: clean-architecture
description: Clean Architecture guidance centered on the dependency rule, entities, use cases/interactors, and interface adapters that keep business policy independent from frameworks, databases, and UI. Use when the main design question is how policy flows through use cases and adapter boundaries. Use hexagonal-architecture when named inbound/outbound ports around external actors are the main concern, onion-architecture when explicit concentric domain/application rings are the requested model, and architecture-review for a read-only audit. Do not use for simple CRUD, prototypes, or framework-convention-first apps where added layers reduce clarity.
---

# Clean Architecture

Use Clean Architecture to keep business policy independent from delivery
mechanisms, frameworks, databases, UI, queues, and vendor SDKs. The core idea is
separation of concerns enforced by the dependency rule: source-code dependencies
point inward toward higher-level policy, while outer details adapt to the core.

Clean Architecture is a dependency strategy, not a mandatory folder layout. Apply
it only where business rules, lifetime, testability, or change pressure justify
the ceremony.

## Use When

Recommend or apply Clean Architecture when the work involves:

- Long-lived services or applications where maintainability matters more than
  fastest initial delivery.
- Complex business rules, invariants, workflows, policies, or application use
  cases that should survive framework, UI, database, or vendor changes.
- Multiple delivery mechanisms invoking the same behavior: HTTP, CLI, jobs,
  schedulers, message consumers, server functions, UI actions, or APIs.
- Infrastructure that should be replaceable or testable behind seams: databases,
  ORMs, queues, caches, clocks, ID generators, file systems, cloud SDKs, payment
  providers, email senders, or external services.
- Teams that can tolerate explicit boundaries, mapping, tests per boundary, and
  the learning curve of dependency inversion.

Do not force it for:

- Simple CRUD with little business behavior.
- Prototypes, one-off scripts, throwaway tools, migrations, or small automation.
- Apps where framework conventions are intentionally the architecture.
- Teams or deadlines where extra indirection will slow learning and reduce
  clarity more than it protects future change.
- Features that might grow later but do not yet have real policy, external
  mechanisms, or testability pressure. Leave seams; do not build unused layers.

## Dependency Rule

- Inner policy must not mention outer details: frameworks, controllers, request
  objects, response objects, ORM rows, database clients, SDK models, queues,
  serializer types, or UI components.
- Outer layers depend on inner layers. If control must flow outward, use
  dependency inversion: define the needed boundary in or near the inner policy and
  implement it outward.
- Data crossing inward should be simple and shaped for the inner use case, not a
  framework, persistence, transport, or vendor format.
- The dependency rule matters more than the number or names of layers. Four
  circles are a teaching diagram, not a required package count.

## Typical Responsibilities

- **Entities/domain model:** general business rules, invariants, calculations,
  state transitions, policies, value objects, aggregates, and domain events. They
  should be independent of application workflow and infrastructure details.
- **Use cases/interactors/application services:** application-specific business
  rules. They orchestrate workflows, authorization handoff, transactions,
  entity/domain operations, outbound gateway calls, and result production.
- **Interface adapters:** controllers, presenters, view models, serializers,
  repository/gateway implementations, persistence mappers, API clients, queue
  consumers/producers, and adapters that translate between inner models and outer
  mechanisms.
- **Frameworks, drivers, and infrastructure:** web frameworks, databases, ORMs,
  UI frameworks, message brokers, file systems, cloud services, external SDKs,
  app startup, dependency injection wiring, and glue code.

Names vary by ecosystem. `use case`, `interactor`, `application service`,
`handler`, or `command handler` can all be valid if dependency direction and
responsibility boundaries are clear.

## Workflow

1. **Confirm the cost is justified.** Identify the business policy, expected
   lifetime, change pressure, delivery mechanisms, infrastructure dependencies,
   and tests that need isolation. If these are weak, recommend a simpler design.
2. **Evaluate the existing architecture first.** Inspect modules, dependencies,
   tests, framework conventions, and where business rules currently live. Do not
   recommend a rewrite or terminology change when healthy inward dependencies
   already exist.
3. **Choose the smallest scope.** Apply Clean Architecture at a service, module,
   package, feature area, or bounded context. Do not reorganize the whole
   repository when one core workflow needs protection.
4. **Name the inner policy.** Put enterprise/application business rules in domain
   objects and use cases. Keep controllers, ORM models, serializers, queue
   handlers, and UI components thin translators.
5. **Define boundaries from core needs.** Create input/output boundaries,
   repository interfaces, gateways, presenters, or ports only where the use case
   needs a seam. Do not mirror a framework or SDK API inward.
6. **Map at the edges.** Convert request DTOs, API payloads, database rows,
   persistence models, SDK objects, framework errors, and transport responses at
   adapter boundaries. Keep business decisions out of mapping code.
7. **Wire dependencies at the outside.** Use dependency injection, composition
   roots, factories, or module wiring outside the core. The core should receive
   abstractions or simple functions, not construct infrastructure.
8. **Adopt incrementally.** Move one use case or boundary at a time, protect it
   with tests, and leave stable code alone. Prefer strangling infrastructure leaks
   over broad directory reshuffles.

When implementation begins, load the matching language engineering skill and any
data skill needed for persistence, schema, query, or transaction work.

## Verification And Reporting

Before reporting completion, check the changed behavior and dependency direction
at the affected policy and adapter boundaries, then run broader repository checks
when the change warrants them. Report failures, skipped checks, and residual risk
from unverified wiring, mappings, or dependency leaks.

## Boundary and Data Guidance

- DTOs are boundary messages. They are not domain entities, ORM rows, API models,
  or view models unless the project has deliberately collapsed a boundary.
- Entities should not depend on persistence annotations, framework base classes,
  request/session objects, or database row shapes when those details can change
  independently of policy.
- Use case inputs should express what the use case needs, not the raw HTTP body,
  CLI args, queue payload, or UI form state.
- Use case outputs can be simple result DTOs, domain results, events, or an output
  port/presenter interface. Prefer the simplest shape that preserves inward
  dependencies and keeps presentation policy outside the use case.
- Repository and gateway abstractions should describe domain/application needs:
  `load_order_for_checkout`, `save_invoice`, or `reserve_credit`, not generic
  table-shaped CRUD unless generic CRUD is truly the policy.
- CQRS is optional. Split commands and queries when read and write concerns,
  models, scaling, authorization, or performance differ enough to justify it; do
  not add buses or handlers just to look architectural.

## Testing Guidance

- Test entities and domain services directly for invariants, calculations,
  policies, and state transitions.
- Test use cases with fake or in-memory gateways, repositories, presenters,
  clocks, ID generators, and external-service ports.
- Test interface adapters against their real contracts: HTTP routing and
  serialization, database mappings and constraints, SQL, queue payloads, SDK error
  mapping, dependency-injection wiring, and framework integration.
- Add architecture/dependency tests when the language or tooling can enforce
  inward dependencies cheaply.
- Use end-to-end tests for critical wiring and behavior that narrower tests cannot
  prove; do not make E2E the only protection for business rules.

## Organization Guidance

There is no universal folder structure. Choose a structure that makes dependency
direction and domain intent visible in the target language:

- For small scoped adoption, organize by feature or bounded context first, then by
  inner policy versus adapters inside that scope.
- For ecosystems that favor projects/packages/modules, make compile-time
  dependencies enforce the dependency rule where practical.
- For framework-heavy apps, keep framework entry points at the edge and move only
  policy-heavy behavior behind use cases; do not fight every framework convention
  when the framework is intentionally the product shell.
- Prefer names from the domain and use cases over generic buckets like `helpers`,
  `managers`, or `services` when the code represents business behavior.

## Relationship To Other Architecture Skills

- **Layered architecture:** layered systems often separate UI, business, and data
  access by horizontal layers, but dependencies may point downward into data
  access. Clean Architecture inverts dependencies so business policy does not
  depend on data or framework details.
- **Hexagonal Architecture:** both protect the core with inward dependencies. Load
  [`hexagonal-architecture`](../hexagonal-architecture/SKILL.md) when the main
  decision is ports/adapters around external actors, multiple drivers, swappable
  infrastructure, or running the core headless. Prefer Clean Architecture wording
  when the main decision is concentric policy/detail layers, use-case boundaries,
  interactors, presenters, and interface-adapter responsibilities. Either is fine
  when the current code already has healthy boundaries; do not rename architecture
  for terminology alone.
- **Onion Architecture:** closely related; both place domain/application policy at
  the center and infrastructure outside. Load
  [`onion-architecture`](../onion-architecture/SKILL.md) when the user asks for
  Onion by name or when domain/application rings are the clearest framing. Prefer
  Clean Architecture wording when use cases, interactors, presenters, and
  interface adapters are the clearer responsibilities.
- **DDD:** DDD defines ubiquitous language, bounded contexts, aggregates, value
  objects, repositories, domain services, and invariants. Load
  [`domain-driven-design`](../domain-driven-design/SKILL.md) when the model and
  language need work; use Clean Architecture to protect that model and route use
  cases around it.
- **CQRS:** CQRS can fit inside Clean Architecture when separate command and query
  models solve real complexity. It is not required, and it does not replace the
  dependency rule.

## Agent Guidance

- Before recommending Clean Architecture, ask or infer: expected lifetime,
  business-rule complexity, delivery mechanisms, infrastructure volatility,
  testing pain, team familiarity, and whether the user wants architecture change
  or a local fix.
- Caution against Clean Architecture when the request is simple CRUD, a prototype,
  a framework tutorial, a one-off script, or a small change in an intentionally
  framework-centric app.
- Propose incremental refactors: extract one use case, introduce one boundary,
  isolate one external dependency, or move one business rule out of a controller.
  Avoid big-bang rewrites.
- Explain tradeoffs explicitly: more files, mapping, abstractions, and onboarding
  cost in exchange for clearer policy boundaries, testability, and replaceable
  details.
- Preserve repository conventions. Adapt vocabulary to the codebase instead of
  imposing Clean Architecture names everywhere.

## Common Mistakes

- Treating Clean Architecture as folders named `domain`, `application`,
  `infrastructure`, and `presentation` while dependencies still point outward.
- Adding interfaces for every class without a real boundary, alternate
  implementation, testing seam, or external mechanism to isolate.
- Putting business rules in controllers, ORM models, serializers, UI components,
  queue handlers, database triggers, or framework services by default.
- Letting use cases depend on HTTP, ORM, SQL, queue, session, UI, or SDK types.
- Passing database rows, active records, framework request objects, or external
  API payloads inward as if they were domain types.
- Confusing DTOs, entities, persistence models, API models, and view models.
- Creating an anemic domain model when rich domain behavior would protect
  invariants better.
- Applying the pattern uniformly across every feature regardless of complexity.

## Successful Use

The final design names the protected business policy, use cases, entities/domain
objects, boundary interfaces, adapters, mapping points, dependency direction,
tests per boundary, and any deliberate decision to keep a simpler structure.

## Source Anchors

- Robert C. Martin, [The Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html).
- Alistair Cockburn, [Hexagonal architecture](https://alistair.cockburn.us/hexagonal-architecture).
- Jeffrey Palermo, [The Onion Architecture](https://jeffreypalermo.com/2008/07/the-onion-architecture-part-1/).
