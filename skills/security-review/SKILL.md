---
name: security-review
description: Security review and audit guidance for concrete code, config, docs, and command-surface changes. Use when implemented changes touch authentication, authorization, crypto, certificates, tokens, signatures, secrets, passwords, sessions, session cookies, CORS, CSP, CSRF, OAuth/OIDC/SAML, redirect/callback handling, input validation, file paths, command execution, or other trust boundaries. Pair with code-review for review findings; use threat-modeling for design-time boundary analysis and dependency-supply-chain-review for supply-chain-specific review.
---

# Security Review

Use this skill to review implemented security-sensitive changes without exposing
secrets or overstating unverified risk. It is the broad concrete-change audit
skill: pair it with [`code-review`](../code-review/SKILL.md) for review finding
format and with
[`security-review-evidence`](../security-review-evidence/SKILL.md) for sanitized
evidence handling.

## Use When

- Implemented authentication, authorization, permissions, roles, tenancy,
  sessions, session cookies, MFA, recovery flows, or invite flows change.
- Cryptography, certificates, TLS, signatures, hashes, password handling, tokens,
  API keys, OAuth/OIDC/SAML, redirect/callback handling, webhooks, nonces, or key
  rotation change.
- Input crosses a trust boundary: HTTP, forms, GraphQL/RPC, CLI args,
  environment variables, files, uploads/downloads, archives, plugins, extensions,
  templates, Markdown/HTML, SQL, shell commands, SSR, browser storage, or network
  calls.
- CORS, CSP, CSRF, SSRF, path traversal, deserialization, sandboxing, logging,
  telemetry, or secret redaction is relevant.
- Dependency, supply-chain, provenance, SBOM, advisory, install-script, or
  lockfile evidence is part of a broader concrete security audit.

Do not use this skill as a generic style review for code with no trust boundary,
secret, identity, privilege, untrusted input, or security control. Use ordinary
code review instead. Do not use it as the primary workflow for design-time
security modeling or supply-chain-only review; route those surfaces as below.

## Routing and Handoffs

- Use [`threat-modeling`](../threat-modeling/SKILL.md) for preparatory design
  work: actors, assets, data flows, trust boundaries, STRIDE/abuse cases,
  mitigations, security requirements, assumptions, and residual risk before
  controls are implemented. Return to this skill when implemented controls or
  reportable findings need evidence.
- Use [`dependency-supply-chain-review`](../dependency-supply-chain-review/SKILL.md)
  when the primary question is dependency, SBOM/SCA, CVE/GHSA, package or binary
  provenance, registry trust, lockfile churn, install/postinstall hooks,
  generated or vendored code, CI actions, containers, base images, checksums, or
  signatures. Bring confirmed supply-chain risk back here only when it affects a
  wider concrete security audit.
- For OAuth/OIDC/SAML, identity-provider, session-cookie, CSRF, redirect URI,
  token lifetime, scope/audience, signature, or key-rotation changes, inspect
  repository policy first and then current provider/protocol documentation before
  judging compliance. Use [`context7-docs`](../context7-docs/SKILL.md) for
  provider SDKs, libraries, CLIs, and APIs when current docs matter; cite only
  sanitized, review-relevant facts instead of turning the review into a protocol
  tutorial.
- Use [`security-review-evidence`](../security-review-evidence/SKILL.md) whenever
  raw artifacts, exploit proof, browser state, auth traces, scanner output, or
  other sensitive evidence must be captured, sanitized, retained, or cleaned up.

## Workflow

1. Inspect repository policy first: `SECURITY.md`, `AGENTS.md`, threat models,
   auth docs, deployment docs, CI security jobs, dependency policy, and review
   templates. For auth protocols or providers, also inspect current
   provider/protocol docs relevant to the changed repository behavior.
2. Scope the implemented boundary: actors, assets, entry points, trust levels,
   data classes, permissions, storage, external services, and attacker-controlled
   inputs. If this becomes design-time modeling, route to `threat-modeling`.
3. State the intended security property before judging code: who may do what,
   which data must remain confidential/integral, what must be authenticated,
   what must be rate-limited, and what must be auditable.
4. Read the full path: caller, middleware, validation, business rule, storage,
   logging, error handling, tests, config, docs, and deployment assumptions.
5. Verify controls with tests, policies, config checks, dependency or protocol
   evidence from the routed specialist skill, or concrete code evidence. Do not
   report speculative vulnerabilities.
6. Keep raw browser and security artifacts local and ignored by default. Share or
   retain only sanitized artifacts when repository policy or explicit approval
   allows it, and capture the security evidence for that exception.
7. Sanitize evidence and clean temporary security artifacts. Never print secrets,
   cookies, tokens, private keys, raw credentialed URLs, `.env` contents, or
   private host paths.
8. Report findings through the code-review format with severity calibrated to
   exploitability, blast radius, data sensitivity, and existing mitigations.

## Review Checklist

- **Authn/authz:** identity is established by trusted middleware; authorization is
  checked server-side at the object/action boundary; tenant and role checks cannot
  be bypassed by direct IDs, cache hits, background jobs, or client-only guards.
