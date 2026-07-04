# Skill Taxonomy

This repository keeps first-party global agent skills small, focused, and
orthogonal. A skill is reusable operating guidance for a recurring task. It is
not a project diary, changelog, broad philosophy document, or dumping ground for
unloaded templates.

## Domain Model

- **Skill:** A directory under `skills/` with `SKILL.md` frontmatter and focused
  procedural guidance.
- **Trigger:** The frontmatter `description` is routing metadata. It must name the
  task surface and the strongest trigger terms before the skill body is loaded.
- **Instructions:** The body explains what the agent should inspect, decide,
  change, verify, and report.
- **Constraints:** Guardrails that prevent misuse, overreach, unsafe actions, or
  stale evidence.
- **Examples:** Minimal scenarios only when they clarify activation, output shape,
  or a common mistake.
- **Resources:** Optional `references/`, `scripts/`, `templates/`, or `assets/`
  files. First-party resources must be linked from `SKILL.md` and must not
  contain broken local links.
- **Third-party skill:** A local runtime install under `skills/` that is listed
  in `.skill-lock.json` or ignored as a skill directory under `skills/` in
  `.gitignore`.
  `.skill-lock.json` may be absent when no skills are managed through the
  installer lockfile; ignored skill directories are still third-party.
- **Validation:** `tools/skills_manager.py validate` checks metadata, first-party
  local links, reachable resource files, this document's current first-party
  inventory, and explicit required related-skill link rules as warnings.

## Skill Quality Rubric

Use this rubric when creating, editing, splitting, merging, renaming, or deleting
first-party skills. Use the concise
[`skill-review-checklist.md`](skill-review-checklist.md) during review and
handoff.

### Purpose and Activation

- The skill does one coherent job with a durable workflow.
- The `description` front-loads trigger words, file types, tools, domains, and
  task verbs that should load the skill.
- Near-miss exclusions are explicit when adjacent skills could otherwise compete.
- The skill has a clear non-trigger boundary; agents can tell when not to load it.

### Scope and Progressive Disclosure

- `SKILL.md` contains the routing cues, core workflow, safety rules, and final
  evidence expectations needed on most uses.
- Long examples, detailed reference material, templates, compatibility notes, and
  failure-class appendices live in linked support files.
- Support files are loaded only when they help the active task; avoid chained or
  deeply nested references.
- Do not add empty `references/`, `scripts/`, `templates/`, or `assets/` folders.

### Workflow Reliability

- Instructions are operational: inspect, decide, edit, test, review, report.
- Repository evidence beats generic advice. Skills should tell agents to inspect
  local configs, scripts, tests, docs, and existing conventions before changing
  behavior.
- Validation instructions name the strongest relevant checks and when to start
  narrow before broadening.
- Failure, skipped validation, and residual risk reporting must be explicit.

### Safety and Editing Discipline

- Skills must preserve unrelated user changes and avoid broad rewrites unless the
  task explicitly requires them.
- Security-sensitive work must avoid printing secrets and should route to
  `security-review` and `security-review-evidence` where applicable.
- Randomness, IDs, tokens, filenames, and fixtures must distinguish secure
  randomness from deterministic seeded reproducibility.
- Scripts should be deterministic, non-interactive where possible, have clear
  errors, and use dry-run or preview behavior for risky side effects.

### Examples, Counterexamples, and Markdown

- Examples are short, realistic, transferable, and maintained by docs/tests when
  practical.
- Counterexamples are used sparingly to prevent common false activation or bad
  output shapes.
- Markdown headings, lists, links, and code fences are consistent and scannable.
- Avoid vague motivational prose, generic best-practice dumping, duplicated
  policy, and AI-sounding filler.

### Cross-Skill Relationships and Duplication Control

- Split skills when activation conditions differ materially.
- Merge skills when they are mostly duplicate checklists with the same trigger.
- Cross-reference related skills only when the relationship helps routing or
  execution.
- Use [`docs/cross-reference-map.md`](cross-reference-map.md) for compact
  routing matrices and validator-required relationships. Keep validator rules
  explicit and category-based where practical; do not infer requirements from
  arbitrary prose. Keep this taxonomy focused on inventory, boundaries, and
  coverage.
- Keep vendor/tool-specific advice in the narrowest skill that needs it; use
  project-neutral wording elsewhere.
- Retire stale skills instead of preserving compatibility for old names.

### Maintenance Burden

- Prefer concise first-party guidance over large universal skills.
- Add helper scripts only when they materially improve repeatability.
- Update this taxonomy inventory whenever first-party skills change.
- Validate should-trigger and should-not-trigger scenarios mentally, and run the
  repository validator before handoff.

## Taxonomy

