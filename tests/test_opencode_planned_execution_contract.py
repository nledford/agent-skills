"""Synthetic, non-runtime observations of the checked-in planned-work contract."""

from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from tools.opencode_contracts import CANONICAL_AGENT_TOPOLOGY, PLANNED_WORK_PROMPT_CONTRACTS
from tools.opencode_frontmatter import ParsedFrontmatter, parse_frontmatter
from tools.opencode_install import OpenCodeInstallService
from tools.opencode_validation import normalize_prompt, single_markdown_section

from tests.opencode_test_support import (
    create_canonical_active_workflow_repo,
    resolve_opencode_action,
)


class Mode(str, Enum):
    IMPLEMENTATION = "implementation"
    VERIFICATION = "verification"


class EffectClass(str, Enum):
    REPEATABLE_LOCAL = "repeatable_local"
    CONSEQUENTIAL = "consequential"
    PROHIBITED = "prohibited"


class ApprovalState(str, Enum):
    APPROVED = "approved"
    PENDING = "pending"
    DENIED = "denied"
    REJECTED = "rejected"


class ExecutionState(str, Enum):
    NOT_STARTED = "not_started"
    RUNNING_OR_WAITING = "running_or_waiting"
    TERMINAL_SUCCESS = "terminal_success"
    TERMINAL_FAILURE = "terminal_failure"
    UNKNOWN = "unknown"


class PriorProcessState(str, Enum):
    NO_LIVE_PROCESS = "no_live_process"
    LIVE_PROCESS = "live_process"
    INCOMPLETE_EVIDENCE = "incomplete_evidence"


class TransitionAction(str, Enum):
    RETRY_ELIGIBLE = "retry_eligible"
    EXHAUSTED_STOP = "exhausted_stop"
    WAIT_TO_DEADLINE = "wait_to_deadline"
    NEEDS_CORRECTION = "needs_correction"
    REPLAY_ELIGIBLE = "replay_eligible"
    RETAIN_WAITING_CHILD = "retain_waiting_child"
    STOP_UNCHECKED = "stop_unchecked"
    RECONCILE_SUCCESS = "reconcile_success"
    INVALID_INPUT_STOP = "invalid_input_stop"


@dataclass(frozen=True)
class PermissionDecision:
    action: str

    @property
    def zero_prompt(self) -> bool:
        return self.action == "allow"


@dataclass(frozen=True)
class TransitionInput:
    effect_class: EffectClass
    approval_state: ApprovalState
    execution_state: ExecutionState
    attempt_count: int
    authorized_max_attempts: int = 3
    prior_process: PriorProcessState = PriorProcessState.NO_LIVE_PROCESS
    every_possible_effect_local_repeatable: bool = False
    known_contention: bool = False
    finite_wait_deadline: int | None = None
    deterministic_verification_failure: bool = False
    unexpected_effect: bool = False
    material_scope_change: bool = False
    reconciled_terminal_success: bool = False


@dataclass(frozen=True)
class TransitionResult:
    action: TransitionAction
    attempt_count: int
    checkbox_advance_permitted: bool = False
    next_units: tuple[Mode, ...] = ()
    replay_safe: bool = False


