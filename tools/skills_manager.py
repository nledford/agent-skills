#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence
from urllib.parse import unquote, urlsplit

try:
    from .project_neutrality import project_neutrality_errors
    from .skill_provenance import validate_provenance_entry
except ImportError:  # Direct script execution.
    from project_neutrality import project_neutrality_errors
    from skill_provenance import validate_provenance_entry


GLOBAL_SKILLS_PATH = Path.home() / ".agents" / "skills"
SKILLS_DIR_NAME = "skills"
LOCKFILE_NAME = ".skill-lock.json"
THIRD_PARTY_PROVENANCE_NAME = "third-party-skills.json"
THIRD_PARTY_PROVENANCE_VERSION = 1
REQUIRED_SKILL_METADATA = ("name", "description")
HOST_SPECIFIC_SKILL_METADATA = ("allowed-tools", "hidden", "user-invocable")
LOCAL_LINK_RE = re.compile(r"(?<![A-Za-z0-9_`])!?\[[^\]]+\]\(([^)]+)\)")
TAXONOMY_DOC = Path("docs") / "skill-taxonomy.md"
TAXONOMY_CATEGORY_HEADING = "## Taxonomy"
TAXONOMY_INVENTORY_HEADING = "## Current First-Party Inventory"
TAXONOMY_INVENTORY_ROW_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|")
TAXONOMY_SKILL_REFERENCE_RE = re.compile(r"`([^`]+)`")
TAXONOMY_CATEGORY_TABLE_HEADER = ("Category", "Skills", "Boundary")
TAXONOMY_CATEGORY_TABLE_DIVIDER = ("---", "---", "---")
TAXONOMY_API_CONTRACT_CATEGORY = "API design and contracts"
TAXONOMY_OBSERVABILITY_CATEGORY = "Observability and operations"
SECURITY_LINK_REQUIRED_SKILLS = frozenset(
    {
        "ci-release-engineering",
        "code-review",
        "container-engineering",
        "git-commit",
        "git-workflows",
        "github-mcp-operations",
        "javascript-typescript-engineering",
        "justfiles",
        "postgresql-sql-engineering",
        "python-engineering",
        "powershell-engineering",
        "ruby-engineering",
        "rust-async-web",
        "rust-engineering",
        "rust-persistence-sql",
        "sql-engineering",
        "sqlite-sql-engineering",
    }
)
REQUIRED_SECURITY_LINKS = ("security-review", "security-review-evidence")
REQUIRED_API_SECURITY_LINKS = ("security-review",)
GIT_SKILLS = frozenset({"git-commit", "git-workflows"})
REQUIRED_GIT_SKILL_LINKS = ("git-commit", "git-workflows")
MCP_ROUTING_SKILLS = frozenset({"github-mcp-operations", "hound-web-research"})
REQUIRED_MCP_ROUTING_SKILL_LINKS = (
    "github-mcp-operations",
    "hound-web-research",
)
FORBIDDEN_SKILL_SOURCE_PROJECT_IDENTIFIERS = (
    "engineering-review-board",
    "chidori",
)


@dataclass(frozen=True)
class Skill:
    name: str
    path: Path
    kind: str
    locked: bool = False
    ignored: bool = False
    source: str | None = None


@dataclass(frozen=True)
class RelatedSkillLinkRule:
    required_links: tuple[str, ...]
    reason: str
    taxonomy_categories: tuple[str, ...] = ()
    skill_names: frozenset[str] = field(default_factory=frozenset)


