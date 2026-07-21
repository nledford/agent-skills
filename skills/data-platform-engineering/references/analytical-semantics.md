# Analytical Semantics and Stewardship

Load this cross-cutting reference whenever analytical meaning changes: grain,
time, identity, history, canonical concepts, governed metrics, semantic
compatibility, ownership, or business lineage. It commonly accompanies
[analytics transformations](analytics-transformations.md) or
[Power BI semantic models](power-bi-semantic-models.md); it is not a mutually
exclusive lifecycle stage.

## Establish Ubiquitous Analytical Language

- Name each fact, event, state, dimension, measure, and reporting concept in
  language that owners and consumers recognize.
- Define synonyms, homonyms, deprecated terms, source-local meanings, and the
  canonical analytical meaning. Do not merge concepts merely because labels or
  columns look alike.
- Assign a decision owner and accountable maintainer for each governed concept or
  metric. Record who approves meaning changes and who must be notified.
- Link definitions to executable tables, model objects, tests, reports, and
  policies so documentation does not become an unattached glossary.

## Grain, Time, Identity, and History

For every published analytical object, state:

- What exactly one row represents and which dimensions can vary independently.
- The natural or business identity, technical identity, cross-source matching
  rules, collision behavior, unknown-member behavior, and survivorship policy.
- Which time concepts apply: event, effective, transaction, ingestion,
  publication, calendar, fiscal, snapshot, or observation time.
- Time-zone, boundary, precision, open-ended range, and late-correction rules.
- Whether history is overwritten, appended, versioned, snapshotted, or modeled
  with effective intervals, plus the invariants that prevent gaps or overlap.
- How facts resolve to historical dimension versions and how unmatched or
  changing identities are handled.

Facts, dimensions, and conformed structures are useful when they make these
contracts explicit, not as mandatory shapes for every analytical workload.

## Governed Metric Contracts

Define each governed metric with:

- Business purpose, owner, formula, numerator, denominator, unit, sign, precision,
  rounding, currency or conversion policy, and blank or zero behavior.
- Base row grain, valid dimensions, inclusion and exclusion rules, filters,
  status treatment, distinctness, and allocation or weighting behavior.
- Time basis, aggregation behavior, semi-additive or non-additive dimensions,
  snapshot rules, and expected totals or subtotals.
- Validity period, version, certification state, compatibility promise, and
  representative examples including edge cases.
- Approved source contract and where the metric is materialized or calculated.

Do not certify two implementations as equivalent from matching names alone.
Compare their contracts and results on representative cases.

## Semantic and Business Lineage

Stewardship owns meaning-oriented lineage:

- Connect business terms and metrics to their governed source concepts,
  transformation contracts, semantic-model objects, reports, owners, and known
  downstream decisions.
- Record why a derivation exists, which policy or definition it implements, and
  where meaning changes across boundaries.
- Distinguish declared lineage from observed usage and identify manual extracts,
  spreadsheet steps, opaque calculations, or undocumented report-local measures.
- Use lineage to assess compatibility and notification scope, not as a substitute
  for correctness tests.

Executable job, query, table, and column derivation is technical lineage owned by
the transformation implementation. Both views should connect at published
contracts without pretending either one is complete on its own.

## Evolution and Compatibility

- Classify changes as clarification, additive extension, compatible correction,
  versioned semantic change, or breaking replacement.
- Assess impact on stored history, current output, trend comparability, thresholds,
  alerts, contracts, reports, extracts, APIs, and user decisions.
- Prefer explicit versions or effective dates when old and new meanings must
  coexist. Avoid silently rewriting historical meaning.
- Define migration, dual-run or parity evidence, consumer notice, deprecation,
  cutover, rollback or forward correction, and audit trail.
- Keep approval workflows proportionate. Governance should make consequential
  changes visible without turning ordinary implementation into ceremony.

## Boundary Checks

- Application aggregates and invariant-bearing domain objects belong to domain
  modeling, even if their data later feeds analytics.
- Physical relational schemas, constraints, indexes, transactions, and query
  plans belong to database engineering, even when tables support analytics.
- Post-landing executable derivations and technical lineage belong to analytics
  transformations.
- DAX, relationships, storage modes, model security, and report-facing behavior
  belong to Power BI modeling.
- Privacy classification, access control, retention, and sensitive attributes
  require security and governance evidence in addition to semantic definitions.

## Validation Evidence

- Use small tabular examples that make grain, keys, history, filters, and expected
  metric results inspectable by both technical and business owners.
- Test duplicate, missing, late, corrected, unknown, boundary-time, zero,
  negative, blank, many-to-many, and total/subtotal cases as applicable.
- Compare independent implementations or old and new versions on representative
  periods and explain every material variance.
- Validate that glossary or catalog definitions, table contracts, semantic model,
  tests, and representative reports agree.
- Include negative tests for forbidden dimensions, invalid history intervals,
  double counting, incompatible joins, and unauthorized semantic access.

Before handoff, state the approved meaning, owner, grain and time contract,
identity and history policy, metric examples, semantic-lineage impact,
compatibility decision, evidence obtained, and unresolved governance questions.
