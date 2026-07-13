---
name: systematic-debugging
description: Evidence-driven debugging for active bugs, failing tests, runtime exceptions, flaky behavior, performance regressions, build/lint/type/compile failures, integration failures, crashes, and unexpected behavior. Use before proposing fixes for a current symptom. Use root-cause-analysis for recurring incidents, systemic failures, and postmortem-style prevention work.
---

# Systematic Debugging

Use this skill to investigate a current defect without guessing, overfitting
fixes, masking symptoms, or making broad speculative changes. Start from
observable evidence, isolate the cause, fix the smallest correct thing, and
verify the behavior that failed.

## When to Use

Use this skill for any task involving:

- Failing tests, test regressions, skipped/ignored tests that need investigation,
  or unexpected assertions.
- Bug reports, incorrect application behavior, runtime exceptions, crashes,
  panics, stack traces, or user-visible failures.
- Unexpected state transitions, data corruption symptoms, stale state, or invalid
  domain state.
- Flaky or nondeterministic failures, timing-sensitive behavior, async issues,
  concurrency issues, races, deadlocks, or ordering problems.
- Performance regressions, timeouts, resource leaks, excessive memory/CPU/I/O,
  or degraded latency/throughput.
- Build, lint, formatting, type-check, compilation, dependency, or toolchain
  failures.
- Integration failures across APIs, services, databases, queues, caches, UI,
  filesystem, network, auth, configuration, or environment boundaries.
- A current incident symptom when the immediate need is reproduce/diagnose/fix.
  For postmortem, prevention, repeated failures, or organizational/system causes,
  use `root-cause-analysis` after the active failure is understood.

Do not use this skill for purely mechanical formatting, documentation-only
changes, or greenfield implementation with no failure or symptom to explain.

## Core Principles

- Start from the observable symptom, not an assumed cause.
- Preserve and inspect exact evidence: error text, stack trace, logs, failing
  assertion, diff, request/response, screenshot, trace, profile, or user-visible
  behavior.
- When that or production evidence may expose secrets, credentials, PII, tenant
  data, payloads, or private paths, load
  [`security-review`](../security-review/SKILL.md) and
  [`security-review-evidence`](../security-review-evidence/SKILL.md). Keep raw
  artifacts local and ignored; report sanitized summaries only. Do not add this
  routing for evidence without a sensitive-data risk.
- Reproduce the issue before fixing whenever feasible. If reproduction is not
  feasible, explain why and use the strongest available evidence.
- Find the smallest reliable reproduction: narrow command, test filter, route,
  input, fixture, component, dataset, seed, profile, or environment.
- Compare expected behavior against actual behavior before changing code.
- Form multiple plausible hypotheses; do not stop at the first plausible bug.
- Test hypotheses one at a time and record evidence for or against each one.
- Prefer direct evidence over speculation, intuition, or broad pattern matching.
- Distinguish symptom, proximate trigger, root cause, and contributing factors.
- Keep fixes minimal, targeted, and aligned with the domain model and public
  contracts.
- Add or update regression coverage for confirmed defects.
- Do not weaken tests, delete assertions, reduce coverage, bypass validation, or
  mark tests ignored/skipped unless the root cause proves the original behavior
  contract was wrong and the change is explicitly justified.

## Investigation Workflow

Follow this sequence unless the repository has a stricter local runbook:

1. **Clarify the symptom**
   - State what failed and where it was observed.
   - Identify impact: user-visible behavior, failing test, broken command,
     incident symptom, performance metric, or integration boundary.
2. **Locate the failing surface**
   - Identify the failing command, test, route, component, module, workflow,
     query, job, or tool invocation.
   - Prefer repository-provided commands and docs over ad hoc commands.
3. **Reproduce the failure**
   - Run the narrowest relevant command first.
   - If flaky, run enough repetitions or vary concurrency/seed/time/environment
     to characterize nondeterminism without hiding it.
4. **Capture exact failure evidence**
   - Save or quote the important error message, assertion, stack frame, log line,
     response body/status, profile metric, or visible behavior.
   - Avoid summarizing away details that distinguish one failure mode from
     another.
5. **Inspect recent changes and call paths**
   - Read the relevant code, tests, fixtures, config, schema, generated code
     boundaries, and recent diffs/history if available.
   - Trace data/control flow across boundaries before editing.
   - Use [`serena`](../serena/SKILL.md) for supported-language symbols,
     references, implementations, call relationships, and diagnostics when call
     paths matter. Use direct reads/search for exact error text, docs, config,
     logs, fixtures, generated assets, and tests, builds, or other validation
     commands.
6. **Build a hypothesis list**
   - Include at least two plausible causes when the failure is not obvious.
   - Separate code defects from data, environment, dependency, timing, and test
     expectation hypotheses.
7. **Rank hypotheses**
   - Prefer high-likelihood, high-testability hypotheses first.
   - Define what observation would confirm or falsify each hypothesis.
8. **Instrument or inspect only as needed**
   - Add temporary logging, tracing, assertions, probes, or debuggers only when
     reading and focused tests do not provide enough evidence.
   - Remove temporary instrumentation before finishing unless it is intentionally
     production-quality observability.
9. **Isolate the root cause**
   - Prove why the failure occurs and why competing hypotheses are less likely or
     false.
   - Identify whether the root cause is code logic, contract mismatch, missing
     validation, incorrect test expectation, data setup, configuration,
     dependency/toolchain change, race/timing, caching, or environment drift.
