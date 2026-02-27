"""Shared fixtures for structured-specs-integration tests."""

import os
import re
import shutil
import tempfile

import pytest


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")
COMMANDS_DIR = os.path.join(REPO_ROOT, "commands")
DOCS_DIR = os.path.join(REPO_ROOT, "docs")


# ---------------------------------------------------------------------------
# Helper functions (used by fixtures and directly in tests via fixtures)
# ---------------------------------------------------------------------------

def _read_skill(skill_name):
    """Read a SKILL.md file and return its content."""
    path = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _read_command(command_name):
    """Read a command .md file and return its content."""
    path = os.path.join(COMMANDS_DIR, f"{command_name}.md")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    lines = content.split("\n")
    in_frontmatter = False
    frontmatter = {}

    for line in lines:
        if line.strip() == "---":
            if in_frontmatter:
                break
            in_frontmatter = True
            continue

        if in_frontmatter:
            match = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
            if match:
                key, value = match.groups()
                frontmatter[key] = value.strip()

    return frontmatter


def _parse_delta_spec(content):
    """Parse a delta spec markdown into structured sections.

    Returns dict with keys: ADDED, MODIFIED, REMOVED.
    Each value is a list of dicts with 'name', 'scenarios', and 'meta' keys.
    """
    sections = {"ADDED": [], "MODIFIED": [], "REMOVED": []}
    current_section = None
    current_behavior = None

    for line in content.split("\n"):
        stripped = line.strip()

        if stripped == "## ADDED":
            current_section = "ADDED"
            current_behavior = None
        elif stripped == "## MODIFIED":
            current_section = "MODIFIED"
            current_behavior = None
        elif stripped == "## REMOVED":
            current_section = "REMOVED"
            current_behavior = None
        elif stripped.startswith("### ") and current_section:
            behavior_name = stripped[4:]
            current_behavior = {"name": behavior_name, "scenarios": [], "meta": {}}
            sections[current_section].append(current_behavior)
        elif current_behavior:
            if stripped.startswith("GIVEN "):
                current_behavior["scenarios"].append({"given": stripped})
            elif stripped.startswith("WHEN ") and current_behavior["scenarios"]:
                current_behavior["scenarios"][-1]["when"] = stripped
            elif stripped.startswith("THEN ") and current_behavior["scenarios"]:
                current_behavior["scenarios"][-1]["then"] = stripped
            elif stripped.startswith("**Was:**"):
                current_behavior["meta"]["was"] = stripped
            elif stripped.startswith("**Now:**"):
                current_behavior["meta"]["now"] = stripped
            elif stripped.startswith("**Reason:**"):
                current_behavior["meta"]["reason"] = stripped

    return sections


# ---------------------------------------------------------------------------
# Fixtures that expose helpers and constants to test files
# ---------------------------------------------------------------------------

@pytest.fixture
def repo_root():
    return REPO_ROOT


@pytest.fixture
def skills_dir():
    return SKILLS_DIR


@pytest.fixture
def commands_dir():
    return COMMANDS_DIR


@pytest.fixture
def read_skill():
    """Fixture returning the read_skill helper function."""
    return _read_skill


@pytest.fixture
def read_command():
    """Fixture returning the read_command helper function."""
    return _read_command


@pytest.fixture
def extract_frontmatter():
    """Fixture returning the extract_frontmatter helper function."""
    return _extract_frontmatter


@pytest.fixture
def parse_delta_spec():
    """Fixture returning the parse_delta_spec helper function."""
    return _parse_delta_spec


@pytest.fixture
def tmp_specs_dir():
    """Create a temporary specs directory structure for testing."""
    tmpdir = tempfile.mkdtemp(prefix="specs-test-")
    feature_dir = os.path.join(tmpdir, "docs", "specs", "test-feature", "specs")
    living_dir = os.path.join(tmpdir, "docs", "specs", "_living")
    archive_dir = os.path.join(tmpdir, "docs", "specs", "_archive")
    os.makedirs(feature_dir)
    os.makedirs(living_dir)
    os.makedirs(archive_dir)

    yield {
        "root": tmpdir,
        "feature": os.path.join(tmpdir, "docs", "specs", "test-feature"),
        "specs": feature_dir,
        "living": living_dir,
        "archive": archive_dir,
    }

    shutil.rmtree(tmpdir)
