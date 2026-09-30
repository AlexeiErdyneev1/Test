#!/usr/bin/env python3
"""Create the installable Dark Citadel resource-pack archive.

The ZIP deliberately contains only Terraria's package root files, rather than
repository documentation or tooling. It is deterministic except for the ZIP
member timestamps supplied by Python's zip implementation.
"""
from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "Dark_Citadel_Phase_1.zip"


def main() -> None:
    files = [ROOT / "pack.json", ROOT / "icon.png"]
    files.extend(sorted((ROOT / "Content").rglob("*.png")))
    missing = [path for path in files if not path.is_file()]
    if missing:
        raise SystemExit("Missing package file(s): " + ", ".join(str(path) for path in missing))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT).as_posix())
    print(f"Created {OUT.relative_to(ROOT)} with {len(files)} files.")


if __name__ == "__main__":
    main()
