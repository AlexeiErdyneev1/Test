#!/usr/bin/env python3
"""Build the original Phase 1 pixel-art assets for Dark Citadel.

The script uses only the Python standard library. It writes 8-bit RGBA PNG files,
so it is safe to run in a clean environment and never needs to extract or copy
Terraria assets.
"""
from __future__ import annotations

import binascii
import json
import math
import struct
import zlib
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]

# One deliberately constrained palette for the entire pack.
P = {
    "clear": (0, 0, 0, 0),
    "void": "#070B14",
    "ink": "#0D1422",
    "slate": "#1A293B",
    "steel": "#304862",
    "blue": "#35698A",
    "ice": "#81D6E8",
    "mist": "#C7F1E9",
    "gold_dark": "#6E4617",
    "gold": "#BF842B",
    "gold_light": "#F2D47A",
    "blood_dark": "#431529",
    "blood": "#972C43",
    "ember": "#E26B3D",
    "violet": "#6C4A99",
    "amethyst": "#B687D9",
    "earth": "#24313A",
    "earth_mid": "#3C5360",
    "earth_light": "#65808A",
    "obsidian": "#182131",
    "ore_dark": "#3A3024",
    "ore": "#B07932",
}


def rgba(value: str | tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    if isinstance(value, tuple):
        return value
    if value.startswith("#"):
        value = value[1:]
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (255,)


class Canvas:
    def __init__(self, width: int, height: int, color: str | tuple[int, int, int, int] = "clear"):
        self.width = width
        self.height = height
        self.data = bytearray(rgba(P[color] if color in P else color) * (width * height))

    def pixel(self, x: int, y: int, color: str | tuple[int, int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            offset = (y * self.width + x) * 4
            self.data[offset : offset + 4] = bytes(rgba(P[color] if color in P else color))

    def rect(self, x: int, y: int, width: int, height: int, color: str | tuple[int, int, int, int]) -> None:
        for yy in range(y, y + height):
            for xx in range(x, x + width):
                self.pixel(xx, yy, color)

    def line(self, x0: int, y0: int, x1: int, y1: int, color: str, width: int = 1) -> None:
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            for ox in range(-(width // 2), width - width // 2):
                for oy in range(-(width // 2), width - width // 2):
                    self.pixel(x0 + ox, y0 + oy, color)
            if x0 == x1 and y0 == y1:
                return
            twice = 2 * err
            if twice >= dy:
                err += dy
                x0 += sx
            if twice <= dx:
                err += dx
                y0 += sy

    def ellipse(self, cx: int, cy: int, rx: int, ry: int, color: str) -> None:
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                if ((x - cx) / max(1, rx)) ** 2 + ((y - cy) / max(1, ry)) ** 2 <= 1:
                    self.pixel(x, y, color)

    def outline_ellipse(self, cx: int, cy: int, rx: int, ry: int, outline: str, fill: str) -> None:
        self.ellipse(cx, cy, rx + 1, ry + 1, outline)
        self.ellipse(cx, cy, rx, ry, fill)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = b"".join(
            b"\x00" + bytes(self.data[y * self.width * 4 : (y + 1) * self.width * 4])
            for y in range(self.height)
        )

        def chunk(name: bytes, payload: bytes) -> bytes:
            return struct.pack(">I", len(payload)) + name + payload + struct.pack(">I", binascii.crc32(name + payload) & 0xFFFFFFFF)

        png = b"\x89PNG\r\n\x1a\n"
        png += chunk(b"IHDR", struct.pack(">IIBBBBB", self.width, self.height, 8, 6, 0, 0, 0))
        png += chunk(b"IDAT", zlib.compress(raw, 9))
        png += chunk(b"IEND", b"")
        path.write_bytes(png)


def bordered_line(c: Canvas, points: Iterable[tuple[int, int]], outer: str, inner: str, outer_width: int, inner_width: int) -> None:
    points = list(points)
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        c.line(x0, y0, x1, y1, outer, outer_width)
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        c.line(x0, y0, x1, y1, inner, inner_width)


def draw_pickaxe() -> Canvas:
    c = Canvas(32, 32)
    # Ash-wood handle with metal bindings.
    bordered_line(c, [(6, 28), (22, 11)], "void", "gold_dark", 4, 2)
    c.line(7, 27, 21, 12, "gold", 1)
    c.rect(8, 24, 2, 2, "gold_light")
    # Cold, serrated crescent head.
    bordered_line(c, [(16, 8), (20, 5), (25, 5), (28, 8), (27, 10), (23, 8), (19, 11)], "void", "steel", 4, 2)
    c.rect(23, 5, 2, 1, "ice")
    c.pixel(27, 9, "ice")
    c.rect(17, 8, 3, 2, "blue")
    c.pixel(18, 7, "ice")
    return c


def draw_broadsword() -> Canvas:
    c = Canvas(36, 36)
    # Broad, blackened blade: a deliberate two-tone silhouette.
    bordered_line(c, [(7, 30), (28, 8)], "void", "steel", 6, 4)
    bordered_line(c, [(11, 27), (28, 8)], "blue", "ice", 2, 1)
    c.line(28, 8, 30, 5, "void", 4)
    c.pixel(30, 4, "ice")
    # Guard, gem and leather grip.
    bordered_line(c, [(5, 24), (13, 32)], "void", "gold", 4, 2)
    c.rect(7, 25, 4, 2, "gold_light")
    c.outline_ellipse(10, 27, 2, 2, "void", "blood")
    bordered_line(c, [(7, 29), (3, 33)], "void", "gold_dark", 4, 2)
    c.pixel(3, 34, "gold_light")
    return c


def draw_shortsword() -> Canvas:
    c = Canvas(32, 32)
    bordered_line(c, [(8, 25), (23, 10)], "void", "steel", 5, 3)
    c.line(11, 22, 23, 10, "ice", 1)
    c.line(23, 10, 25, 8, "void", 3)
    c.pixel(25, 7, "ice")
    bordered_line(c, [(4, 23), (11, 29)], "void", "gold", 4, 2)
    c.rect(5, 24, 3, 1, "gold_light")
    bordered_line(c, [(6, 27), (3, 30)], "void", "gold_dark", 4, 2)
    return c


def draw_hammer() -> Canvas:
    c = Canvas(38, 38)
    bordered_line(c, [(10, 34), (23, 16)], "void", "gold_dark", 5, 3)
    c.line(11, 32, 21, 17, "gold", 1)
    # A heavy rectangular maul with a violet rune.
    c.rect(17, 7, 15, 11, "void")
    c.rect(19, 8, 12, 9, "slate")
    c.rect(20, 9, 9, 2, "steel")
    c.rect(20, 15, 10, 1, "blue")
    c.rect(17, 10, 2, 5, "gold_dark")
    c.rect(30, 10, 2, 5, "gold_dark")
    c.rect(24, 11, 2, 3, "violet")
    c.pixel(25, 12, "amethyst")
    c.rect(7, 31, 5, 3, "void")
    c.rect(8, 31, 3, 2, "gold")
    return c


def draw_axe() -> Canvas:
    c = Canvas(34, 30)
    bordered_line(c, [(8, 27), (20, 9)], "void", "gold_dark", 5, 3)
    c.line(9, 25, 19, 10, "gold", 1)
    # Wide bearded axe, kept well inside the original canvas.
    c.rect(17, 5, 11, 11, "void")
    c.rect(18, 6, 9, 9, "steel")
    c.rect(19, 7, 7, 2, "blue")
    c.rect(23, 13, 5, 2, "steel")
    c.pixel(27, 12, "ice")
    c.rect(15, 9, 4, 4, "gold_dark")
    c.rect(16, 10, 2, 2, "gold")
    c.rect(6, 25, 4, 3, "void")
    c.rect(7, 25, 2, 2, "gold")
    return c


def bounded_noise(seed: int, x: int, y: int) -> int:
    # Deterministic and independent of Python's hash randomisation.
    return ((seed * 92821 + x * 193 + y * 389 + x * y * 17) ^ (x * 7919)) & 0xFF


def draw_terrain_frame(c: Canvas, ox: int, oy: int, material: str, frame: int) -> None:
    # Each source frame is 16x16. The two-pixel gutters are intentionally left
    # transparent as in Terraria's 18px frame grid.
    if material == "dirt":
        base, mid, light, fleck = "earth", "earth_mid", "earth_light", "gold_dark"
    elif material == "stone":
        base, mid, light, fleck = "obsidian", "slate", "steel", "blue"
    else:
        base, mid, light, fleck = "obsidian", "slate", "steel", "ore"
    c.rect(ox, oy, 16, 16, base)
    # Seam safety: every edge is the shared base colour. All detail stays inward.
    for y in range(2, 14):
        for x in range(2, 14):
            n = bounded_noise(frame + (7 if material == "ore" else 0), x, y)
            if n < 28:
                c.pixel(ox + x, oy + y, mid)
            elif n == 31:
                c.pixel(ox + x, oy + y, light)
    # Irregular dark cracks. Their ends never touch the frame edge.
    if frame % 3 == 0:
        c.line(ox + 4, oy + 4, ox + 7, oy + 8, "ink")
        c.line(ox + 7, oy + 8, ox + 6, oy + 12, "ink")
    elif frame % 3 == 1:
        c.line(ox + 11, oy + 3, ox + 9, oy + 7, "ink")
        c.line(ox + 9, oy + 7, ox + 12, oy + 10, "ink")
    else:
        c.line(ox + 3, oy + 10, ox + 7, oy + 9, "ink")
    if material == "ore":
        # Mineral clusters use the same coordinates in every frame type, but are
        # shifted through the animation sheet by frame number for variation.
        px = 3 + (frame * 5) % 9
        py = 3 + (frame * 3) % 9
        c.rect(ox + px, oy + py, 2, 2, "ore_dark")
        c.pixel(ox + px + 1, oy + py, fleck)
        c.pixel(ox + px, oy + py + 1, "gold")
        if frame % 2 == 0:
            c.pixel(ox + max(2, px - 2), oy + min(13, py + 3), "gold_light")


def draw_tiles(material: str) -> Canvas:
    c = Canvas(288, 270)
    for row in range(15):
        for column in range(16):
            frame = row * 16 + column
            draw_terrain_frame(c, column * 18, row * 18, material, frame)
    return c


def draw_slime_frame(c: Canvas, top: int, squashed: bool) -> None:
    # The 32x52 NPC_1 sheet has two 32x26 animation frames.
    body_top = top + (5 if squashed else 3)
    body_ry = 8 if squashed else 10
    c.outline_ellipse(16, body_top + body_ry, 12, body_ry, "void", "slate")
    c.ellipse(16, body_top + body_ry - 2, 10, max(3, body_ry - 3), "steel")
    c.ellipse(14, body_top + body_ry - 4, 6, 3, "blue")
    c.rect(10, body_top + body_ry - 4, 2, 2, "ice")
    c.pixel(11, body_top + body_ry - 5, "mist")
    # Narrow, hostile eyes rather than the vanilla cheerful look.
    eye_y = body_top + body_ry
    c.rect(10, eye_y, 3, 2, "void")
    c.rect(20, eye_y, 3, 2, "void")
    c.pixel(11, eye_y, "gold_light")
    c.pixel(21, eye_y, "gold_light")
    c.pixel(12, eye_y + 1, "blood")
    c.pixel(20, eye_y + 1, "blood")
    c.line(12, eye_y + 5, 19, eye_y + 5, "ink")
    c.pixel(15, eye_y + 5, "blood")
    c.pixel(16, eye_y + 5, "blood")
    # Ground glow, still within its own frame.
    c.line(8, top + 24, 23, top + 24, "blue")
    c.line(12, top + 25, 19, top + 25, "ice")


def draw_slime() -> Canvas:
    c = Canvas(32, 52)
    draw_slime_frame(c, 0, False)
    draw_slime_frame(c, 26, True)
    return c


def draw_heart(width: int, height: int, golden: bool = False) -> Canvas:
    c = Canvas(width, height)
    cx, cy = width // 2, max(7, height // 2 - 1)
    outer = "gold_dark" if golden else "void"
    fill = "gold" if golden else "blood_dark"
    bright = "gold_light" if golden else "blood"
    c.outline_ellipse(cx - 5, cy - 2, 5, 5, outer, fill)
    c.outline_ellipse(cx + 5, cy - 2, 5, 5, outer, fill)
    # Diamond lower half.
    for row, half in enumerate((9, 8, 7, 6, 5, 4, 3, 2, 1)):
        c.rect(cx - half, cy + row, half * 2 + 1, 1, fill)
    c.line(cx - 7, cy - 4, cx - 2, cy - 5, bright)
    c.rect(cx - 4, cy - 2, 2, 2, "gold_light" if golden else "ember")
    c.pixel(cx + 5, cy + 2, "ink")
    c.pixel(cx + 6, cy + 3, "ink")
    return c


def draw_star(width: int, height: int, variant: int) -> Canvas:
    c = Canvas(width, height)
    cx, cy = width // 2, height // 2
    outer, fill = "void", "blue"
    # Crystal star: pixel-aligned and intentionally non-antialiased.
    rows = [(-7, 1), (-6, 3), (-5, 4), (-4, 5), (-3, 8), (-2, 10), (-1, 8), (0, 7), (1, 8), (2, 10), (3, 8), (4, 5), (5, 4), (6, 3), (7, 1)]
    for dy, half in rows:
        c.rect(cx - half - 1, cy + dy, half * 2 + 3, 1, outer)
        c.rect(cx - half, cy + dy, half * 2 + 1, 1, fill)
    c.line(cx - 2, cy - 4, cx + 2, cy + 3, "ice")
    c.pixel(cx - 1 + variant % 3, cy - 5, "mist")
    c.pixel(cx + 4, cy + 3, "violet")
    return c


def draw_bar_piece(width: int, height: int, type_: str) -> Canvas:
    c = Canvas(width, height)
    if type_ == "fill_hp":
        c.rect(0, 0, width, height, "void")
        c.rect(1, 2, width - 2, height - 4, "blood_dark")
        c.rect(2, 3, width - 4, max(1, height - 7), "blood")
        c.rect(3, 3, width - 6, 1, "ember")
    elif type_ == "fill_honey":
        c.rect(0, 0, width, height, "void")
        c.rect(1, 2, width - 2, height - 4, "gold_dark")
        c.rect(2, 3, width - 4, max(1, height - 7), "gold")
        c.rect(3, 3, width - 6, 1, "gold_light")
    elif type_ == "fill_mp":
        c.rect(0, 0, width, height, "void")
        c.rect(1, 2, width - 2, height - 4, "ink")
        c.rect(2, 3, width - 4, max(1, height - 7), "blue")
        c.rect(3, 3, width - 6, 1, "ice")
    elif type_ == "middle":
        c.rect(0, 0, width, height, "void")
        c.rect(0, 1, width, height - 2, "slate")
        c.rect(1, 3, width - 2, height - 6, "ink")
        c.line(0, 1, width - 1, 1, "gold_dark")
        c.line(0, height - 2, width - 1, height - 2, "gold_dark")
    elif type_ == "left":
        c.rect(0, 0, width, height, "void")
        c.rect(0, 2, width, height - 4, "slate")
        c.line(0, 1, width - 1, 1, "gold_dark")
        c.line(0, height - 2, width - 1, height - 2, "gold_dark")
    else:  # right cap / template ornament
        c.rect(0, 0, width, height, "void")
        c.rect(0, 3, width - 4, height - 6, "slate")
        c.rect(2, 5, width - 8, height - 10, "ink")
        c.line(0, 2, width - 6, 2, "gold_dark")
        c.line(0, height - 3, width - 6, height - 3, "gold_dark")
        c.outline_ellipse(width - 10, height // 2, 6, 6, "gold_dark", "void")
        c.outline_ellipse(width - 10, height // 2, 3, 3, "void", "blue")
        c.pixel(width - 11, height // 2 - 1, "ice")
    return c


def draw_hp_template() -> Canvas:
    c = Canvas(56, 68)
    c.rect(2, 3, 52, 62, "void")
    c.rect(4, 5, 48, 58, "slate")
    c.rect(6, 7, 44, 54, "ink")
    # A dark, ornate panel marker used behind the health-bar system.
    for x in (5, 49):
        c.rect(x, 12, 2, 42, "gold_dark")
        c.pixel(x + 1, 13, "gold")
    c.outline_ellipse(28, 34, 13, 13, "gold_dark", "void")
    c.outline_ellipse(28, 34, 9, 9, "void", "blood_dark")
    c.outline_ellipse(28, 34, 5, 5, "blood_dark", "blood")
    c.pixel(25, 30, "ember")
    return c


def draw_icon() -> Canvas:
    c = Canvas(256, 256, "void")
    c.rect(8, 8, 240, 240, "gold_dark")
    c.rect(14, 14, 228, 228, "ink")
    c.rect(20, 20, 216, 216, "slate")
    c.rect(28, 28, 200, 200, "void")
    # Moon, spires and a central blue flame form a legible 256px pack badge.
    c.ellipse(128, 99, 59, 59, "steel")
    c.ellipse(116, 89, 55, 55, "void")
    c.ellipse(132, 102, 44, 44, "blue")
    c.ellipse(124, 92, 38, 38, "ice")
    c.rect(43, 160, 170, 42, "ink")
    for x, h in ((55, 44), (76, 68), (99, 52), (128, 86), (153, 57), (179, 73), (198, 45)):
        c.rect(x, 202 - h, 13, h, "void")
        c.line(x, 202 - h, x + 6, 190 - h, "gold_dark")
        c.line(x + 12, 202 - h, x + 6, 190 - h, "gold_dark")
        c.rect(x + 4, 199 - h, 5, 6, "blue")
    c.outline_ellipse(128, 176, 22, 28, "gold_dark", "void")
    c.ellipse(128, 178, 13, 21, "violet")
    c.ellipse(128, 181, 8, 15, "blue")
    c.ellipse(128, 185, 4, 9, "ice")
    c.rect(31, 31, 8, 8, "gold_light")
    c.rect(217, 31, 8, 8, "gold_light")
    c.rect(31, 217, 8, 8, "gold_light")
    c.rect(217, 217, 8, 8, "gold_light")
    return c


def write_manifest() -> None:
    # Source-of-truth for the dimensions and animation grids used in this milestone.
    manifest = {
        "target": "Terraria Desktop 1.4.5.x resource-pack layout (verify against the exact installed build before release)",
        "assets": [
            {"path": "Content/Images/Item_1.png", "name": "Iron Pickaxe", "size": [32, 32], "grid": [1, 1], "stage": 1},
            {"path": "Content/Images/Item_4.png", "name": "Iron Broadsword", "size": [36, 36], "grid": [1, 1], "stage": 1},
            {"path": "Content/Images/Item_6.png", "name": "Iron Shortsword", "size": [32, 32], "grid": [1, 1], "stage": 1},
            {"path": "Content/Images/Item_7.png", "name": "Iron Hammer", "size": [38, 38], "grid": [1, 1], "stage": 1},
            {"path": "Content/Images/Item_10.png", "name": "Iron Axe", "size": [34, 30], "grid": [1, 1], "stage": 1},
            {"path": "Content/Images/Tiles_0.png", "name": "Dirt Block", "size": [288, 270], "grid": [16, 15], "frame": [16, 16], "stride": [18, 18], "stage": 1},
            {"path": "Content/Images/Tiles_1.png", "name": "Stone Block", "size": [288, 270], "grid": [16, 15], "frame": [16, 16], "stride": [18, 18], "stage": 1},
            {"path": "Content/Images/Tiles_6.png", "name": "Iron Ore", "size": [288, 270], "grid": [16, 15], "frame": [16, 16], "stride": [18, 18], "stage": 1},
            {"path": "Content/Images/NPC_1.png", "name": "Blue Slime / Abyssal Slime", "size": [32, 52], "grid": [1, 2], "frame": [32, 26], "stage": 1},
            {"path": "Content/Images/UI/PlayerResourceSets/HorizontalBars/HP Template.png", "name": "Horizontal HP template", "size": [56, 68], "grid": [1, 1], "stage": 1},
            {"path": "Content/Images/UI/PlayerResourceSets/HorizontalBars/HP_Fill.png", "name": "Horizontal HP fill", "size": [12, 12], "grid": [1, 1], "stage": 1},
            {"path": "Content/Images/UI/PlayerResourceSets/HorizontalBars/HP_Fill_Honey.png", "name": "Honey HP fill", "size": [12, 12], "grid": [1, 1], "stage": 1},
            {"path": "Content/Images/UI/PlayerResourceSets/HorizontalBars/HP_Panel_Middle.png", "name": "HP panel middle", "size": [12, 24], "grid": [1, 1], "stage": 1},
            {"path": "Content/Images/UI/PlayerResourceSets/HorizontalBars/HP_Panel_Right.png", "name": "HP panel right", "size": [46, 38], "grid": [1, 1], "stage": 1},
            {"path": "Content/Images/UI/PlayerResourceSets/HorizontalBars/MP_Fill.png", "name": "MP fill", "size": [12, 12], "grid": [1, 1], "stage": 1},
            {"path": "Content/Images/UI/PlayerResourceSets/HorizontalBars/MP_Panel_Middle.png", "name": "MP panel middle", "size": [12, 24], "grid": [1, 1], "stage": 1},
            {"path": "Content/Images/UI/PlayerResourceSets/HorizontalBars/MP_Panel_Right.png", "name": "MP panel right", "size": [46, 40], "grid": [1, 1], "stage": 1},
            {"path": "Content/Images/UI/PlayerResourceSets/HorizontalBars/Panel_Left.png", "name": "Horizontal panel left", "size": [6, 24], "grid": [1, 1], "stage": 1},
            {"path": "Content/Images/UI/PlayerResourceSets/FancyClassic/Heart_Fill.png", "name": "Life heart", "size": [22, 22], "grid": [1, 1], "stage": 1},
            {"path": "Content/Images/UI/PlayerResourceSets/FancyClassic/Heart_Fill_B.png", "name": "Golden life heart", "size": [22, 22], "grid": [1, 1], "stage": 1},
            {"path": "Content/Images/UI/PlayerResourceSets/FancyClassic/Star_A.png", "name": "Mana star A", "size": [30, 26], "grid": [1, 1], "stage": 1},
            {"path": "Content/Images/UI/PlayerResourceSets/FancyClassic/Star_B.png", "name": "Mana star B", "size": [30, 22], "grid": [1, 1], "stage": 1},
            {"path": "Content/Images/UI/PlayerResourceSets/FancyClassic/Star_C.png", "name": "Mana star C", "size": [30, 28], "grid": [1, 1], "stage": 1},
            {"path": "Content/Images/UI/PlayerResourceSets/FancyClassic/Star_Fill.png", "name": "Mana star fill", "size": [22, 24], "grid": [1, 1], "stage": 1},
            {"path": "Content/Images/UI/PlayerResourceSets/FancyClassic/Star_Single.png", "name": "Single mana star", "size": [30, 32], "grid": [1, 1], "stage": 1},
        ],
    }
    path = ROOT / "docs" / "ASSET_MANIFEST.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    images = ROOT / "Content" / "Images"
    draw_pickaxe().save(images / "Item_1.png")
    draw_broadsword().save(images / "Item_4.png")
    draw_shortsword().save(images / "Item_6.png")
    draw_hammer().save(images / "Item_7.png")
    draw_axe().save(images / "Item_10.png")
    draw_tiles("dirt").save(images / "Tiles_0.png")
    draw_tiles("stone").save(images / "Tiles_1.png")
    draw_tiles("ore").save(images / "Tiles_6.png")
    draw_slime().save(images / "NPC_1.png")

    horizontal = images / "UI" / "PlayerResourceSets" / "HorizontalBars"
    draw_hp_template().save(horizontal / "HP Template.png")
    draw_bar_piece(12, 12, "fill_hp").save(horizontal / "HP_Fill.png")
    draw_bar_piece(12, 12, "fill_honey").save(horizontal / "HP_Fill_Honey.png")
    draw_bar_piece(12, 24, "middle").save(horizontal / "HP_Panel_Middle.png")
    draw_bar_piece(46, 38, "right").save(horizontal / "HP_Panel_Right.png")
    draw_bar_piece(12, 12, "fill_mp").save(horizontal / "MP_Fill.png")
    draw_bar_piece(12, 24, "middle").save(horizontal / "MP_Panel_Middle.png")
    draw_bar_piece(46, 40, "right").save(horizontal / "MP_Panel_Right.png")
    draw_bar_piece(6, 24, "left").save(horizontal / "Panel_Left.png")

    fancy = images / "UI" / "PlayerResourceSets" / "FancyClassic"
    draw_heart(22, 22).save(fancy / "Heart_Fill.png")
    draw_heart(22, 22, golden=True).save(fancy / "Heart_Fill_B.png")
    for name, width, height, variant in (
        ("Star_A.png", 30, 26, 0),
        ("Star_B.png", 30, 22, 1),
        ("Star_C.png", 30, 28, 2),
        ("Star_Fill.png", 22, 24, 3),
        ("Star_Single.png", 30, 32, 4),
    ):
        draw_star(width, height, variant).save(fancy / name)

    draw_icon().save(ROOT / "icon.png")
    write_manifest()
    print("Dark Citadel assets built.")


if __name__ == "__main__":
    main()
