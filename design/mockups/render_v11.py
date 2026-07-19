#!/usr/bin/env python3
"""v11 - drop modifiers, hero layer name, Bluetooth glyph."""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 68, 160
SCALE = 6
OUT = os.path.dirname(os.path.abspath(__file__))
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

FS = ImageFont.truetype(os.path.join(OUT, "fonts/spleen-6x12.otf"), 12)
FM = ImageFont.truetype(os.path.join(OUT, "fonts/spleen-8x16.otf"), 16)
FL = ImageFont.truetype(os.path.join(OUT, "fonts/spleen-12x24.otf"), 24)
FXL = ImageFont.truetype(os.path.join(OUT, "fonts/spleen-16x32.otf"), 32)


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


def battery_h_full(d, y, pct, h=5):
    d.rectangle([0, y, W - 1, y + h - 1], outline=0)
    inner_w = W - 4
    fill = max(0, inner_w * pct // 100)
    if fill > 0:
        top = y + 1 if h < 6 else y + 2
        bot = y + h - 2 if h < 6 else y + h - 3
        if bot >= top:
            d.rectangle([2, top, 2 + fill, bot], fill=0)


# ---------- Bluetooth glyph 9x13 pixels ----------------------------


BLUETOOTH = [
    "....#....",
    "....##...",
    "..#.#.#..",   # upper diagonals cross
    "...####..",
    "....##...",
    "...####..",   # lower diagonals cross
    "..#.#.#..",
    "....##...",
    "....#....",
]


def draw_bt(d, x, y, size=None):
    for ry, row in enumerate(BLUETOOTH):
        for rx, c in enumerate(row):
            if c == "#":
                d.point((x + rx, y + ry), fill=0)


# larger version 11x15
BLUETOOTH_L = [
    ".....#.....",
    ".....##....",
    ".....#.#...",
    "..#..#..#..",
    "...#.#.#...",
    "....###....",
    ".....##....",
    ".....##....",
    "....###....",
    "...#.#.#...",
    "..#..#..#..",
    ".....#.#...",
    ".....##....",
    ".....#.....",
]


def draw_bt_large(d, x, y):
    for ry, row in enumerate(BLUETOOTH_L):
        for rx, c in enumerate(row):
            if c == "#":
                d.point((x + rx, y + ry), fill=0)


# ---------- v11 mockups --------------------------------------------


def v11a_hero_layer_pure():
    """BIG BASE + BT icon + number + batteries. WPM at bottom. No mods."""
    im, d = canvas()
    paste_logo(im)

    # BASE using extra-large 32 px hero
    text_center(d, 24, "BASE", FXL)

    # Layer index dots (small)
    for i in range(5):
        cx = 22 + i * 5
        if i == 0:
            d.rectangle([cx, 62, cx + 2, 64], fill=0)
        else:
            d.rectangle([cx, 62, cx + 2, 64], outline=0)

    # BT icon + "2" number, centered
    icon_x = (W - (9 + 4 + 8)) // 2   # 9 wide icon + 4 gap + 8 wide digit
    draw_bt(d, icon_x, 74)
    d.text((icon_x + 13, 74), "2", fill=0, font=FM)

    # WPM
    text_center(d, 96, "78 WPM", FM)

    # Batteries at bottom
    d.text((0, 122), "L 82", fill=0, font=FM)
    d.text((40, 122), "R 91", fill=0, font=FM)
    battery_h_full(d, 140, 82, h=5)
    battery_h_full(d, 150, 91, h=5)

    save(im, "v11a_hero_layer_pure")


def v11b_biggest_layer_no_wpm():
    """Even more extreme - no WPM, just BASE + BT + batteries."""
    im, d = canvas()
    paste_logo(im)

    # BASE (largest)
    text_center(d, 26, "BASE", FXL)

    # Layer dots
    for i in range(5):
        cx = 22 + i * 5
        if i == 0:
            d.rectangle([cx, 64, cx + 2, 66], fill=0)
        else:
            d.rectangle([cx, 64, cx + 2, 66], outline=0)

    # BT icon + 2 (larger BT glyph)
    icon_x = (W - (11 + 5 + 8)) // 2
    draw_bt_large(d, icon_x, 82)
    d.text((icon_x + 16, 84), "2", fill=0, font=FL)

    # Batteries at bottom, larger
    d.text((0, 118), "L 82%", fill=0, font=FM)
    d.text((38, 118), "R 91%", fill=0, font=FM)
    battery_h_full(d, 136, 82, h=6)
    battery_h_full(d, 148, 91, h=6)

    save(im, "v11b_biggest_layer")


def v11c_module_no_mods():
    """Module block v10b but without modifier module."""
    im, d = canvas()
    paste_logo(im)

    # LAYER module (bigger)
    d.rectangle([2, 22, W - 3, 60], outline=0)
    text_center(d, 24, "LAYER", FS, x_min=2, x_max=W - 3)
    text_center(d, 34, "BASE", FL, x_min=2, x_max=W - 3)

    # BT + BLE profile module
    d.rectangle([2, 64, W - 3, 90], outline=0)
    draw_bt(d, 8, 72)
    d.text((22, 68), "BT 2", fill=0, font=FM)

    # Battery module
    d.rectangle([2, 94, W - 3, 132], outline=0)
    d.text((6, 96), "L 82%", fill=0, font=FS)
    battery_h_full_within = lambda y, pct: (
        d.rectangle([6, y, W - 7, y + 4], outline=0),
        d.rectangle([8, y + 1, 8 + ((W - 15) * pct // 100), y + 3], fill=0),
    )
    battery_h_full_within(107, 82)
    d.text((6, 114), "R 91%", fill=0, font=FS)
    battery_h_full_within(125, 91)

    # WPM module
    d.rectangle([2, 136, W - 3, 158], outline=0)
    text_center(d, 138, "WPM", FS, x_min=2, x_max=W - 3)
    text_center(d, 148, "78", FL, x_min=2, x_max=W - 3)

    save(im, "v11c_module_no_mods")


def v11d_essential_no_mods():
    """Essential line style, without modifier row."""
    im, d = canvas()
    paste_logo(im)

    # Diagonal accent top-right
    for i in range(20):
        d.point((W - 1 - i, 22 + i), fill=0)

    text_center(d, 26, "LAYER", FS)
    text_center(d, 36, "BASE", FL)

    # BT with number
    icon_x = (W - (9 + 4 + 8)) // 2
    draw_bt(d, icon_x, 72)
    d.text((icon_x + 13, 74), "2", fill=0, font=FM)

    # Batteries thin line style
    d.text((0, 96), "L 82%", fill=0, font=FS)
    d.line([(30, 100), (W - 1, 100)], fill=0)
    fill_x = 30 + (W - 30) * 82 // 100
    d.rectangle([30, 98, fill_x, 102], fill=0)

    d.text((0, 108), "R 91%", fill=0, font=FS)
    d.line([(30, 112), (W - 1, 112)], fill=0)
    fill_x = 30 + (W - 30) * 91 // 100
    d.rectangle([30, 110, fill_x, 114], fill=0)

    # WPM
    text_center(d, 128, "WPM", FS)
    text_center(d, 138, "78", FL)

    # Diagonal accent bottom-left
    for i in range(20):
        d.point((i, 158 - i), fill=0)

    save(im, "v11d_essential_no_mods")


def v11e_watch_wpm_hero():
    """WPM 92 is hero (32px). Layer smaller. BT icon + digit."""
    im, d = canvas()
    paste_logo(im)

    # LAYER small at top
    text_center(d, 22, "LAYER", FS)
    text_center(d, 32, "BASE", FL)

    # BT icon + 2
    icon_x = (W - (9 + 4 + 8)) // 2
    draw_bt(d, icon_x, 60)
    d.text((icon_x + 13, 60), "2", fill=0, font=FM)

    # WPM hero
    text_center(d, 82, "92", FXL)
    text_center(d, 118, "WPM", FS)

    # Batteries at bottom
    d.text((0, 132), "L 82%", fill=0, font=FS)
    d.text((40, 132), "R 91%", fill=0, font=FS)
    battery_h_full(d, 146, 82, h=4)
    battery_h_full(d, 152, 91, h=4)

    save(im, "v11e_watch_wpm")


def contact_sheet_v11():
    names = [
        "v11a_hero_layer_pure",
        "v11b_biggest_layer",
        "v11c_module_no_mods",
        "v11d_essential_no_mods",
        "v11e_watch_wpm",
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
    sheet.save(os.path.join(OUT, "contact_sheet_v11.png"))


def main():
    v11a_hero_layer_pure()
    v11b_biggest_layer_no_wpm()
    v11c_module_no_mods()
    v11d_essential_no_mods()
    v11e_watch_wpm_hero()
    contact_sheet_v11()
    print("Done. See:", OUT)


if __name__ == "__main__":
    main()
