---
description: Run a general or focused technical-debt audit through the Engineering Review Board
agent: engineering-review-board
subtask: false
---

Perform a technical-debt audit for:

$ARGUMENTS

Treat the argument as either repository-wide scope or a focused concern such as cyclomatic complexity, database debt, frontend state debt, test reliability, Project Fluent resources, concurrency, or documentation drift.

Load `technical-debt-audit` and `review-verification-protocol`.

Include `technical-debt-auditor` as the central specialist and select only additional specialists whose evidence could materially change prioritization or remediation.

Establish a concise Repository overview before reporting findings: primary languages, frameworks, package/build/test tooling, top-level architecture, key modules, entry points, and declared repository conventions. For a focused audit, keep the overview proportional to the requested scope.

Inspect code quality, dependency health, test confidence, architecture and design, and documentation or operational knowledge. Use repository evidence first. Request `technical-researcher` only when current versions, deprecations, maintenance status, advisories, or other authoritative external facts could materially change a dependency finding. Route active vulnerabilities to `security-critic` rather than treating them only as maintenance debt.

Do not invent numeric coverage percentages. Cite observed coverage output when available; otherwise use a qualitative module or boundary map and state its evidence. Do not assert that a dependency is outdated, deprecated, unmaintained, or vulnerable without current authoritative evidence. Name exact unrun validation when permissions or the environment prevent a safe repository-native check.

Return between 0 and 30 distinct, evidence-supported findings. Do not pad the
list and do not confuse active defects, acceptable trade-offs, or cosmetic
preferences with compounding technical debt. When no material debt is found,
say so explicitly and summarize the evidence examined.

For each finding include priority, severity, likelihood, confidence, classification, scope, concrete evidence, impact and debt interest, durable fix, validation, effort as Small / Medium / Large, expected benefit, and dependencies or sequencing. Keep severity, likelihood, confidence, and priority distinct.

Return the structured report in this order:

1. Repository overview
2. Evidence reviewed and limitations
3. Prioritized findings
4. Quick wins
5. Strategic blockers to future work, upgrades, operations, or scaling
6. Longer-term improvement program
7. Accepted trade-offs and positive evidence
8. Skipped validation and residual risk

Omit empty recommendation categories rather than padding them.

Do not modify the repository or a durable plan. Return findings for direct Lead
remediation when safe. When the human wants a durable remediation initiative,
recommend top-level `/create-plan`; `/start-plan <existing-plan-path>` is only a
separate human-chosen execution of an existing plan.

Conclude with:

- Healthy
- Improvement Program Recommended
- Material Remediation Required
