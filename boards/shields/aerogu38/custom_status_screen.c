/*
 * SPDX-License-Identifier: MIT
 *
 * Peripheral-side status screen for aerogu38.
 * Phase 1: render the Aerogu logo centered on the 160x68 Sharp Memory LCD.
 * Future phases will add relayed central state (layer, batteries, profile).
 */

#include <lvgl.h>

extern const lv_image_dsc_t aerogu_logo;

lv_obj_t *zmk_display_status_screen(void) {
    lv_obj_t *screen = lv_obj_create(NULL);
    lv_obj_set_style_pad_all(screen, 0, 0);
    lv_obj_set_style_bg_color(screen, lv_color_white(), 0);
    lv_obj_set_style_bg_opa(screen, LV_OPA_COVER, 0);

    lv_obj_t *img = lv_image_create(screen);
    lv_image_set_src(img, &aerogu_logo);
    lv_obj_align(img, LV_ALIGN_CENTER, 0, 0);

    return screen;
}
