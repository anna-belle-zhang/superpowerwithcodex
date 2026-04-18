"""Regression tests for canonical Codex installation paths."""

import os


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CODEX_DIR = os.path.join(REPO_ROOT, ".codex")


def _read_codex_file(filename):
    path = os.path.join(CODEX_DIR, filename)
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


class TestSuperpowerwithcodexPaths:
    """Codex-facing entrypoints should use only the canonical repo name."""

    def test_install_doc_uses_canonical_codex_paths(self):
        content = _read_codex_file("INSTALL.md")
        assert "~/.codex/superpowerwithcodex" in content
        assert "superpowers-codex" not in content
        assert "~/.codex/superpowers" not in content

    def test_bootstrap_doc_uses_canonical_codex_paths(self):
        content = _read_codex_file("superpowerwithcodex-bootstrap.md")
        assert "~/.codex/superpowerwithcodex" in content
        assert "superpowers-codex" not in content
        assert "~/.codex/superpowers" not in content

    def test_codex_cli_uses_canonical_runtime_paths(self):
        content = _read_codex_file("superpowerwithcodex-codex")
        assert "superpowerwithcodex" in content
        assert "~/.codex/superpowers" not in content
        assert "superpowers-codex" not in content

    def test_legacy_superpowers_codex_files_removed(self):
        assert not os.path.exists(os.path.join(CODEX_DIR, "superpowers-codex"))
        assert not os.path.exists(os.path.join(CODEX_DIR, "superpowers-bootstrap.md"))
