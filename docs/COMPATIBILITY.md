# Compatibility contract

## Target

`Dark Citadel 0.1.0` targets **Terraria Desktop 1.4.5.x**. Resource packs are data replacements: game version matters even when a file name has not changed.

The 25 Phase-1 overrides are intentionally limited to long-lived vanilla assets. Their canvases and frame grids are locked in `ASSET_MANIFEST.json`; the shipped art was generated at those exact dimensions. The pack never redistributes Re-Logic `.xnb` assets or source PNGs.

## Required release test

Before publishing an update—or using the pack after a Terraria update—extract the installed game's `Content/Images/*.xnb` assets to PNG in a local, ignored directory. Then run:

```bash
python3 tools/validate_pack.py --vanilla /absolute/path/to/extracted/Content/Images
```

The release is valid only when the command reports `VALIDATION OK`. It verifies every implemented override against the user's own source asset by **relative path and exact canvas** in addition to checking 8-bit RGBA and declared sprite grids.

## What the check does and does not prove

| Check | Automated | In-game review still required |
|---|:---:|:---:|
| File path, PNG parse, 8-bit RGBA, alpha channel | ✓ | — |
| Exact canvas against the current local vanilla file | ✓ | — |
| Tile sheet stride and declared frame count | ✓ | — |
| No apparent terrain seam | — | ✓: 3×3 mix + biome edge |
| NPC animation / no frame jitter | — | ✓: observe full loop |
| Collider and attack telegraph readability | — | ✓ |
| HUD legibility at all UI scales | — | ✓ |

Do not use a 1.4.4 source export as a proof for a 1.4.5 release. Conversely, a 1.4.5 validation does not certify a tModLoader build pinned to 1.4.4.9: validate it separately.

## Resource-pack folder contract

The install ZIP contains exactly these root-level members:

```text
pack.json
icon.png
Content/Images/...
```

There is no extra `Dark_Citadel/` wrapper folder. PNG file names retain capitalization—including `HP Template.png`—because asset matching is path-sensitive.
