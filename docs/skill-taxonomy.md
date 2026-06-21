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
  local links, and reachable resource files.

## Taxonomy

| Category | Skills | Boundary |
| --- | --- | --- |
| Skill authoring and governance | `create-agent-skill`, `code-review`, `review-verification-protocol`, `security-review-evidence` | Creating, validating, reviewing, and sanitizing durable agent guidance. |
| Design methods | `brainstorming`, `behavior-driven-development`, `domain-driven-design`, `test-driven-development`, `gherkin` | Use the direct method skill that matches the work; do not load a meta-selection skill. |
| Debugging and prevention | `systematic-debugging`, `root-cause-analysis` | Active symptom diagnosis first; postmortem and recurrence prevention after the direct cause is understood. |
| Rust engineering | `rust-engineering`, `rust-testing-quality`, `rust-async-web`, `rust-persistence-sql`, `rust-code-review` | Project-neutral Rust implementation, tests and quality gates, async/web/full-stack work, SQL persistence, and review. |
| Project workflow tools | `git-commit`, `justfiles`, `playwright-e2e`, `context7-docs`, `suggest-lucide-icons` | Narrow operational guidance for common repository workflows and external documentation/icon checks. |
| Third-party runtime installs | `agent-browser`, `anti-ai-slop-writing`, `find-skills`, `playwright-cli` | Installed locally for runtime use but ignored or lockfile-owned; do not edit as first-party skills. |

## Rust Skill Boundaries

| Skill | Use For | Do Not Use For |
| --- | --- | --- |
| `rust-engineering` | Core Rust implementation, crate/workspace setup, feature flags, ownership/lifetimes, traits/generics, error design, refactoring, design patterns, and macros. | Test-runner strategy, SQLx/database specifics, or framework-specific async/web design except as boundary context. |
| `rust-testing-quality` | Rust unit/integration/e2e/property/doctest/compile-fail tests, TDD/BDD loops, `cargo fmt`, `cargo check`, `cargo test`, `cargo test --doc`, `cargo clippy`, and `cargo nextest`. | General debugging without a known failing symptom, or SQLx/database-specific validation beyond naming the needed gate. |
| `rust-async-web` | Tokio, async tasks, cancellation, timeouts, channels, backpressure, shared state, Axum, Leptos, Axum-Leptos, SSR, hydration, and WASM target concerns. | SQL schema/query design or generic Rust refactors with no async/web surface. |
| `rust-persistence-sql` | SQLx, SQL, SQLite, PostgreSQL, migrations, constraints, indexes, views, transactions, query plans, and persistence boundaries. | Non-database Rust tests or web/UI behavior except at persistence adapter boundaries. |
| `rust-code-review` | Requested reviews of Rust changes and Rust-specific risk triage across the other Rust skills. | Implementation work where the user has not asked for a review. |

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

## Inventory Decisions

| Skill | Decision | Rationale |
| --- | --- | --- |
| `behavior-driven-development` | Keep | Clear boundary for behavior examples and acceptance criteria. |
| `brainstorming` | Keep | Useful for ambiguous engineering choices; non-goals are explicit. |
| `cargo-clippy` | Merge into `rust-testing-quality` | Clippy is one Rust quality gate, not a standalone durable workflow. |
| `cargo-nextest` | Merge into `rust-testing-quality` | Nextest belongs with Rust testing strategy, filtering, and reporting. |
| `code-review` | Keep | General review owns finding format and severity; specialist skills add domain lenses. |
| `context7-docs` | Keep | Covers current third-party docs lookup without replacing repo inspection. |
| `create-agent-skill` | Keep | Canonical authoring workflow for new or updated skills. |
| `domain-driven-design` | Keep | Clear domain modeling boundary and anti-ceremony guidance. |
| `gherkin` | Keep | Focused syntax and quality guidance for `.feature` and scenario writing. |
| `git-commit` | Keep | Broad but coherent commit-quality workflow. |
| `justfiles` | Keep | Detailed because Justfile syntax and safety rules are operationally sharp. |
| `playwright-e2e` | Keep | Distinct from browser automation; owns checked-in Playwright tests. |
| `review-verification-protocol` | Keep | Required evidence gate for review findings. |
| `root-cause-analysis` | Keep | Postmortem and recurrence-prevention workflow remains distinct from active debugging. |
| `rust-async-web` | Add | Covers Tokio, Axum, Leptos, Axum-Leptos, SSR/hydration, WASM, and full-stack boundaries. |
| `rust-code-review` | Rewrite | Review now routes to concise Rust workflow skills instead of a large reference library. |
| `rust-engineering` | Add | Covers core Rust implementation, setup, refactoring, design patterns, and macros. |
| `rust-persistence-sql` | Add | Covers SQLx, SQL, SQLite, PostgreSQL, migrations, and persistence review. |
| `rust-testing-quality` | Add | Consolidates Rust testing, Rustdoc tests, Clippy, nextest, and CI evidence. |
| `rustdoc-guidance` | Merge into `rust-testing-quality` | Rustdoc examples and doctests are part of test and API quality workflow. |
| `security-review-evidence` | Keep | Sanitized evidence checklist for security-sensitive changes. |
| `suggest-lucide-icons` | Keep | Focused icon-selection workflow. |
| `systematic-debugging` | Keep | Strong active-failure workflow; clear handoff to RCA. |
| `test-driven-development` | Keep | Concise and directly actionable for behavior/test changes. |

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
  Given a change touches SQLx queries, migrations, PostgreSQL, SQLite, constraints, indexes, transactions, or query plans
  When the agent implements or reviews the work
  Then it loads rust-persistence-sql
  And validates both Rust query types and database behavior
```

```gherkin
Scenario: Rust review uses the specialist lens
  Given an agent reviews Rust code
  When it identifies Rust-specific risk
  Then it loads rust-code-review with code-review and review-verification-protocol
  And reports only verified behavior, contract, safety, performance, or maintainability findings
```

```gherkin
Scenario: First-party resources are reachable
  Given a first-party skill contains a reference, script, template, or asset
  When repository validation runs
  Then every resource file is reachable from SKILL.md through local Markdown links
  And every local Markdown link resolves to an existing file
```
