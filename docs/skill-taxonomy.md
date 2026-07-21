# Skill Taxonomy

This repository keeps first-party global agent skills small, focused, and
orthogonal. A skill is reusable operating guidance for a recurring task. It is
not a project diary, changelog, broad philosophy document, or dumping ground for
unloaded templates.

## Domain Model

- **Skill:** A directory under `skills/` with `SKILL.md` frontmatter and focused
  procedural guidance. A skill is loaded procedure, not a runtime Task agent ID,
  and it grants no edit, delegation, review, or approval authority. Use the
  [engineering agent governance guide](engineering-agent-governance.md) when a
  skill routes work to an agent or command.
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
- The validator consumes the three-column `Category`, `Skills`, and `Boundary`
  table under `## Taxonomy`. Preserve that heading and table shape, and list
  skill IDs as backticked references in the `Skills` column.
- Keep vendor/tool-specific advice in the narrowest skill that needs it; use
  project-neutral wording elsewhere.
- Keep every first-party skill transferable across target repositories. Derive
  project names, modules, paths, workflow recipes, frameworks, and validation
  commands from local evidence; use placeholders for machine paths and keep
  ecosystem-specific examples conditional rather than universal.
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
| Specialist reviews and release readiness | `adversarial-review`, `architecture-review`, `domain-modeling`, `performance-review`, `prompt-engineering-review`, `release-readiness`, `technical-debt-audit`, `testing-strategy`, `ux-accessibility-review` | Focused final verification, architecture/domain/performance/test/prompt/technical-debt/UX/accessibility review, repository debt portfolio assessment, and evidence-based ship or hold decisions; implementation remains with the owning method or engineering skill. |
| Security review | `threat-modeling`, `security-review`, `security-review-evidence`, `dependency-supply-chain-review` | Security design analysis, implemented-control audits, sanitized evidence handling, and dependency/supply-chain risk for trust-boundary work. |
| Documentation | `documentation-engineering` | Markdown, README, API docs, comments, docstrings, Rustdoc, pydoc, Javadoc, JSDoc/TSDoc, perldoc/POD, executable examples, and documentation review. |
| Internationalization and localization | `internationalization-localization` | User-facing text localization, Project Fluent, `.ftl` authoring, locale fallback, multilingual catalogs, and localized output validation across language stacks. |
| API design and contracts | `api-design` | Public/service interface contracts, compatibility, versioning, idempotency, request/response/error envelopes, schema artifacts, and consumer/provider obligations. |
| Observability and operations | `observability-engineering` | Durable logs, metrics, traces, correlation, dashboards, alerts, SLO/SLI signals, runbooks, incident visibility, and telemetry safety. |
| CI, release, and container engineering | `semantic-versioning`, `ci-release-engineering`, `container-engineering` | Semantic release classification and version metadata, checked-in CI/release provider workflows, automated publication, Docker/OCI image construction, and Docker Compose implementation; API contract design, language commands, Git operations, security review, supply-chain trust, and final readiness remain with their owning skills. |
| Design methods and architecture | `brainstorming`, `behavior-driven-development`, `clean-architecture`, `domain-driven-design`, `hexagonal-architecture`, `onion-architecture`, `test-driven-development`, `gherkin` | Use the direct method or architecture skill that matches the work; do not load a meta-selection skill for simple changes. |
| Debugging and prevention | `systematic-debugging`, `root-cause-analysis` | Active symptom diagnosis first; postmortem and recurrence prevention after the direct cause is understood. |
| Data, identifiers, and SQL | `random-data-identifiers`, `sql-engineering`, `postgresql-sql-engineering`, `sqlite-sql-engineering` | Randomness/IDs, database-neutral SQL, and engine-specific PostgreSQL/SQLite schema, migration, query, transaction, performance, security, and review guidance. |
| Scripting and automation | `script-engineering`, `powershell-engineering` | Cross-language runtime discovery, script suitability and language selection, shared script contracts, testing, safety, task-runner integration, and idiomatic cross-platform PowerShell; other language and workflow skills retain their specialized mechanics. |
| Python engineering | `python-engineering` | Python implementation, review, testing, packaging, dependency management, quality gates, docs, and `uv` workflows. |
| Ruby engineering | `ruby-engineering` | Ruby implementation, scripting, review, testing, Bundler/gem workflows, idioms, anti-patterns, and quality gates. |
| JavaScript and TypeScript engineering | `javascript-typescript-engineering`, `playwright-e2e` | JS/TS implementation/tooling/package workflows and checked-in Playwright E2E tests. |
| Frontend styling | `css-scss-styling` | CSS/SCSS/Sass and Tailwind CSS decisions, stylesheet architecture, CSS modules, CSS-in-JS, utility-class conventions, design tokens, source detection, responsive layout, browser compatibility, and styling migrations across web stacks. |
| Rust engineering | `rust-engineering`, `rust-testing-quality`, `rust-async-web`, `rust-persistence-sql`, `rust-code-review` | Project-neutral Rust implementation, tests, Cargo/Bacon feedback and quality gates, async/web/full-stack work, SQLx/SeaQuery/ORM persistence, and Rust review. |
| Language design patterns and anti-patterns | `rust-design-patterns`, `rust-antipatterns`, `python-design-patterns`, `python-antipatterns`, `typescript-javascript-design-patterns`, `typescript-javascript-antipatterns` | Standalone language-specific pattern selection and smell-detection guidance, with routing from the broader language skills. |
| Public web research | `hound-web-research` | Public source discovery, page and PDF retrieval, bounded crawling, OCR, visual evidence, source verification, and safe Hound MCP operation; structured GitHub platform objects, repository-local evidence, authenticated interaction, and durable browser tests remain elsewhere. |
| Project workflow tools | `git-commit`, `git-workflows`, `github-mcp-operations`, `justfiles`, `suggest-lucide-icons` | Narrow operational guidance for constructing commits, repository-state Git workflows, structured GitHub platform operations, Justfiles, and verified Lucide icon names. |
| Third-party runtime installs | `agent-browser`, `anti-ai-slop-writing`, `find-skills`, `playwright-cli` | Installed locally for runtime use but ignored or lockfile-owned; do not edit as first-party skills. |

## API and Observability Skill Boundaries

