#!/usr/bin/env python3

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import stat
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Sequence


GLOBAL_CONFIG_ROOT = Path.home() / ".config" / "opencode"
DEFINITION_ROOT_NAME = "opencode"
MANIFEST_NAME = "manifest.json"
DEFINITION_KINDS = ("agents", "commands")
INSTALL_KINDS = ("agents", "commands", "workflow-tools")
DEFINITION_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*\.md$")
SUPPORT_FILE_RE = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]*(?:/[A-Za-z0-9][A-Za-z0-9._-]*)+$"
)
TOP_LEVEL_FIELD_RE = re.compile(r"^([a-z][A-Za-z0-9_]*):(?:\s(.*))?$")
PERMISSION_LEVEL_RE = re.compile(
    r'^  (?:(?:"([^"\\]+)")|([a-z][a-z0-9_]*)):(?:\s(.*))?$'
)
PERMISSION_RULE_RE = re.compile(r'^    (?:"(.+)"|([a-z0-9][a-z0-9-]*)):\s*(allow|ask|deny)$')
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
MCP_ENABLED_AGENT_IDS = frozenset({"engineering-lead", "implementation-worker"})
PLAN_PATH_EDIT_RULE = "docs/implementation-plans/**"
PLAN_REDIRECTION_DENY_RULE = "*docs/implementation-plans*"
STATE_PATH_EDIT_RULE = ".start-work/**"
STATE_REDIRECTION_DENY_RULE = "*.start-work*"
RUNTIME_HELPERS = ("workflow-tools/start_work_state.py",)
CANONICAL_AGENTS = (
    "accessibility-critic.md",
    "adversarial-reviewer.md",
    "api-design-critic.md",
    "architecture-strategy-critic.md",
    "change-verifier.md",
    "database-engineering-critic.md",
    "design-critic.md",
    "distributed-systems-concurrency-critic.md",
    "documentation-critic.md",
    "domain-model-critic.md",
    "engineering-lead.md",
    "engineering-review-board.md",
    "frontend-architecture-interaction-critic.md",
    "implementation-worker.md",
    "internationalization-localization-critic.md",
    "performance-critic.md",
    "plan-orchestrator.md",
    "prompt-critic.md",
    "release-readiness-reviewer.md",
    "security-critic.md",
    "technical-debt-auditor.md",
    "technical-researcher.md",
    "testing-critic.md",
)
ACTIVE_WORKFLOW_FIXED_FILES = (
    ".gitignore",
    "AGENTS.md",
    "README.md",
    "docs/engineering-agent-governance.md",
    "docs/implementation-plans/README.md",
    "docs/implementation-plans/TEMPLATE.md",
    "opencode/manifest.json",
)
RETIRED_COMMAND_ID_TOKENS = (
    "planning-coordinator",
    "prepare-work",
    "record-plan-review",
    "revise-plan",
    "approve-plan",
    "normalize-plan",
    "execute-plan",
)
RETIRED_LIFECYCLE_PHRASES = (
    "Ready With Revisions",
    "Not Ready",
    "Approve With Follow-ups",
    "Request Changes",
)
CANONICAL_COMMAND_OWNERS = {
    "audit-technical-debt.md": "engineering-review-board",
    "convert-tapestry-plan.md": "plan-orchestrator",
    "investigate-regression.md": "engineering-review-board",
    "review-implementation.md": "engineering-review-board",
    "review-plan.md": "engineering-review-board",
    "start-work.md": "plan-orchestrator",
}
CANONICAL_COMMANDS = tuple(sorted(CANONICAL_COMMAND_OWNERS))
COMMAND_PROMPT_CONTRACTS = {
    "start-work.md": (
        "Handle `/start-work [<request-or-plan-path>] [instructions]`",
        "obtain normal runtime approval and acquire complete provisional child-lock ownership first",
        'python3 -I "$HOME/.config/opencode/workflow-tools/start_work_state.py" acquire --repo-root .',
        "The acquisition operation and `--repo-root .` are allowlisted literals.",
        "Do not read a locator, pointer, source, plan, allocation, or repository execution state before that ownership is complete.",
        "Never put human input into a helper-launch shell string",
        "Do not use concatenation, redirection, pipes, substitution, or an extra shell operation.",
        "Display the resolved canonical path and its checked and unchecked numbered TODOs",
        "explicit human confirmation before any plan, sidebar, delegation, or implementation mutation.",
        "For a new request, allocate a closed lean plan",
        "execute by default. Plan-only behavior requires an explicit human request.",
        "For an explicit lean path, validate and reconcile the plan",
        "For an immutable legacy canonical plan, preserve the source, allocate a max-plus-one lean successor",
        "For conversational updates to an identified lean plan",
        "accept exactly 1 MiB and reject limit-plus-one data.",
    ),
    "convert-tapestry-plan.md": (
        "This command is plan-only by default. Execute only when the human explicitly asks to execute.",
        "Acquire complete provisional child-lock ownership before reading the human source locator",
        "Obtain normal runtime approval and use only this exact isolated allowlisted acquisition literal:",
        'python3 -I "$HOME/.config/opencode/workflow-tools/start_work_state.py" acquire --repo-root .',
        "The operation and `--repo-root .` are literals;",
        "no human locator, request, instruction, repository string, or alternate target may enter its shell string or argv.",
        "Do not use concatenation, redirection, pipes, substitution, or an extra shell operation.",
        "Preserve the source unchanged",
        "create only a metadata-free lean destination",
        "route any follow-up to `/start-work <destination>`.",
    ),
    "review-plan.md": (
        "optional, read-only advice only",
        "no readiness, approval, sign-off, persistence, or execution gate.",
        "Route any follow-up to top-level `/start-work <path>`.",
    ),
    "review-implementation.md": (
        "optional, read-only advice only",
        "no readiness, approval, sign-off, persistence, or execution gate.",
        "Route any follow-up to top-level `/start-work <path>`.",
    ),
}
RETAINED_ROUTE_CONTRACTS = {
    "commands/audit-technical-debt.md": ("Recommend top-level `/start-work`",),
    "commands/investigate-regression.md": ("return it to top-level `/start-work`.",),
    "cleanup/weave-cleanup-checklist.md": (
        "top-level Plan Orchestrator for durable plan writes.",
        "treats advisory review as an execution gate.",
    ),
}
RETAINED_ROUTE_FORBIDDEN_TOKENS = {
    "commands/audit-technical-debt.md": ("/prepare-work",),
    "commands/investigate-regression.md": ("/revise-plan", "Planning Coordinator"),
    "cleanup/weave-cleanup-checklist.md": ("/normalize-plan", "Planning Coordinator"),
}
_PLAN_ORCHESTRATOR_WORKFLOW_HELPER_BASH_RULES = (
    ("*", "deny"),
    ('python3 -I "$HOME/.config/opencode/workflow-tools/start_work_state.py" acquire --repo-root .', "ask"),
    ('python3 -I "$HOME/.config/opencode/workflow-tools/start_work_state.py" finalize --repo-root . --owner-token * --plan-path *', "ask"),
    ('python3 -I "$HOME/.config/opencode/workflow-tools/start_work_state.py" read-pointer --repo-root . --owner-token *', "ask"),
    ('python3 -I "$HOME/.config/opencode/workflow-tools/start_work_state.py" write-pointer --repo-root . --owner-token * --plan-path *', "ask"),
    ('python3 -I "$HOME/.config/opencode/workflow-tools/start_work_state.py" clear-pointer --repo-root . --owner-token * --plan-path * --contract-sha256 * --completed true', "ask"),
    ('python3 -I "$HOME/.config/opencode/workflow-tools/start_work_state.py" release-provisional --repo-root . --owner-token * --known-clean true --no-mutation true --no-child-can-mutate true', "ask"),
    ('python3 -I "$HOME/.config/opencode/workflow-tools/start_work_state.py" release-final --repo-root . --owner-token * --completed-execution true --completed-plan-only false --outcomes-known true --no-child-can-mutate true', "ask"),
    ('python3 -I "$HOME/.config/opencode/workflow-tools/start_work_state.py" release-final --repo-root . --owner-token * --completed-execution false --completed-plan-only true --outcomes-known true --no-child-can-mutate true', "ask"),
    ('python3 -I "$HOME/.config/opencode/workflow-tools/start_work_state.py" recover-stale --repo-root . --prior-human-confirmation true', "ask"),
)
PLAN_ORCHESTRATOR_WORKFLOW_HELPER_BASH_RULES = tuple(
    (rule.replace('"', r'\"'), action)
    for rule, action in _PLAN_ORCHESTRATOR_WORKFLOW_HELPER_BASH_RULES
)
CANONICAL_PLAN_STAGING_ASK_RULE = (
    "git add -- docs/implementation-plans/plans/*/*.md"
)
PLAN_ORCHESTRATOR_GIT_BASH_RULES = (
    ("git status", "allow"),
    ("git status --short", "allow"),
    ("git diff", "allow"),
    ("git diff --cached", "allow"),
    ("git diff HEAD", "allow"),
    ("git diff HEAD^ HEAD", "allow"),
    ("git diff --check", "allow"),
    ("git diff --stat", "allow"),
    ("git show HEAD", "allow"),
    ("git show HEAD^", "allow"),
    ("git log", "allow"),
    ("git log --oneline -10", "allow"),
    ("git rev-parse HEAD", "allow"),
    ("git branch --show-current", "allow"),
    ("git ls-files", "allow"),
    ("git config --get core.hooksPath", "allow"),
    ("git config --get commit.gpgsign", "allow"),
    ("git config --get gpg.format", "allow"),
    ("git add *", "deny"),
    ("git add -- *", "ask"),
    ("git add --", "deny"),
    ("git add -- .", "deny"),
    ("git add -- :*", "deny"),
    ("git add -- /*", "deny"),
    ("git add -- ../*", "deny"),
    ("git add -- */../*", "deny"),
    ("git add -- *..*", "deny"),
    ("git add -- ~*", "deny"),
    ("git commit *", "ask"),
    ("git commit", "allow"),
    ("git commit *--amend*", "deny"),
    ("git commit *--fixup*", "deny"),
    ("git commit *--squash*", "deny"),
    ("git commit *--all*", "deny"),
    ("git commit -a*", "deny"),
    ("git commit * -a*", "deny"),
    ("git commit *--no-verify*", "deny"),
    ("git commit -n*", "deny"),
    ("git commit * -n*", "deny"),
    ("git commit *--no-gpg-sign*", "deny"),
    ("git commit *--allow-empty*", "deny"),
    ("git commit *--interactive*", "deny"),
    ("git commit -i*", "deny"),
    ("git commit * -i*", "deny"),
    ("git commit *--patch*", "deny"),
    ("git commit -p*", "deny"),
    ("git commit * -p*", "deny"),
    ("git commit *--include*", "deny"),
    ("git commit -o*", "deny"),
    ("git commit * -o*", "deny"),
    ("git commit *--only*", "deny"),
    ("git commit *--pathspec-from-file*", "deny"),
    ("git commit *--pathspec-file-nul*", "deny"),
    ("git commit *--no-post-rewrite*", "deny"),
    (PLAN_REDIRECTION_DENY_RULE, "deny"),
    (CANONICAL_PLAN_STAGING_ASK_RULE, "ask"),
    ("git add -- docs/implementation-plans/plans/*/*/*", "deny"),
    ("git add -- *[*", "deny"),
    ("git add -- *{*", "deny"),
    (STATE_REDIRECTION_DENY_RULE, "deny"),
    ("git *>*", "deny"),
    ("git *<*", "deny"),
    ("git *|*", "deny"),
    ("git *&*", "deny"),
    ("git *;*", "deny"),
    ("git *$(*", "deny"),
    ("git *$*", "deny"),
    ("git *`*", "deny"),
)
PLAN_ORCHESTRATOR_BASH_RULES = (
    PLAN_ORCHESTRATOR_WORKFLOW_HELPER_BASH_RULES + PLAN_ORCHESTRATOR_GIT_BASH_RULES
)
PLAN_ORCHESTRATOR_COMMIT_PROMPT_REQUIREMENTS = (
    "explicit current human request",
    "explicit bounded plan TODO",
    "`git-commit`",
    "`security-review` and `security-review-evidence`",
    "freshly reconcile pointer,",
    "exact verified repository-relative paths",
    "never interpolate human or plan",
    "Re-check the staged",
    "observe the resulting commit and worktree",
    "Never amend, bypass hooks or signing",
    "Retain the lock and staged state",
    "Worker remains forbidden to stage or commit.",
    "full OpenCode restart before this authority exists",
    "fresh trusted `git status`/worktree evidence",
    "Separately enumerate each repository-relative path",
    "quote each path as one literal shell word",
    "Never use `*`, `?`, bracket expressions, braces, pathspec magic, `.` shorthand, traversal, substitution, or any other expansion syntax.",
    "Runtime approval is an additional human check, not proof the path is safe.",
    "Stop if a dirty path cannot be represented literally under the command policy.",
)
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
        "git config --get core.hooksPath",
        "git config --get commit.gpgsign",
        "git config --get gpg.format",
        "pwd",
        'python3 -I "$HOME/.config/opencode/workflow-tools/start_work_state.py" acquire --repo-root .',
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
CONFIGURED_MCP_TOOL_PATTERNS = (
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


def opencode_wildcard_match(value: str, pattern: str) -> bool:
    """Match the OpenCode 1.18.1 simple wildcard language."""
    normalized_value = value.replace("\\", "/")
    normalized_pattern = pattern.replace("\\", "/")
    optional_trailing_argument = normalized_pattern.endswith(" *")
    if optional_trailing_argument:
        normalized_pattern = normalized_pattern[:-2]
    escaped_pattern = "".join(
        ".*" if character == "*" else "." if character == "?" else re.escape(character)
        for character in normalized_pattern
    )
    if optional_trailing_argument:
        escaped_pattern += "( .*)?"
    flags = re.DOTALL | (re.IGNORECASE if os.name == "nt" else 0)
    return re.fullmatch(escaped_pattern, normalized_value, flags=flags) is not None


def resolve_opencode_permission_action(
    rules: tuple[tuple[str, str], ...],
    command: str,
    *,
    baseline: str,
) -> str:
    action = baseline
    for pattern, candidate in rules:
        if opencode_wildcard_match(command, pattern):
            action = candidate
    return action


@dataclass(frozen=True)
class DefinitionInventory:
    agents: tuple[str, ...]
    commands: tuple[str, ...]
    support_files: tuple[str, ...]
    runtime_helpers: tuple[str, ...]

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


@dataclass(frozen=True)
class BoundConfigRoot:
    descriptor: int
    device: int
    inode: int
    parent_descriptor: int
    parent_device: int
    parent_inode: int
    relative_targets: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class BoundConfigParent:
    descriptor: int
    device: int
    inode: int


class OpenCodeInstallService:
    def __init__(
        self,
        repo_root: Path | str,
        config_root: Path | str = GLOBAL_CONFIG_ROOT,
        mutation_hook: Callable[[str, str], None] | None = None,
    ) -> None:
        self.repo_root = Path(repo_root).expanduser().resolve()
        self.definition_root = self.repo_root / DEFINITION_ROOT_NAME
        self.config_root = Path(config_root).expanduser().absolute()
        self.sources = {
            kind: self.definition_root / kind
            for kind in INSTALL_KINDS
        }
        self.destinations = {
            kind: self.config_root / kind
            for kind in INSTALL_KINDS
        }
        self.mutation_hook = mutation_hook

    def validate(self) -> OperationResult:
        inventory, errors = self._load_inventory()
        if inventory is None:
            return OperationResult(errors=errors)

        errors.extend(self._validate_support_files(inventory.support_files))
        errors.extend(self._validate_runtime_helpers(inventory.runtime_helpers))
        for kind in DEFINITION_KINDS:
            errors.extend(self._validate_kind(kind, inventory.for_kind(kind)))

        if not errors:
            agent_metadata = self._agent_metadata(inventory)
            errors.extend(self._validate_task_delegation(agent_metadata))
            errors.extend(self._validate_command_agents(inventory, agent_metadata))
            errors.extend(self._validate_prompt_contracts(inventory))
        if self._has_canonical_active_workflow_inventory(inventory):
            errors.extend(self._validate_retired_lifecycle_tokens(inventory))

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

        bound, root_missing, errors = self._bind_config_root(create=False)
        if errors:
            return OperationResult(errors=errors)
        if root_missing:
            messages = [f"Would create {kind} symlink" for kind in INSTALL_KINDS]
            if dry_run:
                report_errors = self._revalidate_missing_root_success("setup")
                return OperationResult(messages=messages, errors=report_errors)
            return self._create_and_setup(messages)
        assert bound is not None
        try:
            states, errors = self._inspect_destinations(bound, missing_is_error=False)
            if errors:
                return OperationResult(errors=errors)
            messages = [
                f"{kind} symlink is already configured" if states[kind] == "expected" else f"{'Would create' if dry_run else 'Created'} {kind} symlink"
                for kind in INSTALL_KINDS
            ]
            if dry_run or all(state == "expected" for state in states.values()):
                report_errors = self._revalidate_report_state(bound, "setup", states)
                return OperationResult(messages=messages, errors=report_errors)
            return self._create_links(bound, states, messages)
        finally:
            self._close_bound_root(bound)

    def verify(self) -> OperationResult:
        validation = self.validate()
        if not validation.ok:
            return validation

        inventory, inventory_errors = self._load_inventory()
        if inventory is None:
            return OperationResult(errors=inventory_errors)

        bound, missing, errors = self._bind_config_root(create=False)
        if errors or missing or bound is None:
            return OperationResult(errors=errors or ["OpenCode config root is missing"])
        try:
            _, errors = self._inspect_destinations(bound, missing_is_error=True)
            if not errors:
                errors.extend(self._verify_visible_sources(bound, inventory))
            if errors:
                return OperationResult(errors=errors)
            self._before_mutation("success", "verify", bound)
            _, final_errors = self._inspect_destinations(bound, missing_is_error=True)
            if final_errors:
                return OperationResult(errors=final_errors)
            return OperationResult(messages=["OpenCode managed symlinks are configured", f"Visible OpenCode definitions: agents={len(inventory.agents)} commands={len(inventory.commands)} helpers=1"])
        except OSError:
            return OperationResult(errors=["OpenCode configuration root changed"])
        finally:
            self._close_bound_root(bound)

    def _verify_visible_sources(
        self,
        bound: BoundConfigRoot,
        inventory: DefinitionInventory,
    ) -> list[str]:
        self._before_mutation("visibility", "verify", bound)
        _, errors = self._inspect_destinations(bound, missing_is_error=True)
        if errors:
            return errors
        for kind in DEFINITION_KINDS:
            for name in inventory.for_kind(kind):
                source = self.sources[kind] / name
                if source.is_symlink() or not source.is_file():
                    errors.append(f"{kind}: '{name}' is not visible through the symlink")
        helper = self.sources["workflow-tools"] / "start_work_state.py"
        if helper.is_symlink() or not helper.is_file():
            errors.append("runtime helper is not visible through the workflow-tools symlink")
        return errors

    def _revalidate_missing_root_success(self, operation: str) -> list[str]:
        if self.mutation_hook:
            self.mutation_hook("success", operation)
        bound, missing, errors = self._bind_config_root(create=False)
        if errors:
            return errors
        if bound is not None:
            self._close_bound_root(bound)
        if not missing:
            return ["OpenCode configuration root changed"]
        return []

    def _revalidate_report_state(
        self,
        bound: BoundConfigRoot,
        operation: str,
        expected_states: dict[str, str],
    ) -> list[str]:
        try:
            self._before_mutation("success", operation, bound)
            states, errors = self._inspect_destinations(bound, missing_is_error=False)
            if errors:
                return errors
            if states != expected_states:
                return ["OpenCode destination changed"]
            return []
        except OSError:
            return ["OpenCode configuration root changed"]

    def uninstall(self, *, dry_run: bool = False) -> OperationResult:
        bound, missing, errors = self._bind_config_root(create=False)
        if errors:
            return OperationResult(errors=errors)
        if missing:
            report_errors = self._revalidate_missing_root_success("uninstall")
            return OperationResult(
                messages=["No managed OpenCode symlinks are installed"],
                errors=report_errors,
            )
        assert bound is not None
        try:
            states, errors = self._inspect_destinations(bound, missing_is_error=False)
            if errors:
                return OperationResult(errors=errors)
            if all(state == "missing" for state in states.values()):
                report_errors = self._revalidate_report_state(bound, "uninstall", states)
                return OperationResult(
                    messages=["No managed OpenCode symlinks are installed"],
                    errors=report_errors,
                )
            if any(state != "expected" for state in states.values()):
                return OperationResult(errors=["OpenCode install is incomplete; refusing to remove any destination"])
            if dry_run:
                report_errors = self._revalidate_report_state(bound, "uninstall", states)
                return OperationResult(
                    messages=[f"Would remove {kind} symlink" for kind in INSTALL_KINDS],
                    errors=report_errors,
                )
            return self._remove_links(bound)
        finally:
            self._close_bound_root(bound)

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

        manifest_kinds = (*DEFINITION_KINDS, "support_files", "runtime_helpers")
        if not isinstance(data, dict) or set(data) != set(manifest_kinds):
            return None, [
                "OpenCode manifest must contain only agents, commands, support_files, and runtime_helpers lists"
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
            runtime_helpers=values["runtime_helpers"],
        ), []

    @staticmethod
    def _has_canonical_active_workflow_inventory(inventory: DefinitionInventory) -> bool:
        return (
            inventory.agents == CANONICAL_AGENTS
            and inventory.commands == CANONICAL_COMMANDS
            and inventory.support_files == REQUIRED_SUPPORT_FILES
            and inventory.runtime_helpers == RUNTIME_HELPERS
        )

    def _validate_retired_lifecycle_tokens(
        self, inventory: DefinitionInventory
    ) -> list[str]:
        relative_paths = (
            *ACTIVE_WORKFLOW_FIXED_FILES,
            *(f"opencode/agents/{name}" for name in inventory.agents),
            *(f"opencode/commands/{name}" for name in inventory.commands),
            *(f"opencode/{name}" for name in inventory.support_files),
        )
        errors: list[str] = []
        for relative_path in relative_paths:
            text = self._read_active_workflow_inventory_text(relative_path)
            if text is None:
                errors.append(
                    f"active workflow inventory '{relative_path}' is missing or is not a regular UTF-8 file"
                )
                continue
            for token in RETIRED_COMMAND_ID_TOKENS:
                if re.search(
                    rf"(?<![A-Za-z0-9_-]){re.escape(token)}(?![A-Za-z0-9_-])",
                    text,
                ):
                    errors.append(
                        f"active workflow inventory '{relative_path}' contains retired lifecycle token '{token}'"
                    )
            for token in RETIRED_LIFECYCLE_PHRASES:
                if token in text:
                    errors.append(
                        f"active workflow inventory '{relative_path}' contains retired lifecycle token '{token}'"
                    )
        return errors

    def _read_active_workflow_inventory_text(self, relative_path: str) -> str | None:
        path = self.repo_root
        try:
            for part in Path(relative_path).parts:
                path /= part
                if path.is_symlink():
                    return None
            if not path.is_file():
                return None
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            return None

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

    def _validate_runtime_helpers(self, runtime_helpers: tuple[str, ...]) -> list[str]:
        if runtime_helpers != RUNTIME_HELPERS:
            return ["OpenCode manifest runtime_helpers inventory is not canonical"]
        root = self.definition_root / "workflow-tools"
        if root.is_symlink() or not root.is_dir():
            return ["runtime helper root is missing or is not a regular directory"]
        try:
            observed = {entry.name for entry in root.iterdir() if entry.name != "__pycache__"}
        except OSError:
            return ["runtime helper root is not readable"]
        if observed != {"start_work_state.py"}:
            return ["runtime helper root has missing or unexpected entries"]
        helper = root / "start_work_state.py"
        if helper.is_symlink() or not helper.is_file():
            return ["runtime helper is missing or is not a regular non-symlink file"]
        try:
            if helper.resolve(strict=True).parent != root.resolve(strict=True):
                return ["runtime helper is outside the trusted root"]
        except (OSError, RuntimeError):
            return ["runtime helper is outside the trusted root"]
        return []

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
        if agent_id in MCP_ENABLED_AGENT_IDS:
            allowed_tools.update(CONFIGURED_MCP_TOOL_PATTERNS)
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
                    and not (agent_id == "plan-orchestrator" and rule == "git commit")
                    and not (
                        agent_id == "engineering-lead"
                        and (rule, action) in ENGINEERING_LEAD_GIT_BASH_RULES
                    )
                ):
                    errors.append(
                        f"agents: '{name}' bash permission has an unsafe allow rule"
                    )
                    break

        if agent_id == "plan-orchestrator":
            helper_count = len(PLAN_ORCHESTRATOR_WORKFLOW_HELPER_BASH_RULES)
            if (
                not isinstance(bash, tuple)
                or bash[:helper_count] != PLAN_ORCHESTRATOR_WORKFLOW_HELPER_BASH_RULES
            ):
                errors.append(
                    f"agents: '{name}' must preserve canonical workflow-helper permissions"
                )
            if (
                not isinstance(bash, tuple)
                or bash[helper_count:] != PLAN_ORCHESTRATOR_GIT_BASH_RULES
            ):
                errors.append(
                    f"agents: '{name}' must preserve canonical Git permissions"
                )

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
                resolve_opencode_permission_action(bash, command, baseline="ask")
                != expected
                for command, expected in ENGINEERING_LEAD_GIT_EFFECTIVE_ACTIONS
            ):
                errors.append(
                    f"agents: '{name}' must preserve effective git permission actions"
                )
        if agent_id == "plan-orchestrator":
            if permissions.get("todowrite") != "allow":
                errors.append(f"agents: '{name}' must allow todowrite")
        elif agent_id == "engineering-lead":
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
        if agent_id in MCP_ENABLED_AGENT_IDS and any(
            permissions.get(pattern) != "allow"
            for pattern in CONFIGURED_MCP_TOOL_PATTERNS
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
            expected_edit = (("*", "ask"), (PLAN_PATH_EDIT_RULE, "deny"), (STATE_PATH_EDIT_RULE, "deny"))
        elif agent_id == "implementation-worker":
            expected_edit = (("*", "ask"), (PLAN_PATH_EDIT_RULE, "deny"), (STATE_PATH_EDIT_RULE, "deny"))
        elif agent_id == "plan-orchestrator":
            expected_edit = (("*", "ask"), (PLAN_PATH_EDIT_RULE, "ask"), (STATE_PATH_EDIT_RULE, "deny"))
        else:
            expected_edit = "deny"

        errors: list[str] = []
        permitted_edit_values: set[str | tuple[tuple[str, str], ...]] = {expected_edit}
        if agent_id not in {
            "engineering-lead",
            "implementation-worker",
            "plan-orchestrator",
        }:
            permitted_edit_values.add((("*", "deny"),))
        if edit not in permitted_edit_values:
            errors.append(f"agents: '{name}' violates core edit ownership")

        bash = permissions.get("bash")
        if agent_id in ROOT_ASK_AGENT_IDS:
            required_suffix = ((PLAN_REDIRECTION_DENY_RULE, "deny"), (STATE_REDIRECTION_DENY_RULE, "deny"))
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
        expected_edges = {
            "plan-orchestrator": ("implementation-worker",),
            "implementation-worker": (),
        }
        for agent_id, expected in expected_edges.items():
            if agent_id not in agent_metadata:
                continue
            actual = tuple(target for target, _ in agent_metadata[agent_id][1] if target != "*")
            if actual != expected:
                errors.append(f"agents: '{agent_id}.md' violates the approved Task graph")
        if "engineering-lead" in agent_metadata:
            lead_edges = tuple(target for target, _ in agent_metadata["engineering-lead"][1] if target != "*")
            if "plan-orchestrator" in lead_edges or "planning-coordinator" in lead_edges:
                errors.append("agents: 'engineering-lead.md' must not delegate plan authority")
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
        uses_canonical_command_namespace = bool(
            set(inventory.commands) & set(CANONICAL_COMMANDS)
        )
        if uses_canonical_command_namespace and inventory.commands != CANONICAL_COMMANDS:
            errors.append("OpenCode manifest command inventory is not canonical")
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
            expected_owner = CANONICAL_COMMAND_OWNERS.get(name)
            if expected_owner is not None and agent_id != expected_owner:
                errors.append(f"commands: '{name}' must use canonical primary owner")
        return errors

    def _validate_prompt_contracts(self, inventory: DefinitionInventory) -> list[str]:
        contracts = {
            "plan-orchestrator.md": (
                "top-level primary agent, never a Task child",
                "native planned-work TODOs",
                "provisional ownership",
            ),
            "engineering-lead.md": (
                "Never write durable plans or `.start-work/**` state",
                "top-level `/start-work`",
                "even when the request does not use plan vocabulary.",
                "route all durable-contract classification to `/start-work`.",
                "unplanned-session TODOs",
            ),
            "engineering-review-board.md": (
                "top-level, read-only review orchestrator",
                "advisory evidence only",
            ),
            "implementation-worker.md": (
                "Engineering Lead or Plan Orchestrator",
                "`.start-work/**`",
                "edit durable plan paths",
            ),
        }
        errors: list[str] = []
        selected = {"plan-orchestrator.md"} & set(inventory.agents)
        if set(contracts).issubset(inventory.agents):
            selected = set(contracts)
        for name, required in contracts.items():
            if name not in selected:
                continue
            try:
                prompt = (self.sources["agents"] / name).read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                errors.append(f"agents: '{name}' prompt contract is unreadable")
                continue
            if not all(token in " ".join(prompt.split()) for token in required):
                errors.append(f"agents: '{name}' prompt contract is incomplete")
                continue
            if name == "plan-orchestrator.md":
                errors.extend(self._validate_plan_orchestrator_prompt_contract(name, prompt))
        errors.extend(self._validate_command_prompt_contracts(inventory))
        return errors

    def _validate_command_prompt_contracts(self, inventory: DefinitionInventory) -> list[str]:
        """Check checked-in command text only; runtime behavior is not inferred."""
        if not (set(inventory.commands) & set(CANONICAL_COMMANDS)):
            return []
        errors: list[str] = []
        for name, required in COMMAND_PROMPT_CONTRACTS.items():
            try:
                prompt = (self.sources["commands"] / name).read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                errors.append(f"commands: '{name}' prompt contract is unreadable")
                continue
            normalized = " ".join(prompt.split())
            if not all(token in normalized for token in required):
                errors.append(f"commands: '{name}' prompt contract is incomplete")
        for relative_path, required in RETAINED_ROUTE_CONTRACTS.items():
            try:
                prompt = (self.definition_root / relative_path).read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                errors.append(f"OpenCode retained route '{relative_path}' is unreadable")
                continue
            normalized = " ".join(prompt.split())
            if not all(token in normalized for token in required):
                errors.append(f"OpenCode retained route '{relative_path}' contract is incomplete")
            forbidden = RETAINED_ROUTE_FORBIDDEN_TOKENS.get(relative_path, ())
            if any(token in prompt for token in forbidden):
                errors.append(f"OpenCode retained route '{relative_path}' contains obsolete lifecycle routing")
        return errors

    @staticmethod
    def _validate_plan_orchestrator_prompt_contract(name: str, prompt: str) -> list[str]:
        required = (
            "Do not add frontmatter or any other heading, section, lifecycle field, history, provenance, review record, approval field, status, dependency field, or metadata.",
            "For no-path work, display the resolved path and checkbox state, then obtain explicit human confirmation before mutation.",
            "For a new request, allocate and self-check the closed lean shape, then execute by default unless the human explicitly requests plan-only work.",
            "For an explicit valid lean path, validate and reconcile it, then execute its remaining TODOs by default; it does not inherit the no-path confirmation gate.",
            "For an explicit legacy canonical plan, preserve the input, allocate a lean successor without provenance metadata, and execute it by default unless the human explicitly requests plan-only work.",
            "`/convert-tapestry-plan` remains explicit and plan-only by default; execute only when the human also asks to execute.",
            "Conversational updates to a lean plan execute remaining TODOs by default unless the human explicitly requests plan-only work.",
            "Replace the whole native TODO list on every update. Keep at most five entries and zero or one `in_progress` entry.",
            "Start in original plan-step order, retain original step numbers, and use summaries of at most 30 characters excluding the step-number prefix.",
            "On a transition, order entries as most-recent completed, then current, then pending.",
            "A blocked or failed step stays visible with its evidence and never advances a checkbox or window speculatively.",
            "Check a plan step only after observed implementation/validation evidence authorizes it.",
            "After all plan steps are evidenced complete, write the completed-only list once, then replace it with `todos: []`.",
            "Do not clear TODOs on failure, uncertainty, or partial reconciliation.",
            "Your self-check is not independent review, ERB evidence, approval, readiness, or sign-off.",
            "ERB output is optional independent advisory evidence, not a prerequisite or lifecycle authority.",
            "or equivalent ordinary conversation",
            "Only a read-only explanation with no mutation is exempt from acquisition.",
            "Parse locators and read pointer, source, allocation, plan, worktree, and execution evidence only after complete provisional child-lock ownership.",
            "On uncertain outcomes or any mutation retain the lock;",
            "Before pointer persistence, require the repository-owned helper to verify a regular non-symlinked `.gitignore`",
            "For plan-only work, persist a pointer when needed, then release only after all mutation outcomes are known and no child can mutate;",
            "Default execution reconciles the pointer, worktree, plan checkboxes, and TODO state before each at-least-once step.",
            "Before every mutable phase, freshly reload the pointer, plan, and worktree evidence while holding the lock; never rely on stale evidence.",
            *PLAN_ORCHESTRATOR_COMMIT_PROMPT_REQUIREMENTS,
        )
        normalized = " ".join(prompt.split())
        if LEAN_PLAN_TEMPLATE not in prompt or not all(token in normalized for token in required):
            return [f"agents: '{name}' prompt contract is incomplete"]
        return []

    def _config_parent(self) -> Path:
        return self.config_root.parent

    def _validate_config_parent(self) -> tuple[tuple[int, int] | None, list[str]]:
        parent = self._config_parent()
        base = parent.parent
        try:
            base_stat = base.lstat()
            if stat.S_ISLNK(base_stat.st_mode) or not stat.S_ISDIR(base_stat.st_mode):
                return None, ["OpenCode configuration base is unsafe"]
            current = base
            for name in (parent.name,):
                current /= name
                if not current.exists() and not current.is_symlink():
                    return None, ["OpenCode configuration parent is missing"]
                current_stat = current.lstat()
                if stat.S_ISLNK(current_stat.st_mode) or not stat.S_ISDIR(current_stat.st_mode):
                    return None, ["OpenCode configuration parent is unsafe"]
            resolved_parent = parent.resolve(strict=True)
            resolved_repo = self.repo_root.resolve(strict=True)
            sources = [source.resolve(strict=True) for source in self.sources.values()]
            if resolved_parent == resolved_repo or resolved_repo in resolved_parent.parents or any(
                resolved_parent == source or source in resolved_parent.parents for source in sources
            ):
                return None, ["OpenCode configuration root is inside a managed source"]
        except (OSError, RuntimeError):
            return None, ["OpenCode configuration parent is unsafe"]
        parent_stat = parent.lstat()
        return (parent_stat.st_dev, parent_stat.st_ino), []

    def _open_config_parent(
        self,
        expected_identity: tuple[int, int],
    ) -> BoundConfigParent | None:
        try:
            flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
            descriptor = os.open(self._config_parent(), flags)
            opened = os.fstat(descriptor)
            path_stat = self._config_parent().lstat()
            identity = (opened.st_dev, opened.st_ino)
            if (
                stat.S_ISLNK(path_stat.st_mode)
                or not stat.S_ISDIR(path_stat.st_mode)
                or identity != expected_identity
                or (path_stat.st_dev, path_stat.st_ino) != expected_identity
            ):
                os.close(descriptor)
                return None
            return BoundConfigParent(descriptor, *identity)
        except OSError:
            return None

    def _assert_parent(self, bound: BoundConfigParent) -> None:
        path_stat = self._config_parent().lstat()
        opened = os.fstat(bound.descriptor)
        if (
            stat.S_ISLNK(path_stat.st_mode)
            or not stat.S_ISDIR(path_stat.st_mode)
            or (path_stat.st_dev, path_stat.st_ino) != (bound.device, bound.inode)
            or (opened.st_dev, opened.st_ino) != (bound.device, bound.inode)
        ):
            raise OSError("configuration parent changed")

    @staticmethod
    def _descriptor_path(descriptor: int, identity: tuple[int, int]) -> Path | None:
        if hasattr(fcntl, "F_GETPATH"):
            try:
                raw = fcntl.fcntl(descriptor, fcntl.F_GETPATH, b"\0" * 1024)
                path = Path(raw.split(b"\0", 1)[0].decode("utf-8"))
                path_stat = path.lstat()
                if (path_stat.st_dev, path_stat.st_ino) == identity:
                    return path
            except (OSError, UnicodeError):
                pass
        try:
            path = Path(os.path.realpath(f"/dev/fd/{descriptor}"))
            path_stat = path.lstat()
            return path if (path_stat.st_dev, path_stat.st_ino) == identity else None
        except OSError:
            return None

    def _bind_config_root(self, *, create: bool) -> tuple[BoundConfigRoot | None, bool, list[str]]:
        expected_parent, errors = self._validate_config_parent()
        if errors:
            return None, False, errors
        assert expected_parent is not None
        if self.mutation_hook:
            self.mutation_hook("after-parent-validation", "opencode")
        parent = self._open_config_parent(expected_parent)
        if parent is None:
            return None, False, ["OpenCode configuration parent changed"]
        root_name = self.config_root.name
        created_identity: tuple[int, int] | None = None
        root_descriptor: int | None = None
        try:
            self._assert_parent(parent)
            if self.mutation_hook:
                self.mutation_hook("after-parent-binding", "opencode")
            self._assert_parent(parent)
            try:
                root_stat = os.stat(root_name, dir_fd=parent.descriptor, follow_symlinks=False)
            except FileNotFoundError:
                root_stat = None
            if root_stat is None:
                if not create:
                    return None, True, []
                if self.mutation_hook:
                    self.mutation_hook("create-root", "opencode")
                self._assert_parent(parent)
                os.mkdir(root_name, dir_fd=parent.descriptor)
                root_stat = os.stat(root_name, dir_fd=parent.descriptor, follow_symlinks=False)
                created_identity = (root_stat.st_dev, root_stat.st_ino)
                if self.mutation_hook:
                    self.mutation_hook("after-root-create", "opencode")
                self._assert_parent(parent)
            if stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode):
                if created_identity is not None:
                    raise OSError("created root changed")
                return None, False, ["OpenCode config root is unsafe"]
            flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
            if self.mutation_hook:
                self.mutation_hook("before-root-open", "opencode")
            self._assert_parent(parent)
            root_descriptor = os.open(root_name, flags, dir_fd=parent.descriptor)
            opened = os.fstat(root_descriptor)
            relative_stat = os.stat(root_name, dir_fd=parent.descriptor, follow_symlinks=False)
            path_stat = self.config_root.lstat()
            identity = (opened.st_dev, opened.st_ino)
            if (
                not stat.S_ISDIR(opened.st_mode)
                or stat.S_ISLNK(relative_stat.st_mode)
                or not stat.S_ISDIR(relative_stat.st_mode)
                or identity != (root_stat.st_dev, root_stat.st_ino)
                or identity != (relative_stat.st_dev, relative_stat.st_ino)
                or identity != (path_stat.st_dev, path_stat.st_ino)
            ):
                raise OSError("configuration root changed during binding")
            if self.mutation_hook:
                self.mutation_hook("after-root-open", "opencode")
            self._assert_parent(parent)
            final_path_stat = self.config_root.lstat()
            if identity != (final_path_stat.st_dev, final_path_stat.st_ino):
                raise OSError("configuration root changed during binding")
            bound_root_path = self._descriptor_path(root_descriptor, identity)
            if bound_root_path is None:
                raise OSError("configuration root cannot be identified safely")
            bound = BoundConfigRoot(
                root_descriptor,
                *identity,
                parent.descriptor,
                parent.device,
                parent.inode,
                tuple(
                    (kind, os.path.relpath(source, start=bound_root_path))
                    for kind, source in self.sources.items()
                ),
            )
            root_descriptor = None
            parent = None
            return bound, False, []
        except OSError:
            if root_descriptor is not None:
                os.close(root_descriptor)
            cleanup_error = False
            if created_identity is not None:
                try:
                    self._assert_parent(parent)
                    current = os.stat(root_name, dir_fd=parent.descriptor, follow_symlinks=False)
                    if (current.st_dev, current.st_ino) != created_identity:
                        raise OSError("created root changed")
                    os.rmdir(root_name, dir_fd=parent.descriptor)
                except OSError:
                    cleanup_error = True
            message = "OpenCode config root cannot be opened safely"
            if cleanup_error:
                message = "OpenCode config root binding failed; cleanup was incomplete"
            return None, False, [message]
        finally:
            if parent is not None:
                os.close(parent.descriptor)

    def _assert_root(self, bound: BoundConfigRoot) -> None:
        parent_stat = self._config_parent().lstat()
        opened_parent = os.fstat(bound.parent_descriptor)
        root_stat = self.config_root.lstat()
        opened = os.fstat(bound.descriptor)
        if (
            stat.S_ISLNK(parent_stat.st_mode)
            or not stat.S_ISDIR(parent_stat.st_mode)
            or (parent_stat.st_dev, parent_stat.st_ino)
            != (bound.parent_device, bound.parent_inode)
            or (opened_parent.st_dev, opened_parent.st_ino)
            != (bound.parent_device, bound.parent_inode)
            or
            stat.S_ISLNK(root_stat.st_mode)
            or not stat.S_ISDIR(root_stat.st_mode)
            or (root_stat.st_dev, root_stat.st_ino) != (bound.device, bound.inode)
            or (opened.st_dev, opened.st_ino) != (bound.device, bound.inode)
        ):
            raise OSError("configuration root changed")

    @staticmethod
    def _close_bound_root(bound: BoundConfigRoot) -> None:
        os.close(bound.descriptor)
        os.close(bound.parent_descriptor)

    def _destination_state(self, bound: BoundConfigRoot, kind: str) -> str:
        self._assert_root(bound)
        try:
            entry = os.lstat(kind, dir_fd=bound.descriptor)
        except FileNotFoundError:
            return "missing"
        if not stat.S_ISLNK(entry.st_mode):
            return "occupied"
        try:
            raw = os.readlink(kind, dir_fd=bound.descriptor)
            if os.path.isabs(raw):
                target = Path(raw).resolve(strict=True)
            elif os.path.normpath(raw) == os.path.normpath(dict(bound.relative_targets)[kind]):
                target = self.sources[kind].resolve(strict=True)
            else:
                return "foreign"
        except (OSError, RuntimeError):
            return "broken"
        return "expected" if target == self.sources[kind].resolve(strict=True) else "foreign"

    def _inspect_destinations(
        self,
        bound: BoundConfigRoot,
        *,
        missing_is_error: bool,
    ) -> tuple[dict[str, str], list[str]]:
        states: dict[str, str] = {}
        errors: list[str] = []
        for kind in INSTALL_KINDS:
            try:
                state = self._destination_state(bound, kind)
            except OSError:
                return states, ["OpenCode configuration root changed"]
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

    def _before_mutation(self, position: str, kind: str, bound: BoundConfigRoot) -> None:
        if self.mutation_hook:
            self.mutation_hook(position, kind)
        self._assert_root(bound)

    def _create_and_setup(self, messages: list[str]) -> OperationResult:
        bound, _, errors = self._bind_config_root(create=True)
        if errors or bound is None:
            return OperationResult(errors=errors or ["Could not create OpenCode config root"])
        try:
            states, errors = self._inspect_destinations(bound, missing_is_error=False)
            return OperationResult(errors=errors) if errors else self._create_links(bound, states, messages)
        finally:
            self._close_bound_root(bound)

    def _create_links(self, bound: BoundConfigRoot, states: dict[str, str], messages: list[str]) -> OperationResult:
        created: list[str] = []
        active_kind = "OpenCode"
        try:
            for kind in INSTALL_KINDS:
                if states[kind] == "expected":
                    continue
                active_kind = kind
                self._before_mutation("create", kind, bound)
                if self._destination_state(bound, kind) != "missing":
                    raise OSError("destination changed")
                os.symlink(str(self.sources[kind]), kind, target_is_directory=True, dir_fd=bound.descriptor)
                created.append(kind)
            self._before_mutation("success", "setup", bound)
            _, errors = self._inspect_destinations(bound, missing_is_error=True)
            if errors:
                raise OSError("verification failed")
            return OperationResult(messages=messages)
        except OSError:
            warnings = self._rollback_created(bound, created)
            return OperationResult(errors=[f"Failed to create {active_kind} symlink; setup was rolled back"], warnings=warnings)

    def _rollback_created(self, bound: BoundConfigRoot, created: list[str]) -> list[str]:
        warnings: list[str] = []
        for kind in reversed(created):
            try:
                self._before_mutation("rollback", kind, bound)
                if self._destination_state(bound, kind) != "expected":
                    raise OSError("destination changed")
                os.unlink(kind, dir_fd=bound.descriptor)
            except OSError:
                warnings.append(f"Could not safely roll back {kind} symlink")
        return warnings

    def _remove_links(self, bound: BoundConfigRoot) -> OperationResult:
        removed: list[str] = []
        active_kind = "OpenCode"
        try:
            for kind in INSTALL_KINDS:
                active_kind = kind
                self._before_mutation("remove", kind, bound)
                if self._destination_state(bound, kind) != "expected":
                    raise OSError("destination changed")
                os.unlink(kind, dir_fd=bound.descriptor)
                removed.append(kind)
            self._before_mutation("success", "uninstall", bound)
            final_states, errors = self._inspect_destinations(bound, missing_is_error=False)
            if errors or any(state != "missing" for state in final_states.values()):
                raise OSError("uninstall verification failed")
            return OperationResult(messages=[f"Removed {kind} symlink" for kind in INSTALL_KINDS])
        except OSError:
            warnings = self._restore_removed(bound, removed)
            return OperationResult(errors=[f"Failed to remove {active_kind} symlink; uninstall was rolled back"], warnings=warnings)

    def _restore_removed(self, bound: BoundConfigRoot, removed: list[str]) -> list[str]:
        warnings: list[str] = []
        for kind in removed:
            try:
                self._before_mutation("restore", kind, bound)
                if self._destination_state(bound, kind) != "missing":
                    raise OSError("destination changed")
                os.symlink(str(self.sources[kind]), kind, target_is_directory=True, dir_fd=bound.descriptor)
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
        help="Create the managed agents, commands, and workflow-tools symlinks.",
    )
    setup_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report changes without applying them.",
    )

    subcommands.add_parser("verify", help="Verify definitions and all three symlinks.")
    subcommands.add_parser("doctor", help="Validate definitions and all three symlinks.")

    uninstall_parser = subcommands.add_parser(
        "uninstall",
        help="Remove all three symlinks when this repository owns them.",
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
