"""Pure validation for third-party skill provenance entries."""

from __future__ import annotations

import re
from datetime import date
from pathlib import PurePosixPath
from typing import Mapping
from urllib.parse import urlsplit


PROVENANCE_FIELDS = (
    "source",
    "source_path",
    "revision",
    "license",
    "reviewed_on",
    "sha256",
)


def validate_provenance_entry(
    name: str,
    entry: object,
    *,
    manifest_name: str = "third-party-skills.json",
) -> tuple[str | None, list[str]]:
    """Validate one provenance record and return its usable digest, if any."""
    prefix = f"{manifest_name}: {name}"
    if not isinstance(entry, dict):
        return None, [f"{prefix}: entry must be an object"]
    missing = [
        field
        for field in PROVENANCE_FIELDS
        if not isinstance(entry.get(field), str) or not entry[field]
    ]
    if missing:
        return None, [
            f"{prefix}: missing non-empty string fields: {', '.join(missing)}"
        ]

    typed_entry: Mapping[str, str] = entry
    errors = [
        *_source_errors(prefix, typed_entry["source"]),
        *_source_path_errors(prefix, typed_entry["source_path"]),
        *_revision_errors(prefix, typed_entry["revision"]),
        *_reviewed_on_errors(prefix, typed_entry["reviewed_on"]),
    ]
    digest, digest_errors = _validated_digest(prefix, typed_entry["sha256"])
    errors.extend(digest_errors)
    return digest, errors


def _source_errors(prefix: str, source: str) -> list[str]:
    parsed = urlsplit(source)
    valid = (
        parsed.scheme == "https"
        and bool(parsed.netloc)
        and parsed.username is None
        and parsed.password is None
    )
    if valid:
        return []
    return [f"{prefix}: source must be an HTTPS URL without embedded credentials"]


def _source_path_errors(prefix: str, value: str) -> list[str]:
    path = PurePosixPath(value)
    unsafe = (
        not path.parts
        or value == "."
        or "\\" in value
        or path.is_absolute()
        or any(part in ("", ".", "..") for part in path.parts)
    )
    if not unsafe:
        return []
    return [f"{prefix}: source_path must be a safe repository-relative POSIX path"]


def _revision_errors(prefix: str, revision: str) -> list[str]:
    if re.fullmatch(r"[0-9a-f]{40}", revision) is not None:
        return []
    return [f"{prefix}: revision must be a full lowercase 40-character Git commit"]


def _reviewed_on_errors(prefix: str, reviewed_on: str) -> list[str]:
    try:
        date.fromisoformat(reviewed_on)
    except ValueError:
        return [f"{prefix}: reviewed_on must be an ISO date"]
    return []


def _validated_digest(prefix: str, digest: str) -> tuple[str | None, list[str]]:
    if re.fullmatch(r"[0-9a-f]{64}", digest) is not None:
        return digest, []
    return None, [
        f"{prefix}: sha256 must be 64 lowercase hexadecimal characters"
    ]
