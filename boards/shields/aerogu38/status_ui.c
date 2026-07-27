/*
 * SPDX-License-Identifier: MIT
 *
 * Modern-card notification panel for aerogu38 peripheral (68x160).
 * Layout follows design mockup v14b.
 *
 *    y  0..19   Aerogu header logo
 *      26..42   BT card:  [bt-icon] "BT-N" | "USB"
 *      48..108  LAYER card: "LAYER" caption + BASE hero (Spleen 32)
 *     114..156  Battery card: L row (label + bar) + R row (label + bar)
 *
 * All card borders are drawn as four `lv_line` segments directly on the
 * screen. We deliberately avoid `lv_obj_create` for containers: on 1bpp
 * mono the default LVGL theme leaks styles (dark backgrounds, scrollbar
 * layer) that produced a mosaic-then-white failure mode even after
 * `lv_obj_remove_style_all`. Line-based borders + flat labels/bars are
 * the tested-good pipeline (matches Phase 1's approach).
 */

#include "status_ui.h"

#include <string.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zmk/battery.h>
#include <zmk/endpoints.h>
#include <zmk/event_manager.h>
#include <zmk/events/battery_state_changed.h>
#include <zmk/events/ble_active_profile_changed.h>
#include <zmk/events/endpoint_changed.h>
#include <zmk/events/layer_state_changed.h>

LOG_MODULE_REGISTER(aerogu38_status, CONFIG_ZMK_LOG_LEVEL);

extern const lv_image_dsc_t aerogu_logo;
extern const lv_image_dsc_t bt_icon;

LV_FONT_DECLARE(spleen_12);
LV_FONT_DECLARE(spleen_32);

/* File-scope so ZMK event listeners can mutate them post-load. */
static lv_obj_t *layer_name_label;
static lv_obj_t *endpoint_label;
static lv_obj_t *battery_l_label;
static lv_obj_t *battery_l_bar;
static lv_obj_t *battery_r_label;
static lv_obj_t *battery_r_bar;

/* --- Drawing primitives ---------------------------------------------- */

/* Horizontal line (x0,y) → (x1,y). Used for top/bottom card edges and
 * any explicit dividers. */
static void add_hline(lv_obj_t *parent, int x0, int x1, int y) {
    static lv_point_precise_t buf[16][2];
    static int n = 0;
    if (n >= 16) return;
    buf[n][0].x = 0;         buf[n][0].y = 0;
    buf[n][1].x = x1 - x0;   buf[n][1].y = 0;
    lv_obj_t *ln = lv_line_create(parent);
    lv_line_set_points(ln, buf[n], 2);
    lv_obj_set_style_line_width(ln, 1, 0);
    lv_obj_set_style_line_color(ln, lv_color_black(), 0);
    lv_obj_set_pos(ln, x0, y);
    n++;
}

/* Vertical line (x,y0) → (x,y1). */
static void add_vline(lv_obj_t *parent, int x, int y0, int y1) {
    static lv_point_precise_t buf[16][2];
    static int n = 0;
    if (n >= 16) return;
    buf[n][0].x = 0;   buf[n][0].y = 0;
    buf[n][1].x = 0;   buf[n][1].y = y1 - y0;
    lv_obj_t *ln = lv_line_create(parent);
    lv_line_set_points(ln, buf[n], 2);
    lv_obj_set_style_line_width(ln, 1, 0);
    lv_obj_set_style_line_color(ln, lv_color_black(), 0);
    lv_obj_set_pos(ln, x, y0);
    n++;
}

/* Rectangle outline from (x,y) to (x+w-1, y+h-1). Corners aren't clipped
 * for rounding — on 68 px wide the visual difference is negligible. */
static void add_rect(lv_obj_t *parent, int x, int y, int w, int h) {
    add_hline(parent, x,           x + w - 1, y);
    add_hline(parent, x,           x + w - 1, y + h - 1);
    add_vline(parent, x,           y,         y + h - 1);
    add_vline(parent, x + w - 1,   y,         y + h - 1);
}

/* --- Label / bar helpers --------------------------------------------- */

static lv_obj_t *label_at(lv_obj_t *parent, int x, int y,
                          const lv_font_t *font, const char *text) {
    lv_obj_t *lbl = lv_label_create(parent);
    lv_label_set_text(lbl, text);
    lv_obj_set_style_text_font(lbl, font, 0);
    lv_obj_set_style_text_color(lbl, lv_color_black(), 0);
    lv_obj_set_pos(lbl, x, y);
    return lbl;
}

