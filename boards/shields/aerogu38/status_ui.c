/*
 * SPDX-License-Identifier: MIT
 *
 * Peripheral status UI content. Draws inside a caller-provided 160x68
 * parent - never touches the screen itself, so the same code paints on
 * both the real LS011B7DH03 (parent == screen) and the LS013 debug
 * wrapper (parent == a black-framed virtual window).
 */

#include "status_ui.h"

extern const lv_image_dsc_t aerogu_logo;

void aerogu38_status_ui_build(lv_obj_t *parent) {
    lv_obj_set_style_pad_all(parent, 0, 0);
    lv_obj_set_style_bg_color(parent, lv_color_white(), 0);
    lv_obj_set_style_bg_opa(parent, LV_OPA_COVER, 0);
    lv_obj_clear_flag(parent, LV_OBJ_FLAG_SCROLLABLE);

    lv_obj_t *img = lv_image_create(parent);
    lv_image_set_src(img, &aerogu_logo);
    lv_obj_align(img, LV_ALIGN_CENTER, 0, 0);
}
