/*
 * SPDX-License-Identifier: MIT
 *
 * Central-side glue for the peripheral notification-panel LCD.
 *
 * Most events go through ZMK_RELAY_EVENT_CENTRAL_TO_PERIPHERAL, which
 * auto-serializes the ZMK event struct under a chosen identifier.
 *
 * Layer state gets a custom payload ("LNAM") because we also want the
 * layer's display-name string, which is only available from the
 * keymap on the central side (zmk_keymap_layer_name lookup).
 *
 * Compiled only for SHIELD_AEROGU38_RIGHT via CMakeLists.txt.
 */

#include <string.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zmk/event_manager.h>
#include <zmk/keymap.h>
#include <zmk/split/central.h>
#include <zmk/split/transport/types.h>

#include <zmk/events/battery_state_changed.h>
#include <zmk/events/ble_active_profile_changed.h>
#include <zmk/events/endpoint_changed.h>
#include <zmk/events/layer_state_changed.h>
#include <zmk/events/modifiers_state_changed.h>

LOG_MODULE_REGISTER(aerogu38_relay, CONFIG_ZMK_LOG_LEVEL);

ZMK_RELAY_EVENT_CENTRAL_TO_PERIPHERAL(zmk_ble_active_profile_changed, PROF, );
ZMK_RELAY_EVENT_CENTRAL_TO_PERIPHERAL(zmk_endpoint_changed, ENDP, );
ZMK_RELAY_EVENT_CENTRAL_TO_PERIPHERAL(zmk_modifiers_state_changed, MODS, );

/* Central-battery relay uses a custom identifier ("CBAT") to keep it
 * distinct from the peripheral's own zmk_battery_state_changed
 * subscription (which drives battery_l on the display). */
ZMK_RELAY_EVENT_CENTRAL_TO_PERIPHERAL(zmk_battery_state_changed, CBAT, );

/* ---------------------------------------------------------------- *
 *  Custom layer status ("LNAM") - layer index + display-name string  *
 * ---------------------------------------------------------------- */

#define LAYER_NAME_MAX_LEN 15   /* + null terminator = 16 bytes total */

struct aerogu38_layer_status {
    uint8_t layer;
    char name[LAYER_NAME_MAX_LEN + 1];
} __packed;

static void send_layer_status(void) {
    /* Publish the currently highest-active layer so the peripheral can
     * render both its number and its display-name. */
    int32_t layer = (int32_t)zmk_keymap_highest_layer_active();
    if (layer < 0) {
        return;
    }

    struct zmk_split_relay_event_payload payload;
    memset(&payload, 0, sizeof(payload));

    static const char id[] = "LNAM";
    strcpy(payload.event_type, id);
    payload.header.event_type_size = sizeof(id) - 1;

    struct aerogu38_layer_status body = {0};
    body.layer = (uint8_t)layer;
    const char *name = zmk_keymap_layer_name(layer);
    if (name) {
        strncpy(body.name, name, LAYER_NAME_MAX_LEN);
        body.name[LAYER_NAME_MAX_LEN] = '\0';
    }
    memcpy(payload.event_data, &body, sizeof(body));
    payload.header.event_data_size = sizeof(body);

    int err = zmk_split_central_send_relay_event(&payload);
    if (err) {
        LOG_WRN("layer status relay send failed: %d", err);
    }
}

static int on_layer_state(const zmk_event_t *eh) {
    ARG_UNUSED(eh);
    send_layer_status();
    return ZMK_EV_EVENT_BUBBLE;
}

ZMK_LISTENER(aerogu38_layer_relay, on_layer_state);
ZMK_SUBSCRIPTION(aerogu38_layer_relay, zmk_layer_state_changed);
