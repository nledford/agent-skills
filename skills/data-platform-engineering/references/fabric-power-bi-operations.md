# Fabric and Power BI Operations

Load this reference when deployed Fabric or Power BI workloads change promotion,
configuration, scheduling, gateways, monitoring, capacity, recovery, continuity,
or operator response. This lane assesses platform operability. A final
cross-functional ship or hold decision belongs to release readiness.

## Deployment and Environment Control

- Inventory deployment units, source-controlled artifacts, generated artifacts,
  workspaces or environments, dependencies, owners, and promotion order.
- Separate environment-specific configuration, connections, identities, gateway
  bindings, schedules, parameters, and secrets from portable definitions.
- Define how drift is detected between repository source, deployment tooling, and
  live state. A successful command does not by itself prove that the intended
  artifact version is active.
- Make promotion idempotent or explicitly state replacement behavior. Define
  preconditions, validation, partial-failure handling, rollback or forward fix,
  and evidence retained for each environment.
- Verify current vendor behavior for deployment features, APIs, tenant settings,
  limitations, and licensing that affect the procedure.

## Scheduling and Dependency Operations

- Map triggers, schedules, time zones, calendars, dependencies, concurrency,
  timeout, retry, cancellation, and catch-up behavior.
- Define freshness and completion signals at the consumer-visible boundary, not
  only individual activity success.
- Prevent overlapping or out-of-order runs from corrupting checkpoints,
  publications, refreshes, or downstream dependencies. Route generic lease,
  fencing, or ordering protocols to concurrency review.
- State how missed schedules, prolonged upstream delay, partial completion,
  maintenance, and paused capacity are detected and recovered.
- Bound retry storms and backfills so recovery does not overwhelm sources,
  gateways, capacity, or downstream consumers.

## Observability and Incident Response

- Define actionable signals for freshness, completeness, failures, retries,
  duration, queueing, throttling, gateway health, refresh status, data quality,
  capacity saturation, and recovery progress.
- Connect alerts to an owner, severity, routing, deduplication, threshold or SLO,
  dashboard context, and safe first response.
- Correlate source range, pipeline or job run, landing batch, transformation
  publication, semantic refresh, and deployment version without placing sensitive
  row values or credentials in telemetry.
- Validate alert delivery and runbook usefulness with representative failure or
  controlled exercises; dashboard existence alone is not evidence of response.
- Distinguish platform telemetry gaps from workload-correctness gaps and hand the
  latter to the lane that owns the workload.

## Capacity, Performance, and Cost

- Establish workload shape: schedules, interactive concurrency, batch peaks,
  refresh windows, data volume, query patterns, background work, and growth.
- Use measured utilization, throttling, queueing, duration, failure, and cost
  evidence under representative periods. Do not extrapolate capacity from a
  single quiet or incident interval.
- Define thresholds, headroom, autoscaling or manual scaling policy where
  available, noisy-neighbor controls, and the operator action for saturation.
- Test that recovery, backfill, deployment, and peak interactive use can coexist
  or define explicit scheduling and degradation policy.
- Treat SKU behavior, quotas, billing, and feature availability as
  version-sensitive and verify them before making cost or capacity claims.

## Gateways, Identity, and Configuration Security

- Inventory identity boundaries for deployment, source access, gateways,
  scheduled jobs, semantic refresh, monitoring, and operator access.
- Apply least privilege, managed or short-lived credentials where supported,
  rotation, expiry monitoring, revocation, and break-glass controls.
- Verify gateway clustering or redundancy, version management, connectivity,
  certificate or proxy dependencies, patching ownership, and failure detection
  from repository or controlled operational evidence.
- Keep secrets and tenant-specific identifiers out of source, command history,
  logs, screenshots, exports, and incident evidence. Sanitize live-state samples.
- Test unauthorized and expired-identity failure paths without exposing real
  credentials.

## Recovery and Continuity

- Define recovery objectives for configuration, code, data, semantic models,
  refresh state, gateways, and operational metadata. State what cannot be
  reconstructed from source control alone.
- Document replay or resume boundaries, retained source window, checkpoint repair,
  backfill, republish, model rehydration, and reconciliation after recovery.
- Exercise partial deployment, failed schedule, unavailable gateway, corrupted or
  missing configuration, capacity interruption, and regional or workspace loss as
  risk requires.
- Prove restore and failover procedures with timestamps, observed results,
  dependencies, data-loss window, cleanup, and owner sign-off. An untested backup
  is not recovery evidence.
- Keep rollback distinct from recovery: rollback restores a prior deployable
  version; recovery restores service and trustworthy state after failure.

## Runbook and Handoff Evidence

An operator runbook should include symptoms, impact, ownership, safe inspection,
decision points, mitigation, retry or replay bounds, rollback and recovery,
validation, escalation, communications, and cleanup. Commands should be scoped,
non-destructive by default, and free of embedded credentials or private payloads.

Before handoff, record:

- Environment and deployed-version evidence, configuration and drift status.
- Schedule, dependency, alert, gateway, capacity, and identity checks performed.
- Recovery or replay exercises and measured objectives.
- Known evidence gaps, manual steps, version-sensitive assumptions, and residual
  operational risk.
- The operability evidence supplied to release readiness when a final ship or hold
  decision is requested.
