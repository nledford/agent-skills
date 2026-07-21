#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


CORPUS_VERSION = 1
ROUTING_FIELDS = ("agent", "command", "skills", "handoffs")
LIST_ROUTING_FIELDS = ("skills", "handoffs")
MAX_PROMPT_CHARS = 4000
MAX_ROUTING_ITEMS = 64
MAX_RUN_LABEL_CHARS = 200
ROUTING_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,127}$")


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    matched: int
    assertions: int
    failures: tuple[str, ...]
    actual: dict[str, object]

    @property
    def score(self) -> float:
        return self.matched / self.assertions if self.assertions else 0.0

    @property
    def passed(self) -> bool:
        return not self.failures


@dataclass(frozen=True)
class RunSummary:
    cases: tuple[CaseResult, ...]
    minimum_score: float

    @property
    def matched(self) -> int:
        return sum(case.matched for case in self.cases)

    @property
    def assertions(self) -> int:
        return sum(case.assertions for case in self.cases)

    @property
    def score(self) -> float:
        return self.matched / self.assertions if self.assertions else 0.0

    @property
    def failures(self) -> tuple[str, ...]:
        return tuple(
            f"{case.case_id}: {failure}"
            for case in self.cases
            for failure in case.failures
        )

    @property
    def passed(self) -> bool:
        return self.assertions > 0 and self.score >= self.minimum_score


def load_corpus(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read routing corpus {path}: {error}") from error
    errors = validate_corpus(data)
    if errors:
        raise ValueError("; ".join(errors))
    return data


def validate_corpus(corpus: object) -> list[str]:
    if not isinstance(corpus, dict):
        return ["corpus root must be an object"]
    errors: list[str] = []
    if corpus.get("version") != CORPUS_VERSION:
        errors.append(f"version must be {CORPUS_VERSION}")
    if not isinstance(corpus.get("suite"), str) or not corpus["suite"].strip():
        errors.append("suite must be a non-empty routing identifier")
    elif ROUTING_ID_RE.fullmatch(corpus["suite"]) is None:
        errors.append("suite must be a lowercase routing identifier of at most 128 characters")
    minimum_score = corpus.get("minimum_score")
    if not isinstance(minimum_score, (int, float)) or isinstance(minimum_score, bool):
        errors.append("minimum_score must be a number from 0 through 1")
    elif not 0 <= float(minimum_score) <= 1:
        errors.append("minimum_score must be a number from 0 through 1")

    cases = corpus.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("cases must be a non-empty array")
        return errors

    seen_ids: set[str] = set()
    for index, case in enumerate(cases):
        prefix = f"cases[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{prefix} must be an object")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"{prefix}.id must be a non-empty routing identifier")
        elif ROUTING_ID_RE.fullmatch(case_id) is None:
            errors.append(
                f"{prefix}.id must be a lowercase routing identifier of at most 128 characters"
            )
        elif case_id in seen_ids:
            errors.append(f"{prefix}: duplicate case id: {case_id}")
        else:
            seen_ids.add(case_id)
        if case.get("synthetic") is not True:
            errors.append(f"{prefix}.synthetic must be true")
        prompt = case.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append(f"{prefix}.prompt must be a non-empty string")
        elif len(prompt) > MAX_PROMPT_CHARS:
            errors.append(
                f"{prefix}.prompt must contain at most {MAX_PROMPT_CHARS} characters"
            )
        expected = case.get("expected")
        forbidden = case.get("forbidden", {})
        if not isinstance(expected, dict) or not expected:
            errors.append(f"{prefix}.expected must be a non-empty object")
            continue
        if not isinstance(forbidden, dict):
            errors.append(f"{prefix}.forbidden must be an object")
            continue
        unexpected_expected = sorted(set(expected) - set(ROUTING_FIELDS))
        unexpected_forbidden = sorted(set(forbidden) - set(LIST_ROUTING_FIELDS))
        if unexpected_expected:
            errors.append(
                f"{prefix}.expected has unsupported fields: {', '.join(unexpected_expected)}"
            )
        if unexpected_forbidden:
            errors.append(
                f"{prefix}.forbidden has unsupported fields: {', '.join(unexpected_forbidden)}"
            )
        for field in ("agent", "command"):
            if field not in expected:
                continue
            value = expected[field]
            if not isinstance(value, str) or not value.strip():
                errors.append(
                    f"{prefix}.expected.{field} must be a non-empty routing identifier"
                )
            elif ROUTING_ID_RE.fullmatch(value) is None:
                errors.append(
                    f"{prefix}.expected.{field} must be a lowercase routing identifier "
                    "of at most 128 characters"
                )
        for container_name, container in (("expected", expected), ("forbidden", forbidden)):
            for field in LIST_ROUTING_FIELDS:
                if field not in container:
                    continue
                value = container[field]
                if (
                    not isinstance(value, list)
                    or len(value) > MAX_ROUTING_ITEMS
                    or any(
                        not isinstance(item, str)
                        or ROUTING_ID_RE.fullmatch(item) is None
                        for item in value
                    )
                    or len(value) != len(set(value))
                ):
                    errors.append(
                        f"{prefix}.{container_name}.{field} must be an array of at most "
                        f"{MAX_ROUTING_ITEMS} unique lowercase routing identifiers"
                    )
    return errors


