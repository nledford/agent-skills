#!/usr/bin/env python3

from __future__ import annotations

import fcntl
import json
import os
import re
import stat
from dataclasses import dataclass, field as dataclass_field
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Callable, Mapping

try:
    from .opencode_contracts import (
        GLOBAL_CONFIG_ROOT,
        DEFINITION_ROOT_NAME,
        MANIFEST_NAME,
        DEFINITION_KINDS,
        INSTALL_KINDS,
        DEFINITION_NAME_RE,
        SUPPORT_FILE_RE,
        MODEL_VALUE_RE,
        AGENT_ID_RE,
        REQUIRED_AGENT_FIELDS,
        REASONING_EFFORTS,
        ROOT_ASK_AGENT_IDS,
        TECHNICAL_RESEARCHER_MCP_TOOL_PATTERNS,
        LEGACY_PLAN_PATH_EDIT_RULE,
        PLAN_PATH_EDIT_RULE,
        LEGACY_PLAN_REDIRECTION_DENY_RULE,
        PLAN_REDIRECTION_DENY_RULE,
        STATE_PATH_EDIT_RULE,
        STATE_REDIRECTION_DENY_RULE,
        NON_PLAN_WRITER_EDIT_RULES,
        SANITIZED_EVIDENCE_INVARIANT,
        EXTERNAL_DIRECTORY_SCOPE_INVARIANT,
        TECHNICAL_RESEARCHER_EXTERNAL_EGRESS_INVARIANT,
        CanonicalAgentPolicy,
        CANONICAL_AGENT_TOPOLOGY,
        EXTERNAL_DIRECTORY_ASK_AGENT_IDS,
        STANDARD_CRITIC_AGENT_IDS,
        STANDARD_CRITIC_REQUIRED_HEADINGS,
        STANDARD_CRITIC_REQUIRED_SEMANTICS,
        CANONICAL_PROMPT_SECTION_CONTRACTS,
        TECHNICAL_DEBT_AUDIT_PROMPT_CONTRACTS,
        PROJECT_NEUTRAL_EXACT_JUST_RECIPES,
        ADVERSARIAL_REVIEWER_STAGE_PROMPT_CONTRACTS,
        CODE_DOCUMENTATION_PROMPT_CONTRACTS,
        MCP_SELECTION_PROMPT_CONTRACTS,
        PRIMARY_AGENT_TURN_PROMPT_CONTRACTS,
        BOARD_PLAN_REVIEW_PROMPT_CONTRACT,
        ACTIVE_WORKFLOW_FIXED_FILES,
        RETIRED_COMMAND_ID_TOKENS,
        RETIRED_LIFECYCLE_PHRASES,
        HUMAN_CONTROLLED_LIFECYCLE_DOC_TOKENS,
        EXTERNAL_DIRECTORY_DOC_TOKENS,
        HUMAN_CONTROLLED_LIFECYCLE_FORBIDDEN_TOKENS,
        COMMAND_PROMPT_CONTRACTS,
        RETAINED_ROUTE_CONTRACTS,
        RETAINED_ROUTE_FORBIDDEN_TOKENS,
        AUTOMATIC_PLAN_ROUTE_FORBIDDEN_TOKENS,
        PLAN_ORCHESTRATOR_BASH_RULES,
        PLAN_ORCHESTRATOR_COMMIT_PROMPT_REQUIREMENTS,
        ENGINEERING_LEAD_PLAN_STAGING_PROMPT_REQUIREMENTS,
        KNOWN_PERMISSION_TOOLS,
        SAFE_EXACT_GIT_BASH_ALLOWS,
        ENGINEERING_LEAD_PLAN_STAGING_BASH_RULES,
        ENGINEERING_LEAD_POST_PLAN_BASH_RULES,
        ENGINEERING_LEAD_GIT_BASH_RULES,
        ENGINEERING_LEAD_GIT_EFFECTIVE_ACTIONS,
        MCP_TOOL_ACTIONS_BY_AGENT,
        MCP_ENABLED_AGENT_IDS,
        NAVIGATION_TOOLS,
        ALL_FIRST_PARTY_SKILL_IDS,
        CANONICAL_AGENT_SKILL_IDS,
        CANONICAL_PERMISSION_PROFILES,
        canonical_agent_permissions,
        WORKER_DENY_COMMANDS,
        REQUIRED_SUPPORT_FILES,
        PLAN_TEMPLATE_TOKENS,
        PLAN_PATH_TOKENS,
        PLAN_TEMPLATE_HEADINGS,
        LEAN_PLAN_TEMPLATE,
    )
    from .opencode_frontmatter import ParsedFrontmatter, parse_frontmatter
    from .opencode_validation import (
        PromptContract,
        prompt_satisfies_contract,
    )
    from .project_neutrality import project_neutrality_errors
    from .skills_manager import SkillRegistry
except ImportError:  # Direct script execution.
    from opencode_contracts import (
        GLOBAL_CONFIG_ROOT,
        DEFINITION_ROOT_NAME,
        MANIFEST_NAME,
        DEFINITION_KINDS,
        INSTALL_KINDS,
        DEFINITION_NAME_RE,
        SUPPORT_FILE_RE,
        MODEL_VALUE_RE,
        AGENT_ID_RE,
        REQUIRED_AGENT_FIELDS,
        REASONING_EFFORTS,
        ROOT_ASK_AGENT_IDS,
        TECHNICAL_RESEARCHER_MCP_TOOL_PATTERNS,
        LEGACY_PLAN_PATH_EDIT_RULE,
        PLAN_PATH_EDIT_RULE,
        LEGACY_PLAN_REDIRECTION_DENY_RULE,
        PLAN_REDIRECTION_DENY_RULE,
        STATE_PATH_EDIT_RULE,
        STATE_REDIRECTION_DENY_RULE,
        NON_PLAN_WRITER_EDIT_RULES,
        SANITIZED_EVIDENCE_INVARIANT,
        EXTERNAL_DIRECTORY_SCOPE_INVARIANT,
        TECHNICAL_RESEARCHER_EXTERNAL_EGRESS_INVARIANT,
        CanonicalAgentPolicy,
        CANONICAL_AGENT_TOPOLOGY,
        EXTERNAL_DIRECTORY_ASK_AGENT_IDS,
        STANDARD_CRITIC_AGENT_IDS,
        STANDARD_CRITIC_REQUIRED_HEADINGS,
        STANDARD_CRITIC_REQUIRED_SEMANTICS,
        CANONICAL_PROMPT_SECTION_CONTRACTS,
        TECHNICAL_DEBT_AUDIT_PROMPT_CONTRACTS,
        PROJECT_NEUTRAL_EXACT_JUST_RECIPES,
        ADVERSARIAL_REVIEWER_STAGE_PROMPT_CONTRACTS,
        CODE_DOCUMENTATION_PROMPT_CONTRACTS,
        MCP_SELECTION_PROMPT_CONTRACTS,
        PRIMARY_AGENT_TURN_PROMPT_CONTRACTS,
        BOARD_PLAN_REVIEW_PROMPT_CONTRACT,
        ACTIVE_WORKFLOW_FIXED_FILES,
        RETIRED_COMMAND_ID_TOKENS,
        RETIRED_LIFECYCLE_PHRASES,
        HUMAN_CONTROLLED_LIFECYCLE_DOC_TOKENS,
        EXTERNAL_DIRECTORY_DOC_TOKENS,
        HUMAN_CONTROLLED_LIFECYCLE_FORBIDDEN_TOKENS,
        COMMAND_PROMPT_CONTRACTS,
        RETAINED_ROUTE_CONTRACTS,
        RETAINED_ROUTE_FORBIDDEN_TOKENS,
        AUTOMATIC_PLAN_ROUTE_FORBIDDEN_TOKENS,
        PLAN_ORCHESTRATOR_BASH_RULES,
        PLAN_ORCHESTRATOR_COMMIT_PROMPT_REQUIREMENTS,
        ENGINEERING_LEAD_PLAN_STAGING_PROMPT_REQUIREMENTS,
        KNOWN_PERMISSION_TOOLS,
        SAFE_EXACT_GIT_BASH_ALLOWS,
        ENGINEERING_LEAD_PLAN_STAGING_BASH_RULES,
        ENGINEERING_LEAD_POST_PLAN_BASH_RULES,
        ENGINEERING_LEAD_GIT_BASH_RULES,
        ENGINEERING_LEAD_GIT_EFFECTIVE_ACTIONS,
        MCP_TOOL_ACTIONS_BY_AGENT,
        MCP_ENABLED_AGENT_IDS,
        NAVIGATION_TOOLS,
        ALL_FIRST_PARTY_SKILL_IDS,
        CANONICAL_AGENT_SKILL_IDS,
        CANONICAL_PERMISSION_PROFILES,
        canonical_agent_permissions,
        WORKER_DENY_COMMANDS,
        REQUIRED_SUPPORT_FILES,
        PLAN_TEMPLATE_TOKENS,
        PLAN_PATH_TOKENS,
        PLAN_TEMPLATE_HEADINGS,
        LEAN_PLAN_TEMPLATE,
    )
    from opencode_frontmatter import ParsedFrontmatter, parse_frontmatter
    from opencode_validation import (
        PromptContract,
        prompt_satisfies_contract,
    )
    from project_neutrality import project_neutrality_errors
    from skills_manager import SkillRegistry


