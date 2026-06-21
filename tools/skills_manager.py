#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence


GLOBAL_SKILLS_PATH = Path.home() / ".agents" / "skills"
SKILLS_DIR_NAME = "skills"
LOCKFILE_NAME = ".skill-lock.json"
REQUIRED_SKILL_METADATA = ("name", "description")


@dataclass(frozen=True)
class Skill:
    name: str
    path: Path
    kind: str
    locked: bool = False
    ignored: bool = False
    source: str | None = None


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    @classmethod
    def combine(cls, results: Iterable[ValidationResult]) -> ValidationResult:
        combined = cls()
        for result in results:
            combined.errors.extend(result.errors)
            combined.warnings.extend(result.warnings)
        return combined


@dataclass
class OperationResult:
    messages: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


class SkillRegistry:
    def __init__(
        self,
        repo_root: Path,
        skill_root: Path,
        skills: Sequence[Skill],
        locked_skills: dict[str, dict],
        ignored_skill_names: set[str],
        lockfile_error: str | None = None,
    ) -> None:
        self.repo_root = repo_root
        self.root = skill_root
        self.skills = tuple(sorted(skills, key=lambda skill: skill.name))
        self.locked_skills = locked_skills
        self.ignored_skill_names = ignored_skill_names
        self.lockfile_error = lockfile_error

    @classmethod
    def load(cls, root: Path | str) -> SkillRegistry:
        repo_root = Path(root).expanduser().resolve()
        skill_root = repo_root / SKILLS_DIR_NAME
        locked_skills, lockfile_error = _read_lockfile(repo_root / LOCKFILE_NAME)
        ignored_skill_names = _read_ignored_skill_names(repo_root / ".gitignore")
        skills: list[Skill] = []

        if not skill_root.is_dir():
            return cls(repo_root, skill_root, skills, locked_skills, ignored_skill_names, lockfile_error)

        for child in sorted(skill_root.iterdir(), key=lambda item: item.name):
            if child.name.startswith(".") or not child.is_dir():
                continue
            skill_file = child / "SKILL.md"
            if not skill_file.is_file():
                continue
            locked = child.name in locked_skills
            ignored = child.name in ignored_skill_names
            kind = "third-party" if locked or ignored else "first-party"
            source = None
            if locked:
                raw_source = locked_skills[child.name].get("source")
                source = raw_source if isinstance(raw_source, str) else None
            skills.append(
                Skill(
                    name=child.name,
                    path=child,
                    kind=kind,
                    locked=locked,
                    ignored=ignored,
                    source=source,
                )
            )

        return cls(repo_root, skill_root, skills, locked_skills, ignored_skill_names, lockfile_error)

    def all(self) -> tuple[Skill, ...]:
        return self.skills

    def first_party(self) -> tuple[Skill, ...]:
        return tuple(skill for skill in self.skills if skill.kind == "first-party")

    def third_party(self) -> tuple[Skill, ...]:
        return tuple(skill for skill in self.skills if skill.kind == "third-party")

    def find(self, name: str) -> Skill | None:
        for skill in self.skills:
            if skill.name == name:
                return skill
        return None

    def validate_all(self) -> ValidationResult:
        return ValidationResult.combine(
            [
                self._validate_lockfile(),
                self._validate_skills(self.all(), label="skill"),
                self._validate_locked_installs(),
                self._validate_non_empty(),
            ]
        )

    def validate_first_party(self) -> ValidationResult:
        return ValidationResult.combine(
            [
                self._validate_skills(self.first_party(), label="first-party skill"),
                self._validate_non_empty(kind="first-party"),
            ]
        )

    def validate_third_party(self) -> ValidationResult:
        return ValidationResult.combine(
            [
                self._validate_lockfile(),
                self._validate_skills(self.third_party(), label="third-party skill"),
                self._validate_locked_installs(),
            ]
        )

    def _validate_non_empty(self, kind: str | None = None) -> ValidationResult:
        selected = self.skills if kind is None else tuple(skill for skill in self.skills if skill.kind == kind)
        if selected:
            return ValidationResult()
        label = "skills" if kind is None else f"{kind} skills"
        return ValidationResult(errors=[f"No {label} found in {self.root}"])

    def _validate_lockfile(self) -> ValidationResult:
        if self.lockfile_error is None:
            return ValidationResult()
        return ValidationResult(errors=[self.lockfile_error])

    def _validate_locked_installs(self) -> ValidationResult:
        present_names = {skill.name for skill in self.skills}
        errors = [
            f"{name}: third-party skill is listed in {LOCKFILE_NAME} but missing"
            for name in sorted(self.locked_skills)
            if name not in present_names
        ]
        return ValidationResult(errors=errors)

    def _validate_skills(self, skills: Sequence[Skill], *, label: str) -> ValidationResult:
        results = [validate_skill(skill, label=label) for skill in skills]
        return ValidationResult.combine(results)


