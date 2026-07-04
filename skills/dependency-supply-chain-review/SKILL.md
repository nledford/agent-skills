---
name: dependency-supply-chain-review
description: Dependency and software supply-chain security review. Use for dependency audits, SBOM/SCA output, CVE/GHSA advisories, package or binary provenance, registry trust, manifests, lockfiles, checksums/signatures, install/postinstall scripts, vendored/generated code, transitive dependency risk, CI actions, container or base-image pinning, or package-manager security policy. Do not use for routine package-manager workflow, language-specific dependency implementation, or third-party API docs without a supply-chain risk question.
---

# Dependency Supply-Chain Review

Use this skill to review dependency, package, binary, and build-bootstrap risk
without executing untrusted code or leaking private dependency details.

Pair with [`security-review`](../security-review/SKILL.md) for the broader
security audit and [`security-review-evidence`](../security-review-evidence/SKILL.md)
for sanitized evidence. Use [`context7-docs`](../context7-docs/SKILL.md) only for
current package-manager, library, scanner, or API documentation; Context7 output
is not provenance, trust, or exploitability evidence.

## Use When

- Reviewing dependency bumps, new dependencies, removals, SBOM/SCA output,
  vulnerability advisories, or transitive dependency changes.
- Manifests, lockfiles, package-manager config, install scripts, postinstall
  hooks, build scripts, generated clients, vendored source, or checked-in
  binaries change.
- CI bootstrap dependencies change: GitHub Actions, setup actions, shell
  installers, curl-piped commands, container/base images, tool-cache downloads,
  compiler/toolchain pins, or package-manager setup steps.
- Checksums, signatures, SLSA/provenance attestations, trusted publishing,
  registry configuration, mirrors, private registries, or license/security policy
  fit affect acceptance.

Do not use this skill for ordinary version selection, API integration, or package
manager mechanics with no trust or security question. Use the relevant language
skill for implementation details.

## Workflow

1. Inspect local policy first: `SECURITY.md`, dependency policy, license policy,
   package-manager config, lockfiles, CI, Docker/container files, release docs,
   and existing update conventions. Do not read or print credential files.
2. Identify the changed supply-chain surface: direct dependency, transitive
   dependency, lockfile-only churn, script/hook, binary, vendored/generated code,
   CI action, installer command, registry, container image, or toolchain pin.
3. Prefer static inspection before execution. Read manifests, diffs, metadata,
   changelogs, package scripts, workflow YAML, checksums, signatures, and
   provenance attestations. Do not run install hooks, new binaries, curl-piped
   installers, unpinned actions, or generated code unless the repository already
   trusts that command path and the user asked for execution.
4. Compare declared intent with actual impact: dependency tree movement,
   maintainer/source changes, new transitive packages, native extensions,
   lifecycle scripts, network/file/process access, optional features, and
   generated or vendored diffs.
5. Check available trust signals: pinned versions or digests, lockfile integrity,
   checksums, signatures, provenance/attestations, trusted-publishing metadata,
   release tags, source-to-package consistency, license compatibility, and
   repository security policy fit. Record when a signal is unavailable.
6. Triage advisories and scanner output with local context before recommending a
   change. Do not paste raw private package names, registry hosts, exploit
   payloads, customer identifiers, or sensitive advisory details into reports.
7. Choose the smallest safe remediation: upgrade, pin/digest, replace, remove,
   disable feature, patch, vendor with review notes, add allowlist/exception with
   expiry, or defer with documented risk owner and monitoring.
8. Verify through safe repository-owned checks where practical: lockfile
   validation, audit commands already used by the project, tests, build metadata
   checks, signature/provenance verification, or CI dry-run output. Report any
   skipped check and residual risk.

## Advisory Triage

For CVE, GHSA, OSV, vendor, SCA, or package-manager advisory output, record:

- **Affected versions:** installed version, fixed version, dependency path, direct
  vs transitive status, and whether the local lockfile actually includes the
  vulnerable range.
