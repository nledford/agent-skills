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
- **Validation:** `tools/skills_manager.py validate` checks metadata, first-party
  local links, reachable resource files, and this document's current first-party
  inventory.

## Skill Quality Rubric

Use this rubric when creating, editing, splitting, merging, renaming, or deleting
first-party skills.

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
| Security review | `security-review`, `security-review-evidence` | Security audit workflow and sanitized evidence handling for trust-boundary work. |
| Documentation | `documentation-engineering` | Markdown, README, API docs, comments, rustdoc, pydoc/docstrings, examples, and documentation review. |
| Design methods | `brainstorming`, `behavior-driven-development`, `domain-driven-design`, `test-driven-development`, `gherkin` | Use the direct method skill that matches the work; do not load a meta-selection skill for simple changes. |
| Debugging and prevention | `systematic-debugging`, `root-cause-analysis` | Active symptom diagnosis first; postmortem and recurrence prevention after the direct cause is understood. |
| Data, identifiers, and SQL | `random-data-identifiers`, `sql-engineering`, `postgresql-sql-engineering`, `sqlite-sql-engineering` | Randomness/IDs, database-neutral SQL, and engine-specific PostgreSQL/SQLite schema, migration, query, transaction, performance, security, and review guidance. |
| Python engineering | `python-engineering` | Python implementation, review, testing, packaging, dependency management, quality gates, docs, and `uv` workflows. |
| JavaScript and TypeScript engineering | `javascript-typescript-engineering`, `playwright-e2e` | JS/TS implementation/tooling/package workflows and checked-in Playwright E2E tests. |
| Rust engineering | `rust-engineering`, `rust-testing-quality`, `rust-async-web`, `rust-persistence-sql`, `rust-code-review` | Project-neutral Rust implementation, tests and quality gates, async/web/full-stack work, SQLx/SeaQuery/ORM persistence, and Rust review. |
| Project workflow tools | `git-commit`, `justfiles`, `context7-docs`, `suggest-lucide-icons` | Narrow operational guidance for commits, Justfiles, current external docs, and verified Lucide icon names. |
| Third-party runtime installs | `agent-browser`, `anti-ai-slop-writing`, `find-skills`, `playwright-cli` | Installed locally for runtime use but ignored or lockfile-owned; do not edit as first-party skills. |

## Language and Data Boundaries

| Skill | Use For | Do Not Use For |
| --- | --- | --- |
| `sql-engineering` | Database-neutral SQL reading, writing, refactoring, schema/query review, migrations, transactions, and performance reasoning. | Engine-specific behavior that needs PostgreSQL or SQLite semantics, or language adapter code with no SQL/schema change. |
| `postgresql-sql-engineering` | PostgreSQL schema design, migrations, constraints, indexes, views, transactions, RLS, privileges, JSONB, query plans, maintenance, and database review in any language stack. | Rust SQLx/SeaQuery typing, Python adapter code, SQLite-only behavior, or ORM API usage with no database-native change. |
| `sqlite-sql-engineering` | SQLite schema design, migrations, constraints, indexes, transactions, PRAGMAs, locking, WAL, local/embedded behavior, temporary DB tests, and SQLite query review in any language stack. | PostgreSQL-native features, Rust SQLx/SeaQuery adapter choices, or using SQLite as proof of another database's behavior. |
| `random-data-identifiers` | Random numbers, secure tokens, UUIDs/CUIDs/ULIDs, collision-resistant IDs, deterministic seeded tests, fixtures, simulations, and reproducibility. | Fixed examples with no randomness or database-native ID/index design without generated-value decisions. |
| `python-engineering` | Python source, tests, pyproject.toml, uv.lock, packaging, linting, typing, docstrings, dependency management, and Python review. | Non-Python package managers, database-native schema design, or browser E2E test design. |
| `javascript-typescript-engineering` | JS/TS source, package.json, lockfiles, Bun/Node/Deno workflows, TypeScript, lint/format/test/build scripts, dependencies, workspaces, and JS/TS review. | Checked-in Playwright spec design, Rust/Python/database work, or framework-specific frontend architecture not evidenced by local config. |
| `documentation-engineering` | Markdown, README, API docs, code comments, rustdoc, pydoc/docstrings, examples, and documentation review. | Code-only behavior changes with no reader-facing documentation or comment impact. |

## Rust Skill Boundaries

| Skill | Use For | Do Not Use For |
| --- | --- | --- |
| `rust-engineering` | Core Rust implementation, crate/workspace setup, feature flags, ownership/lifetimes, traits/generics, error design, refactoring, design patterns, common crates, and macros. | Test-runner strategy, SQLx/SeaQuery/database specifics, or framework-specific async/web design except as boundary context. |
| `rust-testing-quality` | Rust unit/integration/e2e/property/doctest/compile-fail tests, TDD/BDD loops, `cargo fmt`, `cargo check`, `cargo test`, `cargo test --doc`, `cargo clippy`, and `cargo nextest`. | General debugging without a known failing symptom, or SQLx/database-specific validation beyond naming the needed gate. |
| `rust-async-web` | Tokio, async tasks, cancellation, timeouts, channels, backpressure, shared state, Axum, Leptos, Axum-Leptos, SSR, hydration, and WASM target concerns. | SQL schema/query design or generic Rust refactors with no async/web surface. |
| `rust-persistence-sql` | SQLx queries/macros, SeaQuery builders, SeaORM/Diesel/raw-SQL choices, Rust database adapters, pools, transactions, SQLx offline metadata, SQLite support, dynamic SQL, and persistence boundaries. | Database-native PostgreSQL or SQLite schema/query/index/security review; use the data skills too. |
| `rust-code-review` | Requested reviews of Rust changes and Rust-specific risk triage across the other Rust skills. | Implementation work where the user has not asked for a review, or database-only review without Rust code. |

