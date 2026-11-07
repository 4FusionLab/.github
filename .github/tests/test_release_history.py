"""End-to-end Git range regressions for the shared release eligibility gate.

Exercises the same subprocess-based classifier used by production composite
Actions. No remote repositories, publication, tags or network calls are needed.
"""

import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


CLASSIFIER = Path(__file__).resolve().parents[1] / "actions" / "runtime-changes" / "detect.py"
SPEC = importlib.util.spec_from_file_location("release_range_detector", CLASSIFIER)
detect = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(detect)


class GitRangeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-b", "main")
        self.git("config", "user.name", "CI tests")
        self.git("config", "user.email", "ci@example.invalid")

    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.root, check=True,
            capture_output=True, text=True,
        ).stdout.strip()

    def put(self, path, value="change"):
        dest = self.root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(value, encoding="utf-8")

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-m", message)
        return self.git("rev-parse", "HEAD")

    def changed(self, before, after):
        # git_paths() is intentionally cwd-based, exactly as in the GH Action.
        previous = os.getcwd()
        try:
            os.chdir(self.root)
            return detect.git_paths(before, after)
        finally:
            os.chdir(previous)

    def test_first_push_scans_full_tree(self):
        self.put("README.md", "docs")
        self.put("Perfora/Perfora.py", "source")
        head = self.commit("initial")
        paths = self.changed("0" * 40, head)
        self.assertEqual(paths, ["Perfora/Perfora.py", "README.md"])
        eligible, matched = detect.evaluate(paths, ["Perfora/**", "install.py"])
        self.assertTrue(eligible)
        self.assertEqual(matched, ["Perfora/Perfora.py"])

    def test_rename_out_of_runtime_still_releases(self):
        self.put("Perfora/engine.py")
        base = self.commit("runtime initial")
        (self.root / "docs").mkdir()
        self.git("mv", "Perfora/engine.py", "docs/engine.py")
        head = self.commit("move code to documentation")
        paths = self.changed(base, head)
        self.assertEqual(paths, ["Perfora/engine.py", "docs/engine.py"])
        self.assertEqual(detect.evaluate(paths, ["Perfora/**"])[1], ["Perfora/engine.py"])

    def test_full_push_range_detects_intermediate_runtime_commit(self):
        self.put("README.md", "base")
        base = self.commit("initial documentation")
        self.put("docs/guide.md", "updated")
        self.commit("docs only")
        self.put("Perfora/geometry.py", "new runtime module")
        self.commit("runtime update")
        self.put("README.md", "newer documentation")
        head = self.commit("final documentation")
        paths = self.changed(base, head)
        self.assertIn("Perfora/geometry.py", paths)
        self.assertEqual(detect.evaluate(paths, ["Perfora/**"])[1], ["Perfora/geometry.py"])

    def test_documentation_only_range_does_not_release(self):
        self.put("Perfora/geometry.py", "unchanged runtime")
        base = self.commit("baseline")
        self.put("README.md", "updated")
        self.put("tests/test_geometry.py", "tests only")
        head = self.commit("metadata updates")
        paths = self.changed(base, head)
        self.assertFalse(detect.evaluate(paths, ["Perfora/**", "install.py"])[0])


if __name__ == "__main__":
    unittest.main()
