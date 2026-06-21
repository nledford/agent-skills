# Skill Taxonomy

This repository keeps first-party global agent skills small, focused, and
orthogonal. A skill is reusable operating guidance for a recurring task. It is
not a project diary, changelog, broad philosophy document, or dumping ground for
unloaded templates.

## Domain Model

- **Skill:** A directory under `skills/` with `SKILL.md` frontmatter and focused
  procedural guidance.
- **Trigger:** The frontmatter `description` tells the orchestrator when to load
  the skill. It must name the task surface and non-goals when confusion is
  likely.
- **Instructions:** The body explains what the agent should inspect, decide,
  change, verify, and report.
- **Constraints:** Guardrails that prevent misuse, overreach, unsafe actions, or
  stale evidence.
- **Examples:** Minimal scenarios only when they clarify activation or output
  quality.
- **Resources:** Optional `references/`, `scripts/`, `templates/`, or `assets/`
  files. First-party resources must be linked from `SKILL.md` and must not
  contain broken local links.
- **Validation:** `tools/skills_manager.py validate` checks metadata, first-party
  local links, reachable resource files, and this document's current
  first-party inventory.

## Taxonomy

| Category | Skills | Boundary |
| --- | --- | --- |
| Skill authoring and governance | `create-agent-skill`, `code-review`, `review-verification-protocol`, `security-review-evidence` | Creating, validating, reviewing, and sanitizing durable agent guidance. |
| Design methods | `brainstorming`, `behavior-driven-development`, `domain-driven-design`, `test-driven-development`, `gherkin` | Use the direct method skill that matches the work; do not load a meta-selection skill. |
| Debugging and prevention | `systematic-debugging`, `root-cause-analysis` | Active symptom diagnosis first; postmortem and recurrence prevention after the direct cause is understood. |
| Data engineering | `postgresql-sql-engineering`, `sqlite-sql-engineering` | Language-independent PostgreSQL, SQLite, and SQL schema, migration, query, transaction, performance, security, and review guidance. |
| Python engineering | `python-engineering` | Python implementation, review, testing, packaging, dependency management, quality gates, and `uv` workflows. |
| Rust engineering | `rust-engineering`, `rust-testing-quality`, `rust-async-web`, `rust-persistence-sql`, `rust-code-review` | Project-neutral Rust implementation, tests and quality gates, async/web/full-stack work, SQLx/SeaQuery persistence, and review. |
| JavaScript and TypeScript tooling | `bun-javascript-workflows` | Bun-backed JS/TS runtime, package, script, test, workspace, and workflow guidance without assuming a frontend framework. |
| Project workflow tools | `git-commit`, `justfiles`, `playwright-e2e`, `context7-docs`, `suggest-lucide-icons` | Narrow operational guidance for common repository workflows and external documentation/icon checks. |
| Third-party runtime installs | `agent-browser`, `anti-ai-slop-writing`, `find-skills`, `playwright-cli` | Installed locally for runtime use but ignored or lockfile-owned; do not edit as first-party skills. |

## Language And Data Boundaries

| Skill | Use For | Do Not Use For |
| --- | --- | --- |
| `postgresql-sql-engineering` | PostgreSQL/SQL schema design, migrations, constraints, indexes, views, transactions, query writing, query plans, RLS, privileges, performance, and database review in any language stack. | Rust SQLx/SeaQuery typing, Python adapter code, SQLite-only behavior, or ORM API usage with no database-native change. |
| `sqlite-sql-engineering` | SQLite schema design, migrations, constraints, indexes, transactions, PRAGMAs, locking, local/embedded database behavior, temporary database tests, and SQLite query review in any language stack. | PostgreSQL-native features, Rust SQLx/SeaQuery adapter choices, or using SQLite as proof of another database's behavior. |
| `python-engineering` | Python source, tests, packaging, `pyproject.toml`, `uv.lock`, `uv`, Ruff/type/test gates, refactoring, and Python code review. | Non-Python package managers, database-native schema design, or browser E2E test design. |
| `bun-javascript-workflows` | Bun runtime/package/script/test/workspace workflows, `package.json`, `bun.lock`, JS/TS quality gates, and one-off CLIs. | Checked-in Playwright test design, framework-specific frontend architecture, or Rust/Python/database work. |

