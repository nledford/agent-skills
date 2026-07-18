---
name: release-readiness
description: Assess merge and release readiness across tests, docs, migrations, rollout, rollback, operations, and cross-functional risk. Use for a final ship or hold decision; do not use to choose a semantic patch, minor, or major version, or as the primary implementation, code-review, or deployment workflow.
---

# Release Readiness Skill

Use this skill after implementation and focused reviews are substantially
complete, when the remaining question is whether the change is safe to merge or
release. Load the relevant review skill when security, performance,
accessibility, data, or architecture evidence is incomplete.

Apply
[`review-verification-protocol`](../review-verification-protocol/SKILL.md) to
every blocker, risk finding, and ship-or-hold rationale.

Do not use it to replace implementation, a first code review, or a repository's
deployment runbook. Use
[`semantic-versioning`](../semantic-versioning/SKILL.md) to classify the release
delta and choose or apply a patch, minor, major, or prerelease version;
use
[`ci-release-engineering`](../ci-release-engineering/SKILL.md) to create or
change checked-in CI and release automation, and
[`container-engineering`](../container-engineering/SKILL.md) for Docker/OCI or
Compose implementation.

## Workflow

1. Confirm scope, acceptance criteria, dependency changes, and the exact release
   unit under review.
2. Verify test, build, documentation, configuration, migration, compatibility,
   and release-note evidence.
3. Check rollout, rollback, data recovery, observability, support, and operator
   readiness.
4. Confirm that security, performance, accessibility, architecture, and domain
   risks have either been reviewed or explicitly accepted by the right owner.
5. Record skipped checks, assumptions, blockers, follow-ups, and residual risk.
   Decide: Ship, Ship With Follow-ups, Hold for Fixes, or Do Not Ship.

## Output

Return the decision, evidence, blockers, follow-ups, rollback considerations,
skipped validation, residual risk, and a final release checklist.
