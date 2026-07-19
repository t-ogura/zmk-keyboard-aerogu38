#!/usr/bin/env python3
"""v12 - 4-corner minor info + center hero layer name."""

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


def draw_bt(d, x, y):
    for ry, row in enumerate(BLUETOOTH):
        for rx, c in enumerate(row):
            if c == "#":
                d.point((x + rx, y + ry), fill=0)


def battery_mini(d, x, y, pct, w=18, h=6):
    """Tiny battery for corners."""
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=0)
    # nub
    d.rectangle([x + w, y + 1, x + w + 1, y + h - 2], fill=0)
    fill = max(0, (w - 4) * pct // 100)
    if fill > 0:
        d.rectangle([x + 2, y + 2, x + 2 + fill, y + h - 3], fill=0)


def battery_bar_bottom(d, y, pct, x=0, w=W - 1, h=3):
    """Thin corner-adjacent bar."""
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=0)
    fill = max(0, (w - 4) * pct // 100)
    if fill > 0:
        top = y + 1 if h < 4 else y + 2
        bot = y + h - 2
        if bot >= top:
            d.rectangle([x + 2, top, x + 2 + fill, bot], fill=0)


# ---------- v12 mockups --------------------------------------------


def v12a_corners_no_label():
    """Just BASE centered, corners have BT / WPM / L bat / R bat."""
    im, d = canvas()
    paste_logo(im)

    # Top-left: BT icon + 2
    draw_bt(d, 0, 24)
    d.text((10, 25), "2", fill=0, font=FS)

    # Top-right: WPM 78 (small)
    d.text((44, 25), "78W", fill=0, font=FS)

    # Center hero: BASE (32 pt Spleen)
    text_center(d, 60, "BASE", FXL)

    # Bottom-left: L battery
    d.text((0, 130), "L", fill=0, font=FS)
    d.text((0, 141), "82", fill=0, font=FS)
    battery_bar_bottom(d, 155, 82, x=0, w=32, h=3)

    # Bottom-right: R battery
    d.text((50, 130), "R", fill=0, font=FS)
    d.text((50, 141), "91", fill=0, font=FS)
    battery_bar_bottom(d, 155, 91, x=36, w=32, h=3)

    save(im, "v12a_corners_no_label")


def v12b_corners_with_layer_label():
    """Add small "LAYER" label above BASE."""
    im, d = canvas()
    paste_logo(im)

    # Corners
    draw_bt(d, 0, 24)
    d.text((10, 25), "2", fill=0, font=FS)
    d.text((44, 25), "78W", fill=0, font=FS)

    # Center: small "LAYER" + big BASE
    text_center(d, 56, "LAYER", FS)
    text_center(d, 76, "BASE", FXL)

    # Layer index dots
    for i in range(5):
        cx = 22 + i * 5
        if i == 0:
            d.rectangle([cx, 114, cx + 2, 116], fill=0)
        else:
            d.rectangle([cx, 114, cx + 2, 116], outline=0)

    # Bottom-left L / bottom-right R
    d.text((0, 130), "L", fill=0, font=FS)
    d.text((0, 141), "82%", fill=0, font=FS)
    battery_bar_bottom(d, 154, 82, x=0, w=32, h=4)

    d.text((44, 130), "R", fill=0, font=FS)
    d.text((44, 141), "91%", fill=0, font=FS)
    battery_bar_bottom(d, 154, 91, x=36, w=32, h=4)

    save(im, "v12b_corners_with_label")


def v12c_symmetric_corners_mini_bat():
    """Battery as tiny nubbed icons in corners with % inline."""
    im, d = canvas()
    paste_logo(im)

    # Top-left: BT
    draw_bt(d, 0, 24)
    d.text((10, 25), "2", fill=0, font=FS)

    # Top-right: WPM
    d.text((44, 25), "78W", fill=0, font=FS)

    # Small LAYER + BASE center
    text_center(d, 56, "LAYER", FS)
    text_center(d, 74, "BASE", FXL)

    # Bottom-left: tiny battery + %
    battery_mini(d, 0, 148, 82, w=16, h=7)
    d.text((20, 148), "82%", fill=0, font=FS)

    # Bottom-right: tiny battery + %
    battery_mini(d, 45, 148, 91, w=16, h=7)
    d.text((30, 148), "91%", fill=0, font=FS) if False else None
    # actually put the % on the LEFT of the battery for right side
    # to keep numbers pointing inward
    save_im2 = None
    # reset and redo bottom-right
    d.rectangle([40, 145, W - 1, 158], fill=255)
    battery_mini(d, 51, 148, 91, w=15, h=7)
    d.text((40, 148), "91", fill=0, font=FS)

    save(im, "v12c_mini_batteries")


def v12d_pure_extreme():
    """Absolute extreme: only BASE center, corners smallest possible."""
    im, d = canvas()
    paste_logo(im)

    # Tiny corner info
    draw_bt(d, 0, 24)
    d.text((10, 24), "2", fill=0, font=FS)
    d.text((56, 24), "78", fill=0, font=FS)

    # BASE giant center (as tall as possible)
    text_center(d, 55, "BASE", FXL)

    # Bottom just numbers
    d.text((0, 148), "82", fill=0, font=FS)
    d.text((56, 148), "91", fill=0, font=FS)

    save(im, "v12d_pure_extreme")


def v12e_center_layer_stacked_battery():
    """BASE center, but batteries stacked full-width thin at bottom."""
    im, d = canvas()
    paste_logo(im)

    draw_bt(d, 0, 24)
    d.text((10, 25), "2", fill=0, font=FS)
    d.text((44, 25), "78W", fill=0, font=FS)

    text_center(d, 46, "LAYER", FS)
    text_center(d, 66, "BASE", FXL)

    # 5 layer dots
    for i in range(5):
        cx = 22 + i * 5
        if i == 0:
            d.rectangle([cx, 104, cx + 2, 106], fill=0)
        else:
            d.rectangle([cx, 104, cx + 2, 106], outline=0)

    # Batteries stacked full-width thin
    d.text((0, 118), "L", fill=0, font=FS)
    d.text((50, 118), "82%", fill=0, font=FS)
    battery_bar_bottom(d, 132, 82, x=0, w=W, h=4)

    d.text((0, 140), "R", fill=0, font=FS)
    d.text((50, 140), "91%", fill=0, font=FS)
    battery_bar_bottom(d, 154, 91, x=0, w=W, h=4)

    save(im, "v12e_stacked_bat")


def contact_sheet_v12():
    names = [
        "v12a_corners_no_label",
        "v12b_corners_with_label",
        "v12c_mini_batteries",
        "v12d_pure_extreme",
        "v12e_stacked_bat",
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
    sheet.save(os.path.join(OUT, "contact_sheet_v12.png"))


def main():
    v12a_corners_no_label()
    v12b_corners_with_layer_label()
    v12c_symmetric_corners_mini_bat()
    v12d_pure_extreme()
    v12e_center_layer_stacked_battery()
    contact_sheet_v12()
    print("Done. See:", OUT)


if __name__ == "__main__":
    main()
