#!/usr/bin/env python3
"""Validate Dark Citadel resource-pack assets without third-party packages.

Usage:
    python3 tools/validate_pack.py
    python3 tools/validate_pack.py --vanilla /path/to/extracted/Terraria/Content/Images

The optional second form compares every implemented override against PNGs
extracted from the player's exact game build. This is the final gate before a
release: it catches an upstream Terraria dimension change immediately.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def read_png_header(path: Path) -> tuple[int, int, int, int]:
    data = path.read_bytes()
    if data[:8] != PNG_SIGNATURE or data[12:16] != b"IHDR":
        raise ValueError("not a valid PNG with IHDR")
    width, height, depth, color_type, compression, filter_method, interlace = struct.unpack(">IIBBBBB", data[16:29])
    if compression != 0 or filter_method != 0:
        raise ValueError("unsupported PNG encoding")
    return width, height, depth, color_type


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Dark Citadel texture constraints")
    parser.add_argument("--vanilla", type=Path, help="extracted vanilla Content/Images directory")
    args = parser.parse_args()

    manifest_path = ROOT / "docs" / "ASSET_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures: list[str] = []
    checked = 0

    for asset in manifest["assets"]:
        relative = Path(asset["path"])
        path = ROOT / relative
        expected = tuple(asset["size"])
        if not path.is_file():
            failures.append(f"MISSING  {relative}")
            continue
        try:
            width, height, depth, color_type = read_png_header(path)
        except (OSError, ValueError) as exc:
            failures.append(f"INVALID  {relative}: {exc}")
            continue
        checked += 1
        if (width, height) != expected:
            failures.append(f"SIZE     {relative}: got {width}x{height}, expected {expected[0]}x{expected[1]}")
        if (depth, color_type) != (8, 6):
            failures.append(f"FORMAT   {relative}: requires 8-bit RGBA PNG, got depth={depth}, color_type={color_type}")

        if "frame" in asset:
            frame_w, frame_h = asset["frame"]
            grid_w, grid_h = asset["grid"]
            stride_w, stride_h = asset.get("stride", [frame_w, frame_h])
            required_w = stride_w * grid_w
            required_h = stride_h * grid_h
            if (width, height) != (required_w, required_h):
                failures.append(
                    f"GRID     {relative}: {grid_w}x{grid_h} at stride {stride_w}x{stride_h} needs {required_w}x{required_h}"
                )

        if args.vanilla:
            # The argument is deliberately the Images directory, not the game root.
            source = args.vanilla / relative.relative_to("Content/Images")
            if not source.is_file():
                failures.append(f"VANILLA  missing source texture: {source}")
            else:
                try:
                    source_w, source_h, _, _ = read_png_header(source)
                    if (source_w, source_h) != (width, height):
                        failures.append(
                            f"VANILLA  {relative}: pack {width}x{height} != source {source_w}x{source_h}"
                        )
                except (OSError, ValueError) as exc:
                    failures.append(f"VANILLA  {source}: {exc}")

    # pack.json needs to be valid and at package root.
    try:
        pack = json.loads((ROOT / "pack.json").read_text(encoding="utf-8"))
        for required in ("Name", "Author", "Description", "Version"):
            if required not in pack:
                failures.append(f"PACK     pack.json is missing {required}")
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"PACK     invalid pack.json: {exc}")

    if failures:
        print("VALIDATION FAILED")
        print("\n".join(failures))
        return 1
    source_note = " against extracted vanilla source" if args.vanilla else " against the locked manifest"
    print(f"VALIDATION OK: {checked} RGBA assets checked{source_note}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