@lru_cache(maxsize=1024)
def _compile_opencode_wildcard(normalized_pattern: str) -> re.Pattern[str]:
    """Compile one normalized OpenCode wildcard pattern for repeated policy checks."""
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
    return re.compile(escaped_pattern, flags=flags)


def opencode_wildcard_match(value: str, pattern: str) -> bool:
    """Match the OpenCode 1.18.1 simple wildcard language."""
    normalized_value = value.replace("\\", "/")
    normalized_pattern = pattern.replace("\\", "/")
    return _compile_opencode_wildcard(normalized_pattern).fullmatch(normalized_value) is not None


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

    def for_kind(self, kind: str) -> tuple[str, ...]:
        return getattr(self, kind)


@dataclass(frozen=True)
class LoadedDefinition:
    kind: str
    name: str
    text: str | None
    parsed: ParsedFrontmatter | None


@dataclass(frozen=True)
class DefinitionSnapshot:
    """One immutable view of all manifested agent and command definitions."""

    inventory: DefinitionInventory
    definitions: Mapping[tuple[str, str], LoadedDefinition]

    @classmethod
    def create(
        cls,
        inventory: DefinitionInventory,
        definitions: dict[tuple[str, str], LoadedDefinition],
    ) -> DefinitionSnapshot:
        return cls(inventory, MappingProxyType(definitions.copy()))

    def for_kind(self, kind: str) -> tuple[LoadedDefinition, ...]:
        return tuple(
            definition
            for name in self.inventory.for_kind(kind)
            if (definition := self.definitions.get((kind, name))) is not None
        )

    def get(self, kind: str, name: str) -> LoadedDefinition | None:
        return self.definitions.get((kind, name))


