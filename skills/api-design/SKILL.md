---
name: api-design
description: >-
  API design and contract guidance. Use when defining, changing, reviewing, or
  testing service or public interface contracts: HTTP/REST resources,
  RPC/GraphQL operations, webhooks, event/message schemas,
  request/response/error envelopes, pagination/filtering/sorting, idempotency,
  versioning/deprecation/backward compatibility, OpenAPI/AsyncAPI/JSON
  Schema/protobuf artifacts, SDK or CLI public surfaces, or consumer/provider
  compatibility. Do not use for ordinary language/framework implementation,
  Rust handler mechanics, SQL schema/query design, architecture boundary
  selection, security controls, BDD/TDD mechanics, observability
  instrumentation, or documentation-only API references after the contract is
  set; load those existing skills instead or alongside it when their trigger is
  primary.
  Use semantic-versioning when the primary question is choosing or applying a
  patch, minor, or major release bump after contract impact is understood.
---

# API Design

Use this skill to shape externally visible API contracts before implementation
details take over. Keep decisions protocol-aware but framework-agnostic: the same
review questions should work for REST resources, RPC methods, GraphQL fields and
mutations, webhooks, event/message schemas, SDKs, and CLI public surfaces.

## Use When

- Designing or changing resources, operations, action names, routes, methods,
  GraphQL fields, RPC calls, commands, webhook topics, or event names.
- Defining request inputs, response payloads, error envelopes, outcome/status
  codes, headers/metadata, schema artifacts, or generated client contracts.
- Choosing validation boundaries, required/optional fields, defaults, unknown
  field behavior, nullability, enum evolution, and data representation rules.
- Specifying pagination, filtering, sorting, search parameters, field selection,
  expansion/includes, cursor shape, or result ordering guarantees.
- Designing idempotency, retry behavior, conditional updates, optimistic
  concurrency, duplicate webhook delivery handling, or long-running operation
  contracts.
- Planning versioning, deprecation, backward compatibility, client migration,
  consumer/provider compatibility, or changelog expectations.
- Reviewing API examples, contract tests, SDK/CLI surface compatibility, or
  machine-readable specifications for contract correctness.

Do not use this skill as the primary workflow for framework routing mechanics,
language type modeling, database schema/query design, architecture layering,
security-control review, test methodology, or docs-only polishing after the
contract is already settled.

## Routing and Handoffs

- Use [`semantic-versioning`](../semantic-versioning/SKILL.md) to aggregate
  compatibility impacts across a release and recommend or apply its patch,
  minor, major, or prerelease version. Keep API contract design and consumer
  compatibility analysis in this skill.
- Load [`security-review`](../security-review/SKILL.md) when API work touches
  authentication, authorization, object permissions, tenant isolation, scopes,
  sessions/cookies, CORS/CSRF/CSP, redirects/callbacks, webhook signatures,
  sensitive data exposure, input validation at a trust boundary, rate limits,
  quotas, abuse controls, auditability, or other security-sensitive behavior.
  Keep this skill focused on the public contract shape; let security-review
  judge the security property and evidence.
- Load [`observability-engineering`](../observability-engineering/SKILL.md) for
  telemetry semantics, correlation, audit events, SLOs, dashboards, and alerts.
  Keep this skill involved when a telemetry field or event is itself part of the
  published API, SDK, CLI, webhook, or message contract.
- Load [`context7-docs`](../context7-docs/SKILL.md) when the contract depends on
  current behavior of a third-party provider, API gateway, framework, SDK,
  schema tool, OpenAPI/AsyncAPI/GraphQL/protobuf library, cloud service,
  webhook provider, auth provider, rate-limit product, or CLI. Inspect local
  versions and repository conventions first, then query current docs for the
  exact provider or framework feature needed.
- Use language engineering skills for implementation mechanics, package/tool
  workflow, generated code, serializers, type modeling, and language-specific
  tests. For Rust web runtime and handler mechanics, use
  [`rust-async-web`](../rust-async-web/SKILL.md).
- Use SQL skills for database schemas, migrations, constraints, indexes,
  transactions, privileges, RLS, and query plans. A database schema is API design
  only when that schema is directly published as the external contract.
- Use architecture and DDD skills when dependency direction, ports/adapters,
  application boundaries, aggregates, or ubiquitous language are the main design
  question. Add this skill only for the exposed interface contract.
- Use [`behavior-driven-development`](../behavior-driven-development/SKILL.md)
  or [`test-driven-development`](../test-driven-development/SKILL.md) when
  scenarios, executable specs, regression tests, or test-level selection drive
  the work. This skill owns what the contract must say; testing skills own how
  to prove it.
- Use [`documentation-engineering`](../documentation-engineering/SKILL.md) for
  reference docs, examples, migration guides, changelogs, and API prose once the
  contract decisions are made.

## Protocol-Neutral Vocabulary

Map the local protocol to these neutral terms before designing:

| Contract question | REST/HTTP example | RPC example | GraphQL example |
| --- | --- | --- | --- |
| Addressable thing | resource route | service method | query/mutation field |
| Input | path/query/header/body | params/request message | arguments/input object |
| Output | representation | result message | field payload/type |
| Outcome | status code + body | result/error code | data/errors + extensions |
| Side effect | unsafe method/action | command method | mutation/subscription event |

Use protocol conventions where they help clients, but do not force every API
into REST nouns, RPC verbs, or GraphQL shapes when another style is clearer.

## Workflow

1. **Identify consumers and compatibility stakes.** Name internal and external
   clients, generated SDKs, CLIs, webhooks, integrations, support windows,
   version commitments, and whether existing clients must keep working.
