#!/usr/bin/env python3
"""aerogu38 LCD mockup renderer v3 - focused refinements.

v3 changes from v2:
- Modifier glyphs redrawn at 16x16, chunky Mac-style shapes
- Battery back to horizontal bar with proper "nub" cap (looks like a battery)
- Two battery variants: compact horizontal + short vertical
- Layer name enlarged (24-28 px hero) + layer-index square dots
- Replace BT icon with plain "BLE" text + connection index
- USB glyph traced from Pixelarticons style
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 68, 160
SCALE = 6
OUT = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(os.path.dirname(OUT), "logo_portrait_68x20.png")
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


def load_logo():
    return Image.open(LOGO_PATH).convert("L")


def f(size):
    return ImageFont.truetype(FONT_BOLD, size)


def text_w(draw, s, ft):
    b = draw.textbbox((0, 0), s, font=ft)
    return b[2] - b[0]


def text_center(draw, y, s, ft):
    w = text_w(draw, s, ft)
    draw.text(((W - w) // 2, y), s, fill=0, font=ft)


def hline(draw, y, thick=1):
    draw.rectangle([0, y, W - 1, y + thick - 1], fill=0)


# ---------- 16x16 modifier glyphs (chunky Mac style) -----------------


G16_SHIFT = [
    "................",
    ".......##.......",
    "......####......",
    ".....######.....",
    "....########....",
    "...##########...",
    "..############..",
    ".##############.",
    "....##....##....",
    "....########....",
    "....########....",
    "....########....",
    "....########....",
    "....########....",
    "....########....",
    "................",
]

G16_CTRL = [
    "................",
    "................",
    ".......##.......",
    "......####......",
    ".....######.....",
    "....########....",
    "...##########...",
    "..############..",
    ".##############.",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
]

G16_ALT = [
    "................",
    "................",
    "###.......######",
    "###......###....",
    ".##......##.....",
    ".##.....###.....",
    ".##....###......",
    ".##....##.......",
    ".##...##........",
    ".##..###........",
    ".##..##.........",
    ".##.###.........",
    ".##.##..........",
    ".####...........",
    ".###............",
    "................",
]

G16_GUI = [
    "................",
    "..###.....###...",
    ".#####...#####..",
    ".##.###.###.##..",
    ".##..#####..##..",
    ".##..#####..##..",
    "..###.###.###...",
    "....####.###....",
    "....####.###....",
    "..###.###.###...",
    ".##..#####..##..",
    ".##..#####..##..",
    ".##.###.###.##..",
    ".#####...#####..",
    "..###.....###...",
    "................",
]


def draw_16(draw, x, y, pattern, active):
    """Draw 16x16 glyph: solid when active, outlined-only when idle."""
    for ry, row in enumerate(pattern):
        for rx, c in enumerate(row):
            if c != "#":
                continue
            if active:
                draw.point((x + rx, y + ry), fill=0)
            else:
                # keep only edge pixels
                neigh_empty = False
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    yy, xx = ry + dy, rx + dx
                    if not (0 <= yy < len(pattern) and 0 <= xx < len(row)):
                        neigh_empty = True
                        break
                    if pattern[yy][xx] != "#":
                        neigh_empty = True
                        break
                if neigh_empty:
                    draw.point((x + rx, y + ry), fill=0)


MOD_PATTERNS = {
    "shift": G16_SHIFT,
    "ctrl": G16_CTRL,
    "alt": G16_ALT,
    "gui": G16_GUI,
}


def mods_16(draw, y, active_dict, x_start=1):
    """4 modifier glyphs at 16x16 spaced across the 68-wide screen."""
    # 4 * 16 = 64, plus 3 gaps of 1 = 67 - fits in 68
    x = x_start
    for k in ("shift", "ctrl", "alt", "gui"):
        draw_16(draw, x, y, MOD_PATTERNS[k], active_dict.get(k, False))
        x += 17


# ---------- battery with proper nub ---------------------------------


def battery_h_nub(draw, x, y, pct, body_w=44, body_h=10):
    """Horizontal battery: body rect + 2-pixel nub on the right end."""
    # Body
    draw.rectangle([x, y, x + body_w - 1, y + body_h - 1], outline=0)
    # Nub
    nub_h = max(3, body_h - 4)
    nub_y = y + (body_h - nub_h) // 2
    draw.rectangle([x + body_w, nub_y, x + body_w + 2, nub_y + nub_h - 1], fill=0)
    # Fill
    inner_w = body_w - 4
    fill_w = max(0, inner_w * pct // 100)
    if fill_w > 0:
        draw.rectangle(
            [x + 2, y + 2, x + 2 + fill_w, y + body_h - 3], fill=0
        )


def battery_v_short(draw, x, y, pct, w=10, h=22):
    """Short vertical battery, nub on top."""
    nub_w = max(3, w - 4)
    nub_x = x + (w - nub_w) // 2
    draw.rectangle([nub_x, y, nub_x + nub_w - 1, y + 1], fill=0)
    body_y = y + 2
    draw.rectangle([x, body_y, x + w - 1, body_y + h - 1], outline=0)
    inner_h = h - 4
    fill_h = int(inner_h * pct / 100)
    if fill_h > 0:
        draw.rectangle(
            [x + 2, body_y + h - 2 - fill_h, x + w - 3, body_y + h - 3], fill=0
        )


# ---------- layer dots (3x3 squares) --------------------------------


def layer_dots(draw, y, active_index, count=5, size=3, gap=2):
    """Row of small square dots indicating current layer of total."""
    total_w = count * size + (count - 1) * gap
    x0 = (W - total_w) // 2
    for i in range(count):
        cx = x0 + i * (size + gap)
        if i == active_index:
            draw.rectangle([cx, y, cx + size - 1, y + size - 1], fill=0)
        else:
            draw.rectangle([cx, y, cx + size - 1, y + size - 1], outline=0)


# ---------- USB pixel-art icon (pixelarticons-inspired 12x8) --------


G_USB = [
    "....####....",
    "...######...",
    "....#..#....",
    "....####....",
    "....#..#....",
    "....####....",
    "....####....",
    "....####....",
]


def draw_usb(draw, x, y):
    for ry, row in enumerate(G_USB):
        for rx, c in enumerate(row):
            if c == "#":
                draw.point((x + rx, y + ry), fill=0)


# ---------- v3 mockups ----------------------------------------------


def v3a_compact_baseline():
    """v0/m0 baseline, compressed to bottom, mods enlarged."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 21)

    # Layer name (bigger, hero)
    text_center(d, 26, "BASE", f(24))
    # Layer dots
    layer_dots(d, 54, active_index=0, count=5)

    hline(d, 62)

    # Modifiers 16x16
    mods_16(d, 66, {"shift": True, "ctrl": False, "alt": False, "gui": False})

    hline(d, 87)

    # BLE + connection number
    d.text((4, 92), "BLE 2", fill=0, font=f(14))

    hline(d, 112)

    # Batteries: horizontal with proper battery shape
    d.text((4, 116), "L", fill=0, font=f(10))
    battery_h_nub(d, 14, 117, 87, body_w=32, body_h=9)
    d.text((50, 116), "87%", fill=0, font=f(10))

    d.text((4, 132), "R", fill=0, font=f(10))
    battery_h_nub(d, 14, 133, 92, body_w=32, body_h=9)
    d.text((50, 132), "92%", fill=0, font=f(10))

    # WPM at bottom
    hline(d, 148)
    text_center(d, 150, "78 WPM", f(10))

    save(im, "v3a_compact_baseline")


