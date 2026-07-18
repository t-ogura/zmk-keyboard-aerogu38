/*
 * SPDX-License-Identifier: MIT
 *
 * Portrait notification-panel layout for aerogu38 peripheral (68x160).
 *
 * Phase 1 wiring:
 *   - Header:    Aerogu logo (image, 68x20)
 *   - Layer:     placeholder ("L?" / "----") - awaits central relay
 *   - Endpoint:  placeholder ("USB" / "BT ?") - awaits central relay
 *   - Modifiers: placeholder ("- - - -") - awaits central relay
 *   - Battery L: LIVE - peripheral's own battery via ZMK event
 *   - Battery R: placeholder ("R --%") - awaits central relay
 *
 * Layout coordinates (y offsets from top):
 *    0..19  header
 *   20      1px divider
 *   21..60  layer          (40 tall)
 *   61      divider
 *   62..85  modifiers      (24 tall)
 *   86      divider
 *   87..110 endpoint       (24 tall)
 *   111     divider
 *   112..159 batteries     (48 tall)
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
#include <zmk/events/modifiers_state_changed.h>
#include <dt-bindings/zmk/modifiers.h>

LOG_MODULE_REGISTER(aerogu38_status, CONFIG_ZMK_LOG_LEVEL);

extern const lv_image_dsc_t aerogu_logo;

/* Kept alive as file-scope statics so ZMK event listeners can update
 * them after the screen has been loaded. */
static lv_obj_t *battery_l_label;
static lv_obj_t *battery_l_bar;
static lv_obj_t *battery_r_label;
static lv_obj_t *battery_r_bar;
static lv_obj_t *layer_num_label;
static lv_obj_t *layer_name_label;
static lv_obj_t *modifiers_label;
static lv_obj_t *endpoint_label;

/* Draw a 1-px horizontal separator line spanning the full width at the
 * given y coordinate. Uses lv_line for a proper 1-px stroke. */
static void add_divider(lv_obj_t *parent, int y) {
    static lv_point_precise_t points[2];
    points[0].x = 0;
    points[0].y = 0;
    points[1].x = AEROGU38_UI_W - 1;
    points[1].y = 0;
    lv_obj_t *line = lv_line_create(parent);
    lv_line_set_points(line, points, 2);
    lv_obj_set_style_line_width(line, 1, 0);
    lv_obj_set_style_line_color(line, lv_color_black(), 0);
    lv_obj_set_pos(line, 0, y);
}

/* --- Section builders --------------------------------------------------- */

static void build_header(lv_obj_t *parent) {
    lv_obj_t *img = lv_image_create(parent);
    lv_image_set_src(img, &aerogu_logo);
    lv_obj_set_pos(img, 0, 0);
}

static void build_layer_section(lv_obj_t *parent, int y) {
    layer_num_label = lv_label_create(parent);
    lv_label_set_text(layer_num_label, "L 0");
    lv_obj_set_style_text_font(layer_num_label, &lv_font_unscii_16, 0);
    lv_obj_align(layer_num_label, LV_ALIGN_TOP_LEFT, 2, y + 2);

    layer_name_label = lv_label_create(parent);
    lv_label_set_text(layer_name_label, "...");
    lv_obj_set_style_text_font(layer_name_label, &lv_font_unscii_8, 0);
    lv_obj_align(layer_name_label, LV_ALIGN_TOP_LEFT, 2, y + 22);
}

static void build_modifiers_section(lv_obj_t *parent, int y) {
    modifiers_label = lv_label_create(parent);
    lv_label_set_text(modifiers_label, "- - - -");
    lv_obj_set_style_text_font(modifiers_label, &lv_font_unscii_16, 0);
    lv_obj_align(modifiers_label, LV_ALIGN_TOP_LEFT, 2, y + 4);
}

static void build_endpoint_section(lv_obj_t *parent, int y) {
    endpoint_label = lv_label_create(parent);
    lv_label_set_text(endpoint_label, "BT ?");
    lv_obj_set_style_text_font(endpoint_label, &lv_font_unscii_16, 0);
    lv_obj_align(endpoint_label, LV_ALIGN_TOP_LEFT, 2, y + 4);
}

