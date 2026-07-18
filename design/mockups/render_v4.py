#!/usr/bin/env python3
"""aerogu38 LCD mockup renderer v4 - alphabet mods + left-anchored batteries.

Changes from v3:
- Modifier icons dropped in favour of letter labels (s/S c/C a/A w/W).
  Lowercase = not held, uppercase = held. QMK convention, always same
  width so nothing reflows.
- Vertical batteries shortened and pushed to left; right column takes
  the freed-up space for layer / mods / BLE / WPM.
- Horizontal-bar variant tightened (rows closer together).
- Active / Idle / Sleep state showcase in a single canvas.
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


def vline(draw, x, y0, y1):
    draw.line([(x, y0), (x, y1)], fill=0)


# ---------- battery primitives ---------------------------------------


def battery_h_nub(draw, x, y, pct, body_w=44, body_h=9):
    """Horizontal battery: body + nub."""
    draw.rectangle([x, y, x + body_w - 1, y + body_h - 1], outline=0)
    nub_h = max(3, body_h - 4)
    nub_y = y + (body_h - nub_h) // 2
    draw.rectangle([x + body_w, nub_y, x + body_w + 2, nub_y + nub_h - 1], fill=0)
    inner_w = body_w - 4
    fill_w = max(0, inner_w * pct // 100)
    if fill_w > 0:
        draw.rectangle([x + 2, y + 2, x + 2 + fill_w, y + body_h - 3], fill=0)


def battery_v(draw, x, y, w, h, pct):
    """Vertical battery: nub on top, body below."""
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


# ---------- alphabet-based modifier row ------------------------------


def mods_letters(draw, x, y, mods, ft):
    """
    QMK-style: always render 4 slots "s c a w".
    Uppercase when held, lowercase when not.
    """
    slots = [
        ("shift", "S", "s"),
        ("ctrl", "C", "c"),
        ("alt", "A", "a"),
        ("gui", "W", "w"),
    ]
    parts = [(hi if mods.get(k, False) else lo) for (k, hi, lo) in slots]
    draw.text((x, y), " ".join(parts), fill=0, font=ft)


# ---------- layer indicator dots -------------------------------------


def layer_dots(draw, x, y, active_index, count=5, size=3, gap=2):
    for i in range(count):
        cx = x + i * (size + gap)
        if i == active_index:
            draw.rectangle([cx, y, cx + size - 1, y + size - 1], fill=0)
        else:
            draw.rectangle([cx, y, cx + size - 1, y + size - 1], outline=0)


# ---------- v4 mockups ----------------------------------------------


def v4a_vert_left_info_right():
    """Two vertical batteries on the left, all info on the right."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 21)

    # Two vertical batteries, LEFT anchored. y=25..85 (~58 px tall)
    battery_v(d, 2, 25, w=9, h=58, pct=87)
    battery_v(d, 13, 25, w=9, h=58, pct=92)
    # Values under each
    d.text((1, 86), "87", fill=0, font=f(9))
    d.text((13, 86), "92", fill=0, font=f(9))

    # Divider between columns
    vline(d, 25, 22, 100)

    # Right column starts at x=28
    text_center(d, 24, "BASE", f(18), x_min=28, x_max=W)
    layer_dots(d, 30, 46, active_index=0, count=5)

    hline(d, 55, x0=28)
    d.text((28, 58), "mods", fill=0, font=f(7))
    mods_letters(d, 28, 68, {"shift": True}, f(9))

    hline(d, 82, x0=28)
    d.text((28, 84), "BLE 2", fill=0, font=f(12))

    # Bottom row across full width: WPM
    hline(d, 102)
    text_center(d, 106, "78 WPM", f(14))

    hline(d, 128)
    # Footer status text
    text_center(d, 132, "Aerogu38", f(8))
    text_center(d, 145, "portrait", f(7))
    save(im, "v4a_vert_left")


def v4b_vert_left_minimal():
    """Same left-anchor concept, but right column is bigger BASE + minimal."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 21)

    # Batteries full-height on left, thicker
    battery_v(d, 3, 25, w=11, h=110, pct=87)
    battery_v(d, 17, 25, w=11, h=110, pct=92)
    d.text((1, 138), "87", fill=0, font=f(9))
    d.text((15, 138), "92", fill=0, font=f(9))

    vline(d, 31, 22, 155)

    # Right column - narrower BASE size so it fits in 68-34=34 px
    text_center(d, 26, "BASE", f(14), x_min=34, x_max=W)
    layer_dots(d, 36, 44, active_index=0, count=5)

    hline(d, 54, x0=34)
    d.text((34, 58), "S c A w", fill=0, font=f(9))

    hline(d, 74, x0=34)
    d.text((34, 78), "BLE 2", fill=0, font=f(11))

    hline(d, 96, x0=34)
    d.text((34, 100), "78WPM", fill=0, font=f(10))

    hline(d, 120, x0=34)
    text_center(d, 124, "z", f(14), x_min=34, x_max=W)
    save(im, "v4b_vert_full")


def v4c_horiz_tight():
    """Horizontal bars but with much tighter row spacing."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 21)

    text_center(d, 26, "BASE", f(22))
    layer_dots(d, 22, 54, active_index=0, count=5)

    hline(d, 62)

    # Mods as letters, 9pt
    d.text((2, 66), "S c a w", fill=0, font=f(11))

    hline(d, 82)

    d.text((2, 86), "BLE 2", fill=0, font=f(14))

    hline(d, 106)

    # Batteries with TIGHT spacing (previously 16 px apart, now 11)
    d.text((2, 110), "L", fill=0, font=f(9))
    battery_h_nub(d, 12, 111, 87, body_w=34, body_h=8)
    d.text((54, 110), "87", fill=0, font=f(9))

    d.text((2, 122), "R", fill=0, font=f(9))
    battery_h_nub(d, 12, 123, 92, body_w=34, body_h=8)
    d.text((54, 122), "92", fill=0, font=f(9))

    hline(d, 138)
    text_center(d, 141, "78 WPM", f(11))
    save(im, "v4c_horiz_tight")


