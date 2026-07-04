---
name: javascript-typescript-engineering
description: JavaScript and TypeScript engineering guidance. Use when adding, changing, reviewing, testing, linting, formatting, dependency-managing, packaging, or refactoring JS/TS source, package.json scripts, lockfiles, workspaces, CLIs, Bun/Node/Deno workflows, or project automation. Do not use for checked-in Playwright test design; use playwright-e2e.
---

# JavaScript and TypeScript Engineering

Use this skill for project-neutral JS/TS implementation and workflow work. Inspect
the repository before assuming a runtime, package manager, framework, formatter,
linter, test runner, or bundler.

## Use When

- Editing `.js`, `.jsx`, `.ts`, `.tsx`, `.mts`, `.cts`, package manifests,
  lockfiles, TypeScript configs, lint/format configs, build configs, tests, CLIs,
  workspaces, or project scripts.
- Working with Bun, Node.js, Deno, npm, pnpm, Yarn, package-manager migration, or
  one-off package CLIs.
- Reviewing JS/TS correctness, types, async behavior, module boundaries,
  dependency changes, formatting/linting, build output, or runtime compatibility.

Do not use this skill for Rust, Python, database-native design, or checked-in
Playwright test design. Use [`playwright-e2e`](../playwright-e2e/SKILL.md) for
Playwright specs/configs and browser-visible test lanes.

## Workflow

1. Inspect local evidence first: `package.json`, lockfiles, `bunfig.toml`,
   `deno.json`, `.npmrc`, workspaces, source/test layout, `tsconfig*`, lint and
   formatter config, bundler config, CI, README, and agent instructions.
2. Identify the runtime and package manager actually owned by the repository.
   Bun-first guidance applies only when the repo uses `bun.lock`, Bun scripts, or
   Bun runtime features.
3. Define the behavior before editing. Use BDD examples for user-visible or CLI
   behavior and TDD for focused logic changes and bug fixes.
4. Keep boundaries explicit: domain logic, adapters, UI, scripts, generated code,
   and external service clients should not blur together. Load
   [`hexagonal-architecture`](../hexagonal-architecture/SKILL.md) for
   ports/adapters and external actors, [`clean-architecture`](../clean-architecture/SKILL.md)
   for use-case and interface-adapter boundaries, or
   [`onion-architecture`](../onion-architecture/SKILL.md) for domain/application
   rings.
5. Verify with the narrowest useful script or direct command first, then broaden
   to the repository's lint, type, test, format, and build lanes.

## Runtime and Package Manager Rules

- Do not switch package managers silently. Lockfiles are policy evidence:
  `bun.lock`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, and `deno.lock`
  imply different workflows.
- Use Bun for install/run/test/add/remove/x commands when the repository is
  Bun-owned. Use Node/npm, pnpm, Yarn, or Deno when local config, CI, runtime
  APIs, deployment target, or workspace policy requires them.
- Do not introduce another lockfile unless the project intentionally supports
  multiple package managers.
- Add dependencies only when durable project code needs them. Use one-off CLI
  runners (`bunx`, `npx`, `pnpm dlx`, `yarn dlx`, `deno run`) only when they fit
  the local workflow and do not hide unreviewed side effects.
- Keep package scripts explicit about arguments, environment variables, working
  directory, generated files, and exit codes.

Common commands to adapt to the repo:

```sh
bun install --frozen-lockfile
bun run <script>
bun test <filter>
npm ci
npm run <script>
pnpm install --frozen-lockfile
pnpm run <script>
yarn install --immutable
yarn <script>
deno task <task>
```

## JavaScript and TypeScript Checklist

- Async work is awaited, returned, cancelled, or intentionally detached; promise
  rejections are observed and surfaced.
- TypeScript contracts are explicit at module, API, CLI, network, and persistence
  boundaries. Avoid `any` and broad assertions unless a boundary is genuinely
  untyped and checked at runtime.
- Runtime validation exists for untrusted input. Compile-time types do not prove
  JSON, form, query, environment, file, plugin, or network data is valid.
- ESM/CJS choices match the repo and runtime. Side effects at import time are
  deliberate, cheap, and documented when they affect callers.
- Errors preserve actionable context without logging secrets, tokens, cookies,
  credentialed URLs, or private paths.
