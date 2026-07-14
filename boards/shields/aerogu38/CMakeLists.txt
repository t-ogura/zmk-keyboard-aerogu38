# Peripheral-side display sources compile only when ZMK_DISPLAY is on AND
# this build is the peripheral (SHIELD_AEROGU38_LEFT). The central shield
# leaves ZMK_DISPLAY off, so this block is a no-op there.
if(CONFIG_ZMK_DISPLAY AND CONFIG_SHIELD_AEROGU38_LEFT)
  zephyr_library_sources(custom_status_screen.c)
  zephyr_library_sources(aerogu_logo.c)
endif()
