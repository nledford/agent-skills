import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.opencode_contracts import (
    CANONICAL_AGENT_SKILL_IDS,
    CANONICAL_AGENT_TOPOLOGY,
    CANONICAL_PERMISSION_PROFILES,
    CRITIC_PERMISSION_PROFILE_NAMES,
    EXTERNAL_DIRECTORY_ASK_AGENT_IDS,
    EXTERNAL_DIRECTORY_DOC_TOKENS,
    EXTERNAL_DIRECTORY_SCOPE_INVARIANT,
    MCP_SELECTION_PROMPT_CONTRACTS,
    SANITIZED_EVIDENCE_INVARIANT,
    STANDARD_CRITIC_AGENT_IDS,
    STANDARD_CRITIC_REQUIRED_HEADINGS,
    STANDARD_CRITIC_REQUIRED_SEMANTICS,
    STANDARD_CRITIC_STAGE_REVIEWER_IDS,
    TECHNICAL_RESEARCHER_EXTERNAL_EGRESS_INVARIANT,
    canonical_agent_permissions,
)
from tools.opencode_frontmatter import parse_frontmatter
from tools.opencode_install import OpenCodeInstallService


from tests.opencode_test_support import (
    create_canonical_active_workflow_repo,
    resolve_opencode_action,
)


