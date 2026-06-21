---
name: playwright-e2e
description: "Chidori Playwright browser E2E guidance through Bun and root Just recipes. Use when adding, updating, running, or debugging e2e/*.spec.ts, playwright.config.ts, browser test support helpers, targeted Playwright runs, traces/reports, or Leptos/Axum browser-visible behavior. Do not use for non-browser domain logic, Rust-only tests, or generic browser MCP automation."
---

# Chidori Playwright E2E

## Purpose

Use this skill for checked-in Playwright browser tests in Chidori. The goal is
fast, targeted, behavior-readable evidence for the Rust/Leptos frontend served by
the root Axum application, with same-origin `/api` calls and synthetic test data.

## When to use

- Adding, updating, splitting, moving, or deleting `e2e/**/*.spec.ts` tests.
- Debugging Playwright failures, flakes, traces, reports, browser projects, or
  Playwright web-server startup.
- Choosing between default Chromium, explicit SSR/CSR/hydrate, cross-browser,
  responsive smoke, and live onboarding lanes.
- Testing browser-visible behavior: routing, forms, keyboard/focus behavior,
  visible validation/errors, accessibility-visible state, hydration, responsive
  shell behavior, and same-origin browser API calls.

## When not to use

- Domain invariants, SQL, backend route/security contracts, config validation, or
  pure Leptos state that can be tested faster in Rust.
- Ad hoc manual browser exploration, screenshots, or DOM inspection outside the
  checked-in Playwright test suite; use `docs/agents/browser-mcp.md` and the
  selected browser MCP workflow instead.
- Generic Playwright tutorial work that ignores Chidori's Bun scripts, root Axum
  topology, mock API helpers, and artifact-safety rules.

## Required repo inspection before acting

Before editing or recommending commands, inspect the current repository state:

- `package.json` for Bun-backed Playwright scripts and argument forwarding.
- `playwright.config.ts` for projects, serve modes, ports, artifact directories,
  reporters, retries, workers, and web-server commands.
- `just/test-web.just` and `just/setup.just` for supported root lanes.
- `e2e/**/*.spec.ts` and nearby specs for existing user-language coverage.
- `e2e/support/mock-api.ts`, `e2e/support/api-routes.ts`,
  `e2e/support/api-contract.ts`, `e2e/support/component-fixtures.ts`, and
  `e2e/support/artifact-safety.ts` before adding helpers or mocks.
- `docs/agents/frontend.md`, `docs/agents/testing.md`,
  `docs/agents/validation.md`, `docs/agents/browser-mcp.md`, and
  `docs/agents/dependencies.md` for current topology, test-layer, artifact, and
  Bun policy.

Use `just --list` to confirm recipe names before documenting commands.

## Test organization and boundaries

- Specs live under `e2e/`; workspace-specific specs live under `e2e/workspace/`.
- Shared same-origin API mocks and route assertions live in `e2e/support/`.
- Default browser E2E uses mocked same-origin APIs rather than a seeded backend
  database. Live onboarding is the opt-in exception.
- Keep Playwright tests BDD-shaped: test names should describe observable user or
  workflow behavior, not private Rust modules or implementation fixes.
- Keep DDD boundaries clear: domain rules and persistence belong in Rust/domain or
  backend tests; Playwright proves browser journeys and frontend/backend seams.
- Apply TDD when changing browser behavior: add or update the narrow failing spec
  first when practical, then implement the smallest source change.

## Common commands and workflows

Run from the repository root.

### Setup

```bash
just setup-web-e2e
just setup-web-e2e-cross-browser
```

The setup recipes run `bun install --frozen-lockfile` and install the required
Playwright browsers. Use the cross-browser setup only when Firefox/WebKit lanes
are in scope.

### Fast targeted development

Use direct Bun scripts for focused iteration after dependencies/browsers are
available:

```bash
bun install --frozen-lockfile
bun run test:web:e2e e2e/login.spec.ts
bun run test:web:e2e e2e/login.spec.ts:209
bun run test:web:e2e e2e/login.spec.ts --grep "failed login shows generic error"
```

Use `CHIDORI_FRONTEND_PORT=<loopback-port>` when avoiding a local port conflict.
Use `--workers=1`, `--headed`, `--debug`, or `--ui` only for focused debugging,
not routine handoff evidence.

### Supported lane selection

| Need | Command |
| --- | --- |
| Full mocked same-origin suite on desktop Chromium | `just test-web-e2e` |
| Explicit SSR/Axum browser lane | `just test-web-e2e-ssr` |
| Explicit browser-only CSR/static Trunk lane | `just test-web-e2e-csr` |
| Packaged hydrate asset lane | `just test-web-e2e-hydrate` |
| Curated desktop Chromium/Firefox/WebKit subset | `just test-web-e2e-desktop-cross-browser` |
| Responsive route smoke across desktop engines and mobile Chromium | `just test-web-e2e-responsive-cross-browser-smoke` |
| Live onboarding with isolated DB/runtime source root | `just test-web-e2e-live-onboarding` |