2. **Define the job and boundary.** State the user-visible capability, actor,
   resource or operation, side effects, consistency expectations, and what the
   API deliberately does not expose.
3. **Model resources and actions.** Prefer stable domain nouns for resources and
   explicit command/action names for operations that do not fit CRUD. Avoid
   leaking persistence tables, UI state, framework classes, or internal workflow
   steps as public contract concepts.
4. **Specify request contracts.** Define required fields, optional fields,
   defaults, allowed values, nullability, units, time zones, encodings, size
   limits, unknown field behavior, validation timing, and idempotency keys or
   preconditions where relevant.
5. **Specify response contracts.** Define success payload shape, envelope use,
   metadata, links, pagination cursors, representation expansion, ordering,
   partial success semantics, cache/ETag behavior, and fields clients can rely
   on versus fields that are informational.
6. **Specify error contracts.** Use a consistent machine-readable error shape
   with stable codes, safe messages, invalid-field details, correlation/request
   identifiers when available, retryability, and protocol-appropriate outcome
   codes. Separate client-actionable errors from internal diagnostics.
7. **Define collection behavior.** Make pagination, filtering, sorting, search,
   projection, and includes deterministic. State maximum page sizes, default
   ordering, cursor opacity, filter operators, unsupported combinations, and
   whether total counts are exact, approximate, or omitted.
8. **Define mutation and retry behavior.** State idempotency, duplicate request
   handling, optimistic concurrency, conditional writes, long-running operation
   polling/cancellation, asynchronous completion, webhook retry semantics, and
   event ordering or deduplication guarantees.
9. **Plan evolution.** Classify changes as backward compatible, additive,
   behavior-changing, or breaking. Define version fields/paths/headers/schema
   revisions, deprecation notices, sunset windows, migration paths, and client
   fallback behavior.
10. **Write contract artifacts and examples.** Update OpenAPI/AsyncAPI/JSON
    Schema/protobuf/GraphQL schema, request/response examples, SDK/CLI examples,
    and migration notes at the same level of authority as the implementation.
11. **Verify contract expectations.** Run or add the narrowest practical checks:
    schema validation, contract tests, golden examples, backward-compatibility
    tests, generated-client smoke tests, negative validation cases, and migration
    checks for changed clients.
12. **Complete the handoff.** Name changed contract artifacts, checks run and
    their results, failed or skipped checks, and unresolved consumer, migration,
    or compatibility risk.

## Contract Checklist

- **Names and shape:** names match the domain, are stable across clients, and do
  not expose framework, database, or UI internals as public concepts.
- **Resource/action fit:** CRUD-like operations use predictable resource
  semantics; non-CRUD commands are explicit about side effects and outcomes.
- **Requests:** required fields, optional fields, defaults, unknown fields,
  nulls, enums, formats, units, limits, and validation errors are specified.
- **Responses:** payloads are minimal but sufficient; metadata is separated from
  data; clients know which fields are stable, nullable, deprecated, or computed.
- **Errors/outcomes:** outcome codes and error codes are stable, safe to expose,
  actionable by clients, and consistent across related operations.
- **Collections:** pagination, filtering, sorting, search, projection, includes,
  counts, and ordering guarantees behave predictably under data changes.
- **Idempotency and concurrency:** retries, duplicate requests, conditional
  writes, update conflicts, async operations, webhook redelivery, and event
  deduplication have explicit contracts.
- **Compatibility:** additive changes are safe for old clients; breaking changes
  have a versioning and migration plan; deprecated fields and operations have
  clear replacement paths.
- **Security-sensitive surfaces:** auth, permissions, scopes, validation limits,
  sensitive fields, rate limits, and abuse controls route through
  `security-review` before the contract is treated as complete.
- **Provider/framework dependence:** current external provider or framework
  behavior is checked through `context7-docs` when local code and docs are not
  enough.
- **Docs and examples:** examples are realistic, deterministic, sanitized, and
  cover success, validation failure, authorization/security-sensitive failures
  when appropriate, pagination, and migration-relevant changes.
- **Tests:** contract artifacts, examples, generated clients, compatibility
  guarantees, and error cases are covered by repository-appropriate tests.

## Compatibility Rules of Thumb

Usually backward compatible:

- Adding optional request fields with safe defaults.
- Adding response fields when clients are expected to ignore unknown fields.
- Adding enum values only when clients are documented and tested to tolerate
  unknown values.
- Adding new operations, filters, sort keys, or webhook event types without
  changing existing behavior.

Usually breaking or behavior-changing:

- Renaming, removing, retyping, or changing meaning of existing fields.
- Making optional input required, narrowing accepted values, or changing
  validation timing in a way existing clients can observe.
- Changing default sorting, pagination cursor semantics, ID format stability,
  error codes, status/outcome codes, retryability, or idempotency behavior.
- Returning less data, different units, different time zones, different null
  behavior, or different authorization visibility for existing operations.

When uncertain, treat the change as client-observable and require migration or
compatibility evidence.

## Anti-Patterns

- Designing from handler names, database tables, ORM models, UI components, or a
  single current client instead of the durable external contract.
- Mixing unrelated actions into one catch-all endpoint, method, mutation, event,
  or command because it is easier to implement.
- Returning free-form strings as the only error contract or exposing stack traces,
  internal identifiers, raw provider messages, or policy details in client
  errors.
- Treating pagination cursors as client-editable filters, relying on unstable
  default ordering, or promising exact counts that the system cannot maintain.
- Adding version numbers without a compatibility policy, deprecation path, or
  migration test.
- Copying provider or framework documentation into the contract instead of
  checking current docs and recording the project-specific decision.
