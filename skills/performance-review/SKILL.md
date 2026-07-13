---
name: performance-review
description: Review performance and scalability using workload, baseline, profiling, query-plan, rendering, concurrency, and resource evidence. Use for bottleneck audits, benchmark plans, capacity risks, or performance-sensitive changes; do not use for active unexplained regressions or implementation mechanics alone.
---

# Performance Review

Use this skill as a cross-stack review lens. For repository changes, also load
[`code-review`](../code-review/SKILL.md) and
[`review-verification-protocol`](../review-verification-protocol/SKILL.md).

Use [`systematic-debugging`](../systematic-debugging/SKILL.md) first when an
active regression has not been reproduced or narrowed. Use language, runtime,
browser, and SQL skills for implementation mechanics. Use
[`observability-engineering`](../observability-engineering/SKILL.md) when the
work changes durable production signals, dashboards, alerts, or SLOs.

When profiles, traces, logs, responses, or production evidence may expose
secrets, credentials, PII, tenant data, payloads, or private paths, also load
[`security-review`](../security-review/SKILL.md) and
[`security-review-evidence`](../security-review-evidence/SKILL.md). Keep raw
artifacts local and ignored; report sanitized measurements and summaries only.
This routing is unnecessary for non-sensitive evidence.

## Workflow

1. Define the supported workload, data size, traffic or concurrency shape,
   environment, user-visible impact, and target threshold.
2. Establish a representative baseline from benchmarks, profiles, traces,
   browser measurements, query plans, production-safe telemetry, or reproducible
   timing. Label estimates and missing measurements explicitly.
3. Identify the hot path and scaling variable before reviewing allocations,
   cloning, I/O, query count and shape, serialization, rendering, caching,
   contention, queueing, backpressure, and resource bounds.
4. Verify each finding against repository evidence and distinguish measured
   bottlenecks from plausible risks that still require an experiment.
5. Recommend the smallest change that addresses the demonstrated cause, plus the
   benchmark, load test, query-plan comparison, or runtime measurement that would
   prove the improvement and catch regressions.
6. Report environment limits, skipped measurements, assumptions, tradeoffs, and
   residual capacity risk.

## Output

Return prioritized findings with workload and baseline evidence, expected user
or operational impact, a concrete remedy, a measurement plan, skipped checks,
and residual risk. Do not claim an optimization without a way to compare before
and after behavior.