These first-party contracts document boundaries shared by the taxonomy,
cross-reference map, and validator-required related-link rules. The skill files
remain the source of truth for frontmatter descriptions and detailed workflows.

### `observability-engineering`

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
  `semantic-versioning` when the release delta needs a patch, minor, major, or
  prerelease recommendation or metadata bump. Add
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
| `script-engineering` | Cross-language automation scripts, runtime discovery, POSIX shell/Bash/zsh/Fish/PowerShell/Python/Ruby/Node selection, script suitability, shared safety contracts, behavioral testing, package/task-runner boundaries, and Just integration. | Running an existing script or recipe without changing it, ordinary application code with no automation surface, or hosted CI/container semantics beyond invoked commands. |
| `python-engineering` | Python source, tests, pyproject.toml, uv.lock, packaging, linting, typing, docstrings, dependency management, async task/queue execution, and Python review. | Non-Python package managers, database-native schema design, browser E2E test design, or hosted CI/release provider configuration. |
| `ruby-engineering` | Ruby source, scripts, gems, Gemfile/Gemfile.lock, Bundler, Rake, Minitest, RSpec, RuboCop, CLIs, idioms, anti-patterns, and Ruby review. | Generic script-language selection with no Ruby implementation, non-Ruby package workflows, or framework-specific behavior better owned elsewhere. |
| `powershell-engineering` | Cross-platform `.ps1`/`.psm1`/`.psd1` implementation, advanced functions/modules, objects and streams, native commands, errors, `SupportsShouldProcess`, Pester, PSScriptAnalyzer, and Windows/macOS/Linux compatibility. | Running an existing PowerShell command, generic language selection with no PowerShell implementation, or Windows-only platform administration outside a repository script change. |
| `python-design-patterns` | Python-specific design patterns such as dataclasses, value objects, protocols, context managers, supervised task groups, adapters, repositories, factories, and Python expression of Clean/Hexagonal/Onion boundaries. | General Python workflow, package management, async execution policy, or smell-focused anti-pattern review. |
| `python-antipatterns` | Python-specific generated-code and design smells such as mutable defaults, global state, import-time side effects, broad `Any`, broad exceptions, framework/ORM leakage, async blocking, and brittle tests. | Positive pattern selection or ordinary Python workflow. |
| `javascript-typescript-engineering` | JS/TS source, package.json, lockfiles, Node/npm, Bun, Deno, pnpm, or Yarn workflows, TypeScript, lint/format/test/build scripts, dependencies, workspaces, and JS/TS review. | Checked-in Playwright spec design, Rust/Python/database work, or CSS/SCSS styling decisions without JS/TS implementation or tooling impact. |
| `css-scss-styling` | CSS, SCSS/Sass, Tailwind CSS, CSS modules, CSS-in-JS styling choices, utility-class conventions, design tokens, cascade/layers, source detection, container/media queries, responsive layout, browser compatibility, and styling-system migration. | Pure JS/TS/Python/Rust behavior changes, API/data work, checked-in browser E2E strategy, or vendor-specific framework setup with no styling surface. |
| `typescript-javascript-design-patterns` | TypeScript/JavaScript-specific design patterns such as discriminated unions, branded types, runtime validation boundaries, adapter modules, functional core/imperative shell, use-case handlers, async orchestration, and test builders. | Package manager workflows, checked-in Playwright spec design, or smell-focused anti-pattern review. |
| `typescript-javascript-antipatterns` | TypeScript/JavaScript smells such as `any`, unsafe assertions, missing runtime validation, unawaited promises, singleton service bags, import-time side effects, framework/UI leakage, weak randomness, over-mocked tests, and brittle E2E tests. | Positive pattern selection or ordinary JS/TS workflow. |
| `documentation-engineering` | Markdown, README, API docs, code comments, docstrings, Rustdoc, pydoc, Javadoc, JSDoc/TSDoc, perldoc/POD, examples, documentation tests, and review. | Code-only behavior changes with no reader-facing documentation or comment impact; standalone docs remain outside an explicitly code-only assignment unless used as evidence. |

### Future Python and TypeScript/JavaScript Split Triggers

These are not backlog items. Split `python-engineering` or
`javascript-typescript-engineering` only after repeated tasks show a durable
activation boundary that would make the broad language skill noisy or
under-specific. Cross-stack UI and accessibility audits now route to
`ux-accessibility-review`; implementation remains with styling, language, i18n,
and browser-test skills.

- **Testing:** recurring work is mostly test strategy, fixtures, runner behavior,
  coverage, flake isolation, or CI lane selection across projects, rather than
  implementation plus its normal tests. Keep checked-in browser E2E work in
  `playwright-e2e`.
- **Packaging and toolchains:** package metadata, builds, publishing, lockfiles,
  workspaces, or dependency resolution become version-sensitive enough that they
  can be handled without loading general implementation guidance. Keep checked-in
  provider workflows and automated publication in `ci-release-engineering`.
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

Apply the same evidence threshold to `ruby-engineering`. Keep idioms,
anti-patterns, testing, gems, and ordinary framework-adjacent Ruby together until
repeated tasks show that a Ruby testing, packaging, design-pattern, anti-pattern,
or framework skill has a distinct activation boundary and evidence workflow.

## Rust Skill Boundaries

| Skill | Use For | Do Not Use For |
| --- | --- | --- |
| `rust-engineering` | Core Rust implementation, crate/workspace setup, feature flags, ownership/lifetimes, traits/generics, error design, refactoring, design patterns, common crates, and macros. | Test-runner strategy, SQLx/SeaQuery/database specifics, or framework-specific async/web design except as boundary context. |
| `rust-design-patterns` | Rust-specific pattern and idiom choices such as newtypes, enums, RAII guards, builders, traits as ports, compose-structs, small crates, contained unsafe modules, custom traits for complex bounds, and macros. | Broader Rust workflow, cargo quality gates, persistence-specific work, or smell-focused anti-pattern review. |
| `rust-antipatterns` | Rust-specific generated-code and design smells such as clone-to-satisfy-borrow-checker, reflexive shared mutability, deref polymorphism, crate-root deny-warnings, panic at trust boundaries, async overuse, macro overreach, and framework leakage. | Positive pattern selection or ordinary Rust implementation. |
| `rust-testing-quality` | Rust unit/integration/e2e/property/doctest/compile-fail tests, TDD/BDD loops, `cargo fmt`, `cargo check`, `cargo test`, `cargo test --doc`, `cargo clippy`, `cargo nextest`, and Bacon feedback jobs. | General debugging without a known failing symptom, framework-specific server/client coordination, or SQLx/database-specific validation beyond naming the needed gate. |
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
- Use **Gherkin** when formal `.feature` artifacts or Gherkin syntax are needed.
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

