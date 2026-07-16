/*
 * SPDX-License-Identifier: MIT
 *
 * See portrait_display.h for the rationale.
 *
 * Bit-format matrix (learned the hard way during Phase 0 diagnostics):
 *
 *   LVGL v9 draw buffer for LV_COLOR_FORMAT_I1:
 *     - 8 bytes of I1 palette at the head of the buffer
 *     - pixels packed 1bpp, MSB-first per byte (pixel x=0 in bit 7)
 *     - bit=1 renders as WHITE on this display; bit=0 as BLACK
 *
 *   Sharp Memory LCD (ls0xx driver):
 *     - MONO01: bit=1 = pixel OFF (white), bit=0 = pixel ON (black)
 *     - screen_info has no MONO_MSB_FIRST -> LSB-first per byte
 *     - SPI transfer configured with SPI_TRANSFER_LSB -> pixel x=0 in bit 0
 *
 * Color polarity happens to match (both use "1 = white, 0 = black"),
 * so no inversion is needed. But the bit order within each byte is
 * opposite (MSB-first vs LSB-first), which showed up in earlier tests
 * as ~8-pixel bands with mirror-reflected content. The rotation loop
 * below reads bits from LVGL in MSB-first order and writes them to the
 * native buffer in LSB-first order, which handles the reversal in the
 * same pass as the 90 degree rotation.
 */

#include "portrait_display.h"

#include <string.h>
#include <lvgl.h>
#include <lvgl_display.h>       /* provides lvgl_rounder_cb_mono decl */
#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/display.h>

#define BYTES_PER_LINE      (PORTRAIT_NATIVE_W / 8)   /* 20 */
#define NATIVE_BUF_BYTES    (BYTES_PER_LINE * PORTRAIT_NATIVE_H)  /* 1360 */

static uint8_t native_buf[NATIVE_BUF_BYTES] __aligned(4);

/*
 * LVGL rendering buffer sized for portrait (68 wide, 160 tall). Provided
 * to lv_display_set_buffers() so LVGL recomputes stride from the new
 * width; using our own buffer sidesteps the ordering trap of
 * lv_display_get_buf_active() returning NULL before the first render.
 *
 *   stride = ceil(68 / 8) = 9 bytes
 *   pixels = 9 * 160     = 1440 bytes
 *   + 8-byte palette head = 1448
 */
#define PORTRAIT_LVGL_STRIDE_BYTES ((PORTRAIT_LOGICAL_W + 7) / 8)
#define PORTRAIT_LVGL_PIXEL_BYTES  (PORTRAIT_LVGL_STRIDE_BYTES * PORTRAIT_LOGICAL_H)
#define PORTRAIT_LVGL_BUF_BYTES    (PORTRAIT_LVGL_PIXEL_BYTES + 8)

static uint8_t lvgl_portrait_buf[PORTRAIT_LVGL_BUF_BYTES] __aligned(8);

static const struct device *lcd_dev;

/*
 * Force every LVGL flush to cover the whole logical screen. Sharp
 * Memory LCD writes are whole-line: any rotated sub-region would land
 * as full native lines anyway, so it is simpler and cheaper to redraw
 * the entire panel each time (still only ~1.4 KB over SPI at 1 MHz).
 */
static void portrait_rounder_cb(lv_event_t *e) {
    lv_area_t *area = lv_event_get_param(e);
    area->x1 = 0;
    area->y1 = 0;
    area->x2 = PORTRAIT_LOGICAL_W - 1;
    area->y2 = PORTRAIT_LOGICAL_H - 1;
}

/*
 * Flush callback: rotate LVGL's 68x160 logical framebuffer into the
 * 160x68 native panel buffer, translating bit-order at the same time.
 *
 *   90 degree CCW: logical (x, y) -> native (y, LOGICAL_W - 1 - x)
 *
 * LVGL bit=0 (black on LCD) -> clear the native bit
 * LVGL bit=1 (white on LCD) -> leave native bit as 1 (pre-filled)
 */
