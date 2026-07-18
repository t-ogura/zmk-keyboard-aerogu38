#!/usr/bin/env python3
"""aerogu38 LCD mockup renderer v2 - incorporates feedback + web research.

Improvements over v1:
- Larger fonts (min 10 px, hero elements 20+)
- Bolder modifier icons (drawn on 12x12 pixel grids explicitly)
- Layer name example "BASE"
- Info packed to bottom, no wasted whitespace
- Inspirations from nice-view-gem, Tamagotchi meters, Casio F-91W,
  Vim mode chips, QMK uppercase mods, Pebble anomaly BT
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 68, 160
SCALE = 6
OUT = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(os.path.dirname(OUT), "logo_portrait_68x20.png")

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

# ---------- helpers ---------------------------------------------------


def canvas():
    im = Image.new("L", (W, H), 255)
    return im, ImageDraw.Draw(im)


def save(im, name):
    bw = im.point(lambda v: 0 if v < 128 else 255, mode="1")
    bw.save(os.path.join(OUT, f"{name}.png"))
    bw.convert("L").resize((W * SCALE, H * SCALE), Image.NEAREST).save(
        os.path.join(OUT, f"{name}_x{SCALE}.png")
    )


def load_logo():
    return Image.open(LOGO_PATH).convert("L")


def f(size):
    return ImageFont.truetype(FONT_BOLD, size)


def text_width(draw, s, ft):
    bbox = draw.textbbox((0, 0), s, font=ft)
    return bbox[2] - bbox[0]


def draw_text_center(draw, y, s, ft):
    w = text_width(draw, s, ft)
    draw.text(((W - w) // 2, y), s, fill=0, font=ft)


def hline(draw, y, thick=1):
    draw.rectangle([0, y, W - 1, y + thick - 1], fill=0)


def invert_rect(im, box):
    """Invert pixel colors inside box (for Vim-style mode chip)."""
    x0, y0, x1, y1 = box
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            v = im.getpixel((x, y))
            im.putpixel((x, y), 255 - v)


# ---------- 12x12 pixel-art modifier glyphs --------------------------
#
# Each glyph is a 12x12 list of 12-char strings ('#' filled, '.' empty).

GLYPHS = {
    "shift": [
        "......##....",
        ".....####...",
        "....######..",
        "...########.",
        "..##########",
        ".#####.#####",
        "....###.....",
        "....###.....",
        "....###.....",
        "....###.....",
        "....###.....",
        "....###.....",
    ],
    "ctrl": [
        "....##......",
        "...####.....",
        "..######....",
        ".########...",
        "########....",
        "............",
        "............",
        "............",
        "............",
        "............",
        "............",
        "............",
    ],
    "alt": [
        ".##.....##..",
        "..##....##..",
        "..##....##..",
        "..##....##..",
        "..##....##..",
        "...##...##..",
        "....##..##..",
        "....##..##..",
        "....##..##..",
        "....##..##..",
        ".....####...",
        "............",
    ],
    "gui": [
        ".##......##.",
        "###......###",
        "###......###",
        "###.####.###",
        ".#..####..#.",
        "....####....",
        "....####....",
        ".#..####..#.",
        "###.####.###",
        "###......###",
        "###......###",
        ".##......##.",
    ],
    # Symbols set - modifier glyphs (Mac style condensed to 12x12)
    "sym_shift": [
        "....##......",
        "...####.....",
        "..######....",
        ".########...",
        "########....",
        "..##########",
        "..######.###",
        "..######.###",
        "..######.###",
        "..######.###",
        "..######.###",
        "..##########",
    ],
    "sym_cmd": [
        ".###....###.",
        "#####..#####",
        "#####..#####",
        "###########.",
        ".########.##",
        "..######..##",
        "...####...##",
        "..######..##",
        ".########.##",
        "############",
        "#####..#####",
        ".###....###.",
    ],
}


def draw_glyph(draw, x, y, key, active):
    pattern = GLYPHS.get(key)
    if not pattern:
        return
    for row_i, row in enumerate(pattern):
        for col_i, c in enumerate(row):
            if c == "#" and active:
                draw.point((x + col_i, y + row_i), fill=0)
            elif c == "#" and not active:
                # dim state: draw only the outline pixels
                is_edge = (
                    row_i == 0 or row_i == len(pattern) - 1
                    or col_i == 0 or col_i == len(row) - 1
                )
                # For each # pixel, draw only if it's on an "edge"
                # approx: pixel is drawn if any 4-neighbour is '.'
                neigh = 0
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        yy = row_i + dy
                        xx = col_i + dx
                        if 0 <= yy < len(pattern) and 0 <= xx < len(row):
                            if pattern[yy][xx] == ".":
                                neigh += 1
                        else:
                            neigh += 1
                if neigh > 0:
                    draw.point((x + col_i, y + row_i), fill=0)


def mods_row(draw, x, y, mods, spacing=14):
    """4 glyphs spaced across."""
    keys = ["shift", "ctrl", "alt", "gui"]
    for i, k in enumerate(keys):
        draw_glyph(draw, x + i * spacing, y, k, mods.get(k, False))


# ---------- battery variants -----------------------------------------


def battery_h_big(draw, y, pct, height=10, width=52):
    """Horizontal bar spanning nearly full width, larger."""
    x = 6
    draw.rectangle([x, y, x + width, y + height - 1], outline=0, fill=None)
    fill_w = max(0, (width - 4) * pct // 100)
    if fill_w > 0:
        draw.rectangle([x + 2, y + 2, x + 2 + fill_w, y + height - 3], fill=0)


def battery_cells(draw, y, pct, cells=5, cell_w=10, cell_h=9, gap=1):
    """Tamagotchi cell-count meter. cells filled proportional to pct."""
    filled = round(cells * pct / 100)
    total_w = cells * cell_w + (cells - 1) * gap
    x0 = (W - total_w) // 2
    for i in range(cells):
        cx = x0 + i * (cell_w + gap)
        is_filled = i < filled
        if is_filled:
            draw.rectangle([cx, y, cx + cell_w - 1, y + cell_h - 1], fill=0)
        else:
            draw.rectangle([cx, y, cx + cell_w - 1, y + cell_h - 1], outline=0, fill=None)


def battery_v_stack(draw, x, y0, y1, pct, w=8):
    """Vertical bar stacked between y0 and y1."""
    draw.rectangle([x, y0, x + w - 1, y1], outline=0)
    inner_h = (y1 - y0) - 3
    fill_h = int(inner_h * pct / 100)
    if fill_h > 0:
        draw.rectangle([x + 2, y1 - 1 - fill_h, x + w - 3, y1 - 2], fill=0)


def battery_staircase(draw, x, y, pct, steps=5, step_w=3, step_h=3):
    """Nokia-style staircase, tallest step on far side."""
    filled = round(steps * pct / 100)
    for i in range(steps):
        sh = (i + 1) * step_h
        sx = x + i * step_w
        sy = y - sh
        if i < filled:
            draw.rectangle([sx, sy, sx + step_w - 1, y - 1], fill=0)
        else:
            draw.rectangle([sx, sy, sx + step_w - 1, y - 1], outline=0)


# ---------- other widgets --------------------------------------------


def bt_glyph(draw, x, y, size=14):
    """Bluetooth glyph, chunky."""
    mid = x + size // 2
    top = y
    bot = y + size - 1
    q1 = y + size // 4
    q3 = y + 3 * size // 4
    draw.line([(mid, top), (mid, bot)], fill=0, width=1)
    draw.line([(mid, top), (mid + size // 3, q1)], fill=0)
    draw.line([(mid + size // 3, q1), (mid, y + size // 2)], fill=0)
    draw.line([(mid, y + size // 2), (mid + size // 3, q3)], fill=0)
    draw.line([(mid + size // 3, q3), (mid, bot)], fill=0)


def profile_dots(draw, x, y, active_index, count=5, r=2, gap=3):
    """Row of small dots, active filled, others outlined."""
    for i in range(count):
        cx = x + i * (r * 2 + gap) + r
        if i == active_index:
            draw.ellipse([cx - r, y, cx + r, y + 2 * r], fill=0)
        else:
            draw.ellipse([cx - r, y, cx + r, y + 2 * r], outline=0)


def mode_chip(draw, im, y, s, chip_h=20, invert=True):
    """Vim-style inverted mode chip: [BASE] on inverted background."""
    ft = f(14)
    w = text_width(draw, s, ft) + 8
    x0 = (W - w) // 2
    draw.rectangle([x0, y, x0 + w, y + chip_h], fill=0)
    # Draw text in white on the black chip. PIL doesn't do "white on
    # inverted region" trivially; simulate by drawing then inverting.
    # Simpler: manually punch text out using L=255 pixels.
    tx = x0 + 4
    ty = y + (chip_h - 14) // 2 - 1
    # draw text in white directly since bg is black
    draw.text((tx, ty), s, fill=255, font=ft)


# ---------- 8 new mockups --------------------------------------------


def n1_niceview_stack():
    """Proven vertical stack borrowed from nice-view-gem proportions."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 22)
    # Layer name (big, dominant)
    draw_text_center(d, 30, "BASE", f(20))
    hline(d, 56)
    # BT + profile dots
    bt_glyph(d, 4, 62, size=14)
    profile_dots(d, 22, 68, active_index=2, count=5, r=2, gap=4)
    hline(d, 82)
    # Modifiers row (fixed slots, F-91W discipline)
    mods_row(d, 4, 88, {"shift": True}, spacing=15)
    hline(d, 106)
    # Batteries: two horizontal bars, side letter labels + big %
    d.text((4, 110), "L", fill=0, font=f(9))
    battery_h_big(d, 111, 87, width=42)
    d.text((54, 110), "87", fill=0, font=f(10))
    d.text((4, 128), "R", fill=0, font=f(9))
    battery_h_big(d, 129, 92, width=42)
    d.text((54, 128), "92", fill=0, font=f(10))
    # WPM (bottom)
    hline(d, 145)
    draw_text_center(d, 148, "78WPM", f(10))
    save(im, "n1_niceview_stack")