| Skill | Purpose And Trigger | Boundary Rationale |
| --- | --- | --- |
| `adversarial-review` | Independent final challenge of completed changes, agent claims, merge readiness, hidden regressions, and unsupported assumptions. | Provides a skeptical verification pass after implementation or primary review while reusing the general review evidence protocol. |
| `api-design` | API contracts for HTTP/REST, RPC/GraphQL, webhooks, events, request/response/error envelopes, pagination/filtering/sorting, idempotency, versioning, schema artifacts, SDK/CLI surfaces, and consumer/provider compatibility. | Owns contract and compatibility guidance while language, data, security, testing, observability, and documentation skills own their mechanics. |
| `architecture-review` | Architecture-focused audits of boundaries, dependency direction, ports/adapters, Clean/Hexagonal/Onion/DDD hybrids, and modular structure. | Separates architecture findings from architecture design and implementation guidance. |
| `behavior-driven-development` | Behavior examples, acceptance criteria, workflows, and executable specifications. | Focuses on behavior discovery and examples; `gherkin` owns formal feature-file syntax. |
| `brainstorming` | Structured option generation for ambiguous engineering choices before implementation. | Activates only when multiple credible paths and meaningful tradeoffs exist. |
| `ci-release-engineering` | Checked-in CI and release-provider workflows for triggers, refs, jobs, matrices, services, caches, artifacts, permissions, concurrency, environments, automated versioning, tags, releases, and package or binary publication. | Owns hosted pipeline implementation while language/test skills own invoked commands, supply-chain and security skills own trust review, Git owns manual operations, and release readiness owns ship decisions. |
| `clean-architecture` | Clean Architecture, dependency rule, entities, use cases/interactors, interface adapters, framework/database/UI independence, and Clean vs Hexagonal/Onion/layered tradeoffs. | Owns use-case and interface-adapter framing without duplicating ports/adapters or domain-ring guidance. |
| `code-review` | General repository-local audit and review workflow, severity, and finding format. | Owns general review reporting while specialist skills add narrow evidence lenses. |
| `container-engineering` | Dockerfile, Containerfile, `.dockerignore`, BuildKit/OCI image, and Docker Compose implementation, including stages, artifact transfer, runtime users, entrypoints, health, ports, networks, volumes, secrets/config, lifecycle, resources, and privileges. | Owns container build and Compose behavior while language skills own application commands, supply-chain and security skills own trust review, and CI/release engineering owns hosted pipelines. |
| `create-agent-skill` | Creating, updating, validating, and maintaining reusable `SKILL.md` skills. | Owns reusable skill contracts and repository-specific skill governance. |
| `css-scss-styling` | CSS and SCSS/Sass stylesheet work, Tailwind CSS adoption and conventions, CSS modules, CSS-in-JS styling choices, modern CSS features, Sass modules, utility source detection, responsive/accessibility/performance concerns, and styling-system migration. | Covers cross-stack styling without splitting technologies into duplicate skills, defaulting to Sass, or introducing Tailwind without repository evidence and an explicit adoption goal. |
| `dependency-supply-chain-review` | Dependency audits, SBOM/SCA output, CVE/GHSA advisories, package provenance, registries, manifests, lockfiles, install scripts, CI bootstrap dependencies, containers, binaries, and vendored/generated code. | Owns supply-chain trust while language skills own package-manager mechanics. |
| `documentation-engineering` | Concise, accurate Markdown, README, API docs, comments, docstrings, Rustdoc, pydoc, Javadoc, JSDoc/TSDoc, perldoc/POD, tested examples, and documentation review. | Provides first-party documentation workflow independent of third-party writing tools and uses the repository's existing language-specific documentation toolchain. |
| `domain-driven-design` | Domain modeling, bounded contexts, invariants, repositories, services, events, and language. | Owns model discovery and implementation with explicit anti-ceremony guidance. |
| `domain-modeling` | Tactical DDD review of aggregates, entities, value objects, invariants, services, lifecycle ownership, and ubiquitous language. | Provides a tactical review lens while `domain-driven-design` owns discovery and implementation. |
| `gherkin` | Writing or editing formal `.feature` files, Gherkin syntax, and step wording. | Owns formal Gherkin artifacts as a companion to BDD. |
| `git-commit` | Atomic commits, logical grouping, staged diff review, and commit messages. | Keeps authorization, staging, grouping, and commit-message decisions in one workflow. |
| `git-workflows` | Safe branch, remote, history-inspection, integration, rewrite, conflict, recovery, tag, and worktree workflows. | Owns repository-state operations beyond constructing a new commit while routing commit composition, security-sensitive Git incidents, and supply-chain provenance to their focused skills. |
| `github-mcp-operations` | Structured evidence and authorized operations through GitHub's official MCP server for repositories, commits, issues, pull requests, reviews, Actions, releases, security findings, organizations, and users. | Owns official-server provenance, GitHub object selection, read-versus-mutation boundaries, and GitHub/Hound combination rules while local Git, public-web research, browser interaction, credentials, and security review remain with their dedicated workflows. |
| `hexagonal-architecture` | Ports and Adapters, use cases, application services, dependency inversion, inbound/outbound adapters, and Clean/Onion-style core isolation. | Owns external-actor and port/adapter decisions without making indirection mandatory. |
| `hound-web-research` | Public web research with the Hound MCP server, including source discovery, known-URL and PDF retrieval, bounded same-domain crawling, OCR, visual evidence, cache/version diagnostics, and source verification. | Owns safe Hound tool choice and external-evidence handling while structured GitHub platform objects, repository-local facts, signed-in browser interaction, checked-in Playwright tests, private resources, security review, and Hound installation remain with their dedicated workflows. |
| `internationalization-localization` | Internationalization, localization, Project Fluent, Fluent Translation List (`.ftl`) authoring, locale fallback, multilingual catalogs, localized formatting, and cross-stack Fluent integration guidance. | Owns locale and message behavior while delegating stack mechanics, styling, security, testing, and documentation. |
| `javascript-typescript-engineering` | JS/TS source, TypeScript, package managers, scripts, tests, lint/format/build, dependencies, workspaces, and CLIs. | Covers JS/TS broadly with Node/npm defaults and other runtimes only when local evidence requires them. |
| `justfiles` | Designing, refactoring, auditing, and validating Justfiles and `just` workflows. | Keeps version-sensitive recipe syntax, portability, and safety in one focused workflow. |
| `observability-engineering` | Observability, telemetry, production diagnostics, structured logs, metrics, traces, context propagation, correlation/request IDs, dashboards, alerts, SLO/SLI/error-budget signals, runbooks, incident visibility, and telemetry safety. | Owns signal design and operational visibility while other skills own implementation and active debugging. |
| `onion-architecture` | Onion Architecture, domain/application rings, inward dependencies, infrastructure-at-the-edge design, and Clean/Hexagonal/Onion tradeoffs. | Owns direct domain/application-ring framing and cross-routes to adjacent architectures. |
| `performance-review` | Cross-stack performance and scalability review using workload, baseline, profiling, query-plan, rendering, concurrency, resource, and measurement evidence. | Provides a measurement-driven review lens while implementation remains with language, runtime, browser, SQL, and observability skills. |
| `playwright-e2e` | Checked-in Playwright tests, configs, helpers, traces, lanes, and browser-visible behavior. | Remains distinct from one-off browser automation and lower-level domain tests. |
| `postgresql-sql-engineering` | PostgreSQL schema, migrations, SQL, transactions, indexes, JSONB, RLS, privileges, plans, maintenance, and review. | Owns PostgreSQL-native behavior while Rust adapter details stay in `rust-persistence-sql`. |
| `prompt-engineering-review` | Review and, when requested, rewrite coding-agent prompts, roles, delegation instructions, acceptance criteria, and quality gates. | Owns prompt behavior and clarity while `create-agent-skill` owns reusable skill contracts. |
| `python-antipatterns` | Python generated-code and design smell review for mutable defaults, global state, import-time side effects, broad typing, framework leakage, async blocking, and brittle tests. | Owns smell-focused Python review while positive patterns and broad workflow stay separate. |
| `python-design-patterns` | Python pattern guidance for dataclasses, value objects, protocols, context managers, supervised task groups, adapters, repositories, factories, fixtures, and architecture boundaries. | Owns positive pattern selection while `python-engineering` remains the workflow and concurrency-execution skill. |
| `python-engineering` | Python code, tests, typing, packaging, dependency management, `uv`, Ruff, ty/mypy/Pyright, docstrings, async task/queue execution, and review. | Covers Python broadly while delegating database-native behavior, hosted pipelines, and container configuration to focused skills. |
| `powershell-engineering` | Cross-platform PowerShell scripts, modules, manifests, advanced functions, object pipelines, streams, errors, native processes, safe side effects, Pester, PSScriptAnalyzer, and compatibility testing. | Owns language-specific PowerShell mechanics while `script-engineering` owns script suitability and cross-language selection. |
| `random-data-identifiers` | Secure randomness, UUIDs/CUIDs/ULIDs, generated IDs, test data, seeded reproducibility, and collision review. | Owns cross-language randomness and generated-identifier decisions. |
| `release-readiness` | Final merge or release assessment across acceptance criteria, tests, docs, migrations, rollout, rollback, operations, and cross-functional risk. | Owns the evidence-based ship or hold decision after implementation and focused reviews. |
| `review-verification-protocol` | Evidence gates for review findings and specialist review lenses. | Provides a hidden, reusable gate that prevents speculative findings across review skills. |
| `root-cause-analysis` | Recurring failures, incidents, regressions, control gaps, and prevention work. | Starts after the direct cause is understood and owns recurrence prevention. |
| `ruby-engineering` | Ruby implementation, scripting, gems, Bundler, Rake, Minitest/RSpec, quality gates, idioms, anti-patterns, and review. | Covers Ruby broadly while `script-engineering` owns cross-language selection and focused security/data/workflow skills own their boundaries. |
| `rust-antipatterns` | Rust generated-code and design smell review for ownership workarounds, reflexive shared mutability, deref polymorphism, deny-warnings misuse, panic boundaries, async overuse, and framework leakage. | Owns smell-focused Rust review while positive patterns and broad Rust workflow stay separate. |
| `rust-async-web` | Tokio, async tasks, channels, cancellation, Axum, Leptos, Axum-Leptos, SSR, hydration, and WASM. | Owns Rust runtime and web behavior while delegating SQL, cargo lanes, and deep references. |
| `rust-code-review` | Rust-specific review lens for ownership, APIs, async, persistence, macros, unsafe, and performance. | Adds Rust-specific rigor to the general review workflow and routes to implementation and data skills. |
| `rust-design-patterns` | Rust pattern and idiom guidance for newtypes, enums, RAII guards, builders, traits as ports, compose-structs, contained unsafe modules, custom traits, and macros. | Owns positive Rust pattern selection while `rust-engineering` remains the workflow skill. |
| `rust-engineering` | Core Rust implementation, crates, modules, APIs, ownership, traits, errors, features, refactors, common crates, and macros. | Owns core Rust implementation and delegates specialist surfaces. |
| `rust-persistence-sql` | Rust SQLx, SeaQuery, SeaORM/Diesel/raw-SQL choices, pools, transactions, offline metadata, database adapters, dynamic SQL, and persistence boundaries. | Owns Rust adapter and query-builder choices while database-native design stays with SQL skills. |
| `rust-testing-quality` | Rust tests, doctests, nextest, Clippy, formatting, Cargo checks, Bacon feedback loops, TDD/BDD loops, and CI evidence. | Keeps iterative and final Cargo test and quality gates in one coherent workflow. |
| `script-engineering` | Cross-language script creation, review, testing, runtime discovery, language selection, script-vs-application decisions, safety contracts, and task-runner integration. | Owns shared automation procedure while language skills own language-specific implementation depth, `justfiles` owns recipe design, and CI/container skills own their provider/runtime configuration. |
| `security-review` | Security audit workflow for auth, crypto, secrets, sessions, input validation, trust boundaries, web controls, dependency trust, and sanitized reporting. | Owns implemented-control review and routes evidence and supply-chain concerns explicitly. |
| `security-review-evidence` | Sanitized evidence checklist for security-sensitive changes and reviews. | Provides hidden support for trust-boundary and secret-adjacent evidence. |
| `semantic-versioning` | Semantic Versioning policy, release-delta classification, patch/minor/major and prerelease recommendations, next-version calculation, and requested version-metadata bumps. | Owns release-version selection while API design owns contract semantics, language skills own ecosystem metadata mechanics, CI/release engineering owns automation and publication, Git owns tags and pushes, and release readiness owns ship decisions. |
| `sql-engineering` | Database-neutral SQL reading, writing, refactoring, migrations, constraints, indexes, transactions, advanced queries, performance, and review. | Owns database-neutral SQL before engine-specific escalation. |
| `sqlite-sql-engineering` | SQLite schema, migrations, PRAGMAs, WAL/locking, transactions, temporary DB tests, limitations, and query review. | Owns SQLite-native behavior without duplicating PostgreSQL or Rust adapter guidance. |
| `suggest-lucide-icons` | Verified Lucide icon name selection for UI concepts and placements. | Provides a small, independently routable icon-verification workflow. |
| `systematic-debugging` | Active failures, regressions, crashes, flakes, performance issues, build failures, and evidence-driven fixes. | Owns active symptom diagnosis with detailed heuristics progressively disclosed. |
| `technical-debt-audit` | Repository-wide or focused audits of accumulated maintainability debt, code-quality hotspots, dependency and upgrade friction, testing gaps, architecture erosion, documentation drift, quick wins, and blockers to future work or scaling. | Owns evidence-backed debt portfolio assessment and prioritization while focused review, security, language, testing, architecture, and documentation skills retain their specialist mechanics. |
| `test-driven-development` | Red-Green-Refactor, regression tests, test-level selection, and behavior-first implementation. | Owns the concise test-first implementation method used by language and workflow skills. |
| `testing-strategy` | Risk-focused review of test plans and suites, confidence gaps, flaky tests, boundary coverage, test levels, and maintainability. | Owns test-strategy assessment while test writing and TDD implementation remain separate. |
| `threat-modeling` | Threat models, abuse cases, actors, assets, data flows, trust boundaries, attack surface, security requirements, mitigations, assumptions, and residual risk. | Owns design-time security analysis and hands implemented-control findings to security review. |
| `typescript-javascript-antipatterns` | TypeScript/JavaScript generated-code and design smell review for `any`, unsafe assertions, missing runtime validation, unawaited promises, singleton state, framework/UI leakage, and brittle tests. | Owns smell-focused JS/TS review while positive patterns and broad workflow stay separate. |
| `typescript-javascript-design-patterns` | TypeScript/JavaScript pattern guidance for discriminated unions, branded types, runtime validation boundaries, adapter modules, use-case handlers, async orchestration, and test builders. | Owns positive pattern selection while `javascript-typescript-engineering` remains the workflow skill. |
| `ux-accessibility-review` | Focused UI/UX, responsive, interaction-state, visual-polish, and WCAG 2.2 AA review using rendered-interface evidence. | Owns cross-stack UI review while styling, language, i18n, and Playwright skills own implementation and durable tests. |

