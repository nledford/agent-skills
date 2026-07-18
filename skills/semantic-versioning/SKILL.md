---
name: semantic-versioning
description: >-
  Determine, recommend, review, or apply Semantic Versioning changes. Use when
  deciding whether a release needs a patch, minor, or major bump; calculating
  the next version; auditing changes since the last release; handling 0.x,
  1.0.0, prerelease, deprecation, dependency, or mixed-change cases; or updating
  version metadata after the bump is chosen. Do not use as the primary skill for
  designing an API contract, changing checked-in release automation, creating
  Git tags, publishing artifacts, or making the final ship-or-hold decision.
---

# Semantic Versioning

Recommend the smallest honest Semantic Versioning bump supported by repository
evidence and, only when requested, apply it to the intended release unit. Follow
the project's documented version policy before generic convention. When the
project claims SemVer, keep that policy consistent with the official
[Semantic Versioning 2.0.0 specification](https://semver.org/).

SemVer requires a declared public API. For an application, the declared contract
may include documented user-visible behavior, service APIs, CLI flags and
output, configuration, persisted or exchanged formats, plugin interfaces,
automation hooks, or other surfaces consumers are told they can rely on. Do not
invent a stable contract silently when the repository has not defined one.

## Decision Rules

For a stable `X.Y.Z` release where `X > 0`, use the highest-impact change in the
release:

| Change impact | Minimum normal release | Version calculation |
| --- | --- | --- |
| Any backward-incompatible public-contract change | Major | `(X+1).0.0` |
| Backward-compatible public functionality or a deprecation | Minor | `X.(Y+1).0` |
| Backward-compatible bug fixes only | Patch | `X.Y.(Z+1)` |
| No released-contract change | No release required solely by SemVer | If publishing changed contents, choose a new version under explicit project policy |

Apply these rules to behavior, not labels. A commit named `fix` can require a
major bump if it breaks a supported consumer, while a large internal refactor
may require no SemVer bump. A minor release may include patch fixes, and a major
release may include minor and patch changes. Reset all less-significant fields
to zero when incrementing a more-significant field.

## Workflow

1. **Identify the release unit and policy.**
   - Determine whether the target is one application, package, crate, service,
     SDK, CLI, plugin, schema, image, or a fixed-version monorepo.
   - Read repository instructions, release documentation, package metadata,
     changelog conventions, compatibility promises, and automation that names
     the version source.
   - Confirm that the project uses SemVer. If it uses calendar versioning,
     marketing versions, an ecosystem-specific scheme, or an undocumented
     hybrid, report that boundary instead of forcing SemVer.

2. **Establish the current released baseline.**
   - Find the latest immutable released version from authoritative metadata,
     release records, or tags under repository policy.
   - Distinguish a release version such as `1.4.2` from a conventional Git tag
     name such as `v1.4.2`.
   - Do not treat an unreleased metadata edit, draft release, or arbitrary
     highest-looking tag as the baseline without evidence.

3. **Define the supported contract and consumers.**
   - Name the documented public surfaces, supported clients, compatibility
     window, and any independently versioned components.
   - Include observable defaults, errors, ordering, validation, file formats,
     protocols, configuration, and lifecycle behavior when the project promises
     them to consumers.
   - Separate private implementation details from de facto behavior on which
     supported consumers demonstrably rely.

4. **Inventory the complete release delta.**
   - Inspect the diff from the released baseline to the intended release commit,
     including source, tests, schemas, generated contracts, configuration,
     migrations, documentation, dependency changes, and release notes.
   - Use commit messages and labels only as navigation; never let Conventional
     Commit prefixes or changelog categories substitute for compatibility
     analysis.
   - In a monorepo, scope changes to each release unit and account for shared
     code or fixed-version policy explicitly.

5. **Classify every material change.**
   - Record the affected public surface, previous promise, new behavior,
     affected consumers, compatibility result, and candidate bump.
   - Treat removals, incompatible signature or schema changes, newly required
     inputs, narrowed accepted values, and observable semantic changes as major
     unless compatibility evidence proves otherwise.
   - Treat additive compatible functionality and marking public functionality
     deprecated as minor.
   - Treat a correction to documented behavior as patch only when existing
     compatibility obligations remain intact.

6. **Resolve special cases without hiding uncertainty.**
   - For `0.y.z`, follow the repository's documented initial-development policy;
     SemVer does not promise stability or impose the stable-major mapping. If no
     policy exists, state the proposed convention and lower confidence rather
     than silently assuming one. Recommend `1.0.0` when the project intentionally
     declares its public API stable.
   - For prereleases, choose the correct target core version first, then advance
     the repository's prerelease sequence, such as `2.0.0-rc.1` to
     `2.0.0-rc.2`. Do not use a prerelease suffix to disguise an incorrect major,
     minor, or patch target.
   - Treat build metadata as non-precedence information; changing only `+build`
     metadata does not create a higher SemVer version.
   - Classify dependency updates by their effect on the release contract: bug
     fix, compatible functionality, or incompatibility. Do not infer the bump
     from the dependency's own version change.
   - Classify security fixes by compatibility impact. Load the security skills
     before exposing sensitive advisory or vulnerability details in evidence or
     release communication.
   - Do not assume restoring intended behavior is harmless when supported users
     may rely on the defect. Report the conflict between documented and de facto
     contracts and request a product or maintainer decision when impact is
     material.

7. **Recommend the next version.**
   - Let the highest candidate bump win across the release unit.
   - State the current version, recommended version, dominant change, policy
     applied, confidence, and any assumption that could change the answer.
   - Distinguish a SemVer requirement from an optional project-policy choice.
     Internal refactors, docs-only work, or build-only changes do not require a
     SemVer release merely because a commit exists.

8. **Apply the bump only when requested.**
   - Inspect the working tree and preserve unrelated changes.
   - Identify the canonical version source plus generated mirrors, lockfiles,
     manifests, fixtures, and maintained documentation that repository tooling
     expects to stay synchronized.
   - Update only the selected release unit and use the matching language or
     package-workflow skill for ecosystem-specific mechanics.
   - Run repository-native version, metadata, lockfile, package-build, and
     focused test checks. Search authoritative maintained files for stale
     versions when the project does not provide a sync check.
   - Never reuse or overwrite a published version. Do not tag, commit, push,
     publish, or deploy unless the user separately authorizes that exact side
     effect.

## Routing

- Load [`api-design`](../api-design/SKILL.md) when the public API, SDK, CLI,
  webhook, event, or schema compatibility classification itself needs design or
  contract analysis. This skill aggregates those impacts into the release bump.
- Use [`ci-release-engineering`](../ci-release-engineering/SKILL.md) for
  checked-in workflows that derive versions, create releases, or publish
  artifacts; feed the chosen version policy into that automation.
- Use [`git-workflows`](../git-workflows/SKILL.md) for manual tag, branch, push,
  or recovery operations. A version recommendation does not authorize them.
- Use [`release-readiness`](../release-readiness/SKILL.md) for the final ship or
  hold decision after the version is chosen.
- Use [`documentation-engineering`](../documentation-engineering/SKILL.md) for
  release notes, migration guides, deprecation notices, and version-policy docs.
- Load
  [`dependency-supply-chain-review`](../dependency-supply-chain-review/SKILL.md)
  when a dependency change raises provenance, advisory, registry, lockfile, or
  package trust questions.
- Load [`security-review`](../security-review/SKILL.md) and
  [`security-review-evidence`](../security-review-evidence/SKILL.md) for
  security-sensitive compatibility evidence or disclosure-sensitive release
  notes.

## Output

Report:

1. Release unit, current released version, and version policy.
2. Recommended next version and confidence.
3. A concise change-classification table with the dominant bump identified.
4. Public contract and consumers considered.
5. Assumptions, ambiguous compatibility, and decisions still required.
6. When a bump was applied: files changed, synchronization checks, tests, and
   stale-version checks performed.
7. Tags, commits, publication, deployment, or validation not performed, plus
   residual risk.
