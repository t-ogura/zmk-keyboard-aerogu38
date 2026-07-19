#!/usr/bin/env python3
"""v13 - design #4 (Ring + Bar, futuristic) implementation."""

import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 68, 160
SCALE = 6
OUT = os.path.dirname(os.path.abspath(__file__))
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

FS = ImageFont.truetype(os.path.join(OUT, "fonts/spleen-6x12.otf"), 12)
FM = ImageFont.truetype(os.path.join(OUT, "fonts/spleen-8x16.otf"), 16)
FL = ImageFont.truetype(os.path.join(OUT, "fonts/spleen-12x24.otf"), 24)


def canvas():
    im = Image.new("L", (W, H), 255)
    return im, ImageDraw.Draw(im)


def save(im, name):
    bw = im.point(lambda v: 0 if v < 128 else 255, mode="1")
    bw.save(os.path.join(OUT, f"{name}.png"))
    bw.convert("L").resize((W * SCALE, H * SCALE), Image.NEAREST).save(
        os.path.join(OUT, f"{name}_x{SCALE}.png")
    )


def text_w(draw, s, ft):
    b = draw.textbbox((0, 0), s, font=ft)
    return b[2] - b[0]


def text_center(draw, y, s, ft, x_min=0, x_max=W):
    w = text_w(draw, s, ft)
    draw.text((x_min + (x_max - x_min - w) // 2, y), s, fill=0, font=ft)


def paste_logo(im):
    im.paste(Image.open(os.path.join(os.path.dirname(OUT), "logo_portrait_68x20.png")).convert("L"), (0, 0))


# ---------- Bluetooth glyph ----------------------------------------


BLUETOOTH = [
    "....#....",
    "....##...",
    "..#.#.#..",
    "...####..",
    "....##...",
    "...####..",
    "..#.#.#..",
    "....##...",
    "....#....",
]


def draw_bt(d, x, y, subscript_number=None, subfont=None):
    for ry, row in enumerate(BLUETOOTH):
        for rx, c in enumerate(row):
            if c == "#":
                d.point((x + rx, y + ry), fill=0)
    if subscript_number is not None and subfont is not None:
        # Small number bottom-right of the icon
        d.text((x + 9, y + 3), str(subscript_number), fill=0, font=subfont)


# ---------- Ring gauge with layer segments ------------------------


def draw_ring_layer(d, cx, cy, r, total_layers, active_layer, gap_deg=8):
    """Ring divided into `total_layers` segments. Active is BOLD.
    Between segments is a gap for visual separation."""
    seg_deg = (360 / total_layers) - gap_deg
    start = -90  # top
    for i in range(total_layers):
        seg_start = start + i * (seg_deg + gap_deg)
        seg_end = seg_start + seg_deg
        thickness = 3 if i == active_layer else 1
        rasterize_arc(d, cx, cy, r, seg_start, seg_end, thickness)


def rasterize_arc(d, cx, cy, r, start_deg, end_deg, thickness=1):
    steps = max(int((end_deg - start_deg) * r / 20), 12)
    for i in range(steps + 1):
        a = math.radians(start_deg + (end_deg - start_deg) * i / steps)
        for t in range(thickness):
            px = cx + int((r - t) * math.cos(a))
            py = cy + int((r - t) * math.sin(a))
            if 0 <= px < W and 0 <= py < H:
                d.point((px, py), fill=0)


# ---------- Top decoration (antenna/bracket style) -----------------


def draw_top_decor(d, y_baseline=24):
    """Two horizontal lines with hooks pointing up on outer edges,
    approximating the design #4 top decoration."""
    # Left bracket
    d.line([(0, y_baseline), (18, y_baseline)], fill=0)
    d.line([(18, y_baseline), (22, y_baseline - 4)], fill=0)
    # Right bracket
    d.line([(W - 1, y_baseline), (W - 19, y_baseline)], fill=0)
    d.line([(W - 19, y_baseline), (W - 23, y_baseline - 4)], fill=0)


# ---------- Cell battery (segmented) -----------------------------


def battery_cell_bar(d, x, y, pct, cells=8, cw=4, ch=8, gap=1):
    """Small filled/empty cell bar with tapered end."""
    filled = round(cells * pct / 100)
    for i in range(cells):
        cx = x + i * (cw + gap)
        # slight taper on the last cell (thinner)
        c_ch = ch if i < cells - 2 else ch - 1
        c_top = y + (ch - c_ch)
        if i < filled:
            d.rectangle([cx, c_top, cx + cw - 1, c_top + c_ch - 1], fill=0)
        else:
            d.rectangle([cx, c_top, cx + cw - 1, c_top + c_ch - 1], outline=0)


# ---------- v13 mockups --------------------------------------------


def v13a_ring_and_bar_futuristic():
    """Direct implementation of design #4."""
    im, d = canvas()
    paste_logo(im)

    # Top: antenna/bracket decoration
    draw_top_decor(d, y_baseline=30)

    # BT icon top-center with subscript number bottom-right
    draw_bt(d, 30, 34, subscript_number=2, subfont=FS)

    # Center: ring around BASE with layer segments
    cx, cy = W // 2, 76
    draw_ring_layer(d, cx, cy, r=24, total_layers=5, active_layer=0)
    # BASE inside the ring
    text_center(d, 66, "BASE", FM)

    # Bottom: L and R cell battery bars
    d.text((0, 116), "L", fill=0, font=FM)
    battery_cell_bar(d, 12, 116, 92, cells=8, cw=4, ch=10, gap=1)
    d.text((52, 116), "92%", fill=0, font=FS)

    d.text((0, 134), "R", fill=0, font=FM)
    battery_cell_bar(d, 12, 134, 87, cells=8, cw=4, ch=10, gap=1)
    d.text((52, 134), "87%", fill=0, font=FS)

    save(im, "v13a_ring_bar_futuristic")


def v13b_ring_with_layer_progress():
    """Variant: ring shows 'progress' - segments fill up to active layer."""
    im, d = canvas()
    paste_logo(im)

    draw_top_decor(d, y_baseline=30)
    draw_bt(d, 30, 34, subscript_number=2, subfont=FS)

    # Ring: active_layer segments filled thick, others thin
    cx, cy = W // 2, 76
    total = 5
    active = 2  # for showing intent - "layer 2 of 5"
    gap_deg = 8
    seg_deg = (360 / total) - gap_deg
    for i in range(total):
        seg_start = -90 + i * (seg_deg + gap_deg)
        seg_end = seg_start + seg_deg
        thickness = 3 if i <= active else 1
        rasterize_arc(d, cx, cy, 24, seg_start, seg_end, thickness)

    text_center(d, 66, "BASE", FM)

    d.text((0, 116), "L", fill=0, font=FM)
    battery_cell_bar(d, 12, 116, 92, cells=8, cw=4, ch=10)
    d.text((52, 116), "92%", fill=0, font=FS)
    d.text((0, 134), "R", fill=0, font=FM)
    battery_cell_bar(d, 12, 134, 87, cells=8, cw=4, ch=10)
    d.text((52, 134), "87%", fill=0, font=FS)

    save(im, "v13b_progress_ring")


def v13c_ring_bigger_layer_name():
    """Bigger BASE (24pt) inside a slightly larger ring."""
    im, d = canvas()
    paste_logo(im)

    draw_top_decor(d, y_baseline=30)
    draw_bt(d, 30, 34, subscript_number=2, subfont=FS)

    cx, cy = W // 2, 80
    draw_ring_layer(d, cx, cy, r=28, total_layers=5, active_layer=0)
    text_center(d, 68, "BASE", FL)

    d.text((0, 118), "L", fill=0, font=FM)
    battery_cell_bar(d, 12, 118, 92, cells=8, cw=4, ch=10)
    d.text((52, 118), "92%", fill=0, font=FS)
    d.text((0, 136), "R", fill=0, font=FM)
    battery_cell_bar(d, 12, 136, 87, cells=8, cw=4, ch=10)
    d.text((52, 136), "87%", fill=0, font=FS)

    save(im, "v13c_bigger_ring")


def v13d_minimalist_ring():
    """Cleaner: no top decoration, just BT + ring + batteries."""
    im, d = canvas()
    paste_logo(im)

    # BT icon centered top with subscript
    draw_bt(d, 30, 26, subscript_number=2, subfont=FS)

    cx, cy = W // 2, 78
    draw_ring_layer(d, cx, cy, r=26, total_layers=5, active_layer=0)
    text_center(d, 66, "BASE", FL)

    # WPM at right of BT?
    d.text((44, 26), "78W", fill=0, font=FS)

    d.text((0, 120), "L", fill=0, font=FM)
    battery_cell_bar(d, 12, 120, 92, cells=8, cw=4, ch=10)
    d.text((52, 120), "92%", fill=0, font=FS)
    d.text((0, 138), "R", fill=0, font=FM)
    battery_cell_bar(d, 12, 138, 87, cells=8, cw=4, ch=10)
    d.text((52, 138), "87%", fill=0, font=FS)

    save(im, "v13d_minimalist_ring")


def v13e_double_ring_bat():
    """Alternate: two side-by-side rings for L/R battery (design #8-ish)."""
    im, d = canvas()
    paste_logo(im)

    draw_bt(d, 30, 26, subscript_number=2, subfont=FS)

    cx, cy = W // 2, 68
    draw_ring_layer(d, cx, cy, r=22, total_layers=5, active_layer=0)
    text_center(d, 60, "BASE", FM)

    # L / R rings for batteries
    def ring_bat(d, cx, cy, r, pct):
        rasterize_arc(d, cx, cy, r, -180, -180 + 180 * pct / 100, thickness=2)
        rasterize_arc(d, cx, cy, r, -180 + 180 * pct / 100, 0, thickness=1)

    ring_bat(d, 18, 128, 14, 92)
    text_center(d, 124, "L", FS, x_min=4, x_max=32)
    text_center(d, 134, "92", FS, x_min=4, x_max=32)

    ring_bat(d, 50, 128, 14, 87)
    text_center(d, 124, "R", FS, x_min=36, x_max=W)
    text_center(d, 134, "87", FS, x_min=36, x_max=W)

    save(im, "v13e_double_ring_bat")


def contact_sheet_v13():
    names = [
        "v13a_ring_bar_futuristic",
        "v13b_progress_ring",
        "v13c_bigger_ring",
        "v13d_minimalist_ring",
        "v13e_double_ring_bat",
    ]
    imgs = [Image.open(os.path.join(OUT, f"{n}_x{SCALE}.png")) for n in names]
    per_row = 5
    cell_w, cell_h = imgs[0].size
    gap = 20
    sheet_w = per_row * cell_w + (per_row + 1) * gap
    sheet_h = cell_h + 60
    sheet = Image.new("L", (sheet_w, sheet_h), 240)
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype(FONT_BOLD, 16)
    for i, im in enumerate(imgs):
        x = gap + i * (cell_w + gap)
        sheet.paste(im, (x, gap))
        draw.text((x, gap + cell_h + 4), names[i], fill=0, font=label_font)
    sheet.save(os.path.join(OUT, "contact_sheet_v13.png"))


def main():
    v13a_ring_and_bar_futuristic()
    v13b_ring_with_layer_progress()
    v13c_ring_bigger_layer_name()
    v13d_minimalist_ring()
    v13e_double_ring_bat()
    contact_sheet_v13()
    print("Done. See:", OUT)


if __name__ == "__main__":
    main()