| Category | Skills | Boundary |
| --- | --- | --- |
| Skill authoring and governance | `create-agent-skill`, `code-review`, `review-verification-protocol` | Creating, validating, and reviewing durable agent guidance and repository changes. |
| Security review | `threat-modeling`, `security-review`, `security-review-evidence`, `dependency-supply-chain-review` | Security design analysis, implemented-control audits, sanitized evidence handling, and dependency/supply-chain risk for trust-boundary work. |
| Documentation | `documentation-engineering` | Markdown, README, API docs, comments, rustdoc, pydoc/docstrings, examples, and documentation review. |
| API design and contracts | `api-design` | Public/service interface contracts, compatibility, versioning, idempotency, request/response/error envelopes, schema artifacts, and consumer/provider obligations. |
| Observability and operations | `observability-engineering` | Durable logs, metrics, traces, correlation, dashboards, alerts, SLO/SLI signals, runbooks, incident visibility, and telemetry safety. |
| Design methods and architecture | `brainstorming`, `behavior-driven-development`, `clean-architecture`, `domain-driven-design`, `hexagonal-architecture`, `onion-architecture`, `test-driven-development`, `gherkin` | Use the direct method or architecture skill that matches the work; do not load a meta-selection skill for simple changes. |
| Debugging and prevention | `systematic-debugging`, `root-cause-analysis` | Active symptom diagnosis first; postmortem and recurrence prevention after the direct cause is understood. |
| Data, identifiers, and SQL | `random-data-identifiers`, `sql-engineering`, `postgresql-sql-engineering`, `sqlite-sql-engineering` | Randomness/IDs, database-neutral SQL, and engine-specific PostgreSQL/SQLite schema, migration, query, transaction, performance, security, and review guidance. |
| Python engineering | `python-engineering` | Python implementation, review, testing, packaging, dependency management, quality gates, docs, and `uv` workflows. |
| JavaScript and TypeScript engineering | `javascript-typescript-engineering`, `playwright-e2e` | JS/TS implementation/tooling/package workflows and checked-in Playwright E2E tests. |
| Rust engineering | `rust-engineering`, `rust-testing-quality`, `rust-async-web`, `rust-persistence-sql`, `rust-code-review` | Project-neutral Rust implementation, tests and quality gates, async/web/full-stack work, SQLx/SeaQuery/ORM persistence, and Rust review. |
| Language design patterns and anti-patterns | `rust-design-patterns`, `rust-antipatterns`, `python-design-patterns`, `python-antipatterns`, `typescript-javascript-design-patterns`, `typescript-javascript-antipatterns` | Standalone language-specific pattern selection and smell-detection guidance, with routing from the broader language skills. |
| Project workflow tools | `git-commit`, `justfiles`, `context7-docs`, `suggest-lucide-icons` | Narrow operational guidance for commits, Justfiles, current external docs, and verified Lucide icon names. |
| Third-party runtime installs | `agent-browser`, `anti-ai-slop-writing`, `find-skills`, `playwright-cli` | Installed locally for runtime use but ignored or lockfile-owned; do not edit as first-party skills. |

## API and Observability Skill Boundaries

These first-party contracts document boundaries shared by the taxonomy,
cross-reference map, and validator-required related-link rules. The skill files
remain the detailed workflow source of truth.

### `observability-engineering`

Frontmatter description:

```yaml
description: >-
  Observability, telemetry, and production diagnostics guidance. Use when
  designing, adding, reviewing, or testing structured logs, metrics, traces,
  span/context propagation, correlation or request IDs, sampling,
  labels/cardinality, dashboards, alerts, SLO/SLI/error-budget signals,
  OpenTelemetry/Prometheus/Grafana/Datadog-style instrumentation, operational
  runbooks, or incident visibility. Do not use for ordinary language
  implementation, active debugging without durable instrumentation changes,
  security review except telemetry leakage or audit controls, BDD/TDD mechanics,
  or documentation-only edits; load those existing skills instead or alongside
  this skill when their trigger is primary.
```

Boundary rules:

- Owns telemetry semantics, signal quality, labels/cardinality, context
  propagation, dashboards, alerts, SLOs, and operational visibility.
- Use language engineering skills for implementation mechanics in Rust, Python,
  JavaScript, or TypeScript. Add `observability-engineering` only when the task
  needs instrumentation design or signal review, not because code happens to log.
- Use `rust-async-web` for Tokio/Axum/Leptos runtime, handler, task, SSR,
  hydration, and backpressure behavior. Add `observability-engineering` when the
  primary decision is trace/span structure, async context propagation, request
  correlation, metrics, dashboards, or alerts.
- Use SQL skills for schema, query, transaction, index, privilege, RLS, and
  query-plan behavior. Add `observability-engineering` only for database
  telemetry such as slow-query signals, pool metrics, audit-log shape, or alert
  thresholds.
- Use architecture skills when ports/adapters, dependency direction,
  domain/application rings, or system boundaries are the main design question;
  observability should not introduce architecture ceremony by itself.
- Use `security-review` and `security-review-evidence` when telemetry can expose
  secrets, credentials, PII, tenant data, auth/session traces, exploit payloads,
  or when logs/alerts are security controls or report evidence.
- Use BDD/TDD skills when acceptance examples or executable tests drive the work;
  observability owns what must be observable, not the test methodology.
- Use `documentation-engineering` for runbooks, dashboard notes, API docs,
  comments, and examples when the work is documentation-only.
- Use `systematic-debugging` for active failures and `root-cause-analysis` for
  recurrence prevention unless the fix requires durable instrumentation or
  operational signal design.

### `api-design`

Frontmatter description:

```yaml
description: >-
  API design and contract guidance. Use when defining, changing, reviewing, or
  testing service or public interface contracts: HTTP/REST resources,
  RPC/GraphQL operations, webhooks, event/message schemas,
  request/response/error envelopes, pagination/filtering/sorting, idempotency,
  versioning/deprecation/backward compatibility, OpenAPI/AsyncAPI/JSON
  Schema/protobuf artifacts, SDK or CLI public surfaces, or consumer/provider
  compatibility. Do not use for ordinary language/framework implementation,
  Rust handler mechanics, SQL schema/query design, architecture boundary
  selection, security controls, BDD/TDD mechanics, observability
  instrumentation, or documentation-only API references after the contract is
  set; load those existing skills instead or alongside it when their trigger is
  primary.
```

Boundary rules:

- Owns externally visible contract semantics: resource and operation shape,
  request/response/error envelopes, versioning, compatibility, idempotency,
  pagination/filtering/sorting, webhook/event schemas, and machine-readable
  contract artifacts.
- Use language engineering skills for implementation mechanics, type modeling,
  package/tool workflow, generated clients, and tests in a specific language.
- Use `rust-async-web` for Axum extractors, routers, middleware, Leptos server
  functions, Tokio tasks, SSR/hydration, and Rust web runtime concerns. Add
  `api-design` only when the public or service contract itself is being shaped.
- Use SQL skills for database schemas, migrations, constraints, indexes, query
  plans, and data integrity. Database schema design is not API design unless the
  schema is directly published as an external contract.
- Use Clean, Hexagonal, Onion, or DDD skills when dependency direction,
  ports/adapters, domain language, aggregates, or application boundaries are the
  main question. Add `api-design` only for the exposed interface contract.