10. **Implement the smallest correct fix**
    - Change one causal area at a time.
    - Avoid broad refactors, unrelated cleanup, or public contract changes unless
      the evidence requires them.
11. **Add or update regression tests**
    - Add the narrowest behavior-oriented coverage that would have caught the
      defect.
    - Prefer public behavior and domain outcomes over private implementation
      details when practical.
12. **Run focused verification first**
    - Re-run the reproducer, failing test, affected lints/type checks, or focused
      benchmark/profile.
13. **Run broader verification when justified**
    - Broaden to package/module/full-suite checks only when the change crosses
      boundaries, affects shared behavior, or focused checks cannot provide
      enough confidence.
14. **Summarize evidence, root cause, fix, and verification**
    - State what was observed, what changed, why it fixes the root cause, and
      what remains unverified.

## Debugging Output

Produce a concise debugging summary when the task involved a confirmed defect,
regression, flaky behavior, or non-obvious failure. Use this format, trimming
fields that truly do not apply:

```markdown
## Debugging Summary

- Symptom:
- Impacted behavior:
- Expected behavior:
- Actual behavior:
- Root cause:
- Proximate trigger:
- Contributing factors:
- Why the fix is correct:
- Tests added or updated:
- Verification run:
- Not run / remaining risks:
- Follow-up work:
```

Avoid shallow explanations such as "the test was wrong", "state was invalid",
"race condition", or "environment issue" unless you explain why, show the
evidence, and distinguish the root cause from the symptom.

If the work reveals repeated failures, broad contributing factors, or prevention
items beyond the direct fix, hand off to `root-cause-analysis` for a postmortem-
style RCA rather than expanding this debugging pass.

## Testing and Verification Expectations

- Use focused tests and commands while investigating. Start narrow; broaden only
  for meaningful confidence.
- Add regression coverage for confirmed defects unless impossible or already
  covered by an existing test that was failing for the right reason.
- Keep tests behavior-oriented and domain-facing where practical. Avoid brittle
  tests coupled to private implementation details unless the defect is itself an
  implementation contract.
- Resolve failing tests, clippy/lint errors, type errors, compilation errors,
  formatting issues, and introduced warnings before considering the task done.
- Do not run long full-suite or expensive commands by default. Use them when the
  fix touches shared infrastructure, public contracts, cross-cutting behavior,
  generated artifacts, schemas, concurrency, performance, or release-critical
  surfaces.
- Clearly state every verification command/check run and whether it passed.
- Clearly state important checks not run and why.
- Do not claim performance improvements without before/after measurements from
  the same tool and comparable conditions.

## Guardrails

Do **not**:

- Guess and patch without reproduction when reproduction is feasible.
- Treat the first plausible issue as the root cause without testing alternatives.
- Make multiple unrelated changes in one debugging pass.
- Paper over errors with retries, sleeps, broad exception handlers, broad null
  checks, silent defaults, swallowed errors, cache clears, or relaxed validation
  unless evidence proves that behavior is correct for the domain.
- Change public contracts, API behavior, schemas, migrations, data formats,
  permissions, error semantics, or compatibility guarantees without evidence,
  tests, and explicit justification.
- Assume an environment issue before checking code-level causes, configuration,
  inputs, data setup, dependencies, and command differences.
- Ignore flakiness or nondeterminism. Characterize it and either fix it or report
  the remaining risk explicitly.
- Leave temporary logs, debug prints, tracing, sleeps, feature flags, or probes in
  production code.
- Mark tests ignored/skipped, delete assertions, or reduce coverage as a
  substitute for fixing the defect.

## Debugging Heuristics by Failure Class

When the core workflow is not enough, use the progressive reference
[`references/failure-heuristics.md`](references/failure-heuristics.md) for
failure-class prompts covering unit, integration, flaky, async, state,
serialization, boundary, environment, dependency, performance, UI, database, and
build failures.

## Communication Style

Communicate in short, evidence-based updates:

- State what failed and the exact evidence observed.
- State the hypothesis currently being tested and why it is plausible.
- State what changed and why it addresses the root cause.
- State what verification was performed and the result.
- State uncertainty explicitly when evidence is incomplete; do not overstate
  confidence.

## Examples

### Good debugging behavior

> The `creates_order_without_discount` test fails with `expected total 100,
> actual total 90`. I reproduced it with the single test filter. The failing
> path applies the promotional discount even when the request has no coupon. My
> hypotheses are: stale fixture data, default coupon value, or unconditional
> discount application. Inspecting the request fixture shows no coupon; tracing
> the calculation shows the discount branch checks `customer.is_eligible` but not
> `coupon.is_some()`. I will add a regression assertion for eligible customers
> without coupons, update the branch condition, then rerun the focused test and
> the order calculation tests.

Why this is good: it preserves exact evidence, reproduces narrowly, compares
expected and actual behavior, names multiple hypotheses, tests the relevant path,
implements a targeted fix, and verifies with focused tests.

### Bad debugging behavior to avoid

> The order test is probably flaky because discounts are complicated. I changed
> the expected total to `90`, added a retry, and refactored the pricing module so
> the suite passes locally.

Why this is bad: it guesses without evidence, weakens the test, hides possible
nondeterminism with a retry, makes broad unrelated changes, and never explains
the root cause or why the new behavior is correct.
