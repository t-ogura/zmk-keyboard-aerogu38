#!/usr/bin/env python3
"""v10 - re-render top designs with Spleen bitmap fonts.

Spleen (BSD-2) is a single bitmap family with matching glyph shapes at
5/8, 6/12, 8/16, 12/24, 16/32, 32/64 — one visual identity from status
text to hero display. That solves the "look drastically different at
different sizes" issue we had with mixing UNSCII 8 / UNSCII 16.

Font tiers (all bitmap - render cleanly at 1bpp):
  * FS  = Spleen 6x12   status text, small labels
  * FM  = Spleen 8x16   normal ("BLE 2", "L", "82%")
  * FL  = Spleen 12x24  section headers ("LAYER", "WPM")
  * FXL = Spleen 16x32  numeric hero ("03", "92")
"""

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
# Cozette for icon-ish characters (has some nerd-font glyphs)
FCOZ = ImageFont.truetype(os.path.join(OUT, "fonts/cozette.otb"), 13)


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


def battery_h(d, x, y, pct, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=0)
    inner_w = w - 4
    fill = max(0, inner_w * pct // 100)
    inner_top = y + 1 if h < 6 else y + 2
    inner_bot = y + h - 2 if h < 6 else y + h - 3
    if fill > 0 and inner_bot >= inner_top:
        d.rectangle([x + 2, inner_top, x + 2 + fill, inner_bot], fill=0)


def battery_h_full(d, y, pct, h=5):
    battery_h(d, 0, y, pct, W, h)


# ---------- v10 themes with Spleen ---------------------------------


def v10a_clean_stack():
    """Big BASE, mods dots row, small BLE, thin batteries, WPM."""
    im, d = canvas()
    # Logo
    im.paste(Image.open(os.path.join(os.path.dirname(OUT), "logo_portrait_68x20.png")).convert("L"), (0, 0))

    # LAYER hero at 32 px
    text_center(d, 22, "BASE", FL)
    # Layer index dots
    for i in range(5):
        cx = 22 + i * 5
        if i == 0:
            d.rectangle([cx, 52, cx + 2, 54], fill=0)
        else:
            d.rectangle([cx, 52, cx + 2, 54], outline=0)

    # Modifiers row - inverted tile when held
    row_y = 62
    for i, (k, held) in enumerate([("s", True), ("c", False), ("a", False), ("w", False)]):
        cx = 4 + i * 16
        if held:
            d.rectangle([cx, row_y, cx + 14, row_y + 14], fill=0)
            # White letter over
            tmp = Image.new("L", (10, 18), 255)
            td = ImageDraw.Draw(tmp)
            td.text((0, 0), k.upper(), fill=0, font=FM)
            inv = tmp.point(lambda v: 255 - v)
            im.paste(inv, (cx + 3, row_y - 1))
        else:
            d.text((cx + 3, row_y - 1), k, fill=0, font=FM)

    # BLE + WPM row
    d.text((4, 88), "BLE 2", fill=0, font=FM)
    d.text((40, 88), "WPM 78", fill=0, font=FM)

    # Two full-width thin batteries
    d.text((0, 118), "L 82", fill=0, font=FM)
    d.text((40, 118), "R 91", fill=0, font=FM)
    battery_h_full(d, 138, 82, h=5)
    battery_h_full(d, 148, 91, h=5)

    save(im, "v10a_clean_stack")


def v10b_module_block_spleen():
    """The Braun/module style but with Spleen fonts throughout."""
    im, d = canvas()
    im.paste(Image.open(os.path.join(os.path.dirname(OUT), "logo_portrait_68x20.png")).convert("L"), (0, 0))

    # LAYER module
    d.rectangle([2, 22, W - 3, 52], outline=0)
    text_center(d, 22, "LAYER", FS, x_min=2, x_max=W - 3)
    text_center(d, 30, "03", FL, x_min=2, x_max=W - 3)

    # BLE + WPM module
    d.rectangle([2, 55, W - 3, 79], outline=0)
    d.text((6, 58), "BLE 2", fill=0, font=FM)
    d.text((6, 66), "WPM 78", fill=0, font=FS)

    # Battery module
    d.rectangle([2, 82, W - 3, 130], outline=0)
    d.text((6, 84), "L 82%", fill=0, font=FS)
    battery_h(d, 6, 96, 82, w=54, h=6)
    d.text((6, 106), "R 91%", fill=0, font=FS)
    battery_h(d, 6, 118, 91, w=54, h=6)

    # Mods module
    d.rectangle([2, 133, W - 3, 158], outline=0)
    for i, (k, held) in enumerate([("s", True), ("c", False), ("a", False), ("w", False)]):
        cx = 6 + i * 15
        if held:
            d.rectangle([cx, 138, cx + 12, 152], fill=0)
            tmp = Image.new("L", (10, 18), 255)
            td = ImageDraw.Draw(tmp)
            td.text((0, 0), k.upper(), fill=0, font=FM)
            inv = tmp.point(lambda v: 255 - v)
            im.paste(inv, (cx + 2, 137))
        else:
            d.text((cx + 2, 137), k, fill=0, font=FM)

    save(im, "v10b_module")


def v10c_essential_line_spleen():
    """The 10 essential-line style with Spleen. Very minimal."""
    im, d = canvas()
    im.paste(Image.open(os.path.join(os.path.dirname(OUT), "logo_portrait_68x20.png")).convert("L"), (0, 0))

    # Diagonal accent top-right
    for i in range(20):
        d.point((W - 1 - i, 22 + i), fill=0)

    text_center(d, 28, "LAYER", FS)
    text_center(d, 38, "03", FL)

    # BT + WPM inline
    d.text((6, 70), "BLE 2", fill=0, font=FM)
    d.text((42, 70), "WPM78", fill=0, font=FS)

    # Batteries: thin single-line entries
    d.text((0, 96), "L 82%", fill=0, font=FS)
    d.line([(30, 100), (W - 1, 100)], fill=0)
    fill_x = 30 + (W - 30) * 82 // 100
    d.rectangle([30, 98, fill_x, 102], fill=0)

    d.text((0, 108), "R 91%", fill=0, font=FS)
    d.line([(30, 112), (W - 1, 112)], fill=0)
    fill_x = 30 + (W - 30) * 91 // 100
    d.rectangle([30, 110, fill_x, 114], fill=0)

    # Mods dots row
    for i, (k, held) in enumerate([("s", True), ("c", False), ("a", False), ("w", False)]):
        cx = 6 + i * 14
        if held:
            d.ellipse([cx, 128, cx + 6, 134], fill=0)
        else:
            d.ellipse([cx, 128, cx + 6, 134], outline=0)
        d.text((cx - 1, 138), k, fill=0, font=FS)

    # Diagonal accent bottom-left
    for i in range(20):
        d.point((i, 158 - i), fill=0)

    save(im, "v10c_essential")


def v10d_watch_hero():
    """Big hero WPM like Apple Watch Ultra, using Spleen 16x32."""
    im, d = canvas()
    im.paste(Image.open(os.path.join(os.path.dirname(OUT), "logo_portrait_68x20.png")).convert("L"), (0, 0))

    # LAYER top
    text_center(d, 22, "LAYER 03", FS)

    # WPM MASSIVE center
    text_center(d, 34, "92", FXL)
    text_center(d, 70, "WPM", FS)

    # BT small
    text_center(d, 86, "BLE 2", FS)

    # Modifiers
    for i, (k, held) in enumerate([("s", True), ("c", False), ("a", False), ("w", False)]):
        cx = 6 + i * 14
        if held:
            d.ellipse([cx, 100, cx + 8, 108], fill=0)
        else:
            d.ellipse([cx, 100, cx + 8, 108], outline=0)

    # Batteries
    d.text((0, 118), "L 82%", fill=0, font=FS)
    d.text((40, 118), "R 91%", fill=0, font=FS)
    battery_h_full(d, 132, 82, h=4)
    battery_h_full(d, 140, 91, h=4)

    save(im, "v10d_watch_hero")


def v10e_niceview_inspired():
    """nice_view-inspired: layer + WPM sparkline + batteries."""
    im, d = canvas()
    im.paste(Image.open(os.path.join(os.path.dirname(OUT), "logo_portrait_68x20.png")).convert("L"), (0, 0))

    # LAYER 03 hero
    text_center(d, 22, "BASE", FL)

    # BLE + WPM inline
    d.text((2, 52), "BLE 2", fill=0, font=FS)
    d.text((40, 52), "78 WPM", fill=0, font=FS)

    # Modifiers ratchet
    for i, (k, held) in enumerate([("s", True), ("c", False), ("a", False), ("w", False)]):
        cx = 4 + i * 16
        if held:
            d.rectangle([cx, 70, cx + 14, 84], fill=0)
            tmp = Image.new("L", (10, 18), 255)
            td = ImageDraw.Draw(tmp)
            td.text((0, 0), k.upper(), fill=0, font=FM)
            inv = tmp.point(lambda v: 255 - v)
            im.paste(inv, (cx + 3, 69))
        else:
            d.text((cx + 3, 69), k, fill=0, font=FM)

    # WPM sparkline (10 tiny bars)
    d.text((2, 92), "wpm", fill=0, font=FS)
    heights = [3, 5, 4, 6, 3, 5, 7, 4, 5, 6]
    for i, hh in enumerate(heights):
        d.rectangle([26 + i * 4, 100 - hh, 28 + i * 4, 100], fill=0)

    # Batteries
    d.text((0, 118), "L 82%", fill=0, font=FS)
    d.text((40, 118), "R 91%", fill=0, font=FS)
    battery_h_full(d, 132, 82, h=4)
    battery_h_full(d, 138, 91, h=4)

    save(im, "v10e_niceview")


def contact_sheet_v10():
    names = [
        "v10a_clean_stack",
        "v10b_module",
        "v10c_essential",
        "v10d_watch_hero",
        "v10e_niceview",
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
    sheet.save(os.path.join(OUT, "contact_sheet_v10.png"))


def main():
    v10a_clean_stack()
    v10b_module_block_spleen()
    v10c_essential_line_spleen()
    v10d_watch_hero()
    v10e_niceview_inspired()
    contact_sheet_v10()
    print("Done. See:", OUT)


if __name__ == "__main__":
    main()
