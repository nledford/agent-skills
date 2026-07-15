set shell := ["sh", "-cu"]

python := "python3"
manager := "tools/skills_manager.py"
opencode_manager := "tools/opencode_manager.py"

# Show available commands.
[group('docs')]
default:
    @just --list

# Show available commands.
[group('docs')]
help:
    @just --list

# Create ~/.agents/skills as a symlink to this repository's skills/ directory.
[group('bootstrap')]
setup:
    @{{python}} {{manager}} setup

# Preview global symlink setup without changing files.
[group('bootstrap')]
setup-dry-run:
    @{{python}} {{manager}} setup --dry-run

# Verify ~/.agents/skills points to skills/ and exposes skills.
[group('bootstrap')]
verify:
    @{{python}} {{manager}} verify

# Run skill validation and global symlink verification.
[group('bootstrap')]
doctor:
    @{{python}} {{manager}} doctor

# Remove ~/.agents/skills only when it is this repository's symlink.
[group('bootstrap')]
uninstall:
    @{{python}} {{manager}} uninstall

# Preview removing this repository's global symlink.
[group('bootstrap')]
uninstall-dry-run:
    @{{python}} {{manager}} uninstall --dry-run

# Validate repository-managed OpenCode agents and commands.
[group('opencode')]
validate-opencode:
    @{{python}} {{opencode_manager}} validate

# Create all three global OpenCode links when their destinations are safe.
[group('opencode')]
setup-opencode:
    @{{python}} {{opencode_manager}} setup

# Preview global OpenCode symlink setup without changing files.
[group('opencode')]
setup-opencode-dry-run:
    @{{python}} {{opencode_manager}} setup --dry-run

# Verify repository definitions and all three global OpenCode links.
[group('opencode')]
verify-opencode:
    @{{python}} {{opencode_manager}} verify

# Validate and verify the repository-managed OpenCode installation.
[group('opencode')]
doctor-opencode:
    @{{python}} {{opencode_manager}} doctor

# Remove all three global OpenCode links only when this repository owns them.
[group('opencode')]
uninstall-opencode:
    @{{python}} {{opencode_manager}} uninstall

# Preview removal of both repository-owned OpenCode symlinks.
[group('opencode')]
uninstall-opencode-dry-run:
    @{{python}} {{opencode_manager}} uninstall --dry-run

# List all discovered skills.
[group('skills')]
list:
    @{{python}} {{manager}} list

# Inspect one skill by name.
[group('skills')]
inspect skill:
    @{{python}} {{manager}} inspect '{{skill}}'

# Validate all discovered skills.
[group('skills')]
validate:
    @{{python}} {{manager}} validate

# List first-party skills.
[group('first-party')]
list-first-party:
    @{{python}} {{manager}} list --kind first-party

# Validate first-party skills.
[group('first-party')]
validate-first-party:
    @{{python}} {{manager}} validate --kind first-party

# List third-party skills.
[group('third-party')]
list-third-party:
    @{{python}} {{manager}} list --kind third-party

# Validate third-party skills and lockfile-listed installs.
[group('third-party')]
validate-third-party:
    @{{python}} {{manager}} validate --kind third-party

# Update third-party skills with npx skills or SKILLS_UPDATE_COMMAND.
[group('third-party')]
update-third-party:
    @{{python}} {{manager}} update-third-party

# Preview the third-party update command.
[group('third-party')]
update-third-party-dry-run:
    @{{python}} {{manager}} update-third-party --dry-run

# Copy the repository skill lockfile to ~/.agents/.skill-lock.json.
[group('third-party')]
sync-third-party-lock:
    @{{python}} {{manager}} sync-third-party-lock

# Preview copying the repository skill lockfile to ~/.agents/.skill-lock.json.
[group('third-party')]
sync-third-party-lock-dry-run:
    @{{python}} {{manager}} sync-third-party-lock --dry-run

# Run unit tests for helper behavior.
[group('quality')]
test:
    @{{python}} -m unittest discover -s tests -v

# Compile Python helpers, workflow tools, and tests to catch syntax errors.
[group('quality')]
lint:
    @{{python}} -m compileall -q tools opencode/workflow-tools tests

# Report formatter status.
[group('quality')]
format:
    @echo "No formatter is configured; Python code uses the standard library only."

# Run the source quality gate without inspecting global installations.
[group('quality')]
check: lint test validate validate-opencode

# Remove Python cache files.
[group('quality')]
clean:
    @{{python}} {{manager}} clean
