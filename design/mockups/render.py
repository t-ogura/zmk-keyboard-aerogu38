#!/usr/bin/env python3
"""aerogu38 LCD mockup renderer.

Produces 1bpp 68x160 portrait PNGs that approximate what the LVGL
build would show, plus a 6x upscaled preview for visual review.
Everything drawn here is a design mockup, not a pixel-perfect LVGL
simulation - use it to iterate on layout/hierarchy/spacing.
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 68, 160
SCALE = 6
OUT = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(os.path.dirname(OUT), "logo_portrait_68x20.png")

FONT_TTF = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

# ---------- helpers ---------------------------------------------------


def canvas():
    """New white 68x160 grayscale canvas (drawn in L, thresholded at save)."""
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


def font(size):
    return ImageFont.truetype(FONT_TTF, size)


def text_width(draw, s, f):
    bbox = draw.textbbox((0, 0), s, font=f)
    return bbox[2] - bbox[0]


def draw_text_centered(draw, y, s, f):
    w = text_width(draw, s, f)
    draw.text(((W - w) // 2, y), s, fill=0, font=f)


def hline(draw, y):
    draw.line([(0, y), (W - 1, y)], fill=0, width=1)


# ---------- widget primitives -----------------------------------------


def battery_h(draw, y, label, pct, width=52, height=8):
    """Horizontal battery: [XX%   BAR    ] left-anchored letter + bar."""
    x = 2
    draw.text((x, y), label, fill=0, font=font(10))
    bar_x = 12
    draw.rectangle([bar_x, y, bar_x + width, y + height - 1], outline=0, fill=None)
    fill_w = max(0, min(width - 2, (width - 2) * pct // 100))
    draw.rectangle([bar_x + 1, y + 1, bar_x + fill_w, y + height - 2], fill=0)
    draw.text((bar_x + width + 2, y), f"{pct}", fill=0, font=font(8))


def battery_v(draw, x, y, pct, w=8, h=42):
    """Vertical battery bar with fill from bottom, small nub on top."""
    # Nub
    draw.rectangle([x + w // 3, y - 2, x + w - w // 3, y - 1], fill=0)
    # Body outline
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=0, fill=None)
    inner_h = h - 4
    fill_h = int(inner_h * pct / 100)
    if fill_h > 0:
        draw.rectangle(
            [x + 2, y + h - 2 - fill_h, x + w - 3, y + h - 3], fill=0
        )


def mod_glyph(draw, x, y, kind, active):
    """8x8 pixel-art modifier glyph. Filled when active, outlined when not."""
    outline = 0
    fill_col = 0 if active else 255
    if kind == "shift":
        # Upward arrow like ⇧
        pts = [(4, 0), (7, 3), (5, 3), (5, 7), (2, 7), (2, 3), (0, 3)]
    elif kind == "ctrl":
        # Upward chevron ⌃
        pts = [(4, 1), (7, 4), (5, 4), (5, 5), (2, 5), (2, 4), (0, 4)]
    elif kind == "alt":
        # Diagonal branches (approx ⌥)
        draw.line([(x, y + 5), (x + 3, y + 5), (x + 6, y + 1)], fill=outline)
        draw.line([(x + 4, y + 1), (x + 7, y + 1)], fill=outline)
        if active:
            draw.line([(x + 1, y + 6), (x + 3, y + 6), (x + 5, y + 3)], fill=outline)
        return
    elif kind == "gui":
        # Command loop ⌘ - draw four little loops
        draw.rectangle([x, y, x + 7, y + 7], outline=outline, fill=fill_col)
        return
    else:
        return
    shifted = [(x + px, y + py) for (px, py) in pts]
    draw.polygon(shifted, outline=outline, fill=fill_col)


def mods_row(draw, x, y, mods_flags, spacing=13):
    """Draw 4 modifier glyphs starting at (x, y). mods_flags is dict."""
    for i, key in enumerate(["shift", "ctrl", "alt", "gui"]):
        mod_glyph(draw, x + i * spacing, y, key, mods_flags.get(key, False))


def bt_icon(draw, x, y, connected=True, size=8):
    """Small BT rune."""
    # Vertical line
    draw.line([(x + size // 2, y), (x + size // 2, y + size - 1)], fill=0)
    # Upper triangle
    draw.line([(x + size // 2, y), (x + size - 1, y + size // 4)], fill=0)
    draw.line(
        [(x + size - 1, y + size // 4), (x + size // 2, y + size // 2)], fill=0
    )
    # Lower triangle
    draw.line([(x + size // 2, y + size - 1), (x + size - 1, y + 3 * size // 4)], fill=0)
    draw.line(
        [(x + size - 1, y + 3 * size // 4), (x + size // 2, y + size // 2)], fill=0
    )


def usb_icon(draw, x, y, size=10):
    """Small USB rune."""
    draw.rectangle([x + size // 3, y + 1, x + 2 * size // 3, y + 3], outline=0)
    draw.line([(x + size // 2, y + 3), (x + size // 2, y + size - 1)], fill=0)
    draw.line([(x + size // 2 - 2, y + size // 2), (x + size // 2, y + size - 1)], fill=0)
    draw.line([(x + size // 2 + 2, y + size // 2), (x + size // 2, y + size - 1)], fill=0)


# ---------- mockups ---------------------------------------------------


def m0_current_baseline():
    """What we ship today - for A/B comparison."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 20)
    d.text((2, 23), "L 1", fill=0, font=font(14))
    d.text((2, 43), "Fn", fill=0, font=font(9))
    hline(d, 61)
    d.text((2, 66), "S - - -", fill=0, font=font(14))
    hline(d, 86)
    d.text((2, 91), "BT 2", fill=0, font=font(14))
    hline(d, 111)
    battery_h(d, 114, "L", 87)
    battery_h(d, 138, "R", 92)
    save(im, "m0_current")


