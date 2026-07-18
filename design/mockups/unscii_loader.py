"""Load LVGL's lv_font_unscii_8.c and lv_font_unscii_16.c as pixel data.

Renders glyphs to a PIL image at exact 1bpp fidelity so the mockups
match what the LVGL build shows on the LCD.
"""

import os
import re
from PIL import Image, ImageDraw

LVGL_FONT_DIR = "/home/ogu/workspace/aerogu34/zmk-workspace/modules/lib/gui/lvgl/src/font"


class UnsciiFont:
    def __init__(self, path, line_height):
        src = open(path).read()

        m = re.search(r"glyph_bitmap\[\]\s*=\s*\{(.*?)\};", src, re.DOTALL)
        self.bytes = [int(x, 16) for x in re.findall(r"0x([0-9a-fA-F]+)", m.group(1))]

        m = re.search(r"glyph_dsc\[\]\s*=\s*\{(.*?)\};", src, re.DOTALL)
        self.entries = []
        for m2 in re.finditer(r"\{[^{}]+\}", m.group(1)):
            fields = {}
            for f in re.finditer(r"\.(\w+)\s*=\s*(-?\d+)", m2.group(0)):
                fields[f.group(1)] = int(f.group(2))
            self.entries.append(fields)

        self.line_height = line_height

    def glyph(self, ch):
        idx = ord(ch) - 32 + 1
        if idx < 1 or idx >= len(self.entries):
            return None
        return self.entries[idx]

    def draw_char(self, draw_img, ch, x, y):
        """Return advance width in px. Draws at (x, y) top-left position."""
        g = self.glyph(ch)
        if g is None:
            return 0
        bw, bh = g["box_w"], g["box_h"]
        ox, oy = g["ofs_x"], g["ofs_y"]
        adv = g["adv_w"] // 16
        bmp_idx = g["bitmap_index"]
        # LVGL 1bpp glyph bitmap is a continuous bit stream (no per-row
        # byte alignment). Bit N = pixel at (N%bw, N//bw), MSB-first per byte.
        top = y + (self.line_height - oy - bh)
        for row in range(bh):
            for col in range(bw):
                bit_pos = row * bw + col
                b = self.bytes[bmp_idx + bit_pos // 8]
                if (b >> (7 - (bit_pos % 8))) & 1:
                    draw_img.point((x + ox + col, top + row), fill=0)
        return adv

    def measure(self, s):
        w = 0
        for ch in s:
            g = self.glyph(ch)
            if g:
                w += g["adv_w"] // 16
        return w

    def draw_text(self, draw_img, s, x, y):
        cur = x
        for ch in s:
            cur += self.draw_char(draw_img, ch, cur, y)
        return cur - x

    def draw_text_centered(self, draw_img, s, y, x_min=0, x_max=68):
        w = self.measure(s)
        self.draw_text(draw_img, s, x_min + (x_max - x_min - w) // 2, y)


UNSCII_8 = UnsciiFont(os.path.join(LVGL_FONT_DIR, "lv_font_unscii_8.c"), 9)
UNSCII_16 = UnsciiFont(os.path.join(LVGL_FONT_DIR, "lv_font_unscii_16.c"), 17)


if __name__ == "__main__":
    # Test render
    im = Image.new("L", (68, 40), 255)
    d = ImageDraw.Draw(im)
    UNSCII_8.draw_text(d, "Hello 87%", 2, 2)
    UNSCII_16.draw_text(d, "BASE", 2, 12)
    bw = im.point(lambda v: 0 if v < 128 else 255, mode="1")
    bw.convert("L").resize((68 * 8, 40 * 8), Image.NEAREST).save("/tmp/unscii_test.png")
    print("wrote /tmp/unscii_test.png")