REQUIRED_RELATED_SKILL_LINK_RULES = (
    RelatedSkillLinkRule(
        required_links=REQUIRED_API_SECURITY_LINKS,
        reason="security-sensitive API contract work",
        taxonomy_categories=(TAXONOMY_API_CONTRACT_CATEGORY,),
    ),
    RelatedSkillLinkRule(
        required_links=REQUIRED_SECURITY_LINKS,
        reason="sensitive telemetry or security-evidence handling",
        taxonomy_categories=(TAXONOMY_OBSERVABILITY_CATEGORY,),
    ),
    RelatedSkillLinkRule(
        required_links=REQUIRED_SECURITY_LINKS,
        reason="security-sensitive work",
        taxonomy_categories=("Security review",),
        skill_names=SECURITY_LINK_REQUIRED_SKILLS,
    ),
    RelatedSkillLinkRule(
        required_links=REQUIRED_GIT_SKILL_LINKS,
        reason="related Git operations",
        skill_names=GIT_SKILLS,
    ),
    RelatedSkillLinkRule(
        required_links=REQUIRED_MCP_ROUTING_SKILL_LINKS,
        reason="MCP server selection",
        skill_names=MCP_ROUTING_SKILLS,
    ),
)


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
                self._validate_skills(self.all()),
                self._validate_required_related_skill_links(),
                self._validate_taxonomy_inventory(),
                self._validate_locked_installs(),
                self._validate_third_party_provenance(),
                self._validate_non_empty(),
            ]
        )

    def validate_first_party(self) -> ValidationResult:
        return ValidationResult.combine(
            [
                self._validate_skills(self.first_party()),
                self._validate_required_related_skill_links(),
                self._validate_taxonomy_inventory(),
                self._validate_non_empty(kind="first-party"),
            ]
        )

    def validate_third_party(self) -> ValidationResult:
        return ValidationResult.combine(
            [
                self._validate_lockfile(),
                self._validate_skills(self.third_party()),
                self._validate_locked_installs(),
                self._validate_third_party_provenance(),
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
    def _validate_third_party_provenance(self) -> ValidationResult:
        provenance_path = self.repo_root / THIRD_PARTY_PROVENANCE_NAME
        third_party = {skill.name: skill for skill in self.third_party()}
        if not third_party and not provenance_path.exists():
            return ValidationResult()
        if not provenance_path.is_file():
            return ValidationResult(
                errors=[
                    f"{THIRD_PARTY_PROVENANCE_NAME}: missing provenance manifest for "
                    "installed third-party skills"
                ]
            )

        data, error = _read_third_party_provenance(provenance_path)
        if error is not None:
            return ValidationResult(errors=[error])
        assert data is not None

        entries = data["skills"]
        installed_names = set(third_party)
        entry_names = set(entries)
        errors = [
            f"{THIRD_PARTY_PROVENANCE_NAME}: installed third-party skill missing provenance: {name}"
            for name in sorted(installed_names - entry_names)
        ]
        for name in sorted(entry_names):
            digest, entry_errors = validate_provenance_entry(
                name,
                entries[name],
                manifest_name=THIRD_PARTY_PROVENANCE_NAME,
            )
            errors.extend(entry_errors)
            if digest is not None and name in third_party:
                errors.extend(
                    self._installed_digest_errors(
                        name,
                        third_party[name].path,
                        digest,
                    )
                )
        return ValidationResult(errors=errors)

    @staticmethod
    def _installed_digest_errors(
        name: str,
        path: Path,
        expected_digest: str,
    ) -> list[str]:
        prefix = f"{THIRD_PARTY_PROVENANCE_NAME}: {name}"
        try:
            actual_digest = skill_tree_sha256(path)
        except (OSError, ValueError) as error:
            return [f"{prefix}: cannot hash installed content: {error}"]
        if actual_digest == expected_digest:
            return []
        return [
            f"{prefix}: content digest mismatch; expected {expected_digest}, "
            f"found {actual_digest}"
        ]



    def _validate_skills(self, skills: Sequence[Skill]) -> ValidationResult:
        results = [validate_skill(skill) for skill in skills]
        return ValidationResult.combine(results)

    def _validate_taxonomy_inventory(self) -> ValidationResult:
        first_party_names = {skill.name for skill in self.first_party()}
        if not first_party_names:
            return ValidationResult()

        taxonomy_path = self.repo_root / TAXONOMY_DOC
        if not taxonomy_path.is_file():
            return ValidationResult(errors=[f"{TAXONOMY_DOC}: missing taxonomy document"])

        inventory_names, error = _read_taxonomy_inventory_names(taxonomy_path)
        if error is not None:
            return ValidationResult(errors=[error])

        missing = sorted(first_party_names - inventory_names)
        extra = sorted(inventory_names - first_party_names)
        errors = [
            f"{TAXONOMY_DOC}: first-party skill missing from inventory: {name}"
            for name in missing
        ]
        errors.extend(
            f"{TAXONOMY_DOC}: inventory lists non-first-party skill: {name}"
            for name in extra
        )
        return ValidationResult(errors=errors)

    def _validate_required_related_skill_links(self) -> ValidationResult:
        return _validate_required_related_skill_links(
            self.first_party(),
            taxonomy_path=self.repo_root / TAXONOMY_DOC,
        )


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


def validate_skill(skill: Skill) -> ValidationResult:
    skill_file = skill.path / "SKILL.md"
    if not skill_file.is_file():
        return ValidationResult(errors=[f"{skill.name}: missing SKILL.md"])

    metadata, error = _read_skill_metadata(skill_file)
    if error is not None:
        return ValidationResult(errors=[f"{skill.name}: {error}"])

    errors = []
    warnings: list[str] = []
    for key in REQUIRED_SKILL_METADATA:
        if key not in metadata or not metadata[key].strip():
            errors.append(f"{skill.name}: SKILL.md front matter must define {key}")

    metadata_name = metadata.get("name", "").strip("\"'")
    if metadata_name and metadata_name != skill.name:
        errors.append(
            f"{skill.name}: SKILL.md name is {metadata_name!r}, expected {skill.name!r}"
        )

    warnings.extend(
        f"{skill.name}: SKILL.md front matter '{key}' is cross-host metadata and "
        "is not enforced by OpenCode; use agent permission maps for runtime authority"
        for key in HOST_SPECIFIC_SKILL_METADATA
        if key in metadata
    )

    if skill.kind == "first-party":
        resource_result = _validate_skill_resources(skill)
        errors.extend(resource_result.errors)
        neutrality_result = _validate_skill_project_neutrality(skill)
        errors.extend(neutrality_result.errors)

    return ValidationResult(errors=errors, warnings=warnings)


def _validate_skill_project_neutrality(skill: Skill) -> ValidationResult:
    errors: list[str] = []
    for path in sorted(skill.path.rglob("*")):
        if not path.is_file() or _is_hidden_path(path, skill.path):
            continue
        relative_path = path.relative_to(skill.path)
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        errors.extend(
            project_neutrality_errors(
                text,
                location=f"{skill.name}/{relative_path}",
                forbidden_identifiers=FORBIDDEN_SKILL_SOURCE_PROJECT_IDENTIFIERS,
            )
        )
    return ValidationResult(errors=errors)


def _validate_required_related_skill_links(
    skills: Sequence[Skill], *, taxonomy_path: Path
) -> ValidationResult:
    if not taxonomy_path.is_file():
        return ValidationResult()
    taxonomy_category_skill_names, taxonomy_error = (
        _read_taxonomy_category_skill_names(taxonomy_path)
    )
    if taxonomy_error is not None:
        return ValidationResult(errors=[taxonomy_error])
    warnings = []
    for skill in skills:
        required_links = _required_related_skill_links_for_skill(
            skill.name,
            taxonomy_category_skill_names,
        )
        if not required_links:
            continue
        try:
            linked_skills = _read_linked_skill_names(
                skill.path / "SKILL.md", skill_root=skill.path.parent
            )
        except UnicodeDecodeError:
            continue
        warnings.extend(
            f"{skill.name}: SKILL.md should link to {required_link} for {reason}"
            for required_link, reason in required_links
            if required_link not in linked_skills
        )
    return ValidationResult(warnings=warnings)


def _required_related_skill_links_for_skill(
    skill_name: str,
    taxonomy_category_skill_names: dict[str, set[str]],
) -> list[tuple[str, str]]:
    required_links: list[tuple[str, str]] = []
    seen_links: set[str] = set()
    for rule in REQUIRED_RELATED_SKILL_LINK_RULES:
        rule_skill_names = set(rule.skill_names)
        for category in rule.taxonomy_categories:
            rule_skill_names.update(taxonomy_category_skill_names.get(category, set()))
        if skill_name not in rule_skill_names:
            continue
        for required_link in rule.required_links:
            if required_link == skill_name or required_link in seen_links:
                continue
            required_links.append((required_link, rule.reason))
            seen_links.add(required_link)
    return required_links


def _read_linked_skill_names(skill_file: Path, *, skill_root: Path) -> set[str]:
    linked_skill_names = set()
    resolved_skill_root = skill_root.resolve(strict=False)
    for raw_link in _read_local_markdown_links(skill_file):
        target = _resolve_local_link(skill_file, raw_link)
        if target is None:
            continue
        linked_skill_path = target.parent if target.name == "SKILL.md" else target
        if linked_skill_path.parent == resolved_skill_root:
            linked_skill_names.add(linked_skill_path.name)
    return linked_skill_names


def _validate_skill_resources(skill: Skill) -> ValidationResult:
    resource_files = {
        path
        for path in skill.path.rglob("*")
        if path.is_file()
        and path.name != "SKILL.md"
        and not _is_hidden_path(path, skill.path)
    }
    reachable, errors = _reachable_skill_resources(skill)
    errors.extend(
        f"{skill.name}: resource file is not reachable from SKILL.md: "
        f"{resource_file.relative_to(skill.path)}"
        for resource_file in sorted(resource_files - reachable)
    )
    return ValidationResult(errors=errors)


def _reachable_skill_resources(skill: Skill) -> tuple[set[Path], list[str]]:
    skill_file = skill.path / "SKILL.md"
    reachable = {skill_file}
    pending = [skill_file]
    errors: list[str] = []
    while pending:
        source = pending.pop()
        if source.suffix.lower() == ".md":
            errors.extend(
                _collect_linked_resources(
                    skill,
                    source,
                    reachable,
                    pending,
                )
            )
    return reachable, errors


def _collect_linked_resources(
    skill: Skill,
    source: Path,
    reachable: set[Path],
    pending: list[Path],
) -> list[str]:
    errors: list[str] = []
    for raw_link in _read_local_markdown_links(source):
        target = _resolve_local_link(source, raw_link)
        if target is None:
            continue
        if not target.exists():
            relative_source = source.relative_to(skill.path)
            errors.append(
                f"{skill.name}: broken local link in {relative_source}: {raw_link}"
            )
            continue
        if target.is_dir() or target in reachable:
            continue
        reachable.add(target)
        if _is_relative_to(target, skill.path):
            pending.append(target)
    return errors


def _read_local_markdown_links(path: Path) -> list[str]:
    links = []
    for match in LOCAL_LINK_RE.finditer(path.read_text(encoding="utf-8")):
        raw_link = match.group(1).strip()
        if raw_link:
            links.append(raw_link)
    return links


def _resolve_local_link(source: Path, raw_link: str) -> Path | None:
    link = _extract_link_target(raw_link)
    parsed = urlsplit(link)
    if parsed.scheme or parsed.netloc or link.startswith("#") or link.startswith("/"):
        return None
    if not parsed.path:
        return None
    return (source.parent / unquote(parsed.path)).resolve(strict=False)


def _extract_link_target(raw_link: str) -> str:
    stripped = raw_link.strip()
    if stripped.startswith("<"):
        end_index = stripped.find(">")
        if end_index != -1:
            return stripped[1:end_index]
    return stripped.split()[0].strip("<>")


def _is_hidden_path(path: Path, root: Path) -> bool:
    relative_parts = path.relative_to(root).parts
    return any(part.startswith(".") for part in relative_parts)


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


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


def _read_third_party_provenance(path: Path) -> tuple[dict | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return None, f"{THIRD_PARTY_PROVENANCE_NAME}: invalid JSON: {error}"
    if not isinstance(data, dict):
        return None, f"{THIRD_PARTY_PROVENANCE_NAME}: root must be an object"
    if data.get("version") != THIRD_PARTY_PROVENANCE_VERSION:
        return None, (
            f"{THIRD_PARTY_PROVENANCE_NAME}: version must be "
            f"{THIRD_PARTY_PROVENANCE_VERSION}"
        )
    if not isinstance(data.get("skills"), dict):
        return None, f"{THIRD_PARTY_PROVENANCE_NAME}: skills must be an object"
    if any(not isinstance(name, str) or not name for name in data["skills"]):
        return None, f"{THIRD_PARTY_PROVENANCE_NAME}: skill names must be non-empty strings"
    return data, None


def skill_tree_sha256(skill_path: Path) -> str:
    """Hash visible regular files with stable relative-path framing."""
    if skill_path.is_symlink():
        raise ValueError("symbolic links are not supported: .")
    visible_paths = [
        path
        for path in skill_path.rglob("*")
        if not _is_hidden_path(path, skill_path)
    ]
    symlinks = [path for path in visible_paths if path.is_symlink()]
    if symlinks:
        relative_path = symlinks[0].relative_to(skill_path)
        raise ValueError(f"symbolic links are not supported: {relative_path}")
    files = [path for path in visible_paths if path.is_file()]
    if not files:
        raise ValueError("skill directory contains no visible regular files")
    digest = hashlib.sha256()
    for path in sorted(files, key=lambda candidate: candidate.relative_to(skill_path).as_posix()):
        relative_path = path.relative_to(skill_path).as_posix().encode("utf-8")
        digest.update(relative_path)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


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

    end_index = next(
        (
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.strip() == "---"
        ),
        None,
    )
    if end_index is None:
        return {}, "SKILL.md front matter is not closed"
    return _parse_skill_metadata_lines(lines[1:end_index]), None


def _parse_skill_metadata_lines(lines: Sequence[str]) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in lines:
        if not line.strip() or line.startswith((" ", "\t", "-")) or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key:
            metadata[key] = value.strip().strip("\"'")
    return metadata


def _read_taxonomy_category_skill_names(
    path: Path,
) -> tuple[dict[str, set[str]], str | None]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return {}, f"{TAXONOMY_DOC}: taxonomy document is not readable UTF-8"
    try:
        start_index = lines.index(TAXONOMY_CATEGORY_HEADING)
    except ValueError:
        return {}, f"{TAXONOMY_DOC}: missing {TAXONOMY_CATEGORY_HEADING!r} table"

    table_lines = _taxonomy_table_lines(lines[start_index + 1 :])
    malformed_error = f"{TAXONOMY_DOC}: malformed {TAXONOMY_CATEGORY_HEADING!r} table"
    if not _valid_taxonomy_table_header(table_lines):
        return {}, malformed_error
    categories = _parse_taxonomy_category_rows(table_lines[2:])
    if categories is None:
        return {}, malformed_error
    return categories, None


def _taxonomy_table_lines(lines: Sequence[str]) -> list[str]:
    table_lines: list[str] = []
    for line in lines:
        if line.startswith("## "):
            break
        if line.strip():
            table_lines.append(line)
    return table_lines


def _taxonomy_table_cells(line: str) -> tuple[str, ...] | None:
    if not line.startswith("|") or not line.endswith("|"):
        return None
    return tuple(cell.strip() for cell in line.strip("|").split("|"))


def _valid_taxonomy_table_header(table_lines: Sequence[str]) -> bool:
    return (
        len(table_lines) >= 3
        and _taxonomy_table_cells(table_lines[0]) == TAXONOMY_CATEGORY_TABLE_HEADER
        and _taxonomy_table_cells(table_lines[1]) == TAXONOMY_CATEGORY_TABLE_DIVIDER
    )


def _parse_taxonomy_category_rows(
    lines: Sequence[str],
) -> dict[str, set[str]] | None:
    categories: dict[str, set[str]] = {}
    for line in lines:
        cells = _taxonomy_table_cells(line)
        if cells is None or len(cells) != 3 or not all(cells):
            return None
        skill_names = set(TAXONOMY_SKILL_REFERENCE_RE.findall(cells[1]))
        if not skill_names or cells[0] in categories:
            return None
        categories[cells[0]] = skill_names
    return categories


def _read_taxonomy_inventory_names(path: Path) -> tuple[set[str], str | None]:
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        start_index = lines.index(TAXONOMY_INVENTORY_HEADING)
    except ValueError:
        return set(), f"{TAXONOMY_DOC}: missing {TAXONOMY_INVENTORY_HEADING!r} section"

    inventory: set[str] = set()
    for line in lines[start_index + 1 :]:
        if line.startswith("## "):
            break
        match = TAXONOMY_INVENTORY_ROW_RE.match(line)
        if match:
            name = match.group(1)
            if name in inventory:
                return set(), f"{TAXONOMY_DOC}: duplicate first-party inventory entry: {name}"
            inventory.add(name)

    if not inventory:
        return set(), f"{TAXONOMY_DOC}: current first-party inventory is empty"
    return inventory, None


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


def print_third_party_digests(skills: Sequence[Skill]) -> int:
    if not skills:
        print("No third-party skills found.")
        return 0
    for skill in skills:
        try:
            digest = skill_tree_sha256(skill.path)
        except (OSError, ValueError) as error:
            print(f"error: {skill.name}: {error}", file=sys.stderr)
            return 1
        print(f"{skill.name}\t{digest}")
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


def run_third_party_update(
    repo_root: Path,
    global_path: Path,
    *,
    dry_run: bool = False,
) -> OperationResult:
    verify_result = GlobalInstallService(repo_root, global_path).verify()
    if not verify_result.ok:
        return verify_result

    command_text = os.environ.get("SKILLS_UPDATE_COMMAND", "npx skills update")
    try:
        command = shlex.split(command_text)
    except ValueError:
        return OperationResult(
            errors=["SKILLS_UPDATE_COMMAND is not valid shell-like argument text"]
        )
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

    subcommands.add_parser(
        "third-party-digests",
        help="Print deterministic content digests for installed third-party skills.",
    )

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
    registry = SkillRegistry.load(repo_root)
    registry_result = _run_registry_command(args, registry)
    if registry_result is not None:
        return registry_result
    service = GlobalInstallService(repo_root, args.global_path.expanduser())
    return _run_service_command(args, registry, service)


def _run_registry_command(
    args: argparse.Namespace,
    registry: SkillRegistry,
) -> int | None:
    if args.command == "list":
        selected = {
            "first-party": registry.first_party,
            "third-party": registry.third_party,
            "all": registry.all,
        }[args.kind]()
        return print_skills(selected)
    if args.command == "inspect":
        skill = registry.find(args.name)
        if skill is None:
            print(f"error: skill not found: {args.name}", file=sys.stderr)
            return 1
        return print_inspection(skill)
    if args.command == "third-party-digests":
        return print_third_party_digests(registry.third_party())
    if args.command == "validate":
        validator = {
            "first-party": registry.validate_first_party,
            "third-party": registry.validate_third_party,
            "all": registry.validate_all,
        }[args.kind]
        return emit_validation(validator())
    return None


def _run_service_command(
    args: argparse.Namespace,
    registry: SkillRegistry,
    service: GlobalInstallService,
) -> int:
    if args.command == "setup":
        return emit_operation(service.setup(dry_run=args.dry_run))
    if args.command == "verify":
        return emit_operation(service.verify())
    if args.command == "uninstall":
        return emit_operation(service.uninstall(dry_run=args.dry_run))
    if args.command == "doctor":
        validation_code = emit_validation(registry.validate_all())
        operation_code = emit_operation(service.verify())
        return 0 if validation_code == 0 and operation_code == 0 else 1
    if args.command == "sync-third-party-lock":
        return emit_operation(service.sync_lockfile(dry_run=args.dry_run))
    if args.command == "update-third-party":
        return emit_operation(
            run_third_party_update(
                service.repo_root,
                service.global_path,
                dry_run=args.dry_run,
            )
        )
    if args.command == "clean":
        return emit_operation(clean(service.repo_root))
    print(f"error: unsupported command: {args.command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