def _bounded_actual(actual: object) -> dict[str, object]:
    if not isinstance(actual, dict):
        return {}
    bounded: dict[str, object] = {}
    for field in ("agent", "command"):
        value = actual.get(field)
        if isinstance(value, str) and ROUTING_ID_RE.fullmatch(value) is not None:
            bounded[field] = value
    for field in LIST_ROUTING_FIELDS:
        value = actual.get(field)
        if isinstance(value, list):
            items: list[str] = []
            for item in value:
                if (
                    isinstance(item, str)
                    and ROUTING_ID_RE.fullmatch(item) is not None
                    and item not in items
                ):
                    items.append(item)
                if len(items) == MAX_ROUTING_ITEMS:
                    break
            bounded[field] = items
    return bounded


def evaluate_case(case: dict, actual: object) -> CaseResult:
    bounded = _bounded_actual(actual)
    expected = case["expected"]
    forbidden = case.get("forbidden", {})
    matched = 0
    assertions = 0
    failures: list[str] = []

    for field in ("agent", "command"):
        if field not in expected:
            continue
        assertions += 1
        if bounded.get(field) == expected[field]:
            matched += 1
        else:
            failures.append(
                f"expected {field} {expected[field]!r}, found {bounded.get(field)!r}"
            )

    for field in LIST_ROUTING_FIELDS:
        actual_values = bounded.get(field, [])
        if not isinstance(actual_values, list):
            actual_values = []
        for value in expected.get(field, []):
            assertions += 1
            if value in actual_values:
                matched += 1
            else:
                failures.append(f"expected {field} to contain {value!r}")
        for value in forbidden.get(field, []):
            assertions += 1
            if value not in actual_values:
                matched += 1
            else:
                failures.append(f"forbidden {field} contained {value!r}")

    return CaseResult(
        case_id=case["id"],
        matched=matched,
        assertions=assertions,
        failures=tuple(failures),
        actual=bounded,
    )


def run_suite(
    corpus: dict,
    *,
    runner: Sequence[str],
    model: str,
    configuration: str,
    trace_path: Path | None = None,
    timeout_seconds: int = 120,
) -> RunSummary:
    errors = validate_corpus(corpus)
    if errors:
        raise ValueError("; ".join(errors))
    if not runner:
        raise ValueError("runner command must not be empty")
    if not model.strip() or not configuration.strip():
        raise ValueError("model and configuration labels must be non-empty")
    if any(
        len(label) > MAX_RUN_LABEL_CHARS
        or any(ord(character) < 32 for character in label)
        for label in (model, configuration)
    ):
        raise ValueError(
            f"model and configuration labels must be printable and at most {MAX_RUN_LABEL_CHARS} characters"
        )

    results: list[CaseResult] = []
    trace_cases: list[dict[str, object]] = []
    for case in corpus["cases"]:
        payload = {
            "id": case["id"],
            "prompt": case["prompt"],
            "model": model,
            "configuration": configuration,
        }
        completed = subprocess.run(
            tuple(runner),
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_seconds,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"runner exited with {completed.returncode} for {case['id']}"
            )
        try:
            actual = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"runner returned invalid JSON for {case['id']}: {error}") from error
        result = evaluate_case(case, actual)
        results.append(result)
        trace_cases.append(
            {
                "id": case["id"],
                "prompt": case["prompt"],
                "actual": result.actual,
                "score": result.score,
                "failures": list(result.failures),
            }
        )

    summary = RunSummary(tuple(results), float(corpus["minimum_score"]))
    if trace_path is not None:
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        trace_path.write_text(
            json.dumps(
                {
                    "suite": corpus["suite"],
                    "model": model,
                    "configuration": configuration,
                    "score": summary.score,
                    "minimum_score": summary.minimum_score,
                    "cases": trace_cases,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate or execute synthetic agent-routing evaluation corpora."
    )
    parser.add_argument("action", choices=("validate", "run"))
    parser.add_argument("corpus", type=Path)
    parser.add_argument(
        "--runner",
        help="Runner command string. Receives one JSON case on stdin and returns JSON on stdout.",
    )
    parser.add_argument("--model", help="Model identifier recorded with a live run.")
    parser.add_argument(
        "--configuration", help="Configuration or commit label recorded with a live run."
    )
    parser.add_argument(
        "--trace-out",
        type=Path,
        help="Explicit path for a bounded synthetic trace; no trace is written by default.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        corpus = load_corpus(args.corpus)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    if args.action == "validate":
        print(f"Routing corpus valid: {len(corpus['cases'])} synthetic cases.")
        return 0

    runner_text = args.runner or os.environ.get("ROUTING_EVAL_RUNNER", "")
    model = args.model or os.environ.get("ROUTING_EVAL_MODEL", "")
    configuration = args.configuration or os.environ.get(
        "ROUTING_EVAL_CONFIGURATION", ""
    )
    runner = tuple(shlex.split(runner_text))
    try:
        summary = run_suite(
            corpus,
            runner=runner,
            model=model,
            configuration=configuration,
            trace_path=args.trace_out,
        )
    except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    for failure in summary.failures:
        print(f"failure: {failure}", file=sys.stderr)
    print(
        f"Routing score: {summary.matched}/{summary.assertions} "
        f"({summary.score:.3f}); minimum={summary.minimum_score:.3f}"
    )
    return 0 if summary.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