/* Centered horizontally on the screen (68 px wide). The label object
 * itself is auto-sized to text width, then aligned so its centre sits
 * on the screen centre; y is the top of the label. */
static lv_obj_t *label_hcenter(lv_obj_t *parent, int y,
                               const lv_font_t *font, const char *text) {
    lv_obj_t *lbl = lv_label_create(parent);
    lv_label_set_text(lbl, text);
    lv_obj_set_style_text_font(lbl, font, 0);
    lv_obj_set_style_text_color(lbl, lv_color_black(), 0);
    lv_obj_align(lbl, LV_ALIGN_TOP_MID, 0, y);
    return lbl;
}

static lv_obj_t *battery_bar_create(lv_obj_t *parent, int x, int y,
                                    int w, int h) {
    lv_obj_t *bar = lv_bar_create(parent);
    lv_bar_set_range(bar, 0, 100);
    lv_bar_set_value(bar, 0, LV_ANIM_OFF);
    lv_obj_set_pos(bar, x, y);
    lv_obj_set_size(bar, w, h);
    lv_obj_set_style_bg_color(bar, lv_color_white(), 0);
    lv_obj_set_style_bg_opa(bar, LV_OPA_COVER, 0);
    lv_obj_set_style_border_color(bar, lv_color_black(), 0);
    lv_obj_set_style_border_width(bar, 1, 0);
    lv_obj_set_style_border_opa(bar, LV_OPA_COVER, 0);
    lv_obj_set_style_radius(bar, 0, 0);
    lv_obj_set_style_pad_all(bar, 1, 0);
    lv_obj_set_style_bg_color(bar, lv_color_black(), LV_PART_INDICATOR);
    lv_obj_set_style_bg_opa(bar, LV_OPA_COVER, LV_PART_INDICATOR);
    lv_obj_set_style_radius(bar, 0, LV_PART_INDICATOR);
    return bar;
}

/* --- Section builders ------------------------------------------------- */

static void build_header(lv_obj_t *parent) {
    lv_obj_t *img = lv_image_create(parent);
    lv_image_set_src(img, &aerogu_logo);
    lv_obj_set_pos(img, 0, 0);
}

static void build_bt_card(lv_obj_t *parent) {
    add_rect(parent, 2, 26, AEROGU38_UI_W - 4, 17);

    lv_obj_t *icon = lv_image_create(parent);
    lv_image_set_src(icon, &bt_icon);
    lv_obj_set_pos(icon, 6, 30);

    endpoint_label = label_at(parent, 20, 28, &spleen_12, "BT-?");
}

static void build_layer_card(lv_obj_t *parent) {
    /* Full-width so BASE at Spleen 32 (glyph advance 16 -> 64 px total
     * for 4 chars) fits inside the 1-px borders. */
    add_rect(parent, 0, 48, AEROGU38_UI_W, 61);

    label_hcenter(parent, 51, &spleen_12, "LAYER");
    layer_name_label = label_hcenter(parent, 68, &spleen_32, "BASE");
}

static void build_battery_card(lv_obj_t *parent, int initial_l_pct) {
    add_rect(parent, 2, 114, AEROGU38_UI_W - 4, 43);

    /* Row 1: L */
    battery_l_label = label_at(parent, 5, 116, &spleen_12,
                               initial_l_pct >= 0 ? "L" : "L --%");
    if (initial_l_pct >= 0) {
        lv_label_set_text_fmt(battery_l_label, "L %d%%", initial_l_pct);
    }
    battery_l_bar = battery_bar_create(parent, 5, 128, AEROGU38_UI_W - 14, 4);
    if (initial_l_pct >= 0) {
        lv_bar_set_value(battery_l_bar, initial_l_pct, LV_ANIM_OFF);
    }

    /* Row 2: R (placeholder until CBAT relay arrives) */
    battery_r_label = label_at(parent, 5, 137, &spleen_12, "R --%");
    battery_r_bar = battery_bar_create(parent, 5, 149, AEROGU38_UI_W - 14, 4);
}

/* --- ZMK events: local L battery ------------------------------------- */

static void battery_l_update(int pct) {
    if (battery_l_label) lv_label_set_text_fmt(battery_l_label, "L %d%%", pct);
    if (battery_l_bar)   lv_bar_set_value(battery_l_bar, pct, LV_ANIM_OFF);
}

static int on_battery_changed(const zmk_event_t *eh) {
    const struct zmk_battery_state_changed *ev = as_zmk_battery_state_changed(eh);
    if (ev) battery_l_update(ev->state_of_charge);
    return ZMK_EV_EVENT_BUBBLE;
}
ZMK_LISTENER(aerogu38_status_battery, on_battery_changed);
ZMK_SUBSCRIPTION(aerogu38_status_battery, zmk_battery_state_changed);

