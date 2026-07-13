---
name: python-design-patterns
description: Python design pattern guidance. Use when choosing, implementing, or reviewing idiomatic Python patterns such as dataclasses, value objects, protocols, context managers, dependency injection, adapters, repositories, factories, CLI/service boundaries, async resource handling, pytest fixtures, or Clean/Hexagonal/Onion expression in Python. Use python-antipatterns for smell-focused audits and python-engineering for broader Python workflow.
---

# Python Design Patterns

Use this skill to choose Python patterns that fit the codebase, runtime, and
domain. Prefer simple modules, functions, data types, protocols, and explicit
boundaries over pattern catalogs copied from class-heavy languages.

## Use When

- Python code needs a domain model, adapter boundary, test seam, construction
  pattern, resource-lifetime pattern, or API structure.
- A refactor should make behavior easier to test without real frameworks,
  databases, filesystems, or services.
- Clean, Hexagonal, Onion, DDD, BDD, or TDD guidance needs Python-specific
  expression.
- Review feedback asks for a more idiomatic Python design.

For smell-focused review, use
[`python-antipatterns`](../python-antipatterns/SKILL.md). For package, uv,
typing, test, and command workflow, use
[`python-engineering`](../python-engineering/SKILL.md).

Advice-only pattern choice may use this skill independently. When applying or
implementing a pattern, load
[`python-engineering`](../python-engineering/SKILL.md).

## Selection Rules

1. Inspect local Python version, package layout, tests, framework conventions,
   typing policy, and existing data-model choices.
2. Prefer plain functions and cohesive modules until identity, lifecycle,
   invariants, substitution, or state justify classes or protocols.
3. Use structural typing and dependency injection at real boundaries, not for
   every collaborator.
4. Keep framework, ORM, request, response, serializer, and SDK types at adapters
   unless the project intentionally centers that framework.
5. Test domain rules with ordinary unit tests; test adapters with real framework,
   database, filesystem, or service contracts.

## Patterns To Prefer

- **Dataclasses and frozen dataclasses:** use for explicit data shapes, value
  objects, and immutable domain values. Add validation constructors when invalid
  states matter.
- **Enums and literal types:** use for small closed sets and states where string
  values would otherwise drift.
- **Protocols:** use for outbound ports, plugin surfaces, or collaborators where
  structural substitution matters. Keep protocols small and behavior-oriented.
- **Context managers:** use for resources that need reliable setup and teardown:
  files, locks, transactions, temporary directories, spans, and test fixtures.
- **Factories and constructors:** use factory functions or classmethods when
  creation has validation, defaults, environment lookup, or dependency wiring.
- **Adapter modules:** put HTTP clients, database access, queues, filesystems,
  CLIs, and framework handlers behind boundary modules that translate to domain
  concepts.
- **Repository pattern:** use only when persistence shape should be hidden from
  domain/application policy. Do not create generic CRUD repositories by default.
- **Functional core, imperative shell:** keep parsing, validation, decisions, and
  transformations pure where practical; keep I/O at the edges.
- **Pytest fixtures/builders:** use fixtures for resource setup and builders for
  readable test data, with explicit cleanup and deterministic values.

## Architecture And Methods

- **DDD:** use value objects, entities with identity, domain services, policies,
  and explicit state transitions where they protect real rules.
- **Clean / Hexagonal / Onion:** represent use cases as functions or application
  service classes; use protocols for outbound ports when tests or adapters need
  substitution; keep framework handlers thin.
- **BDD:** express externally observable workflows with domain language before
  choosing pytest, behave, pytest-bdd, or plain test names.
- **TDD:** write focused tests for parsers, validators, policies, state changes,
  and error mapping before wiring broad integrations.

## Review Checklist

- Does the pattern solve a current behavior, boundary, or testing problem?
- Are type hints meaningful without replacing runtime validation at trust
  boundaries?
- Are exceptions specific and preserved with `raise ... from exc` where useful?
- Are resources closed deterministically through context managers, fixtures, or
  framework lifecycle hooks?
- Are framework and persistence models kept out of core domain APIs where that
  boundary matters?
- Are mocks limited to external, slow, nondeterministic, or infrastructure
  boundaries?

## Common Mistakes

- Adding abstract base classes or protocols for one concrete implementation.
- Turning simple functions into manager/service classes with no state or
  boundary.
- Treating Pydantic, ORM, or serializer models as domain objects by default.
- Hiding environment, filesystem, network, or database access in import-time
  side effects.
- Using fixtures or monkeypatching to replace the behavior being specified.
