import os
import tempfile
import unittest
from pathlib import Path

from tools.opencode_contracts import (
    ENGINEERING_LEAD_GIT_BASH_RULES,
    ENGINEERING_LEAD_PLAN_STAGING_PROMPT_REQUIREMENTS,
    PLAN_ORCHESTRATOR_BASH_RULES,
)
from tools.opencode_frontmatter import parse_frontmatter
from tools.opencode_install import (
    OpenCodeInstallService,
    opencode_wildcard_match,
)


from tests.opencode_test_support import (
    SUPPORT_FILES,
    create_opencode_repo,
    create_plan_orchestrator_repo,
    plan_orchestrator_source,
    render_lead_permissions,
    resolve_opencode_action,
    write_agent_definition,
)


class OpenCodeInstallServiceTests(unittest.TestCase):
    def test_validate_accepts_manifested_definitions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertTrue(result.ok)
            self.assertIn("agents=1", result.messages[0])
            self.assertIn("commands=1", result.messages[0])

    def test_validate_accepts_ask_gated_external_directory_permission(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            definition = repo / "opencode" / "agents" / "reviewer.md"
            definition.write_text(
                definition.read_text(encoding="utf-8").replace(
                    "  edit: deny\n",
                    "  external_directory:\n"
                    '    "*": ask\n'
                    "  edit: deny\n",
                    1,
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertTrue(result.ok, result.errors)

    def test_validate_rejects_unprompted_external_directory_permission(self) -> None:
        cases = (
            "  external_directory: allow\n",
            "  external_directory:\n"
            '    "*": deny\n'
            '    "~/projects/<external-project>/**": allow\n',
        )
        for permission in cases:
            with self.subTest(permission=permission), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(root)
                definition = repo / "opencode" / "agents" / "reviewer.md"
                definition.write_text(
                    definition.read_text(encoding="utf-8").replace(
                        "  edit: deny\n",
                        f"{permission}  edit: deny\n",
                        1,
                    ),
                    encoding="utf-8",
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(
                    any(
                        "external_directory permission must require approval or deny access"
                        in error
                        for error in result.errors
                    ),
                    result.errors,
                )

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

    def test_validate_accepts_agents_without_steps_and_rejects_steps_field(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            agent = repo / "opencode" / "agents" / "reviewer.md"
            without_steps = agent.read_text(encoding="utf-8")

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertTrue(result.ok, result.errors)

            agent.write_text(
                without_steps.replace(
                    "reasoningEffort: high\n",
                    "reasoningEffort: high\nsteps: 10\n",
                    1,
                ),
                encoding="utf-8",
            )
            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("unsupported 'steps' field", result.errors[0])

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
                '    "docs/implementation-plans/plans/**": deny\n'
                '    ".erb/plans/**": ask\n'
                "  bash:\n"
                '    "*": ask\n'
                '    "*docs/implementation-plans/plans*": deny\n'
                '    "*.erb/plans*": deny\n',
                ('    ".erb/plans/**": ask', '    ".erb/plans/**": deny'),
            ),
            "implementation-worker.md": (
                '  "*": ask\n'
                "  edit:\n"
                '    "*": ask\n'
                '    "docs/implementation-plans/plans/**": deny\n'
                '    ".erb/plans/**": deny\n'
                "  bash:\n"
                '    "*": ask\n'
                '    "*docs/implementation-plans/plans*": deny\n'
                '    "*.erb/plans*": deny\n',
                ('    ".erb/plans/**": deny', '    ".erb/plans/**": ask'),
            ),
            "planning-coordinator.md": (
                '  "*": deny\n'
                "  edit:\n"
                '    "*": deny\n'
                '    ".erb/plans/**": ask\n'
                "  bash:\n"
                '    "*": deny\n',
                ('    ".erb/plans/**": ask', '    ".erb/plans/**": deny'),
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
                        '    "docs/implementation-plans/plans/**": deny\n'
                        '    ".erb/plans/**": deny\n'
                        "  bash:\n"
                        '    "*": ask\n'
                        '    "*docs/implementation-plans/plans*": deny\n'
                        '    "*.erb/plans*": ask\n',
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

    def test_checked_in_lead_git_rules_resolve_to_expected_v118_actions(self) -> None:
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

        project_root = Path(__file__).parents[1]
        lead, errors = parse_frontmatter(
            "agents",
            "engineering-lead.md",
            (project_root / "opencode/agents/engineering-lead.md").read_text(
                encoding="utf-8"
            ),
        )
        self.assertEqual([], errors)
        assert lead is not None
        bash = lead.permissions["bash"]
        self.assertIsInstance(bash, tuple)
        assert isinstance(bash, tuple)

        for command, expected in cases.items():
            with self.subTest(command=command):
                self.assertEqual(expected, resolve_opencode_action(bash, command))

    def test_checked_in_lead_may_stage_only_canonical_plan_markdown(self) -> None:
        project_root = Path(__file__).parents[1]
        lead, errors = parse_frontmatter(
            "agents",
            "engineering-lead.md",
            (project_root / "opencode/agents/engineering-lead.md").read_text(
                encoding="utf-8"
            ),
        )
        self.assertEqual([], errors)
        assert lead is not None
        bash = lead.permissions["bash"]
        self.assertIsInstance(bash, tuple)
        assert isinstance(bash, tuple)

        cases = {
            "git add -- .erb/plans/example.md": "ask",
            "git add -- .erb/plans/work/01-example.md": "ask",
            "git add -- .erb/plan-state.json": "deny",
            "git add -- .erb/plan-state.json .erb/plans/example.md": "deny",
            "git add -- .erb/plans/work/deep/01-example.md": "deny",
            "git add -- docs/implementation-plans/plans/work/01-example.md": "deny",
            "git add -- docs/implementation-plans/plans/example.md .erb/plans/example.md": "deny",
            "git add -- .erb/plans/example.md docs/implementation-plans/plans/example.md": "deny",
            "git add -- .erb/plans/$(printf example).md": "deny",
            "git diff > .erb/plans/work/01-example.md": "deny",
        }
        for command, expected in cases.items():
            with self.subTest(command=command):
                self.assertEqual(expected, resolve_opencode_action(bash, command))

    def test_checked_in_lead_plan_staging_prompt_is_narrow(self) -> None:
        project_root = Path(__file__).parents[1]
        lead = " ".join(
            (project_root / "opencode/agents/engineering-lead.md")
            .read_text(encoding="utf-8")
            .split()
        )
        for requirement in ENGINEERING_LEAD_PLAN_STAGING_PROMPT_REQUIREMENTS:
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, lead)

    def test_validate_requires_exact_lead_git_rule_matrix(self) -> None:
        mutations = {
            "missing allow": ENGINEERING_LEAD_GIT_BASH_RULES[:-1],
            "downgraded read": tuple(
                (pattern, "ask") if pattern == "git status *" else (pattern, action)
                for pattern, action in ENGINEERING_LEAD_GIT_BASH_RULES
            ),
            "weakened override": tuple(
                (pattern, "allow")
                if pattern == "git commit *--am*"
                else (pattern, action)
                for pattern, action in ENGINEERING_LEAD_GIT_BASH_RULES
            ),
            "extra broad allow": ENGINEERING_LEAD_GIT_BASH_RULES + (("git *", "allow"),),
            "later weakening": ENGINEERING_LEAD_GIT_BASH_RULES + (("git*", "ask"),),
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
                        git_rules=ENGINEERING_LEAD_GIT_BASH_RULES + (weakening_rule,)
                    ),
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(
                    any("override git permissions" in error for error in result.errors),
                    result.errors,
                )

    def test_opencode_wildcard_match_uses_only_star_and_question_mark(self) -> None:
        cases = (
            ("git status", "git status *", True),
            ("git status --short", "git status *", True),
            ("git status --short", "git status", False),
            ("src/file.py", "src/*.py", True),
            ("src/file.py", "src/fil?.py", True),
            ("src/a.py", "src/[a-z].py", False),
            ("src/[a-z].py", "src/[a-z].py", True),
            ("src/0.py", "src/[0-9].py", False),
            ("src/[0-9].py", "src/[0-9].py", True),
            ("src/{a,b}.py", "src/{a,b}.py", True),
            ("src/a.py", "src/{a,b}.py", False),
            ("src/file.py", "src\\file.py", True),
        )
        for value, pattern, expected in cases:
            with self.subTest(value=value, pattern=pattern):
                self.assertEqual(expected, opencode_wildcard_match(value, pattern))

    def test_plan_orchestrator_bash_rules_resolve_to_commit_safety_actions(self) -> None:
        cases = {
            "git status": "allow",
            "git status --short": "allow",
            "git diff": "allow",
            "git diff --cached": "allow",
            "git diff HEAD": "allow",
            "git diff HEAD^ HEAD": "allow",
            "git diff --check": "allow",
            "git diff --stat": "allow",
            "git show HEAD": "allow",
            "git show HEAD^": "allow",
            "git log": "allow",
            "git log --oneline -10": "allow",
            "git rev-parse HEAD": "allow",
            "git branch --show-current": "allow",
            "git ls-files": "allow",
            "git config --get core.hooksPath": "allow",
            "git config --get commit.gpgsign": "allow",
            "git config --get gpg.format": "allow",
            "git add -- AGENTS.md": "ask",
            "git add -- src/changed.py": "ask",
            "git add -- .erb/plans/example.md": "ask",
            "git add -- .erb/plans/opencode/03-complete-plan-workflow-migration.md": "ask",
            "git commit": "allow",
            "git commit -m 'approved message'": "ask",
            "git add src/changed.py": "deny",
            "git add -- .": "deny",
            "git add -- :/": "deny",
            "git add -- :(top)src/changed.py": "deny",
            "git add -- ../outside": "deny",
            "git add -- /tmp/outside": "deny",
            "git add -- .erb/plan-state.json": "deny",
            "git add -- .erb/plans/work/deep/01-example.md": "deny",
            "git add -- docs/implementation-plans/plans/work/01-example.md": "deny",
            "git diff > .erb/plans/work/01-example.md": "deny",
            "git commit --amend": "deny",
            "git commit --no-verify -m message": "deny",
            "git commit --no-gpg-sign -m message": "deny",
            "git commit --allow-empty -m message": "deny",
            "git commit -a -m message": "deny",
            "git commit -am message": "deny",
            "git commit --interactive": "deny",
            "git commit --pathspec-from-file=paths.txt": "deny",
            "git commit --pathspec-from-file paths.txt": "deny",
            "git commit --pathspec-from-file=paths.txt --pathspec-file-nul": "deny",
            "git commit --pathspec-file-nul": "deny",
            "git commit --only src/changed.py": "deny",
            "git fetch origin": "deny",
            "git push origin main": "deny",
            "git rebase HEAD^": "deny",
            "git update-ref refs/heads/main HEAD": "deny",
            "git status | tee status.txt": "deny",
            "git add -- src/changed.py && git commit": "deny",
            "git add -- $(git status --short)": "deny",
            "git add -- $PATH": "deny",
            "git add -- `git status --short`": "deny",
            "git add -- src/*.py": "ask",
            "git add -- src/file?.py": "ask",
            "git add -- src/[ab].py": "deny",
            "git add -- src/{a,b}.py": "deny",
            "git add -- .erb/plans/work/01-*.md": "ask",
        }

        for command, expected in cases.items():
            with self.subTest(command=command):
                self.assertEqual(
                    expected,
                    resolve_opencode_action(PLAN_ORCHESTRATOR_BASH_RULES, command, baseline="deny"),
                )

    def test_validate_requires_exact_plan_orchestrator_git_rule_matrix(self) -> None:
        source = plan_orchestrator_source()
        mutations = {
            "missing inspection": (
                source.replace('    "git status": allow\n', "", 1),
                "canonical Git permissions",
            ),
            "downgraded inspection": (
                source.replace(
                    '    "git diff --cached": allow\n',
                    '    "git diff --cached": ask\n',
                    1,
                ),
                "canonical Git permissions",
            ),
            "broad git allow": (
                source.replace(
                    '  bash:\n    "*": deny\n',
                    '  bash:\n    "*": deny\n    "git *": allow\n',
                    1,
                ),
                "canonical Git permissions",
            ),
            "reordered plan exception": (
                source.replace(
                    '    "git add -- .erb/plans/*.md": ask\n', "", 1
                ).replace(
                    '    "git add -- *": ask\n',
                    '    "git add -- .erb/plans/*.md": ask\n'
                    '    "git add -- *": ask\n',
                    1,
                ),
                "canonical Git permissions",
            ),
            "later weakening": (
                source.replace(
                    '    "git *`*": deny\n',
                    '    "git *`*": deny\n    "git *": ask\n',
                    1,
                ),
                "canonical Git permissions",
            ),
        }
        for label, (mutation, expected_error) in mutations.items():
            with self.subTest(case=label), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo, definition = create_plan_orchestrator_repo(root)
                definition.write_text(mutation, encoding="utf-8")

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertTrue(
                    any(expected_error in error for error in result.errors),
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
                    '    "docs/implementation-plans/plans/**": deny\n'
                    '    ".erb/plans/**": deny\n'
                    '    ".erb/plan-state.json": deny\n'
                    "  bash:\n"
                    '    "*": ask\n'
                    '    "*docs/implementation-plans/plans*": deny\n'
                    '    "*.erb/plans*": deny\n'
                    '    "*.erb/plan-state.json*": deny\n'
                    '    "pbcopy *": allow\n'
                    '  "playwright_*": ask\n'
                    '  "chrome-devtools_*": ask\n'
                    '  "serena_*": ask\n'
                    '  "hound_*": ask\n'
                    "  task: deny\n"
                    "  webfetch: ask\n"
                    "  websearch: ask\n"
                ),
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertTrue(
                any("approval-gated MCP tool patterns" in error for error in result.errors)
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
                    "1. [ ] <one atomic implementation outcome; include prerequisites and expected permission gates when applicable>",
                    "- [ ] <one atomic implementation outcome; include prerequisites and expected permission gates when applicable>",
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("template is not the canonical lean format", result.errors[0])

    def test_validate_rejects_missing_or_non_numbered_verification_checkbox(self) -> None:
        for replacement in (
            "",
            "- [ ] <one atomic verification outcome with focused evidence>",
        ):
            with self.subTest(replacement=replacement), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(root)
                template = repo / "opencode" / SUPPORT_FILES[-1]
                template.write_text(
                    template.read_text(encoding="utf-8").replace(
                        "1. [ ] <one atomic verification outcome with focused evidence>",
                        replacement,
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
                '    "docs/implementation-plans/plans/**": deny\n'
                '    ".erb/plans/**": deny\n'
                '    ".erb/plan-state.json": deny\n'
                "  bash:\n"
                '    "*": ask\n'
                '    "*docs/implementation-plans/plans*": deny\n'
                '    "*.erb/plans*": deny\n'
                '    "*.erb/plan-state.json*": deny\n'
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
                '    "docs/implementation-plans/plans/**": deny\n'
                '    ".erb/plans/**": deny\n'
                '    ".erb/plan-state.json": deny\n'
                "  bash:\n"
                '    "*": ask\n'
                '    "*docs/implementation-plans/plans*": deny\n'
                '    "*.erb/plans*": deny\n'
                '    "*.erb/plan-state.json*": deny\n'
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
                    '    "docs/implementation-plans/plans/**": deny\n'
                    '    ".erb/plans/**": deny\n'
                    '    ".erb/plan-state.json": deny\n'
                    "  bash:\n"
                    '    "*": ask\n'
                    '    "just test-web": allow\n'
                    '    "*docs/implementation-plans/plans*": deny\n'
                    '    "*.erb/plans*": deny\n'
                    '    "*.erb/plan-state.json*": deny\n'
                    "  task: deny\n"
                    "  webfetch: ask\n"
                    "  websearch: ask\n"
                ),
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertIn("bash permission has an unsafe allow rule", result.errors[0])

    def test_validate_rejects_concrete_project_defined_just_recipe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            definition = repo / "opencode" / "agents" / "reviewer.md"
            definition.write_text(
                definition.read_text(encoding="utf-8").replace(
                    '    "*": deny\n  task: deny',
                    '    "*": deny\n    "just application-check": deny\n  task: deny',
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertTrue(
                any(
                    "concrete project-defined Just recipe" in error
                    for error in result.errors
                )
            )

    def test_validate_accepts_generic_just_option_permission(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            definition = repo / "opencode" / "agents" / "reviewer.md"
            definition.write_text(
                definition.read_text(encoding="utf-8").replace(
                    '    "*": deny\n  task: deny',
                    '    "*": deny\n    "just --list": deny\n  task: deny',
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertTrue(result.ok, result.errors)

    def test_validate_rejects_machine_specific_definition_paths(self) -> None:
        cases = {
            "agents": "/Users/example/work/application",
            "commands": r"C:\Users\example\work\application",
        }
        for kind, machine_path in cases.items():
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(root)
                name = "reviewer.md" if kind == "agents" else "review.md"
                definition = repo / "opencode" / kind / name
                definition.write_text(
                    definition.read_text(encoding="utf-8")
                    + f"\nInspect {machine_path}.\n",
                    encoding="utf-8",
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(
                    any("machine-specific" in error for error in result.errors)
                )

    def test_validate_accepts_portable_definition_path_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            command = repo / "opencode" / "commands" / "review.md"
            command.write_text(
                command.read_text(encoding="utf-8")
                + "\nInspect `/home/<user>/workspace` or "
                + r"`C:\Users\<user>\workspace`."
                + "\n",
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertTrue(result.ok, result.errors)

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