def n2_tamagotchi_cells():
    """Cell-count battery meters, Tamagotchi style. Reads faster than a bar."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 22)
    draw_text_center(d, 28, "BASE", f(22))
    hline(d, 58)
    # Mods
    mods_row(d, 4, 64, {"shift": True, "ctrl": False, "alt": True}, spacing=15)
    hline(d, 82)
    # BT label + dots
    d.text((4, 88), "BT", fill=0, font=f(10))
    profile_dots(d, 24, 92, active_index=2, count=5, r=2, gap=4)
    hline(d, 104)
    # Battery cells
    d.text((4, 108), "L", fill=0, font=f(10))
    battery_cells(d, 108, 87, cells=5, cell_w=10, cell_h=9)
    d.text((4, 122), "R", fill=0, font=f(10))
    battery_cells(d, 122, 92, cells=5, cell_w=10, cell_h=9)
    # Pack bottom
    hline(d, 137)
    d.text((4, 141), "L87 R92", fill=0, font=f(10))
    save(im, "n2_tamagotchi_cells")


def n3_nokia_staircase():
    """Two staircases at edges frame the central info column."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 22)
    # Central "column" of info
    draw_text_center(d, 30, "BASE", f(20))
    hline(d, 56)
    # Center-ish mods
    mods_row(d, 4, 62, {"shift": True}, spacing=15)
    hline(d, 80)
    draw_text_center(d, 84, "BT 2", f(14))
    hline(d, 104)
    # Staircase batteries on left/right edges, tall
    battery_staircase(d, 4, 158, 87, steps=7, step_w=3, step_h=5)
    battery_staircase(d, 43, 158, 92, steps=7, step_w=3, step_h=5)
    # Central numbers
    d.text((28, 118), "L", fill=0, font=f(11))
    d.text((28, 132), "87", fill=0, font=f(11))
    d.text((28, 145), "92", fill=0, font=f(11))
    save(im, "n3_nokia_staircase")


