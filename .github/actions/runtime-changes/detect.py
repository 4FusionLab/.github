"""Determine release eligibility from Git changes and a repository-specific allowlist."""
import argparse
import fnmatch
import subprocess
from pathlib import Path


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--before")
    parser.add_argument("--after")
    parser.add_argument("--github-output")
    parser.add_argument("--changed", nargs="*")
    args = parser.parse_args()
    rules = read_rules(args.config)
    files = args.changed if args.changed is not None else git_paths(args.before, args.after)
    eligible, matched = evaluate(files, rules)
    value = "true" if eligible else "false"
    print(f"Release eligible: {value} ({len(matched)} matching paths)")
    for path in matched:
        print("  " + path)
    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as output:
            output.write(f"release={value}\nmatched_count={len(matched)}\n")


if __name__ == "__main__":
    main()
