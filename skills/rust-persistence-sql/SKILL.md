---
name: rust-persistence-sql
description: Rust persistence, SQLx, SeaQuery, and SQL-library guidance. Use when adding, changing, reviewing, or testing SQLx queries/macros, SeaQuery builders, SeaORM, Diesel, raw SQL choices, Rust database adapters, pools, transactions, offline query metadata, migrations invoked from Rust, SQLite support, database-backed Rust tests, dynamic SQL construction, or persistence boundaries. Use sql-engineering, postgresql-sql-engineering, or sqlite-sql-engineering for database-native design.
---

# Rust Persistence, SQLx, And SeaQuery

Use this skill for database-backed Rust work. Keep persistence adapters explicit,
keep core domain rules independent of database mechanics where practical, and
validate both Rust types and database behavior. For database-neutral SQL design,
use [`sql-engineering`](../sql-engineering/SKILL.md). For language-independent
PostgreSQL schema, SQL, query-plan, security, and migration design, use
[`postgresql-sql-engineering`](../postgresql-sql-engineering/SKILL.md). For
SQLite-native schema, transaction, and test-database behavior, use
[`sqlite-sql-engineering`](../sqlite-sql-engineering/SKILL.md). Use
[`hexagonal-architecture`](../hexagonal-architecture/SKILL.md) when deciding
whether repositories, database gateways, transactions, or query services should
be outbound ports and adapters rather than core domain code.

## Workflow

1. Inspect the persistence setup: `Cargo.toml` SQLx and SeaQuery dependencies,
   feature flags, migrations, `DATABASE_URL` conventions, `.sqlx/` offline
   metadata, pool types, transaction helpers, repository recipes, seed/fixture
   strategy, and CI database services.
2. Model the boundary. Use DDD language for tables, aggregates, invariants, and
   repository/service responsibilities. Do not let query row shapes become the
   core domain model by accident.
3. When storage behavior changes, design SQL and migrations with the database
   skill first, then implement the Rust adapter.
4. Implement SQLx or SeaQuery access with typed parameters, explicit result
   mapping, narrow transactions, and safe error conversion.
5. Test at the right layer: pure domain tests, SQLx integration tests against
   the target database, and end-to-end tests only for user-visible workflows.
6. Update SQLx offline query metadata or document why it is not used by the
   repo.

## SQLx Checklist

- Prefer compile-checked SQLx macros such as `query!` or `query_as!` when the
  query shape is static and the repository supports online or offline checking.
- Use dynamic SQL only when the shape is genuinely dynamic; bind values instead
  of formatting user input into SQL.
- Map nullable columns, database enums, time types, UUIDs, JSON, and numeric
  precision deliberately.
- Keep pool acquisition, transaction scope, and timeout behavior explicit.
- Convert database errors at the adapter edge. Preserve enough context for logs
  while returning safe domain or API errors.
- For PostgreSQL and SQLite support in one codebase, test both. SQL dialects,
  type affinity, locking, migrations, and constraint behavior differ.

Prefer `sqlx` when:

- Queries are mostly static and readable as SQL.
- Compile-time checked queries or offline query checking are valuable.
- Query shape is known ahead of time.
- Migrations, pools, transactions, and row mapping are the main concern.
- A query builder would obscure simpler explicit SQL.

## SeaQuery Checklist

Use SeaQuery for dynamic SQL construction in Rust when it is already a project
convention or when runtime query shape would otherwise require unsafe or
unreviewable string assembly.

- Inspect the installed version and features before editing: `sea-query`,
  `sea-query-sqlx`, backend features such as `backend-postgres`,
  `backend-sqlite`, or `backend-mysql`, and existing `Iden`/identifier enums.
- Prefer SeaQuery when many filters, sorts, joins, projections, predicates, or
  dialect targets are optional and composition improves clarity.
- Avoid SeaQuery when a plain `sqlx::query!`, `query_as!`, or `query_file!` is
  clearer, compile-time checking matters more, or dialect-specific SQL is easier
  to review directly.
- Keep query builders small and close to the persistence adapter or query
  service. Do not leak SeaQuery types into core domain models unless the crate
  is explicitly a database adapter.
- Preserve parameter binding. Prefer APIs that build SQL plus values for the
  driver; reserve value-injected SQL strings for tests, sanitized logs, and
  debugging.
- Keep generated SQL reviewable. Name reusable predicates, avoid deeply nested
  builder chains, and snapshot only stable SQL shapes where that helps review.
- Make dialect choices explicit. PostgreSQL, SQLite, and MySQL differ in
  placeholders, quoting, upsert syntax, return clauses, JSON, arrays, date/time,
  locking, and DDL.

Prefer SeaQuery when:

- Query shape is genuinely dynamic.
- Many optional filters, sorts, joins, projections, or predicates must compose.
- The same query-building logic targets multiple SQL dialects.
- Repeated string concatenation would become unsafe or hard to review.
- The project already uses SeaQuery consistently.
- An AST-style builder improves maintainability.

