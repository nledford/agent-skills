---
name: threat-modeling
description: Threat modeling and security design analysis. Use when asked to threat model, identify abuse cases, model actors/assets/data flows/trust boundaries, STRIDE, attack trees, attack surface, security requirements, mitigations, assumptions, or residual risk for new features, systems, integrations, APIs, tenants, uploads, plugins, webhooks, command surfaces, or sensitive-data flows. Do not use for ordinary code review, confirmed vulnerability validation, dependency/SBOM/CVE supply-chain review, language implementation, or third-party API docs.
---

# Threat Modeling

Use this skill before or during significant trust-boundary changes to reason about
security design. Keep it lightweight for feature work: identify what could go
wrong, decide what must be true before ship, and name residual risks. Use
[`security-review`](../security-review/SKILL.md) and
[`security-review-evidence`](../security-review-evidence/SKILL.md) when findings
must be verified against implemented controls and reported with sanitized
evidence.

## Use When

- Designing or changing authentication, authorization, tenancy, admin actions,
  invite/recovery flows, sessions, secrets, tokens, or sensitive-data flows.
- Adding or changing APIs, webhooks, uploads/downloads, imports/exports, plugins,
  command execution, browser storage, background jobs, integrations, or external
  service calls.
- The user asks for a threat model, abuse cases, STRIDE, attack trees, attack
  surface, trust boundaries, data flows, mitigations, residual risk, or security
  acceptance criteria.

Do not use this skill for ordinary code review, confirmed vulnerability
validation, exploit reproduction, or dependency/SBOM/CVE/provenance review. Use
[`security-review`](../security-review/SKILL.md) for concrete implemented-control
review and [`dependency-supply-chain-review`](../dependency-supply-chain-review/SKILL.md)
for supply-chain risk.

## Lightweight vs. Full Review

- **Lightweight feature threat model:** use during design or implementation to map
  actors, assets, entry points, data flows, trust boundaries, abuse cases,
  mitigations, assumptions, residual risks, and security acceptance criteria. It
  can be based on design docs, code paths, API contracts, and repository policy.
- **Full security review:** use after controls exist or when the task asks for
  validated findings. Load [`security-review`](../security-review/SKILL.md) and
  [`security-review-evidence`](../security-review-evidence/SKILL.md), verify each
  claim with repository evidence, sanitize artifacts, and report findings through
  the review format.

## Workflow

1. Inspect local sources first: `SECURITY.md`, architecture docs, threat models,
   auth/permission docs, API specs, data classification notes, deployment docs,
   tests, review templates, and relevant code paths. Do not read or print secrets.
2. Define scope: feature/system, in-scope actors, out-of-scope systems,
   environments, data classes, assumptions, and open questions.
3. Map the system:
   - actors and identities, including anonymous, authenticated, tenant, admin,
     service, integration, and malicious users;
   - assets and security properties: confidentiality, integrity, availability,
     privacy, auditability, tenant isolation, and non-repudiation;
   - entry points and attacker-controlled inputs: HTTP/RPC, files, URLs, CLI,
     queues, webhooks, plugins, templates, browser state, environment variables,
     and third-party callbacks;
   - trust boundaries and privilege changes between client/server, tenant/admin,
     app/database, worker/queue, internal/external service, host/container,
     browser/server, and user-supplied/generated content;
   - data flows, storage, logs, telemetry, caches, exports, backups, retention,
     and deletion paths.
4. Enumerate abuse cases. Use STRIDE, attack trees, misuse cases, or attack-surface
   review only as tools; keep each case tied to an actor, entry point, affected
   asset, violated security property, and plausible path.
5. Select mitigations proportional to risk: server-side authorization,
   least-privilege scopes, input validation and canonicalization, structured APIs,
   rate limits, replay protection, CSRF/CORS/CSP, safe file handling, sandboxing,
   encryption, secret lifecycle controls, logging redaction, audit events,
   monitoring, rollback, and operational runbooks.
6. Convert mitigations into security acceptance criteria: tests, policy checks,
   review gates, config assertions, migration checks, observability requirements,
   rollout constraints, and explicit non-goals.
7. Record residual risk with owner, expiry/revisit trigger, compensating controls,
   and what evidence would be needed to close it. Escalate to full security review
   when a risk is concrete, disputed, high impact, or control verification matters.

## Output Shape

Prefer a compact model the team can act on:

- **Scope and assumptions**
- **Actors and assets**
- **Entry points, trust boundaries, and data flows**
- **Abuse cases and impact**
- **Mitigations and security acceptance criteria**
- **Residual risks, owners, and review handoffs**

## Anti-Patterns

- Producing a generic vulnerability checklist without the local actors, assets,
  entry points, trust boundaries, and data flows.
- Treating a design-time abuse case as a verified vulnerability without evidence.
- Requiring heavyweight security review ceremony for a small feature when a short
  model and concrete acceptance criteria are enough.
- Omitting residual risk, assumptions, or the handoff to verified
  `security-review` findings.
- Printing secrets, raw tokens, private host paths, credentialed URLs, or raw
  security artifacts while modeling risk.
