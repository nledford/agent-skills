---
name: script-engineering
description: Script and automation engineering guidance. Use when creating, changing, reviewing, or testing POSIX shell, Bash, PowerShell, Python, Node, or other repository scripts; choosing a scripting language or interpreter; deciding whether automation belongs in a script; or exposing script workflows through Just. Do not use when only running an existing script or recipe, for ordinary application code with no automation surface, or for hosted CI/release-provider or container semantics beyond the commands scripts invoke.
---

# Script Engineering

Use this skill for cross-language script selection and for the engineering rules
shared by repository automation scripts. Derive the available runtimes, supported
platforms, script layout, and validation commands from the target repository and
execution environment instead of assuming a universal tool list.

Use the matching language engineering skill when implementation needs
language-specific depth. Use [`justfiles`](../justfiles/SKILL.md) when changing
the Just command surface; this skill owns the script behind that surface.

## Workflow

1. Inspect repository instructions, script directories, shebangs, file
   extensions, manifests, version files, lockfiles, task runners, CI images,
   containers, tests, and documentation.
2. Identify every execution target: developer hosts, Windows or Unix-like
   systems, containers, CI runners, remote hosts, or production automation.
3. Decide whether the behavior should be a script. Prefer an existing command,
   task-runner recipe, application module, migration framework, or service when
   that is the clearer maintained boundary.
4. Choose the least complex language that is already supported across the
   required targets. Do not add a runtime merely to make a small script more
   convenient to author.
5. Define inputs, outputs, exit codes, side effects, working-directory rules,
   dependencies, idempotence expectations, preview behavior, and cleanup before
   implementing risky or reusable automation.
6. Implement in small testable units. Keep command construction explicit,
   validate arguments, quote paths and values correctly for the chosen language,
   and avoid hidden ambient state.
7. Run syntax/static checks and behavioral tests narrowly, then run the
   repository's broader script, task-runner, and CI-equivalent quality lanes.
8. Report the runtime evidence, language choice, behavior covered, commands run,
   skipped target platforms, and residual risk.

## Establish Runtime Availability

Treat availability as evidence about one target environment, not a fixed list:

- Repository evidence comes first: shebangs, existing scripts, version managers,
  package manifests, lockfiles, toolchain files, containers, CI configuration,
  setup docs, and task-runner recipes.
- Confirm the interpreter on each relevant target with a non-mutating lookup such
  as `command -v <interpreter>`, `type <interpreter>`, or PowerShell
  `Get-Command <interpreter>`, followed by the appropriate version command when
  version compatibility matters.
- Distinguish POSIX `sh`, Bash, and other shells. A working interactive shell does
  not prove that a script's shebang or requested shell exists elsewhere.
- Distinguish PowerShell 7+ (`pwsh`) from Windows PowerShell
  (`powershell.exe`) when features or platform support differ.
- Treat an agent permission to request or execute a command as authorization,
  not proof that the interpreter is installed. A script never broadens the
  agent's edit, shell, network, external-directory, or destructive-action
  authority.
- If required target availability cannot be established, preserve the existing
  repository convention or stop and report the uncertainty rather than silently
  adding a new runtime assumption.

## Decide Whether To Script

Do not create a durable script when:

- one short, readable, low-risk existing command or task-runner recipe is enough;
- the behavior is domain or application logic that callers should import and
  test through the normal application boundary;
- the repository already provides a maintained generator, migration tool,
  package command, or platform-native mechanism for the operation;
- the work needs a long-running process, durable state, recovery, rich
  concurrency, or an interactive interface better expressed as an application;
- a new interpreter or test framework would cost more than the automation saves;
  or
- the script would conceal destructive, credentialed, or remote operations, or
  work around command approval, sandbox, policy, or audit requirements.

One-off does not automatically mean unscripted. Data migrations, releases, and
other high-risk operations often need a reviewed, repeatable implementation with
preview, rollback, and evidence rather than an improvised terminal sequence.

## Choose A Language

Prefer the repository's established language when it satisfies the target
platforms and keeps the workflow maintainable.

| Choice | Prefer when | Move to another language when |
| --- | --- | --- |
| POSIX `sh` | The script is a small portable sequence of commands with limited branching and no Bash-only features. | Arrays, complex data, substantial parsing, or non-POSIX features are required. |
| Bash | Unix-like targets guarantee Bash and shell-native orchestration, pipelines, traps, or Bash data structures materially simplify the task. | Portability excludes Bash, or quoting, parsing, branching, and state are becoming the main work. |
| Python | The task handles structured data, files, APIs, reusable functions, robust CLI parsing, subprocess orchestration, or meaningful cross-platform behavior. | The repository does not support Python on every target, or a tiny shell command is clearer. |
| PowerShell | Windows administration, registry/services, Microsoft modules, .NET objects, or an existing cross-platform PowerShell workflow is the natural boundary. | Required targets do not provide the needed PowerShell edition, or the repository already has a simpler supported runtime. |
| JavaScript or TypeScript | The repository already standardizes on Node, Bun, or Deno and the script benefits from its package/tooling ecosystem. | Adding that runtime would create a new dependency or the script is simpler in an existing shell/Python workflow. |
| Another existing runtime | Local evidence shows it is the repository's supported automation language and all targets provide it. | Selection is based only on author familiarity or introduces an otherwise unused toolchain. |

Load [`python-engineering`](../python-engineering/SKILL.md) for Python
implementation, packaging, and pytest/unittest workflow. Load
[`javascript-typescript-engineering`](../javascript-typescript-engineering/SKILL.md)
for JavaScript or TypeScript runtime, package, type, lint, and test workflow.

## Script Contract And Safety

- Keep scripts deterministic and non-interactive by default. Make prompts an
  explicit user-facing mode, never an accidental CI or agent dependency.
