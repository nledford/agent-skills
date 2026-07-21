# Post-Landing Analytics Transformations

Load this reference when data is already durably landed and the affected behavior
derives, cleans, conforms, enriches, aggregates, or publishes reusable analytical
tables. Extraction and source capture belong in [ingestion](ingestion.md).

## Define Layer and Publication Contracts

- Name the input and output datasets, owners, row grain, business and technical
  keys, partition or clustering choices, freshness, retention, and consumers.
- Describe what each layer guarantees rather than relying on Bronze, Silver,
  Gold, curated, or warehouse labels. State which layer preserves source
  fidelity, resolves quality, conforms concepts, and publishes stable contracts.
- Identify the publication boundary: when output becomes queryable, how partial
  output is hidden, how consumers detect a complete version, and how failed
  publication is repaired.
- Keep transformation logic reproducible from declared inputs, code, parameters,
  and reference-data versions. Make nondeterministic inputs explicit.

## Prove Transformation Correctness

- Trace representative records through filters, joins, unions, deduplication,
  window functions, type coercion, defaulting, enrichment, and aggregation.
- Check join cardinality and unmatched-row behavior before and after every join.
  Detect unexpected multiplication rather than masking it with `DISTINCT`.
- State null, blank, invalid, late, duplicate, corrected, and deleted-record
  behavior. Quarantine should preserve diagnosable provenance and a recovery path.
- Protect numeric precision, time zones, calendar rules, encoding, and stable
  identifiers across formats and engines.
- Define quality checks as executable contracts with owner, threshold, severity,
  disposition, and recovery action. Counts alone rarely prove semantic accuracy.

## Incremental Processing and Restatement

- Define the incremental selector, overlap window, affected-row or partition
  calculation, merge key, update and delete semantics, and durable completion
  marker.
- Prove that repeated processing of the same input is idempotent or intentionally
  versioned. Include failure between output write and publication acknowledgement.
- State how late facts, corrected dimensions, reference-data changes, and
  slowly-changing history propagate to already published output.
- Treat restatement as a contract: scope selection, dependency order, consumer
  visibility, reconciliation, compatibility, audit trail, and rollback or
  forward repair.
- Ensure incremental and full-rebuild paths produce equivalent results for the
  same declared inputs, or document and test the intended difference.

## Table and Workload Design

- Choose table format, partitioning, clustering, compaction, file sizing,
  statistics, retention, and vacuum or cleanup from measured workload and
  recovery needs, not generic platform folklore.
- Consider write amplification, small-file growth, concurrency, schema evolution,
  snapshot or time-travel requirements, and reader compatibility.
- Preserve enough immutable or versioned input to replay transformations for the
  required recovery and audit window.
- Validate optimization claims with representative query plans, scans, timings,
  file counts, or platform metrics under comparable conditions.

## Technical Lineage

Transformation ownership includes technical execution lineage:

- Record which pipeline, job, notebook, query, model, code version, and parameters
  produced each published dataset version.
- Map input tables and columns to output tables and columns, including filters,
  aggregations, lookups, and opaque transformations that prevent field-level
  tracing.
- Distinguish observed runtime lineage from parsed or declared lineage and note
  gaps caused by dynamic SQL, notebooks, external code, or manual steps.
- Keep operational provenance such as run, batch, partition, and publication IDs
  available without exposing sensitive row values.

The meaning and governance of concepts and measures is semantic or business
lineage; load [analytical semantics](analytical-semantics.md) when that changes.

## Validation Evidence

Test with small, readable fixtures plus representative scale where performance
matters:

- Expected row-level derivation and output grain.
- One-to-many and many-to-many joins, unmatched keys, duplicates, and null keys.
- Late, corrected, and deleted records plus changing reference data.
- Empty input, malformed input, quarantine, and threshold breach.
- Repeated incremental run, interrupted publication, replay, targeted restatement,
  and full rebuild equivalence.
- Schema addition, compatible widening, incompatible change, and consumer-facing
  publication behavior.
- Reconciliation from landed input through published output, with explicit
  explanations for filtered, rejected, or aggregated records.

Before handoff, report the protected output contract, incremental and restatement
semantics, technical-lineage evidence, quality disposition, validation results,
and any untested recovery or workload assumption.
