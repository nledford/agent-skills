import io
import json
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools.opencode_manager import (
    ADVERSARIAL_REVIEWER_STAGE_PROMPT_CONTRACTS,
    CANONICAL_AGENT_TOPOLOGY,
    CANONICAL_PERMISSION_PROFILES,
    CANONICAL_PROMPT_SECTION_CONTRACTS,
    CODE_DOCUMENTATION_PROMPT_CONTRACTS,
    COMMAND_PROMPT_CONTRACTS,
    ENGINEERING_LEAD_PLAN_STAGING_PROMPT_REQUIREMENTS,
    EXTERNAL_DIRECTORY_ASK_AGENT_IDS,
    EXTERNAL_DIRECTORY_DOC_TOKENS,
    EXTERNAL_DIRECTORY_SCOPE_INVARIANT,
    HUMAN_CONTROLLED_LIFECYCLE_DOC_TOKENS,
    MCP_SELECTION_PROMPT_CONTRACTS,
    PLAN_ORCHESTRATOR_BASH_RULES,
    PLAN_ORCHESTRATOR_COMMIT_PROMPT_REQUIREMENTS,
    PRIMARY_AGENT_TURN_PROMPT_CONTRACTS,
    SANITIZED_EVIDENCE_INVARIANT,
    STANDARD_CRITIC_AGENT_IDS,
    STANDARD_CRITIC_REQUIRED_HEADINGS,
    STANDARD_CRITIC_REQUIRED_SEMANTICS,
    STANDARD_CRITIC_STAGE_REVIEWER_IDS,
    TECHNICAL_RESEARCHER_EXTERNAL_EGRESS_INVARIANT,
    OpenCodeInstallService,
    main,
    opencode_wildcard_match,
    resolve_opencode_permission_action,
)


