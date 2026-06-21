---
name: context7-docs
description: Use when the task requires current, version-specific documentation or code examples for third-party libraries, frameworks, SDKs, APIs, or tools. Do not use for repository-local code understanding, generic programming concepts, or stable language syntax unless current external docs are needed.
---

# Context7 Docs

Use this skill to decide when and how to consult the `context7` MCP server for
current, version-aware third-party documentation without wasting tool calls or
context window.

## Purpose

Context7 provides current, version-aware documentation and code examples for
libraries, frameworks, SDKs, APIs, CLIs, and tools. Use it to reduce the risk of
hallucinated, outdated, or incorrect external API usage. Treat Context7 output as
documentation context, not proof that the code is correct in the current
repository.

## Use Context7 when

- The task involves third-party library, framework, SDK, API, CLI, or cloud-tool
  behavior.
- The answer depends on current or version-sensitive APIs.
- You need setup, configuration, migration, integration, or troubleshooting
  steps for an external package or service.
- You are generating code that depends on external package APIs.
- You are uncertain about exact function names, options, configuration keys,
  lifecycle hooks, supported runtimes, or recommended usage.
- The library changes frequently, especially frontend frameworks, cloud SDKs,
  auth libraries, ORMs, database clients, build tools, AI SDKs, and deployment
  platforms.

## Do not use Context7 when

- The answer can be derived from repository-local code, tests, README files, or
  existing project conventions.
- The task is about internal domain logic, architecture, refactoring, or test
  behavior that does not depend on external docs.
- The question is about stable language syntax or general programming concepts.
- The needed documentation is already present in the repository.
- You are making mechanical edits unrelated to external APIs.
- The dependency version cannot be determined yet; inspect local dependency
  files first when possible.

## Preferred workflow

1. Inspect the repository first for dependency versions and existing usage
   patterns.
2. Identify the exact library, framework, SDK, API, CLI, or tool involved.
3. If a Context7-compatible library ID is already known, query docs directly
   with that ID.
4. Otherwise, use the Context7 library-resolution tool first.
5. Query only for the specific topic needed.
6. Apply the retrieved docs to the task.
7. Verify against local dependency versions, existing code style, tests, and
   project conventions.
8. Do not blindly paste examples from Context7 if they conflict with the repo.

## MCP usage guidance

- Use the `context7` MCP server when it is available.
- Use `resolve-library-id` to turn a general library name into a
  Context7-compatible library ID.
- Use `query-docs` with the resolved or known library ID to retrieve targeted
  documentation.
- Prefer exact library IDs such as `/vercel/next.js`, `/supabase/supabase`, or
  IDs discovered through resolution.
- Prefer version-specific queries when the repository pins or implies a version.
- Keep tool queries small and focused; ask for the API, option, or workflow you
  need, not the whole documentation set.
- If the live MCP tool names or schemas differ, inspect the available MCP tools
  and adapt without inventing unsupported parameters.

## Effective query writing

- Ask one documentation question at a time.
- Include the library name, version if known, runtime or framework context, and
  target API or feature.
- Prefer precise topics like `middleware auth redirect Next.js 14` over broad
  topics like `Next.js docs`.
- Prefer task-oriented queries like
  `configure Supabase email password sign up with current JS client` over vague
  queries like `Supabase auth`.
- Include constraints that affect the answer: TypeScript, App Router, ESM, Node
  runtime, edge runtime, async API, test framework, or deployment target.
- Avoid dumping large, generic docs into context.
- Avoid repeated queries for the same information unless the first result was
  incomplete or ambiguous.

## Examples

Good queries:

- `Next.js 14 App Router middleware cookies redirect unauthenticated user`
- `Supabase JavaScript client v2 email password signUp TypeScript`
- `Drizzle ORM PostgreSQL migrations generate apply current CLI`
- `Cloudflare Workers cache API JSON response TypeScript module worker`
- `TanStack Query v5 invalidate queries mutation success TypeScript`

Bad queries:

- `Next.js` — too broad; it does not name a version, runtime, or feature.
- `How does auth work?` — unclear which library or auth flow is involved.
- `React docs` — asks for a whole documentation set instead of a task.
- `database setup` — missing the database, client, framework, and goal.
- `fix this error` — missing the package, version, API, and error context.

## Version handling

- Before querying when possible, inspect dependency files such as
  `package.json`, lockfiles, `Cargo.toml`, `pyproject.toml`, `requirements.txt`,
  `go.mod`, or equivalent manifests.
- Include the detected version or major version in the Context7 query.
- Do not apply docs for a newer major version to an older installed dependency
  without confirming compatibility.
- If the installed version and retrieved docs may not match, call out the
  uncertainty and verify locally before relying on the guidance.

## Context discipline

- Minimize Context7 calls.
- Prefer one targeted query over several broad queries.
- Summarize retrieved docs before applying them when useful.
- Discard irrelevant snippets and avoid copying large examples into the working
  context.
- Do not let external docs override repository-specific conventions without a
  deliberate reason.

## Safety and correctness

- Treat Context7 output as documentation context, not validation evidence.
- Verify behavior with tests, type checks, linting, examples, or focused manual
  checks when practical.
- Do not add new dependencies just because Context7 examples use them.
- Do not include secrets, tokens, private URLs, proprietary code, or internal
  identifiers in Context7 queries.
- Do not query proprietary or internal APIs unless they are publicly documented
  and intentionally available through Context7.

## Final answer behavior

When Context7 influences an implementation decision, briefly mention that the
documentation clarified a version-sensitive API, corrected an assumption, or
confirmed the intended usage. Do not over-explain routine Context7 usage.
