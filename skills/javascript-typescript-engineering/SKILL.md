---
name: javascript-typescript-engineering
description: JavaScript and TypeScript engineering guidance. Use when adding, changing, reviewing, testing, linting, formatting, dependency-managing, packaging, or refactoring JS/TS source, package.json scripts, lockfiles, workspaces, CLIs, Node/npm, Bun, Deno, pnpm, or Yarn workflows, or project automation. Do not use for checked-in hosted CI/release-provider or Docker/OCI/Compose configuration except the JS/TS commands they invoke; use ci-release-engineering or container-engineering. Use api-design for public service/SDK/CLI contracts, observability-engineering for telemetry/logging signal design, and css-scss-styling for CSS/SCSS/CSS-module/CSS-in-JS/utility styling decisions. Do not use for checked-in Playwright test design; use playwright-e2e.
---

# JavaScript and TypeScript Engineering

Use this skill for project-neutral JS/TS implementation and workflow work. Inspect
the repository before assuming a runtime, package manager, framework, formatter,
linter, test runner, or bundler.

## Use When

- Editing `.js`, `.jsx`, `.ts`, `.tsx`, `.mts`, `.cts`, package manifests,
  lockfiles, TypeScript configs, lint/format configs, build configs, tests, CLIs,
  workspaces, or project scripts.
- Working with Node.js, npm, `npx`, pnpm, Yarn, Deno, Bun,
  package-manager migration, or one-off package CLIs.
- Reviewing JS/TS correctness, types, async behavior, module boundaries,
  dependency changes, formatting/linting, build output, or runtime compatibility.

Do not use this skill for Rust, Python, database-native design, or checked-in
Playwright test design. Use [`playwright-e2e`](../playwright-e2e/SKILL.md) for
Playwright specs/configs and browser-visible test lanes. Use
[`css-scss-styling`](../css-scss-styling/SKILL.md) for stylesheet architecture,
CSS/SCSS migration, CSS modules, CSS-in-JS styling choices, utility classes,
responsive layout, and design-token decisions.

## Workflow

1. Inspect local evidence first: `package.json`, lockfiles, `bunfig.toml`,
   `deno.json`, `.npmrc`, workspaces, source/test layout, `tsconfig*`, lint and
   formatter config, bundler config, CI, README, and agent instructions.
   Use local code navigation, direct reads, and search for symbols, references,
   implementations, exact strings, docs, config, logs, fixtures, and generated
   assets; use repository commands for tests, builds, and other validation.
2. Identify the runtime and package manager actually owned by the repository.
   Use Node.js and npm by default when there is no local evidence requiring a
   different workflow. Use Bun only when the repo explicitly uses `bun.lock`, Bun
   scripts, Bun runtime features, or the task is Bun-specific.
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
  `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lock`, and
  `deno.lock` imply different workflows.
- Use Node.js and npm for install/run/test/add/remove commands by default, and
  use `npx` for one-off CLI execution unless the repository documents another
  tool. Use pnpm, Yarn, Deno, or Bun when local config, CI, runtime APIs,
  deployment target, or workspace policy requires them.
- Do not introduce another lockfile unless the project intentionally supports
  multiple package managers.
- Add dependencies only when durable project code needs them. Use one-off CLI
  runners (`npx`, `pnpm dlx`, `yarn dlx`, `bunx`, `deno run`) only when they fit
  the local workflow and do not hide unreviewed side effects.
- Keep package scripts explicit about arguments, environment variables, working
  directory, generated files, and exit codes.

Common commands to adapt to the repo:

```sh
npm ci
npm run <script>
npx <tool> [args]
pnpm install --frozen-lockfile
pnpm run <script>
yarn install --immutable
yarn <script>
bun install --frozen-lockfile
bun run <script>
bun test <filter>
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

## Styling Routing

- Load [`css-scss-styling`](../css-scss-styling/SKILL.md) when JS/TS work
  touches `.css`, `.scss`, `.sass`, CSS modules, CSS-in-JS, utility-class
  conventions, PostCSS/Tailwind/Sass config, design tokens, responsive layout,
  or browser-visible cascade behavior.
- Keep this skill focused on package-manager workflow, TypeScript contracts,
  bundler integration, component code, tests, and build commands. Let the styling
  skill own CSS-vs-SCSS decisions, selector/cascade maintainability,
  accessibility-related visual states, and stylesheet migration risks.

## API and Observability Routing

- Load [`api-design`](../api-design/SKILL.md) when JS/TS work defines or changes
  HTTP/RPC/GraphQL/webhook, SDK, CLI, request/response/error, pagination,
  versioning, or generated-client contracts. Keep this skill focused on JS/TS
  implementation, types, serializers, package workflow, and tests.
- Load [`observability-engineering`](../observability-engineering/SKILL.md) when
  adding or changing structured logs, metrics, traces, correlation IDs, audit
  events, frontend/backend diagnostics, or operator-facing telemetry.
- For public API docs, examples, or migration guides, load
  [`api-design`](../api-design/SKILL.md) first if the contract is still being
  shaped; otherwise use
  [`documentation-engineering`](../documentation-engineering/SKILL.md).

## CI, Release, and Container Routing

- Load [`ci-release-engineering`](../ci-release-engineering/SKILL.md) for hosted
  workflow triggers, jobs, matrices, permissions, artifacts, and automated
  releases. Keep package scripts and JavaScript/TypeScript build mechanics here.
- Load [`container-engineering`](../container-engineering/SKILL.md) for
  Dockerfile, OCI image, or Compose behavior; keep JS/TS runtime and bundler
  behavior here.

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
  Vitest, pnpm, Yarn, Bun, or Deno without local evidence.
- Following default `npm`/`npx` instructions after local evidence shows the repo
  requires pnpm, Yarn, Bun, or Deno, without translating and verifying them.
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
