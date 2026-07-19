#!/usr/bin/env python3
"""v8 - full 68 px width batteries, thin height. Various label treatments."""

import os
from PIL import Image, ImageDraw, ImageFont

from unscii_loader import UNSCII_8, UNSCII_16

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


def paste_logo(im):
    im.paste(load_logo(), (0, 0))


# ---------- battery variants: FULL WIDTH, thin ----------------------


def battery_full_thin(d, y, pct, h=4):
    """Full 68 px wide, `h` px tall bar. Outline + fill. No nub."""
    d.rectangle([0, y, W - 1, y + h - 1], outline=0)
    inner_w = W - 4
    fill_w = max(0, inner_w * pct // 100)
    if fill_w > 0:
        d.rectangle([2, y + 1, 2 + fill_w, y + h - 2], fill=0)


def battery_full_thin_nub(d, y, pct, h=6):
    """Full width minus 3 (for nub); h px tall."""
    body_w = W - 3
    d.rectangle([0, y, body_w - 1, y + h - 1], outline=0)
    inner_w = body_w - 4
    fill_w = max(0, inner_w * pct // 100)
    if fill_w > 0:
        d.rectangle([2, y + 1, 2 + fill_w, y + h - 2], fill=0)
    nub_h = max(2, h - 2)
    nub_y = y + (h - nub_h) // 2
    d.rectangle([body_w, nub_y, body_w + 1, nub_y + nub_h - 1], fill=0)


def layer_dots(d, x, y, active_index, count=5, size=3, gap=2):
    for i in range(count):
        cx = x + i * (size + gap)
        if i == active_index:
            d.rectangle([cx, y, cx + size - 1, y + size - 1], fill=0)
        else:
            d.rectangle([cx, y, cx + size - 1, y + size - 1], outline=0)


def mods_dots(d, x, y, mods, size=6, gap=8):
    keys = [("shift", "s"), ("ctrl", "c"), ("alt", "a"), ("gui", "w")]
    for i, (k, lbl) in enumerate(keys):
        cx = x + i * (size + gap)
        if mods.get(k, False):
            d.ellipse([cx, y, cx + size - 1, y + size - 1], fill=0)
        else:
            d.ellipse([cx, y, cx + size - 1, y + size - 1], outline=0)
        UNSCII_8.draw_char(d, lbl, cx - 1, y + size + 1)


# ---------- v8 mockups ----------------------------------------------


def v8a_thin_bar_labels_above():
    """Full width 4 px bars, label + % on the line above."""
    im, d = canvas()
    paste_logo(im)

    UNSCII_16.draw_text_centered(d, "BASE", 30)
    layer_dots(d, 22, 58, active_index=0)

    mods_dots(d, 12, 76, {"shift": True})

    UNSCII_8.draw_text_centered(d, "BLE 2", 104)
    UNSCII_8.draw_text_centered(d, "78 WPM", 116)

    # Batteries: label above, thin bar below
    UNSCII_8.draw_text(d, "L", 0, 130)
    UNSCII_8.draw_text(d, "87%", 52, 130)
    battery_full_thin(d, 141, 87, h=4)

    UNSCII_8.draw_text(d, "R", 0, 148)
    UNSCII_8.draw_text(d, "92%", 52, 148)
    battery_full_thin(d, 155, 92, h=4)

    save(im, "v8a_labels_above")


def v8b_super_minimal_bars():
    """Just the bars. L is top, R is bottom by convention. No labels."""
    im, d = canvas()
    paste_logo(im)

    UNSCII_16.draw_text_centered(d, "BASE", 30)
    layer_dots(d, 22, 58, active_index=0)

    mods_dots(d, 12, 76, {"shift": True})

    UNSCII_8.draw_text_centered(d, "BLE 2", 104)
    UNSCII_8.draw_text_centered(d, "78 WPM", 116)

    # Two thin full-width bars stacked with 1 px gap
    battery_full_thin(d, 148, 87, h=4)
    battery_full_thin(d, 154, 92, h=4)

    save(im, "v8b_super_minimal")


def v8c_percent_inline():
    """Full width bar with percentage rendered INSIDE the bar (fill inverts)."""
    im, d = canvas()
    paste_logo(im)

    UNSCII_16.draw_text_centered(d, "BASE", 30)
    layer_dots(d, 22, 58, active_index=0)

    mods_dots(d, 12, 76, {"shift": True})

    UNSCII_8.draw_text_centered(d, "BLE 2", 104)
    UNSCII_8.draw_text_centered(d, "78 WPM", 116)

    # Thin bars with L/R label to left, % to right, on same line
    UNSCII_8.draw_text(d, "L", 0, 138)
    battery_full_thin(d, 142, 87, h=6)
    battery_full_thin_nub(d, 151, 92, h=6)
    UNSCII_8.draw_text(d, "R", 0, 150)
    save(im, "v8c_percent_inline")


def v8d_nub_variant():
    """Full width WITH nub (2 px). Nub at right edge, bar thin."""
    im, d = canvas()
    paste_logo(im)

    UNSCII_16.draw_text_centered(d, "BASE", 30)
    layer_dots(d, 22, 58, active_index=0)

    mods_dots(d, 12, 76, {"shift": True})

    UNSCII_8.draw_text_centered(d, "BLE 2", 104)
    UNSCII_8.draw_text_centered(d, "78 WPM", 116)

    # Two nubbed bars
    UNSCII_8.draw_text(d, "L 87", 0, 129)
    battery_full_thin_nub(d, 140, 87, h=5)
    UNSCII_8.draw_text(d, "R 92", 0, 148)
    battery_full_thin_nub(d, 155, 92, h=5)

    save(im, "v8d_nub_variant")


def v8e_number_over_bar():
    """Percentage number above bar, label below bar, ultra-clean."""
    im, d = canvas()
    paste_logo(im)

    UNSCII_16.draw_text_centered(d, "BASE", 30)
    layer_dots(d, 22, 58, active_index=0)

    mods_dots(d, 12, 76, {"shift": True})

    UNSCII_8.draw_text_centered(d, "BLE 2", 104)
    UNSCII_8.draw_text_centered(d, "78 WPM", 116)

    # Numbers above bars, letters inline left
    UNSCII_8.draw_text(d, "L 87    R 92", 0, 132)
    battery_full_thin(d, 141, 87, h=3)
    battery_full_thin(d, 148, 92, h=3)

    save(im, "v8e_number_over_bar")


def contact_sheet_v8():
    names = [
        "v8a_labels_above",
        "v8b_super_minimal",
        "v8c_percent_inline",
        "v8d_nub_variant",
        "v8e_number_over_bar",
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
    sheet.save(os.path.join(OUT, "contact_sheet_v8.png"))


def main():
    v8a_thin_bar_labels_above()
    v8b_super_minimal_bars()
    v8c_percent_inline()
    v8d_nub_variant()
    v8e_number_over_bar()
    contact_sheet_v8()
    print("Done. See:", OUT)


if __name__ == "__main__":
    main()
