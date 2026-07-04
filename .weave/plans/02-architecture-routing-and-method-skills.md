# Architecture Routing and Method Skills

## TL;DR

> **Summary**: Rebalance architecture routing across Clean, Onion, and Hexagonal Architecture, then align BDD, DDD, TDD, brainstorming, and code-review guidance with that taxonomy.

> **Estimated Effort**: Medium

## Context

### Original Request

Implement the approved skill-system improvements after governance language is established in `01-governance-and-architecture-taxonomy.md`.

### Key Findings

- `skills/clean-architecture/SKILL.md` already has strong dependency-rule, use-case, interface-adapter, testing, and organization guidance; Onion coverage is brief.
- `skills/hexagonal-architecture/SKILL.md` is strong for ports/adapters, external actors, swappable infrastructure, and headless core tests.
- Several skills route Clean/Onion-style dependency-direction work only to `hexagonal-architecture`; known examples include `skills/code-review/SKILL.md` and `skills/rust-engineering/SKILL.md`.
- BDD, DDD, and TDD are well separated, but their architecture cross-references should use the same first-class Clean/Onion/Hexagonal vocabulary established by Plan 01.

## Objectives

### Core Objective

Make architecture and method skills route users to the right guidance without overloading Hexagonal Architecture as the default for all inward-dependency concerns.

### Deliverables

- Clean/Hexagonal relationship updates with Onion as first-class vocabulary.
- Method-skill routing that preserves BDD behavior language, DDD domain language, and TDD executable-test guidance.
- Review guidance that separates Clean, Onion, and Hexagonal architecture concerns.
- Focused stale-routing search and first-party validation.

### Definition of Done

- Clean Architecture remains the primary skill for policy/detail, use-case, interactor, presenter, DTO, and dependency-rule framing.
- Onion Architecture is described as domain-centered inward dependency framing.
- Hexagonal Architecture remains the primary skill for ports, adapters, external actors, and swappable infrastructure.
- BDD/DDD/TDD guidance remains proportional and does not force architecture ceremony.

### Guardrails (Must NOT)

- Do not create a standalone Onion skill in this plan.
- Do not remove valid Hexagonal references for ports/adapters or external actors.
- Do not turn method skills into architecture encyclopedias.
- Do not add external reviewer invocation tasks to any plan or skill.

## TODOs

- [ ] 1. Refresh Clean and Hexagonal relationship guidance

  **What**: Update frontmatter descriptions and relationship sections where needed so Clean, Onion, and Hexagonal have distinct routing cues. Keep Clean focused on policy/detail layers and use cases; Onion on domain-centered inward dependencies; Hexagonal on ports/adapters and external actors. Preserve source anchors and local links.

  **Files**: `skills/clean-architecture/SKILL.md`, `skills/hexagonal-architecture/SKILL.md`

  **Acceptance**: Onion has a visible first-class subsection or equivalent routing guidance; Clean and Hexagonal remain complementary rather than competing aliases; local links still resolve; no guidance suggests architecture for simple CRUD, prototypes, or one-off scripts.

- [ ] 2. Align BDD, DDD, TDD, and brainstorming routing

  **What**: Update method skills so BDD examples stay behavior-level, DDD guidance protects domain language and invariants, TDD guidance points to tests before or alongside implementation, and architecture links distinguish Clean/Onion/Hexagonal triggers. Keep Hexagonal examples only where ports/adapters or external actors matter.

  **Files**: `skills/behavior-driven-development/SKILL.md`, `skills/domain-driven-design/SKILL.md`, `skills/test-driven-development/SKILL.md`, `skills/brainstorming/SKILL.md`

  **Acceptance**: BDD, DDD, and TDD each link to Clean and/or Onion where use-case, domain-centered, or dependency-rule concerns are the trigger; Hexagonal links remain for adapter-boundary concerns; no scenarios or acceptance guidance mention internal implementation details unless they are public contract.

- [ ] 3. Update code-review architecture lenses

  **What**: Adjust `code-review` so review routing separates Clean policy/detail boundaries, Onion domain-centered inward dependencies, and Hexagonal ports/adapters. Preserve the existing evidence-first review format and security-sensitive review requirements.

  **Files**: `skills/code-review/SKILL.md`

  **Acceptance**: Architecture review guidance no longer sends generic Clean/Onion dependency direction only to `hexagonal-architecture`; `review-verification-protocol` remains required before findings; security-sensitive findings still require sanitized evidence through security review guidance.

- [ ] 4. Repair stale architecture cross-references

  **What**: Search the changed method/review/architecture skills for stale phrases such as `Clean/Onion-style` or text that routes generic inward dependencies only to Hexagonal. Replace stale wording with the Plan 01 taxonomy vocabulary.

  **Files**: `skills/clean-architecture/SKILL.md`, `skills/hexagonal-architecture/SKILL.md`, `skills/behavior-driven-development/SKILL.md`, `skills/domain-driven-design/SKILL.md`, `skills/test-driven-development/SKILL.md`, `skills/brainstorming/SKILL.md`, `skills/code-review/SKILL.md`

  **Acceptance**: Targeted search finds no stale generic Clean/Onion-to-Hexagonal-only routing; legitimate Hexagonal ports/adapters references remain; first-party validation passes.

## Verification

- [ ] `python3 tools/skills_manager.py validate --kind first-party`
- [ ] Targeted search confirms stale generic Clean/Onion dependency-direction routing no longer points only to `hexagonal-architecture`.
- [ ] Direct inspection confirms BDD, DDD, TDD, and review guidance remain concise and behavior/domain/test focused.
