if(CONFIG_ZMK_DISPLAY AND CONFIG_SHIELD_AEROGU38_LEFT)
  # UI content builder - target-independent, always compiled.
  zephyr_library_sources(status_ui.c)
  zephyr_library_sources(aerogu_logo.c)

  # Screen wrapper - production (LS011). The LS013 debug branch swaps
  # this file for a version that adds rotation + a 160x68 virtual window.
  zephyr_library_sources(custom_status_screen.c)
endif()
