---
name: observability-engineering
description: >-
  Observability, telemetry, and production diagnostics guidance. Use when
  designing, adding, reviewing, or testing structured logs, metrics, traces,
  span/context propagation, correlation or request IDs, sampling,
  labels/cardinality, dashboards, alerts, SLO/SLI/error-budget signals,
  OpenTelemetry/Prometheus/Grafana/Datadog-style instrumentation, operational
  runbooks, or incident visibility. Do not use for ordinary language
  implementation, active debugging without durable instrumentation changes,
  security review except telemetry leakage or audit controls, BDD/TDD mechanics,
  or documentation-only edits; load those existing skills instead or alongside
  this skill when their trigger is primary.
---

# Observability Engineering

Use this skill to make production behavior visible enough for operators to
detect, diagnose, and prevent failures without leaking data or creating noisy,
high-cost telemetry. This skill owns telemetry intent and signal quality:
structured logs, metrics, traces, correlation IDs, dashboards, alerts, SLOs,
runbooks, sampling, cardinality, retention, and validation.

Use language, framework, SQL, architecture, debugging, testing, or documentation
skills for their primary mechanics. Add this skill when the work changes what
must be observable, how signals are shaped, or how operators act on them.

## Use When

- Designing, adding, reviewing, or testing durable logs, metrics, traces, spans,
  telemetry events, context propagation, request IDs, correlation IDs, or audit
  events.
- Defining dashboards, alerts, SLOs, SLIs, error-budget signals, incident
  visibility, runbook links, or production failure signals.
- Reducing telemetry noise, cost, high-cardinality labels, over-collection,
  unsafe sampling, or privacy exposure.
- Converting temporary debugging probes into intentional production
  instrumentation.

Do not use this skill as the primary workflow for:

- Active failures with no durable instrumentation change; use
  [`systematic-debugging`](../systematic-debugging/SKILL.md) first.
- Postmortem prevention after the direct cause is known unless the prevention
  work is observability; use [`root-cause-analysis`](../root-cause-analysis/SKILL.md).
- Documentation-only runbooks, dashboard notes, comments, or examples; use
  [`documentation-engineering`](../documentation-engineering/SKILL.md).
- Language-specific implementation, Rust async/web behavior, SQL schema/query
  design, architecture boundary selection, or BDD/TDD method choices unless the
  task also needs telemetry design.

## Security and Privacy Routing

Load [`security-review`](../security-review/SKILL.md) and
[`security-review-evidence`](../security-review-evidence/SKILL.md) when telemetry
can expose secrets, credentials, API keys, tokens, cookies, session IDs, PII,
tenant data, auth/session traces, raw request or response bodies, SQL values,
exploit payloads, credentialed URLs, private host paths, or customer data. Also
load them when logs, alerts, dashboards, traces, or audit events are security
monitoring controls or report evidence.

Never print raw secrets or sensitive telemetry to prove redaction. Capture only
sanitized evidence and treat raw logs, traces, profiles, dashboard exports,
network dumps, screenshots, incident bundles, and reproduced payloads as local
ignored artifacts unless repository policy explicitly allows sanitized retention.

## Security, Compliance, And Forensic Audit Events (Conditional)

Keep ordinary telemetry operational by default; do not relabel routine logs as
audit events. When a security, compliance, or forensic obligation requires an
audit event, load the security skills above and define an explicit event contract:

- Record actor, action, target, outcome, time, and correlation identifiers with
  stable semantics and appropriate data minimization.
- State whether delivery is complete or has explicit loss semantics. Do not
  sample when completeness is required; define how duplicates, ordering, and
  delayed delivery are handled.
- Define access control, integrity/tamper expectations, retention, and deletion
  rules for the event store and its exports.
- Define failure behavior: fail closed, block, queue durably, degrade with an
  alert, or record explicit loss, according to the threat model and operational
  impact.

## Workflow

1. **Inspect local evidence first.** Read existing logging/tracing setup,
   metrics registries, instrumentation helpers, collectors/processors, alert
   rules, dashboard definitions, SLO docs, runbooks, tests, deployment config,
   privacy policy, and security guidance. Vendor-specific CLIs or consoles are
   optional evidence only; prefer repository-owned local files and commands.
2. **State instrumentation intent.** Name the operator question, decision, owner,
   affected users, failure modes, baseline signal, and action the telemetry must
   support. Remove or avoid signals that do not answer an operational question.
3. **Choose the signal type deliberately.** Use logs for discrete events and
   diagnostic context, metrics for aggregate health and alerting, traces for
   request or job flow across boundaries, and runbooks/dashboards for response.
4. **Define correlation and context.** Decide where request, trace, span,
   correlation, causation, job, tenant, and user context originate; how they are
   validated; how they propagate across async tasks, queues, jobs, and outbound
   calls; and which identifiers must be redacted or omitted.
5. **Design failure signals.** Cover errors, timeouts, retries, cancellations,
   dependency degradation, queue depth, saturation, partial success, dropped work,
   backpressure, and data-quality failures at the boundary where operators can
   act.
6. **Control cardinality, cost, and volume.** Bound labels/tags/attributes,
   histogram buckets, event payloads, log levels, sampling, retention, and export
   paths before adding instrumentation.
7. **Protect privacy and retention.** Classify data fields, minimize collection,
   redact sensitive values at source, avoid raw payload capture, define artifact
   retention/cleanup, and route security-sensitive evidence as above.
