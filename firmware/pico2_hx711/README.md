# PG-01 Pico 2 MicroPython sensor program

**Only for appropriately inspected, low-voltage HX711 measurement circuitry.**
This does **not** build a portal or teleport an object.

## What is shipped
- \`main.py\`: emits bounded raw 24-bit signed HX711 readings over Pico 2 USB serial, approx. 10 Hz.
- Station identity must be manually set to **A** or **B**, one per actual board.
- Protocol \`PG1|A|sequence|uptime_ms|signed_counts|RAW|XOR_HEX\\n\`.
- XOR checksum detects some accidental transmission damage. It does **not** authenticate station hardware or prevent tampering.
- **No commands accepted** by the firmware. No lights, power switching, or control of connected electrical equipment.

## Safe flashing procedure
1. Review the exact Pico 2 and *actual HX711 board revision* with a qualified person before any wiring or power. Check ground reference, the digital signal high voltage **must remain 3.3V-safe**, and board VDD/VCC division if present.
2. Obtain [MicroPython Pico 2 firmware](https://micropython.org/download/RPI_PICO2/) and [official Raspberry Pi Pico 2 documentation](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html). Firmware compatibility may vary; use documented UF2 flashing procedure.
3. On your computer, use Thonny/REPL or an equivalent trusted local development tool to copy this file to the board as \`main.py\`.
4. For the second physical board, change \`STATION_ID = "B"\` first. **Do not connect both boards under the same station ID.**
5. Physically inspect and record that each USB port corresponds to the intended station. Do not infer device authenticity from the ID emitted by software.
6. In the native Windows app, use **Hardware Lab → Refresh Ports**, explicitly select the COM ports, then connect. The app never sends commands to the boards.

## Candidate signal pins (power wiring intentionally excluded)
- HX711 DAT → Pico GP14 (board pin 19)
- HX711 SCK → Pico GP15 (board pin 20)
- Common GND only after board power and safety design review.
- Load-cell bridge to HX711 A+/A-/E+/E- using manufacturer-verified lead identification.
- **Analog HX711 supply and board power are not specified by this file.** Supply choice requires board revision verification and qualified safety review. Never connect Pico GPIO directly to unverified 5V signals.

## Known engineering limitations
- This is bit-bang MicroPython research firmware, not a hard-real-time or metrology-certified driver.
- The data represent **uncalibrated ADC counts**, not grams or a physical transport event.
- A Pico reset can cause sequence and uptime rollback: the host parser fails closed and requires manual reconnection.
- Pico millisecond uptime and host UTC capture time are not synchronized clocks. **No event-time comparisons between stations can be inferred accurately from these values alone.**
- Data flow may be interrupted by REPL messages, cable removal, MCU resets, buffer overruns or USB scheduler jitter. These must be recorded as anomalies, not physical effects.
- The host logs the port label and reported station ID, but USB port identity is not cryptographically authenticated.

## Research integrity
All USB captures go only into clearly labeled \`BENCH_*.jsonl\` with a SHA-256 sidecar, **never** into the approved scientific experiment manifest. This requires deliberate user initiation. A checksum plus file hash cannot establish the authenticity of a claimed physics observation.