- Use `security-review` for auth, authorization, scopes, CORS/CSRF/CSP,
  redirects/callbacks, input validation, webhooks/signatures, sensitive data
  exposure, rate limits, abuse controls, or trust-boundary behavior in the API.
- Use BDD/TDD skills for behavior examples, contract tests, regression tests, or
  test-level selection. API design owns the contract; testing skills own the test
  workflow.
- Use `observability-engineering` for API telemetry, audit/event logs, request
  correlation, SLOs, dashboards, and alerting.
- Use `documentation-engineering` for reference docs, examples, changelogs, and
  API prose when the contract has already been decided.

## Cross-Stack Migration and Evolution Guidance

Do not add a migration meta-skill for ordinary evolution work. Route by the
primary compatibility risk, then add only the companion skill needed for evidence:

- **API compatibility:** use `api-design` for public contract semantics,
  versioning, deprecation, compatibility, and client/provider obligations. Add
  language skills for implementation and
  `documentation-engineering` for migration notes after the contract is settled.
- **Database migration safety:** use `sql-engineering` plus the PostgreSQL or
  SQLite skill when engine behavior matters. Add language persistence skills only
  for adapter, transaction, backfill, or generated-query changes.
- **Telemetry migration signals:** use `observability-engineering` for adoption
  metrics, canary signals, SLO/alert changes, rollback thresholds, and evidence
  that old paths can be removed.
- **Rollout and rollback evidence:** keep feature-flag, deploy, and client code in
  the relevant language/workflow skill; use observability for the signals and
  documentation for runbooks or release notes.
- **Architecture seams:** use DDD, Clean, Hexagonal, or Onion only when the
  migration introduces durable bounded contexts, ports/adapters, dependency-rule
  pressure, or compatibility adapters. Avoid architecture ceremony for a simple
  schema or endpoint version change.
- **Client migration notes:** use `documentation-engineering` for migration
  guides, deprecation windows, examples, and changelog prose; add `api-design` or
  a language skill only if the contract or SDK/example code is still changing.

This section is routing guidance only; keep inventory and validator-required
rules in their dedicated sections.

## Third-Party Install Commands

Third-party classification and update operations are separate:

- `just update-third-party` runs the configured installer update command for
  third-party installs.
- `just update-third-party-dry-run` prints that update command without running
  it.
- `just sync-third-party-lock` copies the repository `.skill-lock.json` to
  `~/.agents/.skill-lock.json` for installer compatibility. It does not run the
  update command or update third-party skill directories.

Run `sync-third-party-lock` only when a repository lockfile exists and should be
mirrored for the installer. A missing `.skill-lock.json` is normal when no
lockfile-managed skills are installed; ignored directories under `skills/` still
count as third-party skills.

## Security Skill Boundaries

| Skill | Use For | Do Not Use For |
| --- | --- | --- |
| `threat-modeling` | Design-time security analysis for new or changed trust boundaries, actors, assets, data flows, entry points, abuse cases, mitigations, security acceptance criteria, assumptions, and residual risk. | Ordinary code review, confirmed vulnerability validation, exploit reproduction, or dependency/SBOM/CVE/provenance review. |
| `security-review` | Implemented-control review for auth, authorization, crypto, secrets, sessions, input validation, web controls, file paths, command execution, and other concrete trust-boundary behavior. | Design-only modeling before controls exist, supply-chain-only review, or unverified vulnerability claims without repository evidence. |
| `security-review-evidence` | Sanitized evidence handling for security-sensitive changes and review findings. | Standalone security review, threat modeling, or implementation work without a security evidence/reporting need. |
| `dependency-supply-chain-review` | Dependency, package, binary, registry, manifest, lockfile, SBOM/SCA, CVE/GHSA, provenance, install-script, CI bootstrap, container/base-image, vendored-code, and generated-code supply-chain risk. | Routine package-manager workflow, third-party API documentation lookup, or language-specific dependency implementation with no supply-chain security question. |

## Language and Data Boundaries

| Skill | Use For | Do Not Use For |
| --- | --- | --- |
| `sql-engineering` | Database-neutral SQL reading, writing, refactoring, schema/query review, migrations, transactions, and performance reasoning. | Engine-specific behavior that needs PostgreSQL or SQLite semantics, or language adapter code with no SQL/schema change. |
| `postgresql-sql-engineering` | PostgreSQL schema design, migrations, constraints, indexes, views, transactions, RLS, privileges, JSONB, query plans, maintenance, and database review in any language stack. | Rust SQLx/SeaQuery typing, Python adapter code, SQLite-only behavior, or ORM API usage with no database-native change. |
| `sqlite-sql-engineering` | SQLite schema design, migrations, constraints, indexes, transactions, PRAGMAs, locking, WAL, local/embedded behavior, temporary DB tests, and SQLite query review in any language stack. | PostgreSQL-native features, Rust SQLx/SeaQuery adapter choices, or using SQLite as proof of another database's behavior. |
| `random-data-identifiers` | Random numbers, secure tokens, UUIDs/CUIDs/ULIDs, collision-resistant IDs, deterministic seeded tests, fixtures, simulations, and reproducibility. | Fixed examples with no randomness or database-native ID/index design without generated-value decisions. |
| `python-engineering` | Python source, tests, pyproject.toml, uv.lock, packaging, linting, typing, docstrings, dependency management, and Python review. | Non-Python package managers, database-native schema design, or browser E2E test design. |
| `python-design-patterns` | Python-specific design patterns such as dataclasses, value objects, protocols, context managers, adapters, repositories, factories, and Python expression of Clean/Hexagonal/Onion boundaries. | General Python workflow, package management, or smell-focused anti-pattern review. |
| `python-antipatterns` | Python-specific generated-code and design smells such as mutable defaults, global state, import-time side effects, broad `Any`, broad exceptions, framework/ORM leakage, async blocking, and brittle tests. | Positive pattern selection or ordinary Python workflow. |
| `javascript-typescript-engineering` | JS/TS source, package.json, lockfiles, Bun/Node/Deno workflows, TypeScript, lint/format/test/build scripts, dependencies, workspaces, and JS/TS review. | Checked-in Playwright spec design, Rust/Python/database work, or framework-specific frontend architecture not evidenced by local config. |
| `typescript-javascript-design-patterns` | TypeScript/JavaScript-specific design patterns such as discriminated unions, branded types, runtime validation boundaries, adapter modules, functional core/imperative shell, use-case handlers, async orchestration, and test builders. | Package manager workflows, checked-in Playwright spec design, or smell-focused anti-pattern review. |
| `typescript-javascript-antipatterns` | TypeScript/JavaScript smells such as `any`, unsafe assertions, missing runtime validation, unawaited promises, singleton service bags, import-time side effects, framework/UI leakage, weak randomness, over-mocked tests, and brittle E2E tests. | Positive pattern selection or ordinary JS/TS workflow. |
| `documentation-engineering` | Markdown, README, API docs, code comments, rustdoc, pydoc/docstrings, examples, and documentation review. | Code-only behavior changes with no reader-facing documentation or comment impact. |