## Required Coverage Matrix

Coverage status means the current first-party baseline is covered and validated,
not that every future skill domain is exhausted. Add or split future skills only
when repeated tasks show a durable activation boundary that does not fit an
existing skill.

| Required Topic | Covering Skill(s) | Status | Notes |
| --- | --- | --- | --- |
| Code review | `code-review`, `review-verification-protocol`, `adversarial-review`, `architecture-review`, `domain-modeling`, `performance-review`, `testing-strategy`, `ux-accessibility-review`, `rust-code-review` | Baseline complete | Generic review and evidence gates plus focused final, architecture, domain, performance, test, UX/accessibility, and Rust review lenses. |
| Technical-debt audit | `technical-debt-audit`, `review-verification-protocol`, `architecture-review`, `testing-strategy`, `dependency-supply-chain-review`, `security-review`, `security-review-evidence`, `documentation-engineering`, language review skills | Baseline complete | Repository overview, evidence-gated systemic debt findings, qualitative test coverage when measured output is unavailable, dependency-health evidence, quick wins, strategic blockers, effort, benefit, sequencing, and residual risk are covered without conflating defects or cosmetic smells with debt. |
| Security review and audit | `threat-modeling`, `security-review`, `security-review-evidence`, `dependency-supply-chain-review`, `code-review`, language/data skills | Baseline complete | Design-time modeling, implemented-control review, supply-chain review, generic audit routing, and sanitized evidence are covered. |
| Public web research and source retrieval | `hound-web-research`, `github-mcp-operations`, `security-review`, `security-review-evidence`, `agent-browser`, `playwright-e2e` | Baseline complete | Covers sanitized public search, authoritative-source retrieval, known URLs and PDFs, bounded same-domain crawling, OCR and screenshots, GitHub-object separation, prompt-injection resistance, cache/version diagnostics, authenticated-browser and durable-test boundaries, and security handoffs. |
| GitHub platform operations | `github-mcp-operations`, `git-workflows`, `hound-web-research`, `security-review`, `security-review-evidence` | Baseline complete | Covers official-server provenance, structured remote GitHub reads, explicitly authorized mutations, local-Git and public-web boundaries, least-privilege operation, untrusted GitHub content, and distinct-gap combination with Hound. |
| Threat modeling and security design | `threat-modeling`, `security-review`, `security-review-evidence`, architecture/method/language skills | Baseline complete | Actors, assets, entry points, data flows, trust boundaries, abuse cases, mitigations, security acceptance criteria, residual risk, and handoff to verified review are covered. |
| Dependency and supply-chain review | `dependency-supply-chain-review`, `security-review`, `security-review-evidence`, language/workflow skills | Baseline complete | Manifests, lockfiles, SBOM/SCA/CVE/GHSA advisories, provenance, registries, install scripts, CI bootstrap, containers, binaries, vendored/generated code, and sanitized evidence are covered. |
| CI and release automation | `ci-release-engineering`, language/test skills, `justfiles`, `git-workflows`, `dependency-supply-chain-review`, `security-review`, `release-readiness` | Baseline complete | Checked-in provider workflows, triggers, ref selection, job graphs, matrices, services, caches, artifacts, permissions, concurrency, environments, automated versioning, publication, rerun safety, and handoffs are covered. |
| Semantic release version selection | `semantic-versioning`, `api-design`, language/package skills, `ci-release-engineering`, `git-workflows`, `release-readiness` | Baseline complete | Public-contract discovery, complete release-delta classification, patch/minor/major precedence, 0.x and prerelease handling, version calculation, requested metadata synchronization, and side-effect handoffs are covered. |
| Docker/OCI and Compose implementation | `container-engineering`, language skills, `justfiles`, `dependency-supply-chain-review`, `security-review`, `ci-release-engineering` | Baseline complete | Build contexts/stages, artifact transfer, runtime users and entrypoints, health, ports, networks, volumes, secrets/config, lifecycle, resource/privilege controls, image validation, and hosted pipeline handoff are covered. |
| BDD | `behavior-driven-development`, `gherkin`, `playwright-e2e` | Baseline complete | BDD principles and misuse are separate from formal `.feature` syntax. |
| DDD | `domain-driven-design`, `domain-modeling`, language/data skills | Baseline complete | Strategic and tactical modeling guidance plus a focused tactical review lens with anti-ceremony boundaries. |
| Clean / Hexagonal Architecture / Onion / Ports and Adapters | `clean-architecture`, `hexagonal-architecture`, `onion-architecture`, `architecture-review`, `domain-driven-design`, language/data skills | Baseline complete | Core isolation, dependency direction, entities, use cases/interactors, domain/application rings, interface adapters, ports/adapters, focused architecture review, tests, tradeoffs, and when not to add indirection. |
| TDD | `test-driven-development`, `testing-strategy`, language/test skills | Baseline complete | Red/green/refactor, test levels, regression, misuse guidance, and risk-focused strategy review. |
| Combining BDD, DDD, TDD, Clean Architecture, Hexagonal Architecture, and Onion Architecture | This taxonomy plus BDD/DDD/TDD/Clean/Hexagonal/Onion cross-references | Baseline complete | Composition guidance lives here to avoid a competing meta-skill. |
| Gherkin and `.feature` files | `gherkin`, `behavior-driven-development`, `playwright-e2e` | Baseline complete | Includes Given/When/Then discipline, outlines, anti-patterns, and language usage. |
| Language-specific design patterns and anti-patterns | `rust-design-patterns`, `rust-antipatterns`, `python-design-patterns`, `python-antipatterns`, `typescript-javascript-design-patterns`, `typescript-javascript-antipatterns`, language engineering skills | Baseline complete; known extensions tracked | Pattern selection and smell detection are standalone skills, with short routing rules in each broader language skill. |
| Random data and identifiers | `random-data-identifiers`, `security-review`, language/data skills | Baseline complete | Covers CSPRNG defaults for secrets and security-sensitive or public unguessable IDs, seeded reproducibility, UUID/CUID/ULID-style choices, tests, and warnings. |
| SQL | `sql-engineering`, `postgresql-sql-engineering`, `sqlite-sql-engineering`, `rust-persistence-sql` | Baseline complete; known extensions tracked | Generic SQL plus engine and Rust adapter specialization. |
| PostgreSQL | `postgresql-sql-engineering`, `sql-engineering`, `rust-persistence-sql` | Baseline complete | JSONB, indexes, plans, constraints, transactions, privileges/RLS, and maintenance. |
| SQLite | `sqlite-sql-engineering`, `sql-engineering`, `rust-persistence-sql` | Baseline complete | PRAGMAs, WAL/locking, one-writer model, migrations, indexes, and limitations. |
| Python | `python-engineering`, `python-design-patterns`, `python-antipatterns`, `documentation-engineering`, data/security skills | Baseline complete; known extensions tracked | `uv`, Ruff, ty/mypy/Pyright, tests, docstrings, review, async task ownership, bounded queues, cancellation/backpressure/retry policy, security, DB delegation, pattern selection, and smell detection. |
| JavaScript and TypeScript | `javascript-typescript-engineering`, `typescript-javascript-design-patterns`, `typescript-javascript-antipatterns`, `playwright-e2e`, `documentation-engineering`, data/security skills | Baseline complete; known extensions tracked | Node/npm defaults, repository-selected pnpm/yarn/Bun/Deno workflows, package scripts, local executables versus potentially fetching `npx`/`pnx`/`pnpm dlx`/`pnpx`/`bunx` runners, supply-chain routing, pattern selection, smell detection, and browser E2E are covered. |
| Ruby | `ruby-engineering`, `script-engineering`, `documentation-engineering`, data/security skills | Baseline complete; known extensions tracked | Runtime/Bundler evidence, gems and lockfiles, idioms, anti-patterns, Minitest/RSpec, unit/integration/CLI/E2E boundaries, scripting selection, quality gates, and security/dependency routing are covered. |
| Scripting and task automation | `script-engineering`, `powershell-engineering`, `ruby-engineering`, `justfiles`, language engineering skills, `test-driven-development`, `dependency-supply-chain-review`, security skills | Baseline complete | Runtime discovery, script suitability, POSIX shell/Bash/zsh/Fish/Python/Ruby/PowerShell/JS selection, no-shell/application promotion, shared contracts, syntax/static/behavioral validation, PowerShell cross-platform mechanics, test-runner choice, safety, package scripts, and thin task-runner wrappers are covered. |
| CSS, SCSS, and utility styling | `css-scss-styling`, `ux-accessibility-review`, `javascript-typescript-engineering`, `python-engineering`, `rust-async-web`, `playwright-e2e` | Baseline complete | Tailwind vs CSS vs SCSS decisions, installed-major detection, static utility source detection, theme tokens, Preflight/base-style risk, Sass modules, modern CSS features, cross-stack integration, accessibility/responsive/performance concerns, focused UI review, and migration validation are covered. |
| Internationalization and localization | `internationalization-localization`, language engineering skills, `api-design`, `css-scss-styling`, `playwright-e2e`, `security-review`, `security-review-evidence` | Baseline complete | Covers i18n/l10n concepts, Project Fluent and `.ftl` authoring, American English source locale, multilingual catalogs, locale fallback, Fluent JS/Python/Rust binding routing, localized output tests, accessibility, and trust-boundary/evidence handoffs. |
| Rust | `rust-engineering`, `rust-design-patterns`, `rust-antipatterns`, `rust-testing-quality`, `rust-async-web`, `rust-persistence-sql`, `rust-code-review`, data/security/docs skills | Baseline complete; known extensions tracked | Crates, workspaces, Cargo/Bacon feedback loops, patterns, anti-patterns, macros, async/web, error handling, docs/tests, rand/serde/anyhow/tokio/reqwest, and SQL library choices. |
| Running and reviewing tests effectively | `test-driven-development`, `testing-strategy`, `script-engineering`, `ruby-engineering`, `powershell-engineering`, `rust-testing-quality`, `python-engineering`, `javascript-typescript-engineering`, `playwright-e2e`, `gherkin` | Baseline complete | Unit, integration, script syntax/static/behavioral checks, Minitest/RSpec, Pester/PSScriptAnalyzer, doctest/rustdoc, pydoc examples, E2E, behavior, property, regression, continuous feedback, strategy review, selection, and failure interpretation are distributed to the relevant workflow skills. |
| Root cause analysis and systematic debugging | `systematic-debugging`, `root-cause-analysis` | Baseline complete | Reproduction, narrowing, hypotheses, instrumentation, logs/traces, minimal cases, fix validation, and prevention. |
| API design and contracts | `api-design`, language/framework/data/security/testing/docs skills | Baseline complete | First-party API contract guidance covers resource/operation shape, request/response/error envelopes, idempotency, versioning, compatibility, schema artifacts, SDK/CLI surfaces, and consumer/provider obligations while existing skills remain primary for implementation, database behavior, security controls, tests, observability, and docs. |
| Observability and telemetry | `observability-engineering`, language/framework/security/debugging/docs skills | Baseline complete | First-party observability guidance covers logs, metrics, traces, correlation/context propagation, telemetry safety, dashboards, alerts, SLO/SLI/error-budget signals, runbooks, and incident visibility while existing skills remain primary for implementation mechanics, active debugging, security evidence, tests, and documentation-only edits. |
| Performance and scalability review | `performance-review`, `code-review`, `review-verification-protocol`, language/runtime/browser/SQL/observability skills | Baseline complete | Cross-stack review covers workload and baseline definition, hot-path and scaling evidence, measurement plans, resource bounds, and before/after verification while specialist skills own implementation mechanics. |
| Git commits and repository workflows | `git-commit`, `git-workflows`, security and supply-chain skills when their triggers apply | Baseline complete | Commit construction remains separate from history inspection, branches, remotes, integration, history rewriting, conflicts, recovery, tags, and worktrees; both preserve unrelated work, require exact authorization for risky side effects, and route sensitive evidence conditionally. |
| Justfiles | `justfiles`, `script-engineering` | Baseline complete | Recipe design, portability, parameters, env vars, docs, composition, safety, idempotence, validation, and thin wrappers around independently testable scripts. |
| Brainstorming and decision support | `brainstorming` | Baseline complete | Divergence, tradeoffs, assumptions, options, and actionable recommendations. |
| Documentation | `documentation-engineering`, `python-engineering`, `rust-testing-quality`, `rust-engineering`, `javascript-typescript-engineering`, `code-review` | Baseline complete | Markdown, README, API docs, comments, docstrings, Rustdoc, pydoc, Javadoc, JSDoc/TSDoc, perldoc/POD, maintainable tested examples, missing-documentation judgment, and anti-slop prose rules. |
| Prompt engineering review | `prompt-engineering-review`, `create-agent-skill` | Baseline complete | Coding-agent prompt audits and rewrites are distinct from reusable skill authoring and application implementation. |
| Release readiness | `release-readiness`, `adversarial-review`, `code-review`, specialist review skills | Baseline complete | Final ship or hold decisions cover scope, validation, migration, rollout, rollback, operations, cross-functional review evidence, and residual risk. |
| UX and accessibility review | `ux-accessibility-review`, `css-scss-styling`, `playwright-e2e`, `internationalization-localization`, language engineering skills | Baseline complete | Cross-stack UI audits cover workflow usability, visual hierarchy, responsive and interaction states, rendered-interface evidence, and WCAG 2.2 AA concerns while implementation remains with the owning stack skill. |

