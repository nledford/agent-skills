import json
import sys
import tempfile
import unittest
from pathlib import Path

from tools.routing_evaluator import (
    evaluate_case,
    load_corpus,
    run_suite,
    validate_corpus,
)


def sample_corpus() -> dict:
    return {
        "version": 1,
        "suite": "synthetic-routing",
        "minimum_score": 1.0,
        "cases": [
            {
                "id": "debt-audit",
                "synthetic": True,
                "prompt": "Audit this synthetic repository for technical debt.",
                "expected": {
                    "agent": "engineering-review-board",
                    "command": "audit-technical-debt",
                    "skills": [
                        "technical-debt-audit",
                        "review-verification-protocol",
                    ],
                    "handoffs": ["technical-debt-auditor"],
                },
                "forbidden": {
                    "skills": ["find-skills"],
                    "handoffs": ["implementation-worker"],
                },
            }
        ],
    }


class RoutingCorpusTests(unittest.TestCase):
    def test_valid_corpus_is_accepted(self) -> None:
        self.assertEqual([], validate_corpus(sample_corpus()))

    def test_corpus_requires_synthetic_cases_and_unique_ids(self) -> None:
        corpus = sample_corpus()
        duplicate = dict(corpus["cases"][0])
        duplicate["synthetic"] = False
        corpus["cases"].append(duplicate)

        errors = validate_corpus(corpus)

        self.assertTrue(any("duplicate case id" in error for error in errors), errors)
        self.assertTrue(any("synthetic must be true" in error for error in errors), errors)

    def test_case_scoring_reports_exact_and_forbidden_mismatches(self) -> None:
        case = sample_corpus()["cases"][0]
        actual = {
            "agent": "engineering-lead",
            "command": "audit-technical-debt",
            "skills": ["technical-debt-audit", "find-skills"],
            "handoffs": ["technical-debt-auditor"],
        }

        result = evaluate_case(case, actual)

        self.assertFalse(result.passed)
        self.assertLess(result.score, 1.0)
        self.assertTrue(any("agent" in failure for failure in result.failures))
        self.assertTrue(any("find-skills" in failure for failure in result.failures))

    def test_run_suite_executes_configured_runner_and_records_bounded_trace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            corpus_path = root / "corpus.json"
            corpus_path.write_text(json.dumps(sample_corpus()), encoding="utf-8")
            runner_path = root / "runner.py"
            runner_path.write_text(
                "import json, sys\n"
                "payload = json.load(sys.stdin)\n"
                "json.dump({\n"
                "  'agent': 'engineering-review-board',\n"
                "  'command': 'audit-technical-debt',\n"
                "  'skills': [\n"
                "    'technical-debt-audit',\n"
                "    'review-verification-protocol',\n"
                "    'SYNTHETIC OUT-OF-CONTRACT VALUE /tmp/example',\n"
                "  ],\n"
                "  'handoffs': ['technical-debt-auditor'],\n"
                "  'ignored': payload['prompt'],\n"
                "}, sys.stdout)\n",
                encoding="utf-8",
            )
            trace_path = root / "trace.json"

            summary = run_suite(
                load_corpus(corpus_path),
                runner=(sys.executable, str(runner_path)),
                model="synthetic-model",
                configuration="test-fixture",
                trace_path=trace_path,
            )

            self.assertTrue(summary.passed, summary.failures)
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
            self.assertEqual("synthetic-model", trace["model"])
            self.assertEqual("test-fixture", trace["configuration"])
            self.assertEqual("debt-audit", trace["cases"][0]["id"])
            self.assertNotIn("ignored", trace["cases"][0]["actual"])
            self.assertNotIn(
                "SYNTHETIC OUT-OF-CONTRACT VALUE /tmp/example",
                trace["cases"][0]["actual"]["skills"],
            )

    def test_corpus_rejects_unbounded_prompts_and_invalid_routing_ids(self) -> None:
        corpus = sample_corpus()
        corpus["cases"][0]["prompt"] = "x" * 4001
        corpus["cases"][0]["expected"]["agent"] = "agent with spaces"

        errors = validate_corpus(corpus)

        self.assertTrue(any("prompt" in error and "4000" in error for error in errors))
        self.assertTrue(any("expected.agent" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
