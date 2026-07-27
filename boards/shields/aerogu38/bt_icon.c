/* SPDX-License-Identifier: MIT
 *
 * 9x9 Bluetooth glyph for the notification panel UI.
 *
 * ....#....
 * ....##...
 * ..#.#.#..
 * ...####..
 * ....##...
 * ...####..
 * ..#.#.#..
 * ....##...
 * ....#....
 */
#include <lvgl.h>

#ifndef LV_ATTRIBUTE_MEM_ALIGN
#define LV_ATTRIBUTE_MEM_ALIGN
#endif
#ifndef LV_ATTRIBUTE_LARGE_CONST
#define LV_ATTRIBUTE_LARGE_CONST
#endif

static const LV_ATTRIBUTE_MEM_ALIGN LV_ATTRIBUTE_LARGE_CONST uint8_t bt_icon_map[] = {
    /* Palette (I1): idx 0 = white, idx 1 = black */
    0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0xff,

    /* 9 rows * 2 bytes/row = 18 bytes, MSB-first, bit8 in byte1 high bit */
    0x08, 0x00,   /* ....#.... */
    0x0c, 0x00,   /* ....##... */
    0x2a, 0x00,   /* ..#.#.#.. */
    0x1e, 0x00,   /* ...####.. */
    0x0c, 0x00,   /* ....##... */
    0x1e, 0x00,   /* ...####.. */
    0x2a, 0x00,   /* ..#.#.#.. */
    0x0c, 0x00,   /* ....##... */
    0x08, 0x00,   /* ....#.... */
};

const lv_image_dsc_t bt_icon = {
    .header.cf = LV_COLOR_FORMAT_I1,
    .header.w = 9,
    .header.h = 9,
    .data_size = 26,
    .data = bt_icon_map,
};