## Rust Skill Boundaries

| Skill | Use For | Do Not Use For |
| --- | --- | --- |
| `rust-engineering` | Core Rust implementation, crate/workspace setup, feature flags, ownership/lifetimes, traits/generics, error design, refactoring, design patterns, and macros. | Test-runner strategy, SQLx/SeaQuery/database specifics, or framework-specific async/web design except as boundary context. |
| `rust-testing-quality` | Rust unit/integration/e2e/property/doctest/compile-fail tests, TDD/BDD loops, `cargo fmt`, `cargo check`, `cargo test`, `cargo test --doc`, `cargo clippy`, and `cargo nextest`. | General debugging without a known failing symptom, or SQLx/database-specific validation beyond naming the needed gate. |
| `rust-async-web` | Tokio, async tasks, cancellation, timeouts, channels, backpressure, shared state, Axum, Leptos, Axum-Leptos, SSR, hydration, and WASM target concerns. | SQL schema/query design or generic Rust refactors with no async/web surface. |
| `rust-persistence-sql` | SQLx queries/macros, SeaQuery builders, Rust database adapters, pools, transactions, SQLx offline metadata, SQLite support, dynamic SQL construction, and Rust persistence boundaries. | Database-native PostgreSQL or SQLite schema/query/index/security review; use `postgresql-sql-engineering` or `sqlite-sql-engineering`. |
| `rust-code-review` | Requested reviews of Rust changes and Rust-specific risk triage across the other Rust skills. | Implementation work where the user has not asked for a review, or database-only review without Rust code. |

## Method Selection

- Use **BDD** when externally observable behavior, workflows, or acceptance
  criteria need concrete examples.
- Use **DDD** when naming, boundaries, invariants, or long-term domain model
  clarity matter.
- Use **TDD** when implementation behavior can be specified and protected with
  executable tests.
- Use **Gherkin** when formal `.feature` syntax or durable Given/When/Then
  artifacts are useful.
- Use **Brainstorming** only when there are multiple credible paths and tradeoffs
  worth comparing before implementation.

Prefer one focused practice over several shallow ones.

## Current First-Party Inventory

