---
name: code-review
description: Perform repository-local code reviews. Use for requested audits, pull-request-style reviews, final focused review after implementation, or changes that affect behavior, APIs, domain boundaries, tests, security, workflows, dependencies, CI, documentation, or agent instructions.
---

# Code Review

Use this skill to review repository changes for correctness, maintainability,
security, reliability, domain integrity, test quality, and operational fit. A
review is not a style pass; report only issues with evidence and impact.

Before reporting findings, apply
[`review-verification-protocol`](../review-verification-protocol/SKILL.md).
Load specialist skills only when they match the changed surface. For Rust code,
pair this skill with [`rust-code-review`](../rust-code-review/SKILL.md). For
ports/adapters and external actors, pair it with
[`hexagonal-architecture`](../hexagonal-architecture/SKILL.md). For use-case,
interactor, presenter, or interface-adapter boundaries, pair it with
[`clean-architecture`](../clean-architecture/SKILL.md). For domain/application
rings, pair it with [`onion-architecture`](../onion-architecture/SKILL.md).

## Use When

- The user asks for a review, audit, PR review, risk pass, or final check.
- You made meaningful repository changes and need a focused review before
  handoff.
- The diff touches production behavior, public interfaces, data contracts,
  architecture, tests, security, dependencies, build, CI, release, docs, or agent
  instructions.
- A prior review needs re-checking after fixes.

## Skip Only When

Skip review only for changes that are clearly low risk, such as typo-only,
formatting-only, or generated mechanical updates with no behavior, workflow,
security, contract, or instruction impact. If skipped, say why and still report
the validation that ran.

Never skip review for security-sensitive work, API/schema changes, domain model
changes, test weakening, dependency/toolchain changes, CI changes, or work where
impact is uncertain.

## Review Workflow

1. **Understand intent.**
   - Identify the request, issue, acceptance criteria, regression, or plan step.
   - Separate intended behavior from implementation choices.

2. **Map affected surfaces.**
   - Name touched modules, domain concepts, public APIs, storage, workflows,
     generated artifacts, docs, commands, CI, and security boundaries.

3. **Choose lenses.**
   - Use this general review lens first.
   - Add narrow specialist skills for Rust, SQL/PostgreSQL/SQLite, Python,
     JavaScript/TypeScript, browser tests, security review, documentation,
     Justfiles, or other surfaces only when they apply.

4. **Review tests and behavior.**
   - Check whether tests or examples specify observable behavior and meaningful
     edge cases.
   - Confirm tests are not brittle implementation snapshots unless the
     implementation detail is the contract.

5. **Review implementation.**
   - Verify the change satisfies intent, preserves invariants, keeps
     responsibilities in the right place, and avoids avoidable coupling.

6. **Review failure modes.**
   - Check validation, authorization, error mapping, retries, cleanup,
     cancellation, transactions, resource limits, logging, metrics, and rollback
     where relevant.

7. **Review contracts and operations.**
   - Check docs, recipes, environment examples, generated artifacts, migrations,
     CI, release surfaces, and runbooks when changed behavior affects operators,
     developers, users, or agents.

8. **Confirm validation.**
   - Required checks should pass, or failures must be clearly unrelated,
     environmental, pre-existing, or intentionally out of scope.

9. **Report verified findings only.**
   - Omit speculation and style preferences.
   - Downgrade uncertain issues to questions when evidence is incomplete.

## BDD, DDD, TDD, and Architecture Lenses

- **BDD:** User-visible behavior should be described as observable outcomes,
  scenarios, acceptance criteria, or behavior-oriented tests.
- **DDD:** Domain names, boundaries, responsibilities, policies, and invariants
  should match the repository language and avoid leaking infrastructure inward.
- **TDD:** New behavior and bug fixes should have meaningful tests where
  practical. Refactors should preserve behavior through existing or added safety
  nets.
- **Hexagonal Architecture:** Domain/application core code should not depend on
  framework, ORM, SDK, transport, or persistence details unless the repository
  deliberately accepts that coupling. Ports and adapters should protect real
  boundaries, not add pass-through indirection.
- **Clean Architecture:** Use cases, interactors, presenters, and interface
  adapters should preserve inward dependencies and keep business policy out of
  framework, database, UI, or SDK details.
- **Onion Architecture:** Domain and application rings should remain independent
  from infrastructure. Outer adapters should translate into domain/application
  types instead of shaping the core API.

## Finding Severity

- **Blocking:** Must be fixed before merge or handoff: security vulnerability,
  data corruption, compile failure, broken required checks, severe regression, or
  unsupported public contract break.
- **High:** Significant correctness, security, reliability, maintainability,
  architectural, domain, persistence, or serialization risk.
- **Medium:** Meaningful edge-case gap, weak test for important behavior,
  unclear contract, avoidable coupling, missing changed-behavior docs, or
  operational drift.
- **Low:** Local clarity, minor docs/test improvement, or low-risk cleanup.
- **Question:** A narrow clarification is needed before judging acceptability.
- **Praise:** Optional, specific positive feedback worth preserving.

## Finding Format

Put findings first, ordered by severity:

```text
[Severity] path/to/file.ext:123 - Short issue title
Problem: What is wrong, tied to the affected behavior or code.
Why it matters: Concrete correctness, domain, security, test, workflow, or
maintainability impact.
Recommended fix: Specific next step.
Evidence: File/line, command output, search result, or verified absence.
```

If there are no verified findings, say so directly and name the review scope,
validation performed, and residual risks.

## Review Checklist

- Correctness and observable behavior match the request.
- Domain names, boundaries, ownership, and invariants remain clear.
- Tests cover the important success path, failure path, edge case, or regression.
- Public APIs, schemas, serialization, docs, and generated contracts are
  deliberate and synchronized.
- Error handling, retries, cleanup, transactions, cancellation, and resource
  limits fit the affected workflow.
- Security and privacy boundaries are preserved and evidence is sanitized.
- Performance, scalability, concurrency, and resource usage are acceptable for
  the touched path.
- Logs, metrics, traces, and user/operator messages are useful without exposing
  secrets.
- Documentation, recipes, CI, release, and agent guidance match changed behavior.
- Formatting, linting, type checking, tests, and required validation are clean or
  accurately reported.

## Reporting Rules

- Lead with findings. Keep summaries secondary.
- Do not report unverified speculation, taste preferences, or unrelated future
  work as defects.
- Do not ask for broad rewrites when a targeted fix addresses the issue.
- For security-sensitive findings, follow repository policy and avoid exposing
  secrets, private paths, raw tokens, cookies, credentialed URLs, or sensitive
  payloads.
- For re-reviews, verify previous fixes only unless the user asks for a fresh
  full review.
