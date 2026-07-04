# Language and Support Skill Guidance

## TL;DR

> **Summary**: Enrich broad Rust, Python, and TypeScript/JavaScript skill guidance with compact idiom, anti-pattern, and architecture examples, while labeling support protocols and tuning security/docs/random/current-docs cross-links.

> **Estimated Effort**: Medium

## Context

### Original Request

Continue the approved skill-system improvements after `01-governance-and-architecture-taxonomy.md` and `02-architecture-routing-and-method-skills.md` establish shared vocabulary.

### Key Findings

- Rust already has a mature skill family; compact pattern guidance belongs mostly in existing Rust skills because pattern mistakes are not frequent.
- `python-engineering` and `javascript-typescript-engineering` are broad entry points that should be enriched before future splitting.
- Support protocol skills already use `user-invocable: false`, but their bodies should make support-protocol status clear.
- Security, documentation, randomness, and current-docs routing should remain focused on their trigger surfaces, not become architecture-selection dumps.

## Objectives

### Core Objective

Make language and support skills more useful for agents without adding new standalone pattern or language-split skills in this iteration.

### Deliverables

- Support protocol labels in hidden support skills.
- Focused routing links for security, Context7, randomness, and documentation workflows.
- Compact Rust, Python, and JS/TS idiom and anti-pattern guidance.
- Concise architecture examples in language skills where they help agents apply Clean, Onion, Hexagonal, BDD, DDD, or TDD idiomatically.

### Definition of Done

- Support protocols remain hidden and are visibly labeled as support protocols.
- Language additions are scannable checklists, not long pattern catalogs.
- Architecture examples preserve inward dependency direction and avoid framework/persistence leakage into domain/application cores.
- Documentation/comment expectations are explicit where future code or public APIs are discussed.

### Guardrails (Must NOT)

- Do not create standalone Rust, Python, or TypeScript/JavaScript pattern skills.
- Do not split Python or JS/TS skills yet.
- Do not duplicate full architecture guidance inside language skills.
- Do not weaken secret-handling or sanitized-evidence language.
- Do not add external reviewer invocation tasks to any plan or skill.

## TODOs

- [ ] 1. Label support protocols and preserve safety routing

  **What**: Add concise support-protocol labels to hidden support skills. Preserve `user-invocable: false`, `code-review`/`security-review` routing, and sanitized evidence requirements. Do not expose raw secrets, tokens, cookies, `.env` contents, credentialed URLs, private keys, or sensitive payloads in examples.

  **Files**: `skills/review-verification-protocol/SKILL.md`, `skills/security-review-evidence/SKILL.md`

  **Acceptance**: Both skills clearly state they are support protocols loaded by other skills; both retain `user-invocable: false`; `security-review-evidence` remains the sanitized-evidence companion for security-sensitive work; local links validate.

- [ ] 2. Tune supporting skill cross-links

  **What**: Add or adjust routing links only where they help execution: security-sensitive surfaces should route to security review; version-sensitive external docs should route to Context7; random IDs/tokens/fixtures should route to randomness guidance; documentation work should route to documentation engineering. Keep each skill focused on its own trigger.

  **Files**: `skills/security-review/SKILL.md`, `skills/context7-docs/SKILL.md`, `skills/random-data-identifiers/SKILL.md`, `skills/documentation-engineering/SKILL.md`, `skills/justfiles/SKILL.md`, `skills/playwright-e2e/SKILL.md`, `skills/postgresql-sql-engineering/SKILL.md`, `skills/python-engineering/SKILL.md`

  **Acceptance**: New links resolve and improve routing; no supporting skill becomes an architecture-selection or general-purpose checklist; security guidance continues to require sanitized evidence for trust-boundary work.

- [ ] 3. Add compact Rust idiom and anti-pattern guidance

  **What**: Enrich Rust guidance with true gaps only. Cover borrowed argument types, newtypes for domain meaning, constructor/`Default`/builder choices, `mem::take`/`mem::replace`, RAII/`Drop` caveats, trait/closure strategy choices, unsafe containment, clone-to-satisfy-borrow-checker, `Deref` polymorphism, and OO pattern cargo-culting. Include concise architecture examples that keep domain/application code free of framework, async runtime, SQL, HTTP, or serialization details unless it is an adapter.

  **Files**: `skills/rust-engineering/SKILL.md`, `skills/rust-code-review/SKILL.md`, `skills/rust-testing-quality/SKILL.md`, `skills/rust-async-web/SKILL.md`, `skills/rust-persistence-sql/SKILL.md`

  **Acceptance**: Rust additions are compact and do not duplicate existing checklist items; review guidance can catch clone/Deref/pattern-cargo-cult issues; Rust testing guidance mentions documentation/rustdoc expectations where public APIs or examples are materially changed; architecture examples preserve ports/adapters and dependency direction.

- [ ] 4. Add compact Python idiom and anti-pattern guidance

  **What**: Enrich Python guidance with project-neutral idioms and red flags: `pyproject.toml`/package layout evidence, `pathlib`, context managers, type hints, `Protocol` for ports where useful, dataclasses with `default_factory`, specific exceptions with `raise ... from ...`, logging instead of production `print`, pytest fixtures/parametrization/fakes, and avoiding mutable defaults, bare `except`, `sys.path` hacks, over-Java design, brittle mocks, and unnecessary architecture layers. Include concise Clean/Onion/Hexagonal examples using Python modules, protocols, adapters, and manual dependency injection.

  **Files**: `skills/python-engineering/SKILL.md`

  **Acceptance**: Guidance remains a compact checklist; architecture examples keep domain/application behavior independent from frameworks, ORM rows, SDK models, request/response objects, and CLI parsing; docstring/comment expectations cover public APIs, invariants, error semantics, and non-obvious boundary decisions.

- [ ] 5. Add compact TypeScript/JavaScript idiom and anti-pattern guidance

  **What**: Enrich JS/TS guidance with strict TypeScript, explicit boundary types, `unknown` over `any`, discriminated unions and exhaustive checks, runtime validation for external data, primitive type annotations, awaited/returned promises, intentional concurrency, EventEmitter `error` handling, consistent ESM/CJS, and red flags such as `as any`, `@ts-ignore`, non-null assertion abuse, optional-everything DTOs, type assertions instead of validation, framework/ORM leakage, floating promises, and sleep-based tests. Include concise architecture examples using ports/adapters or use-case boundaries without importing framework/generated-client types into core logic.

  **Files**: `skills/javascript-typescript-engineering/SKILL.md`

  **Acceptance**: Guidance remains compact and repository-evidence-first; BDD/TDD examples emphasize observable behavior and focused tests; architecture examples preserve inward dependency direction; documentation/comment expectations cover exported APIs, boundary types, runtime validation assumptions, and non-obvious async/error behavior.

- [ ] 6. Verify language and support guidance

  **What**: Run focused first-party validation and inspect changed skill bodies for duplicate architecture dumps or broken links.

  **Acceptance**: `python3 tools/skills_manager.py validate --kind first-party` passes; changed skills contain no external reviewer invocation tasks; language additions remain compact enough to load as operational guidance.

## Verification

- [ ] `python3 tools/skills_manager.py validate --kind first-party`
- [ ] Targeted inspection confirms support protocols retain `user-invocable: false`.
- [ ] Targeted inspection confirms Rust, Python, and JS/TS guidance includes documentation/comment expectations for public APIs, invariants, boundaries, or non-obvious error/async behavior where relevant.