- Use documented arguments and environment variables. Validate required values
  and return nonzero exit codes with actionable stderr on failure.
- Keep machine-readable stdout stable when other tools consume it; send progress
  and diagnostics to stderr.
- Resolve working-directory and relative-path behavior deliberately. Do not
  assume the caller starts beside the script unless that is the documented
  contract.
- Use temporary directories or files with collision-safe creation and guaranteed
  cleanup. Load [`random-data-identifiers`](../random-data-identifiers/SKILL.md)
  when generated names, nonces, tokens, fixtures, or reproducible randomness are
  material.
- Prefer idempotent behavior. For destructive, remote, production, or
  credentialed operations, provide a meaningful preview or dry-run, validate the
  exact target, and make the apply step explicit.
- Never print secrets. Avoid `eval`, dynamically assembled shell command strings,
  and interpolation of untrusted values into a shell; prefer argument arrays or
  direct process APIs.
- Pin or otherwise reproducibly provision non-standard interpreters, linters,
  runners, and helper binaries through the repository's existing dependency
  workflow.

## Test Scripts

Start with observable behavior: arguments, environment inputs, stdout, stderr,
exit status, created or changed files, cleanup, and external-command boundaries.
Use temporary isolated fixtures and test failure paths as well as success.

| Script type | Syntax and static checks | Behavioral tests |
| --- | --- | --- |
| POSIX shell | Run the target shell's no-execute syntax check where supported and ShellCheck with the intended dialect. | Run black-box tests under every shell/platform the repository claims to support. Prefer the existing runner; [ShellSpec](https://github.com/shellspec/shellspec) is an option when multi-shell behavior needs a framework. |
| Bash | Run `bash -n` and the repository's configured ShellCheck lane. | Prefer the existing Bash runner. [`bash_unit`](https://github.com/bash-unit/bash_unit) is suitable for function-oriented assertions, setup/teardown, status checks, and TAP output; [Bats-core](https://github.com/bats-core/bats-core) is suited to command-oriented Bash tests. |
| Python | Run the configured formatter, linter, and type checker as applicable. | Use the repository's pytest or unittest lane through its managed environment; test CLI behavior at process boundaries when invocation is part of the contract. |
| PowerShell | Run the repository's parser or PSScriptAnalyzer lane when configured. | Use [Pester](https://pester.dev/) for functions, modules, commands, side effects, and error behavior. Test both `pwsh` and Windows PowerShell only when both are supported targets. |
| JavaScript or TypeScript | Run the configured format, lint, type-check, and build lanes. | Use the repository's configured test runner and add process-level tests when the CLI contract matters. |

Static analysis is not a substitute for behavioral tests. Conversely, do not add
a test framework for a trivial wrapper when a syntax check plus one repository
smoke test provides proportionate confidence. Adding or downloading a runner,
linter, interpreter, binary, or installer invokes
[`dependency-supply-chain-review`](../dependency-supply-chain-review/SKILL.md);
do not copy unpinned `curl | shell` installation examples into project workflows.

Use [`test-driven-development`](../test-driven-development/SKILL.md) when new
behavior or a regression can be driven through Red-Green-Refactor. Use
[`systematic-debugging`](../systematic-debugging/SKILL.md) first for an active
unexplained script failure.

## Use Scripts With Just

When a repository uses Just, expose supported workflows through small,
documented recipes and keep substantial logic in independently testable scripts:

- Keep one short command inline when quoting, control flow, and reuse remain
  obvious. A shebang recipe can hold a modest self-contained operation.
- Move reusable logic, functions, substantial branching, robust argument
  parsing, or independently tested behavior to the repository's established
  script directory. Keep the recipe a thin parameterized wrapper.
- Resolve script paths from the Justfile location rather than relying on the
  caller's current directory.
- Pass deliberate arguments through the recipe instead of duplicating defaults,
  environment parsing, validation, or business rules in both layers.
- Provide narrow script-test recipes and include them in the repository's normal
  check or verification lane when local conventions support that shape. Derive
  actual recipe names from the repository rather than inventing universal names.
- Pair risky apply recipes with preview/status recipes and preserve the same
  target validation inside the script; a task-runner confirmation prompt is not
  the only safety control.

Load [`justfiles`](../justfiles/SKILL.md) for recipe syntax, parameters, groups,
imports/modules, shell configuration, listing behavior, and Just validation.

## Workflow Routing

- Load [`ci-release-engineering`](../ci-release-engineering/SKILL.md) when the
  change affects hosted workflow triggers, jobs, permissions, artifacts, or
  automated release behavior; scripts own only the commands that workflow runs.
- Load [`container-engineering`](../container-engineering/SKILL.md) when changing
  Dockerfile, OCI image, or Compose behavior; scripts own only their contained
  automation contract.
- Load [`security-review`](../security-review/SKILL.md) for concrete scripts that
  handle credentials, secrets, auth, command execution, untrusted input, paths,
  privileged operations, or remote/production targets. Use
  [`security-review-evidence`](../security-review-evidence/SKILL.md) when captured
  output, fixtures, or reports may contain sensitive values.
- Use [`context7-docs`](../context7-docs/SKILL.md) for current, version-specific
  behavior of an external interpreter, runner, linter, task runner, or module
  after inspecting the repository's pinned version and local usage.

## Completion Evidence

Report:

- the repository and target-environment evidence used to establish runtimes;
- why a script was appropriate and why the selected language fit better than the
  credible local alternatives;
- changed script, tests, task-runner, dependency, and documentation files;
- syntax, static-analysis, behavioral, platform, and broader quality checks run;
  and
- skipped target environments, unverified interpreter assumptions, and residual
  operational or security risk.