## Method Selection and Composition

- Use **BDD** when externally observable behavior, workflows, or acceptance
  criteria need concrete examples.
- Use **DDD** when naming, boundaries, invariants, or long-term domain model
  clarity matter.
- Use **TDD** when behavior can be specified and protected with executable tests.
- Use **Gherkin** when formal `.feature` syntax or durable Given/When/Then
  artifacts are useful.
- Use **Brainstorming** only when there are multiple credible paths and tradeoffs
  worth comparing before implementation.

Combinations should be proportional:

- **BDD + DDD:** when examples need domain language, invariants, roles, policies,
  or bounded-context distinctions before implementation.
- **BDD + TDD:** when acceptance examples should drive executable behavior tests.
- **DDD + TDD:** when domain invariants, state transitions, value objects, or
  policies should be protected with narrow tests.
- **BDD + DDD + TDD:** when a significant feature has user-visible behavior,
  important domain modeling, and executable tests that should evolve together.
- **None of the three:** for formatting-only, docs-only, mechanical renames,
  generated updates, dependency bumps, or obvious one-line fixes with existing
  coverage.

Prefer one focused practice over several shallow ones. Do not add ceremony when
reading the code, making a small change, and running the relevant check is enough.

## Current First-Party Inventory

| Skill | Purpose And Trigger | Audit Decision |
| --- | --- | --- |
| `behavior-driven-development` | Behavior examples, acceptance criteria, workflows, and executable specifications. | Keep. Focused method skill; overlaps with `gherkin` only at the formal syntax boundary. |
| `brainstorming` | Structured option generation for ambiguous engineering choices before implementation. | Keep. Useful only when multiple credible paths exist; non-goals are explicit. |
| `code-review` | General repository-local audit and review workflow, severity, and finding format. | Keep. Owns review reporting; specialist skills add narrow lenses. |
| `context7-docs` | Current third-party library, framework, SDK, API, CLI, and tool documentation lookup. | Keep. External-docs skill; does not replace repository inspection. |
| `create-agent-skill` | Creating, updating, validating, and maintaining reusable `SKILL.md` skills. | Keep. Canonical skill-authoring workflow. |
| `documentation-engineering` | Concise, accurate Markdown, README, API docs, comments, rustdoc, pydoc/docstrings, examples, and documentation review. | Add. Fills documentation coverage without relying on third-party writing skills. |
| `domain-driven-design` | Domain modeling, bounded contexts, invariants, repositories, services, events, and language. | Keep. Focused on domain boundaries and anti-ceremony guidance. |
| `gherkin` | Writing or editing `.feature` files and durable Given/When/Then artifacts. | Keep. Syntax-focused companion to BDD, with language usage boundaries. |
| `git-commit` | Atomic commits, logical grouping, staged diff review, and commit messages. | Keep. Broad but coherent workflow with explicit authorization guardrails. |
| `javascript-typescript-engineering` | JS/TS source, TypeScript, package managers, scripts, tests, lint/format/build, dependencies, workspaces, and CLIs. | Rename from `bun-javascript-workflows`. Covers JS/TS broadly while preserving Bun-first guidance when local evidence supports it. |
| `justfiles` | Designing, refactoring, auditing, and validating Justfiles and `just` workflows. | Keep. Long but justified by version-sensitive syntax and safety concerns. |
| `playwright-e2e` | Checked-in Playwright tests, configs, helpers, traces, lanes, and browser-visible behavior. | Keep. Distinct from generic browser automation and lower-level domain tests. |
| `postgresql-sql-engineering` | PostgreSQL schema, migrations, SQL, transactions, indexes, JSONB, RLS, privileges, plans, maintenance, and review. | Keep. Engine-specific data skill; delegates Rust adapter details to `rust-persistence-sql`. |
| `python-engineering` | Python code, tests, typing, packaging, dependency management, `uv`, Ruff, ty/mypy/Pyright, docstrings, and review. | Keep. Covers Python broadly while delegating database-native behavior to data skills. |
| `random-data-identifiers` | Secure randomness, UUIDs/CUIDs/ULIDs, generated IDs, test data, seeded reproducibility, and collision review. | Add. Fills cross-language randomness and identifier coverage. |
| `review-verification-protocol` | Evidence gates for review findings and specialist review lenses. | Keep. Hidden support skill required by `code-review`; prevents speculative findings. |
| `root-cause-analysis` | Recurring failures, incidents, regressions, control gaps, and prevention work. | Keep. Clear handoff from active debugging after direct cause is understood. |
| `rust-async-web` | Tokio, async tasks, channels, cancellation, Axum, Leptos, Axum-Leptos, SSR, hydration, and WASM. | Keep. Focused runtime/web skill; delegates SQL and cargo lanes. |
| `rust-code-review` | Rust-specific review lens for ownership, APIs, async, persistence, macros, unsafe, and performance. | Keep. Specialist review skill that routes to implementation and data skills. |
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

