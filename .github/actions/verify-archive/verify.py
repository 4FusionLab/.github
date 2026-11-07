"""Validate versioned ZIP packages, content safety, Fusion manifests and SHA-256."""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path


def verify(product, version, archives, manifest="", notes=""):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", product):
        raise ValueError("Invalid product identifier")
    if not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", version):
        raise ValueError("Expected numeric GitVersion MAJOR.MINOR.PATCH")
    if notes and (not Path(notes).is_file() or not Path(notes).read_text(encoding="utf-8").strip()):
        raise ValueError("Release notes missing or empty")
    if not archives:
        raise ValueError("At least one release ZIP is required")
    for filename in archives:
        archive = Path(filename)
        if archive.suffix.lower() != ".zip" or not archive.is_file():
            raise ValueError(f"Missing ZIP: {archive}")
        if archive.name != f"{product}-{version}.zip" and not archive.name.startswith(
            f"{product}-{version}-"
        ):
            raise ValueError(f"ZIP version/name mismatch: {archive.name}")
        checksum = archive.with_suffix(".zip.sha256")
        if not checksum.is_file():
            raise ValueError(f"Missing SHA-256: {checksum}")
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        expected = f"{digest}  {archive.name}"
        if checksum.read_text(encoding="ascii").strip() != expected:
            raise ValueError(f"Incorrect ZIP checksum: {checksum}")
        with zipfile.ZipFile(archive) as bundle:
            for member in bundle.infolist():
                name = member.filename
                p = Path(name)
                if not name or name.startswith("/") or "\\" in name or ".." in p.parts:
                    raise ValueError(f"Unsafe ZIP entry: {name}")
                if (member.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError(f"Symlink in release ZIP: {name}")
            if manifest:
                metadata = json.loads(bundle.read(manifest))
                if metadata.get("version") != version or metadata.get("type") != "addin":
                    raise ValueError(f"Fusion manifest version/type mismatch: {archive}")
            if bundle.testzip() is not None:
                raise ValueError(f"Corrupt ZIP: {archive}")
    return len(archives)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--archives", required=True)
    parser.add_argument("--manifest", default="")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()
    archives = [line.strip() for line in args.archives.splitlines() if line.strip()]
    verified = verify(args.product, args.version, archives, args.manifest, args.notes)
    print(f"Verified {verified} immutable ZIP candidates for {args.product} {args.version}")


if __name__ == "__main__":
    main()