/* Battery row: "L  87%" text + 40-pixel-wide bar below.
 * `label_letter` is "L" for the local half or "R" for the relayed one. */
static void build_battery_row(lv_obj_t *parent, int y, const char *label_letter,
                              int initial_pct, bool is_placeholder,
                              lv_obj_t **out_label, lv_obj_t **out_bar) {
    /* Text: "L 87%" or "L --%" for unknown. */
    lv_obj_t *lbl = lv_label_create(parent);
    if (is_placeholder || initial_pct < 0) {
        lv_label_set_text_fmt(lbl, "%s --%%", label_letter);
    } else {
        lv_label_set_text_fmt(lbl, "%s %d%%", label_letter, initial_pct);
    }
    lv_obj_set_style_text_font(lbl, &lv_font_unscii_8, 0);
    lv_obj_align(lbl, LV_ALIGN_TOP_LEFT, 2, y);

    /* Bar: outlined rectangle 60x6 with inner fill proportional to %. */
    lv_obj_t *bar = lv_bar_create(parent);
    lv_obj_set_size(bar, 60, 6);
    lv_obj_align(bar, LV_ALIGN_TOP_LEFT, 4, y + 10);
    lv_bar_set_range(bar, 0, 100);
    lv_bar_set_value(bar, initial_pct >= 0 ? initial_pct : 0, LV_ANIM_OFF);
    lv_obj_set_style_bg_color(bar, lv_color_white(), 0);
    lv_obj_set_style_bg_color(bar, lv_color_black(), LV_PART_INDICATOR);
    lv_obj_set_style_border_color(bar, lv_color_black(), 0);
    lv_obj_set_style_border_width(bar, 1, 0);
    lv_obj_set_style_radius(bar, 0, 0);
    lv_obj_set_style_radius(bar, 0, LV_PART_INDICATOR);

    if (out_label) *out_label = lbl;
    if (out_bar)   *out_bar   = bar;
}

/* --- ZMK event subscription: keep battery_l live -------------------- */

static void battery_l_update(int pct) {
    if (battery_l_label) {
        lv_label_set_text_fmt(battery_l_label, "L %d%%", pct);
    }
    if (battery_l_bar) {
        lv_bar_set_value(battery_l_bar, pct, LV_ANIM_OFF);
    }
}

static int on_battery_changed(const zmk_event_t *eh) {
    const struct zmk_battery_state_changed *ev = as_zmk_battery_state_changed(eh);
    if (ev) {
        battery_l_update(ev->state_of_charge);
    }
    return ZMK_EV_EVENT_BUBBLE;
}

ZMK_LISTENER(aerogu38_status_battery, on_battery_changed);
ZMK_SUBSCRIPTION(aerogu38_status_battery, zmk_battery_state_changed);

/* --- Relayed state (layer / BT profile / endpoint) -----------------
 *
 * ZMK's layer / endpoint / ble-profile event implementations are only
 * compiled on the central shield, so ZMK_RELAY_EVENT_HANDLE (which
 * re-raises the event locally) can't link here. Instead we subscribe
 * to the raw zmk_relay_event_received event, dispatch by name, and
 * update widgets directly.
 */

/* Custom layer-status payload sent by the central under identifier
 * "LNAM". Kept in sync with central_relay.c's aerogu38_layer_status. */
#define LAYER_NAME_MAX_LEN 15
struct layer_status_payload {
    uint8_t layer;
    char name[LAYER_NAME_MAX_LEN + 1];
} __packed;

static void handle_relay_layer_name(const uint8_t *data, size_t len) {
    if (len < sizeof(struct layer_status_payload)) {
        return;
    }
    struct layer_status_payload body;
    memcpy(&body, data, sizeof(body));
    body.name[LAYER_NAME_MAX_LEN] = '\0';   /* defensive */

    if (layer_num_label) {
        lv_label_set_text_fmt(layer_num_label, "L %u", (unsigned)body.layer);
    }
    if (layer_name_label) {
        /* Blank name -> show "..." so the row still has content. */
        lv_label_set_text(layer_name_label, body.name[0] ? body.name : "...");
    }
}

