# Agent Skills

This repository is the canonical local source for globally installed agent
skills. Its `skills/` directory is intended to be symlinked to
`~/.agents/skills`:

```sh
just setup
just verify
```

The repository keeps runtime skills under `skills/`. Each skill is a directory
with a `SKILL.md` file:

```text
agent-skills/
  skills/
    git-commit/
      SKILL.md
    test-driven-development/
      SKILL.md
  tools/
  tests/
```

## Skill Types

First-party skills are skill directories under `skills/` that are tracked, or
intended to be tracked, by this repository.

Third-party skills are installed into the same directory by external tooling,
such as `bunx skills`. A skill is treated as third-party when it is listed in
`.skill-lock.json` or ignored as a skill directory under `skills/` in `.gitignore`.
Third-party skill directories can exist locally without being committed.

## Common Commands

```sh
just                 # show available commands
just setup           # create ~/.agents/skills -> repo/skills when safe
just verify          # verify the global symlink
just list            # list all skills
just list-first-party
just list-third-party
just validate        # validate all skill metadata
just doctor          # validate skills and verify global install
just check           # run lint, tests, validation, and verify
```

Mutating global install commands are intentionally conservative. `just setup`
is idempotent when `~/.agents/skills` already points to this repository's
`skills/` directory, but it will not overwrite an existing directory or a
symlink to another location.

## Third-Party Updates

`just update-third-party` runs `bunx skills update` by default after verifying
that `~/.agents/skills` points at this repository's `skills/` directory.
Override the command with `SKILLS_UPDATE_COMMAND` when the installer workflow
differs:

```sh
SKILLS_UPDATE_COMMAND="bunx skills update" just update-third-party
```

Use `just update-third-party-dry-run` to see the command without running it.
Use `just sync-third-party-lock` when the repository lockfile should be copied
to `~/.agents/.skill-lock.json` for installer compatibility.

## Validation

Validation checks the repository's actual skill format:

- every discovered skill has `SKILL.md`
- `SKILL.md` starts with YAML front matter
- front matter defines `name` and `description`
- the front matter `name` matches the directory name
- every lockfile-listed third-party skill is present locally

Helper behavior is covered by `python3 -m unittest discover -s tests -v`.

## License

First-party skills and repository tooling are licensed under the MIT License.
See `LICENSE`.

Third-party skills installed into this directory are governed by their own
upstream licenses.