## Retired, Merged, Renamed, Or Third-Party Skills

| Name Or Group | Decision |
| --- | --- |
| `bun-javascript-workflows` | Renamed and broadened to `javascript-typescript-engineering`; Node/npm is the default path, while Bun remains supported when local evidence shows a Bun-backed project. |
| `cargo-clippy`, `cargo-nextest`, `rustdoc-guidance` | Merged into `rust-testing-quality`; they are quality gates, not independent workflows. |
| Narrow Rust topic skills such as async review, Axum review, Leptos guidance, project setup, refactoring, macros, WASM, and SQLx review | Merged into the five Rust skills so activation is by durable workflow rather than library fragment. |
| Chidori project-specific skills and resources | Not part of the global taxonomy. Reusable project-neutral guidance has already been folded into language, data, and Rust skills; local paths, schema details, architecture, and workflow names remain local. |
| `agent-browser`, `anti-ai-slop-writing`, `find-skills`, `playwright-cli` | Third-party or ignored runtime installs. They may exist under `skills/` locally, but repository-owned audits should not edit them. |

## Acceptance Criteria

These scenarios are documented acceptance criteria. Treat one as executable only
when an automated test or validator check explicitly traces to it.

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
Scenario: First-party skills remain project-neutral
  Given a first-party skill is reusable across target repositories
  When repository validation runs
  Then skill instructions and reachable text resources contain no source-project identifiers
  And machine-specific home paths use placeholders or repository-relative examples
  And repository-specific modules, recipes, frameworks, and commands are derived from target-repository evidence