## Required Coverage Matrix

| Required Topic | Covering Skill(s) | Status | Notes |
| --- | --- | --- | --- |
| Code review | `code-review`, `review-verification-protocol`, `rust-code-review` | Complete | Generic review plus Rust-specific review lens and evidence gates. |
| Security review and audit | `security-review`, `security-review-evidence`, `code-review`, language/data skills | Complete | Generic audit skill covers trust boundaries; support skill controls sanitized evidence. |
| BDD | `behavior-driven-development`, `gherkin`, `playwright-e2e` | Complete | BDD principles and misuse are separate from formal `.feature` syntax. |
| DDD | `domain-driven-design`, language/data skills | Complete | Strategic and tactical patterns with anti-ceremony guidance. |
| TDD | `test-driven-development`, language/test skills | Complete | Red/green/refactor, test levels, regression, and misuse guidance. |
| Combining BDD, DDD, and TDD | This taxonomy plus BDD/DDD/TDD cross-references | Complete | Composition guidance lives here to avoid a competing meta-skill. |
| Gherkin and `.feature` files | `gherkin`, `behavior-driven-development`, `playwright-e2e` | Complete | Includes Given/When/Then discipline, outlines, anti-patterns, and language usage. |
| Random data and identifiers | `random-data-identifiers`, `security-review`, language/data skills | Complete | Covers CSPRNG defaults, seeded reproducibility, UUID/CUID/ULID-style choices, tests, and warnings. |
| SQL | `sql-engineering`, `postgresql-sql-engineering`, `sqlite-sql-engineering`, `rust-persistence-sql` | Complete | Generic SQL plus engine and Rust adapter specialization. |
| PostgreSQL | `postgresql-sql-engineering`, `sql-engineering`, `rust-persistence-sql` | Complete | JSONB, indexes, plans, constraints, transactions, privileges/RLS, and maintenance. |
| SQLite | `sqlite-sql-engineering`, `sql-engineering`, `rust-persistence-sql` | Complete | PRAGMAs, WAL/locking, one-writer model, migrations, indexes, and limitations. |
| Python | `python-engineering`, `documentation-engineering`, data/security skills | Complete | `uv`, Ruff, ty/mypy/Pyright, tests, docstrings, review, security, and DB delegation. |
| JavaScript and TypeScript | `javascript-typescript-engineering`, `playwright-e2e`, `documentation-engineering`, data/security skills | Complete | Bun-first when local, but Node/pnpm/npm/yarn/Deno and Prettier/ecosystem tooling are covered. |
| Rust | `rust-engineering`, `rust-testing-quality`, `rust-async-web`, `rust-persistence-sql`, `rust-code-review`, data/security/docs skills | Complete | Crates, workspaces, macros, async/web, error handling, docs/tests, rand/serde/anyhow/tokio/reqwest, and SQL library choices. |
| Running tests effectively | `test-driven-development`, `rust-testing-quality`, `python-engineering`, `javascript-typescript-engineering`, `playwright-e2e`, `gherkin` | Complete | Unit, integration, doctest/rustdoc, pydoc examples, E2E, behavior, property, regression, selection, and failure interpretation are distributed to the relevant workflow skills. |
| Root cause analysis and systematic debugging | `systematic-debugging`, `root-cause-analysis` | Complete | Reproduction, narrowing, hypotheses, instrumentation, logs/traces, minimal cases, fix validation, and prevention. |
| Justfiles | `justfiles` | Complete | Recipe design, portability, parameters, env vars, docs, composition, safety, idempotence, and validation. |
| Brainstorming and decision support | `brainstorming` | Complete | Divergence, tradeoffs, assumptions, options, and actionable recommendations. |
| Documentation | `documentation-engineering`, `python-engineering`, `rust-testing-quality`, `rust-engineering`, `code-review` | Complete | Markdown, README, API docs, comments, rustdoc, pydoc/docstrings, maintainable examples, and anti-slop prose rules. |

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
Scenario: First-party resources are reachable
  Given a first-party skill contains a reference, script, template, or asset
  When repository validation runs
  Then every resource file is reachable from SKILL.md through local Markdown links
  And every local Markdown link resolves to an existing file
```

```gherkin
Scenario: Security-sensitive work uses explicit review
  Given a change touches auth, crypto, secrets, sessions, input validation, CORS, CSP, CSRF, OAuth, tokens, file paths, command execution, or dependency trust
  When an agent reviews the change
  Then it loads security-review and security-review-evidence with code-review
  And reports only sanitized, verified findings
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
