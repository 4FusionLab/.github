#!/usr/bin/env python3
"""Preview or apply search metadata for 4FusionLab repositories.

Requires GitHub CLI (gh) authenticated with repository administration access.
Dry run: python3 scripts/sync-repository-metadata.py
Apply:   python3 scripts/sync-repository-metadata.py --apply
"""
import argparse
import json
import shutil
import subprocess
import sys

OWNER = "4FusionLab"

# Search-friendly descriptions, written for humans rather than keyword stuffing.
REPOSITORIES = {
    "Perfora": {
        "description": "Fusion 360 add-in for parametric hole patterns, perforated panels, honeycomb and Voronoi designs, and ventilation grilles.",
        "topics": [
            "autodesk-fusion", "fusion-360", "fusion360-addin", "cad",
            "3d-printing", "perforation", "hole-patterns", "parametric-design",
            "honeycomb", "voronoi", "ventilation-grille", "python",
        ],
    },
    "Selectra": {
        "description": "Fusion 360 add-in to select similar BRep faces and edges and trace closed contours across bodies, components, and assemblies.",
        "topics": [
            "autodesk-fusion", "fusion-360", "fusion360", "fusion360-addin",
            "cad", "python", "selection", "brep", "select-similar",
            "face-selection", "edge-selection",
        ],
    },
    "Ejix": {
        "description": "Fusion 360 add-in to extract solid volumes from sketch profiles or planar faces into separate bodies or components with optional subtraction.",
        "topics": [
            "autodesk-fusion", "fusion-360", "fusion360-addin", "fusion-addin",
            "cad", "python", "solid-modeling", "volume-extraction",
            "body-extraction", "sketch-profiles",
        ],
    },
    "RuEn": {
        "description": "Fusion 360 keyboard shortcut add-in for Russian layout on macOS and Windows. Use assigned Fusion hotkeys without switching to English.",
        "topics": [
            "autodesk-fusion", "fusion-360", "fusion360", "fusion360-addin",
            "keyboard-shortcuts", "russian-keyboard", "macos", "windows",
            "python", "qt",
        ],
    },
    "Planara": {
        "description": "Planned Fusion 360 surface-flattening add-in to unfold solid-body faces into 2D layouts. Early development; not available for download.",
        "topics": [
            "autodesk-fusion", "fusion-360", "fusion360-addin", "cad",
            "surface-flattening", "surface-unfolding", "unfolding", "3d-to-2d",
        ],
    },
    ".github": {
        "description": "4FusionLab organization profile and project directory for open-source Autodesk Fusion 360 CAD add-ins.",
        "topics": ["organization-profile", "autodesk-fusion", "fusion-360", "cad"],
    },
}


def gh_api(method, endpoint, payload=None):
    command = ["gh", "api", "--method", method, endpoint]
    if payload is not None:
        command += ["--input", "-"]
    result = subprocess.run(
        command,
        input=json.dumps(payload) if payload is not None else None,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        message = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"GitHub API {method} {endpoint}: {message}")
    return json.loads(result.stdout) if result.stdout.strip() else {}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Write descriptions and topics to GitHub")
    parser.add_argument("--repo", choices=list(REPOSITORIES), help="Process only one repository")
    args = parser.parse_args()

    if shutil.which("gh") is None:
        parser.error("GitHub CLI (gh) is required; install it and run 'gh auth login'.")

    names = [args.repo] if args.repo else REPOSITORIES
    for name in names:
        metadata = REPOSITORIES[name]
        endpoint = f"repos/{OWNER}/{name}"
        current = gh_api("GET", endpoint)
        current_topics = gh_api("GET", endpoint + "/topics").get("names", [])
        # Preserve custom topics already configured by repository maintainers.
        topics = list(dict.fromkeys(current_topics + metadata["topics"]))
        if len(topics) > 20:
            raise RuntimeError(f"{name}: {len(topics)} topics, GitHub allows at most 20.")

        update_description = current.get("description") != metadata["description"]
        update_topics = set(current_topics) != set(topics)
        print(f"\n{OWNER}/{name}")
        print(f"  Description: {'CHANGE' if update_description else 'unchanged'}")
        if update_description:
            print(f"    {metadata['description']}")
        added_topics = [topic for topic in topics if topic not in current_topics]
        print(f"  Topics: {'add ' + ', '.join(added_topics) if added_topics else 'unchanged'}")

        if args.apply:
            if update_description:
                gh_api("PATCH", endpoint, {"description": metadata["description"]})
            if update_topics:
                gh_api("PUT", endpoint + "/topics", {"names": topics})
            print("  Applied.")

    if not args.apply:
        print("\nDry run only. Re-run with --apply to update GitHub settings.")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
