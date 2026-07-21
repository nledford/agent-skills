# Just Version And Advanced Syntax

Load this reference only when a task needs version-sensitive Just syntax,
imports/modules, alternate shells, shebang recipes, or a split command surface.
The core workflow and safety rules remain in `SKILL.md`.

## Version Compatibility

- Treat the official manual, upstream repository, and local `just --version` as
  authoritative. Use community examples only as heuristics.
- Do not invent syntax. Verify uncommon features against the installed version's
  official documentation before using them.
- Prefer stable, widely available features: recipes, variables, parameters,
  aliases, dependencies, doc comments, groups, imports, modules, and attributes.
- Label or avoid newer/version-sensitive features when the project does not pin
  `just`. Modules are stable since `just` 1.31; `[script]` is stable since 1.44
  and was available only as unstable syntax from 1.32; recipe option/flag
  argument metadata requires 1.46+; `set default-list`, `set default-script`,
  `[shell]`, and optional-module disabling behavior require 1.52+.
- Conditional `[windows]`/`[unix]` attributes on `set shell` require Just 1.56+.
  Check the repository's pinned or declared minimum Just version first.
- Before Just 1.56, `--dry-run` may still execute `shell()` expressions. Inspect
  those expressions and do not treat a dry run as non-mutating evidence on older
  versions.
- Avoid unstable features unless the repository deliberately opts in with
  `--unstable`, `set unstable`, or `JUST_UNSTABLE` and documents the risk.

## Splitting Large Justfiles

Start with one root Justfile. Split only when the command surface is hard to
scan, ownership differs by domain, or recipes need isolated settings.

- Use `import 'just/quality.just'` for same-namespace shared recipes and
  variables. Avoid duplicate recipe names; import override precedence is subtle.
- Use modules for namespaced subcommands and isolation:

```just
import 'just/quality.just'

# Container workflows.
mod containers 'just/containers.just'
```

Users can then run `just containers up` or `just containers::up`.

- Prefer `just/**` for child Justfiles when the repository already uses that
  layout. Keep the root Justfile as the map: imports/modules should be obvious
  from the top-level file and `just --list`.
- Move complex implementation to `scripts/just/**` or the repository's existing
  script directory; keep recipes as documented, parameterized wrappers.

## Shells, Languages, And Scripts

- Ordinary recipe lines run one line at a time with the configured shell,
  defaulting to `sh -cu` on Unix-like systems.
- Use portable POSIX shell for simple commands. Quote substitutions that may
  contain spaces: `"{{ path }}"` or `'{{ env }}'` as appropriate. This is only
  for constrained or validated values; use argument validation or external
  scripts for untrusted values containing quotes or shell metacharacters.
- Use Bash only when needed. For multi-line Bash, prefer a shebang recipe or an
  external script so strict mode applies to the whole body:

```just
# Regenerate checked artifacts.
[group('maintenance')]
regen:
    #!/usr/bin/env bash
    set -euo pipefail
    ./scripts/generate
```

- Use Python, Node, Ruby, or another language when the task is data-structured,
  cross-platform, or too awkward for shell. Prefer an external script once logic
  needs tests, functions, substantial branching, or robust argument parsing.
- If changing the recipe shell globally with `set shell := [...]`, document why;
  it affects recipe lines and backticks. For platform-specific shells in Just
  1.56+, use conditional attributes on `set shell` instead of
  `set windows-shell`:

  ```just
  [unix]
  set shell := ["bash", "-uc"]

  [windows]
  set shell := ["powershell.exe", "-NoLogo", "-Command"]
  ```

- Avoid brittle `cd ../../...` paths. Use `justfile_directory()` or explicit
  `[working-directory]`/`[no-cd]` behavior when location matters.
