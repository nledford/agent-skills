---
name: data-platform-engineering
description: >-
  Data-platform engineering guidance for implementing, changing, reviewing, or
  testing source-to-landing ingestion, post-landing lakehouse or warehouse
  transformations, analytical semantic contracts, Power BI semantic models and
  DAX, and Microsoft Fabric or Power BI operations. Use for CDC, watermarks,
  replay, Delta tables, medallion layers, analytical grain, governed metrics,
  TMDL, RLS or OLS, refresh, promotion, gateways, capacity, recovery, and
  runbooks. Do not use for application domain modeling, physical OLTP database
  design, generic distributed protocols, generic UX, or final release decisions.
---

# Data Platform Engineering

Use this skill for analytical data-platform work from source arrival through
operated business-intelligence consumption. Start with repository-owned evidence,
identify the responsibility lane or lanes that materially change, and load only
their focused references.

The four lifecycle lanes are ingestion, post-landing transformation, BI
consumption, and platform operations. Analytical semantics is a cross-cutting
responsibility: it can accompany transformation or BI work when grain, identity,
history, governed metrics, or business meaning changes.

## Use When

- Building or reviewing batch, streaming, CDC, replication, watermark,
  checkpoint, reconciliation, replay, or source-to-landing behavior.
- Building or reviewing already-landed lakehouse or warehouse transformations,
  medallion layers, Delta-style tables, incremental publication, restatements,
  or technical lineage.
- Defining or changing analytical grain, time, identity, history, conformed
  concepts, governed measures, semantic compatibility, or business lineage.
- Building or reviewing Power BI semantic models, relationships, DAX, storage
  modes, refresh, RLS or OLS, and report-facing model behavior.
- Changing Fabric or Power BI deployment, scheduling, gateways, monitoring,
  capacity, recovery, continuity, or operator runbooks.

Do not use this skill as the primary workflow for:

- Application aggregates, entities, value objects, or business invariants; use
  [`domain-driven-design`](../domain-driven-design/SKILL.md) or the applicable
  architecture skill.
- Physical OLTP schema, query, index, locking, or migration work; use
  [`sql-engineering`](../sql-engineering/SKILL.md) plus the engine-specific skill.
- A generic lease, ordering, consensus, queue, or partial-failure protocol whose
  correctness is not specific to data movement; use the applicable concurrency
  or language/runtime guidance.
- Generic visual design or accessibility with no semantic-model behavior; use
  [`ux-accessibility-review`](../ux-accessibility-review/SKILL.md).
- A final cross-functional ship or hold decision; use
  [`release-readiness`](../release-readiness/SKILL.md). Platform-operability
  evidence can feed that decision without owning it.

## Progressive Reference Routing

Load every reference whose concern is material, but do not load all five merely
because a platform or vendor name appears:

| Concern | Load | Boundary |
|---|---|---|
| Source to first durable landing | [Ingestion](references/ingestion.md) | Extraction, CDC, checkpoints, replay, reconciliation, and source protection |
| Already-landed data to reusable analytical tables | [Analytics transformations](references/analytics-transformations.md) | Layer contracts, incremental transforms, restatements, technical lineage, and publication quality |
| Cross-cutting analytical meaning | [Analytical semantics](references/analytical-semantics.md) | Grain, time, identity, history, governed metrics, semantic compatibility, and business lineage |
| Power BI consumption behavior | [Power BI semantic models](references/power-bi-semantic-models.md) | Model shape, relationships, DAX, storage mode, security, refresh, and report-facing compatibility |
| Operated Fabric or Power BI estate | [Fabric and Power BI operations](references/fabric-power-bi-operations.md) | Promotion, schedules, gateways, monitoring, capacity, recovery, continuity, and runbooks |

When work crosses a boundary, name why each lane is needed. For example, a Gold
table restatement that changes an official KPI needs both transformation and
analytical-semantics guidance. A CDC implementation with a generic overlapping-
lease protocol needs ingestion guidance plus the repository's concurrency
specialist guidance.

## Workflow

1. **Inspect local evidence.** Read schemas, pipeline or notebook definitions,
   SQL, model metadata, deployment configuration, tests, sample contracts,
   monitoring rules, and runbooks. Identify generated artifacts and their source
   of truth before proposing edits.
2. **State scope and ownership.** Name the source and destination, first durable
   landing point, published consumption contract, affected environments,
   responsibility lanes, explicit exclusions, and decision owner.
