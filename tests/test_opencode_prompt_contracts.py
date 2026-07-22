import json
import re
import tempfile
import unittest
from pathlib import Path

from tools.opencode_contracts import (
    ADVERSARIAL_REVIEWER_STAGE_PROMPT_CONTRACTS,
    CANONICAL_PROMPT_SECTION_CONTRACTS,
    CODE_DOCUMENTATION_PROMPT_CONTRACTS,
    COMMAND_PROMPT_CONTRACTS,
    ENGINEERING_LEAD_PLAN_STAGING_PROMPT_REQUIREMENTS,
    HUMAN_CONTROLLED_LIFECYCLE_DOC_TOKENS,
    MCP_SELECTION_PROMPT_CONTRACTS,
    PLAN_ORCHESTRATOR_COMMIT_PROMPT_REQUIREMENTS,
    PRIMARY_AGENT_TURN_PROMPT_CONTRACTS,
    TECHNICAL_DEBT_AUDIT_PROMPT_CONTRACTS,
)
from tools.opencode_frontmatter import parse_frontmatter
from tools.opencode_install import OpenCodeInstallService
from tools.opencode_validation import (
    PromptContract,
    prompt_satisfies_contract,
    single_markdown_section,
)


from tests.opencode_test_support import (
    RETIRED_COMMAND_ID_TOKENS,
    STALE_LIFECYCLE_MUTATIONS,
    create_canonical_active_workflow_repo,
    create_plan_orchestrator_repo,
    plan_orchestrator_source,
    resolve_opencode_action,
)


