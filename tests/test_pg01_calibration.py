"""Synthetic regression fixtures are never actual experiment results."""
import hashlib
import os
import tempfile
import unittest
from pathlib import Path

from tools.pg01_calibration import calibration_file, file_sha256, fit_calibration, main


class Pg01CalibrationTests(unittest.TestCase):
    def test_exact_known_linear_calibration(self):
        points = [{"reference_g": x, "raw_counts": 500 + 100*x}
                  for x in (0, 10, 20, 30, 30)]
        report = fit_calibration(points)
        self.assertAlmostEqual(report["slope_counts_per_g"], 100)
        self.assertAlmostEqual(report["intercept_counts"], 500)
        self.assertAlmostEqual(report["residual_rms_counts"], 0, places=8)
        self.assertEqual(report["reference_levels"], 4)
        self.assertEqual(report["sample_count"], 5)

    def test_no_reference_variation_is_rejected(self):
        with self.assertRaises(ValueError):
            fit_calibration([{"reference_g": 10, "raw_counts": 10} for _ in range(8)])

    def test_insufficient_levels_rejected(self):
        with self.assertRaises(ValueError):
            fit_calibration([{"reference_g": x, "raw_counts": x*10} for x in (0, 0, 10, 10)])

    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):
            fit_calibration([{"reference_g": x, "raw_counts": y} for x,y in [(0,0),(1,1),(2,2),(3,"NaN")]])

    def test_negative_mass_rejected(self):
        with self.assertRaises(ValueError):
            fit_calibration([{"reference_g": x, "raw_counts": x} for x in (-1,0,1,2)])

    def test_csv_and_digest(self):
        data = b"reference_g,raw_counts\n0,500\n10,1500\n20,2500\n30,3500\n"
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "cal.csv"
            path.write_bytes(data)
            self.assertAlmostEqual(calibration_file(path)["slope_counts_per_g"], 100)
            self.assertEqual(file_sha256(path), hashlib.sha256(data).hexdigest())
            self.assertEqual(main(["calibrate", str(path)]), 0)

    def test_missing_csv_headers_error(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "bad.csv"
            path.write_text("x,y\n0,0\n", encoding="utf-8")
            self.assertEqual(main(["calibrate", str(path)]), 2)


if __name__ == "__main__":
    unittest.main()