### Future Python, TypeScript/JavaScript, and Accessibility Split Triggers

These are not backlog items. Split `python-engineering` or
`javascript-typescript-engineering`, or treat a dedicated accessibility-review
skill as eligible, only after repeated tasks show a durable activation boundary
that would make the broad language or review skill noisy or under-specific:

- **Testing:** recurring work is mostly test strategy, fixtures, runner behavior,
  coverage, flake isolation, or CI lane selection across projects, rather than
  implementation plus its normal tests. Keep checked-in browser E2E work in
  `playwright-e2e`.
- **Accessibility review:** recurring work is mostly WCAG criteria,
  keyboard/focus behavior, ARIA semantics, contrast, screen-reader behavior, or
  axe-style findings across projects, rather than ordinary frontend fixes or
  browser test implementation.
- **Packaging and toolchains:** package metadata, builds, publishing, lockfiles,
  workspaces, dependency resolution, or release automation become version-sensitive
  enough that they can be handled without loading general implementation guidance.
- **Web/API frameworks:** framework routing, middleware, request lifecycles,
  server/client boundaries, SSR, validation adapters, or framework-specific test
  harnesses dominate the task. Keep public contract shape in `api-design` and
  security controls in the security skills.
- **Async and concurrency:** cancellation, backpressure, task lifetimes, queues,
  workers, event loops, shared state, or resource cleanup are the primary risk;
  do not split for routine `await` usage.
- **Anti-pattern review:** create narrower smell-review skills only when one
  repeated review surface has its own evidence rules and false-positive risks.
  Do not split merely to add more examples to the existing anti-pattern skills.

## Rust Skill Boundaries

| Skill | Use For | Do Not Use For |
| --- | --- | --- |
| `rust-engineering` | Core Rust implementation, crate/workspace setup, feature flags, ownership/lifetimes, traits/generics, error design, refactoring, design patterns, common crates, and macros. | Test-runner strategy, SQLx/SeaQuery/database specifics, or framework-specific async/web design except as boundary context. |
| `rust-design-patterns` | Rust-specific pattern and idiom choices such as newtypes, enums, RAII guards, builders, traits as ports, compose-structs, small crates, contained unsafe modules, custom traits for complex bounds, and macros. | Broader Rust workflow, cargo quality gates, persistence-specific work, or smell-focused anti-pattern review. |
| `rust-antipatterns` | Rust-specific generated-code and design smells such as clone-to-satisfy-borrow-checker, reflexive shared mutability, deref polymorphism, crate-root deny-warnings, panic at trust boundaries, async overuse, macro overreach, and framework leakage. | Positive pattern selection or ordinary Rust implementation. |
| `rust-testing-quality` | Rust unit/integration/e2e/property/doctest/compile-fail tests, TDD/BDD loops, `cargo fmt`, `cargo check`, `cargo test`, `cargo test --doc`, `cargo clippy`, and `cargo nextest`. | General debugging without a known failing symptom, or SQLx/database-specific validation beyond naming the needed gate. |
| `rust-async-web` | Tokio, async tasks, cancellation, timeouts, channels, backpressure, shared state, Axum, Leptos, Axum-Leptos, SSR, hydration, and WASM target concerns. | SQL schema/query design or generic Rust refactors with no async/web surface. |
| `rust-persistence-sql` | SQLx queries/macros, SeaQuery builders, SeaORM/Diesel/raw-SQL choices, Rust database adapters, pools, transactions, SQLx offline metadata, SQLite support, dynamic SQL, and persistence boundaries. | Database-native PostgreSQL or SQLite schema/query/index/security review; use the data skills too. |
| `rust-code-review` | Requested reviews of Rust changes and Rust-specific risk triage across the other Rust skills. | Implementation work where the user has not asked for a review, or database-only review without Rust code. |

## Method Selection and Composition

- Use **BDD** when externally observable behavior, workflows, or acceptance
  criteria need concrete examples.
- Use **DDD** when naming, boundaries, invariants, or long-term domain model
  clarity matter.
- Use **Clean Architecture** when concentric policy/detail boundaries, entities,
  use cases/interactors, interface adapters, presenters, dependency direction, or
  framework/database/UI independence shape the implementation.
- Use **Hexagonal Architecture** when ports, adapters, external actors, multiple
  drivers, swappable infrastructure, or headless core testing shape the
  implementation.
- Use **Onion Architecture** when domain/application rings around a protected
  domain model are the clearest framing and infrastructure should stay outside
  those rings.
- Use **TDD** when behavior can be specified and protected with executable tests.
- Use **Gherkin** when formal `.feature` syntax or durable Given/When/Then
  artifacts are useful.
- Use **Brainstorming** only when there are multiple credible paths and tradeoffs
  worth comparing before implementation.
- Use **language design pattern skills** when the main decision is how to express
  a design idiomatically in Rust, Python, or TypeScript/JavaScript.
- Use **language anti-pattern skills** when the task is smell detection, generated
  code cleanup, or review of repeated language-specific failure modes.