def m1_layer_first():
    """Layer name dominates; everything else compresses to a status strip."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 20)

    # HUGE layer name - up to 4 chars, centered
    layer_name = "Fn"
    f_big = font(32)
    w = text_width(d, layer_name, f_big)
    d.text(((W - w) // 2, 32), layer_name, fill=0, font=f_big)

    # Thin divider before status strip
    hline(d, 88)

    # Modifier icons row (4 icons across)
    mods_row(d, 4, 92, {"shift": True, "ctrl": False, "alt": False, "gui": False}, spacing=15)

    hline(d, 105)

    # Compact BT + endpoint row
    bt_icon(d, 4, 108)
    d.text((16, 108), "2", fill=0, font=font(9))

    hline(d, 123)

    # Battery bars horizontal (compact)
    battery_h(d, 126, "L", 87)
    battery_h(d, 145, "R", 92)
    save(im, "m1_layer_first")


def m2_zones_with_symbols():
    """Distinct zones, modifier symbols get more visual weight."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 20)

    # Layer name + small BT profile on the right
    d.text((2, 24), "Fn", fill=0, font=font(24))
    d.text((44, 26), "BT", fill=0, font=font(8))
    d.text((44, 36), "  2", fill=0, font=font(11))

    hline(d, 54)

    # Modifiers - larger glyphs (12x12) spread across
    for i, k in enumerate(["shift", "ctrl", "alt", "gui"]):
        # Scale up modifier icons: draw at 2x
        px = 4 + i * 15
        py = 58
        active = (k == "shift")
        # Simple outlined circle w/ inner letter as fallback
        d.rectangle([px, py, px + 12, py + 12], outline=0, fill=0 if active else 255)
        letter = {"shift": "S", "ctrl": "C", "alt": "A", "gui": "W"}[k]
        col = 255 if active else 0
        d.text((px + 3, py + 1), letter, fill=col, font=font(10))

    hline(d, 75)

    # Batteries: side-by-side vertical bars
    battery_v(d, 12, 90, 87, w=10, h=50)
    d.text((4, 143), "L 87", fill=0, font=font(8))
    battery_v(d, 46, 90, 92, w=10, h=50)
    d.text((38, 143), "R 92", fill=0, font=font(8))
    save(im, "m2_zones_symbols")