@dataclass
class OperationResult:
    messages: list[str] = dataclass_field(default_factory=list)
    errors: list[str] = dataclass_field(default_factory=list)
    warnings: list[str] = dataclass_field(default_factory=list)

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
        self.mutation_hook = mutation_hook

    def validate(self) -> OperationResult:
        inventory, errors = self._load_inventory()
        if inventory is None:
            return OperationResult(errors=errors)
        canonical_active_workflow = self._has_canonical_active_workflow_inventory(inventory)
        agent_metadata: dict[str, tuple[str, tuple[tuple[str, str], ...]]] = {}

        errors.extend(self._validate_support_files(inventory.support_files))
        definitions, definition_errors = self._load_definition_snapshot(inventory)
        errors.extend(definition_errors)
        errors.extend(self._validate_project_neutrality(definitions))

        if canonical_active_workflow:
            agent_metadata = self._agent_metadata(definitions)
            errors.extend(self._validate_task_delegation(agent_metadata))
            errors.extend(self._validate_canonical_agent_topology(inventory, agent_metadata))
            errors.extend(self._validate_canonical_permission_profiles(definitions))
            errors.extend(self._validate_canonical_skill_catalogs())

        if not errors:
            if not canonical_active_workflow:
                agent_metadata = self._agent_metadata(definitions)
                errors.extend(self._validate_task_delegation(agent_metadata))
            errors.extend(
                self._validate_command_agents(
                    definitions,
                    agent_metadata,
                    canonical_active_workflow=canonical_active_workflow,
                )
            )
            errors.extend(self._validate_prompt_contracts(definitions))
        if canonical_active_workflow:
            errors.extend(self._validate_retired_lifecycle_tokens(definitions))
            errors.extend(self._validate_human_controlled_lifecycle_docs())
            errors.extend(self._validate_external_directory_docs())

        if errors:
            return OperationResult(errors=errors)

        return OperationResult(
            messages=[
                "OpenCode definitions are valid: "
                f"agents={len(inventory.agents)} commands={len(inventory.commands)}"
            ]
        )

    def _validate_project_neutrality(
        self,
        definitions: DefinitionSnapshot,
    ) -> list[str]:
        errors: list[str] = []
        for kind in DEFINITION_KINDS:
            for definition in definitions.for_kind(kind):
                if definition.text is None:
                    continue
                errors.extend(
                    project_neutrality_errors(
                        definition.text,
                        location=f"opencode/{kind}/{definition.name}",
                    )
                )
                if kind != "agents" or definition.parsed is None:
                    continue
                bash_rules = definition.parsed.permissions.get("bash")
                if not isinstance(bash_rules, tuple):
                    continue
                for pattern, _ in bash_rules:
                    if (
                        pattern.startswith("just ")
                        and not pattern.removeprefix("just ").startswith("-")
                        and "*" not in pattern
                        and pattern
                        not in PROJECT_NEUTRAL_EXACT_JUST_RECIPES.get(
                            definition.name, frozenset()
                        )
                    ):
                        errors.append(
                            f"agents: '{definition.name}' Bash permission names concrete "
                            f"project-defined Just recipe '{pattern}'; use 'just *' "
                            "and discover target-repository recipes at runtime"
                        )
        return errors

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
            return OperationResult(messages=["OpenCode managed symlinks are configured", f"Visible OpenCode definitions: agents={len(inventory.agents)} commands={len(inventory.commands)}"])
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

    def _has_canonical_active_workflow_inventory(
        self, inventory: DefinitionInventory
    ) -> bool:
        canonical_commands = set(CANONICAL_AGENT_TOPOLOGY.command_filenames)
        if set(inventory.commands) & canonical_commands:
            return True
        return all(
            not (self.repo_root / relative_path).is_symlink()
            and (self.repo_root / relative_path).is_file()
            for relative_path in ACTIVE_WORKFLOW_FIXED_FILES
        )

    def _validate_canonical_skill_catalogs(self) -> list[str]:
        skill_root = self.repo_root / "skills"
        if not skill_root.is_dir():
            return []
        registry = SkillRegistry.load(self.repo_root)
        actual_first_party = {skill.name for skill in registry.first_party()}
        declared_first_party: set[str] = set(ALL_FIRST_PARTY_SKILL_IDS)
        errors = [
            f"canonical OpenCode skill catalog omits first-party skill: {name}"
            for name in sorted(actual_first_party - declared_first_party)
        ]
        errors.extend(
            f"canonical OpenCode skill catalog lists non-first-party skill: {name}"
            for name in sorted(declared_first_party - actual_first_party)
        )
        expected_agents = {policy.agent_id for policy in CANONICAL_AGENT_TOPOLOGY.agents}
        actual_agents = set(CANONICAL_AGENT_SKILL_IDS)
        errors.extend(
            f"canonical OpenCode skill catalog missing agent: {name}"
            for name in sorted(expected_agents - actual_agents)
        )
        errors.extend(
            f"canonical OpenCode skill catalog lists unknown agent: {name}"
            for name in sorted(actual_agents - expected_agents)
        )
        for agent_id, skill_ids in CANONICAL_AGENT_SKILL_IDS.items():
            if len(skill_ids) != len(set(skill_ids)):
                errors.append(
                    f"canonical OpenCode skill catalog for {agent_id} contains duplicates"
                )
            errors.extend(
                f"canonical OpenCode skill catalog for {agent_id} lists "
                f"non-first-party skill: {skill_id}"
                for skill_id in sorted(set(skill_ids) - declared_first_party)
            )
        return errors

    @staticmethod
    def _validate_canonical_agent_topology(
        inventory: DefinitionInventory,
        agent_metadata: dict[str, tuple[str, tuple[tuple[str, str], ...]]],
    ) -> list[str]:
        errors: list[str] = []
        if inventory.agents != CANONICAL_AGENT_TOPOLOGY.agent_filenames:
            errors.append(
                "OpenCode manifest agent inventory diverges from canonical active workflow agent topology"
            )
        for policy in CANONICAL_AGENT_TOPOLOGY.agents:
            actual = agent_metadata.get(policy.agent_id)
            if actual is None:
                continue
            mode, task_rules = actual
            if mode != policy.mode:
                errors.append(
                    f"agents: '{policy.agent_id}.md' must use canonical mode '{policy.mode}'"
                )
            task_targets = tuple(target for target, _ in task_rules if target != "*")
            if task_targets != policy.task_targets:
                errors.append(
                    f"agents: '{policy.agent_id}.md' violates the canonical Task graph"
                )
        return errors

    def _validate_canonical_permission_profiles(
        self,
        definitions: DefinitionSnapshot,
    ) -> list[str]:
        errors: list[str] = []
        assigned_profiles = {
            policy.permission_profile for policy in CANONICAL_AGENT_TOPOLOGY.agents
        }
        if assigned_profiles != set(CANONICAL_PERMISSION_PROFILES):
            errors.append("canonical permission profile assignments are incomplete")
            return errors

        for policy in CANONICAL_AGENT_TOPOLOGY.agents:
            profile = CANONICAL_PERMISSION_PROFILES.get(policy.permission_profile)
            if profile is None:
                errors.append(
                    f"agents: '{policy.agent_id}.md' has an unknown canonical permission profile"
                )
                continue
            definition = definitions.get("agents", f"{policy.agent_id}.md")
            if definition is None or definition.parsed is None:
                continue
            parsed = definition.parsed
            expected_permissions = canonical_agent_permissions(policy)
            if parsed.permissions != expected_permissions:
                errors.append(
                    f"agents: '{policy.agent_id}.md' violates canonical "
                    f"'{profile.name}' permission profile"
                )
            errors.extend(self._canonical_navigation_errors(policy, parsed))
            errors.extend(self._canonical_bash_errors(policy, parsed))
        return errors

    @staticmethod
    def _canonical_navigation_errors(
        policy: CanonicalAgentPolicy,
        parsed: ParsedFrontmatter,
    ) -> list[str]:
        expected_state_action = (
            "allow" if policy.agent_id == "plan-orchestrator" else "deny"
        )
        for tool in NAVIGATION_TOOLS:
            rules = parsed.permissions.get(tool)
            if not isinstance(rules, tuple):
                break
            source_action = resolve_opencode_permission_action(
                rules,
                "src/example.py",
                baseline="deny",
            )
            state_action = resolve_opencode_permission_action(
                rules,
                STATE_PATH_EDIT_RULE,
                baseline="deny",
            )
            if source_action != "allow" or state_action != expected_state_action:
                break
        else:
            return []
        return [
            f"agents: '{policy.agent_id}.md' must preserve plan-state navigation isolation"
        ]

    @staticmethod
    def _canonical_bash_errors(
        policy: CanonicalAgentPolicy,
        parsed: ParsedFrontmatter,
    ) -> list[str]:
        bash = parsed.permissions.get("bash")
        if not isinstance(bash, tuple):
            return [
                f"agents: '{policy.agent_id}.md' must use a canonical Bash rule map"
            ]
        worker_deny_drift = policy.agent_id == "implementation-worker" and any(
            resolve_opencode_permission_action(bash, command, baseline="ask")
            != "deny"
            for command in WORKER_DENY_COMMANDS
        )
        if worker_deny_drift:
            return [
                "agents: 'implementation-worker.md' must preserve the complete Worker deny surface"
            ]
        return []

    def _validate_retired_lifecycle_tokens(
        self,
        definitions: DefinitionSnapshot,
    ) -> list[str]:
        inventory = definitions.inventory
        relative_paths = (
            *ACTIVE_WORKFLOW_FIXED_FILES,
            *(f"opencode/agents/{name}" for name in inventory.agents),
            *(f"opencode/commands/{name}" for name in inventory.commands),
            *(f"opencode/{name}" for name in inventory.support_files),
        )
        errors: list[str] = []
        for relative_path in relative_paths:
            text = self._read_active_workflow_inventory_text(
                relative_path,
                definitions=definitions,
            )
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

    def _validate_human_controlled_lifecycle_docs(self) -> list[str]:
        """Require the checked-in human-controlled lifecycle documentation contract."""
        errors: list[str] = []
        for relative_path, required_tokens in HUMAN_CONTROLLED_LIFECYCLE_DOC_TOKENS.items():
            text = self._read_active_workflow_inventory_text(relative_path)
            if text is None:
                errors.append(
                    f"human-controlled lifecycle document '{relative_path}' is missing or is not a regular UTF-8 file"
                )
                continue
            if not prompt_satisfies_contract(
                text,
                PromptContract(required=required_tokens),
            ):
                errors.append(
                    f"human-controlled lifecycle document '{relative_path}' contract is incomplete"
                )
            if not prompt_satisfies_contract(
                text.lower(),
                PromptContract(forbidden=HUMAN_CONTROLLED_LIFECYCLE_FORBIDDEN_TOKENS),
            ):
                errors.append(
                    f"human-controlled lifecycle document '{relative_path}' contains forbidden automatic `/start-plan` creation"
                )
        return errors

    def _validate_external_directory_docs(self) -> list[str]:
        """Require the checked-in external-directory approval documentation."""
        errors: list[str] = []
        for relative_path, required_tokens in EXTERNAL_DIRECTORY_DOC_TOKENS.items():
            text = self._read_active_workflow_inventory_text(relative_path)
            if text is None:
                errors.append(
                    f"external-directory document '{relative_path}' is missing or is "
                    "not a regular UTF-8 file"
                )
                continue
            normalized = " ".join(text.split())
            if not all(token in normalized for token in required_tokens):
                errors.append(
                    f"external-directory document '{relative_path}' contract is incomplete"
                )
        return errors

    def _read_active_workflow_inventory_text(
        self,
        relative_path: str,
        *,
        definitions: DefinitionSnapshot | None = None,
    ) -> str | None:
        definition_parts = Path(relative_path).parts
        if (
            definitions is not None
            and len(definition_parts) == 3
            and definition_parts[0] == DEFINITION_ROOT_NAME
            and definition_parts[1] in DEFINITION_KINDS
        ):
            definition = definitions.get(definition_parts[1], definition_parts[2])
            return definition.text if definition is not None else None
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
        contents, errors = self._load_support_files(support_files)
        if errors:
            return errors
        return [
            *self._validate_plan_support_contents(contents),
            *self._validate_root_plan_copies(),
        ]

    def _load_support_files(
        self,
        support_files: tuple[str, ...],
    ) -> tuple[dict[str, str], list[str]]:
        contents: dict[str, str] = {}
        errors: list[str] = []
        for relative_path in support_files:
            path = self._safe_support_file(relative_path)
            if path is None:
                errors.append("support file is missing or is not a regular file")
                continue
            try:
                contents[relative_path] = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                errors.append("support file is not readable UTF-8")
        return contents, errors

    def _safe_support_file(self, relative_path: str) -> Path | None:
        path = self.definition_root
        for part in Path(relative_path).parts:
            path /= part
            if path.is_symlink():
                return None
        return path if path.is_file() else None

    @staticmethod
    def _validate_plan_support_contents(contents: Mapping[str, str]) -> list[str]:
        template = contents["project-template/docs/implementation-plans/TEMPLATE.md"]
        headings = tuple(
            line for line in template.splitlines() if line.startswith("#")
        )
        errors: list[str] = []
        if (
            template != LEAN_PLAN_TEMPLATE
            or not all(token in template for token in PLAN_TEMPLATE_TOKENS)
            or headings != PLAN_TEMPLATE_HEADINGS
        ):
            errors.append("implementation plan template is not the canonical lean format")
        path_documents = (
            "project-template/AGENTS-plan-workflow-snippet.md",
            "project-template/docs/implementation-plans/README.md",
        )
        if any(
            not all(token in contents[path] for token in PLAN_PATH_TOKENS)
            for path in path_documents
        ):
            errors.append("implementation plan support path token is missing")
        return errors

    def _validate_root_plan_copies(self) -> list[str]:
        errors: list[str] = []
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
                errors.append(
                    "root implementation plan file is missing or is not a regular file"
                )
                continue
            try:
                if root_copy.read_bytes() != template_copy.read_bytes():
                    errors.append(
                        "root implementation plan files differ from project-template copies"
                    )
            except OSError:
                errors.append("root implementation plan file is not readable")
        return errors


        return errors
    def _load_definition_snapshot(
        self,
        inventory: DefinitionInventory,
    ) -> tuple[DefinitionSnapshot, list[str]]:
        definitions: dict[tuple[str, str], LoadedDefinition] = {}
        errors: list[str] = []
        for kind in DEFINITION_KINDS:
            expected = inventory.for_kind(kind)
            errors.extend(self._definition_directory_errors(kind, expected))
            for name in expected:
                loaded, load_errors = self._load_definition(kind, name)
                definitions[(kind, name)] = loaded
                errors.extend(load_errors)
        return DefinitionSnapshot.create(inventory, definitions), errors

    def _definition_directory_errors(
        self,
        kind: str,
        expected: tuple[str, ...],
    ) -> list[str]:
        root = self.sources[kind]
        if root.is_symlink() or not root.is_dir():
            return [f"{kind} source is missing or is not a regular directory"]
        try:
            observed = {path.name for path in root.iterdir()}
        except OSError:
            return [f"{kind} source directory is not readable"]
        expected_names = set(expected)
        return [
            *(
                f"{kind}: unexpected asset '{name}'"
                for name in sorted(observed - expected_names)
            ),
            *(
                f"{kind}: manifest asset missing '{name}'"
                for name in sorted(expected_names - observed)
            ),
        ]

    def _load_definition(
        self,
        kind: str,
        name: str,
    ) -> tuple[LoadedDefinition, list[str]]:
        path = self.sources[kind] / name
        if path.is_symlink() or not path.is_file():
            return (
                LoadedDefinition(kind, name, None, None),
                [f"{kind}: '{name}' must be a regular non-symlink file"],
            )
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            return (
                LoadedDefinition(kind, name, None, None),
                [f"{kind}: '{name}' is not readable UTF-8"],
            )
        parsed, errors = parse_frontmatter(kind, name, text)
        if parsed is not None:
            validator = (
                self._validate_agent_frontmatter
                if kind == "agents"
                else self._validate_command_frontmatter
            )
            errors.extend(validator(name, parsed))
        return LoadedDefinition(kind, name, text, parsed), errors


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
        if not parsed.permissions:
            errors.append(f"agents: '{name}' must define a permission block")
            return errors
        if "task" not in parsed.permissions:
            errors.append(f"agents: '{name}' permission block must define task")
            return errors
        expected_baseline = "ask" if agent_id in ROOT_ASK_AGENT_IDS else "deny"
        errors.extend(
            OpenCodeInstallService._permission_baseline_errors(
                name,
                parsed.permissions,
                expected_baseline,
            )
        )
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
            )
        )
        return errors

    @staticmethod
    def _permission_baseline_errors(
        name: str,
        permissions: Mapping[
            str,
            str | tuple[tuple[str, str], ...],
        ],
        expected_baseline: str,
    ) -> list[str]:
        errors: list[str] = []
        permission_items = tuple(permissions.items())
        if not permission_items or permission_items[0][0] != "*":
            errors.append(f"agents: '{name}' permission wildcard baseline must be first")
        elif permission_items[0][1] != expected_baseline:
            errors.append(
                f"agents: '{name}' permission wildcard baseline must be {expected_baseline}"
            )
        for level, value in permissions.items():
            errors.extend(
                OpenCodeInstallService._permission_rule_baseline_errors(
                    name,
                    level,
                    value,
                )
            )
        return errors

    @staticmethod
    def _permission_rule_baseline_errors(
        name: str,
        level: str,
        value: str | tuple[tuple[str, str], ...],
    ) -> list[str]:
        if isinstance(value, str):
            if level == "task" and value != "deny":
                return [f"agents: '{name}' task permission must deny by default"]
            return []
        if not value or value[0][0] != "*":
            return [
                f"agents: '{name}' permission '{level}' must put its wildcard baseline first"
            ]
        if level == "task" and value[0][1] != "deny":
            return [f"agents: '{name}' task permission must deny by default"]
        return []

    @staticmethod
    def _validate_capability_schema(
        name: str,
        agent_id: str,
        permissions: dict[str, str | tuple[tuple[str, str], ...]],
        baseline: str,
    ) -> list[str]:
        errors = OpenCodeInstallService._unsupported_tool_errors(
            name,
            agent_id,
            permissions,
        )
        errors.extend(
            OpenCodeInstallService._external_directory_permission_errors(
                name,
                permissions.get("external_directory"),
            )
        )
        bash = permissions.get("bash")
        errors.extend(
            OpenCodeInstallService._bash_schema_errors(
                name,
                agent_id,
                bash,
                baseline,
            )
        )
        errors.extend(
            OpenCodeInstallService._role_bash_contract_errors(
                name,
                agent_id,
                bash,
            )
        )
        errors.extend(
            OpenCodeInstallService._navigation_and_todo_errors(
                name,
                agent_id,
                permissions,
            )
        )
        errors.extend(
            OpenCodeInstallService._network_permission_errors(
                name,
                agent_id,
                permissions,
            )
        )
        errors.extend(
            OpenCodeInstallService._mcp_permission_errors(
                name,
                agent_id,
                permissions,
            )
        )
        return errors

    @staticmethod
    def _unsupported_tool_errors(
        name: str,
        agent_id: str,
        permissions: Mapping[str, object],
    ) -> list[str]:
        allowed_tools = set(KNOWN_PERMISSION_TOOLS)
        if agent_id in MCP_ENABLED_AGENT_IDS:
            allowed_tools.update(MCP_TOOL_ACTIONS_BY_AGENT[agent_id])
        if agent_id == "technical-researcher":
            allowed_tools.update(TECHNICAL_RESEARCHER_MCP_TOOL_PATTERNS)
        if set(permissions) - allowed_tools:
            return [f"agents: '{name}' has unsupported permission tool"]
        return []

    @staticmethod
    def _external_directory_permission_errors(
        name: str,
        permission: str | tuple[tuple[str, str], ...] | None,
    ) -> list[str]:
        allows_access = permission == "allow" or (
            isinstance(permission, tuple)
            and any(action == "allow" for _, action in permission)
        )
        if not allows_access:
            return []
        return [
            f"agents: '{name}' external_directory permission must require "
            "approval or deny access"
        ]

    @staticmethod
    def _bash_schema_errors(
        name: str,
        agent_id: str,
        bash: str | tuple[tuple[str, str], ...] | None,
        baseline: str,
    ) -> list[str]:
        if bash == "allow":
            return [f"agents: '{name}' bash permission must be a rule map"]
        if baseline == "deny" and isinstance(bash, str) and bash != "deny":
            return [f"agents: '{name}' bash permission must be deny or a rule map"]
        if agent_id in ROOT_ASK_AGENT_IDS and isinstance(bash, str):
            return [f"agents: '{name}' bash permission must be a rule map"]
        if not isinstance(bash, tuple):
            return []
        for rule, action in bash:
            error = OpenCodeInstallService._bash_rule_error(agent_id, rule, action)
            if error is not None:
                return [f"agents: '{name}' {error}"]
        return []

    @staticmethod
    def _bash_rule_error(
        agent_id: str,
        rule: str,
        action: str,
    ) -> str | None:
        if action != "allow":
            return None
        has_wildcard = any(marker in rule for marker in "*?[")
        lead_exception = agent_id == "engineering-lead" and (
            (rule, action) in ENGINEERING_LEAD_GIT_BASH_RULES
            or (rule, action) in ENGINEERING_LEAD_POST_PLAN_BASH_RULES
        )
        if has_wildcard:
            return None if lead_exception else "bash permission must not allow wildcard rules"
        safe_role_rule = (
            rule in SAFE_EXACT_GIT_BASH_ALLOWS
            or (agent_id == "plan-orchestrator" and rule == "git commit")
            or (
                agent_id == "engineering-lead"
                and (rule, action) in ENGINEERING_LEAD_GIT_BASH_RULES
            )
        )
        return None if safe_role_rule else "bash permission has an unsafe allow rule"

    @staticmethod
    def _role_bash_contract_errors(
        name: str,
        agent_id: str,
        bash: str | tuple[tuple[str, str], ...] | None,
    ) -> list[str]:
        if agent_id == "plan-orchestrator":
            if not isinstance(bash, tuple) or bash != PLAN_ORCHESTRATOR_BASH_RULES:
                return [f"agents: '{name}' must preserve canonical Git permissions"]
            return []
        if agent_id == "engineering-lead":
            return OpenCodeInstallService._lead_git_permission_errors(name, bash)
        return []

    @staticmethod
    def _lead_git_permission_errors(
        name: str,
        bash: str | tuple[tuple[str, str], ...] | None,
    ) -> list[str]:
        rules = bash if isinstance(bash, tuple) else ()
        git_rules = tuple(rule for rule in rules if rule[0].startswith("git"))
        expected_git_rules = ENGINEERING_LEAD_GIT_BASH_RULES + tuple(
            rule
            for rule in ENGINEERING_LEAD_PLAN_STAGING_BASH_RULES
            if rule[0].startswith("git")
        )
        errors: list[str] = []
        if git_rules != expected_git_rules:
            errors.append(
                f"agents: '{name}' must preserve canonical git permissions"
            )
        if any(
            OpenCodeInstallService._is_noncanonical_lead_wildcard(pattern, action)
            for pattern, action in rules
        ):
            errors.append(
                f"agents: '{name}' has a noncanonical wildcard rule that can override git permissions"
            )
        if isinstance(bash, tuple) and any(
            resolve_opencode_permission_action(rules, command, baseline="ask")
            != expected
            for command, expected in ENGINEERING_LEAD_GIT_EFFECTIVE_ACTIONS
        ):
            errors.append(
                f"agents: '{name}' must preserve effective git permission actions"
            )
        return errors

    @staticmethod
    def _is_noncanonical_lead_wildcard(pattern: str, action: str) -> bool:
        if action not in {"allow", "ask"}:
            return False
        if (
            (pattern, action) in ENGINEERING_LEAD_GIT_BASH_RULES
            or (pattern, action) in ENGINEERING_LEAD_PLAN_STAGING_BASH_RULES
            or pattern
            in {"*", LEGACY_PLAN_REDIRECTION_DENY_RULE, PLAN_REDIRECTION_DENY_RULE}
        ):
            return False
        command_has_wildcard = pattern.startswith("g") and any(
            marker in pattern.split(" ", 1)[0] for marker in "*?["
        )
        return pattern.startswith(("*", "?", "[")) or command_has_wildcard

    @staticmethod
    def _navigation_and_todo_errors(
        name: str,
        agent_id: str,
        permissions: Mapping[str, object],
    ) -> list[str]:
        if agent_id == "plan-orchestrator":
            errors = (
                []
                if permissions.get("todowrite") == "allow"
                else [f"agents: '{name}' must allow todowrite"]
            )
            expected_navigation = (("*", "allow"),)
            if any(
                permissions.get(tool) != expected_navigation
                for tool in NAVIGATION_TOOLS
            ):
                errors.append(
                    f"agents: '{name}' must allow plan-state navigation"
                )
            return errors
        if agent_id == "implementation-worker":
            expected_navigation = (("*", "allow"), (STATE_PATH_EDIT_RULE, "deny"))
            if any(
                permissions.get(tool) != expected_navigation
                for tool in NAVIGATION_TOOLS
            ):
                return [f"agents: '{name}' must deny plan-state navigation"]
            return []
        if agent_id == "engineering-lead":
            if permissions.get("todowrite") != "allow":
                return [f"agents: '{name}' must allow todowrite"]
            return []
        if "todowrite" in permissions and permissions["todowrite"] != "deny":
            return [f"agents: '{name}' must not allow todowrite for this role"]
        return []

    @staticmethod
    def _network_permission_errors(
        name: str,
        agent_id: str,
        permissions: Mapping[str, object],
    ) -> list[str]:
        expected = (
            "ask"
            if agent_id in {"engineering-lead", "technical-researcher"}
            else "deny"
        )
        if any(permissions.get(tool) != expected for tool in ("webfetch", "websearch")):
            return [f"agents: '{name}' network permissions must be {expected}"]
        return []

    @staticmethod
    def _mcp_permission_errors(
        name: str,
        agent_id: str,
        permissions: Mapping[str, object],
    ) -> list[str]:
        errors: list[str] = []
        if agent_id in MCP_ENABLED_AGENT_IDS and any(
            permissions.get(pattern) != action
            for pattern, action in MCP_TOOL_ACTIONS_BY_AGENT[agent_id].items()
        ):
            errors.append(
                f"agents: '{name}' must preserve approval-gated MCP tool patterns"
            )
        if agent_id == "technical-researcher" and any(
            permissions.get(pattern) != "ask"
            for pattern in TECHNICAL_RESEARCHER_MCP_TOOL_PATTERNS
        ):
            errors.append(
                f"agents: '{name}' must ask before using approved research MCP tools"
            )
        return errors


    @staticmethod
    def _validate_core_permission_ownership(
        name: str,
        agent_id: str,
        permissions: dict[str, str | tuple[tuple[str, str], ...]],
    ) -> list[str]:
        edit = permissions.get("edit")
        expected_edit: str | tuple[tuple[str, str], ...]
        if agent_id in {"engineering-lead", "implementation-worker"}:
            expected_edit = NON_PLAN_WRITER_EDIT_RULES
        elif agent_id == "plan-orchestrator":
            expected_edit = (
                ("*", "ask"),
                (LEGACY_PLAN_PATH_EDIT_RULE, "deny"),
                (PLAN_PATH_EDIT_RULE, "ask"),
                (STATE_PATH_EDIT_RULE, "ask"),
            )
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
            if agent_id == "engineering-lead":
                permitted_suffixes = (
                    (
                        (PLAN_REDIRECTION_DENY_RULE, "deny"),
                        *ENGINEERING_LEAD_POST_PLAN_BASH_RULES,
                    ),
                )
            else:
                permitted_suffixes = (
                    (
                        (LEGACY_PLAN_REDIRECTION_DENY_RULE, "deny"),
                        (PLAN_REDIRECTION_DENY_RULE, "deny"),
                        (STATE_REDIRECTION_DENY_RULE, "deny"),
                    ),
                )
            if (
                not isinstance(bash, tuple)
                or not any(
                    len(bash) >= len(suffix) and bash[-len(suffix) :] == suffix
                    for suffix in permitted_suffixes
                )
            ):
                errors.append(
                    f"agents: '{name}' must preserve the plan redirection deny in its required bash suffix"
                )
        if agent_id == "implementation-worker" and (
            not isinstance(bash, tuple)
            or resolve_opencode_permission_action(
                bash, "git add -- src/example.py", baseline="ask"
            )
            != "deny"
            or resolve_opencode_permission_action(
                bash, "git commit", baseline="ask"
            )
            != "deny"
        ):
            errors.append(
                f"agents: '{name}' must deny staging and commit commands"
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
        definitions: DefinitionSnapshot | DefinitionInventory,
    ) -> dict[str, tuple[str, tuple[tuple[str, str], ...]]]:
        if isinstance(definitions, DefinitionInventory):
            definitions, _ = self._load_definition_snapshot(definitions)
        metadata: dict[str, tuple[str, tuple[tuple[str, str], ...]]] = {}
        for definition in definitions.for_kind("agents"):
            if definition.parsed is None:
                continue
            parsed = definition.parsed
            task_rules = parsed.permissions.get("task")
            metadata[Path(definition.name).stem] = (
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
        definitions: DefinitionSnapshot,
        agent_metadata: dict[str, tuple[str, tuple[tuple[str, str], ...]]],
        *,
        canonical_active_workflow: bool,
    ) -> list[str]:
        inventory = definitions.inventory
        primary_agents = {
            agent_id for agent_id, (mode, _) in agent_metadata.items() if mode == "primary"
        }
        all_agents = set(agent_metadata)
        errors: list[str] = []
        if (
            canonical_active_workflow
            and inventory.commands != CANONICAL_AGENT_TOPOLOGY.command_filenames
        ):
            errors.append("OpenCode manifest command inventory is not canonical")
        for definition in definitions.for_kind("commands"):
            name = definition.name
            if definition.parsed is None:
                errors.append(f"commands: '{name}' could not be revalidated")
                continue
            parsed = definition.parsed
            agent_id = parsed.fields.get("agent")
            if agent_id not in all_agents:
                errors.append(f"commands: '{name}' references unknown agent '{agent_id}'")
            elif agent_id not in primary_agents:
                errors.append(
                    f"commands: '{name}' must reference a manifested primary agent"
                )
            expected_owner = CANONICAL_AGENT_TOPOLOGY.command_owners.get(name)
            if expected_owner is not None and agent_id != expected_owner:
                errors.append(f"commands: '{name}' must use canonical primary owner")
        return errors
    def _validate_prompt_contracts(
        self,
        definitions: DefinitionSnapshot,
    ) -> list[str]:
        errors = self._validate_core_agent_prompt_contracts(definitions)
        section_groups = (
            (CANONICAL_PROMPT_SECTION_CONTRACTS, "prompt contract"),
            (TECHNICAL_DEBT_AUDIT_PROMPT_CONTRACTS, "prompt contract"),
            (CODE_DOCUMENTATION_PROMPT_CONTRACTS, "code-documentation prompt contract"),
            (MCP_SELECTION_PROMPT_CONTRACTS, "MCP-selection prompt contract"),
            (PRIMARY_AGENT_TURN_PROMPT_CONTRACTS, "primary-agent turn prompt contract"),
        )
        for contracts, label in section_groups:
            errors.extend(
                self._validate_agent_section_contracts(
                    definitions,
                    contracts,
                    label=label,
                )
            )
        errors.extend(self._validate_adversarial_stage_contracts(definitions))
        errors.extend(self._validate_board_plan_review_contract(definitions))
        if self._has_canonical_active_workflow_inventory(definitions.inventory):
            errors.extend(self._validate_canonical_prompt_invariants(definitions))
        errors.extend(self._validate_automatic_plan_route_tokens(definitions))
        errors.extend(self._validate_command_prompt_contracts(definitions))
        return errors

    def _validate_core_agent_prompt_contracts(
        self,
        definitions: DefinitionSnapshot,
    ) -> list[str]:
        contracts = {
            "engineering-lead.md": (
                "Use only `implementation-worker` for bounded implementation Tasks.",
                "When resuming the same Worker for a correction, send a complete actionable packet",
                "enumerate each evidence gap, the acceptance criterion it blocks",
                "Never send only a status preamble or references such as `these findings`",
            ),
            "plan-orchestrator.md": (
                "top-level primary agent, never a Task child",
                "native planned-work TODOs",
                "`.erb/plan-state.json`",
            ),
            "implementation-worker.md": (
                "Engineering Lead or Plan Orchestrator",
                "`.erb/plan-state.json`",
                "edit durable plan paths",
                "read or edit `.erb/plan-state.json`",
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
        selected = {"plan-orchestrator.md"} & set(definitions.inventory.agents)
        if set(contracts).issubset(definitions.inventory.agents):
            selected = set(contracts)
        errors: list[str] = []
        for name in selected:
            prompt = self._definition_text(definitions, "agents", name)
            if prompt is None:
                errors.append(f"agents: '{name}' prompt contract is unreadable")
                continue
            contract = PromptContract(required=contracts[name])
            if not prompt_satisfies_contract(prompt, contract):
                errors.append(f"agents: '{name}' prompt contract is incomplete")
                continue
            if name == "plan-orchestrator.md":
                errors.extend(self._validate_plan_orchestrator_prompt_contract(name, prompt))
        return errors

    def _validate_agent_section_contracts(
        self,
        definitions: DefinitionSnapshot,
        contracts: Mapping[str, tuple[str, tuple[str, ...]]],
        *,
        label: str,
    ) -> list[str]:
        if not set(contracts).issubset(definitions.inventory.agents):
            return []
        errors: list[str] = []
        for name, (heading, required) in contracts.items():
            prompt = self._definition_text(definitions, "agents", name)
            if prompt is None:
                errors.append(f"agents: '{name}' {label} is unreadable")
                continue
            contract = PromptContract(heading=heading, required=required)
            if not prompt_satisfies_contract(prompt, contract):
                errors.append(f"agents: '{name}' {label} is incomplete")
        return errors

    def _validate_adversarial_stage_contracts(
        self,
        definitions: DefinitionSnapshot,
    ) -> list[str]:
        contracts = ADVERSARIAL_REVIEWER_STAGE_PROMPT_CONTRACTS
        if not set(contracts).issubset(definitions.inventory.agents):
            return []
        errors: list[str] = []
        for name, stage_contracts in contracts.items():
            prompt = self._definition_text(definitions, "agents", name)
            if prompt is None:
                errors.append(
                    f"agents: '{name}' adversarial stage prompt contract is unreadable"
                )
                continue
            for heading, required in stage_contracts:
                contract = PromptContract(heading=heading, required=required)
                if not prompt_satisfies_contract(prompt, contract):
                    errors.append(
                        f"agents: '{name}' adversarial stage prompt contract is incomplete"
                    )
        return errors

    def _validate_board_plan_review_contract(
        self,
        definitions: DefinitionSnapshot,
    ) -> list[str]:
        name = "engineering-review-board.md"
        if name not in definitions.inventory.agents:
            return []
        prompt = self._definition_text(definitions, "agents", name)
        if prompt is None:
            return [
                f"agents: '{name}' Board plan-review prompt contract is unreadable"
            ]
        heading, required, forbidden = BOARD_PLAN_REVIEW_PROMPT_CONTRACT
        contract = PromptContract(
            heading=heading,
            required=required,
            forbidden=forbidden,
        )
        if prompt_satisfies_contract(prompt, contract):
            return []
        return [f"agents: '{name}' Board plan-review prompt contract is incomplete"]

    def _validate_canonical_prompt_invariants(
        self,
        definitions: DefinitionSnapshot,
    ) -> list[str]:
        errors = self._validate_agent_section_contracts(
            definitions,
            {
                "engineering-lead.md": (
                    "## Git Commit Policy",
                    ENGINEERING_LEAD_PLAN_STAGING_PROMPT_REQUIREMENTS,
                )
            },
            label="plan-staging prompt contract",
        )
        errors.extend(self._validate_exact_agent_invariants(definitions))
        errors.extend(self._validate_standard_critic_prompt_contracts(definitions))
        return errors

    def _validate_exact_agent_invariants(
        self,
        definitions: DefinitionSnapshot,
    ) -> list[str]:
        errors: list[str] = []
        for name in CANONICAL_AGENT_TOPOLOGY.agent_filenames:
            prompt = self._definition_text(definitions, "agents", name)
            if prompt is None:
                errors.append(
                    f"agents: '{name}' sanitized-evidence prompt contract is unreadable"
                )
                continue
            sanitized = PromptContract(
                exact_counts=((SANITIZED_EVIDENCE_INVARIANT, 1),)
            )
            if not prompt_satisfies_contract(prompt, sanitized):
                errors.append(
                    f"agents: '{name}' must contain exactly one sanitized-evidence prompt contract"
                )
            expected_count = (
                1 if Path(name).stem in EXTERNAL_DIRECTORY_ASK_AGENT_IDS else 0
            )
            external = PromptContract(
                exact_counts=((EXTERNAL_DIRECTORY_SCOPE_INVARIANT, expected_count),)
            )
            if not prompt_satisfies_contract(prompt, external):
                errors.append(
                    f"agents: '{name}' has an invalid external-directory prompt contract"
                )
        errors.extend(self._validate_researcher_egress_invariant(definitions))
        return errors

    def _validate_researcher_egress_invariant(
        self,
        definitions: DefinitionSnapshot,
    ) -> list[str]:
        name = "technical-researcher.md"
        prompt = self._definition_text(definitions, "agents", name)
        if prompt is None:
            return [
                f"agents: '{name}' external-egress prompt contract is unreadable"
            ]
        contract = PromptContract(
            exact_counts=((TECHNICAL_RESEARCHER_EXTERNAL_EGRESS_INVARIANT, 1),)
        )
        if prompt_satisfies_contract(prompt, contract):
            return []
        return [
            f"agents: '{name}' must contain exactly one external-egress prompt contract"
        ]

    @staticmethod
    def _definition_text(
        definitions: DefinitionSnapshot,
        kind: str,
        name: str,
    ) -> str | None:
        definition = definitions.get(kind, name)
        return definition.text if definition is not None else None

    def _validate_standard_critic_prompt_contracts(
        self,
        definitions: DefinitionSnapshot,
    ) -> list[str]:
        errors: list[str] = []
        contract = PromptContract(
            required=(
                *STANDARD_CRITIC_REQUIRED_HEADINGS,
                *STANDARD_CRITIC_REQUIRED_SEMANTICS,
            )
        )
        for agent_id in sorted(STANDARD_CRITIC_AGENT_IDS):
            name = f"{agent_id}.md"
            prompt = self._definition_text(definitions, "agents", name)
            if prompt is None:
                errors.append(
                    f"agents: '{name}' standard critic prompt contract is unreadable"
                )
            elif not prompt_satisfies_contract(prompt, contract):
                errors.append(
                    f"agents: '{name}' standard critic prompt contract is incomplete"
                )
        return errors

    def _validate_automatic_plan_route_tokens(
        self,
        definitions: DefinitionSnapshot,
    ) -> list[str]:
        """Reject active definition text that restores automatic plan routing."""
        errors: list[str] = []
        for kind in DEFINITION_KINDS:
            for definition in definitions.for_kind(kind):
                if definition.text is None:
                    errors.append(
                        f"{kind}: '{definition.name}' automatic plan-route contract is unreadable"
                    )
                    continue
                normalized = " ".join(definition.text.lower().split())
                if any(
                    token in normalized
                    for token in AUTOMATIC_PLAN_ROUTE_FORBIDDEN_TOKENS
                ):
                    errors.append(
                        f"{kind}: '{definition.name}' contains forbidden automatic plan routing"
                    )
        return errors

    def _validate_command_prompt_contracts(
        self,
        definitions: DefinitionSnapshot,
    ) -> list[str]:
        """Check checked-in command text only; runtime behavior is not inferred."""
        if not self._has_canonical_active_workflow_inventory(definitions.inventory):
            return []
        errors: list[str] = []
        for name, required in COMMAND_PROMPT_CONTRACTS.items():
            prompt = self._definition_text(definitions, "commands", name)
            if prompt is None:
                errors.append(f"commands: '{name}' prompt contract is unreadable")
            elif not prompt_satisfies_contract(
                prompt,
                PromptContract(required=required),
            ):
                errors.append(f"commands: '{name}' prompt contract is incomplete")
        errors.extend(self._validate_retained_route_contracts(definitions))
        return errors

    def _validate_retained_route_contracts(
        self,
        definitions: DefinitionSnapshot,
    ) -> list[str]:
        errors: list[str] = []
        for relative_path, required in RETAINED_ROUTE_CONTRACTS.items():
            prompt = self._retained_route_text(definitions, relative_path)
            if prompt is None:
                errors.append(f"OpenCode retained route '{relative_path}' is unreadable")
                continue
            contract = PromptContract(
                required=required,
                forbidden=RETAINED_ROUTE_FORBIDDEN_TOKENS.get(relative_path, ()),
            )
            if not prompt_satisfies_contract(prompt, contract):
                if not all(token in " ".join(prompt.split()) for token in required):
                    errors.append(
                        f"OpenCode retained route '{relative_path}' contract is incomplete"
                    )
                if any(
                    token in prompt
                    for token in RETAINED_ROUTE_FORBIDDEN_TOKENS.get(relative_path, ())
                ):
                    errors.append(
                        f"OpenCode retained route '{relative_path}' contains obsolete lifecycle routing"
                    )
        return errors

    def _retained_route_text(
        self,
        definitions: DefinitionSnapshot,
        relative_path: str,
    ) -> str | None:
        parts = Path(relative_path).parts
        if len(parts) == 2 and parts[0] in DEFINITION_KINDS:
            return self._definition_text(definitions, parts[0], parts[1])
        return self._read_active_workflow_inventory_text(
            f"{DEFINITION_ROOT_NAME}/{relative_path}"
        )


    @staticmethod
    def _validate_plan_orchestrator_prompt_contract(name: str, prompt: str) -> list[str]:
        required = (
            "Do not add frontmatter or any other heading, section, lifecycle field, history, provenance, review record, approval field, status, dependency field, or metadata.",
            "The lifecycle distinguishes read-only consultation, explicit plan-only creation, explicit active-plan updates, and execution.",
            "It must not execute newly created or updated plans automatically.",
            "Top-level `/consult-plan` is read-only Plan Orchestrator consultation.",
            "It performs no state read, mutation, delegation, implementation, staging, or commit and cannot authorize later work.",
            "`/create-plan` or an equally explicit current top-level human creation request may create a plan.",
            "Conversational plan creation requires equally explicit current human authorization, remains plan-only, and never triggers automatic execution.",
            "`/update-plan <exact-plan-path>` is explicit plan-only authority to update that one existing active canonical plan in place.",
            "It never infers its target from state, updates state, or executes work.",
            "A current top-level human request to split or replace one specific plan is explicit authority to retire that source after safe successor creation.",
            "Review or consultation advice alone is not mutation authority.",
            "The requested split must produce at least two separately managed successor plans.",
            "If successor creation or verification fails, do not delete the source.",
            "Immediately re-read the source and successors before retirement",
            "exact-content edit patch",
            "delete only the exact source plan",
            "No additional deletion confirmation is required",
            "`/start-plan` accepts only an explicit existing valid canonical lean plan path or a no-argument state pointer.",
            "`/start-plan` rejects free-form requests and immutable legacy inputs rather than creating a plan or successor.",
            "`.erb/plan-state.json`",
            '`{"plan_path":".erb/plans/<path>.md"}`',
            "Active means at least one unchecked TODO or Verification checkbox remains.",
            "The current step is the first unchecked checkbox in document order.",
            "This plan has already been implemented.",
            "An explicit valid path replaces missing, invalid, or stale state.",
            "Never block because another plan is selected or may be running.",
            "Replace the whole native TODO list on every update. Keep at most five entries and zero or one `in_progress` entry.",
            "Keep the window on plan TODOs, in their original order and with their original numbers, until every TODO is checked.",
            "Only then replace it with the dedicated Verification steps in their original order.",
            "On a transition, order entries as most-recent completed, then current, then pending.",
            "A blocked or failed step stays visible with its evidence and never advances a checkbox or window speculatively.",
            "Check a TODO only after observed implementation or individual-validation evidence authorizes it.",
            "you must complete every planned TODO before beginning any dedicated Verification step.",
            "Check a Verification step only after its own observed evidence.",
            "After every TODO and Verification step is evidenced complete, write the completed-only list once, then replace it with `todos: []`.",
            "Do not clear TODOs on failure, uncertainty, or partial reconciliation.",
            "Your self-check is not independent review, ERB evidence, approval, readiness, or sign-off.",
            "ERB output is optional independent advisory evidence, not a prerequisite or lifecycle authority.",
            "or equally explicit current top-level human plan-creation or plan-replacement request",
            "Before every mutable phase, freshly reload the selected plan, checkbox state, and worktree evidence; never rely on stale evidence.",
            "One plan is exactly `.erb/plans/<slug>.md`: create no subject directory and use no numeric prefix.",
            "multiple separately managed plans may use `.erb/plans/<subject>/<NN>-<slug>.md`",
            "multiple TODOs in one bounded plan are not sufficient.",
            "Active plan bodies are immutable by default.",
            "must not add, remove, rewrite, reorder, or renumber plan content",
            "Completed plans remain immutable.",
            "## Checklist Entry Contract",
            "Every TODO or Verification entry has one atomic purpose",
            "must not depend on itself or a later checklist entry",
            "known ask-gated or destructive operation and its exact contained target",
            "Every entry needs a finite completion or stop condition.",
            "validate the whole plan against this contract",
            "Do not use Worker slicing to make a compound checklist entry acceptable.",
            "New TODO and Verification entries must be unchecked.",
            "Never change an unchecked checkbox to checked during an update.",
            "Retain a checked item only when its obligation and the surrounding acceptance contract remain materially unchanged and fresh evidence still supports it.",
            "Reset every changed, invalidated, or insufficiently evidenced checked item to unchecked.",
            "Dependency correctness outranks preserving existing order.",
            "old-to-new ordering plus the reason for each move",
            "Never update a plan within the `/start-plan` turn",
            "must never stage or commit and must never be instructed or delegated to create a commit.",
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
            "A second consecutive unsupported no-progress terminal return for the same residual slice is an execution-channel failure",
            "Never repeat an action whose prior result or replay safety cannot be established from fresh evidence.",
            "Apply the permission-state and replay-safety gates before the unsupported no-progress allowance.",
            "A policy denial or rejected approval for a command known not to have started is a genuine blocker",
            "While runtime approval is pending, retain the same waiting child",
            "Approval alone is not evidence that the operation ran.",
            "Worker's exact `approval_state`, `execution_state`, and `replay_safe` fields",
            "resume the same Worker child session by passing its `task_id`",
            "Do not start a fresh Worker Task for an in-scope correction when that child session can be resumed.",
            "If the runtime cannot resume that child after an interruption",
            "Keep a continuation delta-focused",
            "For every resumed correction, send a complete correction packet",
            "numbered evidence gaps",
            "the acceptance criterion each gap blocks",
            "the observed evidence and required result",
            "the exact correction requested",
            "validation to rerun",
            "A status-only preamble or a reference such as `these findings`",
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

    # Keep the descriptor/identity checks together: splitting this security boundary
    # would obscure the ordering that makes its TOCTOU defenses fail closed.
    def _bind_config_root(  # noqa: C901
        self,
        *,
        create: bool,
    ) -> tuple[BoundConfigRoot | None, bool, list[str]]:
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
