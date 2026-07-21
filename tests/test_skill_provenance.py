import unittest

from tools.skill_provenance import validate_provenance_entry


def valid_entry() -> dict[str, str]:
    return {
        "source": "https://example.test/upstream",
        "source_path": "skills/vendor-skill",
        "revision": "a" * 40,
        "license": "MIT",
        "reviewed_on": "2026-07-21",
        "sha256": "b" * 64,
    }


class ProvenanceEntryTests(unittest.TestCase):
    def test_valid_entry_exposes_verified_digest(self) -> None:
        digest, errors = validate_provenance_entry("vendor-skill", valid_entry())

        self.assertEqual("b" * 64, digest)
        self.assertEqual([], errors)

    def test_metadata_checks_are_independent_and_fail_closed(self) -> None:
        mutations = (
            ("source", "http://example.test/upstream", "HTTPS URL"),
            ("source", "https://token@example.test/upstream", "embedded credentials"),
            ("source_path", "../vendor-skill", "safe repository-relative"),
            ("revision", "main", "40-character Git commit"),
            ("reviewed_on", "not-a-date", "ISO date"),
            ("sha256", "invalid", "64 lowercase hexadecimal"),
        )

        for field, value, expected_error in mutations:
            with self.subTest(field=field, value=value):
                entry = valid_entry()
                entry[field] = value
                digest, errors = validate_provenance_entry("vendor-skill", entry)
                self.assertTrue(
                    any(expected_error in error for error in errors),
                    errors,
                )
                if field == "sha256":
                    self.assertIsNone(digest)

    def test_missing_fields_stop_before_digest_use(self) -> None:
        entry = valid_entry()
        del entry["license"]

        digest, errors = validate_provenance_entry("vendor-skill", entry)

        self.assertIsNone(digest)
        self.assertTrue(any("missing non-empty string fields" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
