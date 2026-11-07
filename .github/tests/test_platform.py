"""Regression tests for 4FusionLab shared, nonpublishing release actions."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1] / "actions"


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


detect = load("detect", "runtime-changes/detect.py")
notes = load("notes", "release-notes/notes.py")
verify = load("verify", "verify-archive/verify.py")


class ChangeGateTests(unittest.TestCase):
    def test_documentation_only_does_not_release(self):
        rules = ["Perfora/**", "install.py"]
        self.assertEqual(detect.impacted(["README.md", "docs/USAGE.md",
                                          "tests/test_engine.py", ".github/workflows/ci.yml"],
                                         rules), [])

    def test_runtime_and_deletions_release(self):
        rules = ["Perfora/**", "install.py"]
        self.assertEqual(detect.impacted(["Perfora/core.py", "docs/README.md"], rules),
                         ["Perfora/core.py"])
        self.assertTrue(detect.evaluate(["Perfora/obsolete.py"], rules)[0])

    def test_nested_exclusions_and_catalog_json(self):
        rules = ["frontend/src/**", "!frontend/**/*.test.*",
                 "catalog/brands/**.json"]
        self.assertEqual(detect.impacted(["frontend/src/main.tsx",
                                          "frontend/src/view.test.tsx",
                                          "catalog/brands/abc/pla.json",
                                          "catalog/brands/README.md"], rules),
                         ["frontend/src/main.tsx", "catalog/brands/abc/pla.json"])

    def test_diff_for_removed_runtime_file(self):
        with tempfile.TemporaryDirectory() as temp:
            def git(*args):
                return subprocess.run(["git", *args], cwd=temp, text=True,
                                      check=True, capture_output=True).stdout.strip()
            git("init", "-b", "main")
            git("config", "user.name", "CI")
            git("config", "user.email", "ci@example.invalid")
            path = Path(temp, "Perfora")
            path.mkdir()
            (path / "remove.py").write_text("print('hi')\n")
            git("add", ".")
            git("commit", "-m", "feat: add runtime")
            before = git("rev-parse", "HEAD")
            (path / "remove.py").unlink()
            git("add", "-u")
            git("commit", "-m", "fix: remove runtime")
            after = git("rev-parse", "HEAD")
            previous = os.getcwd()
            try:
                os.chdir(temp)
                self.assertEqual(detect.git_paths(before, after), ["Perfora/remove.py"])
            finally:
                os.chdir(previous)


class NotesTests(unittest.TestCase):
    def test_prefer_reviewed_notes(self):
        with tempfile.TemporaryDirectory() as temp:
            reviewed = Path(temp, "reviewed.md")
            output = Path(temp, "notes.md")
            reviewed.write_text("# Reviewed notes\n", encoding="utf-8")
            mode = notes.create_notes("Perfora", "1.2.3", str(reviewed), str(output))
            self.assertEqual(mode, "reviewed")
            self.assertEqual(output.read_text(), "# Reviewed notes\n")

    def test_generate_from_git_history(self):
        with tempfile.TemporaryDirectory() as temp:
            def git(*args):
                return subprocess.run(["git", *args], cwd=temp, text=True,
                                      check=True, capture_output=True).stdout.strip()
            git("init", "-b", "main")
            git("config", "user.name", "CI")
            git("config", "user.email", "ci@example.invalid")
            Path(temp, "README.md").write_text("old")
            git("add", ".")
            git("commit", "-m", "chore: baseline")
            git("tag", "v1.0.0")
            Path(temp, "src.py").write_text("new")
            git("add", ".")
            git("commit", "-m", "feat: useful improvement")
            previous = os.getcwd()
            try:
                os.chdir(temp)
                output = Path(temp, "notes.md")
                self.assertEqual(notes.create_notes("Perfora", "1.1.0", "", output),
                                 "generated")
                self.assertIn("feat: useful improvement", output.read_text())
                self.assertIn("v1.0.0", output.read_text())
            finally:
                os.chdir(previous)


class PackageTests(unittest.TestCase):
    def make_package(self, temp):
        archive = Path(temp, "Perfora-1.2.3.zip")
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("Perfora/Perfora.manifest",
                       json.dumps({"type": "addin", "version": "1.2.3"}))
            z.writestr("Perfora/Perfora.py", "print('ok')")
        checksum = archive.with_suffix(".zip.sha256")
        checksum.write_text(hashlib.sha256(archive.read_bytes()).hexdigest() +
                            "  " + archive.name + "\n", encoding="ascii")
        return archive, checksum

    def test_valid_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            archive, _ = self.make_package(temp)
            self.assertEqual(verify.verify("Perfora", "1.2.3",
                                           [archive], "Perfora/Perfora.manifest"), 1)

    def test_wrong_checksum_blocks_publication(self):
        with tempfile.TemporaryDirectory() as temp:
            archive, checksum = self.make_package(temp)
            checksum.write_text("invalid\n", encoding="ascii")
            with self.assertRaises(ValueError):
                verify.verify("Perfora", "1.2.3", [archive], "Perfora/Perfora.manifest")

    def test_wrong_manifest_blocks_publication(self):
        with tempfile.TemporaryDirectory() as temp:
            archive, _ = self.make_package(temp)
            with self.assertRaises(KeyError):
                verify.verify("Perfora", "1.2.3", [archive], "Perfora/not-a-file.manifest")


if __name__ == "__main__":
    unittest.main()