- Generated types and artifacts are regenerated through the repo's workflow and
  not hand-edited.
- Random IDs, tokens, and test data follow
  [`random-data-identifiers`](../random-data-identifiers/SKILL.md).

## Pattern Routing

- Load
  [`typescript-javascript-design-patterns`](../typescript-javascript-design-patterns/SKILL.md)
  when the change needs JS/TS-specific pattern choices: discriminated unions,
  branded types, runtime validation boundaries, functional core/imperative shell,
  adapter modules, command or use-case handlers, dependency injection, async
  orchestration, or test builders.
- Load
  [`typescript-javascript-antipatterns`](../typescript-javascript-antipatterns/SKILL.md)
  when reviewing or refactoring JS/TS smells: `any`, unsafe assertions, missing
  runtime validation, unawaited promises, framework/UI leakage, singleton service
  bags, import-time side effects, weak randomness, over-mocked tests, or brittle
  E2E tests.

## Formatting, Linting, Types, and Builds

- Use checked-in scripts when they exist. Otherwise inspect configured tools:
  Prettier, ESLint, Biome, TypeScript, tsup, esbuild, Vite, Next.js, Rollup,
  Webpack, SWC, Jest, Vitest, Node's test runner, Bun test, or Deno tasks.
- Prettier is formatting only. ESLint/Biome and TypeScript checks cover different
  contracts; do not report one as a substitute for the other.
- Run format checks before changing style broadly. Avoid formatting unrelated
  files unless the task is explicitly a formatting pass.
- For TypeScript, run the repo's configured typecheck. If none exists, use the
  narrowest command that respects local `tsconfig` and module resolution.
- For build changes, check bundle/runtime compatibility and generated output only
  where the repository expects generated artifacts to be committed.

## Testing Guidance

- Unit tests: pure logic, parsers, formatters, validators, state machines,
  reducers, and small adapters.
- Integration tests: filesystem, subprocesses, package scripts, API clients,
  database adapters, framework wiring, and generated contracts.
- E2E/browser tests: only when browser behavior is the confidence target; use the
  Playwright skill for checked-in browser tests.
- Keep tests deterministic: no uncontrolled clocks, ports, network calls, random
  seeds, process-global state, shared temp directories, or order dependence.
- Use targeted filters for iteration, then broaden to package/workspace/CI lanes
  when the changed surface crosses boundaries.

## Security Review Prompts

Load [`security-review`](../security-review/SKILL.md) when JS/TS changes touch
auth, sessions, cookies, CSRF/CORS/CSP, cryptography, secrets, `.env`, command
execution, path handling, uploads/downloads, plugin execution, HTML/Markdown
rendering, SSR, or other implemented trust boundaries. Use
[`dependency-supply-chain-review`](../dependency-supply-chain-review/SKILL.md)
for dependency bumps, lockfile churn, package-manager updates, package scripts,
install/postinstall hooks, one-off CLIs, CI bootstrap, generated clients,
vendored code, provenance, or advisory questions. Use
[`threat-modeling`](../threat-modeling/SKILL.md) before or during new auth
middleware, request/API/SSR boundaries, plugins, webhooks, background workers,
external-service integrations, or sensitive data flows. Use
[`security-review-evidence`](../security-review-evidence/SKILL.md) when
collecting or reporting sensitive security evidence.

## Anti-Patterns

- Assuming every JS/TS repo uses React, Next.js, Vite, ESLint, Prettier, Jest,
  Vitest, Node, Bun, or Deno without local evidence.
- Copying upstream `npm`/`npx` instructions into a Bun, pnpm, Yarn, or Deno repo
  without translating and verifying them.
- Adding dependencies for trivial standard-library or platform behavior.
- Letting framework, ORM, SDK, HTTP, UI, or generated-client types leak into core
  domain APIs without an intentional adapter boundary.
- Using `Math.random()` for secrets, tokens, identifiers, or security-sensitive
  test fixtures.
- Reporting a script, typecheck, lint, format, build, or test lane as valid
  without checking it exists or running the relevant command.

## Successful Use

The final handoff states the source/script/package surface changed, package
manager and lockfile impact, commands run, test/type/lint/format/build evidence,
and any remaining runtime or CI compatibility risk.
