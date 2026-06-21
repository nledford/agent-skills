import json
import os
import tempfile
import unittest
from pathlib import Path

from tools.skills_manager import (
    GlobalInstallService,
    SkillRegistry,
    ValidationResult,
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
