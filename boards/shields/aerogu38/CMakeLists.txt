# Peripheral (LEFT) side - display / status UI stack.
if(CONFIG_ZMK_DISPLAY AND CONFIG_SHIELD_AEROGU38_LEFT)
  # Rotation adapter (future module: zmk-widget-sharp-memory-lcd)
  zephyr_library_sources(lcd/portrait_display.c)

  # UI content builder - target-independent, always compiled.
  zephyr_library_sources(status_ui.c)
  zephyr_library_sources(aerogu_logo.c)

  # Screen wrapper - production (LS011). The LS013 debug branch swaps
  # this file for a version that adds rotation + a 160x68 virtual window.
  zephyr_library_sources(custom_status_screen.c)
endif()

# Central (RIGHT) side - relays layer / profile / endpoint events over
# the split BLE link so the peripheral's status UI can display them.
if(CONFIG_ZMK_SPLIT_RELAY_EVENT AND CONFIG_SHIELD_AEROGU38_RIGHT)
  zephyr_library_sources(central_relay.c)
endif()
