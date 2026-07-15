import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from fnmatch import fnmatchcase
from pathlib import Path
from unittest.mock import patch

from tools.opencode_manager import OpenCodeInstallService, main


SUPPORT_FILES = (
    "cleanup/weave-cleanup-checklist.md",
    "config/opencode.merge-fragment.jsonc",
    "project-template/AGENTS-plan-workflow-snippet.md",
    "project-template/docs/implementation-plans/README.md",
    "project-template/docs/implementation-plans/TEMPLATE.md",
)
RUNTIME_HELPERS = ("workflow-tools/start_work_state.py",)

LEAD_GIT_RULES = (
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


def render_lead_permissions(
    *,
    git_rules: tuple[tuple[str, str], ...] = LEAD_GIT_RULES,
    todowrite_action: str = "allow",
) -> str:
    rendered_git_rules = "".join(
        f'    "{pattern}": {action}\n' for pattern, action in git_rules
    )
    return (
        '  "*": ask\n'
        "  edit:\n"
        '    "*": ask\n'
        '    "docs/implementation-plans/**": deny\n'
        '    ".start-work/**": deny\n'
        "  bash:\n"
        '    "*": ask\n'
        f"{rendered_git_rules}"
        '    "*docs/implementation-plans*": deny\n'
        '    "*.start-work*": deny\n'
        '    "pbcopy *": allow\n'
        '  "playwright_*": allow\n'
        '  "chrome-devtools_*": allow\n'
        '  "serena_*": allow\n'
        '  "context7_*": allow\n'
        '  "gh_grep_*": allow\n'
        '  "github_*": allow\n'
        "  task: deny\n"
        "  webfetch: ask\n"
        "  websearch: ask\n"
        f"  todowrite: {todowrite_action}\n"
    )


def resolve_v118_action(
    rules: tuple[tuple[str, str], ...], command: str, *, baseline: str = "ask"
) -> str:
    action = baseline
    for pattern, candidate in rules:
        optional_suffix_match = pattern.endswith(" *") and command == pattern[:-2]
        if optional_suffix_match or fnmatchcase(command, pattern):
            action = candidate
    return action


def write_support_files(repo: Path) -> None:
    contents = {
        "config/opencode.merge-fragment.jsonc": "{\n  // OpenCode merge fragment\n}\n",
        "project-template/AGENTS-plan-workflow-snippet.md": (
            "Use plans in `docs/implementation-plans/plans/<series>/<NN>-<slug>.md`.\n"
        ),
        "project-template/docs/implementation-plans/README.md": (
            "# Plans\n\nUse `docs/implementation-plans/plans/<series>/<NN>-<slug>.md`.\n"
        ),
        "project-template/docs/implementation-plans/TEMPLATE.md": (
            "# <Title>\n\n"
            "## TL;DR\n\n"
            "## Context\n\n"
            "**Original request:**\n\n"
            "**Key repository findings:**\n\n"
            "**Dependencies:**\n\n"
            "## Objectives\n\n"
            "## Guardrails\n\n"
            "## Deliverables\n\n"
            "## Definition of Done\n\n"
            "## TODOs\n\n"
            "1. [ ] <bounded implementation step>\n\n"
            "## Verification\n"
        ),
        "cleanup/weave-cleanup-checklist.md": "# Cleanup\n",
    }
    for relative_path, content in contents.items():
        path = repo / "opencode" / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    for name in ("README.md", "TEMPLATE.md"):
        source = repo / "opencode" / "project-template" / "docs" / "implementation-plans" / name
        destination = repo / "docs" / "implementation-plans" / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
    helper = repo / "opencode" / RUNTIME_HELPERS[0]
    helper.parent.mkdir(parents=True, exist_ok=True)
    helper.write_text("#!/usr/bin/env python3\n", encoding="utf-8")


def write_agent_definition(path: Path, *, mode: str, permissions: str) -> None:
    path.write_text(
        "---\n"
        'description: "Test agent."\n'
        f"mode: {mode}\n"
        "model: openai/test-model\n"
        "reasoningEffort: high\n"
        "steps: 10\n"
        "permission:\n"
        f"{permissions}"
        "---\n\n"
        "Test prompt.\n",
        encoding="utf-8",
    )


def create_opencode_repo(
    root: Path,
    *,
    agents: tuple[str, ...] = ("reviewer.md",),
    commands: tuple[str, ...] = ("review.md",),
) -> Path:
    repo = root / "repo"
    agent_root = repo / "opencode" / "agents"
    command_root = repo / "opencode" / "commands"
    agent_root.mkdir(parents=True)
    command_root.mkdir(parents=True)
    write_support_files(repo)

    for name in agents:
        (agent_root / name).write_text(
            "---\n"
            'description: "Reviews changes."\n'
            "mode: primary\n"
            "model: openai/test-model\n"
            "reasoningEffort: high\n"
            "steps: 10\n"
            "permission:\n"
            "  \"*\": deny\n"
            "  edit: deny\n"
            "  bash:\n"
            "    \"*\": deny\n"
            "  task: deny\n"
            "  webfetch: deny\n"
            "  websearch: deny\n"
            "  question: allow\n"
            "  skill:\n"
            "    \"*\": allow\n"
            "---\n\n"
            "Review the requested change.\n",
            encoding="utf-8",
        )

    agent_name = Path(agents[0]).stem if agents else "missing-agent"
    for name in commands:
        (command_root / name).write_text(
            "---\n"
            'description: "Review a change."\n'
            f"agent: {agent_name}\n"
            "subtask: false\n"
            "---\n\n"
            "Review $ARGUMENTS.\n",
            encoding="utf-8",
        )

    (repo / "opencode" / "manifest.json").write_text(
        json.dumps(
            {
                "agents": list(agents),
                "commands": list(commands),
                "support_files": list(SUPPORT_FILES),
                "runtime_helpers": list(RUNTIME_HELPERS),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return repo


def create_expected_links(repo: Path, config_root: Path, *, relative: bool = False) -> None:
    config_root.mkdir(parents=True)
    for kind in ("agents", "commands", "workflow-tools"):
        source = repo / "opencode" / kind
        target = config_root / kind
        link_source: Path | str = source
        if relative:
            link_source = os.path.relpath(source, start=config_root)
        os.symlink(link_source, target)


def snapshot_tree(root: Path) -> dict[str, bytes]:
    """Capture a simple regular-file fixture without following links."""
    snapshot: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        snapshot[str(path.relative_to(root))] = path.read_bytes()
    return snapshot


def plan_orchestrator_source() -> str:
    return (
        Path(__file__).resolve().parents[1]
        / "opencode"
        / "agents"
        / "plan-orchestrator.md"
    ).read_text(encoding="utf-8")


def create_plan_orchestrator_repo(root: Path) -> tuple[Path, Path]:
    repo = create_opencode_repo(root, agents=("plan-orchestrator.md",), commands=())
    definition = repo / "opencode" / "agents" / "plan-orchestrator.md"
    definition.write_text(plan_orchestrator_source(), encoding="utf-8")
    return repo, definition


class OpenCodeInstallServiceTests(unittest.TestCase):
    def test_validate_accepts_manifested_definitions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertTrue(result.ok)
            self.assertIn("agents=1", result.messages[0])
            self.assertIn("commands=1", result.messages[0])

    def test_validate_rejects_unknown_command_agent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            command = repo / "opencode" / "commands" / "review.md"
            command.write_text(
                command.read_text(encoding="utf-8").replace(
                    "agent: reviewer",
                    "agent: missing",
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("unknown agent 'missing'", result.errors[0])

    def test_validate_rejects_quoted_command_agent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            command = repo / "opencode" / "commands" / "review.md"
            command.write_text(
                command.read_text(encoding="utf-8").replace(
                    "agent: reviewer",
                    'agent: "reviewer"',
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("canonical bare agent", result.errors[0])

    def test_validate_rejects_duplicate_command_agent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            command = repo / "opencode" / "commands" / "review.md"
            command.write_text(
                command.read_text(encoding="utf-8").replace(
                    "agent: reviewer",
                    "agent: reviewer\nagent: reviewer",
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("duplicate 'agent' field", result.errors[0])

    def test_validate_requires_command_agent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            command = repo / "opencode" / "commands" / "review.md"
            command.write_text(
                command.read_text(encoding="utf-8").replace("agent: reviewer\n", ""),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("must define exactly one agent", result.errors[0])

    def test_validate_rejects_noncanonical_command_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            command = repo / "opencode" / "commands" / "review.md"
            command.write_text(
                command.read_text(encoding="utf-8").replace(
                    "subtask: false",
                    "subtask:\n  enabled: false",
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("field 'subtask' must be a non-empty scalar", result.errors[0])

    def test_validate_requires_literal_false_command_subtask(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            command = repo / "opencode" / "commands" / "review.md"
            command.write_text(
                command.read_text(encoding="utf-8").replace(
                    "subtask: false",
                    "subtask: true",
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("literal 'subtask: false'", result.errors[0])

    def test_validate_rejects_command_agent_that_is_not_primary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root, agents=("reviewer.md", "worker.md"))
            worker = repo / "opencode" / "agents" / "worker.md"
            worker.write_text(
                worker.read_text(encoding="utf-8").replace(
                    "mode: primary",
                    "mode: subagent",
                ),
                encoding="utf-8",
            )
            command = repo / "opencode" / "commands" / "review.md"
            command.write_text(
                command.read_text(encoding="utf-8").replace(
                    "agent: reviewer",
                    "agent: worker",
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("must reference a manifested primary agent", result.errors[0])

    def test_validate_rejects_duplicate_agent_frontmatter_field(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            agent = repo / "opencode" / "agents" / "reviewer.md"
            agent.write_text(
                agent.read_text(encoding="utf-8").replace(
                    "mode: primary",
                    "mode: primary\nmode: primary",
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("duplicate 'mode' field", result.errors[0])

    def test_validate_rejects_task_allow_before_deny_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            agent = repo / "opencode" / "agents" / "reviewer.md"
            agent.write_text(
                agent.read_text(encoding="utf-8").replace(
                    "  task: deny",
                    "  task:\n    reviewer: allow\n    \"*\": deny",
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("wildcard baseline first", result.errors[0])

    def test_validate_rejects_recursive_subagent_task_allow(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            agent = repo / "opencode" / "agents" / "reviewer.md"
            agent.write_text(
                agent.read_text(encoding="utf-8")
                .replace("mode: primary", "mode: subagent")
                .replace(
                    "  task: deny",
                    "  task:\n    \"*\": deny\n    reviewer: allow",
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertTrue(
                any("subagents must not define non-wildcard task rules" in error for error in result.errors)
            )

    def test_validate_rejects_subagent_task_ask_rule(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            agent = repo / "opencode" / "agents" / "reviewer.md"
            agent.write_text(
                agent.read_text(encoding="utf-8")
                .replace("mode: primary", "mode: subagent")
                .replace(
                    "  task: deny",
                    '  task:\n    "*": deny\n    "missing-worker": ask',
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("subagents must not define non-wildcard task rules", result.errors[0])

    def test_validate_rejects_unknown_task_allow_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root, agents=("reviewer.md", "worker.md"))
            worker = repo / "opencode" / "agents" / "worker.md"
            worker.write_text(
                worker.read_text(encoding="utf-8").replace(
                    "mode: primary",
                    "mode: subagent",
                ),
                encoding="utf-8",
            )
            agent = repo / "opencode" / "agents" / "reviewer.md"
            agent.write_text(
                agent.read_text(encoding="utf-8").replace(
                    "  task: deny",
                    "  task:\n    \"*\": deny\n    missing-worker: allow",
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertTrue(
                any("unknown task target 'missing-worker'" in error for error in result.errors)
            )

    def test_validate_rejects_primary_task_ask_for_unknown_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            agent = repo / "opencode" / "agents" / "reviewer.md"
            agent.write_text(
                agent.read_text(encoding="utf-8").replace(
                    "  task: deny",
                    '  task:\n    "*": deny\n    "missing-worker": ask',
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertTrue(
                any("unknown task target 'missing-worker'" in error for error in result.errors)
            )

    def test_validate_rejects_disabled_native_task_targets(self) -> None:
        for target in ("general", "explore", "scout"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(root)
                agent = repo / "opencode" / "agents" / "reviewer.md"
                agent.write_text(
                    agent.read_text(encoding="utf-8").replace(
                        "  task: deny",
                        f'  task:\n    "*": deny\n    "{target}": allow',
                    ),
                    encoding="utf-8",
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertIn(f"unknown task target '{target}'", result.errors[0])

    def test_validate_requires_root_permission_baseline_first_and_expected_action(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            agent = repo / "opencode" / "agents" / "reviewer.md"
            agent.write_text(
                agent.read_text(encoding="utf-8").replace(
                    '  "*": deny\n  edit: deny',
                    '  edit: deny\n  "*": ask',
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("permission wildcard baseline must be first", result.errors[0])

    def test_validate_requires_expected_root_permission_baseline_action(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            agent = repo / "opencode" / "agents" / "reviewer.md"
            agent.write_text(
                agent.read_text(encoding="utf-8").replace(
                    '  "*": deny',
                    '  "*": ask',
                    1,
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("permission wildcard baseline must be deny", result.errors[0])

    def test_validate_enforces_core_edit_ownership_and_plan_bash_deny(self) -> None:
        cases = {
            "engineering-lead.md": (
                '  "*": ask\n'
                "  edit:\n"
                '    "*": ask\n'
                '    "docs/implementation-plans/**": ask\n'
                "  bash:\n"
                '    "*": ask\n'
                '    "*docs/implementation-plans*": deny\n',
                ('    "docs/implementation-plans/**": ask', '    "docs/implementation-plans/**": deny'),
            ),
            "implementation-worker.md": (
                '  "*": ask\n'
                "  edit:\n"
                '    "*": ask\n'
                '    "docs/implementation-plans/**": deny\n'
                "  bash:\n"
                '    "*": ask\n'
                '    "*docs/implementation-plans*": deny\n',
                ('    "docs/implementation-plans/**": deny', '    "docs/implementation-plans/**": ask'),
            ),
            "planning-coordinator.md": (
                '  "*": deny\n'
                "  edit:\n"
                '    "*": deny\n'
                '    "docs/implementation-plans/**": ask\n'
                "  bash:\n"
                '    "*": deny\n',
                ('    "docs/implementation-plans/**": ask', '    "docs/implementation-plans/**": deny'),
            ),
        }
        for name, (permissions, (old_rule, new_rule)) in cases.items():
            with self.subTest(agent=name), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(root, agents=(name,))
                agent = repo / "opencode" / "agents" / name
                agent.write_text(
                    agent.read_text(encoding="utf-8").replace(
                        '  "*": deny\n  edit: deny\n  bash:\n    "*": deny\n',
                        permissions,
                    ),
                    encoding="utf-8",
                )
                agent.write_text(
                    agent.read_text(encoding="utf-8").replace(
                        old_rule,
                        new_rule,
                    ),
                    encoding="utf-8",
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(any("core edit ownership" in error for error in result.errors))

    def test_validate_requires_plan_redirection_deny_in_bash_suffix(self) -> None:
        for name in ("engineering-lead.md", "implementation-worker.md"):
            with self.subTest(agent=name), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(root, agents=(name,))
                agent = repo / "opencode" / "agents" / name
                agent.write_text(
                    agent.read_text(encoding="utf-8").replace(
                        '  "*": deny\n  edit: deny\n  bash:\n    "*": deny\n',
                        '  "*": ask\n'
                        "  edit:\n"
                        '    "*": ask\n'
                        f'    "docs/implementation-plans/**": {"ask" if name.startswith("engineering") else "deny"}\n'
                        "  bash:\n"
                        '    "*": ask\n'
                        '    "*docs/implementation-plans*": ask\n',
                    ),
                    encoding="utf-8",
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(any("plan redirection deny" in error for error in result.errors))

    def test_validate_rejects_wildcard_bash_allow_under_deny_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            agent = repo / "opencode" / "agents" / "reviewer.md"
            agent.write_text(
                agent.read_text(encoding="utf-8").replace(
                    '    "*": deny',
                    '    "*": deny\n    "git *": allow',
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertTrue(
                any("bash permission must not allow wildcard rules" in error for error in result.errors)
            )

    def test_validate_accepts_lead_clipboard_and_mcp_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(
                root,
                agents=("engineering-lead.md",),
                commands=(),
            )
            write_agent_definition(
                repo / "opencode" / "agents" / "engineering-lead.md",
                mode="primary",
                permissions=render_lead_permissions(),
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertTrue(result.ok, result.errors)

    def test_lead_git_rules_resolve_to_expected_v118_actions(self) -> None:
        cases = {
            "git status --short": "allow",
            "git diff --cached": "allow",
            "git log --oneline -10": "allow",
            "git branch --list feature/*": "allow",
            "git remote -v": "allow",
            "git worktree list": "allow",
            "git stash list": "allow",
            "git add src/app.py": "allow",
            "git commit": "allow",
            "git commit -m message": "ask",
            "git commit -m message src/app.py": "ask",
            "git fetch": "allow",
            "git fetch origin": "allow",
            "git diff --output=patch.txt": "ask",
            "git diff-tree --output=result HEAD": "ask",
            "git diff-index --ext-diff HEAD": "ask",
            "git reflog show --output=result": "ask",
            "git stash list --output=result": "ask",
            "git grep -Ocustom pattern": "ask",
            "git commit --amend": "ask",
            "git commit -m message --amend": "ask",
            "git commit -a -m message": "ask",
            "git fetch --prune origin": "ask",
            "git fetch -fpP origin": "ask",
            "git fetch -fu origin": "deny",
            "git fetch ../other": "ask",
            "git fetch ~/other": "ask",
            "git fetch $HOME/other": "ask",
            "git pull --ff-only": "ask",
            "git rebase -i HEAD~2": "ask",
            "git remote set-url origin example": "ask",
            "git worktree add ../other": "ask",
            "git status | tee status.txt": "ask",
            "git hash-object -w file": "ask",
            "git commit --no-verify -m message": "deny",
            "git commit -n -m message": "deny",
            "git fetch --update-head-ok origin": "deny",
            "git fetch -u origin": "deny",
            "git push --force origin main": "deny",
            "git push -fv origin main": "deny",
            "git push origin --delete old": "deny",
        }

        for command, expected in cases.items():
            with self.subTest(command=command):
                self.assertEqual(expected, resolve_v118_action(LEAD_GIT_RULES, command))

    def test_validate_requires_exact_lead_git_rule_matrix(self) -> None:
        mutations = {
            "missing allow": LEAD_GIT_RULES[:-1],
            "downgraded read": tuple(
                (pattern, "ask") if pattern == "git status *" else (pattern, action)
                for pattern, action in LEAD_GIT_RULES
            ),
            "weakened override": tuple(
                (pattern, "allow")
                if pattern == "git commit *--am*"
                else (pattern, action)
                for pattern, action in LEAD_GIT_RULES
            ),
            "extra broad allow": LEAD_GIT_RULES + (("git *", "allow"),),
            "later weakening": LEAD_GIT_RULES + (("git*", "ask"),),
        }
        for label, git_rules in mutations.items():
            with self.subTest(case=label), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(
                    root,
                    agents=("engineering-lead.md",),
                    commands=(),
                )
                write_agent_definition(
                    repo / "opencode" / "agents" / "engineering-lead.md",
                    mode="primary",
                    permissions=render_lead_permissions(git_rules=git_rules),
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(
                    any("canonical git permissions" in error for error in result.errors),
                    result.errors,
                )

    def test_validate_rejects_later_git_permission_weakening(self) -> None:
        weakening_rules = (
            ("*commit*", "ask"),
            ("*delete*", "ask"),
            ("*--mirror*", "ask"),
            ("*no-post-rewrite*", "ask"),
        )
        for weakening_rule in weakening_rules:
            with self.subTest(rule=weakening_rule), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(
                    root,
                    agents=("engineering-lead.md",),
                    commands=(),
                )
                write_agent_definition(
                    repo / "opencode" / "agents" / "engineering-lead.md",
                    mode="primary",
                    permissions=render_lead_permissions(
                        git_rules=LEAD_GIT_RULES + (weakening_rule,)
                    ),
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(
                    any("override git permissions" in error for error in result.errors),
                    result.errors,
                )

    def test_validate_requires_lead_todowrite_allow(self) -> None:
        for action in ("ask", "deny"):
            with self.subTest(action=action), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(
                    root,
                    agents=("engineering-lead.md",),
                    commands=(),
                )
                write_agent_definition(
                    repo / "opencode" / "agents" / "engineering-lead.md",
                    mode="primary",
                    permissions=render_lead_permissions(todowrite_action=action),
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(
                    any("todowrite" in error for error in result.errors),
                    result.errors,
                )

    def test_validate_rejects_todowrite_allow_for_other_roles(self) -> None:
        cases = (
            "  todowrite: allow\n",
            '  todowrite:\n    "*": allow\n',
        )
        for permission in cases:
            with self.subTest(permission=permission), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(root)
                agent = repo / "opencode" / "agents" / "reviewer.md"
                agent.write_text(
                    agent.read_text(encoding="utf-8").replace(
                        "  task: deny",
                        f"{permission}  task: deny",
                    ),
                    encoding="utf-8",
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(
                    any("todowrite" in error for error in result.errors),
                    result.errors,
                )

    def test_validate_requires_all_lead_mcp_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(
                root,
                agents=("engineering-lead.md",),
                commands=(),
            )
            write_agent_definition(
                repo / "opencode" / "agents" / "engineering-lead.md",
                mode="primary",
                permissions=(
                    '  "*": ask\n'
                    "  edit:\n"
                    '    "*": ask\n'
                    '    "docs/implementation-plans/**": ask\n'
                    "  bash:\n"
                    '    "*": ask\n'
                    '    "*docs/implementation-plans*": deny\n'
                    '    "pbcopy *": allow\n'
                    '  "playwright_*": allow\n'
                    '  "chrome-devtools_*": allow\n'
                    '  "serena_*": allow\n'
                    '  "context7_*": allow\n'
                    '  "gh_grep_*": allow\n'
                    "  task: deny\n"
                    "  webfetch: ask\n"
                    "  websearch: ask\n"
                ),
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertTrue(
                any("configured MCP tool pattern" in error for error in result.errors)
            )

    def test_validate_rejects_unclosed_markdown_code_fence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            command = repo / "opencode" / "commands" / "review.md"
            command.write_text(
                command.read_text(encoding="utf-8") + "\n```text\nunclosed\n",
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("unclosed Markdown code fence", result.errors[0])

    def test_validate_rejects_code_fence_with_trailing_closing_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            command = repo / "opencode" / "commands" / "review.md"
            command.write_text(
                command.read_text(encoding="utf-8")
                + "\n```text\ncontent\n``` trailing text\n",
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("unclosed Markdown code fence", result.errors[0])

    def test_validate_requires_manifested_regular_support_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            (repo / "opencode" / SUPPORT_FILES[0]).unlink()

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("support file is missing or is not a regular file", result.errors[0])

    def test_validate_rejects_symlinked_support_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            support_file = repo / "opencode" / SUPPORT_FILES[0]
            external_file = root / "external-support.md"
            external_file.write_bytes(support_file.read_bytes())
            support_file.unlink()
            os.symlink(external_file, support_file)

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("support file is missing or is not a regular file", result.errors[0])

    def test_validate_rejects_plan_template_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            template = repo / "opencode" / SUPPORT_FILES[-1]
            template.write_text(
                "---\nstatus: draft\n---\n\n" + template.read_text(encoding="utf-8"),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("template is not the canonical lean format", result.errors[0])

    def test_validate_rejects_reordered_plan_template_heading(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            template = repo / "opencode" / SUPPORT_FILES[-1]
            template.write_text(
                template.read_text(encoding="utf-8").replace(
                    "## TL;DR\n\n## Context", "## Context\n\n## TL;DR"
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("template is not the canonical lean format", result.errors[0])

    def test_validate_rejects_missing_plan_template_context_label(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            template = repo / "opencode" / SUPPORT_FILES[-1]
            template.write_text(
                template.read_text(encoding="utf-8").replace(
                    "**Dependencies:**\n\n", ""
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("template is not the canonical lean format", result.errors[0])

    def test_validate_rejects_non_numbered_plan_template_checkbox(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            template = repo / "opencode" / SUPPORT_FILES[-1]
            template.write_text(
                template.read_text(encoding="utf-8").replace(
                    "1. [ ] <bounded implementation step>",
                    "- [ ] <bounded implementation step>",
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("template is not the canonical lean format", result.errors[0])

    def test_validate_rejects_extra_plan_template_history_heading(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            template = repo / "opencode" / SUPPORT_FILES[-1]
            template.write_text(
                template.read_text(encoding="utf-8") + "\n## Approval History\n",
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("template is not the canonical lean format", result.errors[0])

    def test_validate_rejects_root_plan_template_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            root_template = repo / "docs" / "implementation-plans" / "TEMPLATE.md"
            root_template.write_text("drift\n", encoding="utf-8")

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("root implementation plan files differ", result.errors[0])

    def test_validate_rejects_root_plan_readme_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            root_readme = repo / "docs" / "implementation-plans" / "README.md"
            root_readme.write_text("drift\n", encoding="utf-8")

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("root implementation plan files differ", result.errors[0])

    def test_validate_rejects_symlinked_root_plan_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            root_readme = repo / "docs" / "implementation-plans" / "README.md"
            root_readme.unlink()
            os.symlink(
                repo
                / "opencode"
                / "project-template"
                / "docs"
                / "implementation-plans"
                / "README.md",
                root_readme,
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("root implementation plan file is missing", result.errors[0])

    def test_validate_rejects_scalar_bash_allow(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            agent = repo / "opencode" / "agents" / "reviewer.md"
            agent.write_text(
                agent.read_text(encoding="utf-8").replace(
                    '  bash:\n    "*": deny',
                    "  bash: allow",
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("bash permission must be a rule map", result.errors[0])

    def test_validate_rejects_scalar_bash_ask_for_deny_baseline_agent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            agent = repo / "opencode" / "agents" / "reviewer.md"
            agent.write_text(
                agent.read_text(encoding="utf-8").replace(
                    '  bash:\n    "*": deny',
                    "  bash: ask",
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("bash permission must be deny or a rule map", result.errors[0])

    def test_validate_rejects_mutating_or_unknown_deny_baseline_capabilities(self) -> None:
        cases = (
            ('    "git commit": allow', "bash permission has an unsafe allow rule"),
            ("  mcp: allow", "unsupported permission tool"),
        )
        for addition, expected_error in cases:
            with self.subTest(addition=addition), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(root)
                agent = repo / "opencode" / "agents" / "reviewer.md"
                agent.write_text(
                    agent.read_text(encoding="utf-8").replace(
                        "  task: deny",
                        f"{addition}\n  task: deny",
                    ),
                    encoding="utf-8",
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertIn(expected_error, result.errors[0])

    def test_validate_rejects_unknown_custom_tools_for_ask_baseline_roles(self) -> None:
        cases = (
            (
                "engineering-lead.md",
                "primary",
                '  "*": ask\n'
                "  edit:\n"
                '    "*": ask\n'
                '    "docs/implementation-plans/**": ask\n'
                "  bash:\n"
                '    "*": ask\n'
                '    "*docs/implementation-plans*": deny\n'
                "  task: deny\n"
                "  webfetch: ask\n"
                "  websearch: ask\n"
                "  mcp: allow\n",
            ),
            (
                "implementation-worker.md",
                "subagent",
                '  "*": ask\n'
                "  edit:\n"
                '    "*": ask\n'
                '    "docs/implementation-plans/**": deny\n'
                "  bash:\n"
                '    "*": ask\n'
                '    "*docs/implementation-plans*": deny\n'
                "  task: deny\n"
                "  webfetch: deny\n"
                "  websearch: deny\n"
                "  mcp: allow\n",
            ),
        )
        for name, mode, permissions in cases:
            with self.subTest(agent=name), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(root, agents=(name,), commands=())
                write_agent_definition(
                    repo / "opencode" / "agents" / name,
                    mode=mode,
                    permissions=permissions,
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertIn("unsupported permission tool", result.errors[0])

    def test_validate_rejects_project_runner_bash_allow_for_lead(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(
                root,
                agents=("engineering-lead.md",),
                commands=(),
            )
            write_agent_definition(
                repo / "opencode" / "agents" / "engineering-lead.md",
                mode="primary",
                permissions=(
                    '  "*": ask\n'
                    "  edit:\n"
                    '    "*": ask\n'
                    '    "docs/implementation-plans/**": ask\n'
                    "  bash:\n"
                    '    "*": ask\n'
                    '    "just test-web": allow\n'
                    '    "*docs/implementation-plans*": deny\n'
                    "  task: deny\n"
                    "  webfetch: ask\n"
                    "  websearch: ask\n"
                ),
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("bash permission has an unsafe allow rule", result.errors[0])

    def test_validate_rejects_primary_task_ask_for_manifested_subagent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(
                root,
                agents=("engineering-lead.md", "worker.md"),
            )
            write_agent_definition(
                repo / "opencode" / "agents" / "engineering-lead.md",
                mode="primary",
                permissions=render_lead_permissions().replace(
                    "  task: deny\n",
                    '  task:\n    "*": deny\n    "worker": ask\n',
                ),
            )
            write_agent_definition(
                repo / "opencode" / "agents" / "worker.md",
                mode="subagent",
                permissions=(
                    '  "*": deny\n'
                    "  edit: deny\n"
                    "  bash:\n"
                    '    "*": deny\n'
                    "  task: deny\n"
                    "  webfetch: deny\n"
                    "  websearch: deny\n"
                ),
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("primary task rules must use allow", result.errors[0])

    def test_validate_enforces_role_network_actions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            agent = repo / "opencode" / "agents" / "reviewer.md"
            agent.write_text(
                agent.read_text(encoding="utf-8").replace(
                    "  webfetch: deny\n  websearch: deny",
                    "  webfetch: ask\n  websearch: ask",
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("network permissions must be deny", result.errors[0])

    def test_validate_rejects_unexpected_definition(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            (repo / "opencode" / "agents" / "unexpected.md").write_text(
                "unexpected\n",
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("unexpected asset", result.errors[0])

    def test_validate_rejects_symlinked_definition(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            agent = repo / "opencode" / "agents" / "reviewer.md"
            source = root / "agent-source.md"
            source.write_bytes(agent.read_bytes())
            agent.unlink()
            os.symlink(source, agent)

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("regular non-symlink file", result.errors[0])

    def test_validate_rejects_symlinked_definition_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            external_root = root / "external-opencode"
            (repo / "opencode").rename(external_root)
            os.symlink(external_root, repo / "opencode")

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("source root", result.errors[0])

    def test_setup_creates_both_directory_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_root = root / "config"

            result = OpenCodeInstallService(repo, config_root).setup()

            self.assertTrue(result.ok)
            for kind in ("agents", "commands", "workflow-tools"):
                target = config_root / kind
                self.assertTrue(target.is_symlink())
                self.assertEqual((repo / "opencode" / kind).resolve(), target.resolve())

    def test_setup_is_idempotent_for_correct_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_root = root / "config"
            create_expected_links(repo, config_root)

            result = OpenCodeInstallService(repo, config_root).setup()

            self.assertTrue(result.ok)
            self.assertEqual(3, sum("already configured" in message for message in result.messages))

    def test_setup_accepts_relative_links_to_expected_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_root = root / "config"
            create_expected_links(repo, config_root, relative=True)

            result = OpenCodeInstallService(repo, config_root).setup()

            self.assertTrue(result.ok)

    def test_setup_dry_run_does_not_create_parent_or_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_root = root / "missing"

            result = OpenCodeInstallService(repo, config_root).setup(dry_run=True)

            self.assertTrue(result.ok)
            self.assertFalse(config_root.exists())
            self.assertEqual(3, sum("Would create" in message for message in result.messages))

    def test_setup_preflights_both_destinations_before_mutating(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_root = root / "config"
            (config_root / "commands").mkdir(parents=True)

            result = OpenCodeInstallService(repo, config_root).setup()

            self.assertFalse(result.ok)
            self.assertFalse((config_root / "agents").exists())
            self.assertTrue((config_root / "commands").is_dir())

    def test_setup_refuses_foreign_symlink_without_mutating_sibling(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_root = root / "config"
            foreign = root / "foreign"
            foreign.mkdir()
            config_root.mkdir()
            os.symlink(foreign, config_root / "commands")

            result = OpenCodeInstallService(repo, config_root).setup()

            self.assertFalse(result.ok)
            self.assertFalse((config_root / "agents").exists())
            self.assertEqual(foreign.resolve(), (config_root / "commands").resolve())

    def test_setup_refuses_broken_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_root = root / "config"
            config_root.mkdir()
            os.symlink(root / "missing", config_root / "commands")

            result = OpenCodeInstallService(repo, config_root).setup()

            self.assertFalse(result.ok)
            self.assertIn("broken symlink", result.errors[0])
            self.assertFalse((config_root / "agents").exists())

    def test_setup_rolls_back_first_link_if_second_creation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_root = root / "config"
            real_symlink = os.symlink
            call_count = 0

            def fail_second_link(source: str, target: str, *, target_is_directory: bool, dir_fd: int) -> None:
                nonlocal call_count
                call_count += 1
                if call_count == 2:
                    raise OSError("injected failure")
                real_symlink(source, target, target_is_directory=target_is_directory, dir_fd=dir_fd)

            with patch("tools.opencode_manager.os.symlink", side_effect=fail_second_link):
                result = OpenCodeInstallService(repo, config_root).setup()

            self.assertFalse(result.ok)
            self.assertFalse((config_root / "agents").exists())
            self.assertFalse((config_root / "commands").exists())

    def test_verify_confirms_both_links_and_visible_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_root = root / "config"
            create_expected_links(repo, config_root)

            result = OpenCodeInstallService(repo, config_root).verify()

            self.assertTrue(result.ok)
            self.assertIn("agents=1", result.messages[-1])
            self.assertIn("commands=1", result.messages[-1])

    def test_verify_rejects_one_sided_installation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_root = root / "config"
            config_root.mkdir()
            os.symlink(repo / "opencode" / "agents", config_root / "agents")

            result = OpenCodeInstallService(repo, config_root).verify()

            self.assertFalse(result.ok)
            self.assertTrue(any("commands destination is missing" in error for error in result.errors))

    def test_uninstall_removes_only_the_expected_pair(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_root = root / "config"
            create_expected_links(repo, config_root)

            result = OpenCodeInstallService(repo, config_root).uninstall()

            self.assertTrue(result.ok)
            self.assertFalse((config_root / "agents").exists())
            self.assertFalse((config_root / "commands").exists())
            self.assertTrue((repo / "opencode" / "agents" / "reviewer.md").is_file())

    def test_uninstall_dry_run_preserves_expected_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_root = root / "config"
            create_expected_links(repo, config_root)

            result = OpenCodeInstallService(repo, config_root).uninstall(dry_run=True)

            self.assertTrue(result.ok)
            self.assertTrue((config_root / "agents").is_symlink())
            self.assertTrue((config_root / "commands").is_symlink())

    def test_uninstall_is_idempotent_when_both_links_are_absent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)

            result = OpenCodeInstallService(repo, root / "config").uninstall()

            self.assertTrue(result.ok)
            self.assertIn("No managed OpenCode symlinks", result.messages[0])

    def test_uninstall_refuses_mixed_ownership_without_removing_expected_link(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_root = root / "config"
            config_root.mkdir()
            os.symlink(repo / "opencode" / "agents", config_root / "agents")
            (config_root / "commands").mkdir()

            result = OpenCodeInstallService(repo, config_root).uninstall()

            self.assertFalse(result.ok)
            self.assertTrue((config_root / "agents").is_symlink())
            self.assertTrue((config_root / "commands").is_dir())

    def test_operation_messages_do_not_expose_absolute_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_root = root / "config"
            (config_root / "commands").mkdir(parents=True)

            result = OpenCodeInstallService(repo, config_root).setup()

            output = "\n".join([*result.messages, *result.warnings, *result.errors])
            self.assertNotIn(str(root), output)

    def test_cli_sanitizes_config_parent_creation_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_parent = root / "not-a-directory"
            config_parent.write_text("occupied\n", encoding="utf-8")
            stdout = io.StringIO()
            stderr = io.StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main(
                    [
                        "--repo-root",
                        str(repo),
                        "--config-root",
                        str(config_parent / "opencode"),
                        "setup",
                    ]
                )

            self.assertEqual(1, exit_code)
            output = stdout.getvalue() + stderr.getvalue()
            self.assertNotIn("Traceback", output)
            self.assertNotIn(str(root), output)

    def test_cli_sanitizes_command_read_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            stdout = io.StringIO()
            stderr = io.StringIO()
            original_read_text = Path.read_text

            def fail_command_read(
                path: Path,
                encoding: str | None = None,
                errors: str | None = None,
            ) -> str:
                if path.parent.name == "commands":
                    raise PermissionError("injected private path")
                return original_read_text(path, encoding=encoding, errors=errors)

            with (
                patch.object(Path, "read_text", new=fail_command_read),
                redirect_stdout(stdout),
                redirect_stderr(stderr),
            ):
                exit_code = main(
                    [
                        "--repo-root",
                        str(repo),
                        "--config-root",
                        str(root / "config"),
                        "validate",
                    ]
                )

            self.assertEqual(1, exit_code)
            output = stdout.getvalue() + stderr.getvalue()
            self.assertNotIn("Traceback", output)
            self.assertNotIn(str(root), output)

    def test_cli_sanitizes_service_construction_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            stdout = io.StringIO()
            stderr = io.StringIO()

            with (
                patch.object(
                    Path,
                    "resolve",
                    side_effect=RuntimeError("injected private path"),
                ),
                redirect_stdout(stdout),
                redirect_stderr(stderr),
            ):
                exit_code = main(
                    [
                        "--repo-root",
                        str(repo),
                        "--config-root",
                        str(root / "config"),
                        "validate",
                    ]
                )

            self.assertEqual(1, exit_code)
            output = stdout.getvalue() + stderr.getvalue()
            self.assertNotIn("Traceback", output)
            self.assertNotIn(str(root), output)

    def test_validate_requires_exact_runtime_helper_inventory_and_regular_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            manifest = repo / "opencode" / "manifest.json"
            data = json.loads(manifest.read_text(encoding="utf-8"))
            for helpers in ([], [RUNTIME_HELPERS[0], "workflow-tools/extra.py"]):
                with self.subTest(helpers=helpers):
                    data["runtime_helpers"] = helpers
                    manifest.write_text(json.dumps(data), encoding="utf-8")
                    self.assertFalse(OpenCodeInstallService(repo, root / "config").validate().ok)
            data["runtime_helpers"] = list(RUNTIME_HELPERS)
            manifest.write_text(json.dumps(data), encoding="utf-8")
            helper = repo / "opencode" / RUNTIME_HELPERS[0]
            helper.unlink()
            os.symlink(root / "outside.py", helper)
            result = OpenCodeInstallService(repo, root / "config").validate()
            self.assertFalse(result.ok)
            self.assertTrue(any("runtime helper" in error for error in result.errors))

    def test_setup_creates_three_links_and_verify_requires_visible_helper(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_root = root / "config"
            service = OpenCodeInstallService(repo, config_root)
            self.assertTrue(service.setup().ok)
            self.assertEqual(set(("agents", "commands", "workflow-tools")), {path.name for path in config_root.iterdir()})
            self.assertTrue(service.verify().ok)
            (repo / "opencode" / "workflow-tools" / "start_work_state.py").unlink()
            self.assertFalse(service.verify().ok)

    def test_setup_refuses_unsafe_missing_parent_and_safe_final_root_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            unsafe = OpenCodeInstallService(repo, root / "missing" / "opencode")
            self.assertFalse(unsafe.setup().ok)
            self.assertFalse((root / "missing").exists())
            safe_root = root / "safe" / "opencode"
            safe_root.parent.mkdir()
            service = OpenCodeInstallService(repo, safe_root)
            self.assertTrue(service.setup().ok)
            self.assertTrue(safe_root.is_dir())

    def test_root_swap_before_create_is_fail_closed_and_leaves_sentinel_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_root = root / "config"
            config_root.mkdir()
            replacement = root / "replacement"
            replacement.mkdir()
            sentinel = replacement / "sentinel"
            sentinel.write_text("keep", encoding="utf-8")
            swapped = False

            def swap(position: str, kind: str) -> None:
                nonlocal swapped
                if position == "create" and not swapped:
                    config_root.rename(root / "former-config")
                    replacement.rename(config_root)
                    swapped = True

            result = OpenCodeInstallService(repo, config_root, mutation_hook=swap).setup()
            self.assertFalse(result.ok)
            self.assertEqual("keep", (config_root / "sentinel").read_text(encoding="utf-8"))
            self.assertFalse((config_root / "agents").exists())

    def test_uninstall_refuses_destination_swap_without_touching_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_root = root / "config"
            create_expected_links(repo, config_root)
            sentinel = root / "sentinel"
            sentinel.write_text("keep", encoding="utf-8")
            swapped = False

            def swap(position: str, kind: str) -> None:
                nonlocal swapped
                if position == "remove" and kind == "agents" and not swapped:
                    (config_root / "agents").unlink()
                    os.symlink(sentinel, config_root / "agents")
                    swapped = True

            result = OpenCodeInstallService(repo, config_root, mutation_hook=swap).uninstall()
            self.assertFalse(result.ok)
            self.assertEqual("keep", sentinel.read_text(encoding="utf-8"))
            self.assertTrue((config_root / "commands").is_symlink())

    def test_root_substitution_is_fail_closed_at_each_create_and_setup_success_position(self) -> None:
        positions = (("create", kind) for kind in ("agents", "commands", "workflow-tools"))
        for position in (*positions, ("success", "setup")):
            with self.subTest(position=position), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(root)
                config_root = root / "config"
                config_root.mkdir()
                replacement = root / "replacement"
                replacement.mkdir()
                (replacement / "sentinel").write_bytes(b"replacement")
                before_repo = snapshot_tree(repo)
                before_replacement = snapshot_tree(replacement)
                swapped = False

                def hook(actual_position: str, kind: str) -> None:
                    nonlocal swapped
                    if (actual_position, kind) == position and not swapped:
                        config_root.rename(root / "bound-root")
                        replacement.rename(config_root)
                        swapped = True

                result = OpenCodeInstallService(repo, config_root, mutation_hook=hook).setup()

                self.assertFalse(result.ok)
                self.assertTrue(swapped)
                self.assertEqual(before_repo, snapshot_tree(repo))
                self.assertEqual(before_replacement, snapshot_tree(config_root))

    def test_destination_substitution_is_fail_closed_at_each_create_and_setup_success_position(self) -> None:
        positions = (("create", kind) for kind in ("agents", "commands", "workflow-tools"))
        for position in (*positions, ("success", "setup")):
            with self.subTest(position=position), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(root)
                config_root = root / "config"
                config_root.mkdir()
                sentinel = root / "unrelated-target"
                sentinel.write_bytes(b"sentinel")
                before_repo = snapshot_tree(repo)
                swapped = False

                def hook(actual_position: str, kind: str) -> None:
                    nonlocal swapped
                    if (actual_position, kind) == position and not swapped:
                        target = config_root / (kind if actual_position == "create" else "agents")
                        if target.exists() or target.is_symlink():
                            target.unlink()
                        os.symlink(sentinel, target)
                        swapped = True

                result = OpenCodeInstallService(repo, config_root, mutation_hook=hook).setup()

                self.assertFalse(result.ok)
                self.assertTrue(swapped)
                self.assertEqual(b"sentinel", sentinel.read_bytes())
                self.assertEqual(before_repo, snapshot_tree(repo))

    def test_rollback_refuses_root_and_destination_substitution_and_reports_partial_cleanup(self) -> None:
        for substitution in ("root", "destination"):
            with self.subTest(substitution=substitution), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(root)
                config_root = root / "config"
                config_root.mkdir()
                replacement = root / "replacement"
                replacement.mkdir()
                (replacement / "sentinel").write_bytes(b"replacement")
                sentinel = root / "unrelated-target"
                sentinel.write_bytes(b"sentinel")
                before_repo = snapshot_tree(repo)
                before_replacement = snapshot_tree(replacement)
                real_symlink = os.symlink
                calls = 0
                swapped = False

                def hook(position: str, kind: str) -> None:
                    nonlocal swapped
                    if position != "rollback" or swapped:
                        return
                    if substitution == "root":
                        config_root.rename(root / "bound-root")
                        replacement.rename(config_root)
                    else:
                        target = config_root / kind
                        target.unlink()
                        real_symlink(sentinel, target)
                    swapped = True

                def fail_second_link(source: str, target: str, *, target_is_directory: bool, dir_fd: int) -> None:
                    nonlocal calls
                    calls += 1
                    if calls == 2:
                        raise OSError("injected create failure")
                    real_symlink(source, target, target_is_directory=target_is_directory, dir_fd=dir_fd)

                with patch("tools.opencode_manager.os.symlink", side_effect=fail_second_link):
                    result = OpenCodeInstallService(repo, config_root, mutation_hook=hook).setup()

                self.assertFalse(result.ok)
                self.assertTrue(swapped)
                self.assertTrue(any("roll back" in warning for warning in result.warnings))
                self.assertEqual(before_repo, snapshot_tree(repo))
                self.assertEqual(b"sentinel", sentinel.read_bytes())
                if substitution == "root":
                    self.assertEqual(before_replacement, snapshot_tree(config_root))

    def test_root_substitution_is_fail_closed_at_each_remove_and_uninstall_success_position(self) -> None:
        positions = (("remove", kind) for kind in ("agents", "commands", "workflow-tools"))
        for position in (*positions, ("success", "uninstall")):
            with self.subTest(position=position), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(root)
                config_root = root / "config"
                create_expected_links(repo, config_root)
                replacement = root / "replacement"
                replacement.mkdir()
                (replacement / "sentinel").write_bytes(b"replacement")
                before_repo = snapshot_tree(repo)
                before_replacement = snapshot_tree(replacement)
                swapped = False

                def hook(actual_position: str, kind: str) -> None:
                    nonlocal swapped
                    if (actual_position, kind) == position and not swapped:
                        config_root.rename(root / "bound-root")
                        replacement.rename(config_root)
                        swapped = True

                result = OpenCodeInstallService(repo, config_root, mutation_hook=hook).uninstall()

                self.assertFalse(result.ok)
                self.assertTrue(swapped)
                self.assertEqual(before_repo, snapshot_tree(repo))
                self.assertEqual(before_replacement, snapshot_tree(config_root))

    def test_destination_substitution_is_fail_closed_at_each_remove_uninstall_success_and_verify_position(self) -> None:
        positions = [*( ("remove", kind) for kind in ("agents", "commands", "workflow-tools")), ("success", "uninstall"), ("success", "verify")]
        for operation, position in (("uninstall", position) for position in positions):
            if position == ("success", "verify"):
                operation = "verify"
            with self.subTest(operation=operation, position=position), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(root)
                config_root = root / "config"
                create_expected_links(repo, config_root)
                sentinel = root / "unrelated-target"
                sentinel.write_bytes(b"sentinel")
                before_repo = snapshot_tree(repo)
                swapped = False

                def hook(actual_position: str, kind: str) -> None:
                    nonlocal swapped
                    if (actual_position, kind) == position and not swapped:
                        target = config_root / (kind if actual_position == "remove" else "agents")
                        if target.exists() or target.is_symlink():
                            target.unlink()
                        os.symlink(sentinel, target)
                        swapped = True

                service = OpenCodeInstallService(repo, config_root, mutation_hook=hook)
                result = service.verify() if operation == "verify" else service.uninstall()

                self.assertFalse(result.ok)
                self.assertTrue(swapped)
                self.assertEqual(before_repo, snapshot_tree(repo))
                self.assertEqual(b"sentinel", sentinel.read_bytes())

    def test_restoration_refuses_root_and_destination_substitution_and_reports_partial_restoration(self) -> None:
        for substitution in ("root", "destination"):
            with self.subTest(substitution=substitution), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(root)
                config_root = root / "config"
                create_expected_links(repo, config_root)
                replacement = root / "replacement"
                replacement.mkdir()
                (replacement / "sentinel").write_bytes(b"replacement")
                sentinel = root / "unrelated-target"
                sentinel.write_bytes(b"sentinel")
                before_repo = snapshot_tree(repo)
                before_replacement = snapshot_tree(replacement)
                real_unlink = os.unlink
                calls = 0
                swapped = False

                def hook(position: str, kind: str) -> None:
                    nonlocal swapped
                    if position != "restore" or swapped:
                        return
                    if substitution == "root":
                        config_root.rename(root / "bound-root")
                        replacement.rename(config_root)
                    else:
                        os.symlink(sentinel, config_root / kind)
                    swapped = True

                def fail_second_unlink(target: str, *, dir_fd: int) -> None:
                    nonlocal calls
                    calls += 1
                    if calls == 2:
                        raise OSError("injected remove failure")
                    real_unlink(target, dir_fd=dir_fd)

                with patch("tools.opencode_manager.os.unlink", side_effect=fail_second_unlink):
                    result = OpenCodeInstallService(repo, config_root, mutation_hook=hook).uninstall()

                self.assertFalse(result.ok)
                self.assertTrue(swapped)
                self.assertTrue(any("restore" in warning for warning in result.warnings))
                self.assertEqual(before_repo, snapshot_tree(repo))
                self.assertEqual(b"sentinel", sentinel.read_bytes())
                if substitution == "root":
                    self.assertEqual(before_replacement, snapshot_tree(config_root))

    def test_configuration_root_rejects_mutable_ancestor_aliases_and_managed_source_containment(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            unrelated = root / "unrelated-repository"
            unrelated.mkdir()
            (unrelated / "sentinel").write_bytes(b"unrelated")
            before = snapshot_tree(unrelated)
            aliased_parent = root / "alias-parent"
            os.symlink(unrelated, aliased_parent)
            for config_root in (
                aliased_parent / "opencode",
                repo / "opencode" / "nested-config",
                root / "missing-parent" / "opencode",
            ):
                with self.subTest(config_root=config_root):
                    result = OpenCodeInstallService(repo, config_root).setup()
                    self.assertFalse(result.ok)
                    self.assertEqual(before, snapshot_tree(unrelated))

    def test_root_substitution_before_creation_and_verify_success_reporting_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            parent = root / "safe-parent"
            parent.mkdir()
            config_root = parent / "opencode"
            unrelated = root / "unrelated-target"
            unrelated.mkdir()
            (unrelated / "sentinel").write_bytes(b"unrelated")
            before = snapshot_tree(unrelated)

            def create_root_alias(position: str, kind: str) -> None:
                if position == "create-root":
                    os.symlink(unrelated, config_root)

            result = OpenCodeInstallService(repo, config_root, mutation_hook=create_root_alias).setup()
            self.assertFalse(result.ok)
            self.assertEqual(before, snapshot_tree(unrelated))

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_root = root / "config"
            create_expected_links(repo, config_root)
            replacement = root / "replacement"
            replacement.mkdir()
            (replacement / "sentinel").write_bytes(b"replacement")
            before_repo = snapshot_tree(repo)
            before_replacement = snapshot_tree(replacement)

            def swap_before_verify_report(position: str, kind: str) -> None:
                if (position, kind) == ("success", "verify"):
                    config_root.rename(root / "bound-root")
                    replacement.rename(config_root)

            result = OpenCodeInstallService(repo, config_root, mutation_hook=swap_before_verify_report).verify()
            self.assertFalse(result.ok)
            self.assertEqual(before_repo, snapshot_tree(repo))
            self.assertEqual(before_replacement, snapshot_tree(config_root))

    def test_configuration_root_rejects_symlink_and_non_directory_without_touching_unrelated_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            unrelated = root / "unrelated-target"
            unrelated.mkdir()
            (unrelated / "sentinel").write_bytes(b"unrelated")
            before = snapshot_tree(unrelated)
            symlink_root = root / "symlink-root"
            os.symlink(unrelated, symlink_root)
            file_root = root / "file-root"
            file_root.write_bytes(b"not-a-directory")
            for config_root in (symlink_root, file_root):
                with self.subTest(config_root=config_root):
                    result = OpenCodeInstallService(repo, config_root).setup()
                    self.assertFalse(result.ok)
                    self.assertEqual(before, snapshot_tree(unrelated))

    def test_successful_link_creation_uses_the_bound_directory_descriptor(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_root = root / "config"
            observed_dir_fds: list[int] = []
            real_symlink = os.symlink

            def observe(source: str, target: str, *, target_is_directory: bool, dir_fd: int) -> None:
                observed_dir_fds.append(dir_fd)
                real_symlink(source, target, target_is_directory=target_is_directory, dir_fd=dir_fd)

            with patch("tools.opencode_manager.os.symlink", side_effect=observe):
                result = OpenCodeInstallService(repo, config_root).setup()

            self.assertTrue(result.ok)
            self.assertEqual(3, len(observed_dir_fds))
            self.assertTrue(all(descriptor >= 0 for descriptor in observed_dir_fds))
            self.assertEqual(
                {"agents", "commands", "workflow-tools"},
                {path.name for path in config_root.iterdir()},
            )

    def test_parent_binding_rejects_substitution_at_each_absent_root_position(self) -> None:
        for position in (
            "after-parent-validation",
            "after-parent-binding",
            "after-root-create",
            "after-root-open",
        ):
            with self.subTest(position=position), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(root)
                parent = root / "config"
                parent.mkdir()
                config_root = parent / "opencode"
                replacement = root / "replacement"
                replacement.mkdir()
                (replacement / "sentinel").write_bytes(b"replacement")
                before_repo = snapshot_tree(repo)
                before_replacement = snapshot_tree(replacement)
                swapped = False

                def hook(actual_position: str, kind: str) -> None:
                    nonlocal swapped
                    if actual_position == position and not swapped:
                        parent.rename(root / "bound-parent")
                        replacement.rename(parent)
                        swapped = True

                result = OpenCodeInstallService(repo, config_root, mutation_hook=hook).setup()

                self.assertFalse(result.ok)
                self.assertTrue(swapped)
                self.assertEqual(before_repo, snapshot_tree(repo))
                self.assertEqual(before_replacement, snapshot_tree(parent))
                if position == "after-root-create":
                    self.assertTrue(any("cleanup was incomplete" in error for error in result.errors))

    def test_final_root_binding_rejects_existing_root_substitution_before_and_after_open(self) -> None:
        for position in ("before-root-open", "after-root-open"):
            with self.subTest(position=position), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(root)
                parent = root / "config"
                parent.mkdir()
                config_root = parent / "opencode"
                config_root.mkdir()
                replacement = root / "replacement"
                replacement.mkdir()
                (replacement / "sentinel").write_bytes(b"replacement")
                before_repo = snapshot_tree(repo)
                before_replacement = snapshot_tree(replacement)
                swapped = False

                def hook(actual_position: str, kind: str) -> None:
                    nonlocal swapped
                    if actual_position == position and not swapped:
                        config_root.rename(root / "bound-root")
                        replacement.rename(config_root)
                        swapped = True

                result = OpenCodeInstallService(repo, config_root, mutation_hook=hook).setup()

                self.assertFalse(result.ok)
                self.assertTrue(swapped)
                self.assertEqual(before_repo, snapshot_tree(repo))
                self.assertEqual(before_replacement, snapshot_tree(config_root))

    def test_root_binding_safely_removes_new_empty_root_after_hook_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            parent = root / "config"
            parent.mkdir()
            config_root = parent / "opencode"
            sentinel = parent / "sentinel"
            sentinel.write_bytes(b"safe-parent")

            def fail_after_create(position: str, kind: str) -> None:
                if position == "after-root-create":
                    raise OSError("injected failure")

            bound, missing, errors = OpenCodeInstallService(
                repo,
                config_root,
                mutation_hook=fail_after_create,
            )._bind_config_root(create=True)

            self.assertIsNone(bound)
            self.assertFalse(missing)
            self.assertTrue(errors)
            self.assertFalse(config_root.exists())
            self.assertEqual(b"safe-parent", sentinel.read_bytes())

    def test_root_binding_reports_partial_cleanup_after_created_root_substitution(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            parent = root / "config"
            parent.mkdir()
            config_root = parent / "opencode"

            def replace_created_root(position: str, kind: str) -> None:
                if position == "after-root-create":
                    config_root.rmdir()
                    config_root.mkdir()
                    (config_root / "sentinel").write_bytes(b"replacement")

            result = OpenCodeInstallService(
                repo,
                config_root,
                mutation_hook=replace_created_root,
            ).setup()

            self.assertFalse(result.ok)
            self.assertTrue(any("cleanup was incomplete" in error for error in result.errors))
            self.assertEqual(b"replacement", (config_root / "sentinel").read_bytes())

    def test_root_binding_closes_parent_descriptor_after_successful_safe_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            parent = root / "config"
            parent.mkdir()
            config_root = parent / "opencode"
            opened: list[tuple[str, int]] = []
            real_open = os.open

            def observe_open(
                path: str | os.PathLike[str],
                flags: int,
                mode: int = 0o777,
                *,
                dir_fd: int | None = None,
            ) -> int:
                descriptor = (
                    real_open(path, flags, mode, dir_fd=dir_fd)
                    if dir_fd is not None
                    else real_open(path, flags, mode)
                )
                opened.append((str(path), descriptor))
                return descriptor

            with patch("tools.opencode_manager.os.open", side_effect=observe_open):
                bound, missing, errors = OpenCodeInstallService(repo, config_root)._bind_config_root(create=True)

            self.assertIsNotNone(bound)
            self.assertFalse(missing)
            self.assertEqual([], errors)
            assert bound is not None
            parent_descriptor = opened[0][1]
            os.fstat(parent_descriptor)
            OpenCodeInstallService._close_bound_root(bound)
            with self.assertRaises(OSError):
                os.fstat(parent_descriptor)

    def test_root_binding_closes_parent_and_root_descriptors_on_post_open_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            parent = root / "config"
            parent.mkdir()
            config_root = parent / "opencode"
            opened: list[int] = []
            closed: list[int] = []
            real_open = os.open
            real_close = os.close

            def observe_open(
                path: str | os.PathLike[str],
                flags: int,
                mode: int = 0o777,
                *,
                dir_fd: int | None = None,
            ) -> int:
                descriptor = (
                    real_open(path, flags, mode, dir_fd=dir_fd)
                    if dir_fd is not None
                    else real_open(path, flags, mode)
                )
                opened.append(descriptor)
                return descriptor

            def observe_close(descriptor: int) -> None:
                closed.append(descriptor)
                real_close(descriptor)

            def fail_after_open(position: str, kind: str) -> None:
                if position == "after-root-open":
                    raise OSError("injected failure")

            with (
                patch("tools.opencode_manager.os.open", side_effect=observe_open),
                patch("tools.opencode_manager.os.close", side_effect=observe_close),
            ):
                bound, _, errors = OpenCodeInstallService(
                    repo,
                    config_root,
                    mutation_hook=fail_after_open,
                )._bind_config_root(create=True)

            self.assertIsNone(bound)
            self.assertTrue(errors)
            self.assertEqual(set(opened), set(closed))
            self.assertFalse(config_root.exists())

    def test_early_setup_and_uninstall_reports_revalidate_root_and_destinations(self) -> None:
        cases = (
            ("setup", False, "expected", "root"),
            ("setup", True, "missing", "destination"),
            ("setup", True, "root-missing", "root"),
            ("uninstall", False, "missing", "root"),
            ("uninstall", True, "expected", "destination"),
            ("uninstall", False, "root-missing", "root"),
        )
        for operation, dry_run, state, substitution in cases:
            with self.subTest(operation=operation, dry_run=dry_run, state=state, substitution=substitution), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(root)
                config_root = root / "config"
                if state == "expected":
                    create_expected_links(repo, config_root)
                elif state == "missing":
                    config_root.mkdir()
                else:
                    config_root.parent.mkdir(exist_ok=True)
                replacement = root / "replacement"
                replacement.mkdir()
                (replacement / "sentinel").write_bytes(b"replacement")
                sentinel = root / "sentinel"
                sentinel.write_bytes(b"sentinel")
                before_repo = snapshot_tree(repo)
                before_replacement = snapshot_tree(replacement)
                swapped = False

                def hook(position: str, kind: str) -> None:
                    nonlocal swapped
                    if (position, kind) != ("success", operation) or swapped:
                        return
                    if substitution == "root":
                        if config_root.exists() or config_root.is_symlink():
                            config_root.rename(root / "bound-root")
                        replacement.rename(config_root)
                    else:
                        if (config_root / "agents").exists() or (config_root / "agents").is_symlink():
                            (config_root / "agents").unlink()
                        os.symlink(sentinel, config_root / "agents")
                    swapped = True

                service = OpenCodeInstallService(repo, config_root, mutation_hook=hook)
                result = service.setup(dry_run=dry_run) if operation == "setup" else service.uninstall(dry_run=dry_run)

                self.assertFalse(result.ok)
                self.assertTrue(swapped)
                self.assertEqual(before_repo, snapshot_tree(repo))
                self.assertEqual(b"sentinel", sentinel.read_bytes())
                if substitution == "root":
                    self.assertEqual(before_replacement, snapshot_tree(config_root))

    def test_verify_visibility_rechecks_bound_root_without_following_destination_paths(self) -> None:
        for substitution in ("root", "destination"):
            with self.subTest(substitution=substitution), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(root)
                config_root = root / "config"
                create_expected_links(repo, config_root, relative=True)
                replacement = root / "replacement"
                replacement.mkdir()
                (replacement / "sentinel").write_bytes(b"replacement")
                sentinel = root / "sentinel"
                sentinel.write_bytes(b"sentinel")
                before_repo = snapshot_tree(repo)
                before_replacement = snapshot_tree(replacement)
                swapped = False

                def hook(position: str, kind: str) -> None:
                    nonlocal swapped
                    if (position, kind) != ("visibility", "verify") or swapped:
                        return
                    if substitution == "root":
                        config_root.rename(root / "bound-root")
                        replacement.rename(config_root)
                    else:
                        (config_root / "agents").unlink()
                        os.symlink(sentinel, config_root / "agents")
                    swapped = True

                result = OpenCodeInstallService(repo, config_root, mutation_hook=hook).verify()

                self.assertFalse(result.ok)
                self.assertTrue(swapped)
                self.assertEqual(before_repo, snapshot_tree(repo))
                self.assertEqual(b"sentinel", sentinel.read_bytes())
                if substitution == "root":
                    self.assertEqual(before_replacement, snapshot_tree(config_root))

    def test_validate_requires_plan_orchestrator_closed_prompt_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo, definition = create_plan_orchestrator_repo(root)

            baseline = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(baseline.ok)
            self.assertFalse(
                any("prompt contract" in error for error in baseline.errors),
                baseline.errors,
            )

            definition.write_text(
                plan_orchestrator_source().replace("## Objectives", "## Objective", 1),
                encoding="utf-8",
            )
            heading_result = OpenCodeInstallService(repo, root / "config").validate()
            self.assertTrue(
                any("prompt contract" in error for error in heading_result.errors),
                heading_result.errors,
            )

            prefix = plan_orchestrator_source().split("## Closed Lean Plan Contract", 1)[0]
            definition.write_text(
                prefix
                + "## Closed Lean Plan Contract\n\n"
                + "```markdown\n# <Title>\n\n## Objective\n\n## Scope\n\n## Steps\n\n## Validation\n```\n",
                encoding="utf-8",
            )
            mini_template_result = OpenCodeInstallService(repo, root / "config").validate()
            self.assertTrue(
                any("prompt contract" in error for error in mini_template_result.errors),
                mini_template_result.errors,
            )

    def test_validate_requires_complete_plan_orchestrator_helper_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo, definition = create_plan_orchestrator_repo(root)
            source = plan_orchestrator_source()
            finalize_line = next(
                line for line in source.splitlines() if " finalize --repo-root" in line
            )

            for mutation in (
                "\n".join(line for line in source.splitlines() if line != finalize_line) + "\n",
                source.replace(finalize_line, finalize_line.rsplit(": ", 1)[0] + ": allow"),
            ):
                with self.subTest(mutation=mutation != source):
                    definition.write_text(mutation, encoding="utf-8")
                    result = OpenCodeInstallService(repo, root / "config").validate()
                    self.assertTrue(
                        any("canonical workflow-helper permissions" in error for error in result.errors),
                        result.errors,
                    )


if __name__ == "__main__":
    unittest.main()