8. **Connect signals to response.** Update or verify dashboards, alert rules,
   SLO/SLI definitions, burn-rate or threshold logic, ownership, severity, and
   runbook actions when the instrumentation is meant to page or guide operators.
9. **Validate locally.** Add or update tests, fixtures, snapshots, smoke checks,
   local collectors, generated dashboard/rule validation, or representative
   request/job runs that prove the signal is emitted, bounded, correlated,
   redacted, and actionable.
10. **Report evidence.** Summarize intent, changed signals, validation commands,
    cost/cardinality controls, privacy handling, skipped checks, and remaining
    operational risks.

## Signal Design Checklist

### Structured Logs

- Follow the repository's existing structured format, field names, severity
  levels, and logger setup. Prefer stable fields over parse-dependent prose.
- Include stable event names, component or route class, request/correlation/trace
  IDs, sanitized status or error kind, duration where useful, and enough context
  for diagnosis without raw payloads.
- Keep severity actionable: `debug` for local detail, `info` for expected
  lifecycle events, `warn` for degraded or recovered behavior, and `error` for
  failed user-visible work, lost jobs, or operator action.
- Avoid logging secrets, tokens, cookies, raw headers, request bodies, SQL values,
  credentialed URLs, private paths, unbounded exception payloads, or high-volume
  loop details.

### Metrics

- Use counters for monotonic event totals, gauges for point-in-time state,
  histograms or summaries for latency and size distributions, and explicit units
  in names or metadata.
- Prefer user-visible health signals: request rate, error rate, duration,
  saturation, queue depth, dropped work, dependency health, and business-critical
  success/failure counts.
- Bound labels. Avoid raw user IDs, tenant IDs, emails, URLs with IDs, exception
  messages, SQL text, stack frames, file paths, or request bodies as dimensions.
- Define bucket boundaries, aggregation windows, and reset behavior intentionally;
  dashboards and alerts should not depend on implementation-private metric churn.

### Traces and Spans

- Use low-cardinality span names such as operation or route templates, not raw
  URLs, customer names, IDs, or query text.
- Put spans around inbound requests, message handling, background jobs, outbound
  calls, retries, timeouts, queue boundaries, and important domain decisions only
  when the timing or causal relationship matters.
- Preserve context across async tasks, child jobs, queue messages, and outbound
  requests. If context is intentionally broken, document the reason and the new
  correlation path.
- Record sanitized span attributes, events, status, and error categories. Avoid
  raw payloads and duplicated log content inside spans.

### Correlation and Request IDs

- Generate or normalize correlation/request IDs at ingress when absent; validate
  externally supplied values before echoing them into logs or responses.
- Distinguish request IDs, trace IDs, span IDs, correlation IDs, causation IDs,
  job IDs, tenant IDs, and user IDs. Do not substitute a sensitive identifier for
  a public correlation field.
- Ensure background jobs, retries, fan-out/fan-in work, and scheduled tasks have a
  clear correlation story even when no HTTP request exists.

## Dashboards, Alerts, SLOs, and Runbooks

- Dashboards should answer a specific operator question, show current health,
  expose recent change context where available, and link to the owning service,
  alert, SLO, and runbook.
- Alerts should trigger on symptoms or user impact, not every internal cause.
  Specify threshold, window, severity, owner, routing, deduplication, silence
  expectations, and an actionable first response.
- SLOs need an SLI formula, good/total event definition, measurement window,
  objective, burn-rate or threshold policy, exclusions, and a response when error
  budget is consumed.
- Runbooks should include symptoms, impact, likely causes, safe local inspection
  commands or repository-owned checks, rollback/mitigation paths, escalation, and
  links to dashboards and alerts. Do not embed credentialed URLs, secrets, or
  private console-only steps unless sanitized by repository policy.

## Cardinality, Sampling, Cost, and Retention

- Estimate the volume impact before adding logs, metrics, spans, profiles, or
  exemplars on hot paths. Prefer aggregate metrics over high-volume logs for
  alerting.
- Keep labels, tags, attributes, metric names, span names, and event names from
  growing with users, tenants, files, paths, SQL text, exception text, payloads,
  or arbitrary input.
- Make sampling explicit: head/tail sampling choice, rate, per-error overrides,
  debug escalation, and whether sampled traces still preserve metrics or audit
  requirements.
- Define retention by artifact class. Raw logs, traces, profiles, screenshots,
  incident bundles, network captures, and dashboard exports need access controls,
  cleanup expectations, and sanitized reporting.

## Validation Expectations

- Prefer repository-owned tests and validation recipes over live vendor checks.
  Use vendor-specific commands only when they are existing local project commands
  or examples of local configuration to inspect, and sanitize outputs.
- Verify representative success, expected failure, timeout/retry, cancellation,
  and degraded-dependency paths emit the intended signal once and at the right
  severity.
- Assert redaction for secrets and sensitive fields where practical. Include
  negative checks for high-cardinality labels and raw payload leakage.
- Validate dashboards, alert definitions, SLO formulas, and runbook links when
  they are stored as code or generated artifacts.
- Remove temporary probes before finishing unless they have been converted into
  documented, bounded, production-quality telemetry.
- When validation is partial, report the missing signal, why it could not be
  checked locally, and the operational risk.

## Reporting Template

```markdown
## Observability Summary

- Instrumentation intent:
- Signals changed:
- Correlation/context behavior:
- Dashboards/alerts/SLOs/runbooks changed:
- Cardinality/cost controls:
- Privacy/redaction/retention handling:
- Validation run:
- Not verified / remaining operational risk:
```