def n4_casio_reserved():
    """All slots reserved & always visible; only 'lit' when active."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 22)
    draw_text_center(d, 30, "BASE", f(20))
    hline(d, 56)
    # Reserved BT slot
    bt_glyph(d, 4, 62, size=14)
    d.text((22, 62), "2", fill=0, font=f(14))
    # Reserved USB slot next to it (dim if not USB)
    draw_glyph(d, 46, 62, "shift", False)  # placeholder USB glyph dim
    hline(d, 82)
    # Reserved modifier slots always drawn
    mods_row(d, 4, 88, {"shift": True, "ctrl": False, "alt": True, "gui": False}, spacing=15)
    hline(d, 106)
    # Reserved battery slots
    d.text((4, 110), "L", fill=0, font=f(11))
    battery_h_big(d, 112, 87, width=42)
    d.text((54, 110), "87", fill=0, font=f(11))
    d.text((4, 128), "R", fill=0, font=f(11))
    battery_h_big(d, 130, 92, width=42)
    d.text((54, 128), "92", fill=0, font=f(11))
    hline(d, 146)
    draw_text_center(d, 148, "78WPM", f(10))
    save(im, "n4_casio_reserved")


def n5_vim_chip():
    """Vim mode-chip layer indicator, inverted block for hero element."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 22)
    mode_chip(d, im, 28, "BASE")
    hline(d, 54)
    # Modifiers
    mods_row(d, 4, 60, {"shift": True, "ctrl": False, "alt": False, "gui": True}, spacing=15)
    hline(d, 78)
    # BT + profile dots
    bt_glyph(d, 4, 84, size=14)
    profile_dots(d, 22, 90, active_index=2, count=5, r=2, gap=4)
    hline(d, 104)
    # Batteries
    d.text((4, 108), "L", fill=0, font=f(11))
    battery_h_big(d, 111, 87, width=42)
    d.text((54, 108), "87", fill=0, font=f(11))
    d.text((4, 128), "R", fill=0, font=f(11))
    battery_h_big(d, 131, 92, width=42)
    d.text((54, 128), "92", fill=0, font=f(11))
    hline(d, 146)
    draw_text_center(d, 149, "78WPM", f(10))
    save(im, "n5_vim_chip")


