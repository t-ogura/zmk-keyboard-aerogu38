/*
 * SPDX-License-Identifier: MIT
 *
 * Peripheral status UI builder for aerogu38.
 *
 * Draws inside a caller-provided parent object sized 68x160 (logical
 * portrait). The screen wrapper (custom_status_screen.c) creates the
 * parent; the rotation/bit-order fix-up lives in
 * lcd/portrait_display.c.
 */

#pragma once

#include <lvgl.h>

#define AEROGU38_UI_W 68
#define AEROGU38_UI_H 160

/* Fill `parent` (assumed 68 x 160) with the peripheral status UI. */
void aerogu38_status_ui_build(lv_obj_t *parent);
