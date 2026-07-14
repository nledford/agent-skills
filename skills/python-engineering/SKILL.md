---
name: python-engineering
description: Python engineering guidance with uv. Use when adding, changing, reviewing, testing, packaging, linting, formatting, typing, dependency-managing, or refactoring Python code, pyproject.toml, uv.lock, pytest/unittest tests, Python scripts, Python web templates, or Python project workflows. Do not use as the primary skill for smell-focused Python audits; use python-antipatterns. Do not use for checked-in hosted CI/release-provider or Docker/OCI/Compose configuration except the Python commands they invoke; use ci-release-engineering or container-engineering. Use api-design for public service/SDK/CLI contracts, observability-engineering for telemetry/logging signal design, and css-scss-styling for CSS/SCSS/template styling decisions.
---

# Python Engineering

Use this skill for project-neutral Python implementation, review, tests,
packaging, dependency management, and quality gates. Prefer repository recipes
when they encode the supported Python version, `uv` workflow, test services, or
CI policy.

## Use When

- Editing `.py` files, Python package layout, `pyproject.toml`, `uv.lock`,
  requirements files, tests, type-checker config, Ruff config, or build metadata.
- Adding behavior, fixing bugs, refactoring Python modules, reviewing Python
  code, or modernizing package/dependency workflows.
- Working with `uv`, pytest, unittest, Ruff, ty, mypy, Pyright, packaging, or
  Python CLIs.

Do not use this skill for non-Python package managers, browser E2E test design,
or database-native design except where Python code owns the adapter boundary.
Use [`sqlite-sql-engineering`](../sqlite-sql-engineering/SKILL.md) or
[`postgresql-sql-engineering`](../postgresql-sql-engineering/SKILL.md) for
schema, transaction, query-plan, and database-specific behavior. Use
[`css-scss-styling`](../css-scss-styling/SKILL.md) when Python web work changes
stylesheets, template class conventions, static CSS/SCSS assets, responsive
layout, or design tokens.

## Async And Concurrency Handoff

Load the [asyncio concurrency reference](references/asyncio-concurrency.md) only
when queues, workers, task supervision, cancellation, backpressure, retries,
rate limits, ordering, shared state, or recovery after process restart are
primary risks. Routine `await` usage, sequential async I/O, and ordinary async
context-manager use do not need the reference.

For concurrency-heavy work, give every task a supervising owner and bounded
lifetime; bound fan-out and queues; define overload behavior; specify
cancellation, cleanup, timeout, retry, and rate-limit policy; decide whether
failures are fail-fast or reported as partial success; test time-dependent policy
with injected clocks or sleepers; and coordinate scheduling states with explicit
events, queues, or barriers. Use
[`python-design-patterns`](../python-design-patterns/SKILL.md) only for the
task-group, queue, and resource-lifetime pattern; this skill and its reference
own implementation and execution workflow.

Use [`ci-release-engineering`](../ci-release-engineering/SKILL.md) when changing
checked-in hosted workflow or automated release configuration, and
[`container-engineering`](../container-engineering/SKILL.md) when changing
Dockerfile, OCI image, or Compose behavior. Keep Python build, test, packaging,
and executable-generation commands in this skill.

## Workflow

1. Inspect the local project first: `pyproject.toml`, `uv.lock`,
   `.python-version`, `requirements*.txt`, `tox.ini`, `noxfile.py`, CI, README,
   tests, package layout, and existing commands.
   Use local code navigation, direct reads, and search for symbols, references,
   implementations, exact strings, docs, config, logs, fixtures, and generated
   assets; use repository commands for tests, builds, and other validation.
2. Define the behavior before editing. Use TDD for new behavior and regressions;
   use BDD-style examples for externally observable workflows.
