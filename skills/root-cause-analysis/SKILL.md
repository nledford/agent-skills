---
name: root-cause-analysis
description: >
  Structured root-cause analysis for recurring failures, incidents, regressions,
  systemic process gaps, and postmortem-style prevention work. Use after a
  current symptom is reproduced or understood; use systematic-debugging first for
  active failing tests, crashes, or unknown immediate causes.
---

# Root Cause Analysis

Root cause analysis (RCA) identifies the underlying technical, process, and
system factors that allowed a failure to occur or recur. Its goal is durable
prevention, not just the smallest code fix.

## When to Use

Use this skill for:

- Recurring defects, flaky failures, repeated regressions, or incident trends.
- Production or incident-like failures where impact, timeline, and prevention
  matter.
- Customer-impacting behavior where the direct fix is not enough to explain why
  the defect escaped.
- Cross-team, workflow, validation, documentation, release, observability, or
  ownership gaps.
- Postmortem-style analysis after `systematic-debugging` has identified the
  immediate cause of a current symptom.

Do **not** use this as the first response to an active failing test, crash, or
unknown bug. Use `systematic-debugging` first to reproduce the symptom, capture
evidence, and isolate the direct cause.

## RCA Workflow

1. **Define the event**
   - What happened, when, where it was observed, and who/what was affected?
   - Use concrete evidence: test names, commands, route classes, logs, metrics,
     screenshots, traces, or user-visible behavior.
2. **Separate symptom, trigger, root cause, and contributing factors**
   - Symptom: what was observed.
   - Proximate trigger: what activated the failure.
   - Direct cause: the technical mechanism.
   - Contributing factors: why the issue escaped or recurred.
3. **Map expected vs actual controls**
   - Which test, review, type, constraint, migration, observability, or process
     should have caught this?
   - Was the control absent, weak, bypassed, flaky, undocumented, or scoped to
     the wrong layer?
4. **Identify durable prevention**
   - Prefer behavior-oriented regression tests, domain invariant checks,
     stronger validation, clearer ownership, better observability, or documented
     workflow changes over broad rewrites.
5. **Prioritize actions**
   - Separate required fixes from nice-to-have cleanup.
   - Assign follow-ups to the lowest layer that prevents recurrence.

## Techniques

- **5 Whys**: useful for walking from the proximate failure to a process or
  system gap. Stop when the next "why" would become speculative.
- **Fault tree**: useful when multiple independent factors could have caused or
  amplified the failure.
- **Control gap analysis**: useful for Chidori because repo workflows rely on
  root `just` lanes, generated artifacts, SQLx metadata, feature boundaries, and
  security review evidence.
- **Timeline reconstruction**: useful for incidents, flaky tests, releases, and
  multi-step regressions.

## Output Template

```markdown
## Root Cause Analysis

- Event:
- Impact:
- Evidence reviewed:
- Expected behavior/control:
- Actual behavior/control gap:
- Proximate trigger:
- Direct technical cause:
- Contributing factors:
- Root cause:
- Why existing tests/reviews/checks missed it:
- Corrective actions completed:
- Preventive actions recommended:
- Validation or monitoring needed:
- Remaining risks:
```

## Chidori Considerations

- Prefer root `just` validation lanes when prevention depends on repeatable
  checks.
- For user-visible behavior, connect follow-up coverage to BDD only when a
  stakeholder-readable `.feature` contract is appropriate.
- For code defects, recommend TDD-style regression coverage at the narrowest
  useful layer before or alongside implementation.
- For domain failures, name the Chidori bounded context and invariant rather
  than describing only tables, routes, or UI widgets.
- For security-sensitive incidents or prevention work, follow
  `docs/agents/security.md` and obtain sanitized review evidence.

## Guardrails

Do **not**:

- Stop at "human error", "test was wrong", "race condition", or "environment
  issue" without evidence and a control gap.
- Blame individuals; analyze systems, ownership, workflow, validation, and
  technical constraints.
- Recommend broad rewrites when a targeted control prevents recurrence.
- Add process-heavy follow-ups that are not proportional to impact and
  recurrence risk.
- Claim prevention is complete without validation, monitoring, or an explicit
  reason it is not needed.
