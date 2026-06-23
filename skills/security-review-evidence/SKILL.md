---
name: security-review-evidence
description: Security-review evidence checklist. Use before and after security-sensitive behavior, documentation, or command-surface changes to keep findings sanitized, scoped, and tied to repository policy when one exists.
user-invocable: false
---

# Security Review Evidence

Use this skill when a change touches authentication, authorization, crypto,
certificates, tokens, signatures, sessions, secrets, passwords, CORS, CSP, CSRF,
`.env` handling, credential handling, trust boundaries, security-sensitive input
validation, file import/export paths, plugin or extension trust roots, browser
artifacts, or related commands/docs.

Use [`security-review`](../security-review/SKILL.md) for the audit workflow and
this skill for evidence collection, redaction, and reporting guardrails.

## Source of Truth

- First inspect the repository for security guidance such as `SECURITY.md`,
  `AGENTS.md`, `docs/security*`, threat models, runbooks, CI security jobs, or
  review templates.
- Prefer existing validation commands and evidence templates over inventing a new
  checklist.
- If no repository policy exists, use this skill as the minimum evidence
  checklist and state that no project-specific policy was found.

## Evidence to Collect

- Record **pre-change** and **post-change** security evidence for each
  security-sensitive change; if a checkpoint is impossible, say why.
- Name the affected route classes, commands, docs, helper scripts, deployment
  surfaces, browser artifacts, storage paths, or trust boundaries.
- Cover authentication, authorization, sessions, CORS, CSP, CSRF, MFA,
  throttling, and secret handling where applicable.
- For import/export or filesystem work, confirm raw host paths, canonical paths,
  cache payloads, task payloads, and command output are redacted where needed.
- For plugin, extension, or script execution work, identify trust roots, managed
  roots, path boundaries, and untrusted inputs without exposing private
  filesystem details.
- For browser/frontend evidence, verify artifacts and logs do not include
  cookies, storage state, CSRF/session IDs, credentialed URLs, secrets, private
  paths, or sensitive payloads.

## Forbidden Outputs

Never print or store `.env` contents, secret files, private keys, cookies,
tokens, CSRF values, password hashes, credential material, credentialed database
URLs, browser storage state, raw import paths, or private host paths. Use
placeholders such as `<redacted>` or `<local-secret-file>`.

## Verification Expectations

- Prefer repository-owned validation recipes when they exist; cite exact commands
  run and sanitized pass/fail results.
- Do not treat search output, screenshots containing secrets, or raw logs as
  shareable security evidence.
- If verification is skipped or partial, report the missing control, why it was
  not checked, and the residual risk.
