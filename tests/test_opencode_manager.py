import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
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
            "---\n"
            "plan_id: <series>-<NN>\n"
            "series: <series>\n"
            "sequence: <integer>\n"
            "title: <human-readable title>\n"
            "status: draft\n"
            "revision: 1\n"
            "review_decision: pending\n"
            "reviewed_at:\n"
            "approved_at:\n"
            "approved_revision:\n"
            "depends_on: []\n"
            "baseline_commit: <commit or null>\n"
            "execution_owner: engineering-lead\n"
            "source_format: native\n"
            "source_plan:\n"
            "created: YYYY-MM-DD\n"
            "updated: YYYY-MM-DD\n"
            "completed_at:\n"
            "---\n\n"
            "# Plan\n\n"
            "## Executive Summary\n\n"
            "## Objectives\n\n"
            "## Non-Goals\n\n"
            "## Current-State Evidence\n\n"
            "## Dependencies\n\n"
            "## Implementation Sequence\n\n"
            "## Test Strategy\n\n"
            "## Open Decisions\n\n"
            "## ERB Review History\n\n"
            "## Approval History\n\n"
            "## Amendments\n\n"
            "## Execution Record\n"
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
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return repo


def create_expected_links(repo: Path, config_root: Path, *, relative: bool = False) -> None:
    config_root.mkdir(parents=True)
    for kind in ("agents", "commands"):
        source = repo / "opencode" / kind
        target = config_root / kind
        link_source: Path | str = source
        if relative:
            link_source = os.path.relpath(source, start=config_root)
        os.symlink(link_source, target)


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
                    '  "github_*": allow\n'
                    "  task: deny\n"
                    "  webfetch: ask\n"
                    "  websearch: ask\n"
                ),
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertTrue(result.ok, result.errors)

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

    def test_validate_requires_canonical_plan_template_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            template = repo / "opencode" / SUPPORT_FILES[-1]
            template.write_text(
                template.read_text(encoding="utf-8").replace("revision: 1\n", ""),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("template metadata is not canonical", result.errors[0])

    def test_validate_requires_canonical_plan_template_headings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            template = repo / "opencode" / SUPPORT_FILES[-1]
            template.write_text(
                template.read_text(encoding="utf-8").replace("## Approval History\n\n", ""),
                encoding="utf-8",
            )
            root_template = repo / "docs" / "implementation-plans" / "TEMPLATE.md"
            root_template.write_bytes(template.read_bytes())

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("template headings are not canonical", result.errors[0])

    def test_validate_rejects_root_plan_template_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            root_template = repo / "docs" / "implementation-plans" / "TEMPLATE.md"
            root_template.write_text("drift\n", encoding="utf-8")

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
                    '  "github_*": allow\n'
                    "  task:\n"
                    '    "*": deny\n'
                    '    "worker": ask\n'
                    "  webfetch: ask\n"
                    "  websearch: ask\n"
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
            config_root = root / "config" / "opencode"

            result = OpenCodeInstallService(repo, config_root).setup()

            self.assertTrue(result.ok)
            for kind in ("agents", "commands"):
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
            self.assertEqual(2, sum("already configured" in message for message in result.messages))

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
            config_root = root / "missing" / "opencode"

            result = OpenCodeInstallService(repo, config_root).setup(dry_run=True)

            self.assertTrue(result.ok)
            self.assertFalse(config_root.exists())
            self.assertEqual(2, sum("Would create" in message for message in result.messages))

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

            def fail_second_link(source: Path, target: Path, *, target_is_directory: bool) -> None:
                nonlocal call_count
                call_count += 1
                if call_count == 2:
                    raise OSError("injected failure")
                real_symlink(source, target, target_is_directory=target_is_directory)

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


if __name__ == "__main__":
    unittest.main()