```

```gherkin
Scenario: Technical-debt audits separate systemic debt from defects
  Given a user requests a repository-wide or focused technical-debt audit
  When the agent assesses accumulated maintenance cost
  Then it loads technical-debt-audit and review-verification-protocol
  And maps the repository before reporting evidence-backed findings
  And uses qualitative test coverage unless observed tooling provides numeric coverage
  And verifies current dependency status before claiming deprecation, abandonment, or vulnerability
  And prioritizes quick wins, strategic blockers, and longer-term remediation without padding categories
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
Scenario: Git operations preserve work and require exact authorization
  Given a task constructs commits or changes branches, refs, history, remotes, tags, or worktrees
  When the agent chooses Git guidance
  Then commit grouping, staging, validation, and messages load git-commit
  And repository-state operations load git-workflows
  And the agent inspects policy, current work, publication state, and affected refs before mutation
  And worktree discard, history rewriting, ref deletion, remote updates, and forced changes require explicit authorization
  And secrets, credentialed remotes, signing trust, or untrusted hooks load security-review and security-review-evidence
  And submodule, hook-tool, vendored-source, or provenance questions load dependency-supply-chain-review
  And the result, validation, skipped checks, and residual risk are reported without sensitive values
```

```gherkin
Scenario: Randomness distinguishes security from reproducibility
  Given a change generates IDs, tokens, random test data, fixtures, or simulation inputs
  When the agent chooses randomness guidance
  Then it loads random-data-identifiers
  And uses secure randomness for secrets and security-sensitive or public unguessable IDs
  And uses explicit seeded PRNGs for reproducible tests
