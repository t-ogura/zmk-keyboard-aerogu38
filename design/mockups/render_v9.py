#!/usr/bin/env python3
"""v9 - implement the 10 user-provided theme concepts.

Naming follows the source proposal:
  01 watch_minimal    - Apple Watch Ultra-ish
  02 active_circle    - ring gauges for layer + L/R battery
  03 info_timeline    - vertical timeline with dots
  04 braun_industrial - diagonal stripe borders + bars
  05 sf_radar         - radar screen at top
  06 gameboy_dot      - pixel cat + heart batteries
  07 submarine_dash   - submarine + wave batteries
  08 module_block     - bordered module stack
  09 orbit_gauge      - planet + orbital arcs
  10 essential_line   - thin lines + massive whitespace
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

from unscii_loader import UNSCII_8, UNSCII_16

W, H = 68, 160
SCALE = 6
OUT = os.path.dirname(os.path.abspath(__file__))
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def canvas():
    im = Image.new("L", (W, H), 255)
    return im, ImageDraw.Draw(im)


def save(im, name):
    bw = im.point(lambda v: 0 if v < 128 else 255, mode="1")
    bw.save(os.path.join(OUT, f"{name}.png"))
    bw.convert("L").resize((W * SCALE, H * SCALE), Image.NEAREST).save(
        os.path.join(OUT, f"{name}_x{SCALE}.png")
    )


# ---------- shared helpers ------------------------------------------


def dots_carousel(d, y, count, active, size=3, gap=3):
    total_w = count * size + (count - 1) * gap
    x0 = (W - total_w) // 2
    for i in range(count):
        cx = x0 + i * (size + gap)
        if i == active:
            d.ellipse([cx, y, cx + size - 1, y + size - 1], fill=0)
        else:
            d.ellipse([cx, y, cx + size - 1, y + size - 1], outline=0)


def battery_cells(d, x, y, pct, cells=5, cw=3, ch=6, gap=1):
    filled = round(cells * pct / 100)
    for i in range(cells):
        cx = x + i * (cw + gap)
        if i < filled:
            d.rectangle([cx, y, cx + cw - 1, y + ch - 1], fill=0)
        else:
            d.rectangle([cx, y, cx + cw - 1, y + ch - 1], outline=0)


def battery_thin(d, y, pct, x=0, w=W, h=4):
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=0)
    inner_w = w - 4
    fill_w = max(0, inner_w * pct // 100)
    if fill_w > 0:
        d.rectangle([x + 2, y + 1, x + 2 + fill_w, y + h - 2], fill=0)


def bt_glyph(d, x, y, size=8):
    mid = x + size // 2
    q1 = y + size // 4
    q3 = y + 3 * size // 4
    d.line([(mid, y), (mid, y + size - 1)], fill=0)
    d.line([(mid, y), (mid + size // 3, q1), (mid, y + size // 2)], fill=0)
    d.line([(mid, y + size - 1), (mid + size // 3, q3), (mid, y + size // 2)], fill=0)


def draw_arc(d, cx, cy, r, start_deg, end_deg, thickness=1):
    """Rasterize an arc segment by drawing pixels along the sweep."""
    steps = max(int((end_deg - start_deg) * r / 30), 12)
    for i in range(steps + 1):
        a = math.radians(start_deg + (end_deg - start_deg) * i / steps)
        for t in range(thickness):
            px = cx + int((r - t) * math.cos(a))
            py = cy + int((r - t) * math.sin(a))
            d.point((px, py), fill=0)


def draw_ring_gauge(d, cx, cy, r, pct, thickness=2):
    """Circle outline with fill sweep from top clockwise."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=0)
    if pct > 0:
        # Start at -90 (top), sweep clockwise
        sweep = 360 * pct / 100
        # Ticks around the ring
        n_ticks = 24
        for i in range(n_ticks):
            a = math.radians(-90 + i * (360 / n_ticks))
            px = cx + int((r - 3) * math.cos(a))
            py = cy + int((r - 3) * math.sin(a))
            angle_from_top = (i * 360 / n_ticks)
            if angle_from_top <= sweep:
                d.point((px, py), fill=0)
                d.point((px + 1, py), fill=0) if (px + 1 < W) else None
                d.point((px, py + 1), fill=0) if (py + 1 < H) else None