class SyntheticTransitionOracle:
    """Non-runtime, non-authoritative finite test oracle for prompt observations."""

    def resolve(self, event: TransitionInput) -> TransitionResult:
        if (
            event.attempt_count < 0
            or event.authorized_max_attempts < 1
            or event.authorized_max_attempts > 3
            or event.attempt_count > event.authorized_max_attempts
        ):
            return TransitionResult(TransitionAction.INVALID_INPUT_STOP, event.attempt_count)
        if event.approval_state is ApprovalState.PENDING:
            return TransitionResult(TransitionAction.RETAIN_WAITING_CHILD, event.attempt_count)
        if event.approval_state in {ApprovalState.DENIED, ApprovalState.REJECTED}:
            return TransitionResult(TransitionAction.STOP_UNCHECKED, event.attempt_count)
        if event.unexpected_effect or event.material_scope_change or event.effect_class is EffectClass.PROHIBITED:
            return TransitionResult(TransitionAction.STOP_UNCHECKED, event.attempt_count)
        if event.known_contention:
            if event.finite_wait_deadline is None or event.finite_wait_deadline < 1:
                return TransitionResult(TransitionAction.INVALID_INPUT_STOP, event.attempt_count)
            return TransitionResult(TransitionAction.WAIT_TO_DEADLINE, event.attempt_count)
        if event.execution_state is ExecutionState.UNKNOWN:
            if event.effect_class is EffectClass.CONSEQUENTIAL:
                return TransitionResult(TransitionAction.STOP_UNCHECKED, event.attempt_count)
            if (
                event.effect_class is EffectClass.REPEATABLE_LOCAL
                and event.prior_process is PriorProcessState.NO_LIVE_PROCESS
                and event.every_possible_effect_local_repeatable
            ):
                return TransitionResult(
                    TransitionAction.REPLAY_ELIGIBLE,
                    event.attempt_count,
                    replay_safe=True,
                )
            return TransitionResult(TransitionAction.STOP_UNCHECKED, event.attempt_count)
        if event.deterministic_verification_failure and event.execution_state is ExecutionState.TERMINAL_FAILURE:
            return TransitionResult(
                TransitionAction.NEEDS_CORRECTION,
                event.attempt_count,
                next_units=(Mode.IMPLEMENTATION, Mode.VERIFICATION),
            )
        if event.execution_state is ExecutionState.TERMINAL_FAILURE:
            if event.effect_class is EffectClass.REPEATABLE_LOCAL:
                if event.attempt_count < event.authorized_max_attempts:
                    return TransitionResult(TransitionAction.RETRY_ELIGIBLE, event.attempt_count)
                return TransitionResult(TransitionAction.EXHAUSTED_STOP, event.attempt_count)
            return TransitionResult(TransitionAction.STOP_UNCHECKED, event.attempt_count)
        if event.execution_state is ExecutionState.TERMINAL_SUCCESS:
            return TransitionResult(
                TransitionAction.RECONCILE_SUCCESS,
                event.attempt_count,
                checkbox_advance_permitted=event.reconciled_terminal_success,
            )
        return TransitionResult(TransitionAction.STOP_UNCHECKED, event.attempt_count)


