#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Sequence


GLOBAL_CONFIG_ROOT = Path.home() / ".config" / "opencode"
DEFINITION_ROOT_NAME = "opencode"
MANIFEST_NAME = "manifest.json"
DEFINITION_KINDS = ("agents", "commands")
DEFINITION_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*\.md$")
SUPPORT_FILE_RE = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]*(?:/[A-Za-z0-9][A-Za-z0-9._-]*)+$"
)
TOP_LEVEL_FIELD_RE = re.compile(r"^([a-z][A-Za-z0-9_]*):(?:\s(.*))?$")
PERMISSION_LEVEL_RE = re.compile(
    r'^  (?:(?:"([^"\\]+)")|([a-z][a-z0-9_]*)):(?:\s(.*))?$'
)
PERMISSION_RULE_RE = re.compile(r'^    (?:"([^"\\]+)"|([a-z0-9][a-z0-9-]*)):\s*(allow|ask|deny)$')
MODEL_VALUE_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*/[a-z0-9][a-z0-9._-]*$")
AGENT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
COMMAND_FIELDS = frozenset({"description", "agent", "model", "variant", "subtask"})
AGENT_FIELDS = frozenset(
    {"description", "mode", "model", "reasoningEffort", "steps", "color", "permission"}
)
REQUIRED_AGENT_FIELDS = frozenset(
    {"description", "mode", "model", "reasoningEffort", "steps", "permission"}
)
PERMISSION_ACTIONS = frozenset({"allow", "ask", "deny"})
REASONING_EFFORTS = frozenset({"low", "medium", "high", "xhigh"})
ROOT_ASK_AGENT_IDS = frozenset({"engineering-lead", "implementation-worker"})
PLAN_PATH_EDIT_RULE = "docs/implementation-plans/**"
PLAN_REDIRECTION_DENY_RULE = "*docs/implementation-plans*"
KNOWN_PERMISSION_TOOLS = frozenset(
    {
        "*",
        "edit",
        "bash",
        "task",
        "webfetch",
        "websearch",
        "question",
        "skill",
        "read",
        "glob",
        "grep",
        "list",
        "lsp",
        "todowrite",
    }
)
SAFE_EXACT_GIT_BASH_ALLOWS = frozenset(
    {
        "git status",
        "git status --short",
        "git diff",
        "git diff --cached",
        "git diff HEAD",
        "git diff HEAD^ HEAD",
        "git diff --check",
        "git diff --stat",
        "git show HEAD",
        "git show HEAD^",
        "git log",
        "git log --oneline -10",
        "git rev-parse HEAD",
        "git branch --show-current",
        "git show",
        "git ls-files",
        "pwd",
    }
)
ENGINEERING_LEAD_POST_PLAN_BASH_RULES = (("pbcopy *", "allow"),)
ENGINEERING_LEAD_GIT_BASH_RULES = (
    ("git branch *", "ask"),
    ("git commit *", "ask"),
    ("git push *", "ask"),
    ("git pull *", "ask"),
    ("git merge *", "ask"),
    ("git rebase *", "ask"),
    ("git reset *", "ask"),
    ("git restore *", "ask"),
    ("git checkout *", "ask"),
    ("git switch *", "ask"),
    ("git clean *", "ask"),
    ("git stash *", "ask"),
    ("git tag *", "ask"),
    ("git worktree *", "ask"),
    ("git remote *", "ask"),
    ("git cherry-pick *", "ask"),
    ("git revert *", "ask"),
    ("git status", "allow"),
    ("git status *", "allow"),
    ("git diff", "allow"),
    ("git diff *", "allow"),
    ("git log", "allow"),
    ("git log *", "allow"),
    ("git show", "allow"),
    ("git show *", "allow"),
    ("git grep *", "allow"),
    ("git rev-parse *", "allow"),
    ("git branch", "allow"),
    ("git branch --list *", "allow"),
    ("git branch --show-current", "allow"),
    ("git ls-files", "allow"),
    ("git ls-files *", "allow"),
    ("git blame *", "allow"),
    ("git cat-file *", "allow"),
    ("git diff-tree *", "allow"),
    ("git diff-index *", "allow"),
    ("git diff-files *", "allow"),
    ("git range-diff *", "allow"),
    ("git merge-base *", "allow"),
    ("git name-rev *", "allow"),
    ("git describe *", "allow"),
    ("git shortlog *", "allow"),
    ("git for-each-ref *", "allow"),
    ("git show-ref *", "allow"),
    ("git ls-tree *", "allow"),
    ("git rev-list *", "allow"),
    ("git reflog show *", "allow"),
    ("git remote -v", "allow"),
    ("git remote get-url *", "allow"),
    ("git worktree list *", "allow"),
    ("git stash list *", "allow"),
    ("git submodule status *", "allow"),
    ("git config --get core.hooksPath", "allow"),
    ("git config --get commit.gpgsign", "allow"),
    ("git config --get gpg.format", "allow"),
    ("git add *", "allow"),
    ("git commit", "allow"),
    ("git fetch *", "allow"),
    ("git *--output*", "ask"),
    ("git *--ext-diff*", "ask"),
    ("git *--textconv*", "ask"),
    ("git grep *--open-files-in-pager*", "ask"),
    ("git grep -O*", "ask"),
    ("git grep * -O*", "ask"),
    ("git cat-file *--filters*", "ask"),
    ("git commit *--am*", "ask"),
    ("git commit *--fixup*", "ask"),
    ("git commit *--squash*", "ask"),
    ("git commit *--all*", "ask"),
    ("git commit -a *", "ask"),
    ("git commit * -a *", "ask"),
    ("git commit *--author*", "ask"),
    ("git commit *--date*", "ask"),
    ("git commit *--reset-author*", "ask"),
    ("git commit *--allow-empty*", "ask"),
    ("git commit *--no-gpg-sign*", "ask"),
    ("git commit *--pathspec-from-file*", "ask"),
    ("git commit *--include*", "ask"),
    ("git commit *--only*", "ask"),
    ("git commit *--interactive*", "ask"),
    ("git commit *--patch*", "ask"),
    ("git commit -m * -- *", "ask"),
    ("git fetch *--force*", "ask"),
    ("git fetch -f *", "ask"),
    ("git fetch * -f *", "ask"),
    ("git fetch *--prune*", "ask"),
    ("git fetch -p *", "ask"),
    ("git fetch * -p *", "ask"),
    ("git fetch *--refmap*", "ask"),
    ("git fetch *--set-upstream*", "ask"),
    ("git fetch *--stdin*", "ask"),
    ("git fetch *--upload-pack*", "ask"),
    ("git fetch *--server-option*", "ask"),
    ("git fetch *--recurse-submodules*", "ask"),
    ("git fetch +*", "ask"),
    ("git fetch * +*", "ask"),
    ("git fetch *:*", "ask"),
    ("git fetch -*", "ask"),
    ("git fetch * -*", "ask"),
    ("git fetch ./*", "ask"),
    ("git fetch ../*", "ask"),
    ("git fetch /*", "ask"),
    ("git fetch ~*", "ask"),
    ("git fetch $*", "ask"),
    ("git fetch *://*", "ask"),
    ("git fetch git@*", "ask"),
    ("git *>*", "ask"),
    ("git *<*", "ask"),
    ("git *|*", "ask"),
    ("git *&*", "ask"),
    ("git *;*", "ask"),
    ("git *$(*", "ask"),
    ("git *`*", "ask"),
    ("git commit *--no-verify*", "deny"),
    ("git commit -n *", "deny"),
    ("git commit * -n *", "deny"),
    ("git commit *--no-post-rewrite*", "deny"),
    ("git fetch -*u*", "deny"),
    ("git fetch * -*u*", "deny"),
    ("git fetch --*", "ask"),
    ("git fetch * --*", "ask"),
    ("git fetch *--update-head-ok*", "deny"),
    ("git push *--force*", "deny"),
    ("git push -f *", "deny"),
    ("git push * -f *", "deny"),
    ("git push *--delete*", "deny"),
    ("git push -d *", "deny"),
    ("git push * -d *", "deny"),
    ("git push *--mirror*", "deny"),
    ("git push *--prune*", "deny"),
    ("git push +*", "deny"),
    ("git push * +*", "deny"),
    ("git push :*", "deny"),
    ("git push * :*", "deny"),
    ("git push -f*", "deny"),
    ("git push * -f*", "deny"),
)
ENGINEERING_LEAD_GIT_EFFECTIVE_ACTIONS = (
    ("git status --short", "allow"),
    ("git diff --cached", "allow"),
    ("git add src/app.py", "allow"),
    ("git commit", "allow"),
    ("git commit -m message", "ask"),
    ("git commit --amend", "ask"),
    ("git commit --no-verify -m message", "deny"),
    ("git diff-tree --output=result HEAD", "ask"),
    ("git grep -Ocustom pattern", "ask"),
    ("git fetch origin", "allow"),
    ("git fetch -fpP origin", "ask"),
    ("git fetch -fu origin", "deny"),
    ("git fetch -u origin", "deny"),
    ("git pull --ff-only", "ask"),
    ("git push origin main", "ask"),
    ("git push -fv origin main", "deny"),
    ("git status | tee status.txt", "ask"),
)
ENGINEERING_LEAD_MCP_TOOL_PATTERNS = (
    "playwright_*",
    "chrome-devtools_*",
    "serena_*",
    "context7_*",
    "gh_grep_*",
    "github_*",
)
REQUIRED_SUPPORT_FILES = (
    "cleanup/weave-cleanup-checklist.md",
    "config/opencode.merge-fragment.jsonc",
    "project-template/AGENTS-plan-workflow-snippet.md",
    "project-template/docs/implementation-plans/README.md",
    "project-template/docs/implementation-plans/TEMPLATE.md",
)
PLAN_TEMPLATE_TOKENS = (
    "# <Title>",
    "**Original request:**",
    "**Key repository findings:**",
    "**Dependencies:**",
    "1. [ ] <bounded implementation step>",
)
PLAN_PATH_TOKEN = "docs/implementation-plans/plans/<series>/<NN>-<slug>.md"
PLAN_TEMPLATE_HEADINGS = (
    "# <Title>",
    "## TL;DR",
    "## Context",
    "## Objectives",
    "## Guardrails",
    "## Deliverables",
    "## Definition of Done",
    "## TODOs",
    "## Verification",
)
LEAN_PLAN_TEMPLATE = """# <Title>

## TL;DR

## Context

**Original request:**

**Key repository findings:**

**Dependencies:**

## Objectives

## Guardrails

## Deliverables

## Definition of Done

## TODOs

1. [ ] <bounded implementation step>

## Verification
"""


