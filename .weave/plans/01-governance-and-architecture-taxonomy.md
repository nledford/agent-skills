# Governance and Architecture Taxonomy

## TL;DR

> **Summary**: Update the repository-level skill governance docs so Clean, Onion, and Hexagonal Architecture are first-class routing vocabulary, support protocols are documented, and future semantic-overlap checks have a clear manual baseline.

> **Estimated Effort**: Short

## Context

### Original Request

Implement the approved skill-system improvement plan. The user decided that Onion Architecture should be first-class vocabulary; Python and TypeScript/JavaScript may eventually split into granular skills; standalone pattern skills are not urgent; semantic issue detection should be warning-first if useful; and language skills may include concise architecture examples.

### Key Findings

- `README.md` documents skill directory structure, first-party/third-party skill types, and validation checks, but does not yet explain support protocols or semantic-overlap review conventions.
- `docs/skill-taxonomy.md` already contains skill quality guidance and BDD/DDD/TDD/Clean/Hexagonal composition, but Onion is not presented as first-class architecture-selection vocabulary.
- Support protocol skills already exist as first-party hidden skills: `skills/review-verification-protocol/SKILL.md` and `skills/security-review-evidence/SKILL.md` use `user-invocable: false`.
- Later plans depend on the labels and routing language established here.

## Objectives

### Core Objective

Make repository-level skill governance explicit enough that later skill edits can use consistent architecture, method, support-protocol, and semantic-overlap vocabulary.

### Deliverables

- README guidance for support protocols and repository validation conventions.
- Taxonomy decision guidance for Clean Architecture, Onion Architecture, Hexagonal Architecture, BDD, DDD, TDD, hybrids, and no-formal-architecture cases.
- Manual semantic-overlap review guidance that can later be mirrored by warning-only validation if low-noise.
- Future split triggers for broad Python and TypeScript/JavaScript skills.

### Definition of Done

- README and taxonomy language match the approved decisions without adding new skills.
- Onion Architecture is visible as first-class vocabulary, not only a parenthetical Clean/Hexagonal footnote.
- Support protocols remain first-party and hidden; no plan or doc suggests making them user-invocable.
- Local Markdown links and first-party taxonomy inventory still validate.

### Guardrails (Must NOT)

- Do not create, rename, split, or delete skills in this plan.
- Do not edit skill bodies except through later plans.
- Do not make semantic-overlap checks hard-failing in governance docs.
- Do not add external reviewer invocation tasks to this or any plan.

## TODOs

- [ ] 1. Document support protocols in README

  **What**: Add concise README guidance explaining that first-party skills may be user-facing or support protocols, that support protocols use `user-invocable: false`, and that support protocols remain listed in the first-party taxonomy inventory. Mention that support protocols must be referenced by user-facing skills that require them.

  **Files**: `README.md`

  **Acceptance**: README distinguishes first-party, third-party, and support-protocol conventions without duplicating the full taxonomy; `review-verification-protocol` and `security-review-evidence` remain described as first-party support protocols.

- [ ] 2. Add first-class architecture selection guidance

  **What**: Update `docs/skill-taxonomy.md` with a concise architecture decision matrix or equivalent section comparing Clean Architecture, Onion Architecture, Hexagonal Architecture, hybrid use, and no formal architecture. Use repository vocabulary: Clean for policy/detail and use-case boundaries, Onion for domain-centered inward dependency framing, Hexagonal for ports/adapters around external actors.

  **Files**: `docs/skill-taxonomy.md`

  **Acceptance**: The taxonomy gives agents behavior-oriented routing criteria for selecting Clean, Onion, Hexagonal, hybrid, or no formal architecture; it preserves the existing anti-ceremony guidance for simple CRUD, prototypes, and one-off scripts; it does not duplicate full skill bodies.

- [ ] 3. Clarify BDD, DDD, and TDD composition

  **What**: Refine the taxonomy method-selection section with concrete composition examples for BDD, DDD, TDD, Clean, Onion, and Hexagonal. Keep BDD behavior examples before implementation details, DDD domain language and invariants where relevant, and TDD tests before or alongside implementation where practical.

  **Files**: `docs/skill-taxonomy.md`

  **Acceptance**: Method guidance explains when to combine BDD+DDD, BDD+TDD, DDD+TDD, DDD+Clean/Onion/Hexagonal, and when to use none; examples are concise and do not create a competing meta-skill.

- [ ] 4. Add future split and semantic-overlap review guidance

  **What**: Add taxonomy guidance that broad Python and TypeScript/JavaScript skills may split later when activation boundaries become distinct, while current pattern guidance should remain compact because pattern mistakes are not frequent. Add a manual semantic-overlap checklist covering duplicate skill triggers, over-routing Hexagonal for Clean/Onion work, hidden support-protocol drift, and stale cross-links.

  **Files**: `docs/skill-taxonomy.md`

  **Acceptance**: The taxonomy tells maintainers what evidence justifies future splits; semantic-overlap review remains manual/warning-oriented; no new skill names are added to the current inventory unless files actually exist.

- [ ] 5. Verify governance docs

  **What**: Run focused validation after the README and taxonomy edits. Inspect failures before proceeding to later plans.

  **Acceptance**: `python3 tools/skills_manager.py validate --kind first-party` passes; if validation fails, the failure is fixed before Plan 02 starts.

## Verification

- [ ] `python3 tools/skills_manager.py validate --kind first-party`
- [ ] Targeted inspection confirms `README.md` and `docs/skill-taxonomy.md` contain no external reviewer invocation tasks.