| Skill | Purpose And Trigger | Audit Decision |
| --- | --- | --- |
| `behavior-driven-development` | Behavior examples, acceptance criteria, workflows, and executable specifications. | Keep. Focused method skill; overlaps with `gherkin` only at the formal syntax boundary. |
| `brainstorming` | Structured option generation for ambiguous engineering choices before implementation. | Keep. Useful only when multiple credible paths exist; non-goals are explicit. |
| `bun-javascript-workflows` | Bun runtime, package, script, test, workspace, dependency, and JS/TS workflow guidance. | Keep. Framework-neutral and non-overlapping with checked-in Playwright test design. |
| `code-review` | General repository-local audit and review workflow, severity, and finding format. | Keep. Owns review reporting; specialist skills add narrow lenses. |
| `context7-docs` | Current third-party library, framework, SDK, API, CLI, and tool documentation lookup. | Keep. External-docs skill; does not replace repository inspection. |
| `create-agent-skill` | Creating, updating, validating, and maintaining reusable `SKILL.md` skills. | Keep. Canonical skill-authoring workflow. |
| `domain-driven-design` | Domain modeling, bounded contexts, invariants, repositories, services, events, and language. | Keep. Focused on domain boundaries and anti-ceremony guidance. |
| `gherkin` | Writing or editing `.feature` files and durable Given/When/Then artifacts. | Keep. Syntax-focused companion to BDD, not a replacement for BDD thinking. |
| `git-commit` | Atomic commits, logical grouping, staged diff review, and commit messages. | Keep. Broad but coherent workflow with explicit authorization guardrails. |
| `justfiles` | Designing, refactoring, auditing, and validating Justfiles and `just` workflows. | Keep. Long but justified by version-sensitive syntax and safety concerns. |
| `playwright-e2e` | Checked-in Playwright tests, configs, helpers, traces, lanes, and browser-visible behavior. | Keep. Distinct from generic browser automation and lower-level domain tests. |
| `postgresql-sql-engineering` | PostgreSQL schema, migrations, SQL, transactions, indexes, RLS, privileges, plans, and review. | Keep. Language-independent data skill; delegates Rust adapter details to `rust-persistence-sql`. |
| `python-engineering` | Python code, tests, typing, packaging, dependency management, `uv`, Ruff, and review. | Keep. Covers Python broadly while delegating database-native behavior to data skills. |
| `review-verification-protocol` | Evidence gates for review findings and specialist review lenses. | Keep. Hidden support skill required by `code-review`; prevents speculative findings. |
| `root-cause-analysis` | Recurring failures, incidents, regressions, control gaps, and prevention work. | Keep. Clear handoff from active debugging after direct cause is understood. |
| `rust-async-web` | Tokio, async tasks, channels, cancellation, Axum, Leptos, Axum-Leptos, SSR, hydration, and WASM. | Keep. Focused runtime/web skill; delegates SQL and cargo lanes. |
| `rust-code-review` | Rust-specific review lens for ownership, APIs, async, persistence, macros, unsafe, and performance. | Keep. Specialist review skill that routes to implementation and data skills. |
| `rust-engineering` | Core Rust implementation, crates, modules, APIs, ownership, traits, errors, features, refactors, and macros. | Keep. Primary Rust implementation skill; specialist work is delegated. |
| `rust-persistence-sql` | Rust SQLx, SeaQuery, pools, transactions, offline metadata, database adapters, dynamic SQL, and persistence boundaries. | Keep. Owns Rust adapter/query-builder choices and delegates database-native design. |
| `rust-testing-quality` | Rust tests, doctests, nextest, Clippy, formatting, cargo checks, TDD/BDD loops, and CI evidence. | Keep. Consolidates cargo quality gates that were too narrow as standalone skills. |
| `security-review-evidence` | Sanitized evidence checklist for security-sensitive changes and reviews. | Keep. Hidden support skill for trust-boundary and secret-handling work. |
| `sqlite-sql-engineering` | SQLite schema, migrations, PRAGMAs, transactions, locking, temporary DB tests, and query review. | Keep. Fills database-specific gap without duplicating PostgreSQL or Rust adapter guidance. |
| `suggest-lucide-icons` | Verified Lucide icon name selection for UI concepts and placements. | Keep. Small, focused workflow with concrete verification rules. |
| `systematic-debugging` | Active failures, regressions, crashes, flakes, performance issues, build failures, and evidence-driven fixes. | Keep. Broad but internally consistent; RCA handles recurrence prevention. |
| `test-driven-development` | Red-Green-Refactor, regression tests, test-level selection, and behavior-first implementation. | Keep. Concise method skill used by language and workflow skills. |

## Retired, Merged, Or Third-Party Skills

| Name Or Group | Decision |
| --- | --- |
| `cargo-clippy`, `cargo-nextest`, `rustdoc-guidance` | Merged into `rust-testing-quality`; they are quality gates, not independent workflows. |
| Narrow Rust topic skills such as async review, Axum review, Leptos guidance, project setup, refactoring, macros, WASM, and SQLx review | Merged into the five Rust skills so activation is by durable workflow rather than library fragment. |
| Chidori project-specific skills and resources | Not part of the global taxonomy. Reusable project-neutral guidance has already been folded into Bun, Python, PostgreSQL, and Rust skills; local paths, schema details, architecture, and workflow names remain local. |
| `agent-browser`, `anti-ai-slop-writing`, `find-skills`, `playwright-cli` | Third-party or ignored runtime installs. They may exist under `skills/` locally, but repository-owned audits should not edit them. |

## Acceptance Criteria

```gherkin
Scenario: Core Rust implementation uses the engineering skill
  Given an agent changes crate layout, ownership, traits, errors, features, refactors, or macros
  When it chooses Rust guidance
  Then it loads rust-engineering
  And keeps testing, async/web, and persistence details in their specialist skills
```

