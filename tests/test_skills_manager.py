import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

from tools.skills_manager import (
    GlobalInstallService,
    OperationResult,
    SkillRegistry,
    ValidationResult,
    emit_validation,
    main,
    run_third_party_update,
    skill_tree_sha256,
)


def write_skill(root: Path, name: str, *, description: str = "Test skill.") -> Path:
    skill_dir = root / name
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n",
        encoding="utf-8",
    )
    return skill_dir


def create_repo(root: Path) -> Path:
    repo = root / "repo"
    (repo / "skills").mkdir(parents=True)
    return repo


def create_configured_global_install(
    root: Path,
) -> tuple[Path, Path, GlobalInstallService]:
    repo = create_repo(root)
    write_skill(repo / "skills", "first-party")
    global_link = root / ".agents" / "skills"
    global_link.parent.mkdir()
    os.symlink(repo / "skills", global_link)
    return repo, global_link, GlobalInstallService(repo, global_link)


def write_taxonomy(
    repo: Path,
    names: list[str],
    *,
    categories: dict[str, list[str]] | None = None,
) -> Path:
    docs = repo / "docs"
    docs.mkdir()
    category_rows = []
    effective_categories = categories
    if effective_categories is None:
        effective_categories = {"Test category": names}
    for category, skill_names in effective_categories.items():
        listed_skills = ", ".join(f"`{name}`" for name in skill_names)
        category_rows.append(f"| {category} | {listed_skills} | Test boundary. |")
    category_rows_text = "\n".join(category_rows)
    taxonomy_section = (
        "## Taxonomy\n\n"
        "| Category | Skills | Boundary |\n"
        "| --- | --- | --- |\n"
        f"{category_rows_text}\n\n"
    )
    rows = "\n".join(
        f"| `{name}` | Test purpose. | Keep. |"
        for name in names
    )
    path = docs / "skill-taxonomy.md"
    path.write_text(
        "# Skill Taxonomy\n\n"
        f"{taxonomy_section}"
        "## Current First-Party Inventory\n\n"
        "| Skill | Purpose | Decision |\n"
        "| --- | --- | --- |\n"
        f"{rows}\n",
        encoding="utf-8",
    )
    return path


