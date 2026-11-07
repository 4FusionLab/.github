"""Select reviewed notes or generate fallback release notes from Git history."""
import argparse
import re
import subprocess
from pathlib import Path


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False)


def create_notes(product, version, candidate, output):
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Fusion release version must be MAJOR.MINOR.PATCH")
    output = Path(output)
    if candidate:
        reviewed = Path(candidate)
        if reviewed.is_file() and reviewed.read_text(encoding="utf-8").strip():
            output.write_text(reviewed.read_text(encoding="utf-8"), encoding="utf-8")
            return "reviewed"
    previous = git("describe", "--tags", "--abbrev=0", "--match", "v[0-9]*", "HEAD")
    tag = previous.stdout.strip() if previous.returncode == 0 else None
    rev = f"{tag}..HEAD" if tag else "HEAD"
    logs = subprocess.run(["git", "log", "--max-count=100", "--format=- %s (%h)", rev],
                          check=True, capture_output=True, text=True).stdout.strip()
    if not logs:
        raise ValueError("No commits since previous release; cannot generate notes.")
    previous_label = f"Changes since {tag}" if tag else "Initial release changes"
    output.write_text(f"# {product} v{version}\n\n{previous_label}:\n\n{logs}\n",
                      encoding="utf-8")
    return "generated"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--candidate", default="")
    args = parser.parse_args()
    method = create_notes(args.product, args.version, args.candidate, args.output)
    print(f"Prepared {method} notes: {args.output}")


if __name__ == "__main__":
    main()
