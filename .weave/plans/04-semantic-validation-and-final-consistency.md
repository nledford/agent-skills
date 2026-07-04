# Semantic Validation and Final Consistency

## TL;DR

> **Summary**: Decide whether lightweight semantic warnings are worth implementing, add them only if low-noise, then run a final consistency and validation pass over the full skill-system update.

> **Estimated Effort**: Short

## Context

### Original Request

Complete the approved skill-system improvements after governance, routing, language, and support-skill updates from Plans 01-03.

### Key Findings

- `tools/skills_manager.py` already has `ValidationResult.warnings` and emits warnings without failing validation.
- `tests/test_skills_manager.py` already covers validation behavior and can cover warning-only checks if low-noise heuristics are added.
- Semantic validation should remain a manual-review aid or non-failing warning, not a hard gate, unless a future safety invariant justifies a hard failure.
- This plan depends on the final wording and cross-links created by the prior plans.

## Objectives

### Core Objective

Finish the plan set by either implementing narrow warning-only semantic checks or explicitly relying on the manual taxonomy checklist, then verify the repository is consistent.

### Deliverables

- A documented decision on semantic warnings: implement narrow checks or defer to manual review.
- Warning-only validator changes with tests, if low-noise.
- Final cross-reference, inventory, metadata, and validation pass across the changed skill system.

### Definition of Done

- Any semantic warnings are non-failing and covered by focused unit tests.
- If semantic warnings are deferred, the final handoff explains why the manual checklist is sufficient for now.
- First-party and full skill validation pass.
- No generated plan or skill content includes external reviewer invocation tasks as executable work.

### Guardrails (Must NOT)

- Do not make semantic-overlap warnings fail validation in this iteration.
- Do not implement noisy heuristics that duplicate reviewer judgment without useful signal.
- Do not add compatibility layers or broad rewrites outside the skill-system scope.
- Do not add external reviewer invocation tasks to any plan or verification section.

## TODOs

- [ ] 1. Characterize semantic warning candidates

  **What**: Inspect the final docs and skills from Plans 01-03 and decide whether low-noise warnings are feasible for support-protocol metadata drift, hidden support protocols without inbound references, or architecture mentions that route generic Clean/Onion dependency-direction language only to Hexagonal. Treat the taxonomy manual checklist as the fallback if heuristics are likely noisy.

  **Files**: `tools/skills_manager.py`, `tests/test_skills_manager.py`, `docs/skill-taxonomy.md`, `README.md`, `skills/review-verification-protocol/SKILL.md`, `skills/security-review-evidence/SKILL.md`, `skills/code-review/SKILL.md`, `skills/rust-engineering/SKILL.md`

  **Acceptance**: The execution notes identify which warning candidates were accepted or rejected and why; accepted candidates have clear inputs, expected warning text, and non-failing behavior; rejected candidates remain covered by the manual taxonomy checklist.

- [ ] 2. Implement or defer warning-only validation

  **What**: If TODO 1 finds low-noise candidates, implement warning-only checks in `tools/skills_manager.py` and focused tests in `tests/test_skills_manager.py`. Keep comments/docstrings limited to non-obvious heuristic intent and warning semantics. If candidates are rejected as noisy, do not edit the validator; instead verify that README/taxonomy manual guidance from Plan 01 covers the decision.

  **Files**: `tools/skills_manager.py`, `tests/test_skills_manager.py`, `README.md`, `docs/skill-taxonomy.md`

  **Acceptance**: If code changes are made, unit tests prove warnings are emitted without failing validation and warning wording avoids secrets or raw sensitive evidence; if no code changes are made, the final handoff states that semantic detection remains manual and cites the taxonomy checklist.

- [ ] 3. Repair stale references and metadata drift

  **What**: Search changed docs and skills for old plan assumptions, stale architecture routing, broken local links, duplicate guidance, stale inventory text, and support-protocol wording that conflicts with `user-invocable: false`. Fix only concrete inconsistencies.

  **Files**: `README.md`, `docs/skill-taxonomy.md`, `skills/clean-architecture/SKILL.md`, `skills/hexagonal-architecture/SKILL.md`, `skills/behavior-driven-development/SKILL.md`, `skills/domain-driven-design/SKILL.md`, `skills/test-driven-development/SKILL.md`, `skills/brainstorming/SKILL.md`, `skills/code-review/SKILL.md`, `skills/rust-engineering/SKILL.md`, `skills/rust-code-review/SKILL.md`, `skills/rust-testing-quality/SKILL.md`, `skills/rust-async-web/SKILL.md`, `skills/rust-persistence-sql/SKILL.md`, `skills/python-engineering/SKILL.md`, `skills/javascript-typescript-engineering/SKILL.md`, `skills/review-verification-protocol/SKILL.md`, `skills/security-review-evidence/SKILL.md`, `skills/security-review/SKILL.md`, `skills/context7-docs/SKILL.md`, `skills/random-data-identifiers/SKILL.md`, `skills/documentation-engineering/SKILL.md`, `skills/justfiles/SKILL.md`, `skills/playwright-e2e/SKILL.md`, `skills/postgresql-sql-engineering/SKILL.md`

  **Acceptance**: First-party inventory still matches actual first-party skills; support protocols remain hidden and referenced by user-facing skills; stale generic Clean/Onion-to-Hexagonal-only routing is gone; duplicate architecture/method text is minimized.

- [ ] 4. Run final focused verification

  **What**: Run syntax, unit, validation, and targeted text checks. Inspect command output before reporting success. Reserve broad checks for final validation because the skill-system changes span docs, skill metadata, links, and optional validator behavior.

  **Acceptance**: `python3 -m compileall -q tools tests` passes if validator or tests changed; `python3 -m unittest discover -s tests -v` passes if validator or tests changed; `python3 tools/skills_manager.py validate --kind first-party` passes; `python3 tools/skills_manager.py validate` passes; targeted text searches confirm no generated plan contains external reviewer invocation tasks.

## Verification

- [ ] `python3 -m compileall -q tools tests` — required if validator or tests changed because syntax coverage spans helper code and tests.
- [ ] `python3 -m unittest discover -s tests -v` — required if validator or tests changed because warning behavior belongs to the registry test suite.
- [ ] `python3 tools/skills_manager.py validate --kind first-party`
- [ ] `python3 tools/skills_manager.py validate`
- [ ] Targeted search confirms no generated `.weave/plans/*.md` file lists external reviewer invocation tasks as TODOs, Acceptance criteria, Definition of Done items, or verification items.
- [ ] Targeted search confirms stale generic Clean/Onion dependency-direction routing no longer points only to `hexagonal-architecture`.