Use SeaQuery with `sqlx` when SeaQuery builds the SQL and bind values while
SQLx remains responsible for execution, pooling, transactions, migrations, and
row mapping. In projects using `sea-query-sqlx`, inspect the installed version;
current docs expose a `SqlxBinder` integration that builds SQLx-compatible SQL
and values for `sqlx::query_with`.

Common commands:

```sh
sqlx migrate info
sqlx migrate run
sqlx migrate revert
cargo sqlx prepare
cargo sqlx prepare --check --workspace
SQLX_OFFLINE=true cargo check --workspace --all-targets
```

Adapt command names to the repository's SQLx CLI version and recipes. Some
projects use `cargo sqlx ...`; others install a standalone `sqlx` binary.

## Schema And Migration Review

- Database invariants live in the database skill; the Rust review checks that
  Rust types, query mappings, migrations, and domain errors line up with them.
- SQLx migrations are invoked through the repository's chosen workflow. Do not
  assume `sqlx migrate add/run/revert` is authoritative when the repo has a
  custom migration generator or schema source of truth.
- Rust migration code, embedded migrations, and startup migration hooks have a
  rollback and deployment story. Avoid surprise DDL on application boot unless
  that is explicit repository policy.
- Seed data and fixtures are deterministic, isolated, and safe for repeated test
  runs.

## SQL Library Choice

- Prefer raw SQL with SQLx macros when queries are static, readability matters,
  compile-time checking is available, and SQL expresses the behavior directly.
- Prefer SeaQuery when query shape is genuinely dynamic, many optional filters or
  dialects must compose, or string assembly would be unsafe or hard to review.
- Consider SeaORM only when the project already uses it or needs its entity,
  relation, migration, and active-model conventions across a broad persistence
  layer. Do not add it for one query or to avoid understanding SQL.
- Consider Diesel when the repository already uses Diesel or needs its typed query
  DSL, compile-time schema integration, and migration workflow. Do not mix it
  into a SQLx-centered project without a clear boundary.
- Prefer explicit raw SQL for migrations, performance-sensitive queries,
  database-native features, hand-tuned plans, or cases where an ORM/query builder
  hides important semantics.

## SQLite Guidance

- Do not assume SQLite is a drop-in PostgreSQL substitute. Use
  [`sqlite-sql-engineering`](../sqlite-sql-engineering/SKILL.md) for
  SQLite-specific schema, transaction, PRAGMA, locking, and test-database
  behavior.
- Type affinity, foreign key enforcement, locking, datetime handling, DDL
  support, and concurrency behavior differ from PostgreSQL.
- Ensure foreign keys are enabled when tests or application logic rely on them.
- Keep migrations compatible with SQLite's DDL limits, or isolate SQLite-specific
  migrations when the repository already supports multiple database backends.
- Use SQLite for local or embedded workflows when that is the product choice,
  not as proof that PostgreSQL-specific SQL is correct.

## SQL Review Checklist

- Queries select explicit columns and return only the data the caller needs.
- Predicates are sargable where possible and match available indexes.
- Pagination is stable under inserts/deletes; keyset pagination is considered
  for large ordered result sets.
- Joins preserve intended cardinality and do not accidentally multiply rows.
- `NULL` handling, collation, case sensitivity, timezone, and numeric precision
  are explicit where they affect behavior.
- Transactions cover exactly the consistency boundary and no more.
- User-controlled values are bound parameters, never interpolated SQL.
- Observability exists for slow queries, migration failures, and pool exhaustion
  when the repository has a logging/tracing pattern.
- For PostgreSQL-specific index, constraint, RLS, privilege, and query-plan
  review, load `postgresql-sql-engineering`.
- For SQLite-specific PRAGMA, type-affinity, locking, migration, and temp
  database behavior, load `sqlite-sql-engineering`.

## Testing And Acceptance Criteria

- Write a failing test or migration check before fixing a query bug when
  practical.
- Use BDD-style examples for user-visible persistence behavior, such as
  "Given an existing account, when a duplicate email is saved, then the caller
  receives a conflict and no partial write remains."
- Use integration tests against the database engine whose behavior matters.
- Verify migrations from an empty database and, when compatibility matters, from
  a representative previous schema.
- Run SQLx prepare/check commands after changing compile-checked queries,
  schema, or migrations.
- For SeaQuery builders, add focused tests for generated SQL shape and bind
  values when logic is dynamic. Cover no filters, one filter, multiple filters,
  sort order, pagination, empty inputs, `NULL`, and dialect-specific behavior.

## Anti-Patterns

- Treating application validation as a substitute for database constraints on
  critical invariants.
- Returning raw SQLx or driver errors through domain or HTTP APIs.
- Building SQL by string concatenation with user input.
- Introducing SeaQuery for simple static SQL that would be clearer as `sqlx`
  macros or explicit SQL.
- Calling `to_string` or debug-rendered SQL with user-controlled values as an
  execution path instead of using bound values.
- Adding indexes speculatively without a query and write-cost rationale.
- Hiding long transactions behind generic repository helpers.
- Claiming PostgreSQL behavior from SQLite-only tests, or the reverse.
