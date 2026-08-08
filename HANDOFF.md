# aerogu38 Peripheral LCD — Development Handoff

> **This document exists to hand off in-progress work to a fresh Claude
> Code session in a different environment.** It is NOT permanent
> documentation and will be removed once the branch merges. If you are
> a returning contributor months later, look at `feat/*` branch commits
> and `docs/` in the workspace parent for the canonical write-ups.

**Branch**: `feat/lcd-portrait-notification`
**Repo**: `t-ogura/zmk-keyboard-aerogu38`
**Base commit at handoff**: latest tip of that branch
**Status**: see "Session log" below — the module extraction is DONE and
the sections after the log describe the historical Phase 0-4 work.

---

## 0. Session log (newest first) — READ THIS FIRST

### 2026-07-31 / 08-01: prospector v2.2.2 released (side quest)

Fixed two v2.2.1 regressions in `t-ogura/prospector-zmk-module`
(burst/silent adv duty cycle): uni-body build failure
(zmk-config-prospector#24) and burst/silent cycle lock-up on split
centrals (#22). Merged to module main, tagged `v2.2.2`. Released via
`t-ogura/zmk-config-prospector` per that repo's convention (west.yml
pin bump + README + docs/RELEASES/v2.2.2/release_notes.md + tag), CI
green, issues auto-closed. **Only remaining step: publish the GitHub
Releases page for tag v2.2.2** (needs t-ogura's auth; body text was
drafted in-session — regenerate from docs/RELEASES/v2.2.2 if lost).

### 2026-07-30/31: UI stack extracted to zmk-widget-sharp-memory-lcd

All LCD/UI/relay code moved to the new public module
`t-ogura/zmk-widget-sharp-memory-lcd` (4+ commits on main). This
shield now only carries the SPI overlay + Kconfig glue; west.yml pins
the module. Module architecture:

- **plumbing generic**: panel dims + rotation (CCW/CW) via Kconfig;
  works for any ls0xx (LS013B7DH05 = set 144/168 + LAYOUT_CUSTOM)
- **layouts hand-tuned**: `LAYOUT_68X160` (only one so far);
  `LAYOUT_CUSTOM` = bring-your-own zmk_display_status_screen()
- **data sources**: `SOURCE_PERIPHERAL` (relay receiver, aerogu38's
  topology) / `SOURCE_CENTRAL` (direct local subscriptions, nice!view
  style) selected by Kconfig, auto-defaulted by split role
- **battery L/R labels**: `SIDE_LEFT/RIGHT` Kconfig

### 2026-07-28/29: v14b UI landed on hardware

Design converged after 14 mockup rounds (design/mockups/, brief in
design/DESIGN_BRIEF.md for outsourcing further exploration). Landed
"v14b-nb": keyboard-name header (inverted bar, Spleen 16, from
CONFIG_ZMK_KEYBOARD_NAME), BT icon + subscript profile digit / USB
trident icon swap, LAYER caption + 4-char-uppercase hero (Spleen 32),
L/R slim battery bars. Hardware-verified live updates via relay.

**Critical 1bpp LVGL lesson (cost a debugging session):**
`lv_obj_create` containers leak default-theme styles at 1bpp =
mosaic-then-white screen, even after `lv_obj_remove_style_all`. Use
`lv_line` x4 for rectangles and `lv_bar` at 100% for filled areas.
This and other gotchas are in the module README.

### Next steps when returning to aerogu38 UI work

- v15+ design exploration (hand DESIGN_BRIEF.md to other sessions/AIs)
- docs/preview.png for the module README (photo of real hardware)
- Consider Topics/description on the module repo

---

## 1. Project context in one paragraph

`aerogu38` is a 38-key wireless split keyboard (Seeed XIAO nRF52840 per
half). The **left half is peripheral**, physically mounts a Sharp
Memory LCD **LS011B7DH03 (160×68 native)** portrait-oriented with the
FPC at the bottom. The right half is central and drives the trackball
+ USB/BLE HID. This branch adds a portrait notification panel UI on
that LCD, receiving state (layer, BT profile, endpoint) from the
central via ZMK's split-relay event mechanism. Long-term goal is to
extract the LCD stack into a reusable module named
`zmk-widget-sharp-memory-lcd`.

---

## 2. Repo layout you actually need

```
zmk-keyboard-aerogu38/
├── HANDOFF.md              ← this file
├── boards/shields/aerogu38/
│   ├── aerogu38.dtsi
│   ├── aerogu38_left.overlay   ← LS011 SPI wiring
│   ├── aerogu38_right.overlay
│   ├── Kconfig.defconfig       ← picks CUSTOM status screen for LEFT
│   ├── CMakeLists.txt          ← per-shield source selection
│   ├── custom_status_screen.c  ← screen wrapper (calls portrait_display_init)
│   ├── status_ui.h / status_ui.c   ← the actual widget tree + event handlers
│   ├── aerogu_logo.c           ← 68x20 portrait header logo (I1 image dsc)
│   ├── central_relay.c         ← compiled only for RIGHT; sends LAYR/PROF/ENDP
│   └── lcd/                    ← future module boundary
│       ├── portrait_display.h
│       └── portrait_display.c  ← rotation + bit-order flush cb
├── config/
│   ├── aerogu38_left.conf      ← peripheral display + LVGL widgets
│   └── aerogu38_right.conf     ← relay identifier length bumped to 8
└── firmware/                   ← gitignored; use -f to commit binaries
    ├── aerogu38_left.uf2
    └── aerogu38_right_prospector.uf2
```

Reference material outside this repo (in the same workspace):
- `../docs/sharp-memory-lcd-integration-guide.md` — reusable how-to
- `../docs/lcd-ui-research.md`                    — original UI research
- `../zmk-workspace/`                             — west workspace
  - `zmk/` is `cormoran/zmk main+dya` (Zephyr 4.1, LVGL v9.3)

---

## 3. What each phase produced

### Phase 0 — Portrait rotation with a custom flush cb (DONE)

Physical panel is landscape (160×68) but mounted portrait; LVGL v9 has
no rotation support that reaches Zephyr's monochrome flush glue. Solved
by hijacking the flush cb in `lcd/portrait_display.c`:

1. `lv_display_set_resolution(disp, 68, 160)` → LVGL renders in
   logical portrait.
2. `lv_display_set_color_format(disp, LV_COLOR_FORMAT_I1)` — explicit
   re-affirmation (defensive; resolution changes can perturb state).
3. `lv_display_set_buffers(disp, our_buf, NULL, size,
   LV_DISPLAY_RENDER_MODE_FULL)` — **FULL mode is required**. PARTIAL
   silently produced empty frames (BSS zeros).
4. Remove Zephyr's rounder cb (`lvgl_rounder_cb_mono`) and install one
   that forces the whole logical screen every flush. Sharp LCDs write
   whole lines anyway; full-screen refresh is cheap at 68×160.
5. Install our own flush cb that:
   - Skips the 8-byte I1 palette prefix.
   - Rotates 90° CCW: logical (x,y) → native (y, LOGICAL_W-1-x).
   - Translates MSB-first LVGL packing to LSB-first for ls0xx (each
     byte's bits are reversed within the same loop).
   - Writes directly via `display_write()`, bypassing Zephyr's mono
     glue entirely.

All Phase 0 diagnostics went through 16 steps to nail these facts;
the top-of-file comment in `portrait_display.c` captures the bit
matrix and `docs/sharp-memory-lcd-integration-guide.md` §6.8 has the
generalised recipe.

### Phase 1 — Notification panel layout (DONE)

`status_ui.c` fills the 68×160 canvas with 5 sections separated by
1-px black dividers:

```
y  0..19  header       ← 68x20 Aerogu logo
   20     divider
   21..60 layer         ← "L N" (UNSCII_16) + placeholder "----" (UNSCII_8)
   61     divider
   62..85 modifiers     ← placeholder "- - - -"
   86     divider
   87..110 endpoint     ← "BT N" / "USB" (UNSCII_16)
   111    divider
   112..159 batteries   ← "L NN%" + bar (live) / "R --%" + bar (placeholder)
```

The **left battery is live** via `zmk_battery_state_of_charge()` at
init and `zmk_battery_state_changed` event subscription. All other
sections are placeholders in Phase 1.

Config side effects:
- `CONFIG_LV_USE_LINE=y` for dividers.
- `CONFIG_LV_USE_BAR=y` for battery indicators.

### Phase 2 — Central→peripheral state relay (DONE, needs hw verify)

**Central side** (`central_relay.c`, RIGHT shield only):
```c
ZMK_RELAY_EVENT_CENTRAL_TO_PERIPHERAL(zmk_layer_state_changed, LAYR, );
ZMK_RELAY_EVENT_CENTRAL_TO_PERIPHERAL(zmk_ble_active_profile_changed, PROF, );
ZMK_RELAY_EVENT_CENTRAL_TO_PERIPHERAL(zmk_endpoint_changed, ENDP, );
```

Each macro installs a listener on the ZMK event bus and, when the
event fires, serializes the struct and pushes it over the split BLE
`relay_event` GATT characteristic with the 4-char identifier as the
event name.

**Peripheral side** (`status_ui.c`):
- Cannot use `ZMK_RELAY_EVENT_HANDLE` — it re-raises the ZMK event
  locally, but the layer/profile/endpoint event *implementations* are
  central-only (their `raise_*` symbols don't exist on peripheral, so
  the macro fails to link).
- Instead subscribes directly to `zmk_relay_event_received`, dispatches
  by `strcmp(ev->event_name, ...)`, memcpy's the payload into a local
  struct, and mutates widgets in place.

Both halves must agree on `CONFIG_ZMK_SPLIT_RELAY_EVENT_TYPE_NAME_LEN`
— default 4 is too tight because `sizeof("LAYR")` is 5. We bumped to 8
in both `.conf` files.

---

## 4. Gotchas that already burned an hour, so you don't have to

Prioritised list; the details are also in the source comments.

1. **LVGL v9 rotation doesn't reach the mono flush** — `disp->rotation`
   only affects the resolution getters and touch input. Rendering
   ignores it. If you want rotation on a monochrome Zephyr build, you
   write it yourself.

2. **`LV_DISPLAY_RENDER_MODE_PARTIAL` + custom flush cb + custom buffer
   = silent all-zero frames.** Use FULL. This was the hardest bug in
   Phase 0 and there is NO log message that hints at it.

3. **Zephyr's `lvgl_rounder_cb_mono` clamps area x to the display
   driver's native `x_resolution`.** If you have swapped LVGL's
   resolution, that clamp puts area outside the logical space. Remove
   it via `lv_display_remove_event_cb_with_user_data(disp,
   lvgl_rounder_cb_mono, disp)`.

4. **Byte-level bit reversal is required, not color inversion.**
   `sharp,ls0xx` sets `SPI_TRANSFER_LSB` and does NOT set
   `SCREEN_INFO_MONO_MSB_FIRST` → LSB-first per byte. LVGL is
   MSB-first. Color polarity happens to already match (bit=1 → white
   on both sides), so no `~byte` invert.

5. **LVGL I1 buffer layout** = `[8 bytes I1 palette][MSB-first packed
   pixels]`. Skip the 8 bytes before reading pixel data. The palette
   is at the start of the buffer, not stored separately.

6. **Peripheral cannot re-raise layer/profile/endpoint events.** The
   `ZMK_EVENT_IMPL` for these events is compiled only on central.
   Handle the raw relay event and dispatch by name string.

7. **`zmk_ble_active_profile_changed.profile` is a pointer** — on the
   peripheral it's a central-side address and unsafe to dereference.
   Use `.index` only.

8. **Relay identifier length**: `CONFIG_ZMK_SPLIT_RELAY_EVENT_TYPE_NAME_LEN`
   is compared against `sizeof(identifier_string)` which includes the
   trailing null. A 4-char identifier needs `LEN >= 5`. We set 8.

9. **The `firmware/` directory is `.gitignore`d.** Committing built
   `.uf2` requires `git add -f`. Both halves' binaries are checked in
   on this branch because users flash them directly.

---

## 5. Verified-working configuration

| Thing | Value | Where |
|---|---|---|
| ZMK | `cormoran/zmk main+dya` (Zephyr 4.1) | `config/west.yml` |
| LVGL | v9.3.0 | `modules/lib/gui/lvgl/lv_version.h` |
| Panel driver | Zephyr `sharp,ls0xx` | overlay |
| SPI | `spi1` on nRF, LSB, CS ActiveHIGH, 1 MHz | `aerogu38_left.overlay` |
| LCD wiring | D0=CS, D4=MOSI, D5=SCK, VCC=3V3 | (beekeeb breakout) |
| LVGL color format | `LV_COLOR_FORMAT_I1` | Zephyr LVGL init, we re-affirm |
| Render mode | `LV_DISPLAY_RENDER_MODE_FULL` | `portrait_display_init` |
| Logical resolution | 68 × 160 | `portrait_display.h` |

---

## 6. How to build & flash locally

```bash
cd zmk-workspace
# Left (peripheral) - has the LCD
west build -s zmk/app -d .build/aerogu38_left -p \
  -b xiao_ble/nrf52840/zmk -- \
  -DSHIELD="aerogu38_left rgbled_adapter" \
  -DZMK_CONFIG=$PWD/../zmk-keyboard-aerogu38/config \
  -DZMK_EXTRA_MODULES=$PWD/../zmk-keyboard-aerogu38

# Right (central) with Prospector adv + Studio RPC
west build -s zmk/app -d .build/aerogu38_right -p \
  -b xiao_ble/nrf52840/zmk -S studio-rpc-usb-uart -- \
  -DSHIELD="aerogu38_right rgbled_adapter" \
  -DZMK_CONFIG=$PWD/../zmk-keyboard-aerogu38/config \
  -DZMK_EXTRA_MODULES=$PWD/../zmk-keyboard-aerogu38

# uf2's land in .build/*/zephyr/zmk.uf2 - copy to firmware/ or flash directly
```

CI (`.github/workflows/build.yml`) also produces the same variants
plus `aerogu38_right` (Prospector disabled) and `settings_reset`.

Flash by double-tapping the XIAO reset button and dropping the uf2
onto the mounted `XIAO-BOOT` volume.

---

## 7. Verification checklist for the next session

You come back to a hardware setup that has just been flashed with the
current binaries. Confirm each in order; if one fails, don't proceed
to the next.

- [ ] **Left half boots and LCD lights up.** Look for the notification
      panel - header logo at top, "L 0" layer text, some battery
      percentage.
- [ ] **Left battery reads a plausible number.** Should stabilise
      within ~60s of boot. If stuck at "L --%" the battery event
      isn't firing (see peripheral logs if you can attach a serial
      console, or reset).
- [ ] **Layer changes update the "L N" label.** Press-and-hold a layer-
      tap key; the number should change. Release; it should revert.
- [ ] **Endpoint label reflects USB vs BT.** Plug the right half into
      USB → label should switch to `USB` within a second. Unplug →
      revert to `BT N`.
- [ ] **BT profile change updates the label.** In BT mode, run whatever
      combo swaps profile 0↔1 in the keymap and confirm `BT 0` →
      `BT 1`.

If all pass, Phase 2 is verified. Commit the firmware bump (nothing
should change; the sources are unmodified) and move to Phase 3.

---

## 8. What's left to do

### Phase 3 (near-term wishlist)

- **Central battery relay.** Not straightforward — the peripheral
  already subscribes to `zmk_battery_state_changed` for its own
  battery. To relay the central's own battery separately, either:
  1. Define a custom event type on both sides, relay that, dispatch
     to a separate widget updater.
  2. Add a `source` byte to a synthesised payload.
  3. Use `zmk_peripheral_battery_state_changed` (central-side event
     that fires when it receives peripheral battery) - unclear if
     directly relayable.
  Option 1 is cleanest. See `boards/shields/aerogu38/central_relay.c`
  for the ergonomics of the ZMK relay macros.

- **Modifier state widget.** Central-only event
  `zmk_modifiers_state_changed` (uint8 flags LSFT/LCTL/LALT/LGUI + R*).
  High-frequency — every keystroke fires it — so throttle in the
  central sender or coalesce updates. The placeholder text is
  `- - - -`; wire up to show `S C A W` in some form.

- **Extract to `zmk-widget-sharp-memory-lcd` module.** The seed
  directory `boards/shields/aerogu38/lcd/` already contains
  `portrait_display.{h,c}` with zero aerogu-specific dependencies.
  Move to a stand-alone west module. Add per-orientation Kconfig
  choices and per-theme layout files as originally planned in
  `docs/lcd-ui-research.md`.

### Nice-to-have polish

- Regenerate the header logo at a bigger vertical footprint (currently
  68×20 which reads OK but has some pixel drop-out at 18px scaled
  from the 742-px-tall source). Maybe crop the "Aerogu" text alone.

- Font choice: `LV_FONT_UNSCII_16` is used for the "L N" and "BT N"
  labels. It's readable but blocky. If a nicer bitmap font at 12-14px
  is available in LVGL v9 built-ins, evaluate.

- Idle / activity-driven behavior. Sharp Memory LCD is retention-only
  so nothing bad happens if we don't update - could dim / show a
  splash on `zmk_activity_state_changed`.

- Central-battery-history integration (DYA Studio) already stores
  historical values; a mini-graph widget could be interesting.

---

## 9. Development workflow tips for the next session

- Watch out for **implicit state you'd inherit** when the hardware is
  already flashed: an untimely reset can strand LVGL in a weird
  intermediate state. If widgets look wrong, hold reset and re-flash.

- If you touch `portrait_display.c` or the flush cb, **rebuild BOTH
  halves and pair-flash**. LVGL is only on the left, but relay
  identifier config changes affect the right too.

- The Phase 0 diagnostic history in the branch's git log is worth
  skimming if you ever have to debug the flush pipeline again — the
  step-by-step tests are all captured in commit messages / narrative
  in the earlier commits, but only the finished code was preserved.

- `docs/sharp-memory-lcd-integration-guide.md` §6 has all the bit-
  format gotchas condensed into a reference table. Consult before
  writing new pixel-touching code.

- ZMK's split relay is macro-based — grepping `ZMK_RELAY_EVENT_` in
  the workspace's `zmk/app/include/zmk/event_manager.h` gives the
  full contract.

---

## 10. Contact / disclaimers

- All the work here is on the `feat/lcd-portrait-notification` branch;
  the `main` branch of the aerogu38 repo is untouched and remains the
  distributed base implementation.
- Firmware binaries committed under `firmware/` are **advisory**;
  regenerate from source before shipping.
- This file (`HANDOFF.md`) will be deleted in the merge commit. Don't
  reference it from long-lived docs or PR descriptions.
- Everything designed to migrate cleanly to
  `zmk-widget-sharp-memory-lcd`; keep new code in
  `boards/shields/aerogu38/lcd/` as much as possible.

Good luck. — previous Claude Code session
