---
name: sqlite-sql-engineering
description: SQLite and SQL engineering guidance. Use when adding, changing, reviewing, testing, or optimizing SQLite schemas, migrations, constraints, indexes, transactions, query behavior, local/embedded database workflows, SQLite-backed tests, or SQLite adapter boundaries in any language stack. Use api-design when SQLite schemas or exports affect published contracts and observability-engineering for durable SQLite diagnostics.
---

# SQLite And SQL Engineering

Use this skill for SQLite-specific database work independent of application
language. Keep the guidance focused on SQLite behavior; use
[`sql-engineering`](../sql-engineering/SKILL.md) for database-neutral SQL first
passes, [`postgresql-sql-engineering`](../postgresql-sql-engineering/SKILL.md)
for PostgreSQL-native design, and
[`rust-persistence-sql`](../rust-persistence-sql/SKILL.md) for Rust SQLx or
SeaQuery adapter details.

## Use When

- Designing or reviewing SQLite schemas, migrations, constraints, indexes,
  triggers, views, transactions, or query behavior.
- Using SQLite as an embedded database, local app store, cache, test database,
  fixture database, or lightweight service database.
- Comparing SQLite behavior with PostgreSQL, MySQL, or in-memory mocks.
- Working from Rust, Python, or another language where SQLite-specific
  correctness matters.

Do not use this skill for PostgreSQL-specific features, generic SQLx/SeaQuery
adapter choices, or treating SQLite as proof that another database behaves the
same way.

## Workflow

1. Inspect the database surface: schema files, migrations, connection options,
   PRAGMA setup, tests, fixture strategy, transaction helpers, and production vs
   test database engine.
2. State the data behavior. Use BDD-style examples for observable persistence
   rules such as uniqueness, deletion behavior, conflict handling, and atomicity.
3. Model boundaries with DDD language when domain rules matter. Keep SQLite row
   shapes and connection details out of core domain APIs unless the product is
   intentionally SQLite-centered.
4. Design schema and queries with SQLite semantics in mind: type affinity,
   foreign key enforcement, locking, transaction mode, generated values, and DDL
   limitations.
5. Verify with real SQLite, preferably isolated temporary database files or
   per-test in-memory databases configured exactly like the application.

## SQLite Checklist

- Enable and verify `PRAGMA foreign_keys = ON` when relying on foreign keys;
  do not assume every driver enables it by default.
- Use constraints for important invariants: `PRIMARY KEY`, `UNIQUE`, `NOT NULL`,
  `CHECK`, foreign keys, and conflict policies.
- Choose column types deliberately, but remember SQLite uses type affinity and
  can accept values that stricter engines reject unless constraints prevent it.
- Use transactions for multi-step writes. Pick deferred, immediate, or exclusive
  behavior intentionally when lock timing matters.
- Index real access paths: equality/range predicates, joins, ordering,
  uniqueness, and foreign-key lookups. Avoid speculative indexes in write-heavy
  local stores.
- Review `NULL`, collation, case sensitivity, datetime representation, numeric
  precision, and JSON extension availability where they affect behavior.
- Keep migrations compatible with SQLite's DDL support. Some schema changes need
  create-copy-drop-rename workflows rather than direct `ALTER TABLE`.
- Prefer parameterized statements and driver bind APIs; never interpolate
  user-controlled values into SQL strings.

## Security Review Prompts

Load [`security-review`](../security-review/SKILL.md) when SQLite work touches
database file paths or permissions, import/export paths, extension loading,
encryption or sensitive local data, user-controlled SQL, cache/session storage,
local sync or shared database files, backups, or other local trust boundaries.
Pair it with [`security-review-evidence`](../security-review-evidence/SKILL.md)
when evidence includes sanitized database files, fixture dumps, import/export
artifacts, logs, or reproduction data.

## Untrusted Database Files (Conditional)

Apply this workflow only when a database file or its companion files can be
written by another security domain. Treat the file as untrusted input: record
its provenance, inspect the actual SQLite library and binding versions (and
relevant compile options), and apply the controls the deployed binding supports.

- Apply global or compile-time resource limits before opening the file when the
  deployment supports them. Open it inside the selected isolation boundary, then
  immediately disable `trusted_schema`, enable defensive controls, and install
  the authorizer, connection limits, and progress/cancellation handler before
  preparing or executing schema-dependent SQL. Do not assume every binding or
  deployed SQLite version exposes the same controls.
- Keep extension loading disabled unless a reviewed use case needs it. Bound
  query time, result size, memory, cache, and blob use with the controls the
  deployed API actually exposes.
- Mark application-defined SQL functions and virtual-table modules `DIRECTONLY`
  where supported so schema content cannot invoke them indirectly. Keep custom
  functions, virtual tables, and extensions minimal and reviewed.
- Consider `PRAGMA quick_check` or `integrity_check` as the first SQL statement
  after connection hardening when the cost and failure behavior fit the opening
  path; neither substitutes for a trust boundary or sandbox against SQLite
  engine vulnerabilities.
- Choose controls from the threat model: reject external files when possible, or
  isolate parsing, constrain filesystem access, and define recovery behavior for
  malformed or resource-exhausting files. Load `security-review` and
  `security-review-evidence` for this boundary.

## API and Observability Routing

- Load [`api-design`](../api-design/SKILL.md) when SQLite migrations, local file
  schemas, import/export formats, sync payloads, reporting outputs, or
  constraint-error mapping affect an external or documented compatibility
  contract.
- Load [`observability-engineering`](../observability-engineering/SKILL.md) when
  SQLite work changes migration, query, sync, backup, locking, corruption, or
  local-diagnostic signals meant to persist beyond temporary debugging.

## Testing Guidance

- Test against SQLite itself for SQLite behavior. Mocks do not prove locking,
  constraints, type affinity, collation, or transaction behavior.
- Use temporary database files when persistence, WAL mode, locking, or multiple
  connections matter. Use isolated in-memory databases only when that matches
  the behavior under test.
- Seed fixtures deterministically and clean up per test. Avoid shared mutable
  database state that makes tests order-dependent.
- Cover no rows, duplicate rows, `NULL`, empty inputs, multi-filter queries,
  sort order, pagination, foreign key violations, and rollback paths.
- For Rust SQLx, validate with the repo's SQLx commands and SQLite feature
  flags. For Python, run the configured test and lint/type lanes through the
  project environment.

## Review Checklist

- Queries select explicit columns and return only needed data.
- Predicates and ordering match available indexes.
- Transactions protect one consistency boundary and are not held across slow
  external work.
- Error handling distinguishes not-found, constraint violation, busy/locked
  database, migration failure, and programmer error.
- Connection setup consistently applies required PRAGMAs, busy timeouts, WAL
  mode, journal mode, and extension loading policy when those matter.
- SQLite is used because local, embedded, test, or product constraints justify
  it, not because it is a convenient substitute for a different production
  database.

## Anti-Patterns

- Claiming PostgreSQL or MySQL correctness from SQLite-only tests.
- Forgetting foreign key PRAGMA while assuming referential integrity.
- Treating type declarations as strict validation without constraints.
- Sharing one mutable database across tests without isolation.
- Building SQL by string concatenation.
- Hiding database-specific behavior in generic repository code without tests.

## Successful Use

The final handoff names the SQLite behavior protected, schema or query changes,
test database setup, commands run, and any remaining difference from production
database behavior.