- Use **Threat Modeling** before or during significant trust-boundary design to
  map actors, assets, entry points, data flows, abuse cases, mitigations,
  security acceptance criteria, and residual risk.
- Use **Security Review** after controls exist or when validated findings and
  sanitized evidence are required.
- Use **Dependency Supply-Chain Review** when dependency, package, binary,
  registry, lockfile, CI bootstrap, container, provenance, SBOM/SCA, or advisory
  risk is the security question.

Combinations should be proportional:

- **BDD + DDD:** when examples need domain language, invariants, roles, policies,
  or bounded-context distinctions before implementation.
- **DDD + Clean, Hexagonal, or Onion Architecture:** when the domain model needs
  protection from framework, persistence, messaging, SDK, or delivery-mechanism
  leakage. Use Clean wording for use-case/layer responsibilities; use Hexagonal
  wording for port/adapter decisions; use Onion wording for domain/application
  rings.
- **BDD + Clean, Hexagonal, or Onion Architecture:** when behavior examples should
  execute at the system, inbound-adapter, or use-case boundary without exposing
  internals.
- **BDD + TDD:** when acceptance examples should drive executable behavior tests.
- **DDD + TDD:** when domain invariants, state transitions, value objects, or
  policies should be protected with narrow tests.
- **TDD + Clean, Hexagonal, or Onion Architecture:** when use cases or
  application services should be tested with fake or in-memory adapters before
  real infrastructure exists.
- **BDD + DDD + TDD:** when a significant feature has user-visible behavior,
  important domain modeling, and executable tests that should evolve together.
- **Language engineering + design patterns:** when the implementation needs an
  idiomatic expression of a boundary, invariant, state transition, resource
  lifetime, or construction pattern.
- **Language engineering + anti-patterns:** when reviewing generated code,
  smell-heavy refactors, brittle tests, or repeated language-specific mistakes.
- **Threat modeling + BDD/TDD:** when abuse cases and mitigations should become
  user-visible acceptance criteria or executable security regression tests.
- **Threat modeling + security review:** when design-time risks need verification
  against implemented controls before they are reported as findings.
- **Dependency supply-chain review + language/workflow skills:** when manifests,
  lockfiles, package scripts, CI bootstrap, or container changes require both
  ecosystem mechanics and supply-chain trust review.
- **None of these methods:** for formatting-only, docs-only, mechanical renames,
  generated updates, routine dependency bumps with no trust or supply-chain
  question, or obvious one-line fixes with existing coverage.

Prefer one focused practice over several shallow ones. Do not add ceremony when
reading the code, making a small change, and running the relevant check is enough.

## Current First-Party Inventory