class GlobalInstallService:
    def __init__(self, repo_root: Path | str, global_path: Path | str = GLOBAL_SKILLS_PATH) -> None:
        self.repo_root = Path(repo_root).expanduser().resolve()
        self.skill_root = self.repo_root / SKILLS_DIR_NAME
        self.global_path = Path(global_path).expanduser()

    def setup(self, *, dry_run: bool = False) -> OperationResult:
        if not self.repo_root.is_dir():
            return OperationResult(errors=[f"Repository root does not exist: {self.repo_root}"])
        if not self.skill_root.is_dir():
            return OperationResult(errors=[f"Skills directory does not exist: {self.skill_root}"])

        if self.global_path.is_symlink():
            target = self._resolve_global_path()
            if target == self.skill_root:
                return OperationResult(
                    messages=[f"Global skills symlink already points to {self.skill_root}"]
                )
            return OperationResult(
                errors=[
                    f"{self.global_path} is a symlink to {target}, not {self.skill_root}. "
                    "Remove or move it manually before running setup."
                ]
            )

        if self.global_path.exists():
            return OperationResult(
                errors=[
                    f"{self.global_path} exists and is not a symlink. "
                    "Move it aside manually before running setup."
                ]
            )

        if dry_run:
            return OperationResult(
                messages=[f"Would create symlink {self.global_path} -> {self.skill_root}"]
            )

        self.global_path.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(self.skill_root, self.global_path)
        return OperationResult(messages=[f"Created {self.global_path} -> {self.skill_root}"])

    def verify(self) -> OperationResult:
        if not self.global_path.is_symlink():
            if self.global_path.exists():
                return OperationResult(errors=[f"{self.global_path} exists but is not a symlink"])
            return OperationResult(errors=[f"{self.global_path} does not exist"])

        target = self._resolve_global_path()
        if target != self.skill_root:
            return OperationResult(
                errors=[f"{self.global_path} points to {target}, expected {self.skill_root}"]
            )

        registry = SkillRegistry.load(self.repo_root)
        missing = [
            skill.name
            for skill in registry.all()
            if not (self.global_path / skill.name / "SKILL.md").is_file()
        ]
        if missing:
            errors = [f"{name}: missing through global symlink" for name in missing]
            return OperationResult(errors=errors)

        return OperationResult(
            messages=[
                f"Global skills symlink is configured: {self.global_path} -> {self.skill_root}",
                f"Visible skills: {len(registry.all())}",
            ]
        )

    def uninstall(self, *, dry_run: bool = False) -> OperationResult:
        if not self.global_path.exists() and not self.global_path.is_symlink():
            return OperationResult(messages=[f"No global skills path found at {self.global_path}"])

        if not self.global_path.is_symlink():
            return OperationResult(
                errors=[f"{self.global_path} is not a symlink; refusing to remove it"]
            )

        target = self._resolve_global_path()
        if target != self.skill_root:
            return OperationResult(
                errors=[f"{self.global_path} points to {target}, not {self.skill_root}; refusing to remove it"]
            )

        if dry_run:
            return OperationResult(messages=[f"Would remove symlink {self.global_path}"])

        self.global_path.unlink()
        return OperationResult(messages=[f"Removed symlink {self.global_path}"])

    def sync_lockfile(self, *, dry_run: bool = False) -> OperationResult:
        verify_result = self.verify()
        if not verify_result.ok:
            return verify_result

        repo_lockfile = self.repo_root / LOCKFILE_NAME
        if not repo_lockfile.is_file():
            return OperationResult(errors=[f"Missing repository lockfile: {repo_lockfile}"])

        global_lockfile = self.global_path.parent / LOCKFILE_NAME
        if global_lockfile.exists() and repo_lockfile.read_bytes() == global_lockfile.read_bytes():
            return OperationResult(messages=[f"{global_lockfile} already matches {repo_lockfile}"])

        if dry_run:
            return OperationResult(messages=[f"Would copy {repo_lockfile} to {global_lockfile}"])

        shutil.copy2(repo_lockfile, global_lockfile)
        return OperationResult(messages=[f"Copied {repo_lockfile} to {global_lockfile}"])

    def _resolve_global_path(self) -> Path:
        try:
            return self.global_path.resolve(strict=True)
        except FileNotFoundError:
            return self.global_path.resolve(strict=False)


