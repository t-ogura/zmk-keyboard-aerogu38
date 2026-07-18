/*
 * SPDX-License-Identifier: MIT
 *
 * Central-side glue for the peripheral notification-panel LCD.
 *
 * ZMK's ZMK_RELAY_EVENT_CENTRAL_TO_PERIPHERAL macro installs a
 * listener on the given ZMK event and, whenever it fires on the
 * central, forwards a serialized copy over the split BLE link to
 * every peripheral. The peripheral re-raises the event locally via
 * a matching ZMK_RELAY_EVENT_HANDLE macro (see status_ui.c) so any
 * peripheral code that subscribes to the event works transparently.
 *
 * The four-character identifier strings (LAYR / PROF / ENDP) are the
 * on-the-wire event names; they must match exactly on both sides and
 * fit within CONFIG_ZMK_SPLIT_RELAY_EVENT_TYPE_NAME_LEN.
 *
 * This file is compiled only for SHIELD_AEROGU38_RIGHT (see the
 * conditional in CMakeLists.txt) - the peripheral shield gets a
 * different set of macros in status_ui.c.
 */

#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zmk/event_manager.h>
#include <zmk/events/layer_state_changed.h>
#include <zmk/events/ble_active_profile_changed.h>
#include <zmk/events/endpoint_changed.h>

LOG_MODULE_REGISTER(aerogu38_relay, CONFIG_ZMK_LOG_LEVEL);

ZMK_RELAY_EVENT_CENTRAL_TO_PERIPHERAL(zmk_layer_state_changed, LAYR, );
ZMK_RELAY_EVENT_CENTRAL_TO_PERIPHERAL(zmk_ble_active_profile_changed, PROF, );
ZMK_RELAY_EVENT_CENTRAL_TO_PERIPHERAL(zmk_endpoint_changed, ENDP, );
