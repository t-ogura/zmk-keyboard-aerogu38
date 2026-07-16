/*
 * SPDX-License-Identifier: MIT
 *
 * Peripheral-side status screen for aerogu38 (LS011B7DH03, 160x68).
 *
 * The panel is mounted portrait (FPC down), so we work in a logical
 * 68x160 coordinate space provided by lcd/portrait_display. That
 * module installs a rotation-aware flush cb that maps our 68x160
 * portrait writes to the panel's native 160x68 landscape layout,
 * including the LVGL-MSB vs Sharp-LSB bit-order translation.
 */

#include <lvgl.h>

#include "lcd/portrait_display.h"
#include "status_ui.h"

lv_obj_t *zmk_display_status_screen(void) {
    portrait_display_init();

    lv_obj_t *screen = lv_obj_create(NULL);
    aerogu38_status_ui_build(screen);
    return screen;
}