class CanonicalAgentTopologyTests(unittest.TestCase):
    def test_standard_critic_membership_is_derived_from_topology(self) -> None:
        self.assertEqual(
            {"review-specialist", "technical-debt-auditor"},
            CRITIC_PERMISSION_PROFILE_NAMES,
        )
        review_specialists = {
            policy.agent_id
            for policy in CANONICAL_AGENT_TOPOLOGY.agents
            if policy.permission_profile in CRITIC_PERMISSION_PROFILE_NAMES
        }

        self.assertTrue(STANDARD_CRITIC_STAGE_REVIEWER_IDS <= review_specialists)
        self.assertEqual(
            review_specialists - STANDARD_CRITIC_STAGE_REVIEWER_IDS,
            STANDARD_CRITIC_AGENT_IDS,
        )
        self.assertEqual(20, len(STANDARD_CRITIC_AGENT_IDS))

    def test_data_review_specialists_are_canonical_leaf_reviewers(self) -> None:
        expected_skills = {
            "analytics-engineering-critic": (
                "code-review",
                "review-verification-protocol",
                "data-platform-engineering",
                "architecture-review",
                "sql-engineering",
                "performance-review",
                "testing-strategy",
                "observability-engineering",
                "documentation-engineering",
                "security-review",
                "security-review-evidence",
            ),
            "business-intelligence-critic": (
                "code-review",
                "review-verification-protocol",
                "data-platform-engineering",
                "performance-review",
                "testing-strategy",
                "ux-accessibility-review",
                "internationalization-localization",
                "documentation-engineering",
                "security-review",
                "security-review-evidence",
            ),
            "data-model-steward": (
                "code-review",
                "review-verification-protocol",
                "data-platform-engineering",
                "architecture-review",
                "documentation-engineering",
                "testing-strategy",
                "security-review",
                "security-review-evidence",
            ),
            "ingestion-specialist": (
                "code-review",
                "review-verification-protocol",
                "data-platform-engineering",
                "api-design",
                "sql-engineering",
                "performance-review",
                "testing-strategy",
                "observability-engineering",
                "security-review",
                "security-review-evidence",
            ),
            "data-platform-operations-reviewer": (
                "code-review",
                "review-verification-protocol",
                "data-platform-engineering",
                "observability-engineering",
                "performance-review",
                "ci-release-engineering",
                "documentation-engineering",
                "testing-strategy",
                "security-review",
                "security-review-evidence",
            ),
        }
        policies = {
            policy.agent_id: policy for policy in CANONICAL_AGENT_TOPOLOGY.agents
        }

        for agent_id, skill_ids in expected_skills.items():
            with self.subTest(agent_id=agent_id):
                self.assertIn(agent_id, policies)
                policy = policies[agent_id]
                self.assertEqual("subagent", policy.mode)
                self.assertEqual((), policy.task_targets)
                self.assertEqual("review-specialist", policy.permission_profile)
                self.assertEqual(skill_ids, CANONICAL_AGENT_SKILL_IDS[agent_id])

        data_review_ids = set(expected_skills)
        for caller_id in ("engineering-lead", "engineering-review-board"):
            with self.subTest(caller_id=caller_id):
                self.assertLessEqual(
                    data_review_ids,
                    set(policies[caller_id].task_targets),
                )

    def test_data_platform_engineering_skill_uses_progressive_lane_references(self) -> None:
        project_root = Path(__file__).parents[1]
        skill_root = project_root / "skills/data-platform-engineering"
        skill_path = skill_root / "SKILL.md"
        self.assertTrue(skill_path.is_file())
        text = skill_path.read_text(encoding="utf-8")

        for reference in (
            "ingestion.md",
            "analytics-transformations.md",
            "analytical-semantics.md",
            "power-bi-semantic-models.md",
            "fabric-power-bi-operations.md",
        ):
            with self.subTest(reference=reference):
                self.assertIn(f"(references/{reference})", text)
                self.assertTrue((skill_root / "references" / reference).is_file())

        for agent_id in (
            "analytics-engineering-critic",
            "business-intelligence-critic",
            "data-model-steward",
            "data-platform-operations-reviewer",
            "engineering-lead",
            "implementation-worker",
            "ingestion-specialist",
        ):
            with self.subTest(agent_id=agent_id):
                self.assertIn(
                    "data-platform-engineering",
                    CANONICAL_AGENT_SKILL_IDS[agent_id],
                )
        self.assertNotIn(
            "data-platform-engineering",
            CANONICAL_AGENT_SKILL_IDS["engineering-review-board"],
        )

    def test_data_review_routing_contract_distinguishes_responsibility_lanes(self) -> None:
        project_root = Path(__file__).parents[1]
        agent_ids = {
            "analytics-engineering-critic",
            "business-intelligence-critic",
            "data-model-steward",
            "data-platform-operations-reviewer",
            "ingestion-specialist",
        }
        board = (
            project_root / "opencode/agents/engineering-review-board.md"
        ).read_text(encoding="utf-8")
        lead = (
            project_root / "opencode/agents/engineering-lead.md"
        ).read_text(encoding="utf-8")
        governance = (
            project_root / "docs/engineering-agent-governance.md"
        ).read_text(encoding="utf-8")
        cross_reference = (
            project_root / "docs/cross-reference-map.md"
        ).read_text(encoding="utf-8")

        selection_guard = (
            "A mention of Fabric, Power BI, or a data platform alone does not "
            "justify selecting all five."
        )
        stewardship_guard = (
            "Treat `data-model-steward` as a cross-cutting analytical-semantics "
            "lens, not a mutually exclusive lifecycle stage."
        )
        for name, text in (("Board", board), ("Lead", lead)):
            with self.subTest(definition=name):
                normalized = " ".join(text.split())
                self.assertIn(selection_guard, normalized)
                self.assertIn(stewardship_guard, normalized)
                for agent_id in agent_ids:
                    self.assertIn(f"`{agent_id}`", text)

        for name, text in (
            ("governance", governance),
            ("cross-reference", cross_reference),
        ):
            with self.subTest(document=name):
                self.assertIn(stewardship_guard, " ".join(text.split()))
                for agent_id in agent_ids:
                    self.assertIn(f"`{agent_id}`", text)

        corpus = json.loads(
            (project_root / "evals/routing/v1.json").read_text(encoding="utf-8")
        )
        cases = {case["id"]: case for case in corpus["cases"]}
        expected_routes = {
            "data-ingestion-cdc-review": (
                {"ingestion-specialist"},
                {
                    "analytics-engineering-critic",
                    "business-intelligence-critic",
                    "data-model-steward",
                },
            ),
            "analytics-medallion-transformation-review": (
                {"analytics-engineering-critic"},
                {"ingestion-specialist", "business-intelligence-critic"},
            ),
            "power-bi-semantic-model-review": (
                {"business-intelligence-critic"},
                {"analytics-engineering-critic", "design-critic"},
            ),
            "analytical-grain-governance-review": (
                {"data-model-steward"},
                {"domain-model-critic", "database-engineering-critic"},
            ),
            "data-platform-operations-review": (
                {"data-platform-operations-reviewer"},
                {"release-readiness-reviewer", "ingestion-specialist"},
            ),
            "physical-database-design-near-miss": (
                {"database-engineering-critic"},
                {"data-model-steward"},
            ),
            "application-domain-model-near-miss": (
                {"domain-model-critic"},
                {"data-model-steward"},
            ),
            "ingestion-concurrency-overlap-review": (
                {
                    "ingestion-specialist",
                    "distributed-systems-concurrency-critic",
                },
                {
                    "analytics-engineering-critic",
                    "data-platform-operations-reviewer",
                },
            ),
            "analytics-stewardship-overlap-review": (
                {"analytics-engineering-critic", "data-model-steward"},
                {"ingestion-specialist", "business-intelligence-critic"},
            ),
            "business-intelligence-stewardship-overlap-review": (
                {"business-intelligence-critic", "data-model-steward"},
                {"analytics-engineering-critic", "design-critic"},
            ),
            "data-platform-rollout-readiness-overlap-review": (
                {
                    "data-platform-operations-reviewer",
                    "release-readiness-reviewer",
                },
                {"ingestion-specialist", "analytics-engineering-critic"},
            ),
        }
        for case_id, (expected_handoffs, forbidden_handoffs) in expected_routes.items():
            with self.subTest(case_id=case_id):
                self.assertIn(case_id, cases)
                case = cases[case_id]
                self.assertEqual("engineering-review-board", case["expected"]["agent"])
                self.assertEqual(
                    {"code-review", "review-verification-protocol"},
                    set(case["expected"]["skills"]),
                )
                self.assertEqual(expected_handoffs, set(case["expected"]["handoffs"]))
                self.assertEqual(
                    forbidden_handoffs,
                    set(case["forbidden"]["handoffs"]),
                )

    def test_technical_debt_auditor_uses_ask_gated_evidence_profile(self) -> None:
        policy = next(
            policy
            for policy in CANONICAL_AGENT_TOPOLOGY.agents
            if policy.agent_id == "technical-debt-auditor"
        )
        self.assertEqual("technical-debt-auditor", policy.permission_profile)

        project_root = Path(__file__).parents[1]
        parsed, errors = parse_frontmatter(
            "agents",
            "technical-debt-auditor.md",
            (
                project_root / "opencode/agents/technical-debt-auditor.md"
            ).read_text(encoding="utf-8"),
        )
        self.assertEqual([], errors)
        assert parsed is not None
        bash = parsed.permissions["bash"]
        self.assertIsInstance(bash, tuple)
        assert isinstance(bash, tuple)

        cases = (
            ("metadata", "cargo metadata --no-deps", "ask"),
            ("dependency tree", "cargo tree -d", "ask"),
            ("clippy", "cargo clippy --all-targets", "ask"),
            ("audit", "cargo audit", "ask"),
            ("audit fix", "cargo audit fix", "deny"),
            ("outdated", "cargo outdated", "ask"),
            ("nightly udeps", "cargo +nightly udeps", "ask"),
            ("server build", "cargo build --release --features ssr", "ask"),
            (
                "WASM hydration build",
                "cargo build --target wasm32-unknown-unknown --features hydrate",
                "ask",
            ),
            (
                "WASM hydration lint",
                "cargo clippy --target=wasm32-unknown-unknown --features hydrate",
                "ask",
            ),
            ("Leptos build", "cargo leptos build --release", "ask"),
            ("tests", "cargo test --workspace", "ask"),
            ("Clippy fix", "cargo clippy --fix", "deny"),
            (
                "WASM Clippy fix",
                "cargo clippy --fix --target wasm32-unknown-unknown",
                "deny",
            ),
            ("install", "cargo install cargo-audit", "deny"),
            (
                "WASM-targeted install",
                "cargo install cargo-audit --target wasm32-unknown-unknown",
                "deny",
            ),
            ("update", "cargo update", "deny"),
            ("new project", "cargo leptos new example", "deny"),
            (
                "manifest escape",
                "cargo test --manifest-path ../other/Cargo.toml",
                "deny",
            ),
            (
                "command-line Cargo config",
                'cargo build --config \'build.rustc-wrapper="sh"\'',
                "deny",
            ),
            ("target directory", "cargo build --target-dir src", "deny"),
            (
                "custom target specification",
                "cargo build --target ../outside/target.json",
                "deny",
            ),
            (
                "unapproved WASM subcommand",
                "cargo run --target wasm32-unknown-unknown",
                "deny",
            ),
            (
                "direct rustc output",
                "cargo rustc --target wasm32-unknown-unknown -- -o src/output",
                "deny",
            ),
            ("output directory", "cargo build --out-dir src", "deny"),
            (
                "lockfile path",
                "cargo build --lockfile-path src/Cargo.lock",
                "deny",
            ),
            (
                "artifact directory",
                "cargo build -Z unstable-options --artifact-dir src",
                "deny",
            ),
            ("shell composition", "cargo test; cargo audit", "deny"),
            (
                "newline composition",
                "cargo test --workspace\ncargo audit",
                "deny",
            ),
            ("arbitrary shell", "sh scripts/audit.sh", "deny"),
        )
        for label, command, expected in cases:
            with self.subTest(action=label, command=command):
                self.assertEqual(
                    expected,
                    resolve_opencode_action(bash, command, baseline="deny"),
                )

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

    def test_checked_in_technical_debt_audit_contract_is_structured(self) -> None:
        project_root = Path(__file__).parents[1]
        skill = " ".join(
            (
                project_root / "skills/technical-debt-audit/SKILL.md"
            ).read_text(encoding="utf-8").split()
        )
        auditor = " ".join(
            (
                project_root / "opencode/agents/technical-debt-auditor.md"
            ).read_text(encoding="utf-8").split()
        )
        command = " ".join(
            (
                project_root / "opencode/commands/audit-technical-debt.md"
            ).read_text(encoding="utf-8").split()
        )
        rust_reference = " ".join(
            (
                project_root
                / "skills/rust-async-web/references/axum-leptos-debt-audit.md"
            ).read_text(encoding="utf-8").split()
        )
        code_review = " ".join(
            (project_root / "skills/code-review/SKILL.md")
            .read_text(encoding="utf-8")
            .split()
        )
        taxonomy = (
            project_root / "docs/skill-taxonomy.md"
        ).read_text(encoding="utf-8")
        cross_reference = (
            project_root / "docs/cross-reference-map.md"
        ).read_text(encoding="utf-8")

        for required in (
            "name: technical-debt-audit",
            "`review-verification-protocol`",
            "Repository overview",
            "qualitative",
            "Quick wins",
            "Strategic blockers",
            "`architecture-review`",
            "`testing-strategy`",
            "`dependency-supply-chain-review`",
            "`security-review-evidence`",
            "`documentation-engineering`",
            "approved evidence commands",
        ):
            with self.subTest(skill=required):
                self.assertIn(required, skill)

        for required in (
            "Load `technical-debt-audit`",
            "languages, frameworks, build and test tooling",
            "entry points",
            "Unused dependencies",
            "skipped or quarantined tests",
            "`technical-researcher`",
            "Quick wins",
            "Strategic blockers",
            "tool availability, exact command, exit status",
            "`frontend-architecture-interaction-critic`",
            "`distributed-systems-concurrency-critic`",
        ):
            with self.subTest(auditor=required):
                self.assertIn(required, auditor)

        for required in (
            "Load `technical-debt-audit` and `review-verification-protocol`.",
            "Repository overview",
            "Evidence reviewed and limitations",
            "Prioritized findings",
            "Quick wins",
            "Strategic blockers",
            "Longer-term improvement program",
            "Skipped validation and residual risk",
            "Do not invent numeric coverage percentages",
            "explicitly requests shell or tooling evidence",
            "Do not install missing tools",
        ):
            with self.subTest(command=required):
                self.assertIn(required, command)

        for required in (
            "[package.metadata.leptos]",
            "[[workspace.metadata.leptos]]",
            "hydrate_islands",
            "hydrate_body",
            "HydrationScripts",
            "cargo leptos build --release",
            "wasm32-unknown-unknown",
            "Do not run `--all-features` blindly",
            "ordinary manual Axum routes",
            "process-local state",
        ):
            with self.subTest(rust_reference=required):
                self.assertIn(required, rust_reference)

        self.assertIn(
            "repository-wide or focused technical-debt portfolio audit",
            code_review,
        )
        self.assertIn("`technical-debt-audit`", taxonomy)
        self.assertIn("| Technical-debt audit | `technical-debt-audit` |", cross_reference)

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
        self.assertEqual(29, len(CANONICAL_AGENT_TOPOLOGY.agents))

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
                "browser-evidence-collector": "browser-evidence-collector",
                "technical-debt-auditor": "technical-debt-auditor",
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
            parsed, parse_errors = parse_frontmatter(
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
            parsed, errors = parse_frontmatter(
                "agents",
                f"{policy.agent_id}.md",
                (project_root / "opencode" / "agents" / f"{policy.agent_id}.md").read_text(
                    encoding="utf-8"
                ),
            )
            self.assertEqual([], errors)
            assert parsed is not None
            self.assertEqual(
                canonical_agent_permissions(policy),
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
                permissions_without_skills = {
                    key: value
                    for key, value in parsed.permissions.items()
                    if key != "skill"
                }
                if specialist_permissions is None:
                    specialist_permissions = permissions_without_skills
                else:
                    self.assertEqual(
                        specialist_permissions, permissions_without_skills
                    )

    def test_checked_in_external_directory_governance_contract(self) -> None:
        project_root = Path(__file__).parents[1]
        for relative_path, tokens in EXTERNAL_DIRECTORY_DOC_TOKENS.items():
            with self.subTest(path=relative_path):
                text = (project_root / relative_path).read_text(encoding="utf-8")
                for token in tokens:
                    self.assertIn(token, text)

    def test_checked_in_technical_researcher_asks_before_using_hound(self) -> None:
        project_root = Path(__file__).parents[1]
        parsed, errors = parse_frontmatter(
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

    def test_checked_in_worker_bash_permissions_resolve_to_effective_actions(self) -> None:
        project_root = Path(__file__).parents[1]
        worker, errors = parse_frontmatter(
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
            ("file removal", "rm file.txt", "ask"),
            ("legacy plan removal", "rm docs/implementation-plans/plans/example.md", "deny"),
            ("canonical plan removal", "rm .erb/plans/example.md", "deny"),
            ("plan state removal", "rm .erb/plan-state.json", "deny"),
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

    def test_validate_rejects_worker_rm_approval_bypass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_canonical_active_workflow_repo(root)
            worker = repo / "opencode" / "agents" / "implementation-worker.md"
            original = worker.read_text(encoding="utf-8")
            rule = '    "rm *": ask\n'
            self.assertIn(rule, original)
            worker.write_text(
                original.replace(rule, f'{rule}    "rm*": allow\n', 1),
                encoding="utf-8",
            )

            result = OpenCodeInstallService(repo, root / "config").validate()

            self.assertFalse(result.ok)
            self.assertTrue(
                any("permission profile" in error for error in result.errors),
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