def m3_aviation_hud():
    """Aerogu wing motif taken further - instrument-panel feel."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    # Wing chevrons under logo
    for xo in (10, 25, 40, 55):
        d.line([(xo, 22), (xo + 4, 20)], fill=0)

    d.rectangle([2, 26, W - 3, 62], outline=0)  # boxed layer
    d.text((6, 30), "LAYER", fill=0, font=font(7))
    d.text((6, 40), "Fn", fill=0, font=font(20))

    # Callsign strip
    d.rectangle([2, 66, W - 3, 84], outline=0)
    d.text((6, 68), "COMM", fill=0, font=font(7))
    d.text((6, 74), "BT 2", fill=0, font=font(10))

    # Mods = warning lights
    d.text((2, 88), "MOD", fill=0, font=font(7))
    for i, k in enumerate(["S", "C", "A", "W"]):
        cx = 6 + i * 14
        active = (i == 0)
        d.ellipse([cx, 98, cx + 8, 106], outline=0, fill=0 if active else 255)
        # small letter above
        d.text((cx + 1, 108), k, fill=0, font=font(7))

    # Fuel gauges bottom
    d.rectangle([2, 120, W - 3, 158], outline=0)
    d.text((6, 122), "FUEL", fill=0, font=font(7))
    battery_h(d, 132, "L", 87, width=44)
    battery_h(d, 145, "R", 92, width=44)
    save(im, "m3_hud")


def m4_card_dashboard():
    """Fitbit / Apple Watch complication style - each info as its own card."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))

    # Card 1: Layer name (biggest card)
    d.rectangle([2, 22, W - 3, 60], outline=0)
    d.text((5, 24), "LAYER", fill=0, font=font(6))
    d.text((5, 32), "Fn", fill=0, font=font(24))

    # Two side-by-side cards: BT and MODS
    d.rectangle([2, 63, 33, 92], outline=0)
    d.text((5, 65), "BT", fill=0, font=font(6))
    d.text((5, 72), "2", fill=0, font=font(18))

    d.rectangle([35, 63, W - 3, 92], outline=0)
    d.text((37, 65), "MOD", fill=0, font=font(6))
    d.text((37, 73), "SHFT", fill=0, font=font(9))

    # Battery card wide at bottom
    d.rectangle([2, 95, W - 3, 158], outline=0)
    d.text((5, 97), "BATT", fill=0, font=font(6))
    battery_h(d, 108, "L", 87, width=50)
    battery_h(d, 122, "R", 92, width=50)
    # Show sum? Or just tick lines
    d.text((5, 140), "avg 89", fill=0, font=font(8))
    save(im, "m4_cards")


def m5_active_vs_idle():
    """Two-state design: rich when active, quiet when idle."""
    # ACTIVE variant
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 20)
    d.text((5, 26), "Fn", fill=0, font=font(28))
    hline(d, 60)
    # Modifiers
    mods_row(d, 4, 66, {"shift": True, "ctrl": False, "alt": False, "gui": False}, spacing=15)
    hline(d, 82)
    # BT + WPM row
    bt_icon(d, 4, 86)
    d.text((16, 86), "BT 2", fill=0, font=font(10))
    d.text((44, 86), "78wpm", fill=0, font=font(7))
    hline(d, 102)
    battery_v(d, 12, 112, 87, w=10, h=42)
    d.text((4, 156), "L87", fill=0, font=font(7))
    battery_v(d, 46, 112, 92, w=10, h=42)
    d.text((38, 156), "R92", fill=0, font=font(7))
    save(im, "m5a_active")

    # IDLE variant - just logo + big status
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    # Middle: just battery pair, larger
    battery_v(d, 15, 60, 87, w=14, h=70)
    d.text((11, 133), "L 87", fill=0, font=font(9))
    battery_v(d, 42, 60, 92, w=14, h=70)
    d.text((38, 133), "R 92", fill=0, font=font(9))
    # Bottom: bt icon
    bt_icon(d, W // 2 - 4, 148)
    save(im, "m5b_idle")


def contact_sheet():
    """Compose an overview grid image with all mockups side-by-side."""
    names = [
        "m0_current",
        "m1_layer_first",
        "m2_zones_symbols",
        "m3_hud",
        "m4_cards",
        "m5a_active",
        "m5b_idle",
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
    label_font = ImageFont.truetype(FONT_TTF, 18)
    for i, im in enumerate(imgs):
        row, col = divmod(i, per_row)
        x = gap + col * (cell_w + gap)
        y = gap + row * (cell_h + 40)
        sheet.paste(im, (x, y))
        draw.text((x, y + cell_h + 4), names[i], fill=0, font=label_font)
    sheet.save(os.path.join(OUT, "contact_sheet.png"))
    print("Wrote contact_sheet.png")


def main():
    m0_current_baseline()
    m1_layer_first()
    m2_zones_with_symbols()
    m3_aviation_hud()
    m4_card_dashboard()
    m5_active_vs_idle()
    contact_sheet()
    print("Done. See:", OUT)


if __name__ == "__main__":
    main()