# ---------- 01 Watch Minimal ---------------------------------------


def m01_watch_minimal():
    im, d = canvas()
    # HUGE L3
    UNSCII_16.draw_text_centered(d, "L3", 8)
    # BT + 2
    bt_glyph(d, 20, 40, size=10)
    UNSCII_16.draw_text(d, "2", 36, 40)
    # dots row
    dots_carousel(d, 56, 5, 2)
    # L bat
    UNSCII_16.draw_text(d, "L", 4, 68)
    UNSCII_16.draw_text(d, "82", 22, 68)
    UNSCII_8.draw_text(d, "%", 40, 72)
    battery_cells(d, 4, 88, 82, cells=10, cw=5, ch=4, gap=1)
    # R bat
    UNSCII_16.draw_text(d, "R", 4, 100)
    UNSCII_16.draw_text(d, "91", 22, 100)
    UNSCII_8.draw_text(d, "%", 40, 104)
    battery_cells(d, 4, 120, 91, cells=10, cw=5, ch=4, gap=1)
    # WPM
    UNSCII_8.draw_text_centered(d, "WPM", 130)
    UNSCII_16.draw_text_centered(d, "92", 140)
    # bottom carousel dots
    dots_carousel(d, 156, 5, 0)
    save(im, "m01_watch_minimal")


# ---------- 02 Active Circle ----------------------------------------


