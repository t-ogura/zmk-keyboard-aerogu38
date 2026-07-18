#!/usr/bin/env python3
"""aerogu38 LCD mockup renderer v5 - small batteries bottom-left.

Applies v4 feedback:
- Batteries SHRUNK: ~18 px footprint, tucked into bottom-left corner.
- The freed area (top ~130 px) is dedicated to layer / mods / BLE / WPM
  which get bigger, more stylish treatments.
- Font sizes limited to {10, 12, 14, 16, 20} - the range that thresholds
  cleanly from DejaVu's TTF. Anything smaller (7-9 pt) is noisy on 1-bit.
- Horizontal-bar variant, if used, has L / R rows only 2 px apart
  (previous "tight" was still 11 px because I forgot the request).
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


def text_center(draw, y, s, ft, x_min=0, x_max=W):
    w = text_w(draw, s, ft)
    draw.text((x_min + (x_max - x_min - w) // 2, y), s, fill=0, font=ft)


def hline(draw, y, x0=0, x1=W - 1):
    draw.line([(x0, y), (x1, y)], fill=0)


# ---------- battery primitives ---------------------------------------


def battery_h_nub(draw, x, y, pct, body_w=30, body_h=8):
    draw.rectangle([x, y, x + body_w - 1, y + body_h - 1], outline=0)
    nub_h = max(3, body_h - 4)
    nub_y = y + (body_h - nub_h) // 2
    draw.rectangle([x + body_w, nub_y, x + body_w + 1, nub_y + nub_h - 1], fill=0)
    inner_w = body_w - 4
    fill_w = max(0, inner_w * pct // 100)
    if fill_w > 0:
        draw.rectangle([x + 2, y + 2, x + 2 + fill_w, y + body_h - 3], fill=0)


def battery_v_small(draw, x, y, pct, w=7, h=16):
    """Tiny vertical battery for the bottom-left slot."""
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


# ---------- layer dots -----------------------------------------------


def layer_dots(draw, x, y, active_index, count=5, size=3, gap=2):
    for i in range(count):
        cx = x + i * (size + gap)
        if i == active_index:
            draw.rectangle([cx, y, cx + size - 1, y + size - 1], fill=0)
        else:
            draw.rectangle([cx, y, cx + size - 1, y + size - 1], outline=0)


def mods_letters(draw, x, y, mods, ft):
    slots = [
        ("shift", "S", "s"),
        ("ctrl", "C", "c"),
        ("alt", "A", "a"),
        ("gui", "W", "w"),
    ]
    parts = [(hi if mods.get(k, False) else lo) for (k, hi, lo) in slots]
    draw.text((x, y), " ".join(parts), fill=0, font=ft)


# ---------- v5 mockups ----------------------------------------------


def v5a_hero_stack():
    """Small battery bottom-left, everything else stacked centrally."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 21)

    # HERO layer name
    text_center(d, 30, "BASE", f(24))
    layer_dots(d, 22, 60, active_index=0, count=5)

    hline(d, 72)

    # BLE - larger, styled as pill
    text_center(d, 78, "BLE 2", f(20))

    hline(d, 106)

    # Modifiers
    text_center(d, 111, "S c a w", f(14))

    hline(d, 132)

    # Bottom row: tiny batteries LEFT, WPM RIGHT
    battery_v_small(d, 3, 138, 87)
    d.text((11, 141), "87", fill=0, font=f(10))
    battery_v_small(d, 25, 138, 92)
    d.text((33, 141), "92", fill=0, font=f(10))
    # WPM on the right
    d.text((50, 138), "78", fill=0, font=f(14))
    d.text((50, 153), "wpm", fill=0, font=f(10))
    save(im, "v5a_hero_stack")