static void portrait_flush_cb(lv_display_t *disp, const lv_area_t *area, uint8_t *px_map) {
    int src_w = area->x2 - area->x1 + 1;
    int src_h = area->y2 - area->y1 + 1;

    /* All-white the native buffer (MONO01 LSB-first: every bit set). */
    memset(native_buf, 0xFF, sizeof(native_buf));

    /* Skip LVGL's 8-byte I1 palette header. */
    const uint8_t *src = px_map + 8;
    const int src_stride_bytes = (src_w + 7) / 8;

    /* 90 CCW rotation: logical (x, y) -> native (y, LOGICAL_W - 1 - x).
     * LVGL packs bits MSB-first per byte; ls0xx expects LSB-first per
     * byte. We do both mappings together in this pass. */
    for (int y = 0; y < src_h; y++) {
        const uint8_t *row = src + y * src_stride_bytes;
        int abs_y = y + area->y1;
        for (int x = 0; x < src_w; x++) {
            uint8_t src_bit = (row[x / 8] >> (7 - (x % 8))) & 0x01;
            if (src_bit) {
                continue;   /* white - leave native pixel at 1 */
            }
            int abs_x = x + area->x1;
            int native_x = abs_y;
            int native_y = (PORTRAIT_LOGICAL_W - 1) - abs_x;
            if (native_x < 0 || native_x >= PORTRAIT_NATIVE_W ||
                native_y < 0 || native_y >= PORTRAIT_NATIVE_H) {
                continue;
            }
            int byte_idx = native_y * BYTES_PER_LINE + (native_x / 8);
            uint8_t mask = (uint8_t)(0x01 << (native_x % 8));
            native_buf[byte_idx] &= (uint8_t)~mask;
        }
    }

    struct display_buffer_descriptor desc = {
        .buf_size = NATIVE_BUF_BYTES,
        .width    = PORTRAIT_NATIVE_W,
        .height   = PORTRAIT_NATIVE_H,
        .pitch    = PORTRAIT_NATIVE_W,
    };
    (void)display_write(lcd_dev, 0, 0, &desc, native_buf);

    lv_display_flush_ready(disp);
}

void portrait_display_init(void) {
    lv_display_t *disp = lv_display_get_default();
    if (!disp) {
        return;
    }

    lcd_dev = DEVICE_DT_GET(DT_CHOSEN(zephyr_display));

    /* Swap to portrait. All widget positioning is now in
     * (0..LOGICAL_W-1, 0..LOGICAL_H-1). */
    lv_display_set_resolution(disp, PORTRAIT_LOGICAL_W, PORTRAIT_LOGICAL_H);

    /* Re-affirm I1 color format. Zephyr set this at init but resolution
     * changes can perturb internal caches; being explicit is cheap. */
    lv_display_set_color_format(disp, LV_COLOR_FORMAT_I1);

    /* IMPORTANT: FULL render mode is required, not PARTIAL. When we
     * hand LVGL our own buffer for a display whose rotation-aware
     * flush cb bypasses Zephyr's mono glue, PARTIAL rendering
     * silently produces empty frames (buffer stays at BSS zeros).
     * FULL mode always renders the entire screen every frame - a
     * non-issue at 68x160 mono, and it makes the render path
     * deterministic.
     *
     * Buffer sizing: stride 9 * height 160 = 1440 pixel bytes,
     * plus the 8-byte I1 palette header = 1448 bytes total. */
    lv_display_set_buffers(disp, lvgl_portrait_buf, NULL,
                           sizeof(lvgl_portrait_buf),
                           LV_DISPLAY_RENDER_MODE_FULL);

    /* Replace Zephyr's native-width rounder with a logical-full-screen
     * rounder (native rounder would clamp x to (0..NATIVE_W-1) which
     * is outside the portrait logical space). */
    (void)lv_display_remove_event_cb_with_user_data(disp, lvgl_rounder_cb_mono, disp);
    lv_display_add_event_cb(disp, portrait_rounder_cb,
                            LV_EVENT_INVALIDATE_AREA, NULL);

    /* Replace Zephyr's mono flush cb with our rotate + bit-order
     * translating one. */
    lv_display_set_flush_cb(disp, portrait_flush_cb);
}