static void handle_relay_modifiers(const uint8_t *data, size_t len) {
    if (len < sizeof(struct zmk_modifiers_state_changed) || !modifiers_label) {
        return;
    }
    struct zmk_modifiers_state_changed ev;
    memcpy(&ev, data, sizeof(ev));
    uint8_t m = (uint8_t)ev.modifiers;

    /* One character slot per modifier family (L|R merged). Uppercase
     * letter when the modifier is held, '-' when it isn't. */
    char slot[4] = {
        (m & (MOD_LSFT | MOD_RSFT)) ? 'S' : '-',
        (m & (MOD_LCTL | MOD_RCTL)) ? 'C' : '-',
        (m & (MOD_LALT | MOD_RALT)) ? 'A' : '-',
        (m & (MOD_LGUI | MOD_RGUI)) ? 'W' : '-',
    };
    lv_label_set_text_fmt(modifiers_label, "%c %c %c %c",
                          slot[0], slot[1], slot[2], slot[3]);
}

static void handle_relay_profile(const uint8_t *data, size_t len) {
    if (len < sizeof(struct zmk_ble_active_profile_changed) || !endpoint_label) {
        return;
    }
    struct zmk_ble_active_profile_changed ev;
    memcpy(&ev, data, sizeof(ev));
    /* NOTE: ev.profile pointer is a central-side address and must not
     * be dereferenced here - we only use ev.index. */
    lv_label_set_text_fmt(endpoint_label, "BT %d", ev.index);
}

static void handle_relay_endpoint(const uint8_t *data, size_t len) {
    if (len < sizeof(struct zmk_endpoint_changed) || !endpoint_label) {
        return;
    }
    struct zmk_endpoint_changed ev;
    memcpy(&ev, data, sizeof(ev));
    if (ev.endpoint.transport == ZMK_TRANSPORT_USB) {
        lv_label_set_text(endpoint_label, "USB");
    } else {
        lv_label_set_text_fmt(endpoint_label, "BT %d", ev.endpoint.ble.profile_index);
    }
}

static void handle_relay_central_battery(const uint8_t *data, size_t len) {
    if (len < sizeof(struct zmk_battery_state_changed)) {
        return;
    }
    struct zmk_battery_state_changed ev;
    memcpy(&ev, data, sizeof(ev));
    if (battery_r_label) {
        lv_label_set_text_fmt(battery_r_label, "R %d%%", ev.state_of_charge);
    }
    if (battery_r_bar) {
        lv_bar_set_value(battery_r_bar, ev.state_of_charge, LV_ANIM_OFF);
    }
}

static int on_relay_event(const zmk_event_t *eh) {
    const struct zmk_relay_event_received *ev = as_zmk_relay_event_received(eh);
    if (!ev || !ev->event_name) {
        return ZMK_EV_EVENT_BUBBLE;
    }
    if (strcmp(ev->event_name, "LNAM") == 0) {
        handle_relay_layer_name(ev->event_data, ev->event_data_size);
    } else if (strcmp(ev->event_name, "MODS") == 0) {
        handle_relay_modifiers(ev->event_data, ev->event_data_size);
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

/* --- Public entry point --------------------------------------------- */

void aerogu38_status_ui_build(lv_obj_t *parent) {
    /* Parent (screen) style. */
    lv_obj_set_style_pad_all(parent, 0, 0);
    lv_obj_set_style_bg_color(parent, lv_color_white(), 0);
    lv_obj_set_style_bg_opa(parent, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(parent, 0, 0);
    lv_obj_clear_flag(parent, LV_OBJ_FLAG_SCROLLABLE);

    /* Sections. */
    build_header(parent);
    add_divider(parent, 20);

    build_layer_section(parent, 21);
    add_divider(parent, 61);

    build_modifiers_section(parent, 62);
    add_divider(parent, 86);

    build_endpoint_section(parent, 87);
    add_divider(parent, 111);

    /* Left half battery: live via ZMK event. */
    int init_pct = zmk_battery_state_of_charge();
    build_battery_row(parent, 114, "L", init_pct, false,
                      &battery_l_label, &battery_l_bar);

    /* Right half battery: fed by the central via the CBAT relay event. */
    build_battery_row(parent, 138, "R", -1, false,
                      &battery_r_label, &battery_r_bar);
}
