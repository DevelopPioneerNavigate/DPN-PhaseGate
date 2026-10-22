# PG-01 Paired Evidence Station Architecture v0.2
**Maturity:** paper architecture / integration design; **no functioning hardware built**.
**Purpose:** instrument claims with independent measurements and controlled null trials. **Neither station can physically teleport matter** using this design.

## System diagram
```text
                    REVIEWED, INDEPENDENT NETWORK
                (no actuation commands required for null trials)
                         +-------------------+
                         |  Audit computer   |
                         |  UTC + time-offset|
                         |  Evidence hashing |
                         |  Read-only copies |
                         +-----+---------+---+
                               |         |
             Station A         |         |           Station B
+------------------------------+--+ +----+------------------------------+
| Inspected open-access enclosure | | Inspected open-access enclosure   |
| Distinct camera 1 + witness view | | Distinct camera 1 + witness view  |
| Load-cell/ADC, reference mass    | | Load-cell/ADC, reference mass     |
| Visible event indicator/clock    | | Visible event indicator/clock     |
| Low-voltage power and disconnect | | Low-voltage power and disconnect  |
| Local append-only event journal  | | Local append-only event journal   |
+----------------------------------+ +-----------------------------------+
```
All instrumentation and transport paths must be physically inspectable. Do not install a hidden route between stations. Data network transfers only timestamps and sensor information. Independent witness views may be stored separately from each station.

## Candidate part families (not purchases)
| Subsystem | Qty | Starting component category | Selection requirements | Limits |
|---|---:|---|---|---|
| Controller | 2 | Raspberry Pi SBC or microcontroller with logger | Documentation, regulated rated PSU, UTC/time diagnostics | Platform selection pending |
| Camera | 2–4 | Raspberry Pi Camera Module 3 or supported USB camera | Independent full enclosure views; verified metadata/timestamps | 12MP does not imply timing accuracy; source SRC-012 |
| Mass sensor | 2 | Load cell with mounting and reference masses | Calibratable range, mechanical stability, uncertainty record | Sensor to be selected |
| Mass ADC | 2 | HX711-compatible module | Correct **controller logic levels**, manufacturer documentation | Nominal 10/80 SPS (SRC-013); not a nanosecond sensor |
| Temperature | 2 | Ordinary digital thermometer/humidity sensor | Units and logged drift | Cannot prove transfer |
| Mechanical enclosure | 2 | Transparent inspectable non-hazardous container | No occluded passages, stable scale support | Dimensions pending |
| Power | 2 | Certified low-voltage regulated supply | Voltage/current budget, protection, accessible disconnect | No custom HV |
| Witness device | 1–2 | Independent camera or clock | Independent operator, continuous frame coverage | Out-of-band verification |

## Synchronization and chain-of-custody
- Log **UTC ISO-8601 with offset + monotonic nanoseconds** at every sensor event. Monotonic is local only: never directly compare independent monotonic epochs.
- Measure each station's UTC clock error and drift using a documented common reference. Compare event ordering only with uncertainty intervals that include clock error plus camera exposure/sampling latency.
- Use append-only event files on separate station devices, independent video streams, and a hashed after-run evidence manifest.
- A SHA-256 digest detects later byte changes but **does not** establish source truth or an incorruptible original; pair with witness controls and immutable external storage.
- Select wired network for repeatability where practical. No remote command is needed during baseline null trials.

## Interface concept
```text
scale samples       -> timestamped CSV [sample_id,station,utc,monotonic_ns,counts]
calibration records -> calibrated-reference CSV [reference_g,raw_counts]
video evidence      -> original files with timestamps, camera ID and SHA-256
trial journal       -> blinded sample/tag ID, sham/control flags, observations
evidence register   -> existing experiments manifest only after real approved work
```

## Design review gates
- Freeze selected loads, cables, controller logic voltage, camera connector compatibility and firmware versions before ordering.
- Resolve electrical protection, enclosure integrity, clock-offset errors, load-cell mounting and true uncertainty experimentally.
- Pass baseline false-positive and anti-substitution challenges before attempting to interpret anomalies.
- [PG-PROT-NULL-001](../protocols/PG-PROT-NULL-001.md) remains a **draft**, not permission to conduct it.