- **Local exploitability:** reachable code path, runtime environment, enabled
  features, exposed inputs, privileges, deployment surface, compensating controls,
  and whether the vulnerable package is dev-only, build-only, optional, or
  production-loaded.
- **Severity and source trust:** advisory source, package ecosystem, publication
  date, confidence, CVSS/vendor severity when available, known exploit status,
  and whether the source is authoritative for the package.
- **Remediation choices:** upgrade path, breaking-change risk, patch/backport,
  dependency override, package replacement/removal, mitigation, temporary
  exception, owner, and review/expiry date.
- **Redacted evidence:** sanitized advisory ID, ecosystem, affected range,
  dependency path class, command/source that produced the finding, and redacted
  proof of remediation. Avoid copying private package names or sensitive advisory
  details unless they are necessary and permitted by repository policy.

## Surface Checklist

- **Manifests and lockfiles:** dependency purpose is justified; lockfile churn is
  expected; integrity fields and package-manager versions match the repository.
- **Scripts and installers:** lifecycle scripts, shell installers, one-off CLIs,
  postinstall hooks, build scripts, and code generators are reviewed as code
  execution surfaces before running.
- **Transitives and features:** new transitive packages, native modules, optional
  features, proc macros/plugins, and build dependencies have a need and a review
  path.
- **Binaries and vendored/generated code:** source, version, digest/signature,
  license, regeneration command, and diff scope are documented; generated output
  is not hand-edited unless policy allows it.
- **CI and bootstrap:** GitHub Actions, reusable workflows, setup actions,
  containers, base images, tool downloads, and curl-piped commands are pinned to
  immutable versions or digests where practical.
- **Policy fit:** license, maintenance status, registry trust, private registry
  handling, security support, and exception process match local policy.

## Routing

- Load [`javascript-typescript-engineering`](../javascript-typescript-engineering/SKILL.md)
  for `package.json`, JS/TS lockfiles, package scripts, npm/pnpm/Yarn/Bun/Deno,
  bundlers, or workspace mechanics.
- Load [`python-engineering`](../python-engineering/SKILL.md) for `pyproject.toml`,
  `uv.lock`, requirements files, Python packaging, dependency groups, or Python
  build hooks.
- Load [`rust-engineering`](../rust-engineering/SKILL.md) for `Cargo.toml`,
  `Cargo.lock`, features, build scripts, proc macros, native crates, or Cargo
  tree review; add [`rust-persistence-sql`](../rust-persistence-sql/SKILL.md)
  when database adapter crates or SQL tooling change.
- Load [`justfiles`](../justfiles/SKILL.md) when package-manager or installer
  commands are encoded in Just recipes.
- Load database, testing, documentation, or architecture skills only when the
  dependency change also affects those surfaces.

## Evidence and Reporting

- Keep raw SBOMs, scanner output, audit logs, package metadata, lockfile diffs,
  private registry URLs, local cache paths, and exploit details local unless
  repository policy permits sanitized retention.
- Report only sanitized evidence: ecosystem, public advisory IDs, version ranges,
  dependency path class, trust signals checked, commands run, pass/fail state,
  remediation decision, and residual risk.
- Use placeholders such as `<private-package>`, `<private-registry>`,
  `<internal-advisory>`, `<redacted-path>`, or `<redacted-payload>` when details
  are sensitive.
- State clearly when confidence is limited because provenance, signatures,
  checksums, advisory details, or repository policy were unavailable.

## Anti-Patterns

- Running new install scripts, postinstall hooks, unpinned binaries, or curl-piped
  commands as the first step of review.
- Treating scanner severity as final without checking affected versions and local
  reachability.
- Trusting Context7 docs, README popularity, or package download counts as
  provenance evidence.
- Copying private package names, registry hosts, exploit payloads, or raw scanner
  logs into reviews.
- Approving lockfile churn, vendored code, generated code, or binary blobs without
  source, purpose, and verification notes.
