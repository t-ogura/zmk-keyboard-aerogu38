/*
 * SPDX-License-Identifier: MIT
 *
 * Portrait-orientation adapter for a natively-landscape 1bpp display.
 *
 * Sharp Memory LCD panels are addressed in a fixed line-by-line format
 * dictated by hardware; they cannot be rotated at the panel level. LVGL
 * v9's `lv_display_set_rotation()` only rotates coordinates for input
 * handling and reported resolution - it does NOT rotate the pixel data
 * before flushing, and Zephyr's `lvgl_display_mono.c` glue does not
 * implement rotation either.
 *
 * This module bridges the gap: LVGL sees the display as portrait
 * (LOGICAL_W x LOGICAL_H), UI code targets that portrait coordinate
 * space, and this module's custom flush callback rotates each flushed
 * region 90 degrees CCW into a scratch buffer before handing it off to
 * the standard Zephyr mono flush cb for pixel packing + display_write.
 *
 * Intended to be the seed of a future stand-alone module
 * `zmk-widget-sharp-memory-lcd`; the file is deliberately generic and
 * has no aerogu-specific dependencies.
 */

#pragma once

#include <stdint.h>

/*
 * Install the portrait-rotation flush cb on the LVGL default display.
 *
 * Call this once, AFTER LVGL and Zephyr's display driver have finished
 * their initial setup, and BEFORE the first screen is loaded. In ZMK
 * that is inside zmk_display_status_screen().
 *
 * The physical LCD dimensions must match the compile-time constants
 * below. Change the #defines and rebuild if you use a different panel.
 */
void portrait_display_init(void);

/* Native panel resolution (as configured in the ls0xx DT node). */
#define PORTRAIT_NATIVE_W 160
#define PORTRAIT_NATIVE_H 68

/* Logical resolution after rotation - UI code targets this. */
#define PORTRAIT_LOGICAL_W PORTRAIT_NATIVE_H  /* 68  */
#define PORTRAIT_LOGICAL_H PORTRAIT_NATIVE_W  /* 160 */
