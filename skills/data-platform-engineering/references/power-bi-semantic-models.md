# Power BI Semantic Models

Load this reference when Power BI model behavior is material: model shape,
relationships, DAX, storage mode, refresh semantics, RLS or OLS, report-facing
compatibility, or query performance. Load
[analytical semantics](analytical-semantics.md) too when governed meaning, grain,
identity, history, or metric ownership changes.

## Inspect the Model as Source

- Prefer repository-owned project, TMDL, model, deployment, test, and sample-query
  artifacts over screenshots or manually transcribed UI state.
- Identify generated files and their source of truth before editing. Keep changes
  narrow enough that model diffs remain reviewable.
- Inventory tables, columns, measures, hierarchies, relationships, calculation
  groups, roles, perspectives, partitions, storage modes, refresh policies, and
  consumers affected by the change.
- Treat undocumented tenant settings, service behavior, feature availability,
  licensing, and defaults as unknown until verified against current authoritative
  evidence.

## Model Shape and Relationships

- State the grain, key, uniqueness, null behavior, and role of every affected
  table. Prefer a clear fact-and-dimension shape when it matches the domain, but
  do not force one when a different shape has an evidenced purpose.
- Validate relationship endpoints, cardinality, active state, referential
  assumptions, and filter direction against actual key profiles.
- Use bidirectional filtering and many-to-many relationships only with an
  explicit semantic need and tests for ambiguity, double counting, and query
  behavior.
- Model role-playing dates, inactive relationships, bridge tables, unknown
  members, and slowly changing dimensions intentionally.
- Keep technical columns hidden when they do not help consumers; expose stable
  names, descriptions, formats, folders, sort-by behavior, hierarchies, and
  default summarization that support correct self-service use.

## DAX Correctness

- Write the metric contract before the expression: base grain, formula, filters,
  inclusion rules, time basis, dimensional validity, blank or zero behavior, and
  expected totals.
- Reason explicitly about filter context, row context, context transition,
  expanded tables, relationship propagation, and evaluation at detail, subtotal,
  and grand-total levels.
- Test single and multi-select filters, no selection, missing keys, blanks, zero
  denominators, negative values, duplicate identifiers, many-to-many paths, and
  non-additive totals where relevant.
- Prefer reusable base measures and explicit compositions over duplicated report-
  local logic. Remove unused objects only after checking dependencies and
  compatibility.
- Treat time-intelligence behavior as a calendar and data-completeness contract,
  not a function-name shortcut.

## Storage, Refresh, and Compatibility

- Choose Import, DirectQuery, Direct Lake, composite, aggregation, or hybrid
  behavior from freshness, latency, volume, concurrency, source load, security,
  cost, and recovery evidence. Platform support and limitations are
  version-sensitive.
- Define partition boundaries, incremental-refresh or change-detection semantics,
  late data, correction, deletion, restatement, and full-refresh fallback.
- Verify model changes against representative existing reports, queries,
  bookmarks, field references, exports, APIs, and downstream models.
- Classify renames, removals, type changes, relationship changes, format changes,
  and metric-definition changes by compatibility impact; provide a migration or
  versioning path for breaking changes.

## Model Security

- Treat RLS and OLS as authorization controls. Define identity mapping, role
  membership, tenant or organizational scope, default-deny behavior, and how
  unknown or malformed identities behave.
- Test authorized and unauthorized personas, multiple-role combinations,
  relationship propagation, bridge behavior, hidden versus protected objects,
  export paths, and any privileged bypass.
- Keep credentials, service principals, gateway secrets, and sensitive sample
  values outside model source, logs, screenshots, and test reports.
- Verify that upstream permissions, model permissions, build access, sharing,
  downstream models, and report delivery do not undermine the intended policy.

## Performance and Usability Evidence

- Use representative report queries, filter combinations, concurrency, data
  volume, refresh windows, and cold or warm cache conditions. Record the tools,
  environment, and limits of the measurement.
- Inspect expensive expressions, high-cardinality columns, relationship paths,
  storage-engine versus formula-engine work, partition pruning, source queries,
  and refresh resource use when supported by available evidence.
- Do not trade correctness or maintainability for a micro-optimization without a
  measured bottleneck and regression coverage.
- Check discoverability, naming, descriptions, formats, folders, default behavior,
  error or blank states, and localization when the model is a self-service
  interface. Route visual-layout and accessibility findings to UX review.

## Validation Evidence

- Validate model metadata or source with repository-supported tooling.
- Run compact DAX query fixtures for expected detail rows, filter combinations,
  subtotals, totals, blanks, edge dates, security personas, and compatibility.
- Reconcile representative model results to the governed metric contract and
  published analytical tables; explain every material variance.
- Exercise refresh success, empty increment, late correction, interruption,
  retry, and full fallback when refresh behavior changes.
- Capture representative query and refresh performance before and after material
  performance changes.

Before handoff, report the affected semantic contract, model objects, security
behavior, refresh and compatibility impact, executable evidence, version-sensitive
assumptions, and remaining report or operational risk.