| Skill | Purpose And Trigger | Audit Decision |
| --- | --- | --- |
| `api-design` | API contracts for HTTP/REST, RPC/GraphQL, webhooks, events, request/response/error envelopes, pagination/filtering/sorting, idempotency, versioning, schema artifacts, SDK/CLI surfaces, and consumer/provider compatibility. | Add. Provides first-party contract and compatibility guidance while language, data, security, testing, observability, and documentation skills own their primary mechanics. |
| `behavior-driven-development` | Behavior examples, acceptance criteria, workflows, and executable specifications. | Keep. Focused method skill; overlaps with `gherkin` only at the formal syntax boundary. |
| `brainstorming` | Structured option generation for ambiguous engineering choices before implementation. | Keep. Useful only when multiple credible paths exist; non-goals are explicit. |
| `clean-architecture` | Clean Architecture, dependency rule, entities, use cases/interactors, interface adapters, framework/database/UI independence, and Clean vs Hexagonal/Onion/layered tradeoffs. | Add. Splits detailed Clean Architecture guidance from Ports and Adapters while preserving cross-links to avoid duplicate architecture checklists. |
| `code-review` | General repository-local audit and review workflow, severity, and finding format. | Keep. Owns review reporting; specialist skills add narrow lenses. |
| `context7-docs` | Current third-party library, framework, SDK, API, CLI, and tool documentation lookup. | Keep. External-docs skill; does not replace repository inspection. |
| `create-agent-skill` | Creating, updating, validating, and maintaining reusable `SKILL.md` skills. | Keep. Canonical skill-authoring workflow. |
| `dependency-supply-chain-review` | Dependency audits, SBOM/SCA output, CVE/GHSA advisories, package provenance, registries, manifests, lockfiles, install scripts, CI bootstrap dependencies, containers, binaries, and vendored/generated code. | Add. Specializes security review for supply-chain trust surfaces while language skills continue to own package-manager workflow and implementation details. |
| `documentation-engineering` | Concise, accurate Markdown, README, API docs, comments, rustdoc, pydoc/docstrings, examples, and documentation review. | Add. Fills documentation coverage without relying on third-party writing skills. |
| `domain-driven-design` | Domain modeling, bounded contexts, invariants, repositories, services, events, and language. | Keep. Focused on domain boundaries and anti-ceremony guidance. |
| `gherkin` | Writing or editing `.feature` files and durable Given/When/Then artifacts. | Keep. Syntax-focused companion to BDD, with language usage boundaries. |
| `git-commit` | Atomic commits, logical grouping, staged diff review, and commit messages. | Keep. Broad but coherent workflow with explicit authorization guardrails. |
| `hexagonal-architecture` | Ports and Adapters, use cases, application services, dependency inversion, inbound/outbound adapters, and Clean/Onion-style core isolation. | Add. Reusable architecture guidance that complements DDD, BDD, and TDD without making ports/adapters mandatory. |
| `javascript-typescript-engineering` | JS/TS source, TypeScript, package managers, scripts, tests, lint/format/build, dependencies, workspaces, and CLIs. | Rename from `bun-javascript-workflows`. Covers JS/TS broadly while preserving Bun-first guidance when local evidence supports it. |
| `justfiles` | Designing, refactoring, auditing, and validating Justfiles and `just` workflows. | Keep. Long but justified by version-sensitive syntax and safety concerns. |
| `observability-engineering` | Observability, telemetry, production diagnostics, structured logs, metrics, traces, context propagation, correlation/request IDs, dashboards, alerts, SLO/SLI/error-budget signals, runbooks, incident visibility, and telemetry safety. | Add. Provides first-party signal-design and operational-visibility guidance while implementation, security, debugging, testing, and documentation skills keep their primary boundaries. |
| `onion-architecture` | Onion Architecture, domain/application rings, inward dependencies, infrastructure-at-the-edge design, and Clean/Hexagonal/Onion tradeoffs. | Add. Provides direct activation for Onion requests while cross-linking to Clean, Hexagonal, and DDD. |
| `playwright-e2e` | Checked-in Playwright tests, configs, helpers, traces, lanes, and browser-visible behavior. | Keep. Distinct from generic browser automation and lower-level domain tests. |
| `postgresql-sql-engineering` | PostgreSQL schema, migrations, SQL, transactions, indexes, JSONB, RLS, privileges, plans, maintenance, and review. | Keep. Engine-specific data skill; delegates Rust adapter details to `rust-persistence-sql`. |
| `python-antipatterns` | Python generated-code and design smell review for mutable defaults, global state, import-time side effects, broad typing, framework leakage, async blocking, and brittle tests. | Add. Splits smell-focused Python review from positive pattern selection and broad Python workflow. |
| `python-design-patterns` | Python pattern guidance for dataclasses, value objects, protocols, context managers, adapters, repositories, factories, fixtures, and architecture boundaries. | Add. Provides standalone pattern selection while `python-engineering` remains the workflow skill. |
| `python-engineering` | Python code, tests, typing, packaging, dependency management, `uv`, Ruff, ty/mypy/Pyright, docstrings, and review. | Keep. Covers Python broadly while delegating database-native behavior to data skills. |
| `random-data-identifiers` | Secure randomness, UUIDs/CUIDs/ULIDs, generated IDs, test data, seeded reproducibility, and collision review. | Add. Fills cross-language randomness and identifier coverage. |
| `review-verification-protocol` | Evidence gates for review findings and specialist review lenses. | Keep. Hidden support skill required by `code-review`; prevents speculative findings. |
| `root-cause-analysis` | Recurring failures, incidents, regressions, control gaps, and prevention work. | Keep. Clear handoff from active debugging after direct cause is understood. |
| `rust-antipatterns` | Rust generated-code and design smell review for ownership workarounds, reflexive shared mutability, deref polymorphism, deny-warnings misuse, panic boundaries, async overuse, and framework leakage. | Add. Splits smell-focused Rust review from positive pattern selection and broad Rust engineering. |
| `rust-async-web` | Tokio, async tasks, channels, cancellation, Axum, Leptos, Axum-Leptos, SSR, hydration, and WASM. | Keep. Focused runtime/web skill; delegates SQL and cargo lanes. |
| `rust-code-review` | Rust-specific review lens for ownership, APIs, async, persistence, macros, unsafe, and performance. | Keep. Specialist review skill that routes to implementation and data skills. |
| `rust-design-patterns` | Rust pattern and idiom guidance for newtypes, enums, RAII guards, builders, traits as ports, compose-structs, contained unsafe modules, custom traits, and macros. | Add. Provides standalone pattern selection while `rust-engineering` remains the workflow skill. |
| `rust-engineering` | Core Rust implementation, crates, modules, APIs, ownership, traits, errors, features, refactors, common crates, and macros. | Keep. Primary Rust implementation skill; specialist work is delegated. |
| `rust-persistence-sql` | Rust SQLx, SeaQuery, SeaORM/Diesel/raw-SQL choices, pools, transactions, offline metadata, database adapters, dynamic SQL, and persistence boundaries. | Keep. Owns Rust adapter/query-builder choices and delegates database-native design. |
| `rust-testing-quality` | Rust tests, doctests, nextest, Clippy, formatting, cargo checks, TDD/BDD loops, and CI evidence. | Keep. Consolidates cargo quality gates that were too narrow as standalone skills. |
| `security-review` | Security audit workflow for auth, crypto, secrets, sessions, input validation, trust boundaries, web controls, dependency trust, and sanitized reporting. | Add. Provides generic security review coverage and routes to evidence handling. |
| `security-review-evidence` | Sanitized evidence checklist for security-sensitive changes and reviews. | Keep. Hidden support skill for trust-boundary and secret-handling work. |
| `sql-engineering` | Database-neutral SQL reading, writing, refactoring, migrations, constraints, indexes, transactions, advanced queries, performance, and review. | Add. Provides generic SQL coverage before engine-specific specialization. |
| `sqlite-sql-engineering` | SQLite schema, migrations, PRAGMAs, WAL/locking, transactions, temporary DB tests, limitations, and query review. | Keep. Fills database-specific gap without duplicating PostgreSQL or Rust adapter guidance. |
| `suggest-lucide-icons` | Verified Lucide icon name selection for UI concepts and placements. | Keep. Small, focused workflow with concrete verification rules. |
| `systematic-debugging` | Active failures, regressions, crashes, flakes, performance issues, build failures, and evidence-driven fixes. | Keep. Core workflow remains in `SKILL.md`; detailed failure heuristics moved to a reference. |
| `test-driven-development` | Red-Green-Refactor, regression tests, test-level selection, and behavior-first implementation. | Keep. Concise method skill used by language and workflow skills. |
| `threat-modeling` | Threat models, abuse cases, actors, assets, data flows, trust boundaries, attack surface, security requirements, mitigations, assumptions, and residual risk. | Add. Covers design-time security analysis before implemented-control review; concrete vulnerabilities and evidence still route to `security-review` and `security-review-evidence`. |
| `typescript-javascript-antipatterns` | TypeScript/JavaScript generated-code and design smell review for `any`, unsafe assertions, missing runtime validation, unawaited promises, singleton state, framework/UI leakage, and brittle tests. | Add. Splits smell-focused JS/TS review from positive pattern selection and broad JS/TS workflow. |
| `typescript-javascript-design-patterns` | TypeScript/JavaScript pattern guidance for discriminated unions, branded types, runtime validation boundaries, adapter modules, use-case handlers, async orchestration, and test builders. | Add. Provides standalone pattern selection while `javascript-typescript-engineering` remains the workflow skill. |

