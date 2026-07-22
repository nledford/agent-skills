import json
import os
import shutil
from pathlib import Path

from tools.opencode_contracts import (
    ENGINEERING_LEAD_GIT_BASH_RULES,
    ENGINEERING_LEAD_PLAN_STAGING_BASH_RULES,
)
from tools.opencode_install import (
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

def render_lead_permissions(
    *,
    git_rules: tuple[tuple[str, str], ...] = ENGINEERING_LEAD_GIT_BASH_RULES,
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
            for pattern, action in ENGINEERING_LEAD_PLAN_STAGING_BASH_RULES
        )
        + '    "pbcopy *": allow\n'
        '  "playwright_*": ask\n'
        '  "chrome-devtools_*": ask\n'
        '  "serena_*": ask\n'
        '  "hound_*": ask\n'
        '  "github_*": ask\n'
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
            "1. [ ] <one atomic implementation outcome; include prerequisites and expected permission gates when applicable>\n\n"
            "## Verification\n\n"
            "1. [ ] <one atomic verification outcome with focused evidence>\n"
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
