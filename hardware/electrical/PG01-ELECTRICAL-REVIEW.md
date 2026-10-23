# PG-01 Rev A — Electronics and Power Review (Hold Point)

**Scope:** two isolated, low-voltage, read-only mass sensor endpoints + local USB cameras. This document is a review checklist, **not an instruction to energize an unreviewed circuit**.

## Required equipment verification

| Item | Verification before wiring | Recorded evidence |
|---|---|---|
| Controller A / B | Exact Raspberry Pi Pico 2 revision, datasheet, identified USB ports | Board photos, USB ID mapping, declared station A/B |
| HX711 A / B | Exact actual breakout supplier and revision; identify VDD, VCC, DAT, CLK, GND | Board schematic with reviewed supply levels |
| Load cell A / B | Physical model, rated load, pinout **verified by its own datasheet** | Certificate/spec and approved mount drawing |
| Cabling | Strain relief, no bare high-voltage conductors, appropriately-rated USB supply | Inspection results and cable schedule |
| Workstation cameras | Actual USB camera identifiers, access permissions and storage policy | Consent/retention log |
| PSU interface | Isolated power and fusing needs defined by electrical reviewer | Written sign-off **before** connection |

The current code **only uses Pico GP14 (data) and GP15 (clock)** as proposed signals. The final GPIO-to-board signal mapping must be verified from the *actual selected parts*; do not rely on wire colors alone. The Pico's board-generated logic rail is 3.3 V; digital input must never see an unreviewed 5 V signal. The manufacturer's HX711 breakout has separate analog VCC and digital VDD rails, and **the appropriate supply plan depends on the exact board revision**.

Sources: [Raspberry Pi Pico 2 datasheet](https://datasheets.raspberrypi.com/pico/pico-2-datasheet.pdf), [SparkFun HX711 hookup guide](https://learn.sparkfun.com/tutorials/load-cell-amplifier-hx711-breakout-hookup-guide/all?print=1), [SparkFun board schematic](https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/SparkFun_HX711_Load_Cell_v11.pdf). Do not apply another manufacturer's wiring by analogy without verifying the actual board.

## Logical diagram (power rail intentionally not connected)

```text
  load cell A  -- bridge wiring verified --> HX711 A -- DAT --> Pico 2 A GP14
                                                      -- CLK <-- Pico 2 A GP15
                                                              |
                                                USB (read-only frames)
                                                              |
                                               Native PhaseGate Hardware Lab
                                                              |
                                                BENCH raw captures only

  load cell B  -- independent, identical logical path --> Pico 2 B / USB

  Camera A    -- explicit consent --> native Optical Evidence Lab
  Camera B    -- explicit consent --> native Optical Evidence Lab

  POWER VCC / VDD / GND CONNECTIONS:   NOT APPROVED BY THIS DIAGRAM
  HIGH-ENERGY EMITTER / MAGNET SYSTEM: NOT PART OF PG-01 REV A
```

## Electrical inspection before powering any board

- Board silk-screen pin locations and physical orientation independently checked.
- Pico GP14/GP15 mapped to the intended HX711 DAT/SCK only after design review.
- Digital HX711 VDD compatible with **3.3 V** logic and ground reference measured.
- Board analog supply VCC and load-cell excitation selected within actual revision's ratings.
- No exposed 5 V or higher signal reaches Pico GPIO.
- Wiring continuity, polarity and isolation documented with the device **unpowered**.
- No powered linear motor, field coil, cryogenic equipment, laser or high-current cabinet.
- Two data streams labelled from the physical station and checked for USB swap and MCU reset.
- Low-voltage operation and mechanical guarding inspected before calibration masses are applied.

A reviewer must explicitly sign this checklist under engineering work package **WP-02** before further physical builds or powered measurement trials. The application's Build Lab self-reported progress is **not** independent approval.

## Safe initial test plan

G0: verify and approve the circuit offline. G1: empty-port visibility in Windows, no sensor manipulation. G2: single independent sensor at a time under approved power. G3: two stations with device swap controls. G4: reference mass, zero shift, drift/hysteresis, non-finite readings, disconnected sensor and USB fault-path characterization.

The native application presents live **raw counts** in Hardware Lab; measurements may only be called mass *estimates* when separately loaded with a reviewed in-range calibration profile, which is still marked unreviewed by the software.

**This is a practical engineering build plan.** A field aperture capable of transporting physical matter is not a known component or subsystem and must not be treated as if it has a purchasable coil specification.
