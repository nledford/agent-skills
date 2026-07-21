# Source-to-Landing Ingestion

Load this reference when the affected behavior begins at an external source and
ends at the first durable landing boundary. It applies to batch, micro-batch,
streaming, CDC, replication, file arrival, API extraction, and message capture.
Post-landing business transformation belongs in
[analytics transformations](analytics-transformations.md).

## Establish the Contract

Before implementation or review, identify:

- Source owner, interface, supported extraction method, rate or concurrency
  limits, maintenance windows, retention, and expected change volume.
- Landing owner, format, partitioning, encryption, retention, immutability or
  mutation policy, and the event that makes a batch visible to consumers.
- Business and technical keys, ordering or tie-break fields, source transaction
  markers, time-zone and precision rules, null behavior, and delete semantics.
- Freshness and completeness objectives, reconciliation owner, acceptable lag,
  replay window, and failure escalation path.
- Credential, network, privacy, tenant, and least-privilege boundaries.

Do not call an arbitrary timestamp a watermark. Define its ordering semantics,
tie-break behavior, inclusivity, source-of-truth location, and relationship to a
durably published landing commit.

## Capture State and Publication

- Prefer a source-native log position, version, cursor, or monotonically ordered
  composite key when it provides stronger guarantees than `updated_at` polling.
- Keep capture progress separate from attempt progress. Advance the durable
  checkpoint only after the corresponding landed data and metadata are committed
  and visible under the publication contract.
- Give each attempt and logical batch stable identifiers. Persist source range,
  extraction time, schema version, row or byte counts, outcome, and prior
  checkpoint without embedding sensitive values.
- Make the atomicity boundary explicit. If source read, object write, manifest
  publication, and checkpoint advancement cannot share a transaction, document
  the protocol that prevents gaps and makes duplicates safe.
- State how concurrent runs are excluded, coordinated, or safely merged. When
  lease expiry, fencing, ordering, or partial-failure correctness is generic to a
  distributed protocol, add the repository's concurrency guidance.

## Retry, Replay, Backfill, and Cutover

- Classify failures as retryable, quarantined, operator-actionable, or terminal;
  bound retries and preserve the evidence needed to resume safely.
- Design retries as idempotent or explicitly deduplicated. Validate the actual
  sink write and publish path, not only orchestration retry settings.
- Define replay selection, destination behavior, checkpoint interaction, audit
  trail, and reconciliation. A replay must not silently change the meaning of an
  already published batch.
- Plan backfills with bounded ranges, source protection, separate progress,
  overlap rules, throttling, and a merge or replacement contract.
- For migrations or dual-running cutovers, define start positions, overlap,
  parity checks, ownership switch, rollback window, and cleanup.
- Account for late, out-of-order, duplicated, corrected, and deleted records.
  State when a source retention window makes recovery impossible.

## Fidelity and Schema Evolution

- Preserve source precision, scale, encoding, time zone or offset, nullability,
  binary values, identifiers, and delete/tombstone signals until an intentional
  downstream transformation changes them.
- Record provenance such as source system, object or topic, extraction method,
  capture position, batch identifier, ingestion time, and schema version.
- Define additive, widening, narrowing, rename, removal, and type-conflict
  behavior. Decide whether unknown fields are retained, quarantined, rejected,
  or versioned.
- Avoid silently coercing malformed or out-of-range values. Preserve rejected
  data safely enough to diagnose and replay it without exposing sensitive data.
- Reconcile at the strongest affordable level: batch manifests and counts at a
  minimum, with key ranges, aggregates, checksums, or sampled field comparison
  when risk justifies them.

## Source Protection and Security

- Use supported interfaces and least-privilege read identities. Do not bypass
  source safeguards merely to increase extraction speed.
- Bound connection count, query duration, scan size, batch size, concurrency,
  and retry pressure. Make throttling and backpressure observable.
- Keep credentials out of pipeline definitions, notebooks, logs, manifests, and
  sample payloads. Define rotation and failure behavior for expired identities.
- Classify landed data and metadata. Apply encryption, network isolation, access
  control, retention, deletion, masking, and audit requirements at first landing.
- Treat query-based extraction as SQL work too when correctness, locking, indexes,
  or source load depend on query behavior.

## Validation Evidence

Use representative, bounded fixtures and record exact outcomes for:

- Initial full load and an empty incremental run.
- Multiple changes with the same primary watermark and a deterministic tie-break.
- Insert, update, delete, duplicate delivery, late arrival, and schema change.
- Failure before write, during write, after data write but before publication,
  and after publication but before checkpoint acknowledgement.
- Retry and replay of the same source range without loss or unintended
  multiplication.
- Concurrent or overlapping runs, expired coordination state, and stale workers
  when those states are possible.
- Reconciliation mismatch, quarantine, alerting, and operator recovery.
- Backfill or cutover parity under representative source pressure.

Report the last provably complete source position, how it maps to landed
publication, the evidence for gap and duplicate handling, and any recovery window
that remains unproven.