```gherkin
Scenario: Rust quality gates are consolidated
  Given an agent writes Rust tests or runs cargo fmt, cargo check, cargo test, cargo test --doc, cargo clippy, or cargo nextest
  When it needs test and validation guidance
  Then it loads rust-testing-quality
  And remembers that nextest does not run doctests
```

```gherkin
Scenario: Async full-stack Rust uses framework-specific boundaries
  Given a change touches Tokio tasks, Axum handlers, Leptos server functions, SSR, hydration, or WASM
  When the agent plans or reviews the work
  Then it loads rust-async-web
  And keeps domain rules testable outside HTTP and UI framework code
```

```gherkin
Scenario: SQL-backed Rust uses persistence guidance
  Given a change touches SQLx queries, SeaQuery builders, Rust database adapters, SQLx metadata, SQLite adapter behavior, dynamic SQL construction, or Rust transaction code
  When the agent implements or reviews the work
  Then it loads rust-persistence-sql
  And validates Rust query types, adapter behavior, and database effects
```

```gherkin
Scenario: Dynamic Rust SQL uses SeaQuery only when justified
  Given a Rust change needs optional filters, sorts, joins, projections, predicates, or multiple SQL dialects
  When explicit static SQL would become unsafe or hard to review
  Then the agent may use SeaQuery through rust-persistence-sql
  And keeps sqlx as the execution, pooling, transaction, migration, or row-mapping layer when the project already uses sqlx
```

```gherkin
Scenario: PostgreSQL design is language-independent
  Given a change touches PostgreSQL tables, constraints, indexes, views, transactions, privileges, RLS, migrations, or query plans
  When the agent chooses specialist guidance
  Then it loads postgresql-sql-engineering
  And keeps Rust SQLx/SeaQuery, Python, or Bun adapter details in their language skills
```

```gherkin
Scenario: SQLite design uses SQLite-specific guidance
  Given a change touches SQLite schema, constraints, indexes, PRAGMAs, locking, migrations, transactions, temporary databases, or SQLite-backed tests
  When the agent chooses specialist guidance
  Then it loads sqlite-sql-engineering
  And does not use SQLite-only evidence to claim PostgreSQL or MySQL behavior
```

```gherkin
Scenario: Python work uses uv-aware engineering guidance
  Given a change touches Python source, tests, pyproject.toml, uv.lock, packaging, linting, typing, or dependency management
  When the agent plans implementation or review
  Then it loads python-engineering
  And verifies behavior with the repo's configured uv, test, lint, format, type, or build lanes
```

```gherkin
Scenario: Bun work stays framework-neutral
  Given a change touches package.json, bun.lock, Bun scripts, Bun tests, JS/TS runtime code, or one-off package CLIs
  When the agent chooses workflow guidance
  Then it loads bun-javascript-workflows
  And does not assume React, Vite, Next.js, Playwright, ESLint, or Prettier unless the repository config shows them
```

```gherkin
Scenario: Chidori extraction remains sanitized
  Given project-specific Chidori skills contain local paths, domain names, schema fragments, pinned versions, exact recipes, or architecture decisions
  When reusable guidance is extracted into global skills
  Then the global skill keeps only project-neutral workflows, checklists, commands, and review criteria
  And no Chidori-specific assumption becomes global policy
```

```gherkin
Scenario: Rust review uses the specialist lens
  Given an agent reviews Rust code
  When it identifies Rust-specific risk
  Then it loads rust-code-review with code-review and review-verification-protocol
  And reports only verified behavior, contract, safety, performance, or maintainability findings
```

```gherkin
Scenario: First-party taxonomy inventory stays current
  Given a first-party skill is added, removed, or renamed
  When repository validation runs
  Then docs/skill-taxonomy.md lists exactly the current first-party skills
  And ignored or lockfile-owned third-party installs are not listed as first-party
```

```gherkin
Scenario: First-party resources are reachable
  Given a first-party skill contains a reference, script, template, or asset
  When repository validation runs
  Then every resource file is reachable from SKILL.md through local Markdown links
  And every local Markdown link resolves to an existing file
```
