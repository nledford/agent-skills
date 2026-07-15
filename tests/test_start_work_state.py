from __future__ import annotations

import importlib.util
import io
import json
import multiprocessing
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).parents[1] / "opencode/workflow-tools/start_work_state.py"
SPEC = importlib.util.spec_from_file_location("start_work_state", MODULE_PATH)
assert SPEC and SPEC.loader
state = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = state
SPEC.loader.exec_module(state)
TOKEN = "a" * 64
OTHER_TOKEN = "b" * 64
PLAN = "docs/implementation-plans/plans/state/01-state.md"


def _contend(root, ready, result) -> None:
    ready.wait(5)
    try:
        state.acquire_provisional(Path(root), token_factory=lambda _: TOKEN)
    except state.StateError:
        result.put("lost")
    else:
        result.put("won")


class StartWorkStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="state test ;$() `\n")
        self.root = Path(self.temporary.name) / "- repo 'quotes'"
        self.root.mkdir()
        (self.root / ".git").mkdir()
        (self.root / ".gitignore").write_text("/.start-work/resume.json\n/.start-work/lock/\n", encoding="utf-8")
        path = self.root / PLAN
        path.parent.mkdir(parents=True)
        path.write_text("# state\n1. [ ] acquire\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def acquire(self):
        return state.acquire_provisional(self.root, token_factory=lambda _: TOKEN)

    def invoke_cli(self, *arguments: str) -> tuple[int, str, str]:
        previous = Path.cwd()
        output, errors = io.StringIO(), io.StringIO()
        try:
            os.chdir(self.root)
            with redirect_stdout(output), redirect_stderr(errors):
                code = state.main(arguments)
        finally:
            os.chdir(previous)
        return code, output.getvalue(), errors.getvalue()

    def test_acquires_fresh_and_reuses_empty_parent(self) -> None:
        owner = self.acquire()
        self.assertEqual(owner.owner_token, TOKEN)
        state.release_provisional(self.root, TOKEN, known_clean=True, mutation_occurred=False, child_can_mutate=False)
        self.assertEqual(self.acquire().plan_path, None)

    def test_rejects_symlinked_and_nested_repository_roots(self) -> None:
        alias = self.root.parent / "workspace-alias"
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(state.StateError):
            state.acquire_provisional(alias, token_factory=lambda _: TOKEN)
        nested = self.root / "nested"
        nested.mkdir()
        with self.assertRaises(state.StateError):
            state.acquire_provisional(nested, token_factory=lambda _: TOKEN)

    def test_rejects_non_string_token_factory_output(self) -> None:
        with self.assertRaises(state.StateError):
            state.acquire_provisional(self.root, token_factory=lambda _: 1)
        self.assertTrue((self.root / ".start-work/lock").is_dir())

    def test_immediate_loser_and_process_contention(self) -> None:
        self.acquire()
        with self.assertRaises(state.StateError):
            self.acquire()
        state.release_provisional(self.root, TOKEN, known_clean=True, mutation_occurred=False, child_can_mutate=False)
        context = multiprocessing.get_context("spawn")
        ready, results = context.Event(), context.Queue()
        processes = [context.Process(target=_contend, args=(str(self.root), ready, results)) for _ in range(2)]
        for process in processes:
            process.start()
        ready.set()
        observed = [results.get(timeout=5) for _ in processes]
        for process in processes:
            process.join(timeout=5)
            self.assertFalse(process.is_alive())
            self.assertEqual(process.exitcode, 0)
        self.assertEqual(sorted(observed), ["lost", "won"])

    def test_acquire_does_not_read_pointer_or_plan_before_returning_complete_lock(self) -> None:
        state_dir = self.root / ".start-work"
        state_dir.mkdir()
        (state_dir / "resume.json").write_bytes(b"synthetic-sensitive-looking-data")
        reads: list[Path] = []
        original_read = state._read_regular_bytes

        def observe_read(path: Path, *, limit: int = state.MAX_BYTES) -> bytes:
            reads.append(path)
            return original_read(path, limit=limit)

        with patch.object(state, "_read_regular_bytes", observe_read):
            owner = self.acquire()

        self.assertEqual(reads, [])
        self.assertEqual(state._read_owner(state_dir / "lock"), owner)
        self.assertEqual(owner.plan_path, None)

    def test_tapestry_source_requires_matching_owner_before_any_source_read(self) -> None:
        source = self.root / ".weave/plans/source.md"
        source.parent.mkdir(parents=True)
        original = b"# legacy\nsynthetic-sensitive-looking-data\n"
        source.write_bytes(original)
        source_reads: list[Path] = []
        original_read = state._read_regular_bytes

        def observe_read(path: Path, *, limit: int = state.MAX_BYTES) -> bytes:
            if path == source:
                source_reads.append(path)
            return original_read(path, limit=limit)

        with patch.object(state, "_read_regular_bytes", observe_read):
            with self.assertRaises(state.StateError):
                state.read_tapestry_source(self.root, TOKEN, ".weave/plans/source.md")
        self.assertEqual(source_reads, [])

        self.acquire()
        self.assertEqual(
            state.read_tapestry_source(self.root, TOKEN, ".weave/plans/source.md"),
            original.decode("utf-8"),
        )
        self.assertEqual(source.read_bytes(), original)
        state.finalize_owner(self.root, TOKEN, PLAN)
        self.assertEqual(
            state.read_tapestry_source(self.root, TOKEN, ".weave/plans/source.md"),
            original.decode("utf-8"),
        )
        with self.assertRaises(state.StateError):
            state.read_tapestry_source(self.root, OTHER_TOKEN, ".weave/plans/source.md")

    def test_tapestry_source_rejects_unsafe_paths_and_content(self) -> None:
        source_root = self.root / ".weave/plans"
        source_root.mkdir(parents=True)
        exact = source_root / "exact.md"
        exact.write_bytes(b"a" * state.MAX_BYTES)
        too_large = source_root / "too-large.md"
        too_large.write_bytes(b"a" * (state.MAX_BYTES + 1))
        invalid = source_root / "invalid.md"
        invalid.write_bytes(b"\xff")
        directory = source_root / "directory.md"
        directory.mkdir()
        special = source_root / "special.md"
        os.mkfifo(special)
        outside = self.root.parent / "outside-source.md"
        outside.write_text("outside", encoding="utf-8")
        link = source_root / "link.md"
        link.symlink_to(outside)
        repository_local = self.root / "repository-local.md"
        repository_local.write_text("local", encoding="utf-8")
        non_markdown = source_root / "not-markdown.txt"
        non_markdown.write_text("not markdown", encoding="utf-8")
        self.acquire()

        self.assertEqual(
            len(state.read_tapestry_source(self.root, TOKEN, ".weave/plans/exact.md")),
            state.MAX_BYTES,
        )
        source_reads: list[Path] = []
        original_read = state._read_regular_bytes

        def observe_read(path: Path, *, limit: int = state.MAX_BYTES) -> bytes:
            if path in {repository_local, non_markdown}:
                source_reads.append(path)
            return original_read(path, limit=limit)

        with patch.object(state, "_read_regular_bytes", observe_read):
            for locator in ("repository-local.md", ".weave/plans/not-markdown.txt"):
                with self.subTest(locator=locator):
                    with self.assertRaises(state.StateError):
                        state.read_tapestry_source(self.root, TOKEN, locator)
        self.assertEqual(source_reads, [])
        for locator in (
            "/outside-source.md",
            "../outside-source.md",
            ".weave/plans/too-large.md",
            ".weave/plans/invalid.md",
            ".weave/plans/directory.md",
            ".weave/plans/special.md",
            ".weave/plans/link.md",
        ):
            with self.subTest(locator=locator):
                with self.assertRaises(state.StateError):
                    state.read_tapestry_source(self.root, TOKEN, locator)

    def test_secondary_references_reject_unsafe_values_without_reads_or_execution(self) -> None:
        references = self.root / "references"
        references.mkdir()
        valid = references / "valid.txt"
        valid.write_text("valid", encoding="utf-8")
        large = references / "large.txt"
        large.write_bytes(b"x" * (state.MAX_BYTES + 1))
        invalid_content = references / "invalid-content.txt"
        invalid_content.write_bytes(b"\xff")
        outside = self.root.parent / "outside-reference.txt"
        outside.write_text("outside", encoding="utf-8")
        link = references / "link.txt"
        link.symlink_to(outside)
        self.acquire()
        lock, owner = state._matching_owner(state._repo_root(self.root), TOKEN)
        secondary_reads: list[bytes] = []
        executions: list[str] = []
        original_os_read = state.os.read

        def observe_os_read(descriptor: int, size: int) -> bytes:
            secondary_reads.append(original_os_read(descriptor, size))
            return secondary_reads[-1]

        def fail_execution(command: str) -> int:
            executions.append(command)
            raise AssertionError("secondary references must not execute commands")

        rejected: tuple[str | bytes, ...] = (
            "/references/valid.txt",
            "../outside-reference.txt",
            "references/link.txt",
            "references/large.txt",
            b"references/\xff.txt",
            ".env",
            ".ssh/id_fake",
            "references/control\n.txt",
            "references/semicolon;.txt",
            "references/backtick`.txt",
            "references/$(substitution).txt",
            "references/pipe|.txt",
        )
        with (
            patch.object(state, "_matching_owner", return_value=(lock, owner)) as matching_owner,
            patch.object(state.os, "read", side_effect=observe_os_read),
            patch.object(state.os, "system", side_effect=fail_execution),
        ):
            for reference in rejected:
                with self.subTest(reference=repr(reference)):
                    secondary_reads.clear()
                    with self.assertRaises(state.StateError):
                        state.read_secondary_reference(self.root, TOKEN, reference)
                    self.assertEqual(secondary_reads, [])
            secondary_reads.clear()
            with self.assertRaises(state.StateError):
                state.read_secondary_reference(self.root, TOKEN, "references/invalid-content.txt")
            self.assertTrue(secondary_reads)
            self.assertEqual(
                state.read_secondary_reference(self.root, TOKEN, "references/valid.txt"),
                "valid",
            )
            self.assertTrue(matching_owner.called)
        self.assertEqual(executions, [])

    def test_crash_residue_and_malformed_owner_remain_held(self) -> None:
        state_dir = self.root / ".start-work"
        state_dir.mkdir()
        lock = state_dir / "lock"
        lock.mkdir()
        with self.assertRaises(state.StateError):
            self.acquire()
        (lock / "owner.json").write_text("{", encoding="utf-8")
        state.recover_stale_lock(self.root, prior_human_confirmation=True)
        self.assertFalse(lock.exists())

    def test_stale_recovery_rejects_extra_lock_children(self) -> None:
        self.acquire()
        (self.root / ".start-work/lock/extra").write_text("x", encoding="utf-8")
        with self.assertRaises(state.StateError):
            state.recover_stale_lock(self.root, prior_human_confirmation=True)

    def test_unsupported_children_and_symlink_type_fail_closed(self) -> None:
        (self.root / ".start-work").mkdir()
        (self.root / ".start-work" / "junk").write_text("x", encoding="utf-8")
        with self.assertRaises(state.StateError):
            self.acquire()
        (self.root / ".start-work" / "junk").unlink()
        (self.root / ".start-work" / "resume.json").mkdir()
        with self.assertRaises(state.StateError):
            self.acquire()

    def test_finalization_is_canonical_idempotent_and_conflict_safe(self) -> None:
        self.acquire()
        final = state.finalize_owner(self.root, TOKEN, PLAN)
        self.assertEqual(final.plan_path, PLAN)
        self.assertEqual(state.finalize_owner(self.root, TOKEN, PLAN), final)
        with self.assertRaises(state.StateError):
            state.finalize_owner(self.root, TOKEN, "docs/implementation-plans/plans/state/02-other.md")
        with self.assertRaises(state.StateError):
            state.finalize_owner(self.root, OTHER_TOKEN, PLAN)
        for invalid in ("/tmp/x.md", "docs/implementation-plans/plans/state/../x.md", "plans/x.md"):
            with self.assertRaises(state.StateError):
                state.finalize_owner(self.root, TOKEN, invalid)

    def test_release_rules_and_stale_recovery(self) -> None:
        self.acquire()
        for kwargs in (
            dict(known_clean=False, mutation_occurred=False, child_can_mutate=False),
            dict(known_clean=True, mutation_occurred=True, child_can_mutate=False),
            dict(known_clean=True, mutation_occurred=False, child_can_mutate=True),
        ):
            with self.assertRaises(state.StateError):
                state.release_provisional(self.root, TOKEN, **kwargs)
        with self.assertRaises(state.StateError):
            state.recover_stale_lock(self.root, prior_human_confirmation=False)
        state.recover_stale_lock(self.root, prior_human_confirmation=True)
        self.acquire()
        state.finalize_owner(self.root, TOKEN, PLAN)
        with self.assertRaises(state.StateError):
            state.release_final(
                self.root,
                OTHER_TOKEN,
                completed_execution=True,
                completed_plan_only=False,
                outcomes_known=True,
                child_can_mutate=False,
            )
        with self.assertRaises(state.StateError):
            state.release_final(
                self.root,
                TOKEN,
                completed_execution=False,
                completed_plan_only=False,
                outcomes_known=True,
                child_can_mutate=False,
            )
        state.release_final(
            self.root,
            TOKEN,
            completed_execution=True,
            completed_plan_only=False,
            outcomes_known=True,
            child_can_mutate=False,
        )

    def test_resume_round_trip_clear_and_owner_requirement(self) -> None:
        self.acquire()
        state.finalize_owner(self.root, TOKEN, PLAN)
        pointer = state.write_resume_pointer(self.root, TOKEN, PLAN)
        self.assertEqual(state.read_resume_pointer(self.root, TOKEN), pointer)
        with self.assertRaises(state.StateError):
            state.clear_resume_pointer(self.root, TOKEN, PLAN, pointer.contract_sha256, completed=False)
        with self.assertRaises(state.StateError):
            state.clear_resume_pointer(self.root, TOKEN, PLAN, "b" * 64, completed=True)
        state.clear_resume_pointer(self.root, TOKEN, PLAN, pointer.contract_sha256, completed=True)
        self.assertFalse((self.root / ".start-work/resume.json").exists())

    def test_resume_schema_hash_and_checkbox_rules(self) -> None:
        self.acquire()
        state.finalize_owner(self.root, TOKEN, PLAN)
        first = state.write_resume_pointer(self.root, TOKEN, PLAN)
        path = self.root / PLAN
        path.write_text("# state\n1. [x] acquire\n", encoding="utf-8")
        self.assertEqual(state.read_resume_pointer(self.root, TOKEN), first)
        path.write_text("# changed\n1. [x] acquire\n", encoding="utf-8")
        with self.assertRaises(state.StateError):
            state.read_resume_pointer(self.root, TOKEN)
        resume = self.root / ".start-work/resume.json"
        resume.write_text('{"version":1,"version":1}', encoding="utf-8")
        with self.assertRaises(state.StateError):
            state.read_resume_pointer(self.root, TOKEN)
        resume.write_bytes(b"\xff")
        with self.assertRaises(state.StateError):
            state.read_resume_pointer(self.root, TOKEN)
        resume.write_bytes(b"x" * (state.MAX_BYTES + 1))
        with self.assertRaises(state.StateError):
            state.read_resume_pointer(self.root, TOKEN)
        resume.write_text(json.dumps({"version": 1, "plan_path": "/unsafe.md", "contract_sha256": "a" * 64}), encoding="utf-8")
        with self.assertRaises(state.StateError):
            state.read_resume_pointer(self.root, TOKEN)

    def test_resume_rejects_unsafe_ignore_and_unsupported_state(self) -> None:
        self.acquire()
        state.finalize_owner(self.root, TOKEN, PLAN)
        (self.root / ".gitignore").write_text("/.start-work/\n", encoding="utf-8")
        with self.assertRaises(state.StateError):
            state.write_resume_pointer(self.root, TOKEN, PLAN)
        (self.root / ".gitignore").write_text("/.start-work/resume.json\n/.start-work/lock/\n", encoding="utf-8")
        (self.root / ".start-work" / "extra").write_text("x", encoding="utf-8")
        with self.assertRaises(state.StateError):
            state.write_resume_pointer(self.root, TOKEN, PLAN)

    def test_plan_read_boundaries_encoding_symlink_and_replacement(self) -> None:
        path = self.root / PLAN
        path.write_bytes(b"a" * state.MAX_BYTES)
        self.assertEqual(len(state.contract_sha256(self.root, PLAN)), 64)
        path.write_bytes(b"a" * (state.MAX_BYTES + 1))
        with self.assertRaises(state.StateError):
            state.contract_sha256(self.root, PLAN)
        path.write_bytes(b"\xff")
        with self.assertRaises(state.StateError):
            state.contract_sha256(self.root, PLAN)
        outside = self.root.parent / "outside.md"
        outside.write_text("x", encoding="utf-8")
        path.unlink()
        path.symlink_to(outside)
        with self.assertRaises(state.StateError):
            state.contract_sha256(self.root, PLAN)

    def test_plan_read_rejects_replacement_during_validation(self) -> None:
        path = self.root / PLAN
        original_read = state.os.read
        changed = False

        def replace_once(descriptor, size):
            nonlocal changed
            chunk = original_read(descriptor, size)
            if not changed:
                changed = True
                replacement = path.with_suffix(".replacement")
                replacement.write_text("# replacement\n", encoding="utf-8")
                replacement.replace(path)
            return chunk

        state.os.read = replace_once
        try:
            with self.assertRaises(state.StateError):
                state.contract_sha256(self.root, PLAN)
        finally:
            state.os.read = original_read

    def test_cli_requires_literal_dot_and_never_executes_target_code(self) -> None:
        marker = self.root / "executed"
        (self.root / "sitecustomize.py").write_text(f"open({str(marker)!r}, 'w').close()", encoding="utf-8")
        command = [sys.executable, "-I", str(MODULE_PATH), "acquire", "--repo-root", "."]
        run = subprocess.run(command, cwd=self.root, capture_output=True, text=True, timeout=5, check=False)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertFalse(marker.exists())
        bad = subprocess.run([*command[:-1], ".."], cwd=self.root, capture_output=True, text=True, timeout=5, check=False)
        self.assertNotEqual(bad.returncode, 0)

    def test_cli_closed_transitions_and_token_handoff(self) -> None:
        code, output, errors = self.invoke_cli("acquire", "--repo-root", ".")
        self.assertEqual((code, errors), (0, ""))
        owner = json.loads(output)
        token = owner["owner_token"]
        self.assertRegex(token, r"^[0-9a-f]{64}$")
        self.assertNotIn(str(self.root), output)
        self.assertEqual(self.invoke_cli("finalize", "--repo-root", ".", "--owner-token", token, "--plan-path", PLAN)[0], 0)
        code, output, errors = self.invoke_cli("write-pointer", "--repo-root", ".", "--owner-token", token, "--plan-path", PLAN)
        self.assertEqual((code, errors), (0, ""))
        pointer = json.loads(output)
        self.assertEqual(pointer["plan_path"], PLAN)
        code, output, errors = self.invoke_cli("read-pointer", "--repo-root", ".", "--owner-token", token)
        self.assertEqual((code, errors), (0, ""))
        self.assertEqual(json.loads(output), pointer)
        self.assertEqual(
            self.invoke_cli("clear-pointer", "--repo-root", ".", "--owner-token", token, "--plan-path", PLAN, "--contract-sha256", pointer["contract_sha256"], "--completed", "true")[0],
            0,
        )
        self.assertEqual(
            self.invoke_cli("release-final", "--repo-root", ".", "--owner-token", token, "--completed-execution", "true", "--completed-plan-only", "false", "--outcomes-known", "true", "--no-child-can-mutate", "true")[0],
            0,
        )

    def test_cli_provisional_plan_only_and_stale_recovery_paths(self) -> None:
        code, output, _ = self.invoke_cli("acquire", "--repo-root", ".")
        self.assertEqual(code, 0)
        token = json.loads(output)["owner_token"]
        self.assertEqual(
            self.invoke_cli("release-provisional", "--repo-root", ".", "--owner-token", token, "--known-clean", "true", "--no-mutation", "true", "--no-child-can-mutate", "true")[0],
            0,
        )
        code, output, _ = self.invoke_cli("acquire", "--repo-root", ".")
        token = json.loads(output)["owner_token"]
        self.assertEqual(self.invoke_cli("finalize", "--repo-root", ".", "--owner-token", token, "--plan-path", PLAN)[0], 0)
        self.assertEqual(
            self.invoke_cli("release-final", "--repo-root", ".", "--owner-token", token, "--completed-execution", "false", "--completed-plan-only", "true", "--outcomes-known", "true", "--no-child-can-mutate", "true")[0],
            0,
        )
        code, _, _ = self.invoke_cli("acquire", "--repo-root", ".")
        self.assertEqual(code, 0)
        (self.root / ".start-work/lock/owner.json").write_text("{", encoding="utf-8")
        self.assertEqual(self.invoke_cli("recover-stale", "--repo-root", ".", "--prior-human-confirmation", "true")[0], 0)

    def test_cli_rejects_invalid_grammar_and_pre_acquisition_reads_without_leaks(self) -> None:
        state_dir = self.root / ".start-work"
        state_dir.mkdir()
        (state_dir / "resume.json").write_text(json.dumps({"version": 1, "plan_path": PLAN, "contract_sha256": "a" * 64}), encoding="utf-8")
        cases = (
            ("acquire", "--repo-root", "./"),
            ("acquire", "--repo-root", ".", "--owner-token", TOKEN),
            ("read-pointer", "--repo-root", ".", "--owner-token", TOKEN),
            ("finalize", "--repo-root", ".", "--owner-token", "not-a-token", "--plan-path", PLAN),
            ("release-final", "--repo-root", ".", "--owner-token", TOKEN, "--completed-execution", "maybe"),
        )
        for arguments in cases:
            code, output, errors = self.invoke_cli(*arguments)
            self.assertEqual((code, output), (1, ""))
            self.assertEqual(errors, "start-work state error\n")
            self.assertNotIn(str(self.root), errors)

    def test_cli_unknown_arguments_are_not_reflected(self) -> None:
        hostile = "$(cat /private/secret);--path=/tmp/hostile"
        code, output, errors = self.invoke_cli("acquire", "--repo-root", ".", "--unknown", hostile)
        self.assertEqual((code, output, errors), (1, "", "start-work state error\n"))
        self.assertNotIn(hostile, output)
        self.assertNotIn(hostile, errors)
        self.assertNotIn("/private/secret", errors)

    def test_pointer_limit_bool_versions_and_full_plan_grammar(self) -> None:
        self.acquire()
        state.finalize_owner(self.root, TOKEN, PLAN)
        resume = self.root / ".start-work/resume.json"
        resume.write_bytes(b"x" * (state.MAX_POINTER_BYTES + 1))
        with self.assertRaises(state.StateError):
            state.read_resume_pointer(self.root, TOKEN)
        resume.write_text(json.dumps({"version": True, "plan_path": PLAN, "contract_sha256": "a" * 64}), encoding="utf-8")
        with self.assertRaises(state.StateError):
            state.read_resume_pointer(self.root, TOKEN)
        owner = self.root / ".start-work/lock/owner.json"
        owner.write_text(json.dumps({"version": True, "owner_token": TOKEN, "plan_path": PLAN}), encoding="utf-8")
        with self.assertRaises(state.StateError):
            state.read_resume_pointer(self.root, TOKEN)
        for invalid in (
            "docs/implementation-plans/plans/A/01-slug.md",
            "docs/implementation-plans/plans/a/00-slug.md",
            "docs/implementation-plans/plans/a/100-slug.md",
            "docs/implementation-plans/plans/a/01-unsafe_slug.md",
            "docs/implementation-plans/plans/a/01--slug.md",
            "docs/implementation-plans/plans/a/01-Slug.md",
        ):
            with self.assertRaises(state.StateError):
                state._canonical_plan_path(invalid)

    def test_owner_and_resume_schemas_reject_unknown_oversized_and_invalid_utf8(self) -> None:
        self.acquire()
        owner = self.root / ".start-work/lock/owner.json"
        owner.write_text(json.dumps({"version": 1, "owner_token": TOKEN, "plan_path": None, "extra": True}), encoding="utf-8")
        with self.assertRaises(state.StateError):
            state.finalize_owner(self.root, TOKEN, PLAN)
        owner.write_bytes(b"x" * 513)
        with self.assertRaises(state.StateError):
            state.finalize_owner(self.root, TOKEN, PLAN)
        owner.write_bytes(b"\xff")
        state.recover_stale_lock(self.root, prior_human_confirmation=True)
        self.acquire()
        owner = self.root / ".start-work/lock/owner.json"
        owner.unlink()
        owner.symlink_to(self.root / PLAN)
        with self.assertRaises(state.StateError):
            state.recover_stale_lock(self.root, prior_human_confirmation=True)


if __name__ == "__main__":
    unittest.main()