SUPPORT_FILES = (
    "cleanup/weave-cleanup-checklist.md",
    "config/opencode.merge-fragment.jsonc",
    "project-template/AGENTS-plan-workflow-snippet.md",
    "project-template/docs/implementation-plans/README.md",
    "project-template/docs/implementation-plans/TEMPLATE.md",
)
ACTIVE_WORKFLOW_FIXED_FILES = (
    ".gitignore",
    "AGENTS.md",
    "README.md",
    "docs/engineering-agent-governance.md",
    "docs/cross-reference-map.md",
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
STALE_LIFECYCLE_MUTATIONS = (
    (".gitignore", "planning-coordinator"),
    ("AGENTS.md", "prepare-work"),
    ("README.md", "record-plan-review"),
    ("docs/engineering-agent-governance.md", "revise-plan"),
    ("docs/implementation-plans/README.md", "approve-plan"),
    ("docs/implementation-plans/TEMPLATE.md", "normalize-plan"),
    ("opencode/manifest.json", "execute-plan"),
    ("opencode/agents/engineering-lead.md", "Ready With Revisions"),
    ("opencode/commands/start-plan.md", "Not Ready"),
    ("opencode/cleanup/weave-cleanup-checklist.md", "Approve With Follow-ups"),
    (
        "opencode/project-template/AGENTS-plan-workflow-snippet.md",
        "Request Changes",
    ),
)

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
LEAD_PLAN_STAGING_RULES = (
    ("git add -- .erb/plans/*.md", "ask"),
    ("git add -- .erb/plans/*/*.md", "ask"),
    ("git add -- .erb/plans/*/*/*", "deny"),
    ("git add -- .erb/plans/*[*", "deny"),
    ("git add -- .erb/plans/*{*", "deny"),
    ("git add -- .erb/plans/*>*", "deny"),
    ("git add -- .erb/plans/*<*", "deny"),
    ("git add -- .erb/plans/*|*", "deny"),
    ("git add -- .erb/plans/*&*", "deny"),
    ("git add -- .erb/plans/*;*", "deny"),
    ("git add -- .erb/plans/*$(*", "deny"),
    ("git add -- .erb/plans/*$*", "deny"),
    ("git add -- .erb/plans/*`*", "deny"),
    ("*docs/implementation-plans/plans*", "deny"),
    ("*.erb/plan-state.json*", "deny"),
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
        '    "docs/implementation-plans/plans/**": deny\n'
        '    ".erb/plans/**": deny\n'
        '    ".erb/plan-state.json": deny\n'
        "  bash:\n"
        '    "*": ask\n'
        f"{rendered_git_rules}"
        '    "*.erb/plans*": deny\n'
        + "".join(
            f'    "{pattern}": {action}\n'
            for pattern, action in LEAD_PLAN_STAGING_RULES
        )
        + '    "pbcopy *": allow\n'
        '  "playwright_*": allow\n'
        '  "chrome-devtools_*": allow\n'
        '  "serena_*": allow\n'
        '  "hound_*": allow\n'
        '  "github_*": allow\n'
        "  task: deny\n"
        "  webfetch: ask\n"
        "  websearch: ask\n"
        f"  todowrite: {todowrite_action}\n"
    )


def resolve_opencode_action(
    rules: tuple[tuple[str, str], ...], command: str, *, baseline: str = "ask"
) -> str:
    return resolve_opencode_permission_action(rules, command, baseline=baseline)


def write_support_files(repo: Path) -> None:
    contents = {
        "config/opencode.merge-fragment.jsonc": "{\n  // OpenCode merge fragment\n}\n",
        "project-template/AGENTS-plan-workflow-snippet.md": (
            "Use one plan at `.erb/plans/<slug>.md` or a genuine multi-plan series at "
            "`.erb/plans/<subject>/<NN>-<slug>.md`.\n"
        ),
        "project-template/docs/implementation-plans/README.md": (
            "# Plans\n\nUse `.erb/plans/<slug>.md` or "
            "`.erb/plans/<subject>/<NN>-<slug>.md`.\n"
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
            "## Verification\n\n"
            "1. [ ] <verification step>\n"
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


def create_canonical_active_workflow_repo(root: Path) -> Path:
    project_root = Path(__file__).parents[1]
    repo = root / "repo"
    manifest_path = project_root / "opencode" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    for relative_path in ACTIVE_WORKFLOW_FIXED_FILES:
        source = project_root / relative_path
        destination = repo / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    for kind in ("agents", "commands", "support_files"):
        source_root = project_root / "opencode"
        destination_root = repo / "opencode"
        for name in manifest[kind]:
            relative_path = Path(kind) / name if kind in ("agents", "commands") else Path(name)
            source = source_root / relative_path
            destination = destination_root / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    return repo


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
                self.assertEqual(expected, resolve_opencode_action(LEAD_GIT_RULES, command))

    def test_checked_in_lead_may_stage_only_canonical_plan_markdown(self) -> None:
        project_root = Path(__file__).parents[1]
        lead, errors = OpenCodeInstallService._parse_frontmatter(
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
                    '  "playwright_*": allow\n'
                    '  "chrome-devtools_*": allow\n'
                    '  "serena_*": allow\n'
                    '  "hound_*": allow\n'
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

    def test_validate_rejects_missing_or_non_numbered_verification_checkbox(self) -> None:
        for replacement in ("", "- [ ] <verification step>"):
            with self.subTest(replacement=replacement), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_opencode_repo(root)
                template = repo / "opencode" / SUPPORT_FILES[-1]
                template.write_text(
                    template.read_text(encoding="utf-8").replace(
                        "1. [ ] <verification step>", replacement
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

    def test_setup_creates_both_directory_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_root = root / "config"

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
            config_root = root / "missing"

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

    def test_setup_creates_two_links_and_verify_requires_visible_definitions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_opencode_repo(root)
            config_root = root / "config"
            service = OpenCodeInstallService(repo, config_root)
            self.assertTrue(service.setup().ok)
            self.assertEqual(
                {"agents", "commands"},
                {path.name for path in config_root.iterdir()},
            )
            self.assertTrue(service.verify().ok)
            (repo / "opencode" / "commands" / "review.md").unlink()
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
        positions = (("create", kind) for kind in ("agents", "commands"))
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
        positions = (("create", kind) for kind in ("agents", "commands"))
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
        positions = (("remove", kind) for kind in ("agents", "commands"))
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
        positions = [*( ("remove", kind) for kind in ("agents", "commands")), ("success", "uninstall"), ("success", "verify")]
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
            self.assertEqual(2, len(observed_dir_fds))
            self.assertTrue(all(descriptor >= 0 for descriptor in observed_dir_fds))
            self.assertEqual(
                {"agents", "commands"},
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

            closed_contract_requirement = (
                "Do not add frontmatter or any other heading, section, lifecycle field, "
                "history, provenance, review record, approval field, status, dependency "
                "field, or metadata."
            )
            pattern = r"\s+".join(
                re.escape(token) for token in closed_contract_requirement.split()
            )
            mutation, replacements = re.subn(
                pattern,
                "closed plan contract requirement removed",
                plan_orchestrator_source(),
                count=1,
            )
            self.assertEqual(1, replacements)
            definition.write_text(
                mutation,
                encoding="utf-8",
            )
            mini_template_result = OpenCodeInstallService(repo, root / "config").validate()
            self.assertTrue(
                any("prompt contract" in error for error in mini_template_result.errors),
                mini_template_result.errors,
            )


    def test_validate_requires_plan_orchestrator_commit_safety_prompt_contract(self) -> None:
        source = plan_orchestrator_source()
        for requirement in PLAN_ORCHESTRATOR_COMMIT_PROMPT_REQUIREMENTS:
            with self.subTest(requirement=requirement), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo, definition = create_plan_orchestrator_repo(root)
                mutation, replacements = re.subn(
                    r"\s+".join(re.escape(token) for token in requirement.split()),
                    "missing commit-safety requirement",
                    source,
                    count=1,
                )
                self.assertEqual(1, replacements)
                definition.write_text(
                    mutation,
                    encoding="utf-8",
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertTrue(
                    any("prompt contract is incomplete" in error for error in result.errors),
                    result.errors,
                )

    def test_validate_requires_lead_plan_staging_prompt_contract(self) -> None:
        project_root = Path(__file__).parents[1]
        source = (project_root / "opencode/agents/engineering-lead.md").read_text(
            encoding="utf-8"
        )
        for requirement in ENGINEERING_LEAD_PLAN_STAGING_PROMPT_REQUIREMENTS:
            with self.subTest(requirement=requirement), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_canonical_active_workflow_repo(root)
                definition = repo / "opencode/agents/engineering-lead.md"
                mutation, replacements = re.subn(
                    r"\s+".join(re.escape(token) for token in requirement.split()),
                    "missing plan-staging requirement",
                    source,
                    count=1,
                )
                self.assertEqual(1, replacements)
                definition.write_text(mutation, encoding="utf-8")

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertTrue(
                    any(
                        "plan-staging prompt contract is incomplete" in error
                        for error in result.errors
                    ),
                    result.errors,
                )

    def test_checked_in_planned_commit_ownership_requires_current_human_request(self) -> None:
        project_root = Path(__file__).parents[1]
        orchestrator_text = re.sub(
            r"\s+",
            " ",
            (project_root / "opencode/agents/plan-orchestrator.md").read_text(
                encoding="utf-8"
            ),
        )
        self.assertIn("only after an explicit current human request", orchestrator_text)
        self.assertIn("during implementation or after implementation completes", orchestrator_text)
        self.assertNotIn("explicit bounded plan TODO", orchestrator_text)

        worker = OpenCodeInstallService._parse_frontmatter(
            "agents",
            "implementation-worker.md",
            (project_root / "opencode/agents/implementation-worker.md").read_text(
                encoding="utf-8"
            ),
        )[0]
        assert worker is not None
        bash = worker.permissions["bash"]
        self.assertIsInstance(bash, tuple)
        assert isinstance(bash, tuple)
        self.assertEqual(resolve_opencode_action(bash, "git add -- src/work.py"), "deny")
        self.assertEqual(resolve_opencode_action(bash, "git commit"), "deny")
        for tool in ("read", "glob", "grep", "list", "lsp"):
            rules = worker.permissions[tool]
            self.assertIsInstance(rules, tuple)
            assert isinstance(rules, tuple)
            self.assertEqual(
                resolve_opencode_action(
                    rules, ".erb/plan-state.json", baseline="deny"
                ),
                "deny",
            )
        self.assertIn("must never stage or commit", orchestrator_text)


    def test_validate_rejects_each_retired_lifecycle_token_in_active_inventory(self) -> None:
        for relative_path, token in STALE_LIFECYCLE_MUTATIONS:
            with self.subTest(relative_path=relative_path, token=token), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_canonical_active_workflow_repo(root)
                target = repo / relative_path

                baseline = OpenCodeInstallService(repo, root / "config").validate()
                self.assertTrue(baseline.ok, baseline.errors)

                original = target.read_text(encoding="utf-8")
                if relative_path == "opencode/manifest.json":
                    target.write_text(
                        original.replace(
                            '  "agents": [',
                            f'  "agents": ["{token}.md"],\n  "agents": [',
                            1,
                        ),
                        encoding="utf-8",
                    )
                else:
                    target.write_text(original + f"\n{token}\n", encoding="utf-8")

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertIn(
                    f"active workflow inventory '{relative_path}' contains retired lifecycle token '{token}'",
                    result.errors,
                )

    def test_validate_ignores_retired_command_id_substrings_in_larger_identifiers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_canonical_active_workflow_repo(root)
            ignored = "\n".join(
                f"unrelated-{token}-variant" for token in RETIRED_COMMAND_ID_TOKENS
            )
            gitignore = repo / ".gitignore"
            gitignore.write_text(
                gitignore.read_text(encoding="utf-8") + f"\n{ignored}\n",
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertTrue(result.ok, result.errors)

    def test_validate_matches_retired_command_ids_in_supported_text_forms(self) -> None:
        for text in (
            "prepare-work",
            "/prepare-work",
            "prepare-work.md",
            "opencode/commands/prepare-work.md",
        ):
            with self.subTest(text=text), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_canonical_active_workflow_repo(root)
                gitignore = repo / ".gitignore"
                gitignore.write_text(
                    gitignore.read_text(encoding="utf-8") + f"\n{text}\n",
                    encoding="utf-8",
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertIn(
                    "active workflow inventory '.gitignore' contains retired lifecycle token 'prepare-work'",
                    result.errors,
                )

    def test_validate_fails_closed_when_active_inventory_text_is_missing_or_unreadable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_canonical_active_workflow_repo(root)
            active_file = repo / "AGENTS.md"
            active_file.unlink()

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertIn(
                "active workflow inventory 'AGENTS.md' is missing or is not a regular UTF-8 file",
                result.errors,
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_canonical_active_workflow_repo(root)
            active_file = repo / "AGENTS.md"
            active_file.write_bytes(b"\xff")

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertIn(
                "active workflow inventory 'AGENTS.md' is missing or is not a regular UTF-8 file",
                result.errors,
            )

    def test_validate_excludes_non_active_workflow_files_from_stale_lifecycle_scan(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_canonical_active_workflow_repo(root)
            stale_text = "\n".join(token for _, token in STALE_LIFECYCLE_MUTATIONS)
            excluded_files = (
                "docs/implementation-plans/plans/current/02-active-work.md",
                "docs/implementation-plans/plans/legacy/01-immutable-legacy.md",
                "tests/stale-lifecycle.md",
                "test-fixtures/stale-lifecycle.md",
                ".weave/history/stale-lifecycle.md",
                "generated/stale-lifecycle.md",
                "unmanifested/stale-lifecycle.md",
            )
            for relative_path in excluded_files:
                path = repo / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(stale_text, encoding="utf-8")

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertTrue(result.ok, result.errors)

    def test_checked_in_command_inventory_owners_and_static_contracts(self) -> None:
        """Validate checked-in text; this does not assert runtime OpenCode behavior."""
        project_root = Path(__file__).parents[1]
        manifest = json.loads((project_root / "opencode/manifest.json").read_text(encoding="utf-8"))
        expected_commands = (
            "address-review.md",
            "audit-technical-debt.md",
            "brainstorm.md",
            "consult-plan.md",
            "create-plan.md",
            "investigate-regression.md",
            "optimize-prompt.md",
            "review-implementation.md",
            "review-plan.md",
            "root-cause-analysis.md",
            "semver.md",
            "start-plan.md",
            "update-plan.md",
        )
        expected_owners = {
            "address-review.md": "engineering-lead",
            "audit-technical-debt.md": "engineering-review-board",
            "brainstorm.md": "engineering-review-board",
            "consult-plan.md": "plan-orchestrator",
            "create-plan.md": "plan-orchestrator",
            "investigate-regression.md": "engineering-review-board",
            "optimize-prompt.md": "engineering-lead",
            "review-implementation.md": "engineering-review-board",
            "review-plan.md": "engineering-review-board",
            "root-cause-analysis.md": "engineering-review-board",
            "semver.md": "engineering-lead",
            "start-plan.md": "plan-orchestrator",
            "update-plan.md": "plan-orchestrator",
        }

        self.assertEqual(len(manifest["agents"]), 23)
        self.assertEqual(tuple(manifest["commands"]), expected_commands)
        self.assertEqual(set(manifest), {"agents", "commands", "support_files"})
        command_root = project_root / "opencode/commands"
        self.assertEqual(tuple(sorted(path.name for path in command_root.iterdir())), expected_commands)
        for name, owner in expected_owners.items():
            parsed, errors = OpenCodeInstallService._parse_frontmatter(
                "commands", name, (command_root / name).read_text(encoding="utf-8")
            )
            self.assertEqual(errors, [])
            assert parsed is not None
            self.assertEqual(parsed.fields["agent"], owner)
            self.assertEqual(parsed.fields["subtask"], "false")

    def test_checked_in_semver_routes_explicit_modes_and_guards_tagging(self) -> None:
        """Pin SemVer mode authority, fresh evidence, and local-tag safety."""
        project_root = Path(__file__).parents[1]
        command_path = project_root / "opencode/commands/semver.md"
        self.assertTrue(command_path.is_file(), "semver.md")
        if not command_path.is_file():
            return

        command_text = command_path.read_text(encoding="utf-8")
        parsed, errors = OpenCodeInstallService._parse_frontmatter(
            "commands", "semver.md", command_text
        )
        self.assertEqual(errors, [])
        assert parsed is not None
        self.assertEqual(parsed.fields["agent"], "engineering-lead")
        self.assertEqual(parsed.fields["subtask"], "false")

        stages = (
            "## Shared evidence rules",
            "## Audit mode",
            "## Apply mode",
            "## Tag mode",
            "## Report",
        )
        positions = tuple(command_text.index(stage) for stage in stages)
        self.assertEqual(positions, tuple(sorted(positions)))

        normalized = " ".join(command_text.split())
        required = (
            "Use exactly one mode per invocation",
            "Load `semantic-versioning` for every valid mode.",
            "Treat any earlier version recommendation as context only",
            "Audit mode is read-only.",
            "When audit scope does not identify a target, inspect the released baseline through `HEAD` and report release-relevant staged and unstaged changes separately.",
            "Apply mode authorizes version-metadata edits and their repository-native validation only.",
            "refuse an under-bump",
            "Do not stage, commit, tag, push, publish, or deploy in apply mode.",
            "Load `git-workflows` before any tag operation.",
            "Tag mode authorizes creation of one local release tag only.",
            "With no version operand in tag mode, use only the single unambiguous canonical version recorded at `HEAD`.",
            "require `git status` to show no staged, unstaged, or untracked paths",
            "the canonical version metadata at `HEAD` equals the target Semantic Version",
            "the target version is not lower than the fresh minimum recommendation",
            "Do not edit version metadata, stage, commit, push, publish, or deploy in tag mode.",
            "Never create, move, replace, delete, or force a pre-existing tag.",
        )
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, normalized)

    def test_checked_in_root_cause_analysis_is_read_only_and_human_gated(self) -> None:
        """Pin RCA, specialist, adversarial, and human-gate sequencing."""
        project_root = Path(__file__).parents[1]
        command_path = project_root / "opencode/commands/root-cause-analysis.md"
        command_text = command_path.read_text(encoding="utf-8")
        parsed, errors = OpenCodeInstallService._parse_frontmatter(
            "commands", "root-cause-analysis.md", command_text
        )
        self.assertEqual(errors, [])
        assert parsed is not None
        self.assertEqual(parsed.fields["agent"], "engineering-review-board")
        self.assertEqual(parsed.fields["subtask"], "false")

        stages = (
            "## 1. Establish the root cause",
            "## 2. Brainstorm the smallest safe repair",
            "## 3. Require adversarial proposal review",
            "## 4. Return the proposal to the human and stop",
        )
        positions = tuple(command_text.index(stage) for stage in stages)
        self.assertEqual(positions, tuple(sorted(positions)))

        normalized = " ".join(command_text.split())
        for required in COMMAND_PROMPT_CONTRACTS["root-cause-analysis.md"]:
            with self.subTest(required=required):
                self.assertIn(required, normalized)

        reviewer = (
            project_root / "opencode/agents/adversarial-reviewer.md"
        ).read_text(encoding="utf-8")
        self.assertLess(
            reviewer.index("## Pre-Implementation Repair Proposal Review"),
            reviewer.index("## Completed-Change Review Method"),
        )
        self.assertIn(
            "**No Material Adversarial Objection Found** means only that no evidence-backed",
            reviewer,
        )
        self.assertIn(
            "For the completed-change stage, review the actual diff or commit, relevant\n"
            "tests, and supplied validation output.",
            reviewer,
        )
        self.assertIn(
            "Return one recommendation: **Do Not Merge / Merge Only After Fixes / Merge With Explicit Follow-ups / Merge**.",
            reviewer,
        )

    def test_checked_in_address_review_reanchors_engineering_lead(self) -> None:
        """Pin the explicit ERB-to-Lead handoff contract in the current command turn."""
        project_root = Path(__file__).parents[1]
        command_path = project_root / "opencode/commands/address-review.md"
        self.assertTrue(command_path.is_file(), "address-review.md")
        if not command_path.is_file():
            return

        command_text = command_path.read_text(encoding="utf-8")
        parsed, errors = OpenCodeInstallService._parse_frontmatter(
            "commands", "address-review.md", command_text
        )
        self.assertEqual(errors, [])
        assert parsed is not None
        self.assertEqual(parsed.fields["agent"], "engineering-lead")
        self.assertEqual(parsed.fields["subtask"], "false")

        normalized = " ".join(command_text.split())
        for required in (
            "You are handling this current command turn as the Engineering Lead.",
            "was authored by a different read-only primary agent and is advisory context only; it does not transfer the Board's identity or permissions to this turn.",
            "re-evaluate each proposed action for scope, safety, correctness, and validation",
            "ask the human to provide or identify them instead of inventing work.",
            "Never claim that the Engineering Review Board is selected while this command is running.",
            "identify the actual authority boundary and route",
            "Durable plan creation remains an explicit `/create-plan` choice, an in-place active-plan amendment remains a separate `/update-plan <exact-plan-path>` choice, and execution remains a separate `/start-plan <existing-plan-path>` choice.",
        ):
            with self.subTest(required=required):
                self.assertIn(required, normalized)

    def test_checked_in_plan_commands_reanchor_plan_orchestrator(self) -> None:
        """Pin explicit same-conversation handoffs to every Plan Orchestrator route."""
        project_root = Path(__file__).parents[1]
        command_root = project_root / "opencode/commands"
        shared = (
            "You are handling this current command turn as the Plan Orchestrator.",
            "was authored by a different primary agent and is context only; it does not transfer their identity or permissions to this turn.",
            "Never claim that the Engineering Review Board or Engineering Lead is selected, and never ask the human to select the Plan Orchestrator while this command is running.",
            "Before refusing on role-authority grounds, reconcile the request against the active Plan Orchestrator contract.",
        )
        route_specific = {
            "consult-plan.md": (
                "This invocation is the human's current request for read-only Plan Orchestrator consultation under the constraints below; it grants no plan, state, or implementation authority.",
            ),
            "create-plan.md": (
                "This invocation is the human's explicit current authorization to create and persist a plan under the constraints below; it grants no execution authority.",
            ),
            "start-plan.md": (
                "This invocation is the human's current request to execute or resume an existing plan under the Plan Orchestrator contract, subject to the path, state, and lifecycle validation below.",
            ),
            "update-plan.md": (
                "This invocation is the human's explicit current authorization to update one existing active plan in place under the constraints below; it grants no execution authority.",
            ),
        }

        for name, required in route_specific.items():
            command_path = command_root / name
            command_text = command_path.read_text(encoding="utf-8")
            parsed, errors = OpenCodeInstallService._parse_frontmatter(
                "commands", name, command_text
            )
            self.assertEqual(errors, [])
            assert parsed is not None
            self.assertEqual(parsed.fields["agent"], "plan-orchestrator")
            self.assertEqual(parsed.fields["subtask"], "false")

            normalized = " ".join(command_text.split())
            for phrase in shared + required:
                with self.subTest(command=name, phrase=phrase):
                    self.assertIn(phrase, normalized)

    def test_checked_in_planned_worker_delegation_closes_partial_work(self) -> None:
        """Require self-contained Worker context and evidence-driven correction."""
        project_root = Path(__file__).parents[1]
        orchestrator = " ".join(
            (project_root / "opencode/agents/plan-orchestrator.md")
            .read_text(encoding="utf-8")
            .split()
        )
        worker = " ".join(
            (project_root / "opencode/agents/implementation-worker.md")
            .read_text(encoding="utf-8")
            .split()
        )
        lead = " ".join(
            (project_root / "opencode/agents/engineering-lead.md")
            .read_text(encoding="utf-8")
            .split()
        )
        start_plan = " ".join(
            (project_root / "opencode/commands/start-plan.md")
            .read_text(encoding="utf-8")
            .split()
        )

        orchestrator_requirements = (
            "Treat every new Task child as context-isolated; its prompt must be self-contained",
            "canonical plan path, current TODO number and exact text",
            "relevant Objectives, Guardrails, Deliverables, and Definition of Done",
            "numbered acceptance criteria",
            "One at a time means one active Worker and one current implementation TODO, not one attempt.",
            "A Worker return is evidence, not a terminal event.",
            "Map every acceptance criterion to fresh source, diff, and validation evidence.",
            "resume the same Worker child session by passing its `task_id`",
            "Do not start a fresh Worker Task for an in-scope correction when that child session can be resumed.",
            "For every resumed correction, send a complete correction packet",
            "numbered evidence gaps",
            "the acceptance criterion each gap blocks",
            "the observed evidence and required result",
            "the exact correction requested",
            "validation to rerun",
            "A status-only preamble or a reference such as `these findings`",
        )
        worker_requirements = (
            "Make the smallest durable change that satisfies every assigned acceptance criterion.",
            "Do not return partial progress while safe, in-scope work remains executable.",
            "Return exactly one status: `COMPLETED` or `BLOCKED`.",
            "requirement-to-evidence table",
            "A resumed correction assignment must enumerate at least one concrete evidence gap",
            "Do not infer missing findings from a status-only preamble",
        )
        command_requirements = (
            "Use the Plan Orchestrator's self-contained delegation and corrective-continuation contract.",
            "A Worker return does not end the current TODO.",
            "Each resumed correction prompt must enumerate the evidence gaps, blocked criteria, required corrections, and validation to rerun.",
        )
        lead_requirements = (
            "When resuming the same Worker for a correction, send a complete actionable packet",
            "enumerate each evidence gap, the acceptance criterion it blocks",
            "Never send only a status preamble or references such as `these findings`",
        )

        for phrase in orchestrator_requirements:
            with self.subTest(agent="plan-orchestrator", phrase=phrase):
                self.assertIn(phrase, orchestrator)
        for phrase in worker_requirements:
            with self.subTest(agent="implementation-worker", phrase=phrase):
                self.assertIn(phrase, worker)
        for phrase in command_requirements:
            with self.subTest(command="start-plan", phrase=phrase):
                self.assertIn(phrase, start_plan)
        for phrase in lead_requirements:
            with self.subTest(agent="engineering-lead", phrase=phrase):
                self.assertIn(phrase, lead)

    def test_checked_in_update_plan_requires_exact_plan_only_authority(self) -> None:
        """Pin active-plan amendment, checkbox reconciliation, and resume separation."""
        project_root = Path(__file__).parents[1]
        command_path = project_root / "opencode/commands/update-plan.md"
        command_text = command_path.read_text(encoding="utf-8")
        normalized = " ".join(command_text.split())

        parsed, errors = OpenCodeInstallService._parse_frontmatter(
            "commands", "update-plan.md", command_text
        )
        self.assertEqual(errors, [])
        assert parsed is not None
        self.assertEqual(parsed.fields["agent"], "plan-orchestrator")
        self.assertEqual(parsed.fields["subtask"], "false")

        for required in (
            "Use syntax `/update-plan <exact-plan-path> [instructions]`",
            "requires one explicit canonical plan path and never infers the target from `.erb/plan-state.json`",
            "Only an active plan with at least one unchecked TODO or Verification checkbox may be updated.",
            "A completed plan remains immutable",
            "Apply the smallest exact-content edit patch",
            "New TODO and Verification entries must be unchecked.",
            "Never change an unchecked checkbox to checked during an update.",
            "Retain a checked item only when its obligation and the surrounding acceptance contract remain materially unchanged and fresh evidence still supports it.",
            "Reset every changed, invalidated, or insufficiently evidenced checked item to unchecked.",
            "Do not write or change `.erb/plan-state.json`.",
            "Do not delegate, implement, validate implementation work, stage, commit, or execute TODOs.",
            "A later explicit `/start-plan <existing-plan-path>` request is required to execute or resume the updated plan.",
        ):
            with self.subTest(required=required):
                self.assertIn(required, normalized)

    def test_checked_in_primary_agents_support_same_conversation_handoffs(self) -> None:
        """Keep primary-agent authority turn-scoped without transferring permissions."""
        project_root = Path(__file__).parents[1]
        agent_root = project_root / "opencode/agents"

        shared = (
            "Authority follows the primary agent selected for the current user turn.",
            "Earlier assistant turns from another primary agent are attributed context, not this agent's identity or permission boundary.",
            '"Top-level" means selected as a primary agent rather than invoked through Task; it does not require a new conversation.',
        )
        role_specific = {
            "engineering-lead.md": (
                "When the human explicitly asks the selected Lead to implement earlier ERB advice, proceed in the same conversation under this Lead contract after re-evaluating scope, safety, and validation.",
                "While this Engineering Lead prompt is active, never tell the human to select the Engineering Lead or claim that the Engineering Review Board is selected.",
                "If a requested operation is outside this Lead's authority, identify the actual authority boundary and route without misidentifying this turn's selected primary agent.",
            ),
            "engineering-review-board.md": (
                "The Board remains read-only for its current turn and must not describe the entire conversation as read-only.",
                "The human may select the Engineering Lead in the same conversation and explicitly request implementation; that later Lead turn uses the Lead's authority.",
            ),
            "plan-orchestrator.md": (
                "A same-conversation switch does not carry forward or satisfy a prior request, approval, or state-writing authority.",
                "Apply every current-request and lifecycle gate below before mutation.",
                "While this Plan Orchestrator prompt is active, never tell the human to select the Plan Orchestrator or claim that the Engineering Review Board or Engineering Lead is selected.",
                "Before refusing on role-authority grounds, reconcile the request against this active Plan Orchestrator contract.",
                "If the operation remains outside scope, identify the actual authority boundary and route without misidentifying this turn's selected primary agent.",
            ),
        }

        for name, required in role_specific.items():
            prompt = (agent_root / name).read_text(encoding="utf-8")
            section = OpenCodeInstallService._single_markdown_section(
                prompt, "## Primary-Agent Turn Boundary"
            )
            self.assertIsNotNone(section, name)
            assert section is not None
            for phrase in shared + required:
                with self.subTest(agent=name, phrase=phrase):
                    self.assertIn(phrase, section)

        lead = (agent_root / "engineering-lead.md").read_text(encoding="utf-8")
        governance = (
            project_root / "docs/engineering-agent-governance.md"
        ).read_text(encoding="utf-8")
        for obsolete in (
            "top-level ERB session",
            "as a top-level session",
            "separate ERB session",
        ):
            with self.subTest(obsolete=obsolete):
                self.assertNotIn(obsolete, lead + governance)








    def test_checked_in_human_controlled_lifecycle_docs_fail_closed(self) -> None:
        """Require lifecycle guidance and reject stale automatic `/start-plan` creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_canonical_active_workflow_repo(root)

            self.assertTrue(OpenCodeInstallService(repo, root / "config").validate().ok)

            def remove_token(text: str, token: str) -> str:
                pattern = re.escape(token).replace(r"\ ", r"\s+")
                changed, count = re.subn(pattern, "contract removed", text)
                self.assertGreaterEqual(count, 1, token)
                return changed

            for relative_path, tokens in HUMAN_CONTROLLED_LIFECYCLE_DOC_TOKENS.items():
                document = repo / relative_path
                original = document.read_text(encoding="utf-8")
                for token in tokens:
                    with self.subTest(document=relative_path, token=token):
                        mirror_path = None
                        mirror_original = None
                        if relative_path == "docs/implementation-plans/README.md":
                            mirror_path = (
                                repo
                                / "opencode/project-template/docs/implementation-plans/README.md"
                            )
                        elif relative_path == (
                            "opencode/project-template/docs/implementation-plans/README.md"
                        ):
                            mirror_path = repo / "docs/implementation-plans/README.md"
                        if mirror_path is not None:
                            mirror_original = mirror_path.read_text(encoding="utf-8")
                            mirror_path.write_text(
                                remove_token(mirror_original, token),
                                encoding="utf-8",
                            )
                        document.write_text(remove_token(original, token), encoding="utf-8")

                        result = OpenCodeInstallService(repo, root / "config").validate()

                        self.assertIn(
                            f"human-controlled lifecycle document '{relative_path}' contract is incomplete",
                            result.errors,
                        )
                        if mirror_path is not None and mirror_original is not None:
                            mirror_path.write_text(mirror_original, encoding="utf-8")
                document.write_text(original, encoding="utf-8")

            document = repo / "docs" / "cross-reference-map.md"
            original = document.read_text(encoding="utf-8")
            document.write_text(
                original + "\nComplexity automatically creates a plan through `/start-plan`.\n",
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertIn(
                "human-controlled lifecycle document 'docs/cross-reference-map.md' contains forbidden automatic `/start-plan` creation",
                result.errors,
            )

    def test_checked_in_plan_consultation_is_top_level_and_non_mutating(self) -> None:
        """Protect top-level Plan Orchestrator consultation and forbid Task routing."""
        project_root = Path(__file__).parents[1]
        manifest = json.loads((project_root / "opencode/manifest.json").read_text(encoding="utf-8"))
        self.assertNotIn("plan-consultant.md", manifest["agents"])
        self.assertIn("consult-plan.md", manifest["commands"])
        self.assertFalse((project_root / "opencode/agents/plan-consultant.md").exists())

        agent_root = project_root / "opencode/agents"

        def parse_agent(name: str):
            path = agent_root / name
            self.assertTrue(path.is_file(), name)
            parsed, errors = OpenCodeInstallService._parse_frontmatter(
                "agents", name, path.read_text(encoding="utf-8")
            )
            self.assertEqual(errors, [])
            assert parsed is not None
            return parsed

        for name in ("engineering-lead.md", "engineering-review-board.md"):
            parent = parse_agent(name)
            rules = parent.permissions["task"]
            self.assertIsInstance(rules, tuple)
            assert isinstance(rules, tuple)
            self.assertNotIn(("plan-consultant", "allow"), rules)
            self.assertNotIn(("plan-orchestrator", "allow"), rules)

        orchestrator = parse_agent("plan-orchestrator.md")
        self.assertEqual(orchestrator.fields["mode"], "primary")
        for permission in ("read", "glob", "grep", "list", "lsp"):
            rules = orchestrator.permissions[permission]
            self.assertIsInstance(rules, tuple)
            assert isinstance(rules, tuple)
            self.assertEqual(
                resolve_opencode_action(rules, ".erb/plan-state.json", baseline="deny"),
                "allow",
            )

        command_path = project_root / "opencode/commands/consult-plan.md"
        parsed, errors = OpenCodeInstallService._parse_frontmatter(
            "commands", "consult-plan.md", command_path.read_text(encoding="utf-8")
        )
        self.assertEqual(errors, [])
        assert parsed is not None
        self.assertEqual(parsed.fields["agent"], "plan-orchestrator")
        self.assertEqual(parsed.fields["subtask"], "false")
        normalized = re.sub(r"\s+", " ", command_path.read_text(encoding="utf-8")).strip()
        for required in (
            "top-level read-only Plan Orchestrator consultation",
            "must not create or mutate a plan or state",
            "must not read `.erb/plan-state.json`",
            "must not delegate implementation, implement, stage, or commit",
            "The human controls whether to proceed directly, create or update a plan, or decline the recommendation.",
        ):
            self.assertIn(required, normalized)

        self.assertTrue(
            OpenCodeInstallService(project_root, project_root / "test-config").validate().ok
        )

    def test_checked_in_command_contract_validator_rejects_route_drift(self) -> None:
        """Exercise only checked-in prompt contracts, not agent execution or UI behavior."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_canonical_active_workflow_repo(root)

            self.assertTrue(OpenCodeInstallService(repo, root / "config").validate().ok)

            def remove_token(text: str, token: str) -> str:
                pattern = re.escape(token).replace(r"\ ", r"\s+")
                changed, count = re.subn(pattern, "contract removed", text)
                self.assertGreaterEqual(count, 1, token)
                return changed

            for name, tokens in COMMAND_PROMPT_CONTRACTS.items():
                command = repo / "opencode/commands" / name
                original = command.read_text(encoding="utf-8")
                for token in tokens:
                    with self.subTest(command=name, token=token):
                        command.write_text(remove_token(original, token), encoding="utf-8")
                        result = OpenCodeInstallService(repo, root / "config").validate()
                        self.assertTrue(
                            any(f"{name}' prompt contract is incomplete" in error for error in result.errors),
                            result.errors,
                        )
                command.write_text(original, encoding="utf-8")

            agent_tokens = {
                name: semantics
                for name, (_, semantics) in CANONICAL_PROMPT_SECTION_CONTRACTS.items()
            } | {
                "engineering-lead.md": (
                    "Use only `implementation-worker` for bounded implementation Tasks.",
                    "When resuming the same Worker for a correction, send a complete actionable packet",
                    "enumerate each evidence gap, the acceptance criterion it blocks",
                    "Never send only a status preamble or references such as `these findings`",
                ),
                "plan-orchestrator.md": (
                    "The lifecycle distinguishes read-only consultation, explicit plan-only creation, explicit active-plan updates, and execution.",
                    "It must not execute newly created or updated plans automatically.",
                    "`.erb/plan-state.json`",
                    "Active means at least one unchecked TODO or Verification checkbox remains.",
                    "The current step is the first unchecked checkbox in document order.",
                    "This plan has already been implemented.",
                    "An explicit valid path replaces missing, invalid, or stale state.",
                    "Never block because another plan is selected or may be running.",
                    "Before every mutable phase, freshly reload the selected plan, checkbox state, and worktree evidence; never rely on stale evidence.",
                    "or equally explicit current top-level human plan-creation or plan-replacement request",
                    "`/update-plan <exact-plan-path>` is explicit plan-only authority",
                    "Completed plans remain immutable.",
                    "must complete every planned TODO before beginning any dedicated Verification step",
                    "must not add, remove, rewrite, reorder, or renumber plan content",
                    "Treat every new Task child as context-isolated; its prompt must be self-contained",
                    "canonical plan path, current TODO number and exact text",
                    "relevant Objectives, Guardrails, Deliverables, and Definition of Done",
                    "numbered acceptance criteria",
                    "One at a time means one active Worker and one current implementation TODO, not one attempt.",
                    "A Worker return is evidence, not a terminal event.",
                    "Map every acceptance criterion to fresh source, diff, and validation evidence.",
                    "resume the same Worker child session by passing its `task_id`",
                    "Do not start a fresh Worker Task for an in-scope correction when that child session can be resumed.",
                    "For every resumed correction, send a complete correction packet",
                    "numbered evidence gaps",
                    "the acceptance criterion each gap blocks",
                    "the observed evidence and required result",
                    "the exact correction requested",
                    "validation to rerun",
                    "A status-only preamble or a reference such as `these findings`",
                ),
                "implementation-worker.md": (
                    "Make the smallest durable change that satisfies every assigned acceptance criterion.",
                    "Do not return partial progress while safe, in-scope work remains executable.",
                    "Return exactly one status: `COMPLETED` or `BLOCKED`.",
                    "requirement-to-evidence table",
                    "A resumed correction assignment must enumerate at least one concrete evidence gap",
                    "Do not infer missing findings from a status-only preamble",
                ),
            }
            for name, tokens in agent_tokens.items():
                agent = repo / "opencode/agents" / name
                original = agent.read_text(encoding="utf-8")
                for token in tokens:
                    with self.subTest(agent=name, token=token):
                        agent.write_text(remove_token(original, token), encoding="utf-8")
                        result = OpenCodeInstallService(repo, root / "config").validate()
                        self.assertTrue(
                            any(f"agents: '{name}' prompt contract is incomplete" in error for error in result.errors),
                            result.errors,
                        )
                agent.write_text(original, encoding="utf-8")

            automatic_route_mutations = {
                "opencode/agents/engineering-lead.md": (
                    "Complex work automatically creates a plan.",
                    "agents: 'engineering-lead.md' contains forbidden automatic plan routing",
                ),
                "opencode/agents/engineering-lead.md::stale-direct-only": (
                    "Proceed directly only for local, obvious, low-risk work.",
                    "agents: 'engineering-lead.md' contains forbidden automatic plan routing",
                ),
                "opencode/agents/engineering-lead.md::stale-durable-planning": (
                    "Use durable planning for cross-cutting work.",
                    "agents: 'engineering-lead.md' contains forbidden automatic plan routing",
                ),
            }
            for relative_path, (mutation, expected_error) in automatic_route_mutations.items():
                with self.subTest(route=relative_path, mutation=mutation):
                    target = repo / relative_path.split("::", 1)[0]
                    original = target.read_text(encoding="utf-8")
                    target.write_text(original + f"\n{mutation}\n", encoding="utf-8")

                    result = OpenCodeInstallService(repo, root / "config").validate()

                    self.assertFalse(result.ok)
                    self.assertIn(expected_error, result.errors)
                    target.write_text(original, encoding="utf-8")

            retained_routes = {
                "commands/audit-technical-debt.md": {
                    "required": (
                        "Return findings for direct Lead remediation when safe.",
                        "When the human wants a durable remediation initiative, recommend top-level `/create-plan`;",
                        "`/start-plan <existing-plan-path>` is only a separate human-chosen execution of an existing plan.",
                    ),
                    "forbidden": (
                        "Recommend top-level `/start-plan` for a remediation initiative.",
                        "/prepare-work",
                    ),
                    "sentinel": "Treat the argument as either repository-wide scope",
                },
                "commands/investigate-regression.md": {
                    "required": (
                        "Return repair guidance for direct Lead implementation when safe.",
                        "When the human wants durable repair planning, recommend top-level `/create-plan`;",
                        "`/start-plan <existing-plan-path>` is only a separate human-chosen execution of an existing plan.",
                    ),
                    "forbidden": (
                        "return it to top-level `/start-plan`.",
                        "/revise-plan",
                        "Planning Coordinator",
                    ),
                    "sentinel": "Establish expected behavior, observed behavior",
                },
                "cleanup/weave-cleanup-checklist.md": {
                    "required": (
                        "top-level Plan Orchestrator for durable plan writes.",
                        "plan creation has explicit human authorization and uses `/create-plan`;",
                        "`/start-plan <existing-plan-path>` is only the separate human-chosen execution route.",
                        "primary Plan Orchestrator alone owns plan and plan-state mutations.",
                        "ERB advice is non-gating.",
                    ),
                    "forbidden": ("/normalize-plan", "Planning Coordinator"),
                    "sentinel": "Use this after native OpenCode agents and commands are installed. Keep legacy",
                },
            }
            for relative_path, contract in retained_routes.items():
                route = repo / "opencode" / relative_path
                original = route.read_text(encoding="utf-8")
                sentinel = contract["sentinel"]
                self.assertIn(sentinel, original)
                sentinel_paragraph = next(
                    paragraph
                    for paragraph in original.split("\n\n")
                    if sentinel in paragraph
                )
                for forbidden in contract["forbidden"]:
                    with self.subTest(route=relative_path, forbidden=forbidden):
                        route.write_text(original + f"\n{forbidden}\n", encoding="utf-8")
                        result = OpenCodeInstallService(repo, root / "config").validate()
                        self.assertTrue(
                            any("contains obsolete lifecycle routing" in error for error in result.errors),
                            result.errors,
                        )
                        self.assertIn(sentinel_paragraph, route.read_text(encoding="utf-8"))
                for required in contract["required"]:
                    with self.subTest(route=relative_path, required=required):
                        route.write_text(remove_token(original, required), encoding="utf-8")
                        result = OpenCodeInstallService(repo, root / "config").validate()
                        self.assertTrue(
                            any("retained route" in error and "contract is incomplete" in error for error in result.errors),
                            result.errors,
                        )
                        self.assertIn(sentinel_paragraph, route.read_text(encoding="utf-8"))
                route.write_text(original, encoding="utf-8")

            review = repo / "opencode/commands/review-plan.md"
            review.write_text(
                review.read_text(encoding="utf-8").replace(
                    "agent: engineering-review-board",
                    "agent: plan-orchestrator",
                ),
                encoding="utf-8",
            )
            result = OpenCodeInstallService(repo, root / "config").validate()
            self.assertTrue(
                any("review-plan.md' must use canonical primary owner" in error for error in result.errors),
                result.errors,
            )


class CanonicalPromptSectionTests(unittest.TestCase):
    def test_validate_rejects_mcp_selection_prompt_contract_drift(self) -> None:
        for name, (heading, semantics) in MCP_SELECTION_PROMPT_CONTRACTS.items():
            for semantic in semantics:
                with self.subTest(agent=name, semantic=semantic), tempfile.TemporaryDirectory() as temp_dir:
                    root = Path(temp_dir)
                    repo = create_canonical_active_workflow_repo(root)
                    definition = repo / "opencode" / "agents" / name
                    original = definition.read_text(encoding="utf-8")
                    self.assertEqual(
                        1,
                        sum(line.strip() == heading for line in original.splitlines()),
                    )
                    pattern = re.escape(semantic).replace(r"\ ", r"\s+")
                    mutated, count = re.subn(
                        pattern,
                        "SYNTHETIC_MCP_SELECTION_CONTRACT_MARKER",
                        original,
                        count=1,
                    )
                    self.assertEqual(1, count, semantic)
                    definition.write_text(mutated, encoding="utf-8")

                    result = OpenCodeInstallService(repo, root / "config").validate()

                    self.assertFalse(result.ok)
                    self.assertTrue(
                        any(
                            f"agents: '{name}' MCP-selection prompt contract is incomplete"
                            in error
                            for error in result.errors
                        ),
                        result.errors,
                    )

    def test_validate_rejects_adversarial_stage_prompt_contract_drift(self) -> None:
        for name, stage_contracts in ADVERSARIAL_REVIEWER_STAGE_PROMPT_CONTRACTS.items():
            for heading, semantics in stage_contracts:
                for semantic in semantics:
                    with self.subTest(
                        agent=name, heading=heading, semantic=semantic
                    ), tempfile.TemporaryDirectory() as temp_dir:
                        root = Path(temp_dir)
                        repo = create_canonical_active_workflow_repo(root)
                        definition = repo / "opencode" / "agents" / name
                        original = definition.read_text(encoding="utf-8")
                        self.assertEqual(
                            1,
                            sum(
                                line.strip() == heading
                                for line in original.splitlines()
                            ),
                        )
                        pattern = re.escape(semantic).replace(r"\ ", r"\s+")
                        mutated, count = re.subn(
                            pattern,
                            "SYNTHETIC_ADVERSARIAL_STAGE_CONTRACT_MARKER",
                            original,
                            count=1,
                        )
                        self.assertEqual(1, count, semantic)
                        definition.write_text(mutated, encoding="utf-8")

                        result = OpenCodeInstallService(
                            repo, root / "config"
                        ).validate()

                        self.assertFalse(result.ok)
                        self.assertTrue(
                            any(
                                f"agents: '{name}' adversarial stage prompt contract is incomplete"
                                in error
                                for error in result.errors
                            ),
                            result.errors,
                        )

    def test_validate_rejects_code_documentation_prompt_contract_drift(self) -> None:
        for name, (heading, semantics) in CODE_DOCUMENTATION_PROMPT_CONTRACTS.items():
            for semantic in semantics:
                with self.subTest(agent=name, semantic=semantic), tempfile.TemporaryDirectory() as temp_dir:
                    root = Path(temp_dir)
                    repo = create_canonical_active_workflow_repo(root)
                    definition = repo / "opencode" / "agents" / name
                    original = definition.read_text(encoding="utf-8")
                    self.assertEqual(
                        1,
                        sum(line.strip() == heading for line in original.splitlines()),
                    )
                    self.assertIn(semantic, " ".join(original.split()))
                    pattern = re.escape(semantic).replace(r"\ ", r"\s+")
                    mutated, count = re.subn(
                        pattern,
                        "SYNTHETIC_STATIC_CONTRACT_MARKER",
                        original,
                        count=1,
                    )
                    self.assertEqual(1, count, semantic)
                    definition.write_text(
                        mutated,
                        encoding="utf-8",
                    )

                    result = OpenCodeInstallService(repo, root / "config").validate()

                    self.assertFalse(result.ok)
                    self.assertTrue(
                        any(
                            f"agents: '{name}' code-documentation prompt contract is incomplete"
                            in error
                            for error in result.errors
                        ),
                        result.errors,
                    )

    def test_checked_in_lead_and_board_canonical_sections_are_unique_and_consolidated(self) -> None:
        project_root = Path(__file__).parents[1]
        removed_restatements = {
            "engineering-lead.md": (
                "Do not author or delegate durable plan/state work.",
                "Recommend `/create-plan` when a human wants durable",
                "Do not use Task as a substitute for the top-level `/start-plan` boundary.",
            ),
            "engineering-review-board.md": (
                "## Operating Rules",
                "## Runtime Selection and Failure Recovery",
                "Each Task must set `subagent_type` to the exact registered ID.",
            ),
        }

        for name, (heading, _) in CANONICAL_PROMPT_SECTION_CONTRACTS.items():
            with self.subTest(agent=name):
                prompt = (project_root / "opencode" / "agents" / name).read_text(encoding="utf-8")
                self.assertEqual(1, sum(line.strip() == heading for line in prompt.splitlines()))
                for phrase in removed_restatements[name]:
                    self.assertNotIn(phrase, prompt)

    def test_checked_in_board_plan_reviews_match_closed_lean_contract(self) -> None:
        project_root = Path(__file__).parents[1]
        prompt = (
            project_root / "opencode/agents/engineering-review-board.md"
        ).read_text(encoding="utf-8")
        section = OpenCodeInstallService._single_markdown_section(
            prompt, "## Plan Reviews"
        )

        self.assertIsNotNone(section)
        assert section is not None
        for required in (
            "contained canonical path and layout",
            "canonical template's exact title and ordered headings",
            "fixed Context labels and numbered TODO and Verification checklist grammar",
            "Do not require frontmatter, lifecycle status, revision, dependency fields, history, provenance, approvals, review records, or an `Open Decisions` section.",
            "Do not infer dependencies from filename order.",
        ):
            with self.subTest(required=required):
                self.assertIn(required, section)
        for stale_requirement in (
            "verify canonical path and identity, status, revision",
            "`depends_on` remains authoritative",
        ):
            with self.subTest(stale_requirement=stale_requirement):
                self.assertNotIn(stale_requirement, section)

    def test_validate_rejects_board_plan_review_contract_drift(self) -> None:
        mutations = (
            (
                "missing lean review criterion",
                "contained canonical path and layout",
                "synthetic removed criterion",
            ),
            (
                "restored legacy dependency field",
                "Do not infer",
                "`depends_on` remains authoritative; do not infer",
            ),
        )
        for label, old, new in mutations:
            with self.subTest(mutation=label), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_canonical_active_workflow_repo(root)
                definition = repo / "opencode/agents/engineering-review-board.md"
                prompt = definition.read_text(encoding="utf-8")
                self.assertIn(old, prompt)
                definition.write_text(prompt.replace(old, new, 1), encoding="utf-8")

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(
                    any("Board plan-review prompt contract" in error for error in result.errors),
                    result.errors,
                )

    def test_validate_requires_unique_canonical_prompt_sections(self) -> None:
        for name, (heading, semantics) in CANONICAL_PROMPT_SECTION_CONTRACTS.items():
            with self.subTest(agent=name, mutation="section-locality"), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_canonical_active_workflow_repo(root)
                definition = repo / "opencode" / "agents" / name
                original = definition.read_text(encoding="utf-8")
                pattern = re.escape(semantics[0]).replace(r"\ ", r"\s+")
                mutated, count = re.subn(
                    pattern,
                    "SYNTHETIC_STATIC_CONTRACT_MARKER",
                    original,
                    count=1,
                )
                self.assertEqual(1, count, semantics[0])
                definition.write_text(
                    mutated
                    + f"\n## Unrelated Section\n\n{semantics[0]}\n",
                    encoding="utf-8",
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(
                    any(f"agents: '{name}' prompt contract is incomplete" in error for error in result.errors),
                    result.errors,
                )

            with self.subTest(agent=name, mutation="duplicate-heading"), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_canonical_active_workflow_repo(root)
                definition = repo / "opencode" / "agents" / name
                definition.write_text(
                    definition.read_text(encoding="utf-8") + f"\n{heading}\n",
                    encoding="utf-8",
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(
                    any(f"agents: '{name}' prompt contract is incomplete" in error for error in result.errors),
                    result.errors,
                )

    def test_validate_requires_unique_primary_agent_turn_sections(self) -> None:
        for name, (heading, semantics) in PRIMARY_AGENT_TURN_PROMPT_CONTRACTS.items():
            with self.subTest(agent=name, mutation="section-locality"), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_canonical_active_workflow_repo(root)
                definition = repo / "opencode" / "agents" / name
                original = definition.read_text(encoding="utf-8")
                pattern = re.escape(semantics[0]).replace(r"\ ", r"\s+")
                mutated, count = re.subn(
                    pattern,
                    "SYNTHETIC_PRIMARY_TURN_CONTRACT_MARKER",
                    original,
                    count=1,
                )
                self.assertEqual(1, count, semantics[0])
                definition.write_text(
                    mutated + f"\n## Unrelated Section\n\n{semantics[0]}\n",
                    encoding="utf-8",
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(
                    any(
                        f"agents: '{name}' primary-agent turn prompt contract is incomplete"
                        in error
                        for error in result.errors
                    ),
                    result.errors,
                )

            with self.subTest(agent=name, mutation="duplicate-heading"), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_canonical_active_workflow_repo(root)
                definition = repo / "opencode" / "agents" / name
                definition.write_text(
                    definition.read_text(encoding="utf-8") + f"\n{heading}\n",
                    encoding="utf-8",
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(
                    any(
                        f"agents: '{name}' primary-agent turn prompt contract is incomplete"
                        in error
                        for error in result.errors
                    ),
                    result.errors,
                )


class CanonicalAgentTopologyTests(unittest.TestCase):
    def test_standard_critic_membership_is_derived_from_topology(self) -> None:
        review_specialists = {
            policy.agent_id
            for policy in CANONICAL_AGENT_TOPOLOGY.agents
            if policy.permission_profile == "review-specialist"
        }

        self.assertTrue(STANDARD_CRITIC_STAGE_REVIEWER_IDS <= review_specialists)
        self.assertEqual(
            review_specialists - STANDARD_CRITIC_STAGE_REVIEWER_IDS,
            STANDARD_CRITIC_AGENT_IDS,
        )
        self.assertEqual(15, len(STANDARD_CRITIC_AGENT_IDS))

    def test_checked_in_standard_critics_preserve_common_prompt_contract(self) -> None:
        project_root = Path(__file__).parents[1]

        for agent_id in STANDARD_CRITIC_AGENT_IDS:
            with self.subTest(agent_id=agent_id):
                prompt = (
                    project_root / "opencode" / "agents" / f"{agent_id}.md"
                ).read_text(encoding="utf-8")
                normalized = " ".join(prompt.split())
                for heading in STANDARD_CRITIC_REQUIRED_HEADINGS:
                    self.assertIn(heading, prompt)
                for semantic in STANDARD_CRITIC_REQUIRED_SEMANTICS:
                    self.assertIn(semantic, normalized)

    def test_checked_in_code_documentation_route_is_source_scoped(self) -> None:
        project_root = Path(__file__).parents[1]
        critic_path = project_root / "opencode/agents/documentation-critic.md"
        lead_path = project_root / "opencode/agents/engineering-lead.md"
        board_path = project_root / "opencode/agents/engineering-review-board.md"
        skill_path = project_root / "skills/documentation-engineering/SKILL.md"

        critic = " ".join(critic_path.read_text(encoding="utf-8").split())
        lead = " ".join(lead_path.read_text(encoding="utf-8").split())
        board = " ".join(board_path.read_text(encoding="utf-8").split())
        skill = " ".join(skill_path.read_text(encoding="utf-8").split())

        for required in (
            "code comments",
            "docstrings",
            "Rustdoc",
            "pydoc",
            "Javadoc",
            "JSDoc/TSDoc",
            "perldoc/POD",
            "documentation tests",
            "standalone Markdown files are evidence only",
            "missing documentation",
            "human readers",
            "AI-sounding filler",
            "`documentation-engineering`",
            "`testing-critic`",
            "`technical-debt-auditor`",
        ):
            with self.subTest(critic=required):
                self.assertIn(required, critic)

        for required in (
            "## Code Documentation Work",
            "audit-only code-documentation request",
            "`documentation-critic`",
            "requested source edits remain implementation work",
            "`implementation-worker`",
            "standalone Markdown files remain outside scope",
            "repository-native documentation checks",
        ):
            with self.subTest(lead=required):
                self.assertIn(required, lead)

        self.assertIn(
            "`documentation-critic` (repository and in-code documentation)",
            board,
        )

        for required in (
            "Javadoc",
            "JSDoc/TSDoc",
            "perldoc/POD",
            "repository's existing documentation toolchain",
            "`cargo test --doc`",
            "`podchecker`",
            "prefer an embedded documentation test maintained beside the API",
            "Do not add comments merely to increase documentation coverage",
        ):
            with self.subTest(skill=required):
                self.assertIn(required, skill)

    def test_validate_rejects_standard_critic_common_contract_drift(self) -> None:
        mutations = (
            ("heading", "## Output", "## Response"),
            ("semantic", "Repository evidence first", "Synthetic evidence order"),
        )
        for label, old, new in mutations:
            with self.subTest(mutation=label), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_canonical_active_workflow_repo(root)
                definition = repo / "opencode" / "agents" / "accessibility-critic.md"
                prompt = definition.read_text(encoding="utf-8")
                self.assertIn(old, prompt)
                definition.write_text(prompt.replace(old, new, 1), encoding="utf-8")

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(
                    any("standard critic prompt contract" in error for error in result.errors),
                    result.errors,
                )

    def test_checked_in_agents_contain_sanitized_evidence_contracts(self) -> None:
        """Static prompt-contract validation only; it does not prove runtime model redaction."""
        project_root = Path(__file__).parents[1]

        for policy in CANONICAL_AGENT_TOPOLOGY.agents:
            with self.subTest(agent_id=policy.agent_id):
                prompt = (
                    project_root / "opencode" / "agents" / f"{policy.agent_id}.md"
                ).read_text(encoding="utf-8")
                self.assertEqual(
                    1,
                    " ".join(prompt.split()).count(SANITIZED_EVIDENCE_INVARIANT),
                )
                self.assertEqual(
                    1 if policy.agent_id in EXTERNAL_DIRECTORY_ASK_AGENT_IDS else 0,
                    " ".join(prompt.split()).count(EXTERNAL_DIRECTORY_SCOPE_INVARIANT),
                )

        researcher_prompt = (
            project_root / "opencode" / "agents" / "technical-researcher.md"
        ).read_text(encoding="utf-8")
        self.assertEqual(
            1,
            " ".join(researcher_prompt.split()).count(
                TECHNICAL_RESEARCHER_EXTERNAL_EGRESS_INVARIANT
            ),
        )

    def test_validate_rejects_missing_sanitized_evidence_contract_per_profile(self) -> None:
        """Static prompt-contract validation only; it does not prove runtime model redaction."""
        representatives = {
            "engineering-lead": "engineering-lead.md",
            "engineering-review-board": "engineering-review-board.md",
            "implementation-worker": "implementation-worker.md",
            "plan-orchestrator": "plan-orchestrator.md",
            "technical-researcher": "technical-researcher.md",
            "review-specialist": "accessibility-critic.md",
        }
        for profile, name in representatives.items():
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_canonical_active_workflow_repo(root)
                definition = repo / "opencode" / "agents" / name
                prompt = definition.read_text(encoding="utf-8")
                definition.write_text(
                    prompt.replace(
                        SANITIZED_EVIDENCE_INVARIANT,
                        "SYNTHETIC_STATIC_CONTRACT_MARKER",
                        1,
                    ),
                    encoding="utf-8",
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(
                    any("sanitized-evidence prompt contract" in error for error in result.errors),
                    result.errors,
                )

    def test_validate_rejects_missing_external_directory_contract_per_ask_profile(self) -> None:
        """Static prompt-contract validation only; runtime approval remains OpenCode-owned."""
        representatives = {
            "engineering-lead": "engineering-lead.md",
            "engineering-review-board": "engineering-review-board.md",
            "implementation-worker": "implementation-worker.md",
            "technical-researcher": "technical-researcher.md",
            "review-specialist": "accessibility-critic.md",
        }
        for profile, name in representatives.items():
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_canonical_active_workflow_repo(root)
                definition = repo / "opencode" / "agents" / name
                prompt = definition.read_text(encoding="utf-8")
                definition.write_text(
                    prompt.replace(
                        "For external-path work",
                        "SYNTHETIC_STATIC_CONTRACT_MARKER",
                        1,
                    ),
                    encoding="utf-8",
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(
                    any("external-directory prompt contract" in error for error in result.errors),
                    result.errors,
                )

    def test_validate_rejects_missing_researcher_external_egress_contract(self) -> None:
        """Static prompt-contract validation only; it does not prove runtime model redaction."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_canonical_active_workflow_repo(root)
            researcher = repo / "opencode" / "agents" / "technical-researcher.md"
            researcher.write_text(
                researcher.read_text(encoding="utf-8").replace(
                    TECHNICAL_RESEARCHER_EXTERNAL_EGRESS_INVARIANT,
                    "SYNTHETIC_STATIC_CONTRACT_MARKER",
                    1,
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertTrue(
                any("external-egress prompt contract" in error for error in result.errors),
                result.errors,
            )

    def test_checked_in_agent_identities_modes_task_edges_and_command_owners_match_topology(self) -> None:
        project_root = Path(__file__).parents[1]
        service = OpenCodeInstallService(project_root, project_root / "config")
        inventory, errors = service._load_inventory()

        self.assertEqual([], errors)
        assert inventory is not None
        self.assertEqual(CANONICAL_AGENT_TOPOLOGY.agent_filenames, inventory.agents)
        self.assertEqual(CANONICAL_AGENT_TOPOLOGY.command_filenames, inventory.commands)
        self.assertEqual(23, len(CANONICAL_AGENT_TOPOLOGY.agents))

        metadata = service._agent_metadata(inventory)
        expected_agents = {
            policy.agent_id: (policy.mode, policy.task_targets)
            for policy in CANONICAL_AGENT_TOPOLOGY.agents
        }
        self.assertEqual(
            expected_agents,
            {
                agent_id: (
                    mode,
                    tuple(target for target, _ in task_rules if target != "*"),
                )
                for agent_id, (mode, task_rules) in metadata.items()
            },
        )
        self.assertEqual(
            {
                "engineering-lead": "engineering-lead",
                "engineering-review-board": "engineering-review-board",
                "plan-orchestrator": "plan-orchestrator",
                "implementation-worker": "implementation-worker",
                "technical-researcher": "technical-researcher",
            },
            {
                policy.agent_id: policy.permission_profile
                for policy in CANONICAL_AGENT_TOPOLOGY.agents
                if policy.permission_profile != "review-specialist"
            },
        )

        command_owners = {}
        for name in inventory.commands:
            parsed, parse_errors = service._parse_frontmatter(
                "commands",
                name,
                (project_root / "opencode" / "commands" / name).read_text(encoding="utf-8"),
            )
            self.assertEqual([], parse_errors)
            assert parsed is not None
            command_owners[name] = parsed.fields["agent"]
        self.assertEqual(CANONICAL_AGENT_TOPOLOGY.command_owners, command_owners)

    def test_validate_fails_closed_for_canonical_agent_identity_drift(self) -> None:
        mutations = ("add", "remove", "rename")
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_canonical_active_workflow_repo(root)
                manifest_path = repo / "opencode" / "manifest.json"
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

                if mutation == "add":
                    name = "substitute-critic.md"
                    manifest["agents"].append(name)
                    manifest["agents"].sort()
                    shutil.copy2(
                        repo / "opencode" / "agents" / "accessibility-critic.md",
                        repo / "opencode" / "agents" / name,
                    )
                else:
                    original = "accessibility-critic.md"
                    if mutation == "remove":
                        manifest["agents"].remove(original)
                        (repo / "opencode" / "agents" / original).unlink()
                    else:
                        replacement = "accessibility-reviewer.md"
                        manifest["agents"].remove(original)
                        manifest["agents"].append(replacement)
                        manifest["agents"].sort()
                        (repo / "opencode" / "agents" / original).rename(
                            repo / "opencode" / "agents" / replacement
                        )

                manifest_path.write_text(
                    json.dumps(manifest, indent=2) + "\n",
                    encoding="utf-8",
                )
                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(
                    any("canonical active workflow agent topology" in error for error in result.errors),
                    result.errors,
                )

    def test_validate_rejects_canonical_mode_and_task_graph_drift(self) -> None:
        mutations = (
            (
                "mode flip",
                "opencode/agents/accessibility-critic.md",
                "mode: subagent",
                "mode: primary",
                "canonical mode",
            ),
            (
                "removed Lead edge",
                "opencode/agents/engineering-lead.md",
                '    "implementation-worker": allow\n',
                "",
                "canonical Task graph",
            ),
            (
                "added Lead edge",
                "opencode/agents/engineering-lead.md",
                '    "prompt-critic": allow\n',
                '    "prompt-critic": allow\n    "release-readiness-reviewer": allow\n',
                "canonical Task graph",
            ),
            (
                "removed ERB edge",
                "opencode/agents/engineering-review-board.md",
                '    "design-critic": allow\n',
                "",
                "canonical Task graph",
            ),
            (
                "ERB-to-Worker edge",
                "opencode/agents/engineering-review-board.md",
                '    "technical-researcher": allow\n',
                '    "technical-researcher": allow\n    "implementation-worker": allow\n',
                "canonical Task graph",
            ),
            (
                "removed Plan Orchestrator edge",
                "opencode/agents/plan-orchestrator.md",
                '    "implementation-worker": allow\n',
                "",
                "canonical Task graph",
            ),
            (
                "subagent Task edge",
                "opencode/agents/accessibility-critic.md",
                '  task: deny\n',
                '  task:\n    "*": deny\n    "implementation-worker": allow\n',
                "canonical Task graph",
            ),
        )
        for label, relative_path, old, new, expected in mutations:
            with self.subTest(mutation=label), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_canonical_active_workflow_repo(root)
                definition = repo / relative_path
                original = definition.read_text(encoding="utf-8")
                self.assertIn(old, original)
                definition.write_text(original.replace(old, new, 1), encoding="utf-8")

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(any(expected in error for error in result.errors), result.errors)

    def test_validate_rejects_canonical_command_owner_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_canonical_active_workflow_repo(root)
            command = repo / "opencode" / "commands" / "review-plan.md"
            command.write_text(
                command.read_text(encoding="utf-8").replace(
                    "agent: engineering-review-board",
                    "agent: plan-orchestrator",
                    1,
                ),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertTrue(
                any("review-plan.md' must use canonical primary owner" in error for error in result.errors),
                result.errors,
            )

    def test_checked_in_permission_profiles_match_assignments_and_isolate_plan_state(self) -> None:
        project_root = Path(__file__).parents[1]
        expected_profile_names = {
            policy.permission_profile for policy in CANONICAL_AGENT_TOPOLOGY.agents
        }
        self.assertEqual(expected_profile_names, set(CANONICAL_PERMISSION_PROFILES))

        specialist_permissions = None
        for policy in CANONICAL_AGENT_TOPOLOGY.agents:
            parsed, errors = OpenCodeInstallService._parse_frontmatter(
                "agents",
                f"{policy.agent_id}.md",
                (project_root / "opencode" / "agents" / f"{policy.agent_id}.md").read_text(
                    encoding="utf-8"
                ),
            )
            self.assertEqual([], errors)
            assert parsed is not None
            self.assertEqual(
                CANONICAL_PERMISSION_PROFILES[policy.permission_profile].permissions,
                parsed.permissions,
                policy.agent_id,
            )
            external_directory = parsed.permissions["external_directory"]
            self.assertIsInstance(external_directory, tuple)
            assert isinstance(external_directory, tuple)
            self.assertEqual(
                "deny" if policy.agent_id == "plan-orchestrator" else "ask",
                resolve_opencode_action(
                    external_directory,
                    "/external-audit-root/example.py",
                    baseline="deny",
                ),
            )
            for tool in ("read", "glob", "grep", "list", "lsp"):
                rules = parsed.permissions[tool]
                self.assertIsInstance(rules, tuple)
                assert isinstance(rules, tuple)
                self.assertEqual("allow", resolve_opencode_action(rules, "src/example.py", baseline="deny"))
                self.assertEqual(
                    "allow" if policy.agent_id == "plan-orchestrator" else "deny",
                    resolve_opencode_action(rules, ".erb/plan-state.json", baseline="deny"),
                )
            if policy.permission_profile == "review-specialist":
                if specialist_permissions is None:
                    specialist_permissions = parsed.permissions
                else:
                    self.assertEqual(specialist_permissions, parsed.permissions)

    def test_checked_in_external_directory_governance_contract(self) -> None:
        project_root = Path(__file__).parents[1]
        for relative_path, tokens in EXTERNAL_DIRECTORY_DOC_TOKENS.items():
            with self.subTest(path=relative_path):
                text = (project_root / relative_path).read_text(encoding="utf-8")
                for token in tokens:
                    self.assertIn(token, text)

    def test_checked_in_technical_researcher_asks_before_using_hound(self) -> None:
        project_root = Path(__file__).parents[1]
        parsed, errors = OpenCodeInstallService._parse_frontmatter(
            "agents",
            "technical-researcher.md",
            (project_root / "opencode/agents/technical-researcher.md").read_text(
                encoding="utf-8"
            ),
        )

        self.assertEqual([], errors)
        assert parsed is not None
        self.assertEqual("ask", parsed.permissions["hound_*"])

    def test_checked_in_mcp_enabled_agents_define_server_selection(self) -> None:
        project_root = Path(__file__).parents[1]
        for name, (heading, required_tokens) in MCP_SELECTION_PROMPT_CONTRACTS.items():
            with self.subTest(agent=name):
                text = (project_root / "opencode" / "agents" / name).read_text(
                    encoding="utf-8"
                )
                self.assertEqual(
                    1,
                    sum(line.strip() == heading for line in text.splitlines()),
                )
                normalized = " ".join(text.split())
                for token in required_tokens:
                    self.assertIn(token, normalized)

    def test_validate_rejects_external_directory_governance_drift(self) -> None:
        for relative_path, tokens in EXTERNAL_DIRECTORY_DOC_TOKENS.items():
            with self.subTest(path=relative_path), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_canonical_active_workflow_repo(root)
                path = repo / relative_path
                text = path.read_text(encoding="utf-8")
                path.write_text(
                    text.replace(tokens[0], "SYNTHETIC_STATIC_CONTRACT_MARKER", 1),
                    encoding="utf-8",
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(
                    any("external-directory document" in error for error in result.errors),
                    result.errors,
                )

    def test_validate_rejects_external_directory_permission_profile_drift(self) -> None:
        cases = {
            "engineering-lead.md": ("ask", "allow"),
            "engineering-review-board.md": ("ask", "deny"),
            "implementation-worker.md": ("ask", "deny"),
            "plan-orchestrator.md": ("deny", "ask"),
            "technical-researcher.md": ("ask", "deny"),
            "accessibility-critic.md": ("ask", "deny"),
        }
        for name, (current, replacement) in cases.items():
            with self.subTest(agent=name), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_canonical_active_workflow_repo(root)
                definition = repo / "opencode" / "agents" / name
                text = definition.read_text(encoding="utf-8")
                rule = f'  external_directory:\n    "*": {current}\n'
                self.assertIn(rule, text)
                definition.write_text(
                    text.replace(
                        rule,
                        f'  external_directory:\n    "*": {replacement}\n',
                        1,
                    ),
                    encoding="utf-8",
                )

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(
                    any("permission profile" in error for error in result.errors),
                    result.errors,
                )

    def test_checked_in_worker_git_permissions_resolve_to_effective_actions(self) -> None:
        project_root = Path(__file__).parents[1]
        worker, errors = OpenCodeInstallService._parse_frontmatter(
            "agents",
            "implementation-worker.md",
            (project_root / "opencode/agents/implementation-worker.md").read_text(
                encoding="utf-8"
            ),
        )
        self.assertEqual([], errors)
        assert worker is not None
        bash = worker.permissions["bash"]
        self.assertIsInstance(bash, tuple)
        assert isinstance(bash, tuple)

        cases = (
            ("bare status", "git status", "allow"),
            ("status with arguments", "git status --short", "ask"),
            ("bare diff", "git diff", "allow"),
            ("diff with arguments", "git diff --cached", "ask"),
            ("bare log", "git log", "allow"),
            ("log with arguments", "git log --oneline -10", "ask"),
            ("bare show", "git show", "allow"),
            ("show with arguments", "git show HEAD", "ask"),
            ("branch inspection", "git branch --show-current", "allow"),
            ("staging", "git add -- src/example.py", "deny"),
            ("commit", "git commit", "deny"),
            ("push", "git push origin main", "deny"),
            ("destructive reset", "git reset --hard HEAD", "deny"),
            ("destructive clean", "git clean -fd", "deny"),
            ("state redirection", "git diff > .erb/plan-state.json", "deny"),
        )
        for label, command, expected in cases:
            with self.subTest(action=label, command=command):
                self.assertEqual(expected, resolve_opencode_action(bash, command))

    def test_validate_rejects_permission_profile_and_plan_state_navigation_drift(self) -> None:
        mutations = (
            (
                "profile drift",
                "opencode/agents/accessibility-critic.md",
                "  question: allow\n",
                "  question: deny\n",
                "permission profile",
            ),
            (
                "missing state deny",
                "opencode/agents/engineering-review-board.md",
                '  read:\n    "*": allow\n    ".erb/plan-state.json": deny\n',
                '  read:\n    "*": allow\n',
                "plan-state navigation isolation",
            ),
            (
                "later state override",
                "opencode/agents/technical-researcher.md",
                '    ".erb/plan-state.json": deny\n  glob:',
                '    ".erb/plan-state.json": deny\n    ".erb/*": allow\n  glob:',
                "plan-state navigation isolation",
            ),
        )
        for label, relative_path, old, new, expected in mutations:
            with self.subTest(mutation=label), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_canonical_active_workflow_repo(root)
                definition = repo / relative_path
                original = definition.read_text(encoding="utf-8")
                self.assertIn(old, original)
                definition.write_text(original.replace(old, new, 1), encoding="utf-8")

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(any(expected in error for error in result.errors), result.errors)

    def test_validate_rejects_incomplete_profile_shapes_without_raising(self) -> None:
        mutations = (
            (
                "missing navigation permission",
                "opencode/agents/technical-researcher.md",
                '  read:\n    "*": allow\n    ".erb/plan-state.json": deny\n',
                "",
                "plan-state navigation isolation",
            ),
            (
                "scalar Bash permission",
                "opencode/agents/accessibility-critic.md",
                '  bash:\n    "*": deny\n    "git status": allow\n    "git status --short": allow\n'
                '    "git diff": allow\n    "git diff --cached": allow\n'
                '    "git diff --check": allow\n    "git log --oneline -10": allow\n'
                '    "git branch --show-current": allow\n',
                "  bash: deny\n",
                "canonical Bash rule map",
            ),
        )
        for label, relative_path, old, new, expected in mutations:
            with self.subTest(mutation=label), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_canonical_active_workflow_repo(root)
                definition = repo / relative_path
                original = definition.read_text(encoding="utf-8")
                self.assertIn(old, original)
                definition.write_text(original.replace(old, new, 1), encoding="utf-8")

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(any(expected in error for error in result.errors), result.errors)


    def test_validate_rejects_each_later_worker_deny_weakening(self) -> None:
        mutations = (
            ("git add*", "ask"),
            ("git commit*", "ask"),
            ("git push*", "ask"),
            ("git reset*", "ask"),
            ("git clean*", "ask"),
            ("rm*", "ask"),
            ("sudo*", "ask"),
            ("*plans/*", "ask"),
            ("*.erb/plans/*", "ask"),
            ("*.erb/plan-state.json*", "ask"),
        )
        for pattern, action in mutations:
            with self.subTest(pattern=pattern), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo = create_canonical_active_workflow_repo(root)
                worker = repo / "opencode" / "agents" / "implementation-worker.md"
                original = worker.read_text(encoding="utf-8")
                if pattern == "*.erb/plan-state.json*":
                    mutation = original.replace(
                        '    "*.erb/plan-state.json*": deny\n',
                        '    "*.erb/plan-state.json*": ask\n',
                        1,
                    )
                else:
                    mutation = original.replace(
                        '    "*.erb/plan-state.json*": deny\n',
                        f'    "*.erb/plan-state.json*": deny\n    "{pattern}": {action}\n',
                        1,
                    )
                worker.write_text(mutation, encoding="utf-8")

                result = OpenCodeInstallService(repo, root / "config").validate()

                self.assertFalse(result.ok)
                self.assertTrue(
                    any("complete Worker deny surface" in error for error in result.errors),
                    result.errors,
                )

    def test_checked_in_plan_workflow_uses_explicit_commands_and_pointer_state(self) -> None:
        project_root = Path(__file__).parents[1]
        manifest = json.loads(
            (project_root / "opencode/manifest.json").read_text(encoding="utf-8")
        )

        self.assertEqual(set(manifest), {"agents", "commands", "support_files"})
        self.assertEqual(
            manifest["commands"],
            [
                "address-review.md",
                "audit-technical-debt.md",
                "brainstorm.md",
                "consult-plan.md",
                "create-plan.md",
                "investigate-regression.md",
                "optimize-prompt.md",
                "review-implementation.md",
                "review-plan.md",
                "root-cause-analysis.md",
                "semver.md",
                "start-plan.md",
                "update-plan.md",
            ],
        )

        start_plan = (project_root / "opencode/commands/start-plan.md").read_text(
            encoding="utf-8"
        )
        normalized = " ".join(start_plan.split())
        for token in (
            "Use syntax `/start-plan [<plan-path>] [instructions]`",
            "`.erb/plan-state.json`",
            '`{"plan_path":".erb/plans/<path>.md"}`',
            "Active means at least one unchecked TODO or Verification checkbox remains.",
            "The current step is the first unchecked checkbox in document order.",
            "This plan has already been implemented.",
            "An explicit valid path replaces missing, invalid, or stale state.",
            "Never block because another plan is selected or may be running.",
        ):
            with self.subTest(token=token):
                self.assertIn(token, normalized)



if __name__ == "__main__":
    unittest.main()
