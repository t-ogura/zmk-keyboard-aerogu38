#!/usr/bin/env python3
"""aerogu38 LCD mockup renderer v6 - accurate UNSCII, no dividers, refined.

Improvements from v5:
- Uses actual lv_font_unscii_8.c / lv_font_unscii_16.c bitmaps loaded
  by unscii_loader.py. What you see is what the LCD will draw.
- No horizontal divider lines - relies on whitespace grouping (per feedback:
  they read as clutter).
- BLE label demoted from a hero to a footer element.
- Modifier treatment: held modifiers get an inverted black tile, idle
  modifiers show a dim letter, so state changes are unmistakable
  without a font swap.
- Layout variations lean into the freed-up whitespace with different
  compositional balance (centered / left-aligned / grouped).
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


def draw_char_inverted(im, d, ch, x, y, font):
    """Draw a UNSCII glyph with inverted colours: black bg tile, white glyph."""
    adv = font.entries[ord(ch) - 32 + 1]["adv_w"] // 16
    lh = font.line_height
    d.rectangle([x, y, x + adv, y + lh], fill=0)
    # Draw glyph normally into a temp buffer, then paste inverted
    tmp = Image.new("L", (adv + 2, lh + 2), 255)
    td = ImageDraw.Draw(tmp)
    font.draw_char(td, ch, 0, 0)
    inv = tmp.point(lambda v: 255 - v)
    im.paste(inv, (x, y))
    return adv


def mods_creative(im, d, x, y, mods, font):
    """4 slots. Held mods = inverted tile. Idle = plain letter with a dot."""
    letters = [("shift", "S"), ("ctrl", "C"), ("alt", "A"), ("gui", "W")]
    cur = x
    for key, ch in letters:
        if mods.get(key, False):
            adv = draw_char_inverted(im, d, ch, cur, y, font)
        else:
            adv = font.draw_char(d, ch.lower(), cur, y)
        cur += adv + 2   # 2 px gap between slots


def battery_v_small(d, x, y, pct, w=7, h=16):
    nub_w = max(3, w - 4)
    nub_x = x + (w - nub_w) // 2
    d.rectangle([nub_x, y, nub_x + nub_w - 1, y + 1], fill=0)
    body_y = y + 2
    d.rectangle([x, body_y, x + w - 1, body_y + h - 1], outline=0)
    inner_h = h - 4
    fill_h = int(inner_h * pct / 100)
    if fill_h > 0:
        d.rectangle(
            [x + 2, body_y + h - 2 - fill_h, x + w - 3, body_y + h - 3], fill=0
        )


def layer_dots(d, x, y, active_index, count=5, size=3, gap=2):
    for i in range(count):
        cx = x + i * (size + gap)
        if i == active_index:
            d.rectangle([cx, y, cx + size - 1, y + size - 1], fill=0)
        else:
            d.rectangle([cx, y, cx + size - 1, y + size - 1], outline=0)


def paste_logo(im):
    im.paste(load_logo(), (0, 0))


# ---------- v6 mockups ----------------------------------------------


def v6a_clean_center():
    """Centered, roomy whitespace, no dividers, inverted-mod tiles."""
    im, d = canvas()
    paste_logo(im)

    # BASE hero centered around y=34
    UNSCII_16.draw_text_centered(d, "BASE", 30)
    layer_dots(d, 22, 58, active_index=0)

    # Modifiers, big-ish letters at 8 px with visible tile state
    mods_creative(im, d, 8, 78, {"shift": True}, UNSCII_16)

    # BLE small, unobtrusive
    UNSCII_8.draw_text_centered(d, "BLE 2", 108)

    # Footer: batteries left, WPM right
    battery_v_small(d, 2, 138, 87)
    UNSCII_8.draw_text(d, "87", 10, 141)
    battery_v_small(d, 24, 138, 92)
    UNSCII_8.draw_text(d, "92", 32, 141)
    UNSCII_8.draw_text(d, "78W", 48, 141)

    save(im, "v6a_clean_center")


def v6b_left_aligned():
    """Everything left-aligned; vertical rhythm from spacing only."""
    im, d = canvas()
    paste_logo(im)

    UNSCII_16.draw_text(d, "BASE", 4, 28)
    layer_dots(d, 4, 54, active_index=0)

    mods_creative(im, d, 4, 74, {"shift": True, "alt": True}, UNSCII_16)

    UNSCII_8.draw_text(d, "BLE 2", 4, 108)
    UNSCII_8.draw_text(d, "78 WPM", 4, 122)

    # Footer: batteries stacked at very bottom
    battery_v_small(d, 2, 138, 87)
    UNSCII_8.draw_text(d, "87", 10, 141)
    battery_v_small(d, 24, 138, 92)
    UNSCII_8.draw_text(d, "92", 32, 141)

    save(im, "v6b_left_aligned")


def v6c_grouped_clusters():
    """Group related info with proximity, separate with whitespace only."""
    im, d = canvas()
    paste_logo(im)

    # Group 1: layer identity
    UNSCII_16.draw_text_centered(d, "BASE", 28)
    layer_dots(d, 22, 52, active_index=0)

    # Group 2 (space before): modifiers
    mods_creative(im, d, 8, 74, {"shift": True}, UNSCII_16)

    # Group 3 (space before): connection + speed - same visual weight
    UNSCII_8.draw_text_centered(d, "BLE 2", 100)
    UNSCII_16.draw_text_centered(d, "78", 112)
    UNSCII_8.draw_text_centered(d, "WPM", 132)

    # Footer: tiny batteries only, one line
    battery_v_small(d, 2, 143, 87)
    UNSCII_8.draw_text(d, "87", 10, 146)
    battery_v_small(d, 34, 143, 92)
    UNSCII_8.draw_text(d, "92", 42, 146)

    save(im, "v6c_grouped_clusters")


def v6d_stylish_asymmetric():
    """Deliberate asymmetric composition: BIG BASE, side info column."""
    im, d = canvas()
    paste_logo(im)

    # BASE left-aligned, huge for a wide asymmetric feel
    UNSCII_16.draw_text(d, "BASE", 2, 28)
    layer_dots(d, 44, 32, active_index=0, size=2, gap=2)

    # Modifiers stacked on right, small: idle = lowercase, held = inverted
    y0 = 54
    letters = [("shift", "S"), ("ctrl", "C"), ("alt", "A"), ("gui", "W")]
    mods = {"shift": True, "alt": True}
    for i, (key, ch) in enumerate(letters):
        row_y = y0 + i * 10
        if mods.get(key, False):
            draw_char_inverted(im, d, ch, 48, row_y, UNSCII_8)
        else:
            UNSCII_8.draw_char(d, ch.lower(), 48, row_y)

    # Left column: BLE + WPM stacked, small
    UNSCII_8.draw_text(d, "BLE 2", 2, 60)
    UNSCII_8.draw_text(d, "78WPM", 2, 74)

    # Bottom row: batteries at left
    battery_v_small(d, 2, 138, 87)
    UNSCII_8.draw_text(d, "87", 10, 141)
    battery_v_small(d, 34, 138, 92)
    UNSCII_8.draw_text(d, "92", 42, 141)

    save(im, "v6d_asymmetric")


def v6e_giant_layer_only():
    """Ultra-minimal: layer name is 99% of the screen. Everything else 1 line."""
    im, d = canvas()
    paste_logo(im)

    # BASE dominates
    UNSCII_16.draw_text_centered(d, "BASE", 40)
    layer_dots(d, 22, 68, active_index=0, size=3, gap=3)

    # Modifiers below
    mods_creative(im, d, 8, 88, {"shift": True, "gui": True}, UNSCII_16)

    # Single info footer at bottom
    battery_v_small(d, 2, 138, 87)
    UNSCII_8.draw_text(d, "87", 10, 141)
    battery_v_small(d, 24, 138, 92)
    UNSCII_8.draw_text(d, "92", 32, 141)
    UNSCII_8.draw_text(d, "BLE2", 48, 141)

    save(im, "v6e_giant_layer")


def contact_sheet_v6():
    names = [
        "v6a_clean_center",
        "v6b_left_aligned",
        "v6c_grouped_clusters",
        "v6d_asymmetric",
        "v6e_giant_layer",
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
    sheet.save(os.path.join(OUT, "contact_sheet_v6.png"))


def main():
    v6a_clean_center()
    v6b_left_aligned()
    v6c_grouped_clusters()
    v6d_stylish_asymmetric()
    v6e_giant_layer_only()
    contact_sheet_v6()
    print("Done. See:", OUT)


if __name__ == "__main__":
    main()
