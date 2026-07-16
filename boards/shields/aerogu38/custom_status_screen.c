/*
 * SPDX-License-Identifier: MIT
 *
 * *** DEBUG BUILD (dev/lcd-debug-ls013 branch only) ***
 *
 * Drives an LS013B7DH05 (144 x 168 portrait) as a stand-in for the
 * LS011B7DH03 (160 x 68 landscape) while the real panel is being
 * replaced.
 *
 * NOTE ON ROTATION:
 * LVGL v9 has lv_display_set_rotation() but Zephyr's LVGL monochrome
 * display glue (lvgl_display_mono.c) does not rotate the flush buffer,
 * so setting rotation only shifts logical coordinates while the pixels
 * still get placed at raw x/y on the panel. That produces garbled or
 * blank output on Sharp Memory LCDs. Until that glue grows a rotation
 * path, we keep the panel in native portrait orientation.
 *
 * Effective UI area is therefore 144 x 68 (top-left) - the widest that
 * fits without wrapping. status_ui.c still targets 160 x 68, so the
 * leftmost and rightmost 8 px of any centered widget get clipped by
 * LVGL. That's acceptable for layout / feature checks; the LS011 build
 * on feat/peripheral-lcd-ls011b7dh03 renders the full 160 without
 * clipping.
 *
 * NEVER MERGE THIS FILE INTO feat/peripheral-lcd-ls011b7dh03 or main.
 */

#include <lvgl.h>

#include "status_ui.h"

/* LS013 native resolution. The 160 x 68 LS011 target does not fit in
 * width (160 > 144), so we clip the virt area to 144 x 68 - the widest
 * possible while keeping the coordinate system compatible. */
#define AEROGU38_UI_W 144  /* clipped from 160 */
#define AEROGU38_UI_H 68

lv_obj_t *zmk_display_status_screen(void) {
    lv_obj_t *screen = lv_obj_create(NULL);
    lv_obj_set_style_pad_all(screen, 0, 0);
    lv_obj_set_style_bg_color(screen, lv_color_black(), 0);
    lv_obj_set_style_bg_opa(screen, LV_OPA_COVER, 0);
    lv_obj_clear_flag(screen, LV_OBJ_FLAG_SCROLLABLE);

    /* Virtual LS011 area at top-left. status_ui.c paints it white and
     * places the logo inside - clipped to 144 wide (loses 8 px on each
     * side of the centered logo). */
    lv_obj_t *virt = lv_obj_create(screen);
    lv_obj_remove_style_all(virt);
    lv_obj_set_size(virt, AEROGU38_UI_W, AEROGU38_UI_H);
    lv_obj_align(virt, LV_ALIGN_TOP_LEFT, 0, 0);
    lv_obj_set_style_clip_corner(virt, true, 0);
    lv_obj_add_flag(virt, LV_OBJ_FLAG_OVERFLOW_VISIBLE);  /* no-op if clip is via size */

    aerogu38_status_ui_build(virt);

    return screen;
}