def validate_skill(skill: Skill, *, label: str) -> ValidationResult:
    skill_file = skill.path / "SKILL.md"
    if not skill_file.is_file():
        return ValidationResult(errors=[f"{skill.name}: missing SKILL.md"])

    metadata, error = _read_skill_metadata(skill_file)
    if error is not None:
        return ValidationResult(errors=[f"{skill.name}: {error}"])

    errors = []
    for key in REQUIRED_SKILL_METADATA:
        if key not in metadata or not metadata[key].strip():
            errors.append(f"{skill.name}: SKILL.md front matter must define {key}")

    metadata_name = metadata.get("name", "").strip("\"'")
    if metadata_name and metadata_name != skill.name:
        errors.append(
            f"{skill.name}: SKILL.md name is {metadata_name!r}, expected {skill.name!r}"
        )

    return ValidationResult(errors=errors)


def _read_lockfile(path: Path) -> tuple[dict[str, dict], str | None]:
    if not path.exists():
        return {}, None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return {}, f"{LOCKFILE_NAME}: invalid JSON: {error}"

    raw_skills = data.get("skills")
    if raw_skills is None:
        return {}, None
    if not isinstance(raw_skills, dict):
        return {}, f"{LOCKFILE_NAME}: skills must be an object"

    locked_skills: dict[str, dict] = {}
    for name, metadata in raw_skills.items():
        if not isinstance(name, str):
            return {}, f"{LOCKFILE_NAME}: skill names must be strings"
        if metadata is not None and not isinstance(metadata, dict):
            return {}, f"{LOCKFILE_NAME}: metadata for {name} must be an object"
        locked_skills[name] = metadata or {}
    return locked_skills, None


def _read_ignored_skill_names(path: Path) -> set[str]:
    if not path.exists():
        return set()
    ignored = set()
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("!"):
            continue
        if not line.endswith("/"):
            continue
        normalized = line.strip("/")
        parts = normalized.split("/")
        if len(parts) == 1 and parts[0]:
            ignored.add(parts[0])
        elif len(parts) == 2 and parts[0] == SKILLS_DIR_NAME and parts[1]:
            ignored.add(parts[1])
    return ignored


def _read_skill_metadata(path: Path) -> tuple[dict[str, str], str | None]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError as error:
        return {}, f"SKILL.md must be UTF-8: {error}"

    if not lines:
        return {}, "SKILL.md is empty"
    if lines[0].strip() != "---":
        return {}, "SKILL.md must start with YAML front matter"

    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
    if end_index is None:
        return {}, "SKILL.md front matter is not closed"

    metadata: dict[str, str] = {}
    for line in lines[1:end_index]:
        if not line.strip() or line.startswith((" ", "\t", "-")):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key:
            metadata[key] = value.strip().strip("\"'")
    return metadata, None


def print_skills(skills: Sequence[Skill]) -> int:
    if not skills:
        print("No skills found.")
        return 0
    for skill in skills:
        details = []
        if skill.locked:
            details.append("locked")
        if skill.ignored:
            details.append("ignored")
        suffix = f" ({', '.join(details)})" if details else ""
        print(f"{skill.name}\t{skill.kind}{suffix}")
    return 0


def print_inspection(skill: Skill) -> int:
    print(f"name: {skill.name}")
    print(f"type: {skill.kind}")
    print(f"path: {skill.path}")
    print(f"locked: {str(skill.locked).lower()}")
    print(f"ignored: {str(skill.ignored).lower()}")
    if skill.source:
        print(f"source: {skill.source}")
    return 0


def emit_validation(result: ValidationResult) -> int:
    for warning in result.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    for error in result.errors:
        print(f"error: {error}", file=sys.stderr)
    if result.ok:
        print("Validation passed.")
        return 0
    return 1


def emit_operation(result: OperationResult) -> int:
    for message in result.messages:
        print(message)
    for warning in result.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    for error in result.errors:
        print(f"error: {error}", file=sys.stderr)
    return 0 if result.ok else 1


def clean(root: Path) -> OperationResult:
    removed = []
    for base in (root / "tools", root / "tests"):
        if not base.exists():
            continue
        for path in base.rglob("__pycache__"):
            if path.is_dir():
                shutil.rmtree(path)
                removed.append(path)
        for path in base.rglob("*.py[co]"):
            if path.is_file():
                path.unlink()
                removed.append(path)
    if not removed:
        return OperationResult(messages=["No Python cache files found."])
    return OperationResult(messages=[f"Removed {len(removed)} Python cache paths."])