- **Auth protocols and sessions:** OAuth/OIDC/SAML, identity-provider, and
  session-cookie changes follow repository policy and current provider/protocol
  docs; redirect/callback URIs are exact and environment-appropriate; CSRF,
  state/nonce, replay, and request-correlation controls are not disabled; token
  lifetimes, refresh behavior, scopes, audiences, issuers, subjects, tenant
  claims, signature algorithms, JWKS/certificates, and key rotation expectations
  are verified from local config, code, tests, and sanitized docs evidence.
- **Secrets and sessions:** tokens, cookies, credentials, key material, and
  session IDs are generated with secure randomness, scoped, rotated where needed,
  revoked or destroyed when no longer valid, stored safely, redacted from logs,
  kept out of backups and artifacts, and cleaned up after fixture/test use.
- **Crypto:** use vetted libraries and current repository conventions; do not
  invent algorithms, modes, padding, key derivation, signing formats, or random
  sources. Compare signatures and tokens with constant-time APIs when relevant.
- **Input validation:** untrusted input is parsed, bounded, canonicalized, and
  validated before use. Validation errors are safe externally and actionable
  internally.
- **Injection and execution:** SQL, shell, paths, templates, HTML, Markdown,
  archive extraction, plugin loading, and command arguments use structured APIs or
  strict allowlists rather than string concatenation.
- **Web controls:** CORS, CSP, CSRF, cookies, redirects, SSR, browser storage,
  uploads/downloads, and cache headers fit the threat model and deployment origin
  layout.
- **Data and logs:** sensitive data is classified, minimized, encrypted where
  required, retained intentionally, and excluded from telemetry, screenshots,
  traces, videos, network dumps, downloads, reports, exceptions, and test
  artifacts.
- **Dependencies and supply chain:** new packages, binaries, scripts, generated
  code, lockfile changes, and install hooks route through
  [`dependency-supply-chain-review`](../dependency-supply-chain-review/SKILL.md)
  for provenance, checksum/signature, scanner, and install-script evidence before
  this skill reports broader security impact.
- **Auth evidence boundaries:** never paste raw cookies, authorization codes,
  access/ID/refresh tokens, SAML assertions, CSRF/session values, private keys,
  signed payloads, credentialed callback URLs, private tenant/user identifiers, or
  provider console screenshots. Prefer redacted claim names, TTLs, scope/audience
  names, redirect URI patterns, key IDs/thumbprints, test names, config paths, and
  current-doc citations allowed by repository policy.
- **Security artifacts:** traces, screenshots, videos, storage state,
  HAR/network dumps, downloads, reports, logs, dependency audit output,
  temporary databases, export files, and reproduced exploit payloads stay local
  and ignored by default; sanitized copies are retained or shared only under
  documented policy or explicit approval with security-review evidence.

## Language and Surface Prompts

- **Python:** check subprocess use, path handling, deserialization, template
  rendering, dependency changes, async blocking at boundaries, and exception logs.
- **JavaScript/TypeScript:** check XSS, SSR, package scripts, HTML/Markdown
  rendering, cookies, browser storage, CORS/CSRF, and dependency install scripts.
- **Rust:** check unsafe boundaries, `unwrap`/panic at trust boundaries, async
  task leakage, path handling, crypto/random crates, SQLx/SeaQuery binding, and
  error-to-response mapping.
- **SQL/PostgreSQL/SQLite:** check injection, privileges, RLS/policies, least
  privilege, migration data exposure, constraints, and auditability.
- **Browser tests/artifacts:** use raw screenshots, traces, videos, storage
  state, HAR/network dumps, downloads, reports, credentialed URLs, cookies,
  CSRF/session values, or live data only for local ignored debugging. Retain or
  share only sanitized derivatives when documented policy or explicit approval
  permits it, and include [`security-review-evidence`](../security-review-evidence/SKILL.md)
  for the sanitization, access, and cleanup record.

## Verification Expectations

- Prefer repository-owned security tests, policy checks, dependency audits, and
  integration lanes over generic scanner output.
- Add or request regression coverage for confirmed vulnerabilities when practical.
- When a control cannot be verified locally, report the exact missing evidence and
  residual risk rather than claiming safety.
- When artifact cleanup cannot be verified, report the artifact class, expected
  cleanup, attempted cleanup, reason verification failed, residual exposure risk,
  and follow-up owner/process without exposing raw paths or contents.
- Security-sensitive randomness and identifiers should follow
  [`random-data-identifiers`](../random-data-identifiers/SKILL.md).

## Anti-Patterns

- Printing secrets while trying to prove they are not exposed.
- Treating client-side validation, hidden form fields, or UI routing as an
  authorization boundary.
- Replacing structured APIs with escaped strings for SQL, shell, HTML, paths, or
  templates.
- Adding crypto, auth, or token code without tests or current library docs.
- Reporting hypothetical vulnerabilities without a plausible attacker path,
  affected asset, and evidence from the repository.
