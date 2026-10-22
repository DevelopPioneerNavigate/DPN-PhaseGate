# PG-01 scale calibration and offline analysis

This is measurement engineering, not teleportation research evidence.

## Scientific baseline
NIST emphasizes characterizing actual weighing-system measurement uncertainty and repeatability; 24-bit ADC data are **not** equivalent to 24-bit calibrated physical mass accuracy. References SRC-010/011; ADC nominal sampling SRC-013.

## Proposed calibrations
1. Select and document calibrated reference masses appropriate to the sensor range; note certificate and uncertainty, temperature, warm-up and mounting.
2. Take repeated zero-reference readings, multiple nonzero reference levels, multiple repeated readings **across the intended operating range**, ascending and descending loading, and before/after each proposed measurement session.
3. Record **reference_g,raw_counts** in UTF-8 CSV, only with actual readings (synthetic fixtures are labeled).
4. Use independent hold-out validation points and estimate nonlinearity, repeatability, zero drift and reference mass uncertainty. A linear fit alone is inadequate as a full uncertainty statement.
5. Use `python tools/pg01_calibration.py calibrate calibration.csv` to fit raw counts per mass and report descriptive residual RMS and R². Check outliers, hysteresis and environmental effects separately.
6. Verify SHA-256 of the original file using `python tools/pg01_calibration.py sha256 calibration.csv`.

## Strict interpretation
- The software accepts a calibration CSV file, validates finite numeric rows and fits least-squares counts = slope*(reference_g)+intercept.
- Output labels are **descriptive statistics only**, not a metrological certificate or uncertainty budget.
- For safety and scientific integrity, no code triggers an 'object arrived' condition, and no measurement can be mistaken for physical portal success.
- See `examples/SYNTHETIC-pg01-calibration.csv` for test data, **not an experiment**.