class SkillRegistryTests(unittest.TestCase):
    def test_lists_first_party_and_third_party_skills(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            write_skill(repo / "skills", "first-party")
            write_skill(repo / "skills", "ignored-third-party")
            write_skill(repo / "skills", "locked-third-party")
            (repo / ".gitignore").write_text("/skills/ignored-third-party/\n", encoding="utf-8")
            (repo / ".skill-lock.json").write_text(
                json.dumps({"version": 3, "skills": {"locked-third-party": {}}}),
                encoding="utf-8",
            )

            registry = SkillRegistry.load(repo)

            self.assertEqual(["first-party"], [skill.name for skill in registry.first_party()])
            self.assertEqual(
                ["ignored-third-party", "locked-third-party"],
                [skill.name for skill in registry.third_party()],
            )

    def test_validation_rejects_malformed_skill_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            bad_skill = repo / "skills" / "bad-skill"
            bad_skill.mkdir()
            (bad_skill / "SKILL.md").write_text("# Missing metadata\n", encoding="utf-8")

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertFalse(result.ok)
            self.assertIn("bad-skill: SKILL.md must start with YAML front matter", result.errors)

    def test_first_party_validation_rejects_broken_local_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            skill = write_skill(repo / "skills", "linked-skill")
            (skill / "SKILL.md").write_text(
                "---\n"
                "name: linked-skill\n"
                "description: Test skill.\n"
                "---\n\n"
                "# linked-skill\n\n"
                "[Missing](references/missing.md)\n",
                encoding="utf-8",
            )

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertFalse(result.ok)
            self.assertIn(
                "linked-skill: broken local link in SKILL.md: references/missing.md",
                result.errors,
            )

    def test_first_party_validation_rejects_unreachable_resource_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            skill = write_skill(repo / "skills", "resource-skill")
            references = skill / "references"
            references.mkdir()
            (references / "unused.md").write_text("# Unused\n", encoding="utf-8")

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertFalse(result.ok)
            self.assertIn(
                "resource-skill: resource file is not reachable from SKILL.md: references/unused.md",
                result.errors,
            )

    def test_first_party_validation_rejects_source_project_identifiers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            skill = write_skill(repo / "skills", "portable-skill")
            skill_file = skill / "SKILL.md"
            skill_file.write_text(
                skill_file.read_text(encoding="utf-8")
                + "\nFollow engineering-review-board conventions.\n",
                encoding="utf-8",
            )

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertFalse(result.ok)
            self.assertTrue(
                any("source-project identifier" in error for error in result.errors)
            )

    def test_first_party_validation_rejects_machine_specific_resource_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            skill = write_skill(repo / "skills", "portable-skill")
            references = skill / "references"
            references.mkdir()
            (references / "example.md").write_text(
                "Run the tool from /Users/example/work/application.\n",
                encoding="utf-8",
            )
            skill_file = skill / "SKILL.md"
            skill_file.write_text(
                skill_file.read_text(encoding="utf-8")
                + "\n[Example](references/example.md)\n",
                encoding="utf-8",
            )

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertFalse(result.ok)
            self.assertTrue(
                any(
                    "machine-specific POSIX home path" in error
                    for error in result.errors
                )
            )

    def test_first_party_validation_accepts_portable_path_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            skill = write_skill(repo / "skills", "portable-skill")
            skill_file = skill / "SKILL.md"
            skill_file.write_text(
                skill_file.read_text(encoding="utf-8")
                + "\nUse `/home/<user>/workspace` or `C:\\Users\\<user>\\workspace`.\n",
                encoding="utf-8",
            )
            write_taxonomy(repo, ["portable-skill"])

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertTrue(result.ok, result.errors)

    def test_reachable_resource_files_are_validated_recursively(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            skill = write_skill(repo / "skills", "resource-skill")
            write_taxonomy(repo, ["resource-skill"])
            references = skill / "references"
            references.mkdir()
            (skill / "SKILL.md").write_text(
                "---\n"
                "name: resource-skill\n"
                "description: Test skill.\n"
                "---\n\n"
                "# resource-skill\n\n"
                "[Entry](references/entry.md)\n",
                encoding="utf-8",
            )
            (references / "entry.md").write_text(
                "# Entry\n\n[Details](details.md)\n",
                encoding="utf-8",
            )
            (references / "details.md").write_text("# Details\n", encoding="utf-8")

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertTrue(result.ok)

    def test_image_links_make_asset_files_reachable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            skill = write_skill(repo / "skills", "asset-skill")
            write_taxonomy(repo, ["asset-skill"])
            assets = skill / "assets"
            assets.mkdir()
            (assets / "sample.svg").write_text("<svg />\n", encoding="utf-8")
            (skill / "SKILL.md").write_text(
                "---\n"
                "name: asset-skill\n"
                "description: Test skill.\n"
                "---\n\n"
                "# asset-skill\n\n"
                "![Sample](assets/sample.svg)\n",
                encoding="utf-8",
            )

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertTrue(result.ok)

    def test_angle_bracket_links_support_paths_with_spaces(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            skill = write_skill(repo / "skills", "space-skill")
            write_taxonomy(repo, ["space-skill"])
            references = skill / "references"
            references.mkdir()
            (references / "two words.md").write_text("# Details\n", encoding="utf-8")
            (skill / "SKILL.md").write_text(
                "---\n"
                "name: space-skill\n"
                "description: Test skill.\n"
                "---\n\n"
                "# space-skill\n\n"
                "[Details](<references/two words.md>)\n",
                encoding="utf-8",
            )

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertTrue(result.ok)

    def test_first_party_resource_validation_ignores_third_party_skills(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            skill = write_skill(repo / "skills", "ignored-third-party")
            references = skill / "references"
            references.mkdir()
            (references / "unused.md").write_text("# Unused\n", encoding="utf-8")
            (repo / ".gitignore").write_text("/skills/ignored-third-party/\n", encoding="utf-8")
            write_skill(repo / "skills", "first-party")
            write_taxonomy(repo, ["first-party"])

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertTrue(result.ok)

    def test_third_party_validation_requires_lockfile_installs_to_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            (repo / ".skill-lock.json").write_text(
                json.dumps({"version": 3, "skills": {"missing-skill": {}}}),
                encoding="utf-8",
            )

            result = SkillRegistry.load(repo).validate_third_party()

            self.assertFalse(result.ok)
            self.assertIn(
                "missing-skill: third-party skill is listed in .skill-lock.json but missing",
                result.errors,
            )

    def test_first_party_validation_rejects_missing_taxonomy_inventory_entry(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            write_skill(repo / "skills", "alpha")
            write_skill(repo / "skills", "beta")
            write_taxonomy(repo, ["alpha"])

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertFalse(result.ok)
            self.assertIn(
                "docs/skill-taxonomy.md: first-party skill missing from inventory: beta",
                result.errors,
            )

    def test_first_party_validation_rejects_extra_taxonomy_inventory_entry(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            write_skill(repo / "skills", "alpha")
            write_taxonomy(repo, ["alpha", "ghost"])

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertFalse(result.ok)
            self.assertIn(
                "docs/skill-taxonomy.md: inventory lists non-first-party skill: ghost",
                result.errors,
            )

    def test_first_party_validation_rejects_duplicate_taxonomy_inventory_entry(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            write_skill(repo / "skills", "alpha")
            write_taxonomy(repo, ["alpha", "alpha"])

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertFalse(result.ok)
            self.assertIn(
                "docs/skill-taxonomy.md: duplicate first-party inventory entry: alpha",
                result.errors,
            )

    def test_first_party_validation_accepts_matching_taxonomy_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            write_skill(repo / "skills", "alpha")
            write_skill(repo / "skills", "beta")
            write_taxonomy(repo, ["alpha", "beta"])

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertTrue(result.ok)

    def test_first_party_validation_rejects_missing_taxonomy_category_table(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            write_skill(repo / "skills", "alpha")
            taxonomy = write_taxonomy(
                repo,
                ["alpha"],
                categories={"Security review": ["alpha"]},
            )
            taxonomy.write_text(
                taxonomy.read_text(encoding="utf-8").replace(
                    "## Taxonomy",
                    "## Categories",
                    1,
                ),
                encoding="utf-8",
            )

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertFalse(result.ok)
            self.assertIn(
                "docs/skill-taxonomy.md: missing '## Taxonomy' table",
                result.errors,
            )

    def test_first_party_validation_rejects_malformed_taxonomy_category_table(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            write_skill(repo / "skills", "alpha")
            taxonomy = write_taxonomy(
                repo,
                ["alpha"],
                categories={"Security review": ["alpha"]},
            )
            taxonomy.write_text(
                taxonomy.read_text(encoding="utf-8").replace(
                    "| Category | Skills | Boundary |",
                    "| Category | Boundary |",
                    1,
                ),
                encoding="utf-8",
            )

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertFalse(result.ok)
            self.assertIn(
                "docs/skill-taxonomy.md: malformed '## Taxonomy' table",
                result.errors,
            )

    def test_first_party_validation_rejects_taxonomy_row_without_skill_references(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            write_skill(repo / "skills", "alpha")
            taxonomy = write_taxonomy(
                repo,
                ["alpha"],
                categories={"Security review": ["alpha"]},
            )
            taxonomy.write_text(
                taxonomy.read_text(encoding="utf-8").replace(
                    "`alpha`",
                    "alpha",
                    1,
                ),
                encoding="utf-8",
            )

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertFalse(result.ok)
            self.assertIn(
                "docs/skill-taxonomy.md: malformed '## Taxonomy' table",
                result.errors,
            )

    def test_first_party_validation_rejects_empty_taxonomy_category_table(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            write_skill(repo / "skills", "alpha")
            write_taxonomy(repo, ["alpha"], categories={})

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertFalse(result.ok)
            self.assertIn(
                "docs/skill-taxonomy.md: malformed '## Taxonomy' table",
                result.errors,
            )

    def test_validation_result_combines_errors_and_warnings(self) -> None:
        combined = ValidationResult.combine(
            [
                ValidationResult(errors=["error-a"], warnings=["warning-a"]),
                ValidationResult(errors=["error-b"]),
            ]
        )

        self.assertFalse(combined.ok)
        self.assertEqual(["error-a", "error-b"], combined.errors)
        self.assertEqual(["warning-a"], combined.warnings)

    def test_category_required_link_rule_warns_for_missing_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            write_skill(repo / "skills", "custom-security-skill")
            write_taxonomy(
                repo,
                ["custom-security-skill"],
                categories={"Security review": ["custom-security-skill"]},
            )

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertTrue(result.ok)
            self.assertEqual(
                [
                    "custom-security-skill: SKILL.md should link to security-review for security-sensitive work",
                    "custom-security-skill: SKILL.md should link to security-review-evidence for security-sensitive work",
                ],
                result.warnings,
            )

    def test_git_skills_require_related_skill_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            write_skill(repo / "skills", "git-commit")
            write_skill(repo / "skills", "git-workflows")
            write_taxonomy(repo, ["git-commit", "git-workflows"])

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertTrue(result.ok)
            self.assertEqual(
                [
                    "git-commit: SKILL.md should link to security-review for security-sensitive work",
                    "git-commit: SKILL.md should link to security-review-evidence for security-sensitive work",
                    "git-commit: SKILL.md should link to git-workflows for related Git operations",
                    "git-workflows: SKILL.md should link to security-review for security-sensitive work",
                    "git-workflows: SKILL.md should link to security-review-evidence for security-sensitive work",
                    "git-workflows: SKILL.md should link to git-commit for related Git operations",
                ],
                result.warnings,
            )

    def test_github_and_hound_skills_require_cross_routing_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            write_skill(repo / "skills", "github-mcp-operations")
            write_skill(repo / "skills", "hound-web-research")
            write_taxonomy(
                repo,
                ["github-mcp-operations", "hound-web-research"],
            )

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertTrue(result.ok)
            self.assertEqual(
                [
                    "github-mcp-operations: SKILL.md should link to security-review for security-sensitive work",
                    "github-mcp-operations: SKILL.md should link to security-review-evidence for security-sensitive work",
                    "github-mcp-operations: SKILL.md should link to hound-web-research for MCP server selection",
                    "hound-web-research: SKILL.md should link to github-mcp-operations for MCP server selection",
                ],
                result.warnings,
            )

    def test_ci_and_container_skills_require_security_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            write_skill(repo / "skills", "ci-release-engineering")
            write_skill(repo / "skills", "container-engineering")
            write_taxonomy(
                repo,
                ["ci-release-engineering", "container-engineering"],
            )

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertTrue(result.ok)
            self.assertEqual(
                [
                    "ci-release-engineering: SKILL.md should link to security-review for security-sensitive work",
                    "ci-release-engineering: SKILL.md should link to security-review-evidence for security-sensitive work",
                    "container-engineering: SKILL.md should link to security-review for security-sensitive work",
                    "container-engineering: SKILL.md should link to security-review-evidence for security-sensitive work",
                ],
                result.warnings,
            )

    def test_ruby_and_powershell_skills_require_security_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            write_skill(repo / "skills", "ruby-engineering")
            write_skill(repo / "skills", "powershell-engineering")
            write_taxonomy(
                repo,
                ["ruby-engineering", "powershell-engineering"],
            )

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertTrue(result.ok)
            self.assertEqual(
                [
                    "powershell-engineering: SKILL.md should link to security-review for security-sensitive work",
                    "powershell-engineering: SKILL.md should link to security-review-evidence for security-sensitive work",
                    "ruby-engineering: SKILL.md should link to security-review for security-sensitive work",
                    "ruby-engineering: SKILL.md should link to security-review-evidence for security-sensitive work",
                ],
                result.warnings,
            )

    def test_api_contract_category_requires_security_review_link(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            write_skill(repo / "skills", "contract-skill")
            write_taxonomy(
                repo,
                ["contract-skill"],
                categories={"API design and contracts": ["contract-skill"]},
            )

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertTrue(result.ok)
            self.assertEqual(
                [
                    "contract-skill: SKILL.md should link to security-review for security-sensitive API contract work",
                ],
                result.warnings,
            )

    def test_api_and_observability_category_rules_accept_required_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            api_skill = write_skill(repo / "skills", "api-design")
            observability_skill = write_skill(repo / "skills", "observability-engineering")
            write_skill(repo / "skills", "security-review")
            write_skill(repo / "skills", "security-review-evidence")
            write_taxonomy(
                repo,
                [
                    "api-design",
                    "observability-engineering",
                    "security-review",
                    "security-review-evidence",
                ],
                categories={
                    "API design and contracts": ["api-design"],
                    "Observability and operations": ["observability-engineering"],
                },
            )
            (api_skill / "SKILL.md").write_text(
                "---\n"
                "name: api-design\n"
                "description: Test skill.\n"
                "---\n\n"
                "# api-design\n\n"
                "Load [`security-review`](../security-review/SKILL.md).\n",
                encoding="utf-8",
            )
            (observability_skill / "SKILL.md").write_text(
                "---\n"
                "name: observability-engineering\n"
                "description: Test skill.\n"
                "---\n\n"
                "# observability-engineering\n\n"
                "Load [`security-review`](../security-review/SKILL.md).\n"
                "Use [`security-review-evidence`](../security-review-evidence/SKILL.md).\n",
                encoding="utf-8",
            )

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertTrue(result.ok)
            self.assertEqual([], result.warnings)

    def test_category_required_link_rule_accepts_required_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            write_skill(repo / "skills", "security-review")
            write_skill(repo / "skills", "security-review-evidence")
            skill = write_skill(repo / "skills", "custom-security-skill")
            write_taxonomy(
                repo,
                ["custom-security-skill", "security-review", "security-review-evidence"],
                categories={"Security review": ["custom-security-skill"]},
            )
            (skill / "SKILL.md").write_text(
                "---\n"
                "name: custom-security-skill\n"
                "description: Test skill.\n"
                "---\n\n"
                "# custom-security-skill\n\n"
                "Load [`security-review`](../security-review/SKILL.md).\n"
                "Use [`security-review-evidence`](../security-review-evidence/SKILL.md).\n",
                encoding="utf-8",
            )

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertTrue(result.ok)
            self.assertEqual([], result.warnings)

    def test_category_required_link_rule_ignores_third_party_skills(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            write_skill(repo / "skills", "custom-security-skill")
            write_skill(repo / "skills", "first-party")
            write_taxonomy(
                repo,
                ["first-party"],
                categories={"Security review": ["custom-security-skill"]},
            )
            (repo / ".gitignore").write_text(
                "/skills/custom-security-skill/\n", encoding="utf-8"
            )

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertTrue(result.ok)
            self.assertEqual([], result.warnings)

    def test_required_link_warnings_coexist_with_hard_validation_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            skill = write_skill(repo / "skills", "custom-security-skill")
            write_taxonomy(
                repo,
                ["custom-security-skill"],
                categories={"Security review": ["custom-security-skill"]},
            )
            (skill / "SKILL.md").write_text(
                "---\n"
                "name: custom-security-skill\n"
                "description: Test skill.\n"
                "---\n\n"
                "# custom-security-skill\n\n"
                "[Missing](references/missing.md)\n",
                encoding="utf-8",
            )

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertFalse(result.ok)
            self.assertIn(
                "custom-security-skill: broken local link in SKILL.md: references/missing.md",
                result.errors,
            )
            self.assertEqual(
                [
                    "custom-security-skill: SKILL.md should link to security-review for security-sensitive work",
                    "custom-security-skill: SKILL.md should link to security-review-evidence for security-sensitive work",
                ],
                result.warnings,
            )

    def test_emit_validation_prints_warnings_without_failing(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = emit_validation(ValidationResult(warnings=["missing security link"]))

        self.assertEqual(0, exit_code)
        self.assertEqual("Validation passed.\n", stdout.getvalue())
        self.assertEqual("warning: missing security link\n", stderr.getvalue())

    def test_emit_validation_errors_still_fail(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = emit_validation(
                ValidationResult(errors=["broken skill"], warnings=["missing security link"])
            )

        self.assertEqual(1, exit_code)
        self.assertEqual("", stdout.getvalue())
        self.assertEqual(
            "warning: missing security link\nerror: broken skill\n",
            stderr.getvalue(),
        )


class GlobalInstallServiceTests(unittest.TestCase):
    def test_setup_creates_symlink_when_target_is_absent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_repo(root)
            write_skill(repo / "skills", "first-party")
            global_link = root / ".agents" / "skills"

            service = GlobalInstallService(repo, global_link)
            result = service.setup()

            self.assertTrue(result.ok)
            self.assertTrue(global_link.is_symlink())
            self.assertEqual((repo / "skills").resolve(), global_link.resolve())
            self.assertIn("Created", result.messages[0])

    def test_setup_is_idempotent_when_symlink_is_correct(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_repo(root)
            write_skill(repo / "skills", "first-party")
            global_link = root / ".agents" / "skills"
            global_link.parent.mkdir()
            os.symlink(repo / "skills", global_link)

            result = GlobalInstallService(repo, global_link).setup()

            self.assertTrue(result.ok)
            self.assertIn("already points", result.messages[0])

    def test_setup_refuses_to_replace_existing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_repo(root)
            write_skill(repo / "skills", "first-party")
            global_link = root / ".agents" / "skills"
            global_link.mkdir(parents=True)

            result = GlobalInstallService(repo, global_link).setup()

            self.assertFalse(result.ok)
            self.assertIn("not a symlink", result.errors[0])
            self.assertTrue(global_link.is_dir())

    def test_verify_reports_correct_global_install(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_repo(root)
            write_skill(repo / "skills", "first-party")
            global_link = root / ".agents" / "skills"
            global_link.parent.mkdir()
            os.symlink(repo / "skills", global_link)

            result = GlobalInstallService(repo, global_link).verify()

            self.assertTrue(result.ok)
            self.assertIn("Global skills symlink is configured", result.messages[0])

    def test_uninstall_removes_only_owned_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            _, global_link, service = create_configured_global_install(Path(temp_dir))

            result = service.uninstall()

            self.assertTrue(result.ok)
            self.assertFalse(global_link.exists())
            self.assertFalse(global_link.is_symlink())

    def test_uninstall_dry_run_preserves_owned_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            _, global_link, service = create_configured_global_install(Path(temp_dir))

            result = service.uninstall(dry_run=True)

            self.assertTrue(result.ok)
            self.assertTrue(global_link.is_symlink())
            self.assertIn("Would remove symlink", result.messages[0])

    def test_uninstall_is_idempotent_when_global_path_is_absent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_repo(root)
            service = GlobalInstallService(repo, root / ".agents" / "skills")

            result = service.uninstall()

            self.assertTrue(result.ok)
            self.assertIn("No global skills path found", result.messages[0])

    def test_uninstall_refuses_foreign_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_repo(root)
            foreign = root / "foreign-skills"
            foreign.mkdir()
            global_link = root / ".agents" / "skills"
            global_link.parent.mkdir()
            os.symlink(foreign, global_link)

            result = GlobalInstallService(repo, global_link).uninstall()

            self.assertFalse(result.ok)
            self.assertTrue(global_link.is_symlink())
            self.assertIn("refusing to remove", result.errors[0])

    def test_uninstall_refuses_non_symlink_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_repo(root)
            global_link = root / ".agents" / "skills"
            global_link.mkdir(parents=True)

            result = GlobalInstallService(repo, global_link).uninstall()

            self.assertFalse(result.ok)
            self.assertTrue(global_link.is_dir())
            self.assertIn("is not a symlink", result.errors[0])

    def test_sync_lockfile_copies_repository_lockfile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo, global_link, service = create_configured_global_install(
                Path(temp_dir)
            )
            repository_lockfile = repo / ".skill-lock.json"
            repository_lockfile.write_text(
                json.dumps({"version": 3, "skills": {}}) + "\n",
                encoding="utf-8",
            )
            global_lockfile = global_link.parent / ".skill-lock.json"

            result = service.sync_lockfile()

            self.assertTrue(result.ok)
            self.assertEqual(
                repository_lockfile.read_bytes(),
                global_lockfile.read_bytes(),
            )

    def test_sync_lockfile_dry_run_does_not_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo, global_link, service = create_configured_global_install(
                Path(temp_dir)
            )
            (repo / ".skill-lock.json").write_text(
                json.dumps({"version": 3, "skills": {}}) + "\n",
                encoding="utf-8",
            )
            global_lockfile = global_link.parent / ".skill-lock.json"

            result = service.sync_lockfile(dry_run=True)

            self.assertTrue(result.ok)
            self.assertFalse(global_lockfile.exists())
            self.assertIn("Would copy", result.messages[0])

    def test_sync_lockfile_is_idempotent_when_copy_matches(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo, global_link, service = create_configured_global_install(
                Path(temp_dir)
            )
            content = json.dumps({"version": 3, "skills": {}}) + "\n"
            (repo / ".skill-lock.json").write_text(content, encoding="utf-8")
            global_lockfile = global_link.parent / ".skill-lock.json"
            global_lockfile.write_text(content, encoding="utf-8")

            result = service.sync_lockfile()

            self.assertTrue(result.ok)
            self.assertIn("already matches", result.messages[0])

    def test_sync_lockfile_requires_repository_lockfile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            _, _, service = create_configured_global_install(Path(temp_dir))

            result = service.sync_lockfile()

            self.assertFalse(result.ok)
            self.assertIn("Missing repository lockfile", result.errors[0])

    def test_sync_lockfile_requires_verified_global_install(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_repo(root)
            (repo / ".skill-lock.json").write_text(
                json.dumps({"version": 3, "skills": {}}) + "\n",
                encoding="utf-8",
            )
            global_link = root / ".agents" / "skills"

            result = GlobalInstallService(repo, global_link).sync_lockfile()

            self.assertFalse(result.ok)
            self.assertFalse((global_link.parent / ".skill-lock.json").exists())
            self.assertIn("does not exist", result.errors[0])


class ThirdPartyUpdateTests(unittest.TestCase):
    def test_update_requires_verified_global_install(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_repo(root)
            global_path = root / ".agents" / "skills"

            with (
                patch("tools.skills_manager.shutil.which") as which,
                patch("tools.skills_manager.subprocess.run") as run,
            ):
                result = run_third_party_update(repo, global_path)

            self.assertFalse(result.ok)
            self.assertIn("does not exist", result.errors[0])
            which.assert_not_called()
            run.assert_not_called()

    def test_update_rejects_empty_command(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            _, global_path, service = create_configured_global_install(Path(temp_dir))

            with (
                patch.dict(os.environ, {"SKILLS_UPDATE_COMMAND": ""}),
                patch("tools.skills_manager.shutil.which") as which,
            ):
                result = run_third_party_update(service.repo_root, global_path)

            self.assertEqual(["SKILLS_UPDATE_COMMAND is empty"], result.errors)
            which.assert_not_called()

    def test_update_rejects_malformed_command_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            _, global_path, service = create_configured_global_install(Path(temp_dir))

            with (
                patch.dict(
                    os.environ,
                    {"SKILLS_UPDATE_COMMAND": "runner --label 'unterminated"},
                ),
                patch("tools.skills_manager.shutil.which") as which,
                patch("tools.skills_manager.subprocess.run") as run,
            ):
                result = run_third_party_update(service.repo_root, global_path)

            self.assertEqual(
                ["SKILLS_UPDATE_COMMAND is not valid shell-like argument text"],
                result.errors,
            )
            which.assert_not_called()
            run.assert_not_called()

    def test_update_reports_missing_executable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            _, global_path, service = create_configured_global_install(Path(temp_dir))

            with (
                patch.dict(os.environ, {"SKILLS_UPDATE_COMMAND": "missing update"}),
                patch("tools.skills_manager.shutil.which", return_value=None),
            ):
                result = run_third_party_update(service.repo_root, global_path)

            self.assertEqual(["Required command not found: missing"], result.errors)

    def test_update_dry_run_does_not_start_process(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            _, global_path, service = create_configured_global_install(Path(temp_dir))
            command_text = 'runner --label "two words"'

            with (
                patch.dict(os.environ, {"SKILLS_UPDATE_COMMAND": command_text}),
                patch("tools.skills_manager.shutil.which", return_value="/test/runner"),
                patch("tools.skills_manager.subprocess.run") as run,
            ):
                result = run_third_party_update(
                    service.repo_root,
                    global_path,
                    dry_run=True,
                )

            self.assertTrue(result.ok, result.errors)
            self.assertEqual([f"Would run: {command_text}"], result.messages)
            run.assert_not_called()

    def test_update_runs_structured_arguments_from_global_parent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            _, global_path, service = create_configured_global_install(Path(temp_dir))
            command_text = 'runner --label "two words"'
            completed = Mock(returncode=0)

            with (
                patch.dict(os.environ, {"SKILLS_UPDATE_COMMAND": command_text}),
                patch("tools.skills_manager.shutil.which", return_value="/test/runner"),
                patch(
                    "tools.skills_manager.subprocess.run",
                    return_value=completed,
                ) as run,
            ):
                result = run_third_party_update(service.repo_root, global_path)

            self.assertTrue(result.ok, result.errors)
            run.assert_called_once_with(
                ["runner", "--label", "two words"],
                cwd=global_path.parent,
                check=False,
            )

    def test_update_reports_nonzero_process_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            _, global_path, service = create_configured_global_install(Path(temp_dir))

            with (
                patch.dict(os.environ, {"SKILLS_UPDATE_COMMAND": "runner update"}),
                patch("tools.skills_manager.shutil.which", return_value="/test/runner"),
                patch(
                    "tools.skills_manager.subprocess.run",
                    return_value=Mock(returncode=7),
                ),
            ):
                result = run_third_party_update(service.repo_root, global_path)

            self.assertEqual(["runner update exited with 7"], result.errors)

    def test_update_cli_routes_dry_run_to_orchestrator(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = create_repo(root)
            global_path = root / ".agents" / "skills"
            stdout = io.StringIO()

            with (
                patch(
                    "tools.skills_manager.run_third_party_update",
                    return_value=OperationResult(messages=["Would update"]),
                ) as update,
                redirect_stdout(stdout),
            ):
                exit_code = main(
                    [
                        "--repo-root",
                        str(repo),
                        "--global-path",
                        str(global_path),
                        "update-third-party",
                        "--dry-run",
                    ]
                )

            self.assertEqual(0, exit_code)
            self.assertEqual("Would update\n", stdout.getvalue())
            update.assert_called_once_with(
                repo.resolve(),
                global_path,
                dry_run=True,
            )


class ThirdPartyProvenanceContractTests(unittest.TestCase):
    @staticmethod
    def _write_provenance(repo: Path, skill_name: str, digest: str) -> None:
        (repo / "third-party-skills.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "skills": {
                        skill_name: {
                            "source": "https://example.test/upstream",
                            "source_path": f"skills/{skill_name}",
                            "revision": "a" * 40,
                            "license": "MIT",
                            "reviewed_on": "2026-07-21",
                            "sha256": digest,
                        }
                    },
                }
            )
            + "\n",
            encoding="utf-8",
        )

    def test_third_party_validation_rejects_missing_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            write_skill(repo / "skills", "vendor-skill")
            (repo / ".gitignore").write_text(
                "/skills/vendor-skill/\n", encoding="utf-8"
            )

            result = SkillRegistry.load(repo).validate_third_party()

            self.assertFalse(result.ok)
            self.assertIn(
                "third-party-skills.json: missing provenance manifest for installed third-party skills",
                result.errors,
            )

    def test_third_party_validation_accepts_reviewed_optional_skill_when_absent(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            self._write_provenance(repo, "vendor-skill", "a" * 64)

            result = SkillRegistry.load(repo).validate_third_party()

            self.assertTrue(result.ok, result.errors)

    def test_third_party_validation_still_checks_absent_skill_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            self._write_provenance(repo, "vendor-skill", "a" * 64)
            provenance_path = repo / "third-party-skills.json"
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            provenance["skills"]["vendor-skill"]["revision"] = "main"
            provenance_path.write_text(
                json.dumps(provenance) + "\n", encoding="utf-8"
            )

            result = SkillRegistry.load(repo).validate_third_party()

            self.assertFalse(result.ok)
            self.assertTrue(any("full lowercase" in error for error in result.errors))

    def test_third_party_validation_rejects_content_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            skill = write_skill(repo / "skills", "vendor-skill")
            (repo / ".gitignore").write_text(
                "/skills/vendor-skill/\n", encoding="utf-8"
            )
            self._write_provenance(repo, "vendor-skill", skill_tree_sha256(skill))
            (skill / "SKILL.md").write_text(
                (skill / "SKILL.md").read_text(encoding="utf-8") + "\nDrift.\n",
                encoding="utf-8",
            )

            result = SkillRegistry.load(repo).validate_third_party()

            self.assertFalse(result.ok)
            self.assertTrue(
                any("content digest mismatch" in error for error in result.errors),
                result.errors,
            )

    def test_skill_tree_digest_rejects_visible_directory_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            skill = write_skill(repo / "skills", "vendor-skill")
            outside = repo / "outside-references"
            outside.mkdir()
            (outside / "instructions.md").write_text("Unreviewed.\n", encoding="utf-8")
            (skill / "references").symlink_to(outside, target_is_directory=True)

            with self.assertRaisesRegex(ValueError, "symbolic links"):
                skill_tree_sha256(skill)

    def test_third_party_validation_rejects_unpinned_or_unsafe_source_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            skill = write_skill(repo / "skills", "vendor-skill")
            (repo / ".gitignore").write_text(
                "/skills/vendor-skill/\n", encoding="utf-8"
            )
            self._write_provenance(repo, "vendor-skill", skill_tree_sha256(skill))
            provenance_path = repo / "third-party-skills.json"
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            entry = provenance["skills"]["vendor-skill"]
            entry["source"] = "https://token@example.test/upstream"
            entry["source_path"] = "../skills/vendor-skill"
            entry["revision"] = "main"
            provenance_path.write_text(
                json.dumps(provenance) + "\n", encoding="utf-8"
            )

            result = SkillRegistry.load(repo).validate_third_party()

            self.assertFalse(result.ok)
            self.assertTrue(any("embedded credentials" in error for error in result.errors))
            self.assertTrue(any("source_path" in error for error in result.errors))
            self.assertTrue(any("full lowercase" in error for error in result.errors))

    def test_host_specific_metadata_warns_without_granting_opencode_authority(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            skill = write_skill(repo / "skills", "vendor-skill")
            skill_file = skill / "SKILL.md"
            skill_file.write_text(
                skill_file.read_text(encoding="utf-8").replace(
                    "description: Test skill.\n",
                    "description: Test skill.\nallowed-tools: Bash(example:*)\n",
                ),
                encoding="utf-8",
            )
            (repo / ".gitignore").write_text(
                "/skills/vendor-skill/\n", encoding="utf-8"
            )
            self._write_provenance(repo, "vendor-skill", skill_tree_sha256(skill))

            result = SkillRegistry.load(repo).validate_third_party()

            self.assertTrue(result.ok, result.errors)
            self.assertTrue(
                any("not enforced by OpenCode" in warning for warning in result.warnings),
                result.warnings,
            )

    def test_checked_in_third_party_skills_have_verified_provenance(self) -> None:
        project_root = Path(__file__).parents[1]
        self.assertTrue((project_root / "third-party-skills.json").is_file())

        result = SkillRegistry.load(project_root).validate_third_party()

        self.assertEqual([], result.errors)


if __name__ == "__main__":
    unittest.main()
