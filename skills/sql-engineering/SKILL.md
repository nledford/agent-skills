---
name: sql-engineering
description: Database-neutral SQL engineering guidance. Use when reading, writing, refactoring, reviewing, testing, or optimizing SQL queries, schemas, migrations, tables, views, functions, triggers, constraints, indexes, transactions, reporting queries, or data behavior before choosing a database-specific skill. Use PostgreSQL or SQLite skills for engine-specific behavior.
---

# SQL Engineering

Use this skill for database-neutral SQL work and as the first pass when the target
engine is unknown or multiple engines are involved. Add PostgreSQL or SQLite
specialist guidance when engine semantics matter.

## Use When

- Reading, writing, refactoring, or reviewing SQL queries, schemas, migrations,
  tables, views, functions, triggers, constraints, indexes, transactions,
  reporting queries, data repair scripts, or query performance.
- Translating business rules into database constraints, transaction boundaries,
  or query behavior.
- Comparing SQL produced by ORMs/query builders with the behavior the database
  must enforce.

Do not rely on this skill alone for PostgreSQL-specific features, SQLite-specific
semantics, SQLx/SeaQuery adapter code, or ORM API usage with no SQL/schema
behavior. Use [`postgresql-sql-engineering`](../postgresql-sql-engineering/SKILL.md),
[`sqlite-sql-engineering`](../sqlite-sql-engineering/SKILL.md), or
[`rust-persistence-sql`](../rust-persistence-sql/SKILL.md) as appropriate.

## Workflow

1. Identify the target engine, version, migration tool, schema source of truth,
   seed/fixture strategy, generated SQL, and CI database setup.
2. State the data behavior before editing: invariants, cardinality, lifecycle,
   authorization, conflict handling, atomicity, retention, and rollback needs.
3. Read existing SQL in context: callers, migrations, constraints, indexes,
   transactions, tests, and production data assumptions.
4. Design schema/query changes with deploy order, data backfill, compatibility,
   rollback, lock/latency impact, and validation queries in mind.
5. Implement with explicit columns, bound parameters, narrow transactions,
   meaningful constraints, and tested error mapping.
6. Verify against the target database engine, not mocks, when SQL semantics are
   the behavior being changed.

## Reading and Refactoring SQL

- Trace each query from caller inputs to returned data and side effects.
- Confirm join cardinality, filtering order, aggregation level, grouping keys,
  window frames, CTE materialization assumptions, sort order, pagination, null
  behavior, collation, time zones, and numeric precision.
- Preserve behavior with characterization tests or before/after result checks
  before rewriting complex SQL.
- Separate readability refactors from semantic changes. Avoid reformatting or
  reordering large queries while changing behavior unless it is necessary for
  review.

## Schema, Constraints, and Migrations

- Use constraints for invariants the database must enforce: primary keys, foreign
  keys, `NOT NULL`, `UNIQUE`, `CHECK`, exclusion-like rules, and valid state
  transitions where the engine supports them.
- Migration plans should cover empty database, representative previous schema,
  backfill, validation, lock-heavy DDL, data loss, rollback, app/schema
  compatibility windows, and deployment order.
- Indexes require a query rationale. Match predicates, joins, ordering,
  uniqueness, and write cost to real access paths.
- Views, functions, and triggers need ownership, security, performance, error,
  testing, and migration stories. Do not hide core domain rules in triggers
  unless the repository intentionally treats the database as the rule owner.

## Query and Transaction Checklist

- Select explicit columns unless the full row is the documented contract.
- Bind user-controlled values; never concatenate untrusted input into SQL.
- Keep predicates sargable where practical and aligned with available indexes.
- Ensure joins do not accidentally multiply rows or turn required rows optional.
- Make pagination stable under inserts/deletes; prefer keyset pagination for
  large ordered result sets.
- Keep transactions scoped to one consistency boundary. Name isolation,
  lock-ordering, idempotency, retry, and deadlock assumptions when writes are
  concurrent.
- Prefer set-based operations for bulk work; avoid row-at-a-time loops unless the
  domain truly needs per-row side effects.

## Advanced Techniques

- Use CTEs, window functions, lateral joins, recursive queries, upserts, partial
  indexes, generated columns, materialized views, or JSON operations only when
  they simplify a real query or enforce a real invariant.
- Check whether a technique is engine-specific before relying on it. Document the
  target engine if portability is not a goal.
- For performance claims, compare plans or timings under comparable conditions
  and representative data. Do not infer performance from query appearance alone.

## Testing and Review

- Use BDD-style examples for observable data behavior such as duplicate
  prevention, authorization, lifecycle state, conflict responses, and atomicity.
- Use TDD for query bugs when practical: a fixture or integration test should fail
  on the old behavior for the expected reason.
- Test migrations and constraints against the actual engine. Mocks and in-memory
  substitutes do not prove SQL semantics.
- Review security for injection, least privilege, RLS/policies when applicable,
  secret handling, audit logs, and safe error messages.

## Anti-Patterns

- Treating application validation as the only protection for critical data
  invariants.
- Adding indexes speculatively without query evidence and write-cost awareness.
- Claiming one database engine proves another engine's behavior.
- Hiding long or multi-domain transactions behind generic repository helpers.
- Storing relational facts in schemaless blobs because the first query was easy.