def run_third_party_update(repo_root: Path, global_path: Path, *, dry_run: bool = False) -> OperationResult:
    verify_result = GlobalInstallService(repo_root, global_path).verify()
    if not verify_result.ok:
        return verify_result

    command_text = os.environ.get("SKILLS_UPDATE_COMMAND", "bunx skills update")
    command = command_text.split()
    if not command:
        return OperationResult(errors=["SKILLS_UPDATE_COMMAND is empty"])
    if shutil.which(command[0]) is None:
        return OperationResult(errors=[f"Required command not found: {command[0]}"])

    if dry_run:
        return OperationResult(messages=[f"Would run: {command_text}"])

    completed = subprocess.run(command, cwd=global_path.parent, check=False)
    if completed.returncode != 0:
        return OperationResult(errors=[f"{command_text} exited with {completed.returncode}"])
    return OperationResult(messages=[f"Completed: {command_text}"])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage the global agent skills repository.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--global-path",
        type=Path,
        default=GLOBAL_SKILLS_PATH,
        help="Global skills path. Defaults to ~/.agents/skills.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    list_parser = subcommands.add_parser("list", help="List discovered skills.")
    list_parser.add_argument(
        "--kind",
        choices=("all", "first-party", "third-party"),
        default="all",
        help="Skill type to list.",
    )

    inspect_parser = subcommands.add_parser("inspect", help="Inspect one skill.")
    inspect_parser.add_argument("name", help="Skill name to inspect.")

    validate_parser = subcommands.add_parser("validate", help="Validate skills.")
    validate_parser.add_argument(
        "--kind",
        choices=("all", "first-party", "third-party"),
        default="all",
        help="Skill type to validate.",
    )

    setup_parser = subcommands.add_parser("setup", help="Create the global skills symlink.")
    setup_parser.add_argument("--dry-run", action="store_true", help="Report changes without applying them.")

    verify_parser = subcommands.add_parser("verify", help="Verify the global skills symlink.")
    verify_parser.set_defaults(_verify=True)

    uninstall_parser = subcommands.add_parser("uninstall", help="Remove this repo's global symlink.")
    uninstall_parser.add_argument("--dry-run", action="store_true", help="Report changes without applying them.")

    doctor_parser = subcommands.add_parser("doctor", help="Run validation and global install verification.")
    doctor_parser.set_defaults(_doctor=True)

    sync_parser = subcommands.add_parser(
        "sync-third-party-lock",
        help="Copy the repository lockfile to ~/.agents/.skill-lock.json.",
    )
    sync_parser.add_argument("--dry-run", action="store_true", help="Report changes without applying them.")

    update_parser = subcommands.add_parser(
        "update-third-party",
        help="Run the configured third-party skill update command.",
    )
    update_parser.add_argument("--dry-run", action="store_true", help="Report changes without applying them.")

    clean_parser = subcommands.add_parser("clean", help="Remove Python cache files.")
    clean_parser.set_defaults(_clean=True)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = args.repo_root.expanduser().resolve()
    global_path = args.global_path.expanduser()
    registry = SkillRegistry.load(repo_root)

    if args.command == "list":
        if args.kind == "first-party":
            return print_skills(registry.first_party())
        if args.kind == "third-party":
            return print_skills(registry.third_party())
        return print_skills(registry.all())

    if args.command == "inspect":
        skill = registry.find(args.name)
        if skill is None:
            print(f"error: skill not found: {args.name}", file=sys.stderr)
            return 1
        return print_inspection(skill)

    if args.command == "validate":
        if args.kind == "first-party":
            return emit_validation(registry.validate_first_party())
        if args.kind == "third-party":
            return emit_validation(registry.validate_third_party())
        return emit_validation(registry.validate_all())

    service = GlobalInstallService(repo_root, global_path)
    if args.command == "setup":
        return emit_operation(service.setup(dry_run=args.dry_run))
    if args.command == "verify":
        return emit_operation(service.verify())
    if args.command == "uninstall":
        return emit_operation(service.uninstall(dry_run=args.dry_run))
    if args.command == "doctor":
        validation = registry.validate_all()
        validation_code = emit_validation(validation)
        operation_code = emit_operation(service.verify())
        return 0 if validation_code == 0 and operation_code == 0 else 1
    if args.command == "sync-third-party-lock":
        return emit_operation(service.sync_lockfile(dry_run=args.dry_run))
    if args.command == "update-third-party":
        return emit_operation(run_third_party_update(repo_root, global_path, dry_run=args.dry_run))
    if args.command == "clean":
        return emit_operation(clean(repo_root))

    print(f"error: unsupported command: {args.command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
