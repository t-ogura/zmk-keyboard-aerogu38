/*
 * SPDX-License-Identifier: MIT
 *
 * Peripheral-side status screen for aerogu38 (LS011B7DH03, 160 x 68).
 * The screen IS the 160x68 UI area - status_ui.c paints directly on it.
 */

#include <lvgl.h>

#include "status_ui.h"

lv_obj_t *zmk_display_status_screen(void) {
    lv_obj_t *screen = lv_obj_create(NULL);
    aerogu38_status_ui_build(screen);
    return screen;
}
