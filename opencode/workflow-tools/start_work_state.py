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
MAX_POINTER_BYTES = 4_096
MAX_UNTRUSTED_LOCATOR_BYTES = 4_096
OWNER_NAME = "owner.json"
LOCK_NAME = "lock"
RESUME_NAME = "resume.json"
TOKEN_RE = re.compile(r"[0-9a-f]{64}\Z")
TODO_RE = re.compile(br"(?m)^(\s*\d+\.\s+)\[[ xX]\]")
PLAN_PREFIX = PurePosixPath("docs/implementation-plans/plans")
PLAN_PATH_RE = re.compile(
    r"docs/implementation-plans/plans/"
    r"(?P<series>[a-z][a-z0-9-]{1,19})/"
    r"(?P<sequence>0[1-9]|[1-9][0-9])-"
    r"(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.md\Z"
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
    plan_path: str | None


@dataclass(frozen=True)
class ResumePointer:
    version: int
    plan_path: str
    contract_sha256: str


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
    if not isinstance(plan_path, str) or not PLAN_PATH_RE.fullmatch(plan_path):
        raise _error("plan path is outside the canonical plan namespace")
    return plan_path


def _plan_bytes(root: Path, plan_path: str) -> bytes:
    canonical = _canonical_plan_path(plan_path)
    path = root.joinpath(*PurePosixPath(canonical).parts)
    parent = root
    for part in PurePosixPath(canonical).parts[:-1]:
        parent = parent / part
        _directory(parent)
    return _read_regular_bytes(path)


def contract_sha256(root: Path, plan_path: str) -> str:
    """Hash a stable strict-UTF-8 plan, ignoring numbered TODO completion marks."""
    raw = _plan_bytes(_repo_root(root), plan_path)
    try:
        raw.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise _error("plan is not strict UTF-8") from exc
    normalized = TODO_RE.sub(br"\1[ ]", raw)
    return hashlib.sha256(normalized).hexdigest()


def _owner_from_bytes(data: bytes) -> OwnerMetadata:
    value = _strict_json(data, limit=512)
    if set(value) != {"version", "owner_token", "plan_path"}:
        raise _error("owner metadata has unsupported fields")
    version, token, plan_path = value["version"], value["owner_token"], value["plan_path"]
    if type(version) is not int or version != 1 or not isinstance(token, str) or not TOKEN_RE.fullmatch(token):
        raise _error("owner metadata is invalid")
    if plan_path is not None:
        if not isinstance(plan_path, str):
            raise _error("owner metadata is invalid")
        plan_path = _canonical_plan_path(plan_path)
    return OwnerMetadata(version=1, owner_token=token, plan_path=plan_path)


def _read_owner(lock: Path) -> OwnerMetadata:
    _directory(lock)
    entries = {entry.name for entry in lock.iterdir()}
    if entries != {OWNER_NAME}:
        raise _error("lock metadata is missing or corrupt")
    return _owner_from_bytes(_read_regular_bytes(lock / OWNER_NAME, limit=512))


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
    return json.dumps(owner.__dict__, separators=(",", ":"), sort_keys=False).encode("utf-8")


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
    owner = OwnerMetadata(version=1, owner_token=token, plan_path=None)
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
    """Bind a provisional lock to one canonical plan path exactly once."""
    root = _repo_root(repo_root)
    canonical = _canonical_plan_path(plan_path)
    lock, owner = _matching_owner(root, owner_token)
    if owner.plan_path == canonical:
        return owner
    if owner.plan_path is not None:
        raise _error("lock is already finalized for another plan")
    final = OwnerMetadata(version=1, owner_token=owner.owner_token, plan_path=canonical)
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
    entries = _state_entries(_state_root(root, create=False))
    if (
        owner.plan_path is not None
        or RESUME_NAME in entries
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
        owner.plan_path is None
        or (completed_execution == completed_plan_only)
        or not outcomes_known
        or child_can_mutate
    ):
        raise _error("final release requires known completed outcomes")
    (lock / OWNER_NAME).unlink()
    lock.rmdir()


def _resume_from_bytes(data: bytes) -> ResumePointer:
    value = _strict_json(data)
    if set(value) != {"version", "plan_path", "contract_sha256"}:
        raise _error("resume pointer has unsupported fields")
    version, plan_path, digest = value["version"], value["plan_path"], value["contract_sha256"]
    if type(version) is not int or version != 1 or not isinstance(plan_path, str) or not isinstance(digest, str):
        raise _error("resume pointer is invalid")
    canonical = _canonical_plan_path(plan_path)
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise _error("resume pointer hash is invalid")
    return ResumePointer(version=1, plan_path=canonical, contract_sha256=digest)


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


def write_resume_pointer(repo_root: Path, owner_token: str, plan_path: str) -> ResumePointer:
    """Persist a hash-bound resume pointer while the matching owner holds the lock."""
    root = _repo_root(repo_root)
    canonical = _canonical_plan_path(plan_path)
    _, owner = _matching_owner(root, owner_token)
    if owner.plan_path != canonical:
        raise _error("resume pointer must match the finalized owner plan")
    _verify_ignore(root)
    digest = contract_sha256(root, canonical)
    state = _state_root(root, create=False)
    _state_entries(state)
    pointer = ResumePointer(version=1, plan_path=canonical, contract_sha256=digest)
    _atomic_write(state / RESUME_NAME, json.dumps(pointer.__dict__, separators=(",", ":")).encode("utf-8"))
    return pointer


def read_resume_pointer(repo_root: Path, owner_token: str) -> ResumePointer:
    """Read and validate a resume pointer and its referenced plan hash."""
    root = _repo_root(repo_root)
    state = _state_root(root, create=False)
    _matching_owner(root, owner_token)
    _state_entries(state)
    pointer = _resume_from_bytes(_read_regular_bytes(state / RESUME_NAME, limit=MAX_POINTER_BYTES))
    if not secrets.compare_digest(pointer.contract_sha256, contract_sha256(root, pointer.plan_path)):
        raise _error("resume pointer does not match its plan contract")
    return pointer


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
        owner.plan_path != canonical
        or current.plan_path != canonical
        or not secrets.compare_digest(current.contract_sha256, contract_digest)
    ):
        raise _error("resume pointer does not match the completion contract")
    (root / ".start-work" / RESUME_NAME).unlink()


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


def _json_output(value: OwnerMetadata | ResumePointer) -> None:
    print(json.dumps(value.__dict__, separators=(",", ":"), sort_keys=True))


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