3. Keep boundaries clear. Use DDD language where domain rules matter; keep I/O,
   framework, database, and CLI parsing at adapters instead of leaking into core
   domain logic. Load
   [`hexagonal-architecture`](../hexagonal-architecture/SKILL.md) for
   ports/adapters and external actors, [`clean-architecture`](../clean-architecture/SKILL.md)
   for use-case and interface-adapter boundaries, or
   [`onion-architecture`](../onion-architecture/SKILL.md) for domain/application
   rings.
4. Implement small, typed, testable units. Prefer simple functions/classes,
   explicit data models, narrow exceptions, and dependency injection at
   boundaries over global state and broad mocks.
5. Run a narrow feedback loop first, then broaden to the repository's quality
   gate.

## uv And Packaging

- Use `uv` project commands when the repo has `pyproject.toml` and `uv.lock`.
  Use legacy `uv pip ...` only when the project is intentionally
  requirements-driven.
- Keep dependency changes intentional: add runtime dependencies with `uv add`,
  dev/test dependencies with the repo's configured dependency group, and remove
  unused packages with the corresponding `uv remove`.
- Keep lockfiles reproducible. Do not edit `uv.lock` by hand.
- Use `uv run` for project commands so the environment and lockfile are
  respected.
- For distributable packages, ensure `pyproject.toml` has an appropriate
  `[build-system]`, package metadata, and importable package layout before
  relying on builds.

Useful commands:

```sh
uv sync
uv sync --locked
uv lock
uv lock --check
uv add <package>
uv add --dev <package>
uv remove <package>
uv run python -m pytest
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run mypy .
uv run pyright
uv build
```

Adapt type-check and test commands to the tools actually configured. Use `ty`
when the repository has adopted it; otherwise use the configured type checker.

## Python Design Checklist

- Public functions and methods have meaningful parameter and return types.
  Avoid `Any` unless the boundary is genuinely untyped and the reason is clear.
- Use built-in generics and unions (`list[T]`, `dict[K, V]`, `T | None`) when
  supported by the repo's Python version.
- Use dataclasses, `TypedDict`, protocols, enums, or small value objects when
  they clarify data shape or domain invariants.
- Exceptions are specific, preserve cause with `raise ... from exc`, and carry
  enough context for diagnosis without leaking secrets.
- Public docstrings explain caller-relevant behavior, parameters, return values,
  raised exceptions, and examples only when type hints and names are not enough.
- Async code uses non-blocking libraries, awaits coroutines, manages async
  context managers with `async with`, and avoids blocking file/network/sleep
  calls in the event loop.
- Module names and package boundaries follow cohesive behavior, not arbitrary
  utility buckets.
- Avoid mutable defaults, hidden import-time side effects, implicit global
  configuration, broad monkeypatching, and print-based observability in
  application code.

## Pattern Routing

- Load [`python-design-patterns`](../python-design-patterns/SKILL.md) when the
  change needs Python-specific pattern choices: dataclasses, value objects,
  protocols, context managers, factories, adapters, repositories, application
  services, or pytest fixture design.
- Load [`python-antipatterns`](../python-antipatterns/SKILL.md) when reviewing or
  refactoring Python smells: mutable defaults, import-time side effects, global
  state, broad `Any`, broad exceptions, framework/ORM leakage, async blocking,
  monkeypatch-heavy tests, or over-mocking.

## API and Observability Routing

- Load [`api-design`](../api-design/SKILL.md) when Python work defines or changes
  HTTP/RPC/GraphQL/webhook, SDK, CLI, request/response/error, pagination,
  versioning, or generated-client contracts. Keep this skill focused on Python
  implementation, typing, serializers, and tests.
- Load [`observability-engineering`](../observability-engineering/SKILL.md) when
  adding or changing structured logging, metrics, traces, correlation IDs, audit
  events, or production diagnostics.
- For public API docs, examples, or migration guides, load
  [`api-design`](../api-design/SKILL.md) first if the contract is still being
  shaped; otherwise use
  [`documentation-engineering`](../documentation-engineering/SKILL.md).

## Styling Routing