def m02_active_circle():
    im, d = canvas()
    # Big ring with L3 inside
    draw_ring_gauge(d, W // 2, 28, 22, 100)
    UNSCII_16.draw_text_centered(d, "L3", 22)
    # BT + signal
    bt_glyph(d, 12, 56, size=8)
    UNSCII_8.draw_text(d, "2", 22, 56)
    # signal bars (5 mini)
    for i in range(5):
        h = i + 2
        d.rectangle([44 + i * 4, 62 - h, 46 + i * 4, 62], fill=0)
    # L battery ring
    draw_ring_gauge(d, W // 2, 84, 15, 82)
    UNSCII_8.draw_text_centered(d, "L", 76)
    UNSCII_8.draw_text_centered(d, "82%", 86)
    # R battery ring
    draw_ring_gauge(d, W // 2, 118, 15, 91)
    UNSCII_8.draw_text_centered(d, "R", 110)
    UNSCII_8.draw_text_centered(d, "91%", 120)
    # WPM bar viz
    UNSCII_8.draw_text_centered(d, "WPM 92", 142)
    # small bar chart
    heights = [3, 5, 4, 6, 3, 5, 6, 4, 7, 5, 3, 4]
    for i, hh in enumerate(heights):
        d.rectangle([4 + i * 5, 156 - hh, 6 + i * 5, 156], fill=0)
    save(im, "m02_active_circle")


# ---------- 03 Info Timeline ---------------------------------------


def m03_info_timeline():
    im, d = canvas()
    # Clock top
    UNSCII_16.draw_text_centered(d, "14:32", 4)
    # Vertical timeline line
    d.line([(W // 2, 24), (W // 2, 152)], fill=0)
    # Node 1: LAYER 03
    d.ellipse([W // 2 - 2, 26, W // 2 + 2, 30], outline=0)
    UNSCII_8.draw_text_centered(d, "LAYER", 34)
    UNSCII_16.draw_text_centered(d, "03", 44)
    # Node 2: BT
    d.ellipse([W // 2 - 2, 62, W // 2 + 2, 66], outline=0)
    bt_glyph(d, 22, 68, size=8)
    UNSCII_8.draw_text(d, "2", 38, 68)
    # Node 3: BATTERY
    d.ellipse([W // 2 - 2, 82, W // 2 + 2, 86], fill=0)
    UNSCII_8.draw_text_centered(d, "BATTERY", 90)
    UNSCII_8.draw_text(d, "L", 8, 100)
    battery_cells(d, 18, 100, 82, cells=8, cw=4, ch=6, gap=1)
    UNSCII_8.draw_text(d, "82%", 4, 110)
    UNSCII_8.draw_text(d, "R", 8, 120)
    battery_cells(d, 18, 120, 91, cells=8, cw=4, ch=6, gap=1)
    UNSCII_8.draw_text(d, "91%", 4, 130)
    # Node 4: WPM
    d.ellipse([W // 2 - 2, 140, W // 2 + 2, 144], fill=0)
    UNSCII_8.draw_text_centered(d, "WPM", 146)
    UNSCII_16.draw_text_centered(d, "92", 150)
    save(im, "m03_info_timeline")


# ---------- 04 Braun Industrial ------------------------------------


def m04_braun_industrial():
    im, d = canvas()
    # Diagonal stripes top
    for i in range(0, W + 20, 6):
        d.line([(i, 0), (i - 8, 8)], fill=0)
    # LAYER
    UNSCII_8.draw_text(d, "LAYER", 4, 14)
    UNSCII_16.draw_text(d, "03", 4, 24)
    # BLE
    UNSCII_8.draw_text(d, "BLE", 4, 46)
    bt_glyph(d, 30, 46, size=8)
    # BATTERY
    UNSCII_8.draw_text(d, "BATTERY", 4, 62)
    UNSCII_8.draw_text(d, "L", 4, 74)
    battery_cells(d, 14, 74, 82, cells=8, cw=5, ch=7, gap=1)
    UNSCII_8.draw_text(d, "82%", 4, 86)
    UNSCII_8.draw_text(d, "R", 4, 100)
    battery_cells(d, 14, 100, 91, cells=8, cw=5, ch=7, gap=1)
    UNSCII_8.draw_text(d, "91%", 4, 112)
    # WPM
    UNSCII_8.draw_text(d, "WPM", 4, 126)
    UNSCII_16.draw_text(d, "92", 4, 136)
    # Diagonal stripes bottom
    for i in range(0, W + 20, 6):
        d.line([(i, 156), (i - 8, 148)], fill=0)
    save(im, "m04_braun_industrial")


# ---------- 05 SF Radar ---------------------------------------------


def m05_sf_radar():
    im, d = canvas()
    # Radar circle top
    cx, cy, r = 34, 22, 20
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=0)
    d.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5], outline=0)
    # Radar sweep line
    a = math.radians(-45)
    d.line([(cx, cy), (cx + int(r * math.cos(a)), cy + int(r * math.sin(a)))], fill=0)
    # Blip dot
    d.ellipse([cx + 8, cy - 12, cx + 11, cy - 9], fill=0)
    d.ellipse([cx - 6, cy + 4, cx - 4, cy + 6], fill=0)
    # LAYER
    UNSCII_8.draw_text(d, "LAYER", 4, 50)
    UNSCII_16.draw_text(d, "03", 4, 60)
    # BLE with signal bars
    UNSCII_8.draw_text(d, "BLE", 4, 82)
    UNSCII_8.draw_text(d, "2", 22, 82)
    # signal bars
    for i in range(8):
        hh = i + 2
        d.rectangle([32 + i * 4, 88 - hh, 34 + i * 4, 88], fill=0)
    # L bat cells
    d.text_pos = None
    battery_cells(d, 0, 100, 82, cells=8, cw=4, ch=7, gap=1)
    UNSCII_8.draw_text(d, "L", 48, 100)
    UNSCII_8.draw_text(d, "82%", 40, 110)
    # R bat cells
    battery_cells(d, 0, 122, 91, cells=8, cw=4, ch=7, gap=1)
    UNSCII_8.draw_text(d, "R", 48, 122)
    UNSCII_8.draw_text(d, "91%", 40, 132)
    # WPM
    UNSCII_8.draw_text_centered(d, "WPM", 144)
    UNSCII_16.draw_text_centered(d, "92", 152) if False else None
    UNSCII_16.draw_text_centered(d, "92", 145)
    save(im, "m05_sf_radar")


# ---------- 06 Game Boy Dot -----------------------------------------


# 10x10 pixel cat
CAT = [
    "..#####.....",
    ".##...##....",
    ".#.....#....",
    ".##...##....",
    "...###......",
    "..######....",
    ".#..##..#...",
    ".########...",
    "..#....#....",
    "..######....",
]


def m06_gameboy_dot():
    im, d = canvas()
    # Cat top-center
    for ry, row in enumerate(CAT):
        for rx, c in enumerate(row):
            if c == "#":
                d.point((28 + rx, 4 + ry), fill=0)
    # dashed hline
    for x in range(0, W, 3):
        d.point((x, 24), fill=0)
    # LAYER 03
    UNSCII_8.draw_text(d, "LAYER", 4, 30)
    UNSCII_16.draw_text(d, "03", 4, 40)
    # BT
    bt_glyph(d, 4, 60, size=8)
    UNSCII_8.draw_text(d, "2", 20, 60)
    # L battery card with hearts
    d.rectangle([2, 76, W - 3, 96], outline=0)
    UNSCII_8.draw_text(d, "L", 6, 80)
    # Draw hearts
    for i in range(5):
        cx = 14 + i * 8
        cy = 82
        # tiny heart shape
        d.point((cx, cy), fill=0)
        d.point((cx + 2, cy), fill=0)
        d.point((cx - 1, cy + 1), fill=0)
        d.point((cx, cy + 1), fill=0)
        d.point((cx + 1, cy + 1), fill=0)
        d.point((cx + 2, cy + 1), fill=0)
        d.point((cx + 3, cy + 1), fill=0)
        d.point((cx, cy + 2), fill=0)
        d.point((cx + 1, cy + 2), fill=0)
        d.point((cx + 2, cy + 2), fill=0)
        d.point((cx + 1, cy + 3), fill=0)
        if i >= 4:  # only 4 hearts filled for 82%
            pass
    UNSCII_8.draw_text(d, "82%", 48, 88)
    # R battery card
    d.rectangle([2, 100, W - 3, 120], outline=0)
    UNSCII_8.draw_text(d, "R", 6, 104)
    for i in range(5):
        cx = 14 + i * 8
        cy = 106
        d.point((cx, cy), fill=0)
        d.point((cx + 2, cy), fill=0)
        d.point((cx - 1, cy + 1), fill=0)
        d.point((cx, cy + 1), fill=0)
        d.point((cx + 1, cy + 1), fill=0)
        d.point((cx + 2, cy + 1), fill=0)
        d.point((cx + 3, cy + 1), fill=0)
        d.point((cx, cy + 2), fill=0)
        d.point((cx + 1, cy + 2), fill=0)
        d.point((cx + 2, cy + 2), fill=0)
        d.point((cx + 1, cy + 3), fill=0)
    UNSCII_8.draw_text(d, "91%", 48, 112)
    # WPM
    UNSCII_8.draw_text_centered(d, "WPM", 128)
    UNSCII_16.draw_text_centered(d, "92", 138)
    # bottom checkerboard
    for x in range(0, W, 2):
        d.point((x, 156), fill=0)
    save(im, "m06_gameboy_dot")


# ---------- 07 Submarine Dash --------------------------------------


SUBMARINE = [
    "...............",
    ".....######....",
    "....########...",
    "...##########..",
    "..##.##.#####..",
    "..############.",
    "...##########..",
    "....#.#.#.#....",
]


def m07_submarine_dash():
    im, d = canvas()
    for ry, row in enumerate(SUBMARINE):
        for rx, c in enumerate(row):
            if c == "#":
                d.point((26 + rx, 4 + ry), fill=0)
    # bubbles
    d.ellipse([20, 8, 22, 10], outline=0)
    d.ellipse([16, 12, 18, 14], outline=0)
    UNSCII_8.draw_text(d, "LAYER", 4, 28)
    UNSCII_16.draw_text(d, "03", 4, 38)
    bt_glyph(d, 4, 58, size=8)
    UNSCII_8.draw_text(d, "2", 18, 58)
    dots_carousel(d, 60, 5, 2)
    # L bat cells
    UNSCII_8.draw_text(d, "L", 4, 74)
    battery_cells(d, 12, 74, 82, cells=6, cw=5, ch=7, gap=2)
    UNSCII_8.draw_text(d, "82%", 48, 74)
    # wave under L
    for x in range(0, W, 4):
        d.point((x + 1, 84), fill=0)
        d.point((x + 2, 84), fill=0)
        d.point((x, 85), fill=0)
        d.point((x + 3, 85), fill=0)
    # R bat cells
    UNSCII_8.draw_text(d, "R", 4, 96)
    battery_cells(d, 12, 96, 91, cells=6, cw=5, ch=7, gap=2)
    UNSCII_8.draw_text(d, "91%", 48, 96)
    # wave under R
    for x in range(0, W, 4):
        d.point((x + 1, 106), fill=0)
        d.point((x + 2, 106), fill=0)
        d.point((x, 107), fill=0)
        d.point((x + 3, 107), fill=0)
    # WPM
    UNSCII_8.draw_text_centered(d, "WPM", 120)
    UNSCII_16.draw_text_centered(d, "92", 130)
    # bottom wave
    for x in range(0, W, 4):
        d.point((x + 1, 152), fill=0)
        d.point((x + 2, 152), fill=0)
        d.point((x, 153), fill=0)
        d.point((x + 3, 153), fill=0)
    save(im, "m07_submarine_dash")


# ---------- 08 Module Block ----------------------------------------


def m08_module_block():
    im, d = canvas()
    # Layer module
    d.rectangle([4, 4, W - 5, 26], outline=0)
    UNSCII_8.draw_text_centered(d, "LAYER", 8)
    UNSCII_16.draw_text_centered(d, "03", 15)
    # BLE module with signal
    d.rectangle([4, 30, W - 5, 50], outline=0)
    UNSCII_8.draw_text(d, "BLE", 8, 34)
    UNSCII_16.draw_text(d, "2", 8, 40)
    for i in range(5):
        hh = i + 2
        d.rectangle([40 + i * 4, 46 - hh, 42 + i * 4, 46], fill=0)
    # L module
    d.rectangle([4, 54, W - 5, 82], outline=0)
    UNSCII_8.draw_text(d, "L", 8, 58)
    # small battery icon
    d.rectangle([8, 66, 32, 76], outline=0)
    d.rectangle([32, 68, 33, 74], fill=0)
    fill = 82 * 20 // 100
    d.rectangle([10, 68, 10 + fill, 74], fill=0)
    UNSCII_8.draw_text(d, "82%", 42, 68)
    # R module
    d.rectangle([4, 86, W - 5, 114], outline=0)
    UNSCII_8.draw_text(d, "R", 8, 90)
    d.rectangle([8, 98, 32, 108], outline=0)
    d.rectangle([32, 100, 33, 106], fill=0)
    fill = 91 * 20 // 100
    d.rectangle([10, 100, 10 + fill, 106], fill=0)
    UNSCII_8.draw_text(d, "91%", 42, 100)
    # WPM module
    d.rectangle([4, 118, W - 5, 152], outline=0)
    UNSCII_8.draw_text_centered(d, "WPM", 122)
    UNSCII_16.draw_text_centered(d, "92", 132)
    save(im, "m08_module_block")


# ---------- 09 Orbit Gauge -----------------------------------------


def m09_orbit_gauge():
    im, d = canvas()
    # Planet + rings
    cx, cy = W // 2, 20
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], outline=0)
    # 2 elliptical orbits
    for a, b in [(24, 8), (30, 6)]:
        for t in range(0, 360, 12):
            th = math.radians(t)
            px = cx + int(a * math.cos(th))
            py = cy + int(b * math.sin(th))
            if 0 <= px < W and 0 <= py < H:
                d.point((px, py), fill=0)
    # tiny satellite
    d.ellipse([cx + 22, cy - 2, cx + 24, cy], fill=0)
    UNSCII_8.draw_text(d, "LAYER", 4, 44)
    UNSCII_16.draw_text(d, "03", 4, 54)
    bt_glyph(d, 40, 46, size=8)
    UNSCII_8.draw_text(d, "2", 54, 46)
    dots_carousel(d, 58, 5, 2)
    # L curved gauge (half-circle)
    draw_arc(d, 20, 92, 14, 180, 360, thickness=1)
    filled_deg = 180 * 82 / 100
    draw_arc(d, 20, 92, 12, 180, 180 + filled_deg, thickness=2)
    UNSCII_8.draw_text(d, "L", 15, 80)
    UNSCII_8.draw_text(d, "82%", 8, 96)
    # R curved gauge
    draw_arc(d, 48, 92, 14, 180, 360, thickness=1)
    filled_deg = 180 * 91 / 100
    draw_arc(d, 48, 92, 12, 180, 180 + filled_deg, thickness=2)
    UNSCII_8.draw_text(d, "R", 43, 80)
    UNSCII_8.draw_text(d, "91%", 36, 96)
    # WPM
    UNSCII_8.draw_text_centered(d, "WPM", 116)
    UNSCII_16.draw_text_centered(d, "92", 126)
    # bottom subtle line
    d.line([(4, 150), (W - 5, 150)], fill=0)
    save(im, "m09_orbit_gauge")


# ---------- 10 Essential Line --------------------------------------


def m10_essential_line():
    im, d = canvas()
    # Diagonal decor top-right
    d.line([(W - 25, 0), (W - 1, 24)], fill=0)
    UNSCII_8.draw_text_centered(d, "LAYER", 30)
    UNSCII_16.draw_text_centered(d, "03", 40)
    # tiny circle bottom-right of layer
    d.ellipse([W - 8, 46, W - 4, 50], outline=0)
    # BT
    bt_glyph(d, 24, 66, size=8)
    UNSCII_8.draw_text(d, "2", 40, 66)
    # L bat thin line + %
    UNSCII_8.draw_text(d, "L", 4, 88)
    d.line([(14, 92), (44, 92)], fill=0)
    fill_x = 14 + (44 - 14) * 82 // 100
    d.rectangle([14, 90, fill_x, 94], fill=0)
    UNSCII_8.draw_text(d, "82%", 48, 88)
    # R bat
    UNSCII_8.draw_text(d, "R", 4, 108)
    d.line([(14, 112), (44, 112)], fill=0)
    fill_x = 14 + (44 - 14) * 91 // 100
    d.rectangle([14, 110, fill_x, 114], fill=0)
    UNSCII_8.draw_text(d, "91%", 48, 108)
    # WPM
    UNSCII_8.draw_text_centered(d, "WPM", 132)
    UNSCII_16.draw_text_centered(d, "92", 142)
    # Diagonal decor bottom-left
    d.line([(0, 158), (24, 138)], fill=0)
    save(im, "m10_essential_line")


# ---------- contact sheet ------------------------------------------


def contact_sheet_v9():
    names = [
        "m01_watch_minimal",
        "m02_active_circle",
        "m03_info_timeline",
        "m04_braun_industrial",
        "m05_sf_radar",
        "m06_gameboy_dot",
        "m07_submarine_dash",
        "m08_module_block",
        "m09_orbit_gauge",
        "m10_essential_line",
    ]
    imgs = [Image.open(os.path.join(OUT, f"{n}_x{SCALE}.png")) for n in names]
    per_row = 5
    cell_w, cell_h = imgs[0].size
    gap = 20
    rows = (len(imgs) + per_row - 1) // per_row
    sheet_w = per_row * cell_w + (per_row + 1) * gap
    sheet_h = rows * (cell_h + 40) + gap
    sheet = Image.new("L", (sheet_w, sheet_h), 240)
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype(FONT_BOLD, 16)
    for i, im in enumerate(imgs):
        row, col = divmod(i, per_row)
        x = gap + col * (cell_w + gap)
        y = gap + row * (cell_h + 40)
        sheet.paste(im, (x, y))
        draw.text((x, y + cell_h + 4), names[i], fill=0, font=label_font)
    sheet.save(os.path.join(OUT, "contact_sheet_v9.png"))


def main():
    m01_watch_minimal()
    m02_active_circle()
    m03_info_timeline()
    m04_braun_industrial()
    m05_sf_radar()
    m06_gameboy_dot()
    m07_submarine_dash()
    m08_module_block()
    m09_orbit_gauge()
    m10_essential_line()
    contact_sheet_v9()
    print("Done. See:", OUT)


if __name__ == "__main__":
    main()
