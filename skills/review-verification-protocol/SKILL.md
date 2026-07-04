---
name: review-verification-protocol
description: Mandatory evidence gates for code-review findings. Load with code-review and any specialist review skill before reporting findings, or read/apply manually if the runtime hides this skill.
user-invocable: false
---

# Review Verification Protocol

Use this protocol before reporting any code-review finding. It is the evidence
gate for [`code-review`](../code-review/SKILL.md) and any specialist review
skills. Skipping it creates false positives that waste reviewer time and erode
trust.

## Hard gates per finding

Apply these gates **once per finding**. If a gate fails, omit the finding,
downgrade it, or rephrase it as a question. Do not ship soft accusations.

| Step | What you do | Pass condition |
| --- | --- | --- |
| **1. Anchor** | Read the full enclosing function, module, test, migration, recipe, config, or doc section, not only the diff hunk. | You can cite the file path and line range, symbol, module, test, or behavior being judged. |
| **2. Evidence** | Search/read enough surrounding code and docs to prove the issue is real and not handled elsewhere. | You have an artifact: file:line citation, command output, search result, relevant absence after search, or explicit “not run because ...”. |
| **3. Impact** | Explain how the issue affects behavior, maintainability, security, tests, operations, or architecture in the repository being reviewed. | The finding is not merely personal style or an implausible hypothetical. |
| **4. Severity** | Assign severity using `code-review` severity calibration or the user-requested review vocabulary. | The label matches impact and urgency; unrelated net-new nice-to-have work is not a blocker. |
| **5. Remedy** | Name a concrete fix or next step. | The author can act without guessing what you want. |

## Required checks before flagging

- Read the actual changed code or document, not just a summary.
- Search for usages before claiming something is unused, dead, or unreferenced.
- Use [`serena`](../serena/SKILL.md) for supported-language references,
  implementations, call relationships, and diagnostics when semantic evidence
  helps. Use direct reads/search for exact strings, docs, config, logs, fixtures,
  generated assets, and tests, builds, or other validation commands.
- Check whether validation, authorization, error handling, cleanup, or behavior
  coverage exists at a higher layer, middleware, caller, transaction boundary,
  database constraint, generated contract, test harness, or runbook.
- Distinguish incorrect behavior from a valid different style.
- Consider intentional design documented in comments, `AGENTS.md`, docs,
  migrations, feature files, or existing architecture.
- Verify framework/library syntax against current docs when the finding depends
  on version-sensitive APIs.

## Issue-type prompts

- **Missing behavior, validation, or error handling:** Confirm the missing case
  can occur and matters to a supported user, operator, API, or domain flow.
- **Authorization, privacy, or security:** Identify the trust boundary, actor,
  data class, and route/command/path. Use any available repository security
  process and sanitized evidence; never expose secrets.
- **Unused or dead code:** Search tests, generated contracts, trait impls, macros,
  serde names, SQLx mappings, route registration, CLI recipes, and docs links.
- **Test weakness:** Check whether another layer already covers the behavior;
  prefer behavior and invariant gaps over implementation-detail assertions.
- **Refactor or architecture concern:** Name the boundary, ownership, or
  responsibility that moved, blurred, or coupled.
- **Performance or scalability:** Confirm a hot path, unbounded input, query-shape
  change, repeated allocation/I/O, or resource contention risk.
- **Concurrency, async, and resources:** Check task lifetimes, cancellation, lock
  scopes, `.await` points, transactions, handles, pools, backpressure, and cleanup.
- **Documentation, workflow, or agent guidance:** Check whether the changed doc is
  authoritative, linked from the right index, concise, and free of conflicting
  duplicate policy.

## Before submitting findings

1. Every finding passed the hard gates.
2. Findings use the format and severity vocabulary from `code-review` unless the
   user requested a different format.
3. No finding is style preference, unverified speculation, or unrelated future
   work.
4. Validation status is truthful: passed, failed, not run, and why.
5. Re-reviews verify previous fixes only unless a fresh full review was requested.

If uncertain, read more context, ask a `Question`, downgrade the severity, or
remove the finding.