def v4d_states_active_idle_sleep():
    """Wide canvas showing three states side by side."""
    single_w = W * SCALE + 20
    total_w = single_w * 3 + 40
    total_h = H * SCALE + 100
    sheet = Image.new("L", (total_w, total_h), 240)
    sheet_draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype(FONT_BOLD, 22)

    # ACTIVE ------------------------------------------------------------
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 21)
    battery_v(d, 3, 26, w=10, h=48, pct=87)
    battery_v(d, 16, 26, w=10, h=48, pct=92)
    d.text((1, 77), "87", fill=0, font=f(9))
    d.text((14, 77), "92", fill=0, font=f(9))
    vline(d, 29, 22, 90)
    text_center(d, 26, "BASE", f(18), x_min=32, x_max=W)
    layer_dots(d, 35, 48, active_index=0, count=5)
    hline(d, 60, x0=32)
    d.text((32, 63), "S c A w", fill=0, font=f(9))
    hline(d, 76, x0=32)
    d.text((32, 79), "BLE 2", fill=0, font=f(11))
    hline(d, 94)
    text_center(d, 98, "78 WPM", f(14))
    hline(d, 118)
    text_center(d, 122, "typing", fill=0, ft=None) if False else None
    text_center(d, 122, "typing...", f(9))
    d.text((30, 140), "Aerogu38", fill=0, font=f(8))
    save(im, "v4d_active")
    active_x6 = Image.open(os.path.join(OUT, "v4d_active_x6.png"))

    # IDLE --------------------------------------------------------------
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 21)
    # Big centered BASE + dots + batteries only
    text_center(d, 34, "BASE", f(28))
    layer_dots(d, 22, 72, active_index=0, count=5)
    hline(d, 88)
    battery_v(d, 12, 96, w=14, h=52, pct=87)
    battery_v(d, 42, 96, w=14, h=52, pct=92)
    d.text((11, 152), "87", fill=0, font=f(9))
    d.text((41, 152), "92", fill=0, font=f(9))
    save(im, "v4d_idle")
    idle_x6 = Image.open(os.path.join(OUT, "v4d_idle_x6.png"))

    # SLEEP -------------------------------------------------------------
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    # Just logo + tiny status at very bottom
    hline(d, 148)
    d.text((3, 151), "87  92", fill=0, font=f(8))
    text_center(d, 151, "z", f(8))
    d.text((52, 151), "BLE", fill=0, font=f(7))
    save(im, "v4d_sleep")
    sleep_x6 = Image.open(os.path.join(OUT, "v4d_sleep_x6.png"))

    # Compose the 3-state showcase
    for i, (im6, label) in enumerate(
        [(active_x6, "ACTIVE"), (idle_x6, "IDLE"), (sleep_x6, "SLEEP")]
    ):
        x = 20 + i * (single_w)
        sheet.paste(im6, (x, 20))
        sheet_draw.text((x, 30 + im6.height), label, fill=0, font=label_font)
    sheet.save(os.path.join(OUT, "v4d_states.png"))


def v4e_horiz_squeezed():
    """Compact horizontal batteries with everything else squeezed above."""
    im, d = canvas()
    logo = load_logo()
    im.paste(logo, (0, 0))
    hline(d, 21)

    # Layer with even bigger name
    text_center(d, 26, "BASE", f(26))
    layer_dots(d, 22, 60, active_index=0, count=5)

    hline(d, 70)

    d.text((3, 74), "S c a w", fill=0, font=f(12))

    hline(d, 92)

    d.text((3, 96), "BLE 2", fill=0, font=f(14))
    d.text((40, 100), "78WPM", fill=0, font=f(8))

    hline(d, 120)

    # Batteries with almost NO gap between rows
    d.text((2, 124), "L", fill=0, font=f(10))
    battery_h_nub(d, 12, 125, 87, body_w=36, body_h=8)
    d.text((54, 124), "87", fill=0, font=f(10))

    d.text((2, 136), "R", fill=0, font=f(10))
    battery_h_nub(d, 12, 137, 92, body_w=36, body_h=8)
    d.text((54, 136), "92", fill=0, font=f(10))

    save(im, "v4e_horiz_squeezed")


def contact_sheet_v4():
    names = [
        "v4a_vert_left",
        "v4b_vert_full",
        "v4c_horiz_tight",
        "v4e_horiz_squeezed",
        "v4d_active",
        "v4d_idle",
        "v4d_sleep",
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
    label_font = ImageFont.truetype(FONT_BOLD, 16)
    for i, im in enumerate(imgs):
        row, col = divmod(i, per_row)
        x = gap + col * (cell_w + gap)
        y = gap + row * (cell_h + 40)
        sheet.paste(im, (x, y))
        draw.text((x, y + cell_h + 4), names[i], fill=0, font=label_font)
    sheet.save(os.path.join(OUT, "contact_sheet_v4.png"))


def main():
    v4a_vert_left_info_right()
    v4b_vert_left_minimal()
    v4c_horiz_tight()
    v4d_states_active_idle_sleep()
    v4e_horiz_squeezed()
    contact_sheet_v4()
    print("Done. See:", OUT)


if __name__ == "__main__":
    main()