```

```gherkin
Scenario: CI and release implementation stays separate from readiness review
  Given a change touches checked-in CI or release-provider triggers, jobs, permissions, artifacts, versioning, tags, or publication
  When the agent implements the workflow
  Then it loads ci-release-engineering
  And language and test skills own the commands run by jobs
  And security-review and security-review-evidence handle permissions, secrets, OIDC, untrusted events, and command injection
  And release-readiness remains the final ship or hold decision
```

```gherkin
Scenario: Semantic version selection follows the released public contract
  Given a release unit has a current released version and a complete change delta
  When an agent recommends or applies the next Semantic Version
  Then it loads semantic-versioning
  And identifies the declared public contract and supported consumers
  And classifies every material change by compatibility impact
  And lets the highest required patch, minor, or major bump win
  And treats 0.x, prerelease, dependency, and ambiguous de facto behavior according to explicit project policy
  And does not tag, push, publish, deploy, or make the final ship decision without the owning workflow and authorization
```

```gherkin
Scenario: Container implementation composes with security and supply-chain review
  Given a change touches Dockerfile, Containerfile, .dockerignore, OCI image construction, or Docker Compose behavior
  When the agent implements the container configuration
  Then it loads container-engineering
  And dependency-supply-chain-review handles base image, package, registry, SBOM, attestation, and provenance trust
  And security-review and security-review-evidence handle secrets, mounts, ports, capabilities, sockets, and other trust boundaries
  And ci-release-engineering owns hosted workflows that build, test, or publish the image
