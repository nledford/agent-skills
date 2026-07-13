---
name: postgresql-sql-engineering
description: PostgreSQL and SQL engineering guidance. Use when adding, changing, reviewing, testing, or optimizing PostgreSQL schemas, SQL queries, migrations, transactions, constraints, indexes, views, functions, row-level security, privileges, data behavior, or database performance in any language stack. Use api-design when migrations or query outputs affect published contracts and observability-engineering for PostgreSQL telemetry signals.
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

## Security Review Routing

Load [`security-review`](../security-review/SKILL.md) when PostgreSQL work
touches roles, privileges, RLS/policies, `SECURITY DEFINER`, extensions,
dynamic SQL or injection risk, tenant isolation, audit logs, sensitive
migrations/backfills, data repair scripts, secrets, or production-data access.
Pair it with [`security-review-evidence`](../security-review-evidence/SKILL.md)
when evidence includes redacted SQL, `EXPLAIN` output, schema diffs,
audit/log samples, dumps, or migration artifacts.

## API and Observability Routing

- Load [`api-design`](../api-design/SKILL.md) when PostgreSQL migrations, views,
  functions, outbox/event rows, generated schemas, reporting outputs, or
  constraint-error mapping affect an external contract or compatibility promise.
- Load [`observability-engineering`](../observability-engineering/SKILL.md) when
  PostgreSQL work changes slow-query, migration, pool, lock wait, deadlock,
  replication, maintenance, dashboard, alert, or runbook signals.

## Workflow

1. Inspect the real database surface: migrations, schema dumps, SQL files,
   query builders, ORM mappings, seed data, test fixtures, migration tool,
   target PostgreSQL major version, extensions, and CI database setup. Verify
   version-sensitive behavior in the official documentation for that target
   version, not only the current documentation.
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

## RLS, Privileges, And Privileged Functions

- Model the actual application role, migration role, and object-owner role;
  test the policy with representative connections or `SET ROLE`, not just a
  privileged development connection. Superusers and roles with `BYPASSRLS`
  always bypass RLS; table owners usually do too unless the table uses `FORCE
  ROW LEVEL SECURITY`.
- Scope each policy deliberately by command and `TO` role. `USING` controls
  which existing rows are visible or targetable by `SELECT`, `UPDATE`, and
  `DELETE`; `WITH CHECK` controls proposed rows for `INSERT` and `UPDATE`.
  Ordinary table grants still authorize commands: RLS filters authorized access,
  it does not replace grants.
- Test allowed and denied reads, inserts, updates, and deletes for the app role,
  migration/owner behavior where relevant, and expected bypass behavior. Include
  cross-tenant and policy-absent cases.
- Use `SECURITY DEFINER` only for a narrow, reviewed privilege boundary. Give
  the function a trusted owner, fully qualify referenced objects, and set a
  trusted `search_path` with `pg_temp` last (for example, `SET search_path =
  app_private, pg_temp`); do not search schemas writable by callers.
- Create privileged functions transactionally, revoke default `PUBLIC` execute
  immediately, then grant execute only to intended roles. Keep the function
  owner and its table privileges least-privileged and explicit.

## Commands

Prefer repository recipes when they exist. Useful direct commands include:

```sh
psql -f path/to/query.sql
psql -c "\\d+ table_name"
psql -c "EXPLAIN (ANALYZE, BUFFERS) SELECT ..."
sqlx migrate run
sqlx migrate revert
```

Use SQLx migration commands only when the repository uses SQLx. Otherwise use
the repository's migration tool or SQL deployment recipe. Use a repository-owned
recipe, libpq defaults, or a named `PGSERVICE` configured outside the command;
never put credentialed DSNs in argv, shell history, logs, examples, or reports.

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
