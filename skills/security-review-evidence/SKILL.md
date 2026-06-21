---
name: security-review-evidence
description: >
  Chidori security-review evidence checklist. Use before and after security-sensitive
  behavior, documentation, or command-surface changes to keep findings sanitized,
  scoped, and linked to the source-of-truth policy.
user-invocable: false
allowed-tools: Read, Grep, Glob, Bash
---

# Security Review Evidence

Use this repo-local skill when a change touches auth, authorization, crypto,
certificates, tokens, signatures, sessions, secrets, passwords, CORS, CSP,
`.env` handling, credential-secret handling, trust boundaries, security-sensitive
input validation, importer paths, plugin trust roots, browser artifacts, or
related commands/docs.

## Source of truth

- Detailed policy, validation commands, and templates live in
  [`docs/agents/security.md`](../../../docs/agents/security.md).
- Do not copy long auth, importer, plugin, or artifact matrices into task notes;
  cite the relevant section and summarize only the lanes and controls you checked.

## Evidence to collect

- Record **pre-change** and **post-change** security evidence for each
  security-sensitive change; if a checkpoint is impossible, say why.
- Name the route classes, commands, docs, helper scripts, compose lanes, or
  browser artifacts affected.
- Cover auth, authorization, sessions, CORS, CSP, CSRF, WebAuthn, MFA,
  throttling, and secrets/credential-secret handling where applicable.
- For importer work, confirm raw host paths, canonical paths, cache payloads,
  task payloads, and command output are redacted.
- For plugin work, identify trust roots, managed roots, path boundaries, and
  untrusted inputs without exposing private filesystem details.
- For browser/frontend evidence, verify artifacts and logs do not include
  cookies, storage state, CSRF/session IDs, credentialed URLs, secrets, private
  paths, or sensitive payloads.

## Forbidden outputs

Never print or store `.env` contents, secret files, private keys, cookies,
tokens, CSRF values, password hashes, credential-secret material, credentialed
PostgreSQL URLs, browser storage state, raw importer paths, or private host
paths. Use placeholders such as `<redacted>` or `<local-secret-file>`.

## Verification expectations

- Prefer root `just` recipes named in `docs/agents/security.md`; cite exact
  commands run and sanitized pass/fail results.
- Do not treat MCP/search output, screenshots containing secrets, or raw logs as
  security evidence.
- If verification is skipped or partial, report the missing control, why it was
  not checked, and the residual risk.