class OpenCodeInstallServiceTests(unittest.TestCase):
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

        worker = parse_frontmatter(
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

        self.assertEqual(len(manifest["agents"]), 29)
        self.assertEqual(tuple(manifest["commands"]), expected_commands)
        self.assertEqual(set(manifest), {"agents", "commands", "support_files"})
        command_root = project_root / "opencode/commands"
        self.assertEqual(tuple(sorted(path.name for path in command_root.iterdir())), expected_commands)
        for name, owner in expected_owners.items():
            parsed, errors = parse_frontmatter(
                "commands", name, (command_root / name).read_text(encoding="utf-8")
            )
            self.assertEqual(errors, [])
            assert parsed is not None
            self.assertEqual(parsed.fields["agent"], owner)
            self.assertEqual(parsed.fields["subtask"], "false")

    def test_prompt_commands_delegate_methodology_to_loaded_skills(self) -> None:
        """Keep command-specific authority while loading reusable methodology once."""
        project_root = Path(__file__).parents[1]
        cases = {
            "brainstorm.md": {
                "skill": "brainstorming",
                "required": (
                    "Apply the loaded `brainstorming` workflow for framing, evidence "
                    "separation, option comparison, recommendation, and validation."
                ),
                "removed": "Generate at least two credible options",
                "owned": (
                    "tasks with an obvious single correct implementation",
                    "Route active unexplained symptoms to",
                    "Produce at least two credible candidate approaches",
                ),
            },
            "optimize-prompt.md": {
                "skill": "prompt-engineering-review",
                "required": (
                    "Apply the loaded `prompt-engineering-review` workflow for "
                    "objective, scope, autonomy, evidence, sequencing, verification, "
                    "and unresolved decisions."
                ),
                "removed": (
                    "Identify the intended agent, objective, inputs, scope, non-goals"
                ),
                "owned": (
                    "Identify the intended agent, objective, inputs, scope, non-goals",
                ),
            },
        }

        for command_name, case in cases.items():
            with self.subTest(command=command_name):
                command = " ".join(
                    (project_root / "opencode/commands" / command_name)
                    .read_text(encoding="utf-8")
                    .split()
                )
                skill = " ".join(
                    (project_root / "skills" / case["skill"] / "SKILL.md")
                    .read_text(encoding="utf-8")
                    .split()
                )
                self.assertIn(case["required"], command)
                self.assertNotIn(case["removed"], command)
                for owned_requirement in case["owned"]:
                    self.assertIn(owned_requirement, skill)

    def test_checked_in_semver_routes_explicit_modes_and_guards_tagging(self) -> None:
        """Pin SemVer mode authority, fresh evidence, and local-tag safety."""
        project_root = Path(__file__).parents[1]
        command_path = project_root / "opencode/commands/semver.md"
        self.assertTrue(command_path.is_file(), "semver.md")
        if not command_path.is_file():
            return

        command_text = command_path.read_text(encoding="utf-8")
        parsed, errors = parse_frontmatter(
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
        parsed, errors = parse_frontmatter(
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
        parsed, errors = parse_frontmatter(
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
            parsed, errors = parse_frontmatter(
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
            "derive the full canonical TODO obligation set",
            "three disjoint and collectively exhaustive sets: active slice, evidenced complete, and unresolved or deferred",
            "Select one bounded active slice",
            "No active criterion may also be deferred or prohibited.",
            "numbered acceptance criteria",
            "Satisfied dependencies / preserved state",
            "Plan and Task scope authorize the bounded work; they never satisfy an `ask` permission.",
            "Classify every required operation as allowed, ask-gated, or denied before delegation.",
            "One at a time means one active Worker and one current implementation TODO, not one attempt.",
            "A Worker return is evidence, not a terminal event.",
            "Map every acceptance criterion to fresh source, diff, and validation evidence.",
            "A Worker `COMPLETED` report closes only the active slice",
            "TODO-level integration validation",
            "Reconcile fresh evidence before interpreting either Worker status.",
            "close only that transient slice regardless of an incorrect label",
            "Strict progress means fresh evidence moves at least one previously unresolved active-slice criterion to evidenced complete.",
            "Re-partition strict progress into preserved completed criteria and a strictly smaller residual active slice.",
            "Reset the consecutive no-progress allowance only after strict progress.",
            "If no criterion changes classification, allow one same-`task_id` correction",
            "Never repeat an action whose prior result or replay safety cannot be established from fresh evidence.",
            "Apply the permission-state and replay-safety gates before the unsupported no-progress allowance.",
            "A policy denial or rejected approval for a command known not to have started is a genuine blocker",
            "While runtime approval is pending, retain the same waiting child",
            "Approval alone is not evidence that the operation ran.",
            "Worker's exact `approval_state`, `execution_state`, and `replay_safe` fields",
            "resume the same Worker child session by passing its `task_id`",
            "Do not start a fresh Worker Task for an in-scope correction when that child session can be resumed.",
            "A second consecutive unsupported no-progress terminal return for the same residual slice is an execution-channel failure",
            "If the runtime cannot resume that child after an interruption",
            "Keep a continuation delta-focused",
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
            "The numbered acceptance criteria define the active slice, not the parent plan TODO.",
            "Deferred or unassigned parent work is context only",
            "Preserve satisfied dependencies and do not repeat completed actions.",
            "Plan and Task scope do not satisfy an `ask` permission.",
            "While approval is pending, do not return a terminal status or issue another request.",
            "A policy denial or rejected approval before execution starts is `BLOCKED`",
            "approval state, whether execution started, whether a terminal outcome is known, and replay-safety evidence",
            "`execution_state` (`not_started`, `terminal_success`, `terminal_failure`, or `unknown`)",
            "Return exactly one status: `COMPLETED` or `BLOCKED`.",
            "`COMPLETED` reports only that the active slice is complete",
            "prevents every remaining safe action in the active slice",
            "requirement-to-evidence table",
            "A resumed correction assignment must enumerate at least one concrete evidence gap",
            "Do not infer missing findings from a status-only preamble",
        )
        command_requirements = (
            "Use the Plan Orchestrator's self-contained delegation and corrective-continuation contract.",
            "A Worker return does not end the current TODO.",
            "derive and reconcile the full canonical TODO obligation set",
            "one bounded active slice",
            "Reconcile fresh slice evidence before interpreting `COMPLETED` or `BLOCKED`.",
            "Strict progress moves at least one previously unresolved active-slice criterion to evidenced complete.",
            "A second consecutive unsupported no-progress terminal return for the same residual slice is an execution-channel failure",
            "Never repeat an action whose prior result or replay safety cannot be established from fresh evidence.",
            "Plan and Task scope never satisfy an `ask` permission.",
            "Do not continue or create another Task while runtime approval is pending.",
            "A policy denial or rejected approval for a command known not to have started stops the current `/start-plan` invocation immediately.",
            "Approval alone does not prove execution.",
            "TODO-level integration validation",
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

    def test_validate_rejects_planned_worker_slice_contract_drift(self) -> None:
        """Require production validation for sliced evidence-first handoffs."""
        mutations = (
            (
                "opencode/agents/plan-orchestrator.md",
                "three disjoint and collectively exhaustive sets: active slice, evidenced complete, and unresolved or deferred",
            ),
            (
                "opencode/agents/plan-orchestrator.md",
                "Strict progress means fresh evidence moves at least one previously unresolved active-slice criterion to evidenced complete.",
            ),
            (
                "opencode/agents/plan-orchestrator.md",
                "Reset the consecutive no-progress allowance only after strict progress.",
            ),
            (
                "opencode/agents/plan-orchestrator.md",
                "A second consecutive unsupported no-progress terminal return for the same residual slice is an execution-channel failure",
            ),
            (
                "opencode/agents/plan-orchestrator.md",
                "close only that transient slice regardless of an incorrect label",
            ),
            (
                "opencode/agents/plan-orchestrator.md",
                "Never repeat an action whose prior result or replay safety cannot be established from fresh evidence.",
            ),
            (
                "opencode/agents/plan-orchestrator.md",
                "Keep a continuation delta-focused",
            ),
            (
                "opencode/agents/plan-orchestrator.md",
                "Apply the permission-state and replay-safety gates before the unsupported no-progress allowance.",
            ),
            (
                "opencode/agents/implementation-worker.md",
                "Deferred or unassigned parent work is context only",
            ),
            (
                "opencode/agents/implementation-worker.md",
                "Plan and Task scope do not satisfy an `ask` permission.",
            ),
            (
                "opencode/agents/implementation-worker.md",
                "prevents every remaining safe action in the active slice",
            ),
            (
                "opencode/commands/start-plan.md",
                "TODO-level integration validation",
            ),
            (
                "opencode/commands/start-plan.md",
                "Do not continue or create another Task while runtime approval is pending.",
            ),
            (
                "docs/engineering-agent-governance.md",
                "an unavailable prior Task session",
            ),
            (
                "docs/engineering-agent-governance.md",
                "A policy denial or rejected approval never enters the unsupported no-progress allowance.",
            ),
        )

        for index, (relative_path, token) in enumerate(mutations):
            with self.subTest(path=relative_path, token=token):
                with tempfile.TemporaryDirectory() as temp_dir:
                    root = Path(temp_dir) / str(index)
                    repo = create_canonical_active_workflow_repo(root)
                    baseline = OpenCodeInstallService(repo, root / "config").validate()
                    self.assertTrue(baseline.ok, baseline.errors)

                    definition = repo / relative_path
                    original = definition.read_text(encoding="utf-8")
                    self.assertIn(token, " ".join(original.split()))
                    pattern = r"\s+".join(re.escape(part) for part in token.split())
                    mutation, replacements = re.subn(
                        pattern,
                        "slice contract removed",
                        original,
                        count=1,
                    )
                    self.assertEqual(1, replacements)
                    definition.write_text(
                        mutation,
                        encoding="utf-8",
                    )

                    result = OpenCodeInstallService(repo, root / "config").validate()
                    self.assertTrue(
                        any(
                            "contract is incomplete" in error
                            for error in result.errors
                        ),
                        result.errors,
                    )

    def test_checked_in_update_plan_requires_exact_plan_only_authority(self) -> None:
        """Pin active-plan amendment, checkbox reconciliation, and resume separation."""
        project_root = Path(__file__).parents[1]
        command_path = project_root / "opencode/commands/update-plan.md"
        command_text = command_path.read_text(encoding="utf-8")
        normalized = " ".join(command_text.split())

        parsed, errors = parse_frontmatter(
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
            "Revalidate every TODO and Verification entry against the Plan Orchestrator's checklist-entry contract.",
            "Dependency correctness outranks preserving existing order.",
            "old-to-new ordering and the reason for each move",
            "checklist-entry violations in the existing active plan are repair inputs",
            "execution-only `/start-plan` material-plan-change stop rule",
            "validate the complete candidate plan before mutation",
            "including checkbox reconciliation and any re-sequencing",
            "stop with the original plan unchanged",
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
            section = single_markdown_section(
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

            def remove_token(text: str, token: str) -> str:
                pattern = re.escape(token).replace(r"\ ", r"\s+")
                changed, count = re.subn(pattern, "contract removed", text)
                self.assertGreaterEqual(count, 1, token)
                return changed

            for relative_path, tokens in HUMAN_CONTROLLED_LIFECYCLE_DOC_TOKENS.items():
                original = (repo / relative_path).read_text(encoding="utf-8")
                contract = PromptContract(required=tokens)
                self.assertTrue(
                    prompt_satisfies_contract(original, contract),
                    relative_path,
                )
                for token in tokens:
                    with self.subTest(document=relative_path, token=token):
                        self.assertFalse(
                            prompt_satisfies_contract(
                                remove_token(original, token),
                                contract,
                            )
                        )

            relative_path = "docs/cross-reference-map.md"
            document = repo / relative_path
            original = document.read_text(encoding="utf-8")
            required = HUMAN_CONTROLLED_LIFECYCLE_DOC_TOKENS[relative_path][0]
            document.write_text(
                remove_token(original, required),
                encoding="utf-8",
            )
            result = OpenCodeInstallService(repo, root / "config").validate()
            self.assertIn(
                f"human-controlled lifecycle document '{relative_path}' contract is incomplete",
                result.errors,
            )

            forbidden = "automatically creates a plan through `/start-plan`"
            document.write_text(
                original + f"\nComplexity {forbidden}.\n",
                encoding="utf-8",
            )
            self.assertFalse(
                prompt_satisfies_contract(
                    document.read_text(encoding="utf-8").lower(),
                    PromptContract(forbidden=(forbidden,)),
                )
            )
            result = OpenCodeInstallService(repo, root / "config").validate()
            self.assertIn(
                f"human-controlled lifecycle document '{relative_path}' contains forbidden automatic `/start-plan` creation",
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
            parsed, errors = parse_frontmatter(
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
        parsed, errors = parse_frontmatter(
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
                contract = PromptContract(required=tokens)
                self.assertTrue(prompt_satisfies_contract(original, contract), name)
                for token in tokens:
                    with self.subTest(command=name, token=token):
                        self.assertFalse(
                            prompt_satisfies_contract(
                                remove_token(original, token),
                                contract,
                            )
                        )

            sentinel_name, sentinel_tokens = next(iter(COMMAND_PROMPT_CONTRACTS.items()))
            sentinel_command = repo / "opencode/commands" / sentinel_name
            sentinel_original = sentinel_command.read_text(encoding="utf-8")
            sentinel_command.write_text(
                remove_token(sentinel_original, sentinel_tokens[0]),
                encoding="utf-8",
            )
            result = OpenCodeInstallService(repo, root / "config").validate()
            self.assertTrue(
                any(
                    f"{sentinel_name}' prompt contract is incomplete" in error
                    for error in result.errors
                ),
                result.errors,
            )
            sentinel_command.write_text(sentinel_original, encoding="utf-8")

            agent_tokens = {
                name: semantics
                for name, (_, semantics) in CANONICAL_PROMPT_SECTION_CONTRACTS.items()
            } | {
                name: semantics
                for name, (_, semantics) in TECHNICAL_DEBT_AUDIT_PROMPT_CONTRACTS.items()
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
                    "derive the full canonical TODO obligation set",
                    "three disjoint and collectively exhaustive sets: active slice, evidenced complete, and unresolved or deferred",
                    "Select one bounded active slice",
                    "No active criterion may also be deferred or prohibited.",
                    "numbered acceptance criteria",
                    "Satisfied dependencies / preserved state",
                    "Plan and Task scope authorize the bounded work; they never satisfy an `ask` permission.",
                    "Classify every required operation as allowed, ask-gated, or denied before delegation.",
                    "One at a time means one active Worker and one current implementation TODO, not one attempt.",
                    "A Worker return is evidence, not a terminal event.",
                    "Map every acceptance criterion to fresh source, diff, and validation evidence.",
                    "A Worker `COMPLETED` report closes only the active slice",
                    "TODO-level integration validation",
                    "Reconcile fresh evidence before interpreting either Worker status.",
                    "close only that transient slice regardless of an incorrect label",
                    "Strict progress means fresh evidence moves at least one previously unresolved active-slice criterion to evidenced complete.",
                    "Re-partition strict progress into preserved completed criteria and a strictly smaller residual active slice.",
                    "Reset the consecutive no-progress allowance only after strict progress.",
                    "If no criterion changes classification, allow one same-`task_id` correction",
                    "Never repeat an action whose prior result or replay safety cannot be established from fresh evidence.",
                    "Apply the permission-state and replay-safety gates before the unsupported no-progress allowance.",
                    "A policy denial or rejected approval for a command known not to have started is a genuine blocker",
                    "While runtime approval is pending, retain the same waiting child",
                    "Approval alone is not evidence that the operation ran.",
                    "Worker's exact `approval_state`, `execution_state`, and `replay_safe` fields",
                    "resume the same Worker child session by passing its `task_id`",
                    "Do not start a fresh Worker Task for an in-scope correction when that child session can be resumed.",
                    "A second consecutive unsupported no-progress terminal return for the same residual slice is an execution-channel failure",
                    "If the runtime cannot resume that child after an interruption",
                    "Keep a continuation delta-focused",
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
                    "The numbered acceptance criteria define the active slice, not the parent plan TODO.",
                    "Deferred or unassigned parent work is context only",
                    "Preserve satisfied dependencies and do not repeat completed actions.",
                    "Plan and Task scope do not satisfy an `ask` permission.",
                    "While approval is pending, do not return a terminal status or issue another request.",
                    "A policy denial or rejected approval before execution starts is `BLOCKED`",
                    "approval state, whether execution started, whether a terminal outcome is known, and replay-safety evidence",
                    "`execution_state` (`not_started`, `terminal_success`, `terminal_failure`, or `unknown`)",
                    "Return exactly one status: `COMPLETED` or `BLOCKED`.",
                    "`COMPLETED` reports only that the active slice is complete",
                    "prevents every remaining safe action in the active slice",
                    "requirement-to-evidence table",
                    "A resumed correction assignment must enumerate at least one concrete evidence gap",
                    "Do not infer missing findings from a status-only preamble",
                ),
            }
            for name, tokens in agent_tokens.items():
                agent = repo / "opencode/agents" / name
                original = agent.read_text(encoding="utf-8")
                contract = PromptContract(required=tokens)
                self.assertTrue(prompt_satisfies_contract(original, contract), name)
                for token in tokens:
                    with self.subTest(agent=name, token=token):
                        self.assertFalse(
                            prompt_satisfies_contract(
                                remove_token(original, token),
                                contract,
                            )
                        )

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
                        "Return repair guidance for direct Lead implementation only when the direct cause is confirmed and the repair is safely bounded.",
                        "For a probable or incomplete result, return the next discriminating experiment instead of a repair.",
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
                prompt_contract = PromptContract(
                    required=contract["required"],
                    forbidden=contract["forbidden"],
                )
                self.assertTrue(
                    prompt_satisfies_contract(original, prompt_contract),
                    relative_path,
                )
                sentinel_paragraph = next(
                    paragraph
                    for paragraph in original.split("\n\n")
                    if sentinel in paragraph
                )
                for forbidden in contract["forbidden"]:
                    with self.subTest(route=relative_path, forbidden=forbidden):
                        mutated = original + f"\n{forbidden}\n"
                        self.assertFalse(
                            prompt_satisfies_contract(mutated, prompt_contract)
                        )
                        self.assertIn(sentinel_paragraph, mutated)
                for required in contract["required"]:
                    with self.subTest(route=relative_path, required=required):
                        mutated = remove_token(original, required)
                        self.assertFalse(
                            prompt_satisfies_contract(mutated, prompt_contract)
                        )
                        self.assertIn(sentinel_paragraph, mutated)

            retained = repo / "opencode/commands/audit-technical-debt.md"
            retained_original = retained.read_text(encoding="utf-8")
            retained_required = retained_routes["commands/audit-technical-debt.md"][
                "required"
            ][0]
            retained.write_text(
                remove_token(retained_original, retained_required),
                encoding="utf-8",
            )
            result = OpenCodeInstallService(repo, root / "config").validate()
            self.assertTrue(
                any(
                    "retained route" in error and "contract is incomplete" in error
                    for error in result.errors
                ),
                result.errors,
            )
            retained.write_text(retained_original, encoding="utf-8")

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
    def test_checked_in_prompt_critic_agent_system_review_is_bounded_and_reusable(
        self,
    ) -> None:
        project_root = Path(__file__).parents[1]
        prompt = (
            project_root / "opencode/agents/prompt-critic.md"
        ).read_text(encoding="utf-8")
        section = single_markdown_section(prompt, "## Agent-System Review")

        self.assertIsNotNone(section)
        assert section is not None
        normalized_section = " ".join(section.split())
        for required in (
            "explicitly identifies a bounded coordination surface",
            "Adjacent definitions are evidence only",
            "Agent-system review: applicable",
            "instruction interfaces, not application architecture",
            "Static prompt contracts do not prove runtime behavior",
        ):
            with self.subTest(required=required):
                self.assertIn(required, normalized_section)

        skill = (
            project_root / "skills/prompt-engineering-review/SKILL.md"
        ).read_text(encoding="utf-8")
        skill_section = single_markdown_section(skill, "## Agent-System Review")
        self.assertIsNotNone(skill_section)
        assert skill_section is not None
        normalized_skill_section = " ".join(skill_section.split())
        for required in (
            "two or more interacting prompt artifacts",
            "Do not infer a repository-wide review",
            "entry point, nodes, handoff edges, and state owners",
            "Distinguish instruction defects from application architecture",
        ):
            with self.subTest(required=required):
                self.assertIn(required, normalized_skill_section)

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
                for phrase in removed_restatements.get(name, ()):
                    self.assertNotIn(phrase, prompt)

    def test_checked_in_board_plan_reviews_match_closed_lean_contract(self) -> None:
        project_root = Path(__file__).parents[1]
        prompt = (
            project_root / "opencode/agents/engineering-review-board.md"
        ).read_text(encoding="utf-8")
        section = single_markdown_section(
            prompt, "## Plan Reviews"
        )

        self.assertIsNotNone(section)
        assert section is not None
        for required in (
            "contained canonical path and layout",
            "canonical template's exact title and ordered headings",
            "fixed Context labels and numbered TODO and Verification checklist grammar",
            "one atomic purpose",
            "expected permission gates and contained targets",
            "prerequisite-before-dependent ordering",
            "dependency cycles, mutually waiting steps, or unbounded progress loops",
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

    def test_checked_in_plan_checklist_contract_is_atomic_permission_aware_and_ordered(
        self,
    ) -> None:
        project_root = Path(__file__).parents[1]
        sources = {
            "guide": project_root / "docs/implementation-plans/README.md",
            "orchestrator": project_root / "opencode/agents/plan-orchestrator.md",
            "create": project_root / "opencode/commands/create-plan.md",
            "update": project_root / "opencode/commands/update-plan.md",
            "board": project_root / "opencode/agents/engineering-review-board.md",
        }
        normalized = {
            name: " ".join(path.read_text(encoding="utf-8").split())
            for name, path in sources.items()
        }

        requirements = {
            "guide": (
                "## Checklist Entry Contract",
                "one atomic purpose",
                "must not depend on itself or a later checklist entry",
                "known ask-gated or destructive operation and its exact contained target",
                "planning disclosure is not approval",
                "finite completion or stop condition",
                "checklist-entry violations in the existing active plan are repair inputs",
                "validate the complete candidate plan before mutation",
                "including checkbox reconciliation and any re-sequencing",
                "stop with the original plan unchanged",
            ),
            "orchestrator": (
                "## Checklist Entry Contract",
                "Do not use Worker slicing to make a compound checklist entry acceptable.",
                "validate the whole plan against this contract",
                "checklist-entry violations in the existing active plan are repair inputs",
                "execution-only `/start-plan` material-plan-change stop rule",
                "During `/start-plan`, if an existing plan fails it",
                "validate the complete candidate plan before mutation",
                "including checkbox reconciliation and any re-sequencing",
            ),
            "create": (
                "Apply the Plan Orchestrator's checklist-entry contract before writing.",
            ),
            "update": (
                "Dependency correctness outranks preserving existing order.",
                "old-to-new ordering and the reason for each move",
                "checklist-entry violations in the existing active plan are repair inputs",
                "validate the complete candidate plan before mutation",
                "including checkbox reconciliation and any re-sequencing",
                "stop with the original plan unchanged",
            ),
            "board": (
                "one atomic purpose",
                "expected permission gates and contained targets",
                "prerequisite-before-dependent ordering",
                "dependency cycles, mutually waiting steps, or unbounded progress loops",
            ),
        }

        for source, required_phrases in requirements.items():
            for phrase in required_phrases:
                with self.subTest(source=source, phrase=phrase):
                    self.assertIn(phrase, normalized[source])

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo, definition = create_plan_orchestrator_repo(root)
            prompt = definition.read_text(encoding="utf-8")
            required = "Do not use Worker slicing to make a compound checklist entry acceptable."
            self.assertIn(required, " ".join(prompt.split()))
            pattern = r"\s+".join(re.escape(part) for part in required.split())
            mutation, replacements = re.subn(
                pattern,
                "removed checklist-entry gate",
                prompt,
                count=1,
            )
            self.assertEqual(1, replacements)
            definition.write_text(
                mutation,
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertTrue(
                any("prompt contract is incomplete" in error for error in result.errors),
                result.errors,
            )

    def test_validate_rejects_plan_orchestrator_update_repair_phase_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo, definition = create_plan_orchestrator_repo(root)
            prompt = definition.read_text(encoding="utf-8")
            required = (
                "checklist-entry violations in the existing active plan are repair inputs"
            )
            self.assertIn(required, " ".join(prompt.split()))
            pattern = r"\s+".join(re.escape(part) for part in required.split())
            mutation, replacements = re.subn(
                pattern,
                "pre-existing violations require another update",
                prompt,
                count=1,
            )
            self.assertEqual(1, replacements)
            definition.write_text(
                mutation,
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertTrue(
                any("prompt contract is incomplete" in error for error in result.errors),
                result.errors,
            )

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
            (
                "missing atomic checklist criterion",
                "one atomic purpose",
                "synthetic removed criterion",
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