def n6_qmk_uppercase():
    """QMK-style SHFT/CTL/ALT/GUI text — uppercase = held. No pixel icons."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 22)
    draw_text_center(d, 30, "BASE", f(20))
    hline(d, 56)
    # Mod row as text: 4 slots, uppercase if held
    active = {"shift": True, "ctrl": False, "alt": True, "gui": False}
    labels = [
        "SHFT" if active["shift"] else "----",
        "CTL " if active["ctrl"] else "----",
        "ALT " if active["alt"] else "----",
        "GUI " if active["gui"] else "----",
    ]
    # Split into 2 rows of 2
    d.text((4, 60), labels[0], fill=0, font=f(11))
    d.text((36, 60), labels[1], fill=0, font=f(11))
    d.text((4, 74), labels[2], fill=0, font=f(11))
    d.text((36, 74), labels[3], fill=0, font=f(11))
    hline(d, 90)
    bt_glyph(d, 4, 94, size=14)
    d.text((22, 94), "BT2", fill=0, font=f(14))
    hline(d, 114)
    d.text((4, 118), "L", fill=0, font=f(11))
    battery_h_big(d, 121, 87, width=42)
    d.text((54, 118), "87", fill=0, font=f(11))
    d.text((4, 137), "R", fill=0, font=f(11))
    battery_h_big(d, 140, 92, width=42)
    d.text((54, 137), "92", fill=0, font=f(11))
    save(im, "n6_qmk_uppercase")


def n7_pebble_hidden_bt():
    """BT icon hidden when connected — profile dots + activity mark. Frees space."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 22)
    draw_text_center(d, 30, "BASE", f(22))
    hline(d, 58)
    # Mods
    mods_row(d, 4, 64, {"shift": True, "alt": True}, spacing=15)
    hline(d, 82)
    # Profile dots only (BT icon hidden)
    d.text((4, 88), "P", fill=0, font=f(11))
    profile_dots(d, 20, 92, active_index=2, count=5, r=3, gap=5)
    hline(d, 106)
    # Big batteries with reversed layout: percentage first, bar second
    d.text((4, 110), "L 87%", fill=0, font=f(11))
    battery_h_big(d, 122, 87, width=56, height=6)
    d.text((4, 132), "R 92%", fill=0, font=f(11))
    battery_h_big(d, 144, 92, width=56, height=6)
    save(im, "n7_pebble_hidden_bt")


