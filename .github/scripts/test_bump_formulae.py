#!/usr/bin/env python3
"""Unit tests for bump-formulae.py (no network calls)."""

import importlib.util
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).with_name("bump-formulae.py")
spec = importlib.util.spec_from_file_location("bump_formulae", SCRIPT_PATH)
bump = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(bump)

SAMPLE_FORMULA = """\
# autobump: scallister/example
class Example < Formula
  desc "Example tool"
  homepage "https://github.com/scallister/example"
  url "https://github.com/scallister/example.git",
    tag: "v1.0.0",
    :using => :git

  version "v1.0.0"

  def install
    bin.install "example"
  end
end
"""

BRANCH_FORMULA = """\
# autobump: scallister/example
class Example < Formula
  url "https://github.com/scallister/example.git",
    branch: "main",
    :using => :git

  version "v1.0.0"
end
"""


class TestBumpFormulae(unittest.TestCase):
    def test_parse_autobump_repo(self):
        self.assertEqual(
            bump.parse_autobump_repo(SAMPLE_FORMULA),
            ("scallister", "example"),
        )
        self.assertIsNone(bump.parse_autobump_repo("class Foo < Formula\nend\n"))

    def test_current_version(self):
        self.assertEqual(bump.current_version(SAMPLE_FORMULA), "v1.0.0")

    def test_parse_version(self):
        self.assertEqual(bump.parse_version("v1.0.4"), (1, 0, 4))
        self.assertEqual(bump.parse_version("v0.0.10"), (0, 0, 10))
        self.assertIsNone(bump.parse_version("latest"))

    def test_latest_release_tag(self):
        self.assertEqual(
            bump.latest_release_tag(["v1.0.0", "v1.0.4", "v1.0.10", "latest"]),
            "v1.0.10",
        )

    def test_version_outdated(self):
        self.assertTrue(bump.version_outdated("v1.0.0", "v1.0.1"))
        self.assertFalse(bump.version_outdated("v1.0.4", "v1.0.4"))
        self.assertFalse(bump.version_outdated("v2.0.0", "v1.9.9"))

    def test_bump_formula_contents_updates_tag(self):
        updated = bump.bump_formula_contents(SAMPLE_FORMULA, "v1.2.3")
        self.assertIn('version "v1.2.3"', updated)
        self.assertIn('tag: "v1.2.3",', updated)
        self.assertNotIn("v1.0.0", updated)

    def test_bump_formula_contents_converts_branch_to_tag(self):
        updated = bump.bump_formula_contents(BRANCH_FORMULA, "v2.0.0")
        self.assertIn('tag: "v2.0.0",', updated)
        self.assertNotIn("branch:", updated)
        self.assertIn('version "v2.0.0"', updated)


if __name__ == "__main__":
    unittest.main()
