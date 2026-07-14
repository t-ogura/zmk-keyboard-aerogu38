/*
 * SPDX-License-Identifier: MIT
 *
 * Peripheral status UI builder for aerogu38.
 *
 * The UI targets a 160 x 68 area and is written to be independent of how
 * that area is placed on the physical display. The production wrapper
 * passes the whole screen (LS011B7DH03). A debug wrapper (LS013 branch)
 * passes a virtual 160x68 sub-object it constructs itself.
 */

#pragma once

#include <lvgl.h>

/* Fill `parent` (assumed 160 x 68) with the peripheral status UI. */
void aerogu38_status_ui_build(lv_obj_t *parent);