def v3b_short_vertical():
    """Same as v3a but batteries are short vertical bars saving 1 row."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 21)

    text_center(d, 26, "BASE", f(24))
    layer_dots(d, 54, active_index=0, count=5)

    hline(d, 62)

    mods_16(d, 66, {"shift": True, "ctrl": False, "alt": False, "gui": False})

    hline(d, 87)

    d.text((4, 92), "BLE 2", fill=0, font=f(14))

    hline(d, 112)

    # Vertical batteries side by side, short
    d.text((6, 116), "L", fill=0, font=f(10))
    battery_v_short(d, 4, 128, 87, w=10, h=26)
    d.text((4, 156), "87", fill=0, font=f(9))

    d.text((41, 116), "R", fill=0, font=f(10))
    battery_v_short(d, 39, 128, 92, w=10, h=26)
    d.text((39, 156), "92", fill=0, font=f(9))

    # WPM to the right of L battery text
    d.text((22, 132), "78", fill=0, font=f(16))
    d.text((22, 149), "WPM", fill=0, font=f(8))

    save(im, "v3b_short_vertical")


def v3c_hero_layer():
    """Layer name is the star. Everything else in a tight bottom cluster."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 21)

    # Massive hero layer
    text_center(d, 32, "BASE", f(28))
    layer_dots(d, 68, active_index=0, count=5)

    hline(d, 78)

    # Modifiers 16x16
    mods_16(d, 82, {"shift": True, "alt": True})

    hline(d, 103)

    # BLE
    d.text((4, 107), "BLE 2", fill=0, font=f(14))

    hline(d, 126)

    # Compact batteries
    d.text((4, 130), "L", fill=0, font=f(9))
    battery_h_nub(d, 12, 131, 87, body_w=30, body_h=8)
    d.text((48, 130), "87%", fill=0, font=f(9))

    d.text((4, 145), "R", fill=0, font=f(9))
    battery_h_nub(d, 12, 146, 92, body_w=30, body_h=8)
    d.text((48, 145), "92%", fill=0, font=f(9))

    save(im, "v3c_hero_layer")