```

```gherkin
Scenario: JavaScript and TypeScript choose the local workflow
  Given a change touches JS/TS source, package scripts, lockfiles, type checks, linting, formatting, tests, builds, or dependencies
  When the agent chooses workflow guidance
  Then it loads javascript-typescript-engineering
  And defaults to Node/npm when no repository evidence requires another workflow
  And does not assume pnpm, yarn, Bun, Deno, React, Vite, ESLint, or Prettier without repository evidence
```

```gherkin
Scenario: Package runners distinguish local tools from fetched execution
  Given a JavaScript or TypeScript workflow needs a package CLI
  When an agent chooses package scripts, npm exec or npx, pnpm exec or pnx/dlx/pnpx, or bunx
  Then it loads javascript-typescript-engineering
  And prefers the repository's selected package manager and locked local dependency for durable work
  And treats any missing-package fetch-and-run behavior as an explicit dependency and supply-chain decision
  And does not rely on an interactive confirmation prompt in CI or another non-interactive environment
```

```gherkin
Scenario: Ruby work uses repository-owned runtime and test conventions
  Given a change touches Ruby source, scripts, gems, Bundler, Rake, Minitest, or RSpec
  When the agent implements or validates the change
  Then it loads ruby-engineering
  And derives Ruby, Bundler, dependency, style, and test commands from repository evidence
  And chooses unit, integration, CLI/process, or end-to-end coverage for the observable risk
  And uses script-engineering when the unresolved decision is Ruby versus another automation language
```

```gherkin
Scenario: Cross-platform PowerShell is tested as a platform contract
  Given a change claims PowerShell support on more than one operating system or edition
  When the agent implements or validates the script or module
  Then it loads powershell-engineering
  And distinguishes pwsh from Windows PowerShell
  And checks cmdlets, modules, paths, encodings, native commands, streams, and exit behavior on the claimed targets
  And uses Pester, PSScriptAnalyzer, and target execution proportionately without treating static analysis as runtime proof
```

```gherkin
Scenario: Rust continuous feedback uses project-level Bacon jobs
  Given a Rust repository adopts Bacon or the task asks to establish it
  And the project needs continuous check, test, lint, or server feedback
  When the agent establishes or updates the development loop
  Then it loads rust-testing-quality and writes supported jobs in bacon.toml
  And it loads rust-async-web for Axum or Leptos server and client coordination
  And it does not nest a framework-managed development server inside another file watcher
  And it runs direct repository or CI-equivalent commands for final evidence
```

```gherkin
Scenario: CSS, SCSS, and utility changes preserve the local styling system
  Given a change touches CSS, SCSS, Sass, Tailwind, CSS modules, CSS-in-JS, utility classes, design tokens, or stylesheet build config
  When the agent chooses styling guidance
  Then it loads css-scss-styling
  And detects the existing styling system and installed framework version before editing
  And preserves that system unless an explicit adoption or migration goal justifies Tailwind, CSS, or SCSS
  And validates source detection plus the generated, compiled, or browser-visible result as applicable
```

```gherkin
Scenario: Database-neutral SQL escalates to engine-specific guidance
  Given a change touches SQL, schemas, migrations, transactions, indexes, views, functions, triggers, or query performance
  When the target database has PostgreSQL or SQLite-specific behavior
  Then the agent loads sql-engineering plus the matching engine skill
  And validates behavior against the target engine rather than mocks or another database
```
