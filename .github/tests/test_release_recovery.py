"""Regression tests for opt-in recovery of GitHub Releases that failed CI.

All tests use local Git history and mocked GitHub API responses. No releases,
tags on real repositories, network calls or writes to remote branches occur.
"""

import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


DETECTOR = Path(__file__).resolve().parents[1] / "actions" / "runtime-changes" / "detect.py"
SPEC = importlib.util.spec_from_file_location("recovery_detector", DETECTOR)
detect = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(detect)


def release(tag, published_at="2026-11-07T09:00:00Z", *, draft=False, assets=None):
    return {
        "tag_name": tag,
        "draft": draft,
        "published_at": published_at,
        "assets": [{"name": name} for name in (
            ["Example-1.0.0.zip"] if assets is None else assets
        )],
    }


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.original_cwd = os.getcwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, self.original_cwd)
        self.git("init", "-b", "main")
        self.git("config", "user.name", "CI")
        self.git("config", "user.email", "ci@example.invalid")
        self.rules = ["Example/**", "scripts/build_release.py"]

    def git(self, *args):
        return subprocess.run(
            ["git", *args], check=True, capture_output=True, text=True,
        ).stdout.strip()

    def file(self, path, contents="new"):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(contents, encoding="utf-8")

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-m", message)
        return self.git("rev-parse", "HEAD")

    def baseline(self, tag="v1.0.0"):
        self.file("Example/runtime.py", "baseline")
        sha = self.commit("initial published runtime")
        self.git("tag", tag)
        return sha

    def test_failed_runtime_release_recovers_on_docs_only_push(self):
        baseline = self.baseline()
        self.file("Example/runtime.py", "new runtime")
        failed = self.commit("feat: runtime changed, CI publication failed")
        self.file("README.md", "docs")
        current = self.commit("docs: update README")
        self.assertEqual(detect.impacted(detect.git_paths(failed, current), self.rules), [])
        with mock.patch.object(detect, "fetch_releases", return_value=[release("v1.0.0")]):
            start, tag = detect.release_baseline(failed, current, "4FusionLab/Example", "token")
        self.assertEqual((start, tag), (baseline, "v1.0.0"))
        matched = detect.impacted(detect.git_paths(start, current), self.rules)
        self.assertEqual(matched, ["Example/runtime.py"])

    def test_after_successful_release_docs_only_never_releases(self):
        self.baseline()
        self.file("Example/runtime.py", "published change")
        runtime = self.commit("fix: published change")
        self.git("tag", "v1.0.1")
        self.file("README.md", "docs")
        current = self.commit("docs only")
        with mock.patch.object(detect, "fetch_releases", return_value=[
            release("v1.0.0", "2026-11-06T09:00:00Z"),
            release("v1.0.1", "2026-11-07T09:00:00Z"),
        ]):
            start, tag = detect.release_baseline(runtime, current, "4FusionLab/Example", "token")
        self.assertEqual((start, tag), (runtime, "v1.0.1"))
        self.assertFalse(detect.evaluate(detect.git_paths(start, current), self.rules)[0])

    def test_no_published_release_preserves_legacy_push_range(self):
        self.baseline()
        self.file("Example/runtime.py", "unpublished change")
        previous = self.commit("runtime change never published")
        self.file("README.md", "docs")
        current = self.commit("documentation")
        with mock.patch.object(detect, "fetch_releases", return_value=[]):
            start, tag = detect.release_baseline(previous, current, "4FusionLab/Example", "token")
        self.assertEqual((start, tag), (previous, ""))
        self.assertFalse(detect.evaluate(detect.git_paths(start, current), self.rules)[0])

    def test_newest_published_ancestor_not_most_recent_unrelated_release(self):
        baseline = self.baseline()
        self.file("Example/runtime.py", "main branch change")
        head = self.commit("main runtime")
        self.git("checkout", "--orphan", "other")
        self.git("rm", "-r", "-f", ".")
        self.file("README.md", "different branch")
        self.commit("other branch")
        self.git("tag", "v9.0.0")
        self.git("checkout", "main")
        checkpoint = detect.published_release_anchor(head, [
            release("v9.0.0", "2026-11-08T09:00:00Z"),
            release("v1.0.0", "2026-11-07T09:00:00Z"),
        ])
        self.assertEqual(checkpoint, ("v1.0.0", baseline))

    def test_draft_without_zip_and_malformed_tag_are_not_checkpoints(self):
        baseline = self.baseline()
        self.assertEqual(detect.published_release_anchor(baseline, [
            release("v5.0.0", draft=True),
            release("v4.0.0", assets=["release-notes.md"]),
            release("v1.0.0; echo BAD"),
            release("v1.0.0"),
        ]), ("v1.0.0", baseline))

    def test_unfetchable_published_tag_fails_closed(self):
        baseline = self.baseline()
        with self.assertRaisesRegex(RuntimeError, "no local tag"):
            detect.published_release_anchor(baseline, [release("v2.0.0")])

    def test_http_failure_does_not_silently_disable_recovery(self):
        with mock.patch.object(detect, "urlopen", side_effect=OSError("API offline")):
            with self.assertRaisesRegex(OSError, "API offline"):
                detect.fetch_releases("4FusionLab/Example", "token")
        with self.assertRaisesRegex(ValueError, "GITHUB_TOKEN"):
            detect.fetch_releases("4FusionLab/Example", "")
        with self.assertRaisesRegex(ValueError, "owner/repository"):
            detect.fetch_releases("../unsafe", "token")

    def test_api_pagination_and_bearer_auth(self):
        class APIResponse(io.BytesIO):
            pass

        seen = []

        def urlopen(req, timeout):
            seen.append((req.full_url, req.headers.get("Authorization"), timeout))
            data = [release("v1.0.0")] * (100 if len(seen) == 1 else 1)
            return APIResponse(json.dumps(data).encode("utf-8"))

        with mock.patch.object(detect, "urlopen", side_effect=urlopen):
            releases = detect.fetch_releases("4FusionLab/Example", "secure")
        self.assertEqual(len(releases), 101)
        self.assertEqual(len(seen), 2)
        self.assertTrue(seen[0][0].endswith("page=1"))
        self.assertTrue(seen[1][0].endswith("page=2"))
        self.assertEqual(seen[0][1], "Bearer secure")

    def test_composite_outputs_have_real_newlines_and_valid_version_tags(self):
        baseline = self.baseline()
        self.file("Example/feature.py")
        current = self.commit("runtime missing release")
        self.assertTrue(detect.VERSION_TAG.fullmatch("v1.2.3"))
        self.assertTrue(detect.VERSION_TAG.fullmatch("v1.2.3-beta.1"))
        self.assertFalse(detect.VERSION_TAG.fullmatch("v1_2_3"))
        config = self.root / "release-paths.txt"
        config.write_text("Example/**\n", encoding="utf-8")
        output = self.root / "output"
        args = [
            "detect.py", "--config", str(config), "--before", baseline,
            "--after", current, "--github-output", str(output),
            "--recover-unpublished",
        ]
        with mock.patch.object(sys, "argv", args), mock.patch.object(
            detect, "fetch_releases", return_value=[release("v1.0.0")]
        ), mock.patch.dict(os.environ, {
            "GITHUB_REPOSITORY": "4FusionLab/Example", "GITHUB_TOKEN": "token",
        }):
            detect.main()
        self.assertEqual(output.read_text(encoding="utf-8"), (
            "release=true\nmatched_count=1\n"
            f"baseline_sha={baseline}\nbaseline_tag=v1.0.0\n"
        ))


if __name__ == "__main__":
    unittest.main()