def resolve_v118_permission_action(
    rules: tuple[tuple[str, str], ...],
    command: str,
    *,
    baseline: str,
) -> str:
    action = baseline
    for pattern, candidate in rules:
        optional_suffix_match = pattern.endswith(" *") and command == pattern[:-2]
        if optional_suffix_match or fnmatchcase(command, pattern):
            action = candidate
    return action


@dataclass(frozen=True)
class DefinitionInventory:
    agents: tuple[str, ...]
    commands: tuple[str, ...]
    support_files: tuple[str, ...]

    def for_kind(self, kind: str) -> tuple[str, ...]:
        return getattr(self, kind)


@dataclass(frozen=True)
class ParsedFrontmatter:
    fields: dict[str, str | None]
    permissions: dict[str, str | tuple[tuple[str, str], ...]]
    closing_index: int


@dataclass
class OperationResult:
    messages: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


class OpenCodeInstallService:
    def __init__(
        self,
        repo_root: Path | str,
        config_root: Path | str = GLOBAL_CONFIG_ROOT,
    ) -> None:
        self.repo_root = Path(repo_root).expanduser().resolve()
        self.definition_root = self.repo_root / DEFINITION_ROOT_NAME
        self.config_root = Path(config_root).expanduser()
        self.sources = {
            kind: self.definition_root / kind
            for kind in DEFINITION_KINDS
        }
        self.destinations = {
            kind: self.config_root / kind
            for kind in DEFINITION_KINDS
        }

    def validate(self) -> OperationResult:
        inventory, errors = self._load_inventory()
        if inventory is None:
            return OperationResult(errors=errors)

        errors.extend(self._validate_support_files(inventory.support_files))
        for kind in DEFINITION_KINDS:
            errors.extend(self._validate_kind(kind, inventory.for_kind(kind)))

        if not errors:
            agent_metadata = self._agent_metadata(inventory)
            errors.extend(self._validate_task_delegation(agent_metadata))
            errors.extend(self._validate_command_agents(inventory, agent_metadata))

        if errors:
            return OperationResult(errors=errors)

        return OperationResult(
            messages=[
                "OpenCode definitions are valid: "
                f"agents={len(inventory.agents)} commands={len(inventory.commands)}"
            ]
        )

    def setup(self, *, dry_run: bool = False) -> OperationResult:
        validation = self.validate()
        if not validation.ok:
            return validation

        if self.config_root.exists() and not self.config_root.is_dir():
            return OperationResult(
                errors=["OpenCode config root exists but is not a directory"]
            )

        states, errors = self._inspect_destinations(missing_is_error=False)
        if errors:
            return OperationResult(errors=errors)

        messages: list[str] = []
        for kind in DEFINITION_KINDS:
            if states[kind] == "expected":
                messages.append(f"{kind} symlink is already configured")
            else:
                prefix = "Would create" if dry_run else "Created"
                messages.append(f"{prefix} {kind} symlink")

        if dry_run or all(state == "expected" for state in states.values()):
            return OperationResult(messages=messages)

        try:
            self.config_root.mkdir(parents=True, exist_ok=True)
        except OSError:
            return OperationResult(errors=["Could not create OpenCode config root"])
        created: list[str] = []
        active_kind = "OpenCode"
        try:
            for kind in DEFINITION_KINDS:
                if states[kind] == "expected":
                    continue
                active_kind = kind
                os.symlink(
                    self.sources[kind],
                    self.destinations[kind],
                    target_is_directory=True,
                )
                created.append(kind)
        except OSError:
            warnings = self._rollback_created(created)
            return OperationResult(
                errors=[f"Failed to create {active_kind} symlink; setup was rolled back"],
                warnings=warnings,
            )

        _, verification_errors = self._inspect_destinations(missing_is_error=True)
        if verification_errors:
            warnings = self._rollback_created(created)
            return OperationResult(
                errors=["OpenCode symlink verification failed; setup was rolled back"],
                warnings=warnings,
            )

        return OperationResult(messages=messages)

    def verify(self) -> OperationResult:
        validation = self.validate()
        if not validation.ok:
            return validation

        inventory, inventory_errors = self._load_inventory()
        if inventory is None:
            return OperationResult(errors=inventory_errors)

        _, errors = self._inspect_destinations(missing_is_error=True)
        if errors:
            return OperationResult(errors=errors)

        for kind in DEFINITION_KINDS:
            for name in inventory.for_kind(kind):
                visible_path = self.destinations[kind] / name
                if not visible_path.is_file():
                    errors.append(f"{kind}: '{name}' is not visible through the symlink")

        if errors:
            return OperationResult(errors=errors)

        return OperationResult(
            messages=[
                "OpenCode agents and commands symlinks are configured",
                "Visible OpenCode definitions: "
                f"agents={len(inventory.agents)} commands={len(inventory.commands)}",
            ]
        )

    def uninstall(self, *, dry_run: bool = False) -> OperationResult:
        states, errors = self._inspect_destinations(missing_is_error=False)
        if errors:
            return OperationResult(errors=errors)

        if all(state == "missing" for state in states.values()):
            return OperationResult(messages=["No managed OpenCode symlinks are installed"])

        if any(state != "expected" for state in states.values()):
            return OperationResult(
                errors=[
                    "OpenCode install is incomplete; refusing to remove either destination"
                ]
            )

        if dry_run:
            return OperationResult(
                messages=[
                    "Would remove agents symlink",
                    "Would remove commands symlink",
                ]
            )

        removed: list[str] = []
        active_kind = "OpenCode"
        try:
            for kind in DEFINITION_KINDS:
                active_kind = kind
                if self._destination_state(kind) != "expected":
                    raise OSError("destination changed during uninstall")
                self.destinations[kind].unlink()
                removed.append(kind)
        except OSError:
            warnings = self._restore_removed(removed)
            return OperationResult(
                errors=[
                    f"Failed to remove {active_kind} symlink; uninstall was rolled back"
                ],
                warnings=warnings,
            )

        return OperationResult(
            messages=["Removed agents symlink", "Removed commands symlink"]
        )

    def _load_inventory(self) -> tuple[DefinitionInventory | None, list[str]]:
        if self.definition_root.is_symlink() or not self.definition_root.is_dir():
            return None, ["OpenCode source root is missing or is not a regular directory"]

        manifest = self.definition_root / MANIFEST_NAME
        if manifest.is_symlink() or not manifest.is_file():
            return None, ["OpenCode manifest is missing or is not a regular file"]

        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return None, ["OpenCode manifest is not valid UTF-8 JSON"]

        manifest_kinds = (*DEFINITION_KINDS, "support_files")
        if not isinstance(data, dict) or set(data) != set(manifest_kinds):
            return None, [
                "OpenCode manifest must contain only agents, commands, and support_files lists"
            ]

        values: dict[str, tuple[str, ...]] = {}
        errors: list[str] = []
        for kind in manifest_kinds:
            entries = data.get(kind)
            if not isinstance(entries, list) or not all(
                isinstance(entry, str) for entry in entries
            ):
                errors.append(f"OpenCode manifest {kind} value must be a list of filenames")
                continue
            if entries != sorted(set(entries)):
                errors.append(
                    f"OpenCode manifest {kind} filenames must be sorted and unique"
                )
            entry_pattern = DEFINITION_NAME_RE if kind in DEFINITION_KINDS else SUPPORT_FILE_RE
            invalid = [entry for entry in entries if not entry_pattern.fullmatch(entry)]
            if invalid:
                errors.append(f"OpenCode manifest {kind} contains an invalid filename")
            values[kind] = tuple(entries)

        if errors:
            return None, errors

        return DefinitionInventory(
            agents=values["agents"],
            commands=values["commands"],
            support_files=values["support_files"],
        ), []

    def _validate_support_files(self, support_files: tuple[str, ...]) -> list[str]:
        if support_files != REQUIRED_SUPPORT_FILES:
            return ["OpenCode manifest support_files inventory is not canonical"]

        contents: dict[str, str] = {}
        errors: list[str] = []
        for relative_path in support_files:
            path = self.definition_root
            safe_path = True
            for part in Path(relative_path).parts:
                path /= part
                if path.is_symlink():
                    safe_path = False
                    break
            if not safe_path or not path.is_file():
                errors.append("support file is missing or is not a regular file")
                continue
            try:
                contents[relative_path] = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                errors.append("support file is not readable UTF-8")

        if errors:
            return errors

        template = contents["project-template/docs/implementation-plans/TEMPLATE.md"]
        if (
            template != LEAN_PLAN_TEMPLATE
            or not all(token in template for token in PLAN_TEMPLATE_TOKENS)
            or tuple(
                line for line in template.splitlines() if line.startswith("#")
            )
            != PLAN_TEMPLATE_HEADINGS
        ):
            errors.append("implementation plan template is not the canonical lean format")
        for path in (
            "project-template/AGENTS-plan-workflow-snippet.md",
            "project-template/docs/implementation-plans/README.md",
        ):
            if PLAN_PATH_TOKEN not in contents[path]:
                errors.append("implementation plan support path token is missing")
        for name in ("README.md", "TEMPLATE.md"):
            root_copy = self.repo_root / "docs" / "implementation-plans" / name
            template_copy = (
                self.definition_root
                / "project-template"
                / "docs"
                / "implementation-plans"
                / name
            )
            if root_copy.is_symlink() or not root_copy.is_file():
                errors.append("root implementation plan file is missing or is not a regular file")
                continue
            try:
                if root_copy.read_bytes() != template_copy.read_bytes():
                    errors.append("root implementation plan files differ from project-template copies")
            except OSError:
                errors.append("root implementation plan file is not readable")
        return errors

    def _validate_kind(self, kind: str, expected: tuple[str, ...]) -> list[str]:
        root = self.sources[kind]
        if root.is_symlink() or not root.is_dir():
            return [f"{kind} source is missing or is not a regular directory"]

        try:
            observed = {path.name for path in root.iterdir()}
        except OSError:
            return [f"{kind} source directory is not readable"]
        expected_names = set(expected)
        errors = [
            f"{kind}: unexpected asset '{name}'"
            for name in sorted(observed - expected_names)
        ]
        errors.extend(
            f"{kind}: manifest asset missing '{name}'"
            for name in sorted(expected_names - observed)
        )

        for name in expected:
            path = root / name
            if path.is_symlink() or not path.is_file():
                errors.append(f"{kind}: '{name}' must be a regular non-symlink file")
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                errors.append(f"{kind}: '{name}' is not readable UTF-8")
                continue
            parsed, markdown_errors = self._parse_frontmatter(kind, name, text)
            errors.extend(markdown_errors)
            if parsed is None:
                continue
            if kind == "agents":
                errors.extend(self._validate_agent_frontmatter(name, parsed))
            else:
                errors.extend(self._validate_command_frontmatter(name, parsed))

        return errors

    @staticmethod
    def _parse_frontmatter(
        kind: str,
        name: str,
        text: str,
    ) -> tuple[ParsedFrontmatter | None, list[str]]:
        """Parse this repository's scalar frontmatter and permission-map subset.

        This deliberately does not implement YAML. Supported definitions use
        unindented scalar fields and one ``permission`` mapping with optional
        four-space wildcard/action rule maps; other YAML forms fail closed.
        """
        lines = text.splitlines()
        if not lines or lines[0] != "---":
            return None, [f"{kind}: '{name}' is missing YAML frontmatter"]
        try:
            closing_index = lines.index("---", 1)
        except ValueError:
            return None, [f"{kind}: '{name}' has unterminated YAML frontmatter"]
        if not "\n".join(lines[closing_index + 1 :]).strip():
            return None, [f"{kind}: '{name}' has an empty prompt body"]

        errors: list[str] = []
        fields: dict[str, str | None] = {}
        permissions: dict[str, str | tuple[tuple[str, str], ...]] = {}
        active_permission: str | None = None
        permission_rules: list[tuple[str, str]] = []

        def finish_permission_rules() -> None:
            nonlocal active_permission, permission_rules
            if active_permission is not None:
                permissions[active_permission] = tuple(permission_rules)
            active_permission = None
            permission_rules = []

        for line in lines[1:closing_index]:
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if line.startswith("    "):
                if active_permission is None:
                    errors.append(
                        f"{kind}: '{name}' metadata must use supported top-level fields"
                    )
                    continue
                rule_match = PERMISSION_RULE_RE.fullmatch(line)
                if rule_match is None:
                    errors.append(
                        f"{kind}: '{name}' permission rules must use canonical key-value fields"
                    )
                    continue
                rule_key = rule_match.group(1) or rule_match.group(2)
                if any(existing_key == rule_key for existing_key, _ in permission_rules):
                    errors.append(
                        f"{kind}: '{name}' has duplicate permission rule '{rule_key}'"
                    )
                    continue
                permission_rules.append((rule_key, rule_match.group(3)))
                continue

            if line.startswith("  "):
                finish_permission_rules()
                if "permission" not in fields:
                    errors.append(
                        f"{kind}: '{name}' metadata must use scalar top-level fields"
                    )
                    continue
                permission_match = PERMISSION_LEVEL_RE.fullmatch(line)
                if permission_match is None:
                    errors.append(
                        f"{kind}: '{name}' permission fields must use canonical key-value fields"
                    )
                    continue
                quoted_key, named_key, value = permission_match.groups()
                permission_key = quoted_key or named_key
                if permission_key in permissions:
                    errors.append(
                        f"{kind}: '{name}' has duplicate permission '{permission_key}'"
                    )
                    continue
                if value is None:
                    active_permission = permission_key
                    continue
                if value not in PERMISSION_ACTIONS:
                    errors.append(
                        f"{kind}: '{name}' permission values must be allow, ask, or deny"
                    )
                    continue
                permissions[permission_key] = value
                continue

            finish_permission_rules()
            field_match = TOP_LEVEL_FIELD_RE.fullmatch(line)
            if field_match is None:
                errors.append(
                    f"{kind}: '{name}' metadata must use canonical key-value fields"
                )
                continue
            key, value = field_match.groups()
            allowed_fields = AGENT_FIELDS if kind == "agents" else COMMAND_FIELDS
            if key not in allowed_fields:
                errors.append(f"{kind}: '{name}' has unsupported '{key}' field")
                continue
            if key in fields:
                errors.append(f"{kind}: '{name}' has duplicate '{key}' field")
                continue
            if key == "permission":
                if value is not None:
                    errors.append(f"{kind}: '{name}' permission must be a block")
                    continue
                fields[key] = None
                continue
            if value is None or not value.strip():
                errors.append(f"{kind}: '{name}' field '{key}' must be a non-empty scalar")
                continue
            fields[key] = value
        finish_permission_rules()

        fence: tuple[str, int] | None = None
        for line in lines[closing_index + 1 :]:
            match = FENCE_RE.fullmatch(line)
            if match is None:
                continue
            marker, suffix = match.groups()
            if fence is None:
                fence = (marker[0], len(marker))
            elif (
                marker[0] == fence[0]
                and len(marker) >= fence[1]
                and not suffix.strip()
            ):
                fence = None
        if fence is not None:
            errors.append(f"{kind}: '{name}' has an unclosed Markdown code fence")

        if errors:
            return None, errors
        return ParsedFrontmatter(fields, permissions, closing_index), []

    @staticmethod
    def _validate_agent_frontmatter(name: str, parsed: ParsedFrontmatter) -> list[str]:
        fields = parsed.fields
        agent_id = Path(name).stem
        errors: list[str] = []
        missing = sorted(REQUIRED_AGENT_FIELDS - fields.keys())
        if missing:
            errors.append(f"agents: '{name}' is missing required '{missing[0]}' field")
            return errors
        if fields["mode"] not in {"primary", "subagent"}:
            errors.append(f"agents: '{name}' has invalid mode")
        if not MODEL_VALUE_RE.fullmatch(fields["model"] or ""):
            errors.append(f"agents: '{name}' has invalid model")
        if fields["reasoningEffort"] not in REASONING_EFFORTS:
            errors.append(f"agents: '{name}' has invalid reasoningEffort")
        steps = fields["steps"] or ""
        if not steps.isdecimal() or int(steps) < 1:
            errors.append(f"agents: '{name}' must use positive integer steps")
        if not parsed.permissions:
            errors.append(f"agents: '{name}' must define a permission block")
            return errors
        if "task" not in parsed.permissions:
            errors.append(f"agents: '{name}' permission block must define task")
            return errors
        permission_items = tuple(parsed.permissions.items())
        expected_baseline = "ask" if agent_id in ROOT_ASK_AGENT_IDS else "deny"
        if not permission_items or permission_items[0][0] != "*":
            errors.append(f"agents: '{name}' permission wildcard baseline must be first")
        elif permission_items[0][1] != expected_baseline:
            errors.append(
                f"agents: '{name}' permission wildcard baseline must be {expected_baseline}"
            )
        for level, value in parsed.permissions.items():
            if isinstance(value, str):
                if level == "task" and value != "deny":
                    errors.append(f"agents: '{name}' task permission must deny by default")
                continue
            if not value or value[0][0] != "*":
                errors.append(
                    f"agents: '{name}' permission '{level}' must put its wildcard baseline first"
                )
                continue
            if level == "task" and value[0][1] != "deny":
                errors.append(f"agents: '{name}' task permission must deny by default")
        errors.extend(
            OpenCodeInstallService._validate_capability_schema(
                name,
                agent_id,
                parsed.permissions,
                expected_baseline,
            )
        )
        errors.extend(
            OpenCodeInstallService._validate_core_permission_ownership(
                name,
                agent_id,
                parsed.permissions,
                expected_baseline,
            )
        )
        return errors

    @staticmethod
    def _validate_capability_schema(
        name: str,
        agent_id: str,
        permissions: dict[str, str | tuple[tuple[str, str], ...]],
        baseline: str,
    ) -> list[str]:
        errors: list[str] = []
        allowed_tools = set(KNOWN_PERMISSION_TOOLS)
        if agent_id == "engineering-lead":
            allowed_tools.update(ENGINEERING_LEAD_MCP_TOOL_PATTERNS)
        unknown_tools = set(permissions) - allowed_tools
        if unknown_tools:
            errors.append(f"agents: '{name}' has unsupported permission tool")

        bash = permissions.get("bash")
        if bash == "allow":
            errors.append(f"agents: '{name}' bash permission must be a rule map")
        elif baseline == "deny" and isinstance(bash, str) and bash != "deny":
            errors.append(
                f"agents: '{name}' bash permission must be deny or a rule map"
            )
        elif agent_id in ROOT_ASK_AGENT_IDS and isinstance(bash, str):
            errors.append(f"agents: '{name}' bash permission must be a rule map")
        elif isinstance(bash, tuple):
            for rule, action in bash:
                if action == "allow" and any(marker in rule for marker in "*?["):
                    if (
                        agent_id == "engineering-lead"
                        and (
                            (rule, action) in ENGINEERING_LEAD_GIT_BASH_RULES
                            or (rule, action) in ENGINEERING_LEAD_POST_PLAN_BASH_RULES
                        )
                    ):
                        continue
                    errors.append(
                        f"agents: '{name}' bash permission must not allow wildcard rules"
                    )
                    break
                if (
                    action == "allow"
                    and rule not in SAFE_EXACT_GIT_BASH_ALLOWS
                    and not (
                        agent_id == "engineering-lead"
                        and (rule, action) in ENGINEERING_LEAD_GIT_BASH_RULES
                    )
                ):
                    errors.append(
                        f"agents: '{name}' bash permission has an unsafe allow rule"
                    )
                    break

        if agent_id == "engineering-lead":
            git_rules = (
                tuple(rule for rule in bash if rule[0].startswith("git"))
                if isinstance(bash, tuple)
                else ()
            )
            if git_rules != ENGINEERING_LEAD_GIT_BASH_RULES:
                errors.append(
                    f"agents: '{name}' must preserve canonical git permissions"
                )
            if isinstance(bash, tuple) and any(
                action in {"allow", "ask"}
                and (pattern, action) not in ENGINEERING_LEAD_GIT_BASH_RULES
                and pattern not in {"*", PLAN_REDIRECTION_DENY_RULE}
                and (
                    pattern.startswith(("*", "?", "["))
                    or (
                        pattern.startswith("g")
                        and any(
                            marker in pattern.split(" ", 1)[0]
                            for marker in "*?["
                        )
                    )
                )
                for pattern, action in bash
            ):
                errors.append(
                    f"agents: '{name}' has a noncanonical wildcard rule that can override git permissions"
                )
            if isinstance(bash, tuple) and any(
                resolve_v118_permission_action(bash, command, baseline="ask")
                != expected
                for command, expected in ENGINEERING_LEAD_GIT_EFFECTIVE_ACTIONS
            ):
                errors.append(
                    f"agents: '{name}' must preserve effective git permission actions"
                )
            if permissions.get("todowrite") != "allow":
                errors.append(f"agents: '{name}' must allow todowrite")
        elif "todowrite" in permissions and permissions["todowrite"] != "deny":
            errors.append(
                f"agents: '{name}' must not allow todowrite for this role"
            )

        expected_network_action = "ask" if agent_id in {
            "engineering-lead",
            "technical-researcher",
        } else "deny"
        for tool in ("webfetch", "websearch"):
            if permissions.get(tool) != expected_network_action:
                errors.append(
                    f"agents: '{name}' network permissions must be {expected_network_action}"
                )
                break
        if agent_id == "engineering-lead" and any(
            permissions.get(pattern) != "allow"
            for pattern in ENGINEERING_LEAD_MCP_TOOL_PATTERNS
        ):
            errors.append(
                f"agents: '{name}' must allow every configured MCP tool pattern"
            )
        return errors

    @staticmethod
    def _validate_core_permission_ownership(
        name: str,
        agent_id: str,
        permissions: dict[str, str | tuple[tuple[str, str], ...]],
        baseline: str,
    ) -> list[str]:
        edit = permissions.get("edit")
        expected_edit: str | tuple[tuple[str, str], ...]
        if agent_id == "engineering-lead":
            expected_edit = (("*", "ask"), (PLAN_PATH_EDIT_RULE, "ask"))
        elif agent_id == "implementation-worker":
            expected_edit = (("*", "ask"), (PLAN_PATH_EDIT_RULE, "deny"))
        elif agent_id == "planning-coordinator":
            expected_edit = (("*", "deny"), (PLAN_PATH_EDIT_RULE, "ask"))
        else:
            expected_edit = "deny"

        errors: list[str] = []
        permitted_edit_values: set[str | tuple[tuple[str, str], ...]] = {expected_edit}
        if agent_id not in {
            "engineering-lead",
            "implementation-worker",
            "planning-coordinator",
        }:
            permitted_edit_values.add((("*", "deny"),))
        if edit not in permitted_edit_values:
            errors.append(f"agents: '{name}' violates core edit ownership")

        bash = permissions.get("bash")
        if agent_id in ROOT_ASK_AGENT_IDS:
            required_suffix = ((PLAN_REDIRECTION_DENY_RULE, "deny"),)
            if agent_id == "engineering-lead":
                required_suffix += ENGINEERING_LEAD_POST_PLAN_BASH_RULES
            if (
                not isinstance(bash, tuple)
                or len(bash) < len(required_suffix)
                or bash[-len(required_suffix) :] != required_suffix
            ):
                errors.append(
                    f"agents: '{name}' must preserve the plan redirection deny in its required bash suffix"
                )
        return errors

    @staticmethod
    def _validate_command_frontmatter(name: str, parsed: ParsedFrontmatter) -> list[str]:
        fields = parsed.fields
        errors: list[str] = []
        if parsed.permissions:
            return [f"commands: '{name}' does not support a permission block"]
        for field in ("description", "agent", "subtask"):
            if field not in fields:
                errors.append(f"commands: '{name}' must define exactly one {field}")
        if errors:
            return errors
        if not AGENT_ID_RE.fullmatch(fields["agent"] or ""):
            errors.append(f"commands: '{name}' must use a canonical bare agent name")
        if fields["subtask"] != "false":
            errors.append(f"commands: '{name}' must use literal 'subtask: false'")
        for optional_field in ("model", "variant"):
            if optional_field in fields and not fields[optional_field]:
                errors.append(f"commands: '{name}' field '{optional_field}' must be a non-empty scalar")
        return errors

    def _agent_metadata(
        self,
        inventory: DefinitionInventory,
    ) -> dict[str, tuple[str, tuple[tuple[str, str], ...]]]:
        metadata: dict[str, tuple[str, tuple[tuple[str, str], ...]]] = {}
        for name in inventory.agents:
            try:
                text = (self.sources["agents"] / name).read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                continue
            parsed, errors = self._parse_frontmatter("agents", name, text)
            if parsed is None or errors:
                continue
            task_rules = parsed.permissions.get("task")
            metadata[Path(name).stem] = (
                parsed.fields["mode"] or "",
                task_rules if isinstance(task_rules, tuple) else (),
            )
        return metadata

    @staticmethod
    def _validate_task_delegation(
        agent_metadata: dict[str, tuple[str, tuple[tuple[str, str], ...]]],
    ) -> list[str]:
        subagents = {
            agent_id for agent_id, (mode, _) in agent_metadata.items() if mode == "subagent"
        }
        errors: list[str] = []
        for agent_id, (mode, task_rules) in agent_metadata.items():
            non_wildcard_rules = [
                (target, action) for target, action in task_rules if target != "*"
            ]
            if mode == "subagent" and non_wildcard_rules:
                errors.append(
                    f"agents: '{agent_id}.md' subagents must not define non-wildcard task rules"
                )
                continue
            for target, action in non_wildcard_rules:
                if action != "allow":
                    errors.append(
                        f"agents: '{agent_id}.md' primary task rules must use allow"
                    )
                if target not in subagents:
                    errors.append(f"agents: '{agent_id}.md' has unknown task target '{target}'")
        return errors

    def _validate_command_agents(
        self,
        inventory: DefinitionInventory,
        agent_metadata: dict[str, tuple[str, tuple[tuple[str, str], ...]]],
    ) -> list[str]:
        primary_agents = {
            agent_id for agent_id, (mode, _) in agent_metadata.items() if mode == "primary"
        }
        all_agents = set(agent_metadata)
        errors: list[str] = []
        for name in inventory.commands:
            try:
                text = (self.sources["commands"] / name).read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                errors.append(f"commands: '{name}' could not be revalidated")
                continue
            parsed, parse_errors = self._parse_frontmatter("commands", name, text)
            if parsed is None or parse_errors:
                errors.append(f"commands: '{name}' could not be revalidated")
                continue
            agent_id = parsed.fields.get("agent")
            if agent_id not in all_agents:
                errors.append(f"commands: '{name}' references unknown agent '{agent_id}'")
            elif agent_id not in primary_agents:
                errors.append(
                    f"commands: '{name}' must reference a manifested primary agent"
                )
        return errors

    def _inspect_destinations(
        self,
        *,
        missing_is_error: bool,
    ) -> tuple[dict[str, str], list[str]]:
        states: dict[str, str] = {}
        errors: list[str] = []
        for kind in DEFINITION_KINDS:
            state = self._destination_state(kind)
            states[kind] = state
            if state == "missing" and missing_is_error:
                errors.append(f"{kind} destination is missing")
            elif state == "broken":
                errors.append(f"{kind} destination is a broken symlink")
            elif state == "foreign":
                errors.append(f"{kind} destination points somewhere else")
            elif state == "occupied":
                errors.append(
                    f"{kind} destination exists and is not a symlink; "
                    "move it aside manually"
                )
        return states, errors

    def _destination_state(self, kind: str) -> str:
        destination = self.destinations[kind]
        if destination.is_symlink():
            try:
                resolved = destination.resolve(strict=True)
            except (FileNotFoundError, RuntimeError, OSError):
                return "broken"
            return "expected" if resolved == self.sources[kind].resolve() else "foreign"
        if destination.exists():
            return "occupied"
        return "missing"

    def _rollback_created(self, created: list[str]) -> list[str]:
        warnings: list[str] = []
        for kind in reversed(created):
            destination = self.destinations[kind]
            if self._destination_state(kind) != "expected":
                warnings.append(f"Could not safely roll back {kind} symlink")
                continue
            try:
                destination.unlink()
            except OSError:
                warnings.append(f"Could not safely roll back {kind} symlink")
        return warnings

    def _restore_removed(self, removed: list[str]) -> list[str]:
        warnings: list[str] = []
        for kind in removed:
            destination = self.destinations[kind]
            if destination.exists() or destination.is_symlink():
                warnings.append(f"Could not safely restore {kind} symlink")
                continue
            try:
                os.symlink(
                    self.sources[kind],
                    destination,
                    target_is_directory=True,
                )
            except OSError:
                warnings.append(f"Could not safely restore {kind} symlink")
        return warnings


