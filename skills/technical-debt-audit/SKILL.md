---
name: technical-debt-audit
description: Perform repository-wide or focused technical-debt audits covering maintainability, complexity, duplication, dependency health, testing gaps, architecture erosion, documentation drift, and remediation priorities. Use when the user asks to assess accumulated debt, modernization risk, change friction, quick wins, or blockers to future work or scaling. Do not use for an ordinary diff review, an active unexplained failure, implementation, or a vulnerability-only audit.
---

# Technical Debt Audit

Use this skill to identify accumulated decisions that repeatedly increase change
cost, defect risk, cognitive load, upgrade friction, or operational burden. A
technical-debt audit is a repository portfolio assessment, not a style pass or a
request to collect every local code smell.

Always apply
[`review-verification-protocol`](../review-verification-protocol/SKILL.md)
before reporting findings. Use
[`code-review`](../code-review/SKILL.md) instead when the primary artifact is a
diff, pull request, or completed change rather than accumulated repository debt.

## Boundaries

- Do not treat a current correctness bug, active vulnerability, isolated smell,
  old dependency, TODO, or long file as technical debt without evidence of
  recurring cost, risk, or blocked evolution.
- Route active unexplained failures to
  [`systematic-debugging`](../systematic-debugging/SKILL.md). Route
  vulnerability-only or supply-chain-only audits to the matching security skill.
- Remain read-only unless the user separately requests remediation and the
  active agent has edit authority. Loading this skill grants no permission,
  delegation, planning, or execution authority.
- Derive languages, frameworks, modules, entry points, conventions, commands,
  and validation lanes from the repository. Do not impose a preferred
  architecture or toolchain.
- Return zero findings when the evidence does not establish material debt. Never
  pad categories or convert cosmetic preferences into findings.

## Workflow

1. **Set the audit frame.**
   - Confirm whether the scope is repository-wide or focused.
   - Establish the repository's maintenance horizon, active areas, declared
     conventions, and the future work or scaling concerns that make debt costly.
   - Distinguish systemic debt from defects, security incidents, accepted
     trade-offs, speculative cleanup, and temporary work with an owner or exit
     condition.

2. **Build the Repository overview.**
   - Identify primary languages, frameworks, package managers, build tooling,
     test tooling, and deployment or runtime surfaces.
   - Map top-level folders, key modules, entry points, public boundaries, data
     stores, and important dependency direction.
   - Read applicable README, CONTRIBUTING, AGENTS, architecture records, and
     repository-native commands before judging convention drift.

3. **Collect evidence.**
   - Inspect source, tests, manifests, lockfiles, build and CI configuration,
     documentation, generated boundaries, TODO/FIXME markers, and relevant local
     history when available.
   - Prefer repository-native static analysis, coverage, dependency, and audit
     output when execution is authorized and safe. Otherwise name the exact
     unrun check and the uncertainty it leaves.
   - Search references and registrations before claiming code, exports,
     dependencies, routes, configuration, or compatibility paths are unused.

4. **Apply proportionate lenses.**
   - **Code quality:** duplicated concepts or behavior, complexity hotspots,
     deep nesting, oversized responsibilities, inconsistent async or error
     handling, stale commented-out blocks, obsolete abstractions, dead code,
     unused exports, and hard-to-change APIs.
   - **Dependency health:** unused direct dependencies, upgrade blockers,
     deprecated or unsupported packages, maintenance risk, stale toolchains,
     vulnerable resolved versions, and costly transitive or bootstrap surfaces.
   - **Testing:** risk coverage by module or boundary, critical untested paths,
     skipped or quarantined tests, flakiness, slow feedback, over-mocking,
     environment fragility, and missing architecture or contract guards.
   - **Architecture and design:** coupling, cycles, unclear ownership, leaky or
     missing abstractions, shared dumping grounds, convention violations, and
     boundary erosion that increases future migration cost.
   - **Documentation and operations:** stale setup guidance, missing public or
     extension-boundary documentation, undocumented non-obvious logic,
     configuration drift, fragile build/deploy knowledge, and absent recovery or
     upgrade guidance.

5. **Load focused companions only when evidence warrants them.**
   - Use [`architecture-review`](../architecture-review/SKILL.md) for structural
     boundaries or dependency direction.
   - Use [`testing-strategy`](../testing-strategy/SKILL.md) for suite confidence,
     flakiness, test levels, or module coverage.
   - Use language engineering or anti-pattern skills for ecosystem-specific
     code, package-manager, and static-analysis semantics.
   - Use
     [`dependency-supply-chain-review`](../dependency-supply-chain-review/SKILL.md),
     [`security-review`](../security-review/SKILL.md), and
     [`security-review-evidence`](../security-review-evidence/SKILL.md) for
     advisories, provenance, install scripts, vulnerable dependency paths, or
     other supply-chain trust questions.
   - Use [`documentation-engineering`](../documentation-engineering/SKILL.md)
     for documentation accuracy, public surfaces, examples, or setup journeys.
   - Use [`performance-review`](../performance-review/SKILL.md) only when
     workload or measurement evidence makes performance debt decision-relevant.

6. **Control evidence quality.**
   - Cite numeric coverage only from observed coverage output. Without it,
     provide a qualitative module or boundary map such as strong, partial, weak,
     or absent and cite the tests inspected.
   - Treat outdated, deprecated, unmaintained, or vulnerable dependency claims
     as current facts requiring authoritative evidence. A manifest or lockfile
     proves local versions, not current maintenance or advisory status.
   - Classify unverified tool-dependent concerns as hypotheses and list the
     validation needed to confirm them.

7. **Deduplicate and prioritize.**
   - Group symptoms under the smallest evidenced root cause.
   - Rank by severity, likelihood or recurrence, breadth, debt interest, cost of
     delay, remediation effort, migration risk, expected benefit, and sequencing
     dependencies.
   - Prefer durable corrections and recurrence guards over broad rewrites.

## Finding Standard

For every finding include:

- **ID and title**; **Priority**; **Severity**; **Likelihood**;
  **Confidence**; **Classification**
- **Scope and evidence**; **Impact and debt interest**; **Durable fix**
- **Effort:** Small / Medium / Large, with the main sizing assumption
- **Expected benefit**; **Dependencies and sequencing**; **Verification**

Keep severity, likelihood, confidence, and priority distinct: severity is the
consequence, likelihood is recurrence or realization risk, confidence is the
strength of evidence, and priority synthesizes those factors with cost of delay,
effort, and sequencing.

## Output

Return, in order:

1. **Repository overview**
2. **Evidence reviewed and limitations**
3. **Prioritized findings** using the Finding Standard
4. **Quick wins** — high expected benefit, small effort, and low migration risk
5. **Strategic blockers** — debt blocking future work, upgrades, operations, or
   scaling
6. **Longer-term improvement program** — larger sequenced remediation, if any
7. **Accepted trade-offs and positive evidence** worth preserving
8. **Skipped validation and residual risk**
9. **Conclusion:** Healthy / Improvement Program Recommended / Material
   Remediation Required

When no material debt is found, say so explicitly, retain the overview and
evidence sections, and omit empty recommendation categories.
