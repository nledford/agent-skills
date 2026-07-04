import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from tools.skills_manager import (
    GlobalInstallService,
    SkillRegistry,
    ValidationResult,
    emit_validation,
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


def write_taxonomy(repo: Path, names: list[str]) -> Path:
    docs = repo / "docs"
    docs.mkdir()
    rows = "\n".join(
        f"| `{name}` | Test purpose. | Keep. |"
        for name in names
    )
    path = docs / "skill-taxonomy.md"
    path.write_text(
        "# Skill Taxonomy\n\n"
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

            result = SkillRegistry.load(repo).validate_all()

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

            result = SkillRegistry.load(repo).validate_all()

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

    def test_security_sensitive_first_party_skill_warns_for_missing_security_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            write_skill(repo / "skills", "python-engineering")
            write_taxonomy(repo, ["python-engineering"])

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertTrue(result.ok)
            self.assertEqual(
                [
                    "python-engineering: SKILL.md should link to security-review for security-sensitive work",
                    "python-engineering: SKILL.md should link to security-review-evidence for security-sensitive work",
                ],
                result.warnings,
            )

    def test_security_sensitive_first_party_skill_accepts_required_security_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            write_skill(repo / "skills", "security-review")
            write_skill(repo / "skills", "security-review-evidence")
            skill = write_skill(repo / "skills", "python-engineering")
            write_taxonomy(
                repo,
                ["python-engineering", "security-review", "security-review-evidence"],
            )
            (skill / "SKILL.md").write_text(
                "---\n"
                "name: python-engineering\n"
                "description: Test skill.\n"
                "---\n\n"
                "# python-engineering\n\n"
                "Load [`security-review`](../security-review/SKILL.md).\n"
                "Use [`security-review-evidence`](../security-review-evidence/SKILL.md).\n",
                encoding="utf-8",
            )

            result = SkillRegistry.load(repo).validate_first_party()

            self.assertTrue(result.ok)
            self.assertEqual([], result.warnings)

    def test_security_sensitive_link_warnings_ignore_third_party_skills(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = create_repo(Path(temp_dir))
            write_skill(repo / "skills", "python-engineering")
            (repo / ".gitignore").write_text("/skills/python-engineering/\n", encoding="utf-8")

            result = SkillRegistry.load(repo).validate_all()

            self.assertTrue(result.ok)
            self.assertEqual([], result.warnings)

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


if __name__ == "__main__":
    unittest.main()