Default `playwright.config.ts` values are SSR serve mode, project set `default`,
host `127.0.0.1`, port `3000`, traces/screenshots/videos off, list reporter,
and artifacts under `target/playwright/artifacts`. `CHIDORI_FRONTEND_HOST` must
be `127.0.0.1` or `localhost`. `CHIDORI_PLAYWRIGHT_SKIP_WEBSERVER=1` is only for
an intentionally managed server, such as the live onboarding helper.

### Project and mode selectors

Use selectors only when they match the risk:

```bash
CHIDORI_PLAYWRIGHT_SERVE_MODE=hydrate bun run test:web:e2e e2e/ssr-hydration.spec.ts
CHIDORI_PLAYWRIGHT_PROJECT_SET=responsive-smoke bun run test:web:e2e e2e/responsive-cross-browser-smoke.spec.ts
CHIDORI_PLAYWRIGHT_PROJECT_SET=desktop-cross-browser bun run test:web:e2e e2e/login.spec.ts --project=firefox
```

Prefer the corresponding `just` recipe for final lane evidence.

## Debugging, traces, and reports

1. Re-run the smallest failing filter first: spec path, `file:line`, or
   `--grep` title regex.
2. Use `--list` to confirm a filter before starting browsers.
3. Use `--workers=1` or `--repeat-each <N>` to diagnose ordering or flake
   hypotheses without broadening the suite.
4. Use `--headed`, `--debug`, or `--ui` only for local interactive diagnosis.
5. Enable traces only as a narrow opt-in, for example
   `bun run test:web:e2e e2e/login.spec.ts --trace=retain-on-failure`.
6. Inspect traces with Playwright's trace CLI when needed, for example
   `bun --bun node_modules/.bin/playwright trace open <trace.zip>`.
7. If you generate an HTML report, keep it in an ignored local target directory:
   `PLAYWRIGHT_HTML_OUTPUT_DIR=target/playwright/report PLAYWRIGHT_HTML_OPEN=never bun run test:web:e2e e2e/login.spec.ts --reporter=html`.
   Review it with
   `bun --bun node_modules/.bin/playwright show-report target/playwright/report`.

The package script runs `e2e/support/artifact-safety.ts` after Playwright. If you
invoke `node_modules/.bin/playwright` directly, run
`bun e2e/support/artifact-safety.ts` before sharing any browser-derived evidence.
Do not retain or share raw screenshots, videos, traces, network dumps, storage
state, cookies, CSRF/session values, credentialed URLs, local paths, `.env`
contents, or live data.

## Testing and verification guidance

- Browser source or spec change: run the narrowest targeted Bun script first,
  then the strongest relevant `just test-web-e2e*` lane before handoff.
- Playwright config or helper-script topology change: run `just test-python-scripts`
  for config/helper contracts plus a targeted Playwright lane.
- Hydrate/packaged asset risk: run `just test-web-e2e-hydrate` or a targeted
  `CHIDORI_PLAYWRIGHT_SERVE_MODE=hydrate bun run ...` check while iterating.
- Cross-browser or responsive risk: run the curated cross-browser or responsive
  smoke lane, not the entire suite on every engine.
- Documentation-only E2E guidance changes: run `just drift-docs`; use
  `just drift-tests` only when test inventory or feature ownership changes.

## Failure triage

- Missing browser executable: run `just setup-web-e2e` or
  `just setup-web-e2e-cross-browser`.
- Web server cannot start: check `CHIDORI_FRONTEND_PORT`, host restrictions, and
  whether an old loopback server is occupying the port. The config intentionally
  does not reuse stale servers.
- Unexpected API call: update or extend `e2e/support/mock-api.ts` and route
  assertions only if the browser behavior is intentionally changing; otherwise
  fix the frontend API call.
- Hydration failure: prefer `e2e/ssr-hydration.spec.ts`, hydrate mode, and
  console diagnostics before broad browser matrices.
- Flake suspicion: use `--workers=1`, `--repeat-each`, and focused specs; do not
  hide nondeterminism with retries unless the lane's CI policy already owns them.

## Common mistakes to avoid

- Do not use Playwright as the only proof for domain invariants, SQL constraints,
  auth/session security controls, CORS/CSRF policy, or config parsing.
- Do not add live-backend or database setup to mocked specs when support helpers
  can express the same browser contract deterministically.
- Do not promote CSR, hydrate, cross-browser, responsive, or live-onboarding lanes
  into default checks without explicit approval.
- Do not leave `test.only`, retained traces, screenshots, videos, HTML reports, or
  raw browser artifacts in handoff evidence.
- Do not use `npx playwright`; use Bun scripts,
  `bun --bun node_modules/.bin/playwright ...`, or root `just` recipes.

## References

- `package.json`
- `playwright.config.ts`
- `just/setup.just`
- `just/test-web.just`
- `e2e/`
- `e2e/support/`
- `scripts/just/test_playwright_config_contract.py`
- `scripts/just/web_e2e_live_onboarding.py`
- `docs/agents/frontend.md`
- `docs/agents/testing.md`
- `docs/agents/validation.md`
- `docs/agents/browser-mcp.md`
- `docs/agents/dependencies.md`