- Load [`css-scss-styling`](../css-scss-styling/SKILL.md) when Django, Flask, or
  other Python web work touches `.css`, `.scss`, `.sass`, static asset paths,
  template class hooks, CSS modules through a frontend build, utility classes,
  responsive layout, or accessibility-related visual states.
- Keep this skill focused on Python routes, templates, packaging, tests, and
  framework configuration. Let the styling skill own CSS-vs-SCSS decisions,
  stylesheet build behavior, cascade/layout maintainability, and migration
  validation.

## Security Review Routing

Load [`security-review`](../security-review/SKILL.md) when Python work touches
implemented auth, sessions, crypto, credentials, secrets or `.env`,
deserialization, template rendering, subprocess or command execution, path
handling, uploads/downloads, or other trust boundaries. Use
[`dependency-supply-chain-review`](../dependency-supply-chain-review/SKILL.md)
for dependency bumps, `uv.lock` or requirements churn, package/install/build
hooks, generated clients, vendored code, registry trust, provenance, or advisory
questions. Use [`threat-modeling`](../threat-modeling/SKILL.md) before or during
new auth flows, request/API boundaries, background jobs, external-service calls,
tenant changes, or sensitive data flows. Pair security-sensitive reviews with
[`security-review-evidence`](../security-review-evidence/SKILL.md) so examples
stay sanitized.

## Testing Guidance

- Unit tests cover pure domain logic, validation, parsing, error mapping, and
  edge cases.
- Integration tests cover filesystems, databases, services, framework wiring,
  subprocesses, and package/CLI behavior.
- Use pytest fixtures for shared setup with explicit cleanup; keep mutable
  fixtures function-scoped unless sharing is intentional and safe.
- Parametrize real behavior variants instead of duplicating similar tests.
- Mock external boundaries, not the domain logic being specified. Patch where
  the symbol is used, use `AsyncMock` for awaited collaborators, and verify
  important calls.
- Async tests must use the configured async test plugin or framework support and
  await all async work.
- Regression tests should fail on the old bug for the expected reason before the
  fix.

## Review Checklist

- Correctness: behavior matches the request, edge cases are handled, exceptions
  are specific, and resource cleanup is reliable.
- Typing and API: type hints describe the contract, optional values are handled,
  public APIs are stable enough, and data shapes are explicit.
- Maintainability: modules have cohesive ownership, names use domain language,
  abstractions remove real duplication, and refactors preserve behavior.
- Performance: hot paths avoid accidental O(n^2) work, repeated I/O, import-time
  cost, unnecessary serialization, and blocking work in async contexts.
- Security: input is validated at trust boundaries, secrets are not logged,
  subprocesses and paths are safe, and dependency changes are reviewed.
- Tests: new behavior has unit or integration coverage at the narrowest useful
  level, and broad mocks do not make tests meaningless.
- Workflow: `pyproject.toml`, lockfiles, format/lint/type/test commands, docs,
  and CI remain synchronized.

## Pydoc and Docstrings

- Use module, class, function, and method docstrings for public APIs, extension
  points, CLIs, and non-obvious behavior. Do not restate obvious names.
- Keep examples deterministic and runnable through the repository's doctest,
  pytest, or documentation lane when one exists.
- Document `Raises` only for exceptions callers can intentionally handle.
- Prefer type hints for ordinary parameter and return shape; use prose for
  semantics, side effects, units, invariants, and security constraints.

## Anti-Patterns

- Running tools outside the project environment and then reporting confidence.
- Replacing domain behavior with mocks.
- Leaking framework, ORM, SDK, request, response, or row types into core domain
  APIs without an intentional adapter boundary.
- Catching `Exception` broadly without a recovery policy and context.
- Adding dependencies for trivial standard-library behavior.
- Treating formatting, linting, type checking, and tests as interchangeable.
- Shipping Python package changes without checking lockfile and build metadata.

## Successful Use

The final handoff states the behavior changed, tests or quality gates run, lock
or packaging changes made, and residual risk if type checks, tests, or builds
could not run.