def emit_operation(result: OperationResult) -> int:
    for message in result.messages:
        print(message)
    for warning in result.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    for error in result.errors:
        print(f"error: {error}", file=sys.stderr)
    return 0 if result.ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and install repository-managed OpenCode definitions."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--config-root",
        type=Path,
        default=GLOBAL_CONFIG_ROOT,
        help="OpenCode config root. Defaults to ~/.config/opencode.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    subcommands.add_parser("validate", help="Validate repository definitions.")

    setup_parser = subcommands.add_parser(
        "setup",
        help="Create the managed agents and commands symlinks.",
    )
    setup_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report changes without applying them.",
    )

    subcommands.add_parser("verify", help="Verify definitions and both symlinks.")
    subcommands.add_parser("doctor", help="Validate definitions and both symlinks.")

    uninstall_parser = subcommands.add_parser(
        "uninstall",
        help="Remove both symlinks when this repository owns them.",
    )
    uninstall_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report changes without applying them.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        service = OpenCodeInstallService(args.repo_root, args.config_root)
        if args.command == "validate":
            return emit_operation(service.validate())
        if args.command == "setup":
            return emit_operation(service.setup(dry_run=args.dry_run))
        if args.command in {"verify", "doctor"}:
            return emit_operation(service.verify())
        if args.command == "uninstall":
            return emit_operation(service.uninstall(dry_run=args.dry_run))
    except (OSError, RuntimeError, UnicodeError, ValueError):
        print("error: OpenCode operation failed safely", file=sys.stderr)
        return 1

    print(f"error: unsupported command: {args.command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
