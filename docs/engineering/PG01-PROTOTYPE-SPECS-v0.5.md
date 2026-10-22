# PG-01 Engineering | Prototype Specifications v0.5

[Main README](../../README.md) | [Blueprints](PG-01-BLUEPRINTS.md) | [Console](../../console/README.md) | [Safety](../safety/safety.md)

**STATUS: DESIGN REVIEW. NOT ASSEMBLED OR APPROVED FOR PHYSICAL TESTING.** PG-01 is an instrumentation project, not a teleportation apparatus. No actual object transfer has been demonstrated.

## Diagram of the selected concept

Station A: load cell -> HX711 -> Pico 2 -> USB -> local DPN PC
Station B: independent load cell -> HX711 -> Pico 2 -> USB -> same local PC
Witness cameras: standard USB cameras -> PC directly
PC: local read-only console; v0.5 currently SYNTHETIC ONLY and does not ingest USB devices or video.

**Important:** A Raspberry Pi Pico 2 microcontroller cannot directly host the CSI-2 interface of a Raspberry Pi Camera Module 3. Use a supported USB webcam connected to a PC, or separate camera-capable SBC, with compatibility reviews.

## Physical concept (NOT fabrication dimensions)

| Feature | Draft target | Must verify before constructing |
|---|---|---|
| Each station enclosure | Approx. 250 x 250 x 300 mm | Transparent, accessible, stable and inspectable material |
| Mass platform | Approx. 120 x 120 mm | Load-cell mount geometry and stable support |
| Sample range | Proposed 20–250 grams | Reference masses, calibration and uncertainty |
| Load-cell capacity | Candidate 5kg straight bar | Capacity does not imply resolution or accuracy |
| Power | Commercial USB-low-voltage | Total current and logic-level compatibility |
| Data link | Separate USB connections to PC | Isolation, timestamps and clock-offset uncertainty |

These draft envelopes are illustrative, not build-ready CAD or toleranced manufacturing drawings.

## Candidate parts with 2026-10-22 USD price anchors

| Qty | Hardware | Verified vendor reference | Example per unit | Status |
|---|---|---|---|---|
| 2 | Raspberry Pi Pico 2 | https://www.raspberrypi.com/products/raspberry-pi-pico-2/ | ~$5 original launch MSRP | Candidate only |
| 2 | SparkFun HX711 load-cell amplifier SEN-13879 | https://www.sparkfun.com/sparkfun-load-cell-amplifier-hx711.html | $4.95 | Candidate only |
| 2 | SparkFun TAL220B 5kg load cell SEN-14729 | https://www.sparkfun.com/load-cell-5kg-straight-bar-tal220b.html | $15.50 | Candidate only |
| 2 | PC-compatible USB webcam | Verify hardware/OS support | TBD | Not selected |
| 2 | Transparent housing, stable platform, mechanical fasteners | Material and dimensions TBD | TBD | Not selected |
| 2 | Rated USB cable/power protections | Electrical design not final | TBD | Not selected |
| 1+ | Suitable reference-mass set | Calibration requirements TBD | TBD | Not selected |

Known component subtotal, two bare electronics endpoints: approximately **$50.90**, before PC, cameras, cases, mechanical mounting, reference masses, protection, cables, taxes and shipping. It is not a complete prototype cost quotation or shopping authorization.

## Signal and pin map — proposed, no power connections authorized

| Physical interface | Proposed connection | Meaning |
|---|---|---|
| Load cell Exc+ / Exc- | HX711 E+ / E- | Bridge supply; confirm labels |
| Load cell Sig+ / Sig- | HX711 A+ / A- | Differential sensor; check datasheets rather than colors |
| HX711 DOUT | Pico 2 GP14, physical pin 19 | Data input candidate |
| HX711 SCK | Pico 2 GP15, physical pin 20 | Clock output candidate |
| HX711 GND | Pico 2 GND (common) | Digital reference |
| HX711 VDD digital | 3.3V regulated, ONLY if confirmed for exact board | Keep Pico GPIO 3.3V-safe |
| HX711 VCC analog | **Unassigned** pending qualified review | Analog bridge supply: do not guess |
| Pico USB | Local host USB | Proposed future serial telemetry |

Different HX711 carrier boards expose different power pins. In SparkFun's board VCC is analog excitation, VDD digital interface; never assume another HX711 breakout shares that pinout. Do not energize a circuit until all electrical connections, current limits, GPIO levels and mounting are verified. **No physical wiring is attempted by this repository.**

References:
- Pico 2 pinout: https://datasheets.raspberrypi.com/pico/Pico-2-Pinout.pdf
- Pico 2 documentation: https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html
- HX711 vendor guide: https://learn.sparkfun.com/tutorials/load-cell-amplifier-hx711-breakout-hookup-guide
- HX711 SparkFun product page: https://www.sparkfun.com/sparkfun-load-cell-amplifier-hx711.html
- 5kg load-cell details: https://www.sparkfun.com/load-cell-5kg-straight-bar-tal220b.html

## Responsible development gates

1. Run synthetic console and verify it never edits actual experiment records.
2. Approve exact board revision, voltages, enclosure CAD, mounting, independent video placement and cable routing.
3. Implement Pico firmware and serial transport with documented IDs, sequence numbers and calibration offsets in a **separate PR**.
4. Implement host serial parser with strict source labels and failure flags in a **separate PR**.
5. Independently review safety and preregister null/control protocol before any real physical experiment.

**No working object-transfer mechanism, experimental data or physical prototype is claimed.**