def n8_combined_best():
    """Combination of what I think are the strongest ideas from n1-n7."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 22)
    # Vim inverted chip for layer name (n5)
    mode_chip(d, im, 28, "BASE")
    hline(d, 54)
    # Reserved modifier slots always visible (n4 / F-91W discipline)
    mods_row(d, 4, 60, {"shift": True}, spacing=15)
    hline(d, 78)
    # Profile dots only (n7 - BT icon hidden when connected)
    d.text((4, 84), "P", fill=0, font=f(11))
    profile_dots(d, 20, 88, active_index=2, count=5, r=3, gap=5)
    hline(d, 102)
    # Tamagotchi cells for battery (n2)
    d.text((4, 106), "L", fill=0, font=f(10))
    battery_cells(d, 106, 87, cells=5, cell_w=10, cell_h=9)
    d.text((4, 120), "R", fill=0, font=f(10))
    battery_cells(d, 120, 92, cells=5, cell_w=10, cell_h=9)
    hline(d, 135)
    # WPM (idle-friendly, small)
    draw_text_center(d, 138, "78 WPM", f(11))
    # Numeric battery summary at bottom
    hline(d, 152)
    draw_text_center(d, 154, "87 / 92", f(9))
    save(im, "n8_combined")


def contact_sheet_v2():
    names = [
        "n1_niceview_stack",
        "n2_tamagotchi_cells",
        "n3_nokia_staircase",
        "n4_casio_reserved",
        "n5_vim_chip",
        "n6_qmk_uppercase",
        "n7_pebble_hidden_bt",
        "n8_combined",
    ]
    imgs = [Image.open(os.path.join(OUT, f"{n}_x{SCALE}.png")) for n in names]
    per_row = 4
    cell_w, cell_h = imgs[0].size
    gap = 20
    rows = (len(imgs) + per_row - 1) // per_row
    sheet_w = per_row * cell_w + (per_row + 1) * gap
    sheet_h = rows * (cell_h + 40) + gap
    sheet = Image.new("L", (sheet_w, sheet_h), 240)
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype(FONT_BOLD, 18)
    for i, im in enumerate(imgs):
        row, col = divmod(i, per_row)
        x = gap + col * (cell_w + gap)
        y = gap + row * (cell_h + 40)
        sheet.paste(im, (x, y))
        draw.text((x, y + cell_h + 4), names[i], fill=0, font=label_font)
    sheet.save(os.path.join(OUT, "contact_sheet_v2.png"))


def main():
    n1_niceview_stack()
    n2_tamagotchi_cells()
    n3_nokia_staircase()
    n4_casio_reserved()
    n5_vim_chip()
    n6_qmk_uppercase()
    n7_pebble_hidden_bt()
    n8_combined_best()
    contact_sheet_v2()
    print("Done. See:", OUT)


if __name__ == "__main__":
    main()
