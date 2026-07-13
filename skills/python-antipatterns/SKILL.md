---
name: python-antipatterns
description: Python anti-pattern detection and correction guidance. Use when reviewing or refactoring generated or hand-written Python for mutable defaults, global state, import-time side effects, broad Any or dict-shaped data, broad exception handling, monkeypatch-heavy tests, Pydantic/ORM/framework leakage, async blocking, resource leaks, dependency sprawl, brittle tests, or architecture boundary violations.
---

# Python Anti-Patterns

Use this skill to find Python designs that make behavior harder to reason about,
test, type-check, secure, or maintain. Verify the concrete risk before labeling
code as an anti-pattern.

## Use When

- Reviewing Python code, tests, CLIs, adapters, frameworks, package changes, or
  generated code for design and maintainability risks.
- A refactor is needed because domain rules, I/O, framework handlers, database
  access, or tests have become tangled.
- Type hints, mocks, fixtures, globals, exceptions, or async behavior look
  suspicious.
- The user asks for Python smells, anti-patterns, cleanup, or idiomatic review.

For positive pattern selection, use
[`python-design-patterns`](../python-design-patterns/SKILL.md). For broader
workflow and tooling, use [`python-engineering`](../python-engineering/SKILL.md).
Read-only smell identification may use this skill independently or with the
review skills below. When fixing Python code, tests, manifests, or tooling, load
[`python-engineering`](../python-engineering/SKILL.md).
For a requested review or audit, also load
[`code-review`](../code-review/SKILL.md) and
[`review-verification-protocol`](../review-verification-protocol/SKILL.md)
before reporting findings.

## Common Anti-Patterns

- **Mutable defaults:** lists, dicts, sets, objects, or clients used as default
  arguments unless intentionally shared and documented.
- **Import-time side effects:** configuration loading, network calls, database
  connections, logging setup, file writes, or environment mutation during import.
- **Global state as architecture:** hidden singletons, module-level registries,
  process-wide clients, caches, or settings that tests and callers cannot
  control.
- **Dict soup and broad `Any`:** important domain shapes move through untyped
  dictionaries, `Any`, string keys, or loose JSON without validation or named
  types.
- **Catch-all exceptions:** broad `except Exception` can swallow errors, lose
  cause, log secrets, or return misleading defaults. Do not claim it swallows
  cancellation merely from that clause: `asyncio.CancelledError` has inherited
  from `BaseException` since Python 3.8. Flag cancellation swallowing only when
  the concrete caught hierarchy or framework behavior actually catches it.
- **Framework leakage:** request, response, ORM, serializer, Pydantic, Click,
  FastAPI, Django, SDK, or database row types become core domain APIs without an
  intentional boundary.
- **Anemic domain services:** all decisions live in handlers or service classes
  while domain types only carry data.
- **Mocking the behavior under test:** tests replace the domain logic instead of
  external boundaries.
- **Monkeypatch sprawl:** tests patch many internals because dependencies are not
  explicit at module or constructor boundaries.
- **Blocking async code:** synchronous file, sleep, database, or network calls run
  inside the event loop without an explicit boundary.
- **Dependency sprawl:** packages are added for trivial standard-library
  behavior or one-off scripts.

## Architecture And Method Smells

- Clean, Hexagonal, or Onion layers are named but framework or database types
  still flow inward.
- Repositories are generic CRUD wrappers with no domain language or persistence
  boundary.
- BDD scenarios describe routes, selectors, tables, or mocks instead of
  observable behavior.
- TDD tests assert private call order or patch details rather than behavior and
  outcomes.
- DDD names are added before the domain language or invariants are known.

## Refactoring Prompts

- Can a dataclass, `TypedDict`, enum, protocol, or value object replace an
  unstructured dict?
- Can an explicit dependency parameter replace a global lookup or monkeypatch?
- Can a context manager or fixture own cleanup?
- Can a specific exception preserve cause and caller context?
- Can a framework/ORM/Pydantic object be mapped at the adapter boundary?
- Can a pure function hold the rule while the handler owns I/O?
- Can the test fake an external dependency instead of mocking domain behavior?

## Reporting Rules

- Do not flag Python code for being dynamic by itself. Show the concrete type,
  test, security, resource, or maintenance risk.
- Respect framework-convention-first projects when the project intentionally
  keeps logic near the framework and the behavior is simple.
- Prefer targeted changes that improve explicitness and tests over broad
  rewrites into layers.
- State which checks would validate the fix: unit tests, integration tests,
  type checks, linting, or framework-specific tests.