def v3d_side_verticals():
    """Vertical batteries hugging left/right edges; central column for info."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 21)

    # Layer name (with side batteries flanking)
    text_center(d, 26, "BASE", f(22))
    layer_dots(d, 52, active_index=0, count=5)

    hline(d, 60)

    # Central mods
    mods_16(d, 64, {"shift": True, "ctrl": False})

    hline(d, 85)

    # Central BLE
    text_center(d, 90, "BLE 2", f(14))

    hline(d, 110)

    # WPM central
    text_center(d, 114, "78", f(22))
    text_center(d, 138, "WPM", f(10))

    # Side vertical batteries (edge)
    battery_v_short(d, 2, 114, 87, w=8, h=32)
    d.text((2, 148), "87", fill=0, font=f(8))

    battery_v_short(d, 58, 114, 92, w=8, h=32)
    d.text((56, 148), "92", fill=0, font=f(8))

    save(im, "v3d_side_verticals")


def v3e_grid():
    """Info as 2-column grid pairs: L/R, Layer/Endpoint - denser."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 21)

    text_center(d, 26, "BASE", f(24))
    layer_dots(d, 54, active_index=0, count=5)

    hline(d, 62)

    # Two-column info row: BLE left, WPM right
    d.text((4, 66), "BLE 2", fill=0, font=f(12))
    d.text((40, 66), "78WPM", fill=0, font=f(10))

    hline(d, 82)

    # Mods
    mods_16(d, 86, {"shift": True})

    hline(d, 107)

    # Batteries dense
    d.text((4, 111), "L 87%", fill=0, font=f(11))
    battery_h_nub(d, 4, 124, 87, body_w=60, body_h=8)

    d.text((4, 136), "R 92%", fill=0, font=f(11))
    battery_h_nub(d, 4, 149, 92, body_w=60, body_h=8)

    save(im, "v3e_grid")


def contact_sheet_v3():
    names = [
        "v3a_compact_baseline",
        "v3b_short_vertical",
        "v3c_hero_layer",
        "v3d_side_verticals",
        "v3e_grid",
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
        y = gap
        sheet.paste(im, (x, y))
        draw.text((x, y + cell_h + 4), names[i], fill=0, font=label_font)
    sheet.save(os.path.join(OUT, "contact_sheet_v3.png"))


def main():
    v3a_compact_baseline()
    v3b_short_vertical()
    v3c_hero_layer()
    v3d_side_verticals()
    v3e_grid()
    contact_sheet_v3()
    print("Done. See:", OUT)


if __name__ == "__main__":
    main()
