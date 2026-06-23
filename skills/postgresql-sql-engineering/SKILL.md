---
name: postgresql-sql-engineering
description: PostgreSQL and SQL engineering guidance. Use when adding, changing, reviewing, testing, or optimizing PostgreSQL schemas, SQL queries, migrations, transactions, constraints, indexes, views, functions, row-level security, privileges, data behavior, or database performance in any language stack.
---

# PostgreSQL And SQL Engineering

Use this skill for database-native PostgreSQL and SQL work independent of the
application language. Keep database invariants explicit, changes deployable, and
query behavior proven with the target database. Use
[`sql-engineering`](../sql-engineering/SKILL.md) for database-neutral SQL first
passes when the target engine is unknown or multiple engines are involved.

## Use When

- Designing or reviewing tables, constraints, indexes, views, functions,
  triggers, migrations, transactions, privileges, RLS, or PostgreSQL extensions.
- Writing or reviewing SQL queries, query plans, pagination, bulk operations,
  reporting queries, or data repair scripts.
- A change needs database correctness, performance, security, observability, or
  rollback evidence.
- Rust code uses SQLx or SeaQuery against PostgreSQL: use this skill for
  database design and [`rust-persistence-sql`](../rust-persistence-sql/SKILL.md)
  for Rust adapter, execution, and query-builder details.

Do not use this skill for generic in-memory domain logic, ORM-only API usage
with no SQL/schema behavior, or SQLite-specific behavior except when comparing
it to PostgreSQL.

## Workflow

1. Inspect the real database surface: migrations, schema dumps, SQL files,
   query builders, ORM mappings, seed data, test fixtures, migration tool,
   database version, extensions, and CI database setup.
2. State the data behavior before implementation. Use BDD-style examples for
   observable rules such as uniqueness, authorization, lifecycle transitions,
   conflict handling, and partial-write prevention.
3. Model the boundary. Use DDD language for entities, value objects,
   aggregate-like consistency boundaries, repositories, and invariants. Do not
   let table shape leak into core domain APIs without a deliberate adapter.
4. Design schema and migration order: new objects, backfill, constraints,
   indexes, locks, deploy compatibility, rollback, and validation queries.
5. Implement SQL with bound parameters, explicit columns, deliberate
   transaction scope, and safe error mapping at the application edge.
6. Verify with the target engine: migration from empty database, migration from
   a representative previous schema, focused query tests, and plan inspection
   for performance-sensitive paths.

## Schema And Migration Checklist

- Tables have stable primary keys when identity matters, meaningful foreign
  keys, `NOT NULL` for required facts, and `CHECK`, `UNIQUE`, exclusion, or
  domain constraints for invariants the database must enforce.
- Normalize first. Denormalize, materialize, or duplicate only for measured read
  needs with an ownership and refresh story.
- Choose types by semantics: `TEXT` for ordinary strings, `NUMERIC` for exact
  decimal money-like values, `TIMESTAMPTZ` for instants, `DATE` for dates,
  `BOOLEAN` for two-state facts, JSONB only for semi-structured data, and
  enums/domains/lookup tables when they fit the change cadence.
- Index foreign key columns manually when joins or parent updates/deletes need
  them; PostgreSQL does not create those indexes automatically.
- Indexes have a query rationale. Match predicates, join keys, sort order,
  uniqueness, and partial or expression predicates to real access paths.
- Migration files are ordered for safe rollout. Call out lock-heavy DDL,
  backfills, table rewrites, `CREATE INDEX CONCURRENTLY`, data loss, and
  app/schema compatibility windows.
- Views and materialized views declare security, staleness, refresh, ownership,
  and indexing assumptions.

## Query And Transaction Checklist

- Select explicit columns. Avoid `SELECT *` unless the whole row is the
  contract.
- Bind user-controlled values. Never concatenate untrusted input into SQL.
- Predicates are sargable where possible and line up with available indexes.
- Joins preserve intended cardinality and do not accidentally multiply rows.
- Pagination is stable under inserts and deletes; prefer keyset pagination for
  large ordered result sets.
- `NULL`, collation, case sensitivity, timezone, numeric precision, and enum
  evolution are explicit where they affect behavior.
- Transactions cover exactly one consistency boundary. Name isolation,
  lock-ordering, retry, idempotency, and deadlock assumptions when concurrent
  writes matter.
- Bulk writes use set-based SQL, `COPY`, or batched statements when appropriate
  instead of row-at-a-time loops.

## PostgreSQL Features

- Use B-tree indexes for normal equality/range/order queries; GIN for JSONB,
  arrays, and full-text search; GiST/SP-GiST for ranges, geometry, and exclusion
  constraints; BRIN for very large naturally ordered data.
- JSONB works best for optional or variable attributes. Promote frequently
  filtered or constrained fields to columns, generated columns, expression
  indexes, or constraints when they become core behavior.
- Arrays are useful for ordered scalar lists, not many-to-many relationships
  that need referential integrity.
- Range types plus exclusion constraints are strong tools for non-overlap rules
  such as bookings and schedules.
- Row-level security and privileges are security boundaries. Review actor,
  role, policy predicate, bypass paths, and test coverage before relying on
  them.
- Extensions such as `pg_trgm`, `pgcrypto`, `citext`, PostGIS, TimescaleDB, or
  pgvector must have a clear product need, migration story, and operational
  ownership.

## Commands

Prefer repository recipes when they exist. Useful direct commands include:

```sh
psql "$DATABASE_URL" -f path/to/query.sql
psql "$DATABASE_URL" -c "\\d+ table_name"
psql "$DATABASE_URL" -c "EXPLAIN (ANALYZE, BUFFERS) SELECT ..."
sqlx migrate run
sqlx migrate revert
```

Use SQLx migration commands only when the repository uses SQLx. Otherwise use
the repository's migration tool or SQL deployment recipe.

For mutating `EXPLAIN ANALYZE`, use a transaction and rollback on disposable or
safe data:

```sql
BEGIN;
EXPLAIN (ANALYZE, BUFFERS) UPDATE ...;
ROLLBACK;
```

## Testing And Review

- Use TDD for query bugs when practical: write a failing fixture or integration
  test that proves the old behavior is wrong.
- Use BDD examples for data behavior users can observe: duplicate prevention,
  authorization, lifecycle state, conflict responses, and atomicity.
- Test constraints and transactions against PostgreSQL, not only mocks or
  SQLite.
- Review plans for expensive queries with representative data and current
  statistics. Do not claim performance improvement without comparable evidence.
- Review security for injection, least privilege, RLS policy coverage, secret
  handling, audit logs, and safe error messages.
- Review observability for slow queries, migration failures, pool saturation,
  deadlocks, lock waits, and maintenance signals.

## Anti-Patterns

- Treating application validation as a substitute for database constraints on
  critical invariants.
- Adding indexes speculatively without query, cardinality, and write-cost
  rationale.
- Assuming `EXPLAIN ANALYZE` is read-only.
- Hiding long or multi-domain transactions behind generic repository helpers.
- Storing relational facts in JSONB because it is convenient.
- Claiming PostgreSQL behavior from tests that only ran on SQLite or mocks.

## Successful Use

The final handoff names the data behavior protected, migrations or SQL changed,
database-specific checks run, query-plan or performance evidence when relevant,
and any deploy or rollback risk that remains.
