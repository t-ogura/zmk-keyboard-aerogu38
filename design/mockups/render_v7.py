#!/usr/bin/env python3
"""v7 - horizontal batteries (nice_view style) + non-alphabet modifiers.

Applies v6 feedback:
- Batteries switch to horizontal nice_view-style capsules
- Modifier alphabet ('S c a w') dropped - try dot / icon indicators
- BLE stays compact
"""

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


# ---------- battery: nice_view style horizontal capsule --------------


def battery_niceview(d, x, y, pct, body_w=30, body_h=10):
    """nice_view-inspired: outlined rect + inner fill + 2 px nub. Nice
    and clearly reads as a battery even at small sizes."""
    # Body outline
    d.rectangle([x, y, x + body_w - 1, y + body_h - 1], outline=0)
    # Inner fill area (2 px margin)
    inner_x, inner_y = x + 2, y + 2
    inner_w, inner_h = body_w - 4, body_h - 4
    fill_w = max(0, inner_w * pct // 100)
    if fill_w > 0:
        d.rectangle([inner_x, inner_y, inner_x + fill_w, inner_y + inner_h - 1], fill=0)
    # Nub
    nub_h = max(3, body_h - 4)
    nub_y = y + (body_h - nub_h) // 2
    d.rectangle([x + body_w, nub_y, x + body_w + 1, nub_y + nub_h - 1], fill=0)


def battery_niceview_labelled(d, x, y, pct, letter):
    """Combo: letter + battery + percentage in a compact 68-wide row."""
    UNSCII_8.draw_char(d, letter, x, y + 1)
    battery_niceview(d, x + 8, y, pct, body_w=30, body_h=10)
    UNSCII_8.draw_text(d, f"{pct}", x + 42, y + 1)


def layer_dots(d, x, y, active_index, count=5, size=3, gap=2):
    for i in range(count):
        cx = x + i * (size + gap)
        if i == active_index:
            d.rectangle([cx, y, cx + size - 1, y + size - 1], fill=0)
        else:
            d.rectangle([cx, y, cx + size - 1, y + size - 1], outline=0)


# ---------- modifier indicators (non-alphabet) -----------------------


def mods_dots(d, x, y, mods, size=6, gap=4, label_below=True):
    """4 filled/empty dots. Optionally tiny label below each."""
    keys = [("shift", "S"), ("ctrl", "C"), ("alt", "A"), ("gui", "W")]
    for i, (k, lbl) in enumerate(keys):
        cx = x + i * (size + gap)
        if mods.get(k, False):
            d.ellipse([cx, y, cx + size - 1, y + size - 1], fill=0)
        else:
            d.ellipse([cx, y, cx + size - 1, y + size - 1], outline=0)
        if label_below:
            UNSCII_8.draw_char(d, lbl.lower(), cx - 1, y + size + 1)


def mods_bar_tiles(d, x, y, mods, tile_w=13, tile_h=10, gap=2):
    """4 rectangular tiles. Filled black if held, empty outlined if idle.
    A small letter label in the center identifies the tile."""
    keys = [("shift", "S"), ("ctrl", "C"), ("alt", "A"), ("gui", "W")]
    for i, (k, lbl) in enumerate(keys):
        cx = x + i * (tile_w + gap)
        held = mods.get(k, False)
        if held:
            d.rectangle([cx, y, cx + tile_w - 1, y + tile_h - 1], fill=0)
            # White letter in center
            tmp = Image.new("L", (10, tile_h + 2), 255)
            td = ImageDraw.Draw(tmp)
            UNSCII_8.draw_char(td, lbl, 0, 0)
            # Paste inverted
            inv = tmp.point(lambda v: 255 - v)
            # Position label roughly centered
            # Ignore inverted paste - simplified: just leave the black tile
        else:
            d.rectangle([cx, y, cx + tile_w - 1, y + tile_h - 1], outline=0)


def mods_dashes(d, x, y, mods, gap=4):
    """Underscore-style: a thick dash under each slot, black if held."""
    keys = ["shift", "ctrl", "alt", "gui"]
    dash_w = 10
    for i, k in enumerate(keys):
        cx = x + i * (dash_w + gap)
        held = mods.get(k, False)
        # 3px tall dash - filled if held, thin line if not
        if held:
            d.rectangle([cx, y, cx + dash_w - 1, y + 2], fill=0)
        else:
            d.line([(cx, y + 1), (cx + dash_w - 1, y + 1)], fill=0)


# ---------- v7 mockups ----------------------------------------------


def v7a_horiz_bat_no_mods():
    """Nice_view purist: no modifier display, big layer name, horiz bats stacked."""
    im, d = canvas()
    paste_logo(im)

    # Big layer
    UNSCII_16.draw_text_centered(d, "BASE", 32)
    layer_dots(d, 22, 60, active_index=0)

    # WPM as secondary
    UNSCII_8.draw_text_centered(d, "78 WPM", 78)
    UNSCII_8.draw_text_centered(d, "BLE 2", 94)

    # Batteries: two horizontal, stacked, letter + capsule + %
    battery_niceview_labelled(d, 15, 122, 87, "L")
    battery_niceview_labelled(d, 15, 138, 92, "R")

    save(im, "v7a_horiz_bat_no_mods")


def v7b_dot_mods():
    """Compact dots for modifiers, horizontal batteries at bottom."""
    im, d = canvas()
    paste_logo(im)

    UNSCII_16.draw_text_centered(d, "BASE", 28)
    layer_dots(d, 22, 54, active_index=0)

    # Modifier dots row - 6 px dots + small letter label
    mods_dots(d, 12, 72, {"shift": True}, size=6, gap=8, label_below=True)

    # BLE small
    UNSCII_8.draw_text_centered(d, "BLE 2", 100)
    UNSCII_8.draw_text_centered(d, "78 WPM", 112)

    # Batteries stacked bottom
    battery_niceview_labelled(d, 15, 128, 87, "L")
    battery_niceview_labelled(d, 15, 144, 92, "R")

    save(im, "v7b_dot_mods")


def v7c_tile_mods():
    """Modifier as small rectangular tiles (filled=held). No letter."""
    im, d = canvas()
    paste_logo(im)

    UNSCII_16.draw_text_centered(d, "BASE", 28)
    layer_dots(d, 22, 54, active_index=0)

    # 4 modifier tiles, no letter labels - user learns order (S/C/A/W left→right)
    mods_bar_tiles(d, 4, 72, {"shift": True, "alt": True}, tile_w=13, tile_h=10, gap=3)
    # Legend micro-label below
    UNSCII_8.draw_text(d, "s c a w", 6, 84)

    UNSCII_8.draw_text_centered(d, "BLE 2", 100)
    UNSCII_8.draw_text_centered(d, "78 WPM", 112)

    battery_niceview_labelled(d, 15, 128, 87, "L")
    battery_niceview_labelled(d, 15, 144, 92, "R")

    save(im, "v7c_tile_mods")


def v7d_dash_mods():
    """Ultra-minimal: modifiers are just underscores that fill when held."""
    im, d = canvas()
    paste_logo(im)

    UNSCII_16.draw_text_centered(d, "BASE", 28)
    layer_dots(d, 22, 54, active_index=0)

    # Dashes - 4 slots, empty = thin line, held = thick bar
    mods_dashes(d, 8, 72, {"shift": True, "gui": True}, gap=4)

    UNSCII_8.draw_text_centered(d, "BLE 2", 88)
    UNSCII_8.draw_text_centered(d, "78 WPM", 100)

    battery_niceview_labelled(d, 15, 120, 87, "L")
    battery_niceview_labelled(d, 15, 136, 92, "R")

    save(im, "v7d_dash_mods")


def v7e_no_mods_niceview_purist():
    """Full nice_view purist: no mods, just layer + batteries + WPM + BLE."""
    im, d = canvas()
    paste_logo(im)

    # Layer huge center
    UNSCII_16.draw_text_centered(d, "BASE", 34)
    layer_dots(d, 22, 62, active_index=0, size=4, gap=3)

    # Big WPM
    UNSCII_16.draw_text_centered(d, "78", 84)
    UNSCII_8.draw_text_centered(d, "WPM", 104)

    # Compact BLE
    UNSCII_8.draw_text_centered(d, "BLE 2", 118)

    # Batteries at bottom
    battery_niceview_labelled(d, 15, 132, 87, "L")
    battery_niceview_labelled(d, 15, 146, 92, "R")

    save(im, "v7e_niceview_purist")


def contact_sheet_v7():
    names = [
        "v7a_horiz_bat_no_mods",
        "v7b_dot_mods",
        "v7c_tile_mods",
        "v7d_dash_mods",
        "v7e_niceview_purist",
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
    sheet.save(os.path.join(OUT, "contact_sheet_v7.png"))


def main():
    v7a_horiz_bat_no_mods()
    v7b_dot_mods()
    v7c_tile_mods()
    v7d_dash_mods()
    v7e_no_mods_niceview_purist()
    contact_sheet_v7()
    print("Done. See:", OUT)


if __name__ == "__main__":
    main()