class PlannedExecutionContractTests(unittest.TestCase):
    """Static source-contract tests; they never execute OpenCode or external state."""

    def setUp(self) -> None:
        self.oracle = SyntheticTransitionOracle()

    def _canonical_definitions(self) -> tuple[dict[str, list[str]], dict[str, str]]:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_canonical_active_workflow_repo(root)
            validation = OpenCodeInstallService(repo, root / "synthetic-config").validate()
            self.assertTrue(validation.ok, validation.errors)

            manifest = json.loads((repo / "opencode/manifest.json").read_text(encoding="utf-8"))
            self.assertEqual({"agents", "commands", "support_files"}, set(manifest))
            for kind in ("agents", "commands", "support_files"):
                for name in manifest[kind]:
                    relative = Path(kind) / name if kind != "support_files" else Path(name)
                    self.assertTrue((repo / "opencode" / relative).is_file(), relative)

            definitions = {
                "engineering-lead.md": (repo / "opencode/agents/engineering-lead.md").read_text(encoding="utf-8"),
                "implementation-worker.md": (repo / "opencode/agents/implementation-worker.md").read_text(encoding="utf-8"),
                "plan-orchestrator.md": (repo / "opencode/agents/plan-orchestrator.md").read_text(encoding="utf-8"),
                "start-plan.md": (repo / "opencode/commands/start-plan.md").read_text(encoding="utf-8"),
            }
            return manifest, definitions

    def _parsed_agents(self) -> dict[str, ParsedFrontmatter]:
        _, definitions = self._canonical_definitions()
        parsed_agents: dict[str, ParsedFrontmatter] = {}
        for name in ("engineering-lead.md", "implementation-worker.md", "plan-orchestrator.md"):
            parsed, errors = parse_frontmatter("agents", name, definitions[name])
            self.assertEqual([], errors)
            assert parsed is not None
            parsed_agents[name] = parsed
        return parsed_agents

    def _assert_effect_contract(self, prompt: str) -> None:
        section = single_markdown_section(prompt, "## Effect Classification And Transitions")
        self.assertIsNotNone(section)
        assert section is not None
        normalized = normalize_prompt(section)
        for token in PLANNED_WORK_PROMPT_CONTRACTS["plan-orchestrator.md"]:
            with self.subTest(token=token):
                self.assertIn(token, normalize_prompt(prompt))
        for token in (
            "known live lock/process contention waits to the packet deadline",
            "terminal transient `repeatable_local` failure may consume only remaining pre-authorized starts",
            "deterministic verification failure returns `NEEDS_CORRECTION`",
            "fresh bounded `implementation` assignment",
            "require fresh verification after correction",
            "Replay only when no prior process is live",
            "Unknown `consequential` execution",
            "denied or rejected permission",
            "A Worker result is evidence, never checkbox authority.",
        ):
            with self.subTest(effect_token=token):
                self.assertIn(token, normalized)

    def test_complete_fixture_connects_interaction_surface_and_ownership(self) -> None:
        manifest, definitions = self._canonical_definitions()
        self.assertEqual(CANONICAL_AGENT_TOPOLOGY.agent_filenames, tuple(manifest["agents"]))
        self.assertIn("start-plan.md", manifest["commands"])

        agents = self._parsed_agents()
        self.assertEqual("primary", agents["engineering-lead.md"].fields["mode"])
        self.assertEqual("subagent", agents["implementation-worker.md"].fields["mode"])
        self.assertEqual("primary", agents["plan-orchestrator.md"].fields["mode"])
        self.assertEqual(
            (("*", "deny"), ("implementation-worker", "allow")),
            agents["plan-orchestrator.md"].permissions["task"],
        )
        self.assertEqual((("*", "deny"),), agents["implementation-worker.md"].permissions["task"])

        start_plan, errors = parse_frontmatter("commands", "start-plan.md", definitions["start-plan.md"])
        self.assertEqual([], errors)
        assert start_plan is not None
        self.assertEqual("plan-orchestrator", start_plan.fields["agent"])
        self.assertEqual("false", start_plan.fields["subtask"])

        for name in definitions:
            normalized = normalize_prompt(definitions[name])
            with self.subTest(definition=name):
                self.assertIn("implementation", normalized)
                self.assertIn("verification", normalized)
        worker = normalize_prompt(definitions["implementation-worker.md"])
        for field in (
            "`effect_class`",
            "`approval_state`",
            "`execution_state`",
            "attempt_count` and `authorized_max_attempts`",
            "`replay_safe`",
        ):
            self.assertIn(field, worker)

        self._assert_effect_contract(definitions["plan-orchestrator.md"])
        self.assertEqual(
            1,
            normalize_prompt(definitions["plan-orchestrator.md"]).count(
                "sole normative planned-work effect and transition policy"
            ),
        )
        start = normalize_prompt(definitions["start-plan.md"])
        self.assertNotIn("Effect Classification And Transitions", definitions["start-plan.md"])
        self.assertIn("does not duplicate that transition policy", start)

    def test_ordered_permission_profiles_distinguish_zero_prompt_ask_and_deny(self) -> None:
        agents = self._parsed_agents()
        for name in ("engineering-lead.md", "implementation-worker.md"):
            with self.subTest(profile=name):
                parsed = agents[name]
                edit = parsed.permissions["edit"]
                bash = parsed.permissions["bash"]
                external_directory = parsed.permissions["external_directory"]
                self.assertIsInstance(edit, tuple)
                self.assertIsInstance(bash, tuple)
                self.assertIsInstance(external_directory, tuple)
                assert isinstance(edit, tuple)
                assert isinstance(bash, tuple)
                assert isinstance(external_directory, tuple)

                for representative in (
                    (edit, "src/synthetic.py", "allow", "ordinary edit"),
                    (bash, "just validate-opencode", "allow", "project runner"),
                    (bash, "cargo check", "allow", "cargo quality"),
                    (bash, "cargo build", "allow", "cargo build"),
                    (bash, "cargo test", "allow", "cargo test"),
                    (bash, "npm run lint", "allow", "package quality"),
                ):
                    rules, value, expected, label = representative
                    decision = PermissionDecision(resolve_opencode_action(rules, value))
                    with self.subTest(label=label):
                        self.assertEqual(expected, decision.action)
                        self.assertTrue(decision.zero_prompt)

                for rules, value, label in (
                    (bash, "synthetic-unknown-command", "unknown"),
                    (bash, "npm install -g synthetic-package", "global install"),
                    (bash, "docker rm synthetic-container", "shared service"),
                    (external_directory, "/synthetic-external-root/example.py", "external directory"),
                ):
                    with self.subTest(label=label):
                        self.assertEqual("ask", resolve_opencode_action(rules, value))

                denied_cases = [
                    (bash, "sudo synthetic-command", "privilege escalation"),
                    (edit, ".erb/plan-state.json", "plan state"),
                ]
                denied_cases.append(
                    (
                        bash,
                        "git push --force origin synthetic"
                        if name == "engineering-lead.md"
                        else "git reset --hard HEAD",
                        "destructive git",
                    )
                )
                for rules, value, label in denied_cases:
                    with self.subTest(label=label):
                        self.assertEqual("deny", resolve_opencode_action(rules, value))

        lead_bash = agents["engineering-lead.md"].permissions["bash"]
        worker_bash = agents["implementation-worker.md"].permissions["bash"]
        assert isinstance(lead_bash, tuple)
        assert isinstance(worker_bash, tuple)
        self.assertEqual("deny", resolve_opencode_action(lead_bash, "git push --force origin synthetic"))
        self.assertEqual("deny", resolve_opencode_action(worker_bash, "git push origin synthetic"))

        orchestrator = agents["plan-orchestrator.md"]
        edit = orchestrator.permissions["edit"]
        self.assertIsInstance(edit, tuple)
        assert isinstance(edit, tuple)
        self.assertEqual("allow", resolve_opencode_action(edit, ".erb/plans/synthetic.md", baseline="deny"))
        self.assertEqual("allow", resolve_opencode_action(edit, ".erb/plan-state.json", baseline="deny"))
        self.assertEqual("deny", resolve_opencode_action(edit, "src/synthetic.py", baseline="deny"))

    def test_finite_transition_oracle_observes_all_required_safe_outcomes(self) -> None:
        _, definitions = self._canonical_definitions()
        self._assert_effect_contract(definitions["plan-orchestrator.md"])

        transient = [
            self.oracle.resolve(
                TransitionInput(
                    EffectClass.REPEATABLE_LOCAL,
                    ApprovalState.APPROVED,
                    ExecutionState.TERMINAL_FAILURE,
                    attempt_count=attempt,
                )
            )
            for attempt in (1, 2, 3)
        ]
        self.assertEqual(
            [TransitionAction.RETRY_ELIGIBLE, TransitionAction.RETRY_ELIGIBLE, TransitionAction.EXHAUSTED_STOP],
            [result.action for result in transient],
        )
        self.assertTrue(all(not result.checkbox_advance_permitted for result in transient))

        contention = self.oracle.resolve(
            TransitionInput(
                EffectClass.REPEATABLE_LOCAL,
                ApprovalState.APPROVED,
                ExecutionState.RUNNING_OR_WAITING,
                attempt_count=1,
                known_contention=True,
                finite_wait_deadline=1,
            )
        )
        self.assertEqual(TransitionAction.WAIT_TO_DEADLINE, contention.action)
        self.assertEqual(1, contention.attempt_count)
        self.assertFalse(contention.checkbox_advance_permitted)

        correction = self.oracle.resolve(
            TransitionInput(
                EffectClass.REPEATABLE_LOCAL,
                ApprovalState.APPROVED,
                ExecutionState.TERMINAL_FAILURE,
                attempt_count=1,
                deterministic_verification_failure=True,
            )
        )
        self.assertEqual(TransitionAction.NEEDS_CORRECTION, correction.action)
        self.assertEqual((Mode.IMPLEMENTATION, Mode.VERIFICATION), correction.next_units)
        self.assertFalse(correction.checkbox_advance_permitted)

        replay = self.oracle.resolve(
            TransitionInput(
                EffectClass.REPEATABLE_LOCAL,
                ApprovalState.APPROVED,
                ExecutionState.UNKNOWN,
                attempt_count=1,
                every_possible_effect_local_repeatable=True,
            )
        )
        self.assertEqual(TransitionAction.REPLAY_ELIGIBLE, replay.action)
        self.assertTrue(replay.replay_safe)
        self.assertFalse(replay.checkbox_advance_permitted)
        for prior_process, complete_effect_proof in (
            (PriorProcessState.LIVE_PROCESS, True),
            (PriorProcessState.NO_LIVE_PROCESS, False),
            (PriorProcessState.INCOMPLETE_EVIDENCE, True),
        ):
            result = self.oracle.resolve(
                TransitionInput(
                    EffectClass.REPEATABLE_LOCAL,
                    ApprovalState.APPROVED,
                    ExecutionState.UNKNOWN,
                    attempt_count=1,
                    prior_process=prior_process,
                    every_possible_effect_local_repeatable=complete_effect_proof,
                )
            )
            with self.subTest(prior_process=prior_process, complete_effect_proof=complete_effect_proof):
                self.assertEqual(TransitionAction.STOP_UNCHECKED, result.action)
                self.assertFalse(result.replay_safe)
                self.assertFalse(result.checkbox_advance_permitted)

        unknown_consequential = self.oracle.resolve(
            TransitionInput(
                EffectClass.CONSEQUENTIAL,
                ApprovalState.APPROVED,
                ExecutionState.UNKNOWN,
                attempt_count=1,
            )
        )
        self.assertEqual(TransitionAction.STOP_UNCHECKED, unknown_consequential.action)
        self.assertFalse(unknown_consequential.replay_safe)
        self.assertFalse(unknown_consequential.checkbox_advance_permitted)

        known_consequential_failure = self.oracle.resolve(
            TransitionInput(
                EffectClass.CONSEQUENTIAL,
                ApprovalState.APPROVED,
                ExecutionState.TERMINAL_FAILURE,
                attempt_count=1,
            )
        )
        self.assertEqual(TransitionAction.STOP_UNCHECKED, known_consequential_failure.action)
        self.assertFalse(known_consequential_failure.replay_safe)
        self.assertFalse(known_consequential_failure.checkbox_advance_permitted)

        pending = self.oracle.resolve(
            TransitionInput(
                EffectClass.REPEATABLE_LOCAL,
                ApprovalState.PENDING,
                ExecutionState.NOT_STARTED,
                attempt_count=0,
            )
        )
        self.assertEqual(TransitionAction.RETAIN_WAITING_CHILD, pending.action)
        self.assertEqual(0, pending.attempt_count)
        for approval_state in (ApprovalState.DENIED, ApprovalState.REJECTED):
            result = self.oracle.resolve(
                TransitionInput(
                    EffectClass.REPEATABLE_LOCAL,
                    approval_state,
                    ExecutionState.NOT_STARTED,
                    attempt_count=0,
                )
            )
            with self.subTest(approval_state=approval_state):
                self.assertEqual(TransitionAction.STOP_UNCHECKED, result.action)
                self.assertFalse(result.checkbox_advance_permitted)

        for event in (
            TransitionInput(EffectClass.PROHIBITED, ApprovalState.APPROVED, ExecutionState.NOT_STARTED, 0),
            TransitionInput(EffectClass.REPEATABLE_LOCAL, ApprovalState.APPROVED, ExecutionState.TERMINAL_FAILURE, 1, unexpected_effect=True),
            TransitionInput(EffectClass.REPEATABLE_LOCAL, ApprovalState.APPROVED, ExecutionState.TERMINAL_FAILURE, 1, material_scope_change=True),
            TransitionInput(EffectClass.REPEATABLE_LOCAL, ApprovalState.APPROVED, ExecutionState.TERMINAL_FAILURE, 4),
        ):
            result = self.oracle.resolve(event)
            with self.subTest(event=event):
                self.assertIn(result.action, {TransitionAction.STOP_UNCHECKED, TransitionAction.INVALID_INPUT_STOP})
                self.assertFalse(result.checkbox_advance_permitted)

        unreconciled_success = self.oracle.resolve(
            TransitionInput(EffectClass.REPEATABLE_LOCAL, ApprovalState.APPROVED, ExecutionState.TERMINAL_SUCCESS, 1)
        )
        reconciled_success = self.oracle.resolve(
            TransitionInput(
                EffectClass.REPEATABLE_LOCAL,
                ApprovalState.APPROVED,
                ExecutionState.TERMINAL_SUCCESS,
                1,
                reconciled_terminal_success=True,
            )
        )
        self.assertFalse(unreconciled_success.checkbox_advance_permitted)
        self.assertTrue(reconciled_success.checkbox_advance_permitted)


if __name__ == "__main__":
    unittest.main()
