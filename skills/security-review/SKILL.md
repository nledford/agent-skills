---
name: security-review
description: Security review and audit guidance for code, configs, docs, and command surfaces. Use when changes touch authentication, authorization, crypto, certificates, tokens, signatures, secrets, passwords, sessions, CORS, CSP, CSRF, OAuth/OIDC/SAML, input validation, file paths, command execution, dependency trust, or other trust boundaries. Pair with code-review for review findings.
---

# Security Review

Use this skill to review security-sensitive changes without exposing secrets or
overstating unverified risk. Pair it with [`code-review`](../code-review/SKILL.md)
for review finding format and with
[`security-review-evidence`](../security-review-evidence/SKILL.md) for sanitized
evidence handling.

## Use When

- Authentication, authorization, permissions, roles, tenancy, sessions, cookies,
  MFA, recovery flows, or invite flows change.
- Cryptography, certificates, TLS, signatures, hashes, password handling, tokens,
  API keys, OAuth/OIDC/SAML, webhooks, nonces, or key rotation change.
- Input crosses a trust boundary: HTTP, forms, GraphQL/RPC, CLI args,
  environment variables, files, uploads/downloads, archives, plugins, extensions,
  templates, Markdown/HTML, SQL, shell commands, SSR, browser storage, or network
  calls.
- CORS, CSP, CSRF, SSRF, path traversal, deserialization, sandboxing, dependency
  trust, supply chain, logging, telemetry, or secret redaction is relevant.

Do not use this skill as a generic style review for code with no trust boundary,
secret, identity, privilege, untrusted input, or security control. Use ordinary
code review instead.

## Workflow

1. Inspect repository policy first: `SECURITY.md`, `AGENTS.md`, threat models,
   auth docs, deployment docs, CI security jobs, dependency policy, and review
   templates.
2. Scope the boundary: actors, assets, entry points, trust levels, data classes,
   permissions, storage, external services, and attacker-controlled inputs.
3. State the intended security property before judging code: who may do what,
   which data must remain confidential/integral, what must be authenticated,
   what must be rate-limited, and what must be auditable.
4. Read the full path: caller, middleware, validation, business rule, storage,
   logging, error handling, tests, config, docs, and deployment assumptions.
5. Verify controls with tests, policies, config checks, dependency audit output,
   or concrete code evidence. Do not report speculative vulnerabilities.
6. Sanitize evidence. Never print secrets, cookies, tokens, private keys, raw
   credentialed URLs, `.env` contents, or private host paths.
7. Report findings through the code-review format with severity calibrated to
   exploitability, blast radius, data sensitivity, and existing mitigations.

## Review Checklist

- **Authn/authz:** identity is established by trusted middleware; authorization is
  checked server-side at the object/action boundary; tenant and role checks cannot
  be bypassed by direct IDs, cache hits, background jobs, or client-only guards.
- **Secrets and sessions:** tokens, cookies, credentials, key material, and
  session IDs are generated with secure randomness, scoped, rotated where needed,
  stored safely, redacted from logs, and not leaked to clients or artifacts.
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
  traces, reports, exceptions, and test artifacts.
- **Dependencies and supply chain:** new packages, binaries, scripts, generated
  code, lockfile changes, and install hooks have a clear need and review path.

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
- **Browser tests/artifacts:** never retain or share raw traces, screenshots,
  videos, storage state, network dumps, cookies, CSRF tokens, credentialed URLs,
  or live data.

## Verification Expectations

- Prefer repository-owned security tests, policy checks, dependency audits, and
  integration lanes over generic scanner output.
- Add or request regression coverage for confirmed vulnerabilities when practical.
- When a control cannot be verified locally, report the exact missing evidence and
  residual risk rather than claiming safety.
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