3. **Define the protected behavior.** Record grain, keys, ordering, time zones,
   null and delete semantics, schema evolution, history, metric definitions,
   authorization, freshness, availability, and recovery expectations that apply.
4. **Trace one representative record and failure.** Follow data and metadata
   through each affected boundary. Include duplicates, late or missing input,
   partial success, retry, replay, restatement, and incompatible contract change
   where relevant.
5. **Design compatibility and recovery before mechanics.** Specify checkpoint or
   publication commits, idempotency, rollback or forward repair, backfill,
   consumer compatibility, observability, and operator action before optimizing.
6. **Implement narrowly.** Preserve established repository conventions and keep
   extraction, transformation, semantic, presentation, and operational concerns
   explicit even when one platform hosts several of them.
7. **Validate at the real boundary.** Prefer executable fixtures, representative
   data, schema or model validation, reconciliation queries, failure injection,
   replay exercises, and deployment or recovery checks over configuration-only
   inspection.
8. **Report evidence and residual risk.** State lanes used, behavior protected,
   checks run and results, skipped checks and why, current unknowns, compatibility
   impact, recovery posture, and required handoffs.

## Ownership Boundaries

- Ingestion owns movement from a source to the first durable landing boundary,
  including capture state, fidelity, replay, and reconciliation.
- Analytics transformations own executable post-landing derivation and technical
  lineage: which jobs, queries, columns, and tables produced a published output.
- Analytical semantics owns semantic and business lineage: what a concept or
  metric means, its grain and history, who governs it, and which consumers depend
  on that meaning.
- Power BI modeling owns the correctness and usability of the BI consumption
  contract, including DAX and model security behavior.
- Platform operations owns reliable promotion and operation of deployed data and
  BI workloads. It supplies, but does not replace, final release-readiness
  judgment.

## Companion Skill Routing

- For a requested review, load [`code-review`](../code-review/SKILL.md) and
  [`review-verification-protocol`](../review-verification-protocol/SKILL.md);
  this skill supplies the data-platform lens, not the finding format or evidence
  gate.
- Load [`api-design`](../api-design/SKILL.md) when source or published data,
  event, webhook, or message contracts are externally consumed.
- Load [`sql-engineering`](../sql-engineering/SKILL.md) and an engine-specific
  skill when SQL semantics, physical schema, transactions, indexes, or migration
  mechanics are material.
- Load [`observability-engineering`](../observability-engineering/SKILL.md) for
  durable telemetry, alerts, SLOs, and operator diagnostics, and
  [`performance-review`](../performance-review/SKILL.md) for evidence-backed
  throughput, latency, query, refresh, or capacity analysis.
- Load [`testing-strategy`](../testing-strategy/SKILL.md) for broad confidence-gap
  analysis or [`test-driven-development`](../test-driven-development/SKILL.md)
  when implementing a behavioral change test-first.
- Load [`documentation-engineering`](../documentation-engineering/SKILL.md) when
  contracts, catalogs, runbooks, or examples are durable documentation work.
- Load [`security-review`](../security-review/SKILL.md) and
  [`security-review-evidence`](../security-review-evidence/SKILL.md) for
  credentials, gateways, identities, tenant isolation, RLS or OLS, sensitive
  data, privacy, audit controls, or sanitized security evidence.

## Evidence and Version Discipline

- Treat repository-owned configuration and executable checks as the primary
  evidence for the system under review. A diagram, UI screenshot, or prose claim
  does not prove deployed behavior by itself.
- Treat vendor limits, licensing, preview status, defaults, feature availability,
  and UI paths as version-sensitive. Verify them against current authoritative
  documentation when they affect the decision, and distinguish documented fact
  from inference.
- Never invent production telemetry, refresh history, query plans, lineage,
  capacity data, or recovery results. Mark unavailable evidence and narrow the
  conclusion.
- Sanitize samples, logs, query results, model exports, screenshots, and support
  bundles. Do not expose credentials, tokens, customer data, or private tenant
  identifiers to prove a finding.

## Completion Criteria

Before handoff, ensure that:

- Each affected responsibility lane and its owner are explicit.
- Grain, identity, time, history, and metric semantics are stated where relevant.
- Incremental, retry, replay, restatement, rollback, and recovery behavior are
  tested or identified as evidence gaps.
- Technical lineage and semantic or business lineage are distinguished.
- Security, observability, performance, compatibility, and operational handoffs
  are included only when the change materially requires them.
- Current platform claims are sourced or clearly labeled as assumptions.
