---
name: bun-javascript-workflows
description: Bun JavaScript and TypeScript workflow guidance. Use when running, changing, reviewing, testing, linting, formatting, dependency-managing, or packaging Bun-backed package.json scripts, bun.lock, JS/TS runtime code, workspaces, CLIs, or project automation.
---

# Bun JavaScript Workflows

Use this skill for Bun as a JavaScript/TypeScript runtime, package manager,
script runner, test runner, and workflow tool. Keep guidance project-neutral and
inspect the repository before assuming framework, bundler, or lint tooling.

## Use When

- Working with `package.json`, `bun.lock`, Bun scripts, JS/TS source, Bun tests,
  workspaces, one-off package CLIs, or package-manager migration.
- Translating `npm`, `npx`, `yarn`, or `pnpm` instructions into a Bun-backed
  repository that already uses Bun.
- Reviewing dependency, script, test, lint, formatting, or runtime behavior in a
  Bun project.

Do not use this skill for Rust, Python, database, or browser E2E test design
except where Bun owns the package script that launches the tool. Use
`playwright-e2e` for checked-in Playwright test design and debugging.

## Workflow

1. Inspect `package.json`, `bun.lock`, `bunfig.toml`, workspace declarations,
   scripts, source/test layout, TypeScript config, lint/format config, CI, and
   README/AGENTS docs.
2. Decide the role Bun plays: runtime, package manager, script runner, test
   runner, bundler/transpiler, or one-off CLI runner.
3. Use repository scripts for broad lanes; use direct Bun commands for narrow
   iteration and tool discovery.
4. Keep behavior test-first when practical. Use BDD-style acceptance criteria
   for user-visible JS/TS or CLI behavior and TDD for focused logic changes.
5. After edits, verify the lockfile, scripts, tests, type checks, lint, format,
   and build lane that match the changed surface.

## Commands

Prefer checked-in scripts when they exist:

```sh
bun --version
bun install --frozen-lockfile
bun install
bun add <package>
bun add -d <package>
bun remove <package>
bun run <script>
bun test
bun test ./path/to/file.test.ts
bun test --test-name-pattern "<name>"
bunx <package> --help
bun x <package> --help
```

Use `bun install --frozen-lockfile` for reproducible CI-like installs. If
`package.json` and `bun.lock` disagree, fix the manifest or lockfile with Bun;
do not switch package managers silently.

For quality gates, inspect scripts before running:

```sh
bun run lint
bun run format
bun run format:check
bun run typecheck
bun run build
bun run test
```

Run only scripts that exist, or document that the repo lacks that gate.

## Dependency And Script Guidance

- Treat `bun.lock` as the source of reproducible dependency resolution; do not
  hand-edit it.
- Avoid introducing `package-lock.json`, `npm-shrinkwrap.json`, `yarn.lock`, or
  `pnpm-lock.yaml` in a Bun-owned project unless the repo intentionally supports
  multiple package managers.
- Use `bunx` or `bun x` for one-off package CLIs. Add a dependency only when the
  CLI is part of durable project workflow.
- Put script arguments after the script name and verify forwarding behavior in
  `package.json` before documenting examples.
- For workspaces, inspect the root and package-local scripts before choosing a
  command. Prefer the workspace command that matches CI.
- Keep environment variables, secrets, and `.env` handling explicit. Never print
  secrets while debugging scripts.

## JavaScript And TypeScript Review Checklist

- Correctness: async work is awaited, promises are returned or handled, errors
  are surfaced, and test assertions observe behavior rather than implementation
  calls.
- Types: TypeScript contracts are explicit at boundaries, `any` is justified,
  generated types are synchronized, and runtime validation exists for untrusted
  input.
- Modules: ESM/CJS choices match the repo, import paths are stable, side effects
  are intentional, and shared code is not hidden in scripts.
- Runtime compatibility: code does not assume Node-only APIs when running under
  Bun unless compatibility has been checked; likewise do not assume Bun APIs
  when the code must run in browsers or Node.
- Security: package scripts avoid shell injection, paths are quoted or
  structured, dependencies are reviewed, credentials are not logged, and network
  or filesystem access is intentional.
- Performance: avoid unbounded concurrency, repeated process startup, large
  synchronous filesystem work in hot paths, and unnecessary bundle/runtime
  dependencies.
- Observability: script failures are actionable and do not hide underlying CLI
  exit codes.

## Testing Guidance

- Use Bun's test runner when the repo uses `bun test`; otherwise use the
  configured test runner through `bun run`.
- Test file filters and `--test-name-pattern` are useful for tight loops. Broaden
  to the package or workspace lane before final handoff.
- Keep tests deterministic: no uncontrolled clocks, ports, network calls,
  process-global state, or shared temp directories.
- For browser behavior, API contracts, or framework rendering, use the repo's
  browser or integration test lane instead of pretending a unit test proves the
  full workflow.

## Anti-Patterns

- Copying upstream `npm`/`npx` instructions into a Bun-owned repo without
  translation.
- Running `bun install` in CI-like validation when the lockfile should be frozen.
- Adding persistent dependencies for a one-off generator or checker.
- Assuming every JS/TS project uses React, Vite, Next.js, ESLint, Prettier, or a
  specific test framework.
- Reporting a script as valid without checking it exists in `package.json` or
  running an equivalent focused command.

## Successful Use

The final handoff names the package/script surface changed, lockfile impact,
commands run, tests or quality gates covered, and any remaining runtime or CI
compatibility risk.