## Required Coverage Matrix

Coverage status means the current first-party baseline is covered and validated,
not that every future skill domain is exhausted. Add or split future skills only
when repeated tasks show a durable activation boundary that does not fit an
existing skill.

| Required Topic | Covering Skill(s) | Status | Notes |
| --- | --- | --- | --- |
| Code review | `code-review`, `review-verification-protocol`, `rust-code-review` | Baseline complete | Generic review plus Rust-specific review lens and evidence gates. |
| Security review and audit | `threat-modeling`, `security-review`, `security-review-evidence`, `dependency-supply-chain-review`, `code-review`, language/data skills | Baseline complete | Design-time modeling, implemented-control review, supply-chain review, generic audit routing, and sanitized evidence are covered. |
| Threat modeling and security design | `threat-modeling`, `security-review`, `security-review-evidence`, architecture/method/language skills | Baseline complete | Actors, assets, entry points, data flows, trust boundaries, abuse cases, mitigations, security acceptance criteria, residual risk, and handoff to verified review are covered. |
| Dependency and supply-chain review | `dependency-supply-chain-review`, `security-review`, `security-review-evidence`, language/workflow skills | Baseline complete | Manifests, lockfiles, SBOM/SCA/CVE/GHSA advisories, provenance, registries, install scripts, CI bootstrap, containers, binaries, vendored/generated code, and sanitized evidence are covered. |
| BDD | `behavior-driven-development`, `gherkin`, `playwright-e2e` | Baseline complete | BDD principles and misuse are separate from formal `.feature` syntax. |
| DDD | `domain-driven-design`, language/data skills | Baseline complete | Strategic and tactical patterns with anti-ceremony guidance. |
| Clean / Hexagonal Architecture / Onion / Ports and Adapters | `clean-architecture`, `hexagonal-architecture`, `onion-architecture`, `domain-driven-design`, language/data skills | Baseline complete | Core isolation, dependency direction, entities, use cases/interactors, domain/application rings, interface adapters, ports/adapters, tests, tradeoffs, and when not to add indirection. |
| TDD | `test-driven-development`, language/test skills | Baseline complete | Red/green/refactor, test levels, regression, and misuse guidance. |
| Combining BDD, DDD, TDD, Clean Architecture, Hexagonal Architecture, and Onion Architecture | This taxonomy plus BDD/DDD/TDD/Clean/Hexagonal/Onion cross-references | Baseline complete | Composition guidance lives here to avoid a competing meta-skill. |
| Gherkin and `.feature` files | `gherkin`, `behavior-driven-development`, `playwright-e2e` | Baseline complete | Includes Given/When/Then discipline, outlines, anti-patterns, and language usage. |
| Language-specific design patterns and anti-patterns | `rust-design-patterns`, `rust-antipatterns`, `python-design-patterns`, `python-antipatterns`, `typescript-javascript-design-patterns`, `typescript-javascript-antipatterns`, language engineering skills | Baseline complete; known extensions tracked | Pattern selection and smell detection are standalone skills, with short routing rules in each broader language skill. |
| Random data and identifiers | `random-data-identifiers`, `security-review`, language/data skills | Baseline complete | Covers CSPRNG defaults, seeded reproducibility, UUID/CUID/ULID-style choices, tests, and warnings. |
| SQL | `sql-engineering`, `postgresql-sql-engineering`, `sqlite-sql-engineering`, `rust-persistence-sql` | Baseline complete; known extensions tracked | Generic SQL plus engine and Rust adapter specialization. |
| PostgreSQL | `postgresql-sql-engineering`, `sql-engineering`, `rust-persistence-sql` | Baseline complete | JSONB, indexes, plans, constraints, transactions, privileges/RLS, and maintenance. |
| SQLite | `sqlite-sql-engineering`, `sql-engineering`, `rust-persistence-sql` | Baseline complete | PRAGMAs, WAL/locking, one-writer model, migrations, indexes, and limitations. |
| Python | `python-engineering`, `python-design-patterns`, `python-antipatterns`, `documentation-engineering`, data/security skills | Baseline complete; known extensions tracked | `uv`, Ruff, ty/mypy/Pyright, tests, docstrings, review, security, DB delegation, pattern selection, and smell detection. |
| JavaScript and TypeScript | `javascript-typescript-engineering`, `typescript-javascript-design-patterns`, `typescript-javascript-antipatterns`, `playwright-e2e`, `documentation-engineering`, data/security skills | Baseline complete; known extensions tracked | Bun-first when local, Node/pnpm/npm/yarn/Deno, Prettier/ecosystem tooling, pattern selection, smell detection, and browser E2E are covered. |
| Rust | `rust-engineering`, `rust-design-patterns`, `rust-antipatterns`, `rust-testing-quality`, `rust-async-web`, `rust-persistence-sql`, `rust-code-review`, data/security/docs skills | Baseline complete; known extensions tracked | Crates, workspaces, patterns, anti-patterns, macros, async/web, error handling, docs/tests, rand/serde/anyhow/tokio/reqwest, and SQL library choices. |
| Running tests effectively | `test-driven-development`, `rust-testing-quality`, `python-engineering`, `javascript-typescript-engineering`, `playwright-e2e`, `gherkin` | Baseline complete | Unit, integration, doctest/rustdoc, pydoc examples, E2E, behavior, property, regression, selection, and failure interpretation are distributed to the relevant workflow skills. |
| Root cause analysis and systematic debugging | `systematic-debugging`, `root-cause-analysis` | Baseline complete | Reproduction, narrowing, hypotheses, instrumentation, logs/traces, minimal cases, fix validation, and prevention. |
| API design and contracts | `api-design`, language/framework/data/security/testing/docs skills | Baseline complete | First-party API contract guidance covers resource/operation shape, request/response/error envelopes, idempotency, versioning, compatibility, schema artifacts, SDK/CLI surfaces, and consumer/provider obligations while existing skills remain primary for implementation, database behavior, security controls, tests, observability, and docs. |
| Observability and telemetry | `observability-engineering`, language/framework/security/debugging/docs skills | Baseline complete | First-party observability guidance covers logs, metrics, traces, correlation/context propagation, telemetry safety, dashboards, alerts, SLO/SLI/error-budget signals, runbooks, and incident visibility while existing skills remain primary for implementation mechanics, active debugging, security evidence, tests, and documentation-only edits. |
| Justfiles | `justfiles` | Baseline complete | Recipe design, portability, parameters, env vars, docs, composition, safety, idempotence, and validation. |
| Brainstorming and decision support | `brainstorming` | Baseline complete | Divergence, tradeoffs, assumptions, options, and actionable recommendations. |
| Documentation | `documentation-engineering`, `python-engineering`, `rust-testing-quality`, `rust-engineering`, `code-review` | Baseline complete | Markdown, README, API docs, comments, rustdoc, pydoc/docstrings, maintainable examples, and anti-slop prose rules. |

