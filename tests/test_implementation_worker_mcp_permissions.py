import unittest

from tools.opencode_manager import OpenCodeInstallService


CONFIGURED_MCP_TOOL_PATTERNS = (
    "playwright_*",
    "chrome-devtools_*",
    "serena_*",
    "context7_*",
    "gh_grep_*",
    "github_*",
)


def worker_permissions(
    patterns: tuple[str, ...] = CONFIGURED_MCP_TOOL_PATTERNS,
) -> dict[str, str | tuple[tuple[str, str], ...]]:
    permissions: dict[str, str | tuple[tuple[str, str], ...]] = {
        "*": "ask",
        "bash": (("*", "ask"),),
        "task": "deny",
        "webfetch": "deny",
        "websearch": "deny",
    }
    permissions.update({pattern: "allow" for pattern in patterns})
    return permissions


class ImplementationWorkerMcpPermissionTests(unittest.TestCase):
    def test_validator_accepts_all_configured_worker_mcp_permissions(self) -> None:
        errors = OpenCodeInstallService._validate_capability_schema(
            "implementation-worker.md",
            "implementation-worker",
            worker_permissions(),
            "ask",
        )

        self.assertEqual(errors, [])

    def test_validator_requires_every_configured_worker_mcp_permission(self) -> None:
        patterns = tuple(
            pattern for pattern in CONFIGURED_MCP_TOOL_PATTERNS if pattern != "github_*"
        )

        errors = OpenCodeInstallService._validate_capability_schema(
            "implementation-worker.md",
            "implementation-worker",
            worker_permissions(patterns),
            "ask",
        )

        self.assertTrue(
            any("configured MCP tool pattern" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
