/*
 * SPDX-License-Identifier: MIT
 *
 * *** DEBUG BUILD (dev/lcd-debug-ls013 branch only) ***
 *
 * Drives an LS013B7DH05 (144 x 168) as if it were an LS011B7DH03
 * (160 x 68) so UI code targeting the real panel can be developed on
 * beekeeb's readily-available Toucan-style breakout.
 *
 * The physical panel is used in landscape: LVGL is rotated 90 degrees,
 * giving a 168 x 144 canvas. Inside that canvas a 160 x 68 "virtual
 * LS011" object is placed at the top-left corner; everything else is
 * painted black so the target area is unmistakable to the eye. UI code
 * (status_ui.c) is called with that 160x68 object as its parent, so
 * the exact same pixels land on either target.
 *
 * NEVER MERGE THIS FILE INTO feat/peripheral-lcd-ls011b7dh03 or main.
 * The production wrapper on the feat branch is much simpler and does
 * not touch rotation or backgrounds.
 */

#include <lvgl.h>

#include "status_ui.h"

#define AEROGU38_UI_W 160
#define AEROGU38_UI_H 68

lv_obj_t *zmk_display_status_screen(void) {
    /* Physical LS013 is 144x168; rotating 90 deg gives a 168x144
     * landscape canvas, which comfortably contains a 160x68 window. */
    lv_display_set_rotation(lv_display_get_default(), LV_DISPLAY_ROTATION_90);

    lv_obj_t *screen = lv_obj_create(NULL);
    lv_obj_set_style_pad_all(screen, 0, 0);
    lv_obj_set_style_bg_color(screen, lv_color_black(), 0);
    lv_obj_set_style_bg_opa(screen, LV_OPA_COVER, 0);
    lv_obj_clear_flag(screen, LV_OBJ_FLAG_SCROLLABLE);

    /* Virtual LS011 area - status_ui.c will paint this white and place
     * the logo inside, just like on real hardware. */
    lv_obj_t *virt = lv_obj_create(screen);
    lv_obj_remove_style_all(virt);
    lv_obj_set_size(virt, AEROGU38_UI_W, AEROGU38_UI_H);
    lv_obj_align(virt, LV_ALIGN_TOP_LEFT, 0, 0);

    aerogu38_status_ui_build(virt);

    return screen;
}