## Retired, Merged, Renamed, Or Third-Party Skills

| Name Or Group | Decision |
| --- | --- |
| `bun-javascript-workflows` | Renamed and broadened to `javascript-typescript-engineering`; Bun remains a first-class path when local evidence shows a Bun-backed project. |
| `cargo-clippy`, `cargo-nextest`, `rustdoc-guidance` | Merged into `rust-testing-quality`; they are quality gates, not independent workflows. |
| Narrow Rust topic skills such as async review, Axum review, Leptos guidance, project setup, refactoring, macros, WASM, and SQLx review | Merged into the five Rust skills so activation is by durable workflow rather than library fragment. |
| Chidori project-specific skills and resources | Not part of the global taxonomy. Reusable project-neutral guidance has already been folded into language, data, and Rust skills; local paths, schema details, architecture, and workflow names remain local. |
| `agent-browser`, `anti-ai-slop-writing`, `find-skills`, `playwright-cli` | Third-party or ignored runtime installs. They may exist under `skills/` locally, but repository-owned audits should not edit them. |

## Acceptance Criteria

```gherkin
Scenario: First-party taxonomy inventory stays current
  Given a first-party skill is added, removed, or renamed
  When repository validation runs
  Then docs/skill-taxonomy.md lists exactly the current first-party skills
  And ignored or lockfile-owned third-party installs are not listed as first-party
```

```gherkin
Scenario: Third-party lock sync stays separate from updates
  Given third-party skills may be ignored under skills/ or listed in .skill-lock.json
  When an operator needs to update third-party skill contents
  Then they run update-third-party or update-third-party-dry-run
  And sync-third-party-lock only copies the repository lockfile to ~/.agents/.skill-lock.json
  And a missing repository lockfile means there are no lockfile-managed skills to sync
```

```gherkin
Scenario: First-party resources are reachable
  Given a first-party skill contains a reference, script, template, or asset
  When repository validation runs
  Then every resource file is reachable from SKILL.md through local Markdown links
  And every local Markdown link resolves to an existing file
```

```gherkin
Scenario: Category-required related links stay explicit
  Given a first-party skill belongs to a taxonomy category with required related links
  When repository validation runs
  Then missing local SKILL.md links to those related skills are emitted as warnings
  And existing hard validation errors are still reported as errors
  And ignored or lockfile-owned third-party skills do not emit these warnings
```

```gherkin
Scenario: Security-sensitive work uses explicit review
  Given a change touches auth, crypto, secrets, sessions, input validation, CORS, CSP, CSRF, OAuth, tokens, file paths, command execution, or dependency trust
  When an agent reviews the change
  Then it loads security-review and security-review-evidence with code-review
  And reports only sanitized, verified findings
```

```gherkin
Scenario: Threat modeling stays separate from verified findings
  Given a change introduces a trust boundary, sensitive-data flow, external integration, upload, webhook, command surface, or tenant/admin distinction
  When an agent models security risk before or during implementation
  Then it loads threat-modeling
  And records actors, assets, entry points, trust boundaries, abuse cases, mitigations, security acceptance criteria, and residual risk
  And hands concrete implemented-control findings to security-review and security-review-evidence before reporting verified vulnerabilities
```

```gherkin
Scenario: Dependency supply-chain review inspects trust signals safely
  Given a change touches dependency manifests, lockfiles, SBOM or SCA output, CVE or GHSA advisories, registries, install scripts, CI bootstrap dependencies, container images, vendored code, generated code, or binaries
  When an agent reviews supply-chain risk
  Then it loads dependency-supply-chain-review with security-review and security-review-evidence
  And inspects provenance, pins, checksums, signatures, dependency-path impact, scripts, and sanitized advisory evidence without running untrusted code first
```

```gherkin
Scenario: Randomness distinguishes security from reproducibility
  Given a change generates IDs, tokens, random test data, fixtures, or simulation inputs
  When the agent chooses randomness guidance
  Then it loads random-data-identifiers
  And uses secure randomness for secrets and IDs or explicit seeded PRNGs for reproducible tests
```

```gherkin
Scenario: JavaScript and TypeScript choose the local workflow
  Given a change touches JS/TS source, package scripts, lockfiles, type checks, linting, formatting, tests, builds, or dependencies
  When the agent chooses workflow guidance
  Then it loads javascript-typescript-engineering
  And does not assume Bun, Node, pnpm, npm, yarn, Deno, React, Vite, ESLint, or Prettier without repository evidence
```

```gherkin
Scenario: Database-neutral SQL escalates to engine-specific guidance
  Given a change touches SQL, schemas, migrations, transactions, indexes, views, functions, triggers, or query performance
  When the target database has PostgreSQL or SQLite-specific behavior
  Then the agent loads sql-engineering plus the matching engine skill
  And validates behavior against the target engine rather than mocks or another database
```
