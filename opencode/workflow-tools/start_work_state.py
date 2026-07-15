"""Trusted local state primitives and closed CLI for the Plan Orchestrator."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import stat
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Callable, NoReturn, Sequence


MAX_BYTES = 1_048_576
MAX_OWNER_BYTES = 65_536
MAX_STATE_BYTES = 1_048_576
MAX_POINTER_BYTES = MAX_STATE_BYTES
MAX_UNTRUSTED_LOCATOR_BYTES = 4_096
OWNER_NAME = "owner.json"
LOCK_NAME = "lock"
RESUME_NAME = "resume.json"
TOKEN_RE = re.compile(r"[0-9a-f]{64}\Z")
PLAN_CHECKBOX_RE = re.compile(br"(?m)^(\d+\. )\[[ x]\](?= \S)")
CHECKLIST_LINE_RE = re.compile(
    r"^(?P<number>[1-9][0-9]*)\. \[(?P<mark>[ x])\] (?P<body>\S.*)$"
)
NUMBERED_CHECKBOX_LINE_RE = re.compile(r"^[1-9][0-9]*\. \[[ xX]\](?: |$)")
SINGLE_PLAN_PATH_RE = re.compile(
    r"\.erb/plans/(?P<slug>[a-z][a-z0-9]*(?:-[a-z0-9]+)*)\.md\Z"
)
MULTI_PLAN_PATH_RE = re.compile(
    r"\.erb/plans/"
    r"(?P<subject>[a-z][a-z0-9-]{1,19})/"
    r"(?P<sequence>0[1-9]|[1-9][0-9])-"
    r"(?P<slug>[a-z][a-z0-9]*(?:-[a-z0-9]+)*)\.md\Z"
)
PLAN_PREFIX = PurePosixPath(".erb/plans")
PLAN_HEADINGS = (
    "## TL;DR",
    "## Context",
    "## Objectives",
    "## Guardrails",
    "## Deliverables",
    "## Definition of Done",
    "## TODOs",
    "## Verification",
)
CONTEXT_LABELS = (
    "**Original request:**",
    "**Key repository findings:**",
    "**Dependencies:**",
)
UNTRUSTED_RELATIVE_PATH_RE = re.compile(
    r"[A-Za-z0-9][A-Za-z0-9._-]*(?:/[A-Za-z0-9][A-Za-z0-9._-]*)*\Z"
)
TAPESTRY_SOURCE_PATH_RE = re.compile(
    r"\.weave/plans/(?:[A-Za-z0-9][A-Za-z0-9._-]*/)*"
    r"[A-Za-z0-9][A-Za-z0-9._-]*\.md\Z"
)
SENSITIVE_LOCAL_SEGMENT_RE = re.compile(
    r"(?:^|/)(?:\.git|\.start-work|\.env(?:\..*)?|\.ssh|\.aws|"
    r"secret(?:s)?|credential(?:s)?|id_[A-Za-z0-9._-]+)(?:/|\Z)",
    re.IGNORECASE,
)


class StateError(RuntimeError):
    """Raised when local state is unsafe, corrupt, or owned by another caller."""


@dataclass(frozen=True)
class OwnerMetadata:
    version: int
    owner_token: str
    plan_paths: tuple[str, ...]


@dataclass(frozen=True)
class PlanContract:
    plan_path: str
    contract_sha256: str
    todo_progress: str
    verification_progress: str


@dataclass(frozen=True)
class ResumePointer:
    version: int
    plan_path: str
    contract_sha256: str
    todo_progress: str
    verification_progress: str


@dataclass(frozen=True)
class ResumeState:
    version: int
    active_plan_path: str | None
    plans: tuple[PlanContract, ...]


def _error(message: str) -> StateError:
    return StateError(message)


def _lstat(path: Path) -> os.stat_result:
    try:
        return path.lstat()
    except FileNotFoundError as exc:
        raise _error("required state entry is missing") from exc


def _regular(path: Path) -> os.stat_result:
    data = _lstat(path)
    if stat.S_ISLNK(data.st_mode) or not stat.S_ISREG(data.st_mode):
        raise _error("state entry must be a regular file")
    return data


def _directory(path: Path) -> os.stat_result:
    data = _lstat(path)
    if stat.S_ISLNK(data.st_mode) or not stat.S_ISDIR(data.st_mode):
        raise _error("state entry must be a directory")
    return data


def _repo_root(repo_root: Path) -> Path:
    root = Path(repo_root)
    if not root.is_absolute():
        root = root.resolve()
    if root.is_symlink() or not root.is_dir() or not (root / ".git").exists():
        raise _error("repository root is not a canonical workspace root")
    return root.resolve(strict=True)


def _state_root(root: Path, *, create: bool) -> Path:
    state = root / ".start-work"
    if state.exists() or state.is_symlink():
        _directory(state)
    elif create:
        try:
            state.mkdir()
        except FileExistsError:
            _directory(state)
    else:
        raise _error("trusted state directory is missing")
    if state.parent.resolve(strict=True) != root:
        raise _error("trusted state directory is not contained")
    return state


def _state_entries(state: Path) -> set[str]:
    entries = {entry.name for entry in state.iterdir()}
    unsupported = entries - {LOCK_NAME, RESUME_NAME}
    if unsupported:
        raise _error("trusted state contains an unsupported entry")
    for name in entries:
        entry = state / name
        if entry.is_symlink():
            raise _error("trusted state contains a symlink")
        if name == LOCK_NAME:
            _directory(entry)
        else:
            _regular(entry)
    return entries


def _strict_json(data: bytes, *, limit: int = MAX_BYTES) -> dict[str, object]:
    if len(data) > limit:
        raise _error("state file exceeds the size limit")
    try:
        decoded = data.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise _error("state file is not strict UTF-8") from exc

    def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in items:
            if key in result:
                raise _error("state JSON contains duplicate fields")
            result[key] = value
        return result

    try:
        value = json.loads(decoded, object_pairs_hook=pairs)
    except (json.JSONDecodeError, TypeError, StateError) as exc:
        if isinstance(exc, StateError):
            raise
        raise _error("state JSON is malformed") from exc
    if not isinstance(value, dict):
        raise _error("state JSON must be an object")
    return value


def _read_regular_bytes(path: Path, *, limit: int = MAX_BYTES) -> bytes:
    before = _regular(path)
    if before.st_size > limit:
        raise _error("file exceeds the size limit")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise _error("file cannot be opened safely") from exc
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or opened.st_size > limit:
            raise _error("file is not a safe regular file")
        chunks: list[bytes] = []
        remaining = limit + 1
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        data = b"".join(chunks)
    finally:
        os.close(descriptor)
    after = _regular(path)
    stable = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    current = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if stable != current or len(data) != before.st_size:
        raise _error("file changed while being read")
    if len(data) > limit:
        raise _error("file exceeds the size limit")
    return data


def _untrusted_relative_locator(locator: str | bytes, *, tapestry_source: bool = False) -> str:
    """Normalize only a safe, contained relative locator without touching disk."""
    if isinstance(locator, bytes):
        if len(locator) > MAX_UNTRUSTED_LOCATOR_BYTES:
            raise _error("untrusted locator exceeds the size limit")
        try:
            value = locator.decode("utf-8", "strict")
        except UnicodeDecodeError as exc:
            raise _error("untrusted locator is not strict UTF-8") from exc
    elif isinstance(locator, str):
        try:
            encoded = locator.encode("utf-8", "strict")
        except UnicodeEncodeError as exc:
            raise _error("untrusted locator is not strict UTF-8") from exc
        if len(encoded) > MAX_UNTRUSTED_LOCATOR_BYTES:
            raise _error("untrusted locator exceeds the size limit")
        value = locator
    else:
        raise _error("untrusted locator is invalid")
    if (
        not value
        or value.startswith("/")
        or "//" in value
        or any(ord(character) < 32 or ord(character) == 127 for character in value)
        or not (TAPESTRY_SOURCE_PATH_RE if tapestry_source else UNTRUSTED_RELATIVE_PATH_RE).fullmatch(value)
        or SENSITIVE_LOCAL_SEGMENT_RE.search(value)
    ):
        raise _error("untrusted locator is unsafe")
    parts = PurePosixPath(value).parts
    if any(part in {".", ".."} for part in parts):
        raise _error("untrusted locator is unsafe")
    return value


def _untrusted_regular_bytes(
    root: Path,
    locator: str | bytes,
    *,
    tapestry_source: bool = False,
) -> bytes:
    relative = _untrusted_relative_locator(locator, tapestry_source=tapestry_source)
    parts = PurePosixPath(relative).parts
    parent = root
    for part in parts[:-1]:
        parent = parent / part
        _directory(parent)
    data = _read_regular_bytes(parent / parts[-1])
    parent = root
    for part in parts[:-1]:
        parent = parent / part
        _directory(parent)
    return data


def _canonical_plan_path(plan_path: str) -> str:
    if not isinstance(plan_path, str) or not (
        SINGLE_PLAN_PATH_RE.fullmatch(plan_path)
        or MULTI_PLAN_PATH_RE.fullmatch(plan_path)
    ):
        raise _error("plan path is outside the canonical plan namespace")
    return plan_path


def _plan_layout(plan_path: str) -> tuple[str, str | None, int | None]:
    canonical = _canonical_plan_path(plan_path)
    single = SINGLE_PLAN_PATH_RE.fullmatch(canonical)
    if single is not None:
        return "single", None, None
    multi = MULTI_PLAN_PATH_RE.fullmatch(canonical)
    assert multi is not None
    return "multi", multi.group("subject"), int(multi.group("sequence"))


def _plan_bytes(root: Path, plan_path: str) -> bytes:
    canonical = _canonical_plan_path(plan_path)
    path = root.joinpath(*PurePosixPath(canonical).parts)
    parent = root
    for part in PurePosixPath(canonical).parts[:-1]:
        parent = parent / part
        _directory(parent)
    return _read_regular_bytes(path)


def contract_sha256(root: Path, plan_path: str) -> str:
    """Hash stable strict-UTF-8 plan bytes, ignoring canonical checkbox marks."""
    raw = _plan_bytes(_repo_root(root), plan_path)
    try:
        raw.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise _error("plan is not strict UTF-8") from exc
    normalized = PLAN_CHECKBOX_RE.sub(br"\1[ ]", raw)
    return hashlib.sha256(normalized).hexdigest()


def _checklist_progress(lines: list[str], *, name: str) -> str:
    progress: list[str] = []
    for line in lines:
        if not line:
            continue
        match = CHECKLIST_LINE_RE.fullmatch(line)
        if match is None:
            raise _error(f"{name} must contain only numbered canonical checkboxes")
        expected = len(progress) + 1
        if int(match.group("number")) != expected:
            raise _error(f"{name} checkbox numbering is not sequential")
        progress.append("1" if match.group("mark") == "x" else "0")
    if not progress:
        raise _error(f"{name} must contain at least one checkbox")
    return "".join(progress)


def _plan_contract(root: Path, plan_path: str) -> PlanContract:
    canonical = _canonical_plan_path(plan_path)
    raw = _plan_bytes(root, canonical)
    try:
        text = raw.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise _error("plan is not strict UTF-8") from exc
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# ") or len(lines[0]) <= 2:
        raise _error("plan title is invalid")
    headings = tuple(line for line in lines[1:] if line.startswith("#"))
    if headings != PLAN_HEADINGS:
        raise _error("plan headings do not match the closed lean contract")

    indices = {heading: lines.index(heading) for heading in PLAN_HEADINGS}
    context_start = indices["## Context"]
    context_end = indices["## Objectives"]
    label_positions: list[int] = []
    for label in CONTEXT_LABELS:
        positions = [index for index, line in enumerate(lines) if line == label]
        if len(positions) != 1 or not context_start < positions[0] < context_end:
            raise _error("plan context labels do not match the closed lean contract")
        label_positions.append(positions[0])
    if label_positions != sorted(label_positions):
        raise _error("plan context labels are out of order")

    todo_start = indices["## TODOs"] + 1
    verification_heading = indices["## Verification"]
    if any(NUMBERED_CHECKBOX_LINE_RE.match(line) for line in lines[:todo_start]):
        raise _error("numbered checkboxes are allowed only in checklist sections")
    todo_progress = _checklist_progress(
        lines[todo_start:verification_heading], name="TODO section"
    )
    verification_progress = _checklist_progress(
        lines[verification_heading + 1 :], name="Verification section"
    )
    if "1" in verification_progress and "0" in todo_progress:
        raise _error("verification cannot advance before every TODO is complete")

    digest = hashlib.sha256(PLAN_CHECKBOX_RE.sub(br"\1[ ]", raw)).hexdigest()
    return PlanContract(
        plan_path=canonical,
        contract_sha256=digest,
        todo_progress=todo_progress,
        verification_progress=verification_progress,
    )


def _owner_from_bytes(data: bytes) -> OwnerMetadata:
    value = _strict_json(data, limit=MAX_OWNER_BYTES)
    if set(value) != {"version", "owner_token", "plan_paths"}:
        raise _error("owner metadata has unsupported fields")
    version = value["version"]
    token = value["owner_token"]
    plan_paths = value["plan_paths"]
    if (
        type(version) is not int
        or version != 2
        or not isinstance(token, str)
        or not TOKEN_RE.fullmatch(token)
        or not isinstance(plan_paths, list)
        or len(plan_paths) > 99
    ):
        raise _error("owner metadata is invalid")
    canonical_paths: list[str] = []
    for plan_path in plan_paths:
        if not isinstance(plan_path, str):
            raise _error("owner metadata is invalid")
        canonical_paths.append(_canonical_plan_path(plan_path))
    if len(canonical_paths) != len(set(canonical_paths)):
        raise _error("owner metadata contains duplicate plan paths")
    return OwnerMetadata(
        version=2,
        owner_token=token,
        plan_paths=tuple(canonical_paths),
    )


def _read_owner(lock: Path) -> OwnerMetadata:
    _directory(lock)
    entries = {entry.name for entry in lock.iterdir()}
    if entries != {OWNER_NAME}:
        raise _error("lock metadata is missing or corrupt")
    return _owner_from_bytes(
        _read_regular_bytes(lock / OWNER_NAME, limit=MAX_OWNER_BYTES)
    )


def _atomic_write(path: Path, data: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp-{secrets.token_hex(8)}")
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as file:
            file.write(data)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _owner_bytes(owner: OwnerMetadata) -> bytes:
    return json.dumps(
        {
            "version": owner.version,
            "owner_token": owner.owner_token,
            "plan_paths": list(owner.plan_paths),
        },
        separators=(",", ":"),
        sort_keys=False,
    ).encode("utf-8")


def acquire_provisional(
    repo_root: Path,
    *,
    token_factory: Callable[[int], str] = secrets.token_hex,
) -> OwnerMetadata:
    """Atomically acquire an empty child lock and install fresh owner metadata."""
    root = _repo_root(repo_root)
    state = _state_root(root, create=True)
    entries = _state_entries(state)
    if LOCK_NAME in entries:
        raise _error("a child lock is already held")
    lock = state / LOCK_NAME
    try:
        lock.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise _error("a child lock is already held") from exc
    token = token_factory(32)
    if not isinstance(token, str) or not TOKEN_RE.fullmatch(token):
        raise _error("token factory returned an invalid token")
    owner = OwnerMetadata(version=2, owner_token=token, plan_paths=())
    _atomic_write(lock / OWNER_NAME, _owner_bytes(owner))
    return owner


def _matching_owner(root: Path, token: str) -> tuple[Path, OwnerMetadata]:
    if not TOKEN_RE.fullmatch(token):
        raise _error("owner token is invalid")
    state = _state_root(root, create=False)
    _state_entries(state)
    lock = state / LOCK_NAME
    owner = _read_owner(lock)
    if not secrets.compare_digest(owner.owner_token, token):
        raise _error("owner token does not match the held lock")
    return lock, owner


def _owned_workspace(repo_root: Path, owner_token: str) -> Path:
    """Bind untrusted reads to an already-acquired matching owner first."""
    root = _repo_root(repo_root)
    _matching_owner(root, owner_token)
    return root


def read_tapestry_source(repo_root: Path, owner_token: str, locator: str) -> str:
    """Read a preserved legacy source only after matching lock ownership exists."""
    raw = _untrusted_regular_bytes(
        _owned_workspace(repo_root, owner_token),
        locator,
        tapestry_source=True,
    )
    try:
        return raw.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise _error("untrusted source is not strict UTF-8") from exc


def read_secondary_reference(repo_root: Path, owner_token: str, reference: str | bytes) -> str:
    """Read a validated secondary reference without a shell or execution path."""
    raw = _untrusted_regular_bytes(_owned_workspace(repo_root, owner_token), reference)
    try:
        return raw.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise _error("secondary reference is not strict UTF-8") from exc


def finalize_owner(repo_root: Path, owner_token: str, plan_path: str) -> OwnerMetadata:
    """Bind a held lock to one or more validated canonical plan paths."""
    root = _repo_root(repo_root)
    canonical = _canonical_plan_path(plan_path)
    lock, owner = _matching_owner(root, owner_token)
    _plan_contract(root, canonical)
    if canonical in owner.plan_paths:
        return owner
    if len(owner.plan_paths) >= 99:
        raise _error("lock cannot own more plan paths")
    final = OwnerMetadata(
        version=2,
        owner_token=owner.owner_token,
        plan_paths=(*owner.plan_paths, canonical),
    )
    _atomic_write(lock / OWNER_NAME, _owner_bytes(final))
    return final


def release_provisional(
    repo_root: Path,
    owner_token: str,
    *,
    known_clean: bool,
    mutation_occurred: bool,
    child_can_mutate: bool,
) -> None:
    """Release only a clean provisional lock before any mutable child exists."""
    root = _repo_root(repo_root)
    lock, owner = _matching_owner(root, owner_token)
    _state_entries(_state_root(root, create=False))
    if (
        owner.plan_paths
        or not known_clean
        or mutation_occurred
        or child_can_mutate
    ):
        raise _error("provisional release is not safe")
    (lock / OWNER_NAME).unlink()
    lock.rmdir()


def release_final(
    repo_root: Path,
    owner_token: str,
    *,
    completed_execution: bool,
    completed_plan_only: bool,
    outcomes_known: bool,
    child_can_mutate: bool,
) -> None:
    """Release a finalized lock only after verified completion outcomes."""
    root = _repo_root(repo_root)
    lock, owner = _matching_owner(root, owner_token)
    if (
        not owner.plan_paths
        or (completed_execution == completed_plan_only)
        or not outcomes_known
        or child_can_mutate
    ):
        raise _error("final release requires known completed outcomes")
    resume_state = _read_resume_state(root)
    registered = {contract.plan_path: contract for contract in resume_state.plans}
    for plan_path in owner.plan_paths:
        contract = registered.get(plan_path)
        if contract is None or contract != _plan_contract(root, plan_path):
            raise _error("final release requires registered immutable plan contracts")
    if completed_execution:
        if len(owner.plan_paths) != 1 or resume_state.active_plan_path is not None:
            raise _error("execution release requires one completed inactive plan")
        contract = registered[owner.plan_paths[0]]
        if "0" in contract.todo_progress or "0" in contract.verification_progress:
            raise _error("execution release requires completed plan checklists")
    elif resume_state.active_plan_path is not None:
        raise _error("plan-only release cannot replace active execution")
    (lock / OWNER_NAME).unlink()
    lock.rmdir()


def _plan_contract_from_value(value: object) -> PlanContract:
    if not isinstance(value, dict) or set(value) != {
        "plan_path",
        "contract_sha256",
        "todo_progress",
        "verification_progress",
    }:
        raise _error("resume state plan contract has unsupported fields")
    plan_path = value["plan_path"]
    digest = value["contract_sha256"]
    todo_progress = value["todo_progress"]
    verification_progress = value["verification_progress"]
    if (
        not isinstance(plan_path, str)
        or not isinstance(digest, str)
        or not re.fullmatch(r"[0-9a-f]{64}", digest)
        or not isinstance(todo_progress, str)
        or not re.fullmatch(r"[01]+", todo_progress)
        or not isinstance(verification_progress, str)
        or not re.fullmatch(r"[01]+", verification_progress)
    ):
        raise _error("resume state plan contract is invalid")
    if "1" in verification_progress and "0" in todo_progress:
        raise _error("resume state verification cannot precede TODO completion")
    return PlanContract(
        plan_path=_canonical_plan_path(plan_path),
        contract_sha256=digest,
        todo_progress=todo_progress,
        verification_progress=verification_progress,
    )


def _resume_state_from_bytes(data: bytes) -> ResumeState:
    value = _strict_json(data, limit=MAX_STATE_BYTES)
    if set(value) != {"version", "active_plan_path", "plans"}:
        raise _error("resume state has unsupported fields")
    version = value["version"]
    active_plan_path = value["active_plan_path"]
    plans = value["plans"]
    if type(version) is not int or version != 2 or not isinstance(plans, list):
        raise _error("resume state is invalid")
    contracts = tuple(_plan_contract_from_value(plan) for plan in plans)
    paths = tuple(contract.plan_path for contract in contracts)
    if len(paths) != len(set(paths)):
        raise _error("resume state contains duplicate plan contracts")
    if active_plan_path is not None:
        if not isinstance(active_plan_path, str):
            raise _error("resume state is invalid")
        active_plan_path = _canonical_plan_path(active_plan_path)
        if active_plan_path not in paths:
            raise _error("resume state active plan is not registered")
    return ResumeState(
        version=2,
        active_plan_path=active_plan_path,
        plans=contracts,
    )


def _resume_state_bytes(resume_state: ResumeState) -> bytes:
    data = json.dumps(
        {
            "version": resume_state.version,
            "active_plan_path": resume_state.active_plan_path,
            "plans": [contract.__dict__ for contract in resume_state.plans],
        },
        separators=(",", ":"),
        sort_keys=False,
    ).encode("utf-8")
    if len(data) > MAX_STATE_BYTES:
        raise _error("resume state exceeds the size limit")
    return data


def _read_resume_state(root: Path) -> ResumeState:
    state = _state_root(root, create=False)
    _state_entries(state)
    return _resume_state_from_bytes(
        _read_regular_bytes(state / RESUME_NAME, limit=MAX_STATE_BYTES)
    )


def _write_resume_state(root: Path, resume_state: ResumeState) -> None:
    state = _state_root(root, create=False)
    _state_entries(state)
    _atomic_write(state / RESUME_NAME, _resume_state_bytes(resume_state))


def _pointer(contract: PlanContract) -> ResumePointer:
    return ResumePointer(version=2, **contract.__dict__)


def _validate_registration_layout(
    root: Path,
    plan_paths: tuple[str, ...],
    registered_contracts: tuple[PlanContract, ...],
) -> None:
    layouts = [_plan_layout(plan_path) for plan_path in plan_paths]
    if all(layout[0] == "single" for layout in layouts):
        if len(plan_paths) != 1:
            raise _error("multiple plans require one subject series")
        return
    if any(layout[0] != "multi" for layout in layouts):
        raise _error("single-plan and multi-plan layouts cannot be mixed")
    subjects = {layout[1] for layout in layouts}
    if len(subjects) != 1:
        raise _error("multiple plans must share one subject series")
    subject = next(iter(subjects))
    assert subject is not None
    subject_root = root / ".erb" / "plans" / subject
    _directory(subject_root)
    inventory: dict[str, int] = {}
    sequence_owners: dict[int, str] = {}
    for entry in subject_root.iterdir():
        data = _lstat(entry)
        if stat.S_ISLNK(data.st_mode) or not stat.S_ISREG(data.st_mode):
            raise _error("multi-plan series contains an unsafe entry")
        relative = entry.relative_to(root).as_posix()
        match = MULTI_PLAN_PATH_RE.fullmatch(relative)
        if match is None:
            raise _error("multi-plan series contains a non-canonical entry")
        sequence = int(match.group("sequence"))
        if sequence in sequence_owners:
            raise _error("multi-plan series contains a sequence collision")
        inventory[relative] = sequence
        sequence_owners[sequence] = relative

    historical_sequence_owners: dict[int, str] = {}
    for contract in registered_contracts:
        layout, registered_subject, sequence = _plan_layout(contract.plan_path)
        if layout != "multi" or registered_subject != subject:
            continue
        assert sequence is not None
        prior = historical_sequence_owners.get(sequence)
        if prior is not None and prior != contract.plan_path:
            raise _error("registered multi-plan series contains a sequence collision")
        historical_sequence_owners[sequence] = contract.plan_path
    for sequence, current_path in sequence_owners.items():
        historical_path = historical_sequence_owners.get(sequence)
        if historical_path is not None and historical_path != current_path:
            raise _error("multi-plan sequence collides with registered history")

    owned = set(plan_paths)
    if any(path not in inventory for path in plan_paths):
        raise _error("owned multi-plan path is missing from the series inventory")
    owned_sequences = sorted(inventory[path] for path in plan_paths)
    unowned_sequences = {
        sequence for path, sequence in inventory.items() if path not in owned
    }
    unowned_sequences.update(
        sequence
        for sequence, path in historical_sequence_owners.items()
        if path not in owned
    )
    if len(plan_paths) == 1 and not unowned_sequences:
        raise _error("one plan must use the single-plan root layout")
    first = max(unowned_sequences, default=0) + 1
    expected = list(range(first, first + len(plan_paths)))
    if expected[-1] > 99:
        raise _error("multi-plan series is exhausted")
    if owned_sequences != expected:
        raise _error("multi-plan allocation is not sequential max-plus-one")


def _verify_ignore(root: Path) -> None:
    ignore = root / ".gitignore"
    content = _read_regular_bytes(ignore)
    try:
        lines = content.decode("utf-8", "strict").splitlines()
    except UnicodeDecodeError as exc:
        raise _error("ignore file is not strict UTF-8") from exc
    exact = {"/.start-work/resume.json", "/.start-work/lock/"}
    if sum(line == "/.start-work/resume.json" for line in lines) != 1:
        raise _error("ignore rules are unsafe")
    if sum(line == "/.start-work/lock/" for line in lines) != 1:
        raise _error("ignore rules are unsafe")
    if any(".start-work" in line and line not in exact for line in lines):
        raise _error("ignore rules are unsafe")


def register_plan_contracts(
    repo_root: Path, owner_token: str
) -> tuple[PlanContract, ...]:
    """Register immutable unchecked contracts for every plan owned by this lock."""
    root = _repo_root(repo_root)
    _, owner = _matching_owner(root, owner_token)
    if not owner.plan_paths:
        raise _error("plan registration requires finalized owner paths")
    _verify_ignore(root)
    state_root = _state_root(root, create=False)
    entries = _state_entries(state_root)
    if RESUME_NAME in entries:
        resume_state = _read_resume_state(root)
    else:
        resume_state = ResumeState(version=2, active_plan_path=None, plans=())
    if resume_state.active_plan_path is not None:
        raise _error("plan creation cannot replace active execution")
    _validate_registration_layout(
        root, owner.plan_paths, resume_state.plans
    )
    contracts = tuple(_plan_contract(root, path) for path in owner.plan_paths)
    if any(
        "1" in contract.todo_progress or "1" in contract.verification_progress
        for contract in contracts
    ):
        raise _error("new plan contracts must begin with unchecked checklists")
    registered = {contract.plan_path: contract for contract in resume_state.plans}
    merged = list(resume_state.plans)
    for contract in contracts:
        existing = registered.get(contract.plan_path)
        if existing is not None and existing != contract:
            raise _error("plan registration collides with an existing contract")
        if existing is None:
            merged.append(contract)
    _write_resume_state(
        root,
        ResumeState(version=2, active_plan_path=None, plans=tuple(merged)),
    )
    return contracts


def _validate_progress_transition(
    previous: PlanContract, current: PlanContract
) -> None:
    if not secrets.compare_digest(
        previous.contract_sha256, current.contract_sha256
    ):
        raise _error("plan content changed after contract registration")
    if (
        len(previous.todo_progress) != len(current.todo_progress)
        or len(previous.verification_progress) != len(current.verification_progress)
    ):
        raise _error("plan checklist shape changed after contract registration")
    if any(
        old == "1" and new != "1"
        for old, new in zip(previous.todo_progress, current.todo_progress)
    ) or any(
        old == "1" and new != "1"
        for old, new in zip(
            previous.verification_progress, current.verification_progress
        )
    ):
        raise _error("plan checkboxes may only advance from unchecked to checked")
    verification_advanced = (
        previous.verification_progress != current.verification_progress
    )
    if verification_advanced and "0" in previous.todo_progress:
        raise _error("verification cannot begin before every TODO is persisted complete")


def write_resume_pointer(repo_root: Path, owner_token: str, plan_path: str) -> ResumePointer:
    """Activate or advance one registered immutable plan under the held lock."""
    root = _repo_root(repo_root)
    canonical = _canonical_plan_path(plan_path)
    _, owner = _matching_owner(root, owner_token)
    if owner.plan_paths != (canonical,):
        raise _error("resume pointer must match the finalized owner plan")
    _verify_ignore(root)
    resume_state = _read_resume_state(root)
    if resume_state.active_plan_path not in {None, canonical}:
        raise _error("another registered plan is active")
    previous = next(
        (contract for contract in resume_state.plans if contract.plan_path == canonical),
        None,
    )
    if previous is None:
        raise _error("plan must be registered by explicit plan creation before execution")
    current = _plan_contract(root, canonical)
    _validate_progress_transition(previous, current)
    updated = tuple(
        current if contract.plan_path == canonical else contract
        for contract in resume_state.plans
    )
    _write_resume_state(
        root,
        ResumeState(version=2, active_plan_path=canonical, plans=updated),
    )
    return _pointer(current)


def read_resume_pointer(repo_root: Path, owner_token: str) -> ResumePointer:
    """Read and validate the active pointer and exact registered plan progress."""
    root = _repo_root(repo_root)
    _, owner = _matching_owner(root, owner_token)
    resume_state = _read_resume_state(root)
    canonical = resume_state.active_plan_path
    if canonical is None or owner.plan_paths not in {(), (canonical,)}:
        raise _error("resume pointer is not active for the held owner")
    registered = next(
        contract for contract in resume_state.plans if contract.plan_path == canonical
    )
    current = _plan_contract(root, canonical)
    if registered != current:
        raise _error("resume pointer does not match exact plan progress")
    return _pointer(registered)


def clear_resume_pointer(
    repo_root: Path,
    owner_token: str,
    plan_path: str,
    contract_digest: str,
    *,
    completed: bool,
) -> None:
    """Clear a pointer only for its matching completed contract under the owner."""
    root = _repo_root(repo_root)
    _, owner = _matching_owner(root, owner_token)
    if not completed:
        raise _error("resume pointer requires a completed contract")
    current = read_resume_pointer(root, owner_token)
    canonical = _canonical_plan_path(plan_path)
    if (
        owner.plan_paths != (canonical,)
        or current.plan_path != canonical
        or not secrets.compare_digest(current.contract_sha256, contract_digest)
        or "0" in current.todo_progress
        or "0" in current.verification_progress
    ):
        raise _error("resume pointer does not match the completion contract")
    resume_state = _read_resume_state(root)
    _write_resume_state(
        root,
        ResumeState(version=2, active_plan_path=None, plans=resume_state.plans),
    )


def recover_stale_lock(repo_root: Path, *, prior_human_confirmation: bool) -> None:
    """Remove a safe, inspected stale lock after explicit human confirmation."""
    if not prior_human_confirmation:
        raise _error("stale recovery requires prior human confirmation")
    root = _repo_root(repo_root)
    state_path = root / ".start-work"
    if not state_path.exists() and not state_path.is_symlink():
        return
    state = _state_root(root, create=False)
    entries = _state_entries(state)
    if LOCK_NAME not in entries:
        return
    lock = state / LOCK_NAME
    children = {entry.name for entry in lock.iterdir()}
    if children - {OWNER_NAME}:
        raise _error("lock contains an unsupported entry")
    owner_path = lock / OWNER_NAME
    if OWNER_NAME in children:
        _regular(owner_path)
        owner_path.unlink()
    lock.rmdir()


OPERATIONS = (
    "acquire",
    "finalize",
    "register-plans",
    "read-pointer",
    "write-pointer",
    "clear-pointer",
    "release-provisional",
    "release-final",
    "recover-stale",
)


class _SanitizedArgumentParser(argparse.ArgumentParser):
    """Reject malformed runtime argv without reflecting caller-controlled text."""

    def error(self, message: str) -> NoReturn:
        raise _error("operation arguments are invalid")


def _assert_true(value: str | None) -> bool:
    if value != "true":
        raise _error("required assertion is invalid")
    return True


def _assert_bool(value: str | None) -> bool:
    if value not in {"true", "false"}:
        raise _error("required assertion is invalid")
    return value == "true"


def _json_output(value: OwnerMetadata | ResumePointer | dict[str, object]) -> None:
    if isinstance(value, OwnerMetadata):
        payload: object = {
            "version": value.version,
            "owner_token": value.owner_token,
            "plan_paths": list(value.plan_paths),
        }
    elif isinstance(value, ResumePointer):
        payload = value.__dict__
    else:
        payload = value
    print(json.dumps(payload, separators=(",", ":"), sort_keys=True))


def _cli_parser() -> argparse.ArgumentParser:
    parser = _SanitizedArgumentParser(prog="start_work_state.py", add_help=False)
    parser.add_argument("operation", choices=OPERATIONS)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--owner-token")
    parser.add_argument("--plan-path")
    parser.add_argument("--contract-sha256")
    parser.add_argument("--known-clean")
    parser.add_argument("--no-mutation")
    parser.add_argument("--no-child-can-mutate")
    parser.add_argument("--completed-execution")
    parser.add_argument("--completed-plan-only")
    parser.add_argument("--outcomes-known")
    parser.add_argument("--completed")
    parser.add_argument("--prior-human-confirmation")
    return parser


def _require_token(value: str | None) -> str:
    if not isinstance(value, str) or not TOKEN_RE.fullmatch(value):
        raise _error("owner token is invalid")
    return value


def _require_plan(value: str | None) -> str:
    if not isinstance(value, str):
        raise _error("plan path is invalid")
    return _canonical_plan_path(value)


def _require_hash(value: str | None) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise _error("contract hash is invalid")
    return value


def _only_fields(arguments: argparse.Namespace, *allowed: str) -> None:
    ignored = {"operation", "repo_root", *allowed}
    if any(value is not None for name, value in vars(arguments).items() if name not in ignored):
        raise _error("operation arguments are invalid")


def main(argv: Sequence[str] | None = None) -> int:
    """Run fixed-literal runtime transitions without target-shell construction."""
    parser = _cli_parser()
    try:
        arguments = parser.parse_args(argv)
        if arguments.repo_root != ".":
            raise _error("runtime repository root must be the literal dot argument")
        cwd = Path.cwd()
        if cwd.is_symlink() or cwd.resolve(strict=True) != cwd.absolute():
            raise _error("runtime workspace root is aliased")
        operation = arguments.operation
        if operation == "acquire":
            _only_fields(arguments)
            _json_output(acquire_provisional(cwd))
        elif operation == "finalize":
            _only_fields(arguments, "owner_token", "plan_path")
            finalize_owner(cwd, _require_token(arguments.owner_token), _require_plan(arguments.plan_path))
        elif operation == "register-plans":
            _only_fields(arguments, "owner_token")
            contracts = register_plan_contracts(
                cwd, _require_token(arguments.owner_token)
            )
            _json_output({"plans": [contract.__dict__ for contract in contracts]})
        elif operation == "read-pointer":
            _only_fields(arguments, "owner_token")
            _json_output(read_resume_pointer(cwd, _require_token(arguments.owner_token)))
        elif operation == "write-pointer":
            _only_fields(arguments, "owner_token", "plan_path")
            _json_output(write_resume_pointer(cwd, _require_token(arguments.owner_token), _require_plan(arguments.plan_path)))
        elif operation == "clear-pointer":
            _only_fields(arguments, "owner_token", "plan_path", "contract_sha256", "completed")
            clear_resume_pointer(
                cwd,
                _require_token(arguments.owner_token),
                _require_plan(arguments.plan_path),
                _require_hash(arguments.contract_sha256),
                completed=_assert_true(arguments.completed),
            )
        elif operation == "release-provisional":
            _only_fields(arguments, "owner_token", "known_clean", "no_mutation", "no_child_can_mutate")
            release_provisional(
                cwd,
                _require_token(arguments.owner_token),
                known_clean=_assert_true(arguments.known_clean),
                mutation_occurred=not _assert_true(arguments.no_mutation),
                child_can_mutate=not _assert_true(arguments.no_child_can_mutate),
            )
        elif operation == "release-final":
            _only_fields(
                arguments,
                "owner_token",
                "completed_execution",
                "completed_plan_only",
                "outcomes_known",
                "no_child_can_mutate",
            )
            release_final(
                cwd,
                _require_token(arguments.owner_token),
                completed_execution=_assert_bool(arguments.completed_execution),
                completed_plan_only=_assert_bool(arguments.completed_plan_only),
                outcomes_known=_assert_true(arguments.outcomes_known),
                child_can_mutate=not _assert_true(arguments.no_child_can_mutate),
            )
        else:
            _only_fields(arguments, "prior_human_confirmation")
            recover_stale_lock(cwd, prior_human_confirmation=_assert_true(arguments.prior_human_confirmation))
    except (StateError, SystemExit):
        print("start-work state error", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