def v5b_center_focus():
    """Centered content column, wpm+batteries pack the bottom."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 21)

    text_center(d, 28, "BASE", f(20))
    layer_dots(d, 22, 56, active_index=0, count=5)

    hline(d, 68)

    text_center(d, 72, "S c a w", f(14))

    hline(d, 96)

    text_center(d, 100, "BLE 2", f(20))

    hline(d, 128)

    # Bottom cluster: batteries left, WPM right (small)
    battery_v_small(d, 3, 134, 87)
    d.text((11, 137), "87%", fill=0, font=f(10))
    battery_v_small(d, 3, 145, 92) if False else None
    battery_v_small(d, 32, 134, 92)
    d.text((40, 137), "92%", fill=0, font=f(10))
    d.text((3, 150), "78wpm", fill=0, font=f(10))
    save(im, "v5b_center_focus")


def v5c_footer_row():
    """Everything stacked; tiny footer row with 2 batteries + BLE + WPM."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 21)

    # Layer big
    text_center(d, 32, "BASE", f(24))
    layer_dots(d, 22, 62, active_index=0, count=5)

    hline(d, 76)

    # Mods
    text_center(d, 82, "S c a w", f(16))

    hline(d, 108)

    # BLE hero
    text_center(d, 114, "BLE 2", f(20))

    hline(d, 142)

    # Footer row: L bat | R bat | WPM
    battery_v_small(d, 2, 145, 87)
    d.text((10, 148), "87", fill=0, font=f(10))
    battery_v_small(d, 24, 145, 92)
    d.text((32, 148), "92", fill=0, font=f(10))
    d.text((46, 148), "78W", fill=0, font=f(10))
    save(im, "v5c_footer_row")


def v5d_horiz_tightened():
    """Horizontal bars but ACTUALLY touching (2 px apart)."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 21)

    text_center(d, 30, "BASE", f(24))
    layer_dots(d, 22, 60, active_index=0, count=5)

    hline(d, 72)

    text_center(d, 78, "S c a w", f(16))

    hline(d, 100)

    text_center(d, 106, "BLE 2", f(20))

    hline(d, 132)

    # Batteries at bottom - horizontal bars TOUCHING
    d.text((2, 136), "L", fill=0, font=f(10))
    battery_h_nub(d, 12, 137, 87, body_w=30, body_h=7)
    d.text((48, 136), "87", fill=0, font=f(10))

    d.text((2, 147), "R", fill=0, font=f(10))  # only 2 px below L row
    battery_h_nub(d, 12, 148, 92, body_w=30, body_h=7)
    d.text((48, 147), "92", fill=0, font=f(10))
    save(im, "v5d_horiz_tightened")


def v5e_wpm_hero():
    """Alternate flavour where WPM is the hero (typing feedback)."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 21)

    # Layer smaller top corner
    d.text((3, 25), "BASE", fill=0, font=f(16))
    layer_dots(d, 38, 32, active_index=0, count=5)

    hline(d, 46)

    # WPM as the hero element in center
    text_center(d, 54, "78", f(48))

    text_center(d, 108, "WPM", f(14))

    hline(d, 128)

    # Mods small row
    d.text((3, 132), "S c a w", fill=0, font=f(12))

    hline(d, 148)

    # Bottom compact status
    battery_v_small(d, 2, 148, 87, w=6, h=10)
    d.text((10, 150), "87", fill=0, font=f(10))
    battery_v_small(d, 24, 148, 92, w=6, h=10)
    d.text((32, 150), "92", fill=0, font=f(10))
    d.text((48, 150), "BLE2", fill=0, font=f(10))
    save(im, "v5e_wpm_hero")


def contact_sheet_v5():
    names = [
        "v5a_hero_stack",
        "v5b_center_focus",
        "v5c_footer_row",
        "v5d_horiz_tightened",
        "v5e_wpm_hero",
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
    sheet.save(os.path.join(OUT, "contact_sheet_v5.png"))


def main():
    v5a_hero_stack()
    v5b_center_focus()
    v5c_footer_row()
    v5d_horiz_tightened()
    v5e_wpm_hero()
    contact_sheet_v5()
    print("Done. See:", OUT)


if __name__ == "__main__":
    main()
