"""Determine release eligibility from changes since the last published release.

Legacy mode checks only github.event.before..github.sha. In opt-in recovery
mode, consider the cumulative net Git diff since the last published GitHub
Release on this branch. This repairs missed publications on later docs-only
pushes without touching or moving historical release tags.
"""
import argparse
import fnmatch
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.request import Request, urlopen


VERSION_TAG = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+(?:-[a-zA-Z0-9][a-zA-Z0-9.-]*)?$")
REPOSITORY = re.compile(r"^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$")


def read_rules(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    rules = [line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#")]
    if not any(not line.startswith("!") for line in rules):
        raise ValueError("Release paths must contain at least one positive pattern.")
    return rules


def impacted(files, rules):
    include = [pattern for pattern in rules if not pattern.startswith("!")]
    exclude = [pattern[1:] for pattern in rules if pattern.startswith("!")]
    return [path for path in files
            if any(fnmatch.fnmatchcase(path, pattern) for pattern in include)
            and not any(fnmatch.fnmatchcase(path, pattern) for pattern in exclude)]


def git_paths(before, after):
    if not after:
        raise ValueError("An after SHA is required.")
    if not before or before == "0" * 40:
        command = ["git", "ls-tree", "-rz", "--name-only", after]
    else:
        # --no-renames reports both old and new paths; deleted runtime files count too.
        command = ["git", "diff", "--name-only", "-z", "--no-renames", before, after]
    stdout = subprocess.check_output(command)
    return [entry.decode("utf-8", errors="surrogateescape")
            for entry in stdout.split(b"\0") if entry]


def evaluate(paths, rules):
    changed = list(paths)
    matches = impacted(changed, rules)
    return len(matches) > 0, matches


def fetch_releases(repository, token):
    """Fail closed on API failures, rather than silently losing recovery."""
    if (not REPOSITORY.fullmatch(repository)
            or any(component in (".", "..") for component in repository.split("/"))):
        raise ValueError("Expected a GitHub owner/repository name.")
    if not token:
        raise ValueError("GITHUB_TOKEN is required to recover unpublished releases.")
    results = []
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + token,
        "User-Agent": "4FusionLab-Release-Recovery",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    for page in range(1, 102):
        url = f"https://api.github.com/repos/{repository}/releases?per_page=100&page={page}"
        with urlopen(Request(url, headers=headers), timeout=30) as response:
            batch = json.load(response)
        if not isinstance(batch, list):
            raise ValueError("Unexpected response while listing published Releases.")
        results.extend(batch)
        if len(batch) < 100:
            return results
    raise ValueError("Published release pagination limit exceeded.")


def published_release_anchor(after, releases):
    """Return (tag, SHA) for the newest valid, published ancestor release.

    An old published release may omit sidecar SHA-256 files (RuEn v1.0.0),
    so ZIP assets suffice to establish a historical checkpoint. New releases
    still have their own ZIP, manifest and checksum verification gates.
    """
    candidates = []
    for item in releases:
        if item.get("draft") or not item.get("published_at"):
            continue
        tag = item.get("tag_name", "")
        if not VERSION_TAG.fullmatch(tag):
            continue
        assets = item.get("assets") or []
        if not any(a.get("name", "").endswith(".zip") for a in assets):
            continue
        candidates.append((item["published_at"], tag))
    for _published_at, tag in sorted(candidates, reverse=True):
        ref = f"refs/tags/{tag}^{{commit}}"
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", ref],
            capture_output=True, text=True,
        )
        if result.returncode:
            raise RuntimeError(f"Published GitHub Release has no local tag: {tag}. Fetch all tags.")
        sha = result.stdout.strip()
        ancestry = subprocess.run(["git", "merge-base", "--is-ancestor", sha, after])
        if ancestry.returncode == 0:
            return tag, sha
        if ancestry.returncode != 1:
            raise RuntimeError(f"Cannot inspect published Release ancestry: {tag}")
    if candidates:
        raise RuntimeError("None of the published release tags is an ancestor of HEAD.")
    return None


def release_baseline(before, after, repository, token):
    """If no releases exist, preserve the original per-push behavior."""
    checkpoint = published_release_anchor(after, fetch_releases(repository, token))
    if checkpoint:
        tag, sha = checkpoint
        return sha, tag
    return before, ""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--before")
    parser.add_argument("--after")
    parser.add_argument("--github-output")
    parser.add_argument("--changed", nargs="*")
    parser.add_argument("--recover-unpublished", action="store_true")
    args = parser.parse_args()
    rules = read_rules(args.config)
    before, baseline_tag = args.before, ""
    if args.recover_unpublished and args.changed is None:
        before, baseline_tag = release_baseline(
            args.before, args.after, os.environ.get("GITHUB_REPOSITORY", ""),
            os.environ.get("GITHUB_TOKEN", ""),
        )
    files = args.changed if args.changed is not None else git_paths(before, args.after)
    eligible, matched = evaluate(files, rules)
    value = "true" if eligible else "false"
    print(f"Baseline: {baseline_tag or 'push range'} ({before or 'initial tree'})")
    print(f"Release eligible: {value} ({len(matched)} matching paths)")
    for path in matched:
        print("  " + path)
    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as output:
            output.write(f"release={value}\nmatched_count={len(matched)}\n")
            output.write(f"baseline_sha={before or ''}\nbaseline_tag={baseline_tag}\n")


if __name__ == "__main__":
    main()
