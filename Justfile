set shell := ["sh", "-cu"]

python := "python3"
manager := "tools/skills_manager.py"

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

# Update third-party skills with bunx skills or SKILLS_UPDATE_COMMAND.
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

# Compile Python helpers and tests to catch syntax errors.
[group('quality')]
lint:
    @{{python}} -m compileall -q tools tests

# Report formatter status.
[group('quality')]
format:
    @echo "No formatter is configured; Python code uses the standard library only."

# Run the full non-mutating quality gate.
[group('quality')]
check: lint test validate verify

# Remove Python cache files.
[group('quality')]
clean:
    @{{python}} {{manager}} clean
