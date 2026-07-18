---
name: ci-release-engineering
description: Implement, change, review, or test checked-in CI and release provider configuration, including workflow triggers, job graphs, matrices, caches, artifacts, permissions, concurrency, environments, automated versioning, tags, releases, and package or binary publication. Do not use to choose a semantic patch, minor, or major bump from application changes; use semantic-versioning. Do not use for underlying language/test commands, Justfile wrappers, manual Git operations, final ship/hold decisions, unexplained CI failures, supply-chain-only or security-review-only audits, or production deployment infrastructure implementation.
---

# CI and Release Engineering

Use this skill for provider workflow and release automation configuration. Keep
the change scoped to the checked-in pipeline contract; inspect local conventions
and provider documentation before assuming syntax or behavior.

## Workflow

1. Inspect the changed workflow files, repository instructions, existing release
   process, referenced scripts, package metadata, and recent pipeline behavior.
   Identify the provider, event source, protected refs, intended release unit,
   and the commands the workflow invokes.
2. Define the execution contract before editing: triggers, path filters, event
   payload assumptions, ref and tag selection, job dependencies, matrix axes,
   service lifecycle, cache keys, artifact producers and consumers, and failure
   propagation.
3. Apply the smallest workflow change. Make job ordering and `needs` explicit;
   keep matrix expansion bounded; scope cache keys and artifact names to the
   inputs that affect them; prevent cancellation or concurrency rules from
   interrupting work that must finish.
4. For releases, make version source, tag/ref selection, publication target,
   immutability, rerun behavior, and recovery path explicit. A retry must not
   duplicate a release, overwrite an unintended artifact, or publish from a
   different commit.
5. Define environment and promotion gates deliberately. Separate build,
   verification, approval, and publication where the provider supports it; do
   not encode production deployment infrastructure in this skill's scope.
6. Verify with the provider's available workflow linting, schema checks, static
   contract tests, and safe local emulation. Treat local emulation as incomplete
   evidence for provider events, permissions, hosted runners, protected refs,
   environments, caches, and release APIs.
7. Run the narrowest repository-owned commands affected by the pipeline, then
   inspect the rendered workflow or a safe test run when available. Record what
   could only be verified remotely.

## Security and Supply Chain Guardrails

- Never print or persist secrets, tokens, credentials, private artifact URLs, or
  unredacted workflow logs.
- Load [`security-review`](../security-review/SKILL.md) and
  [`security-review-evidence`](../security-review-evidence/SKILL.md) for
  permissions, secrets, OIDC, untrusted events or forks, command injection,
  artifact trust, or privileged release behavior.
- Load
  [`dependency-supply-chain-review`](../dependency-supply-chain-review/SKILL.md)
  for action, image, tool, installer, package, binary, or provenance trust.
  Do not treat pinned syntax alone as sufficient provenance evidence.
- Use least privilege, explicit trust boundaries, and immutable inputs where the
  provider and repository policy allow. Avoid passing untrusted event fields to
  shells or privileged steps without validated structured handling.

## Routing

- [`semantic-versioning`](../semantic-versioning/SKILL.md) owns classifying the
  release delta and choosing a patch, minor, major, or prerelease version; this
  skill consumes that policy in checked-in automation.
- Language and test skills own the commands run by jobs and their application
  behavior; this skill owns the hosted workflow that selects and connects them.
- [`justfiles`](../justfiles/SKILL.md) owns local command wrappers and recipe
  design.
- [`container-engineering`](../container-engineering/SKILL.md) owns Dockerfile,
  OCI image, and Compose behavior that a pipeline invokes.
- [`context7-docs`](../context7-docs/SKILL.md) owns current CI or release-provider
  syntax and API documentation.
- [`git-workflows`](../git-workflows/SKILL.md) owns manual tags, branches, pushes,
  recovery, and other Git operations outside automation.
- [`systematic-debugging`](../systematic-debugging/SKILL.md) starts investigation
  of active unexplained CI failures before pipeline changes are proposed.
- [`release-readiness`](../release-readiness/SKILL.md) owns the final ship or hold
  decision, not this skill.
- For a requested review, load [`code-review`](../code-review/SKILL.md) and
  [`review-verification-protocol`](../review-verification-protocol/SKILL.md).
- Exclude production deployment infrastructure implementation; route platform,
  runtime, and deployment-system changes to the relevant infrastructure skill or
  repository workflow.

## Validation and Reporting

- Validate changed configuration with the strongest safe provider-native and
  repository-owned checks available. Confirm trigger coverage, ref selection,
  dependency graph, matrix behavior, cache/artifact boundaries, permission scope,
  concurrency, promotion gates, and release idempotency.
- Report the files changed, workflow behavior changed, checks run and results,
  remote-only or skipped validation, recovery assumptions, and residual risk.