/* --- Relayed state (layer name / BT profile / endpoint / R bat) ------ */

#define LAYER_NAME_MAX_LEN 15
struct layer_status_payload {
    uint8_t layer;
    char name[LAYER_NAME_MAX_LEN + 1];
} __packed;

/* BASE hero is Spleen 32 (16 px per glyph advance): 4 chars = 64 px,
 * which exactly matches the LAYER card's inner width. Truncate to 4 and
 * force uppercase so any layer name renders identically. */
static void set_layer_display(const char *name) {
    if (!layer_name_label) return;
    char disp[5];
    if (name[0]) {
        int i;
        for (i = 0; i < 4 && name[i]; i++) {
            char c = name[i];
            if (c >= 'a' && c <= 'z') c -= 32;
            disp[i] = c;
        }
        disp[i] = '\0';
    } else {
        strcpy(disp, "BASE");
    }
    lv_label_set_text(layer_name_label, disp);
    lv_obj_align(layer_name_label, LV_ALIGN_TOP_MID, 0, 68);
}

static void handle_relay_layer_name(const uint8_t *data, size_t len) {
    if (len < sizeof(struct layer_status_payload)) return;
    struct layer_status_payload body;
    memcpy(&body, data, sizeof(body));
    body.name[LAYER_NAME_MAX_LEN] = '\0';
    set_layer_display(body.name);
}

static void handle_relay_profile(const uint8_t *data, size_t len) {
    if (len < sizeof(struct zmk_ble_active_profile_changed) || !endpoint_label) return;
    struct zmk_ble_active_profile_changed ev;
    memcpy(&ev, data, sizeof(ev));
    lv_label_set_text_fmt(endpoint_label, "BT-%d", ev.index);
}

static void handle_relay_endpoint(const uint8_t *data, size_t len) {
    if (len < sizeof(struct zmk_endpoint_changed) || !endpoint_label) return;
    struct zmk_endpoint_changed ev;
    memcpy(&ev, data, sizeof(ev));
    if (ev.endpoint.transport == ZMK_TRANSPORT_USB) {
        lv_label_set_text(endpoint_label, "USB");
    } else {
        lv_label_set_text_fmt(endpoint_label, "BT-%d", ev.endpoint.ble.profile_index);
    }
}

static void handle_relay_central_battery(const uint8_t *data, size_t len) {
    if (len < sizeof(struct zmk_battery_state_changed)) return;
    struct zmk_battery_state_changed ev;
    memcpy(&ev, data, sizeof(ev));
    if (battery_r_label) lv_label_set_text_fmt(battery_r_label, "R %d%%", ev.state_of_charge);
    if (battery_r_bar)   lv_bar_set_value(battery_r_bar, ev.state_of_charge, LV_ANIM_OFF);
}

static int on_relay_event(const zmk_event_t *eh) {
    const struct zmk_relay_event_received *ev = as_zmk_relay_event_received(eh);
    if (!ev || !ev->event_name) return ZMK_EV_EVENT_BUBBLE;

    if (strcmp(ev->event_name, "LNAM") == 0) {
        handle_relay_layer_name(ev->event_data, ev->event_data_size);
    } else if (strcmp(ev->event_name, "PROF") == 0) {
        handle_relay_profile(ev->event_data, ev->event_data_size);
    } else if (strcmp(ev->event_name, "ENDP") == 0) {
        handle_relay_endpoint(ev->event_data, ev->event_data_size);
    } else if (strcmp(ev->event_name, "CBAT") == 0) {
        handle_relay_central_battery(ev->event_data, ev->event_data_size);
    }
    return ZMK_EV_EVENT_BUBBLE;
}
ZMK_LISTENER(aerogu38_status_relay, on_relay_event);
ZMK_SUBSCRIPTION(aerogu38_status_relay, zmk_relay_event_received);

/* --- Public entry point ---------------------------------------------- */

void aerogu38_status_ui_build(lv_obj_t *parent) {
    lv_obj_set_style_pad_all(parent, 0, 0);
    lv_obj_set_style_bg_color(parent, lv_color_white(), 0);
    lv_obj_set_style_bg_opa(parent, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(parent, 0, 0);
    lv_obj_clear_flag(parent, LV_OBJ_FLAG_SCROLLABLE);

    build_header(parent);
    build_bt_card(parent);
    build_layer_card(parent);
    build_battery_card(parent, zmk_battery_state_of_charge());
}
