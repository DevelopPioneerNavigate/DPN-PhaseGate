"""Native desktop scientific-model checks; does not require Qt or hardware."""
import json
import tempfile
import unittest
from pathlib import Path
from desktop.model import DISCLAIMER, export_demo, inventory, literature, simulated_samples, snapshot


class NativeModelTests(unittest.TestCase):
    def test_fixed_seed_is_deterministic(self):
        self.assertEqual(simulated_samples(123, 20), simulated_samples(123, 20))
        self.assertEqual(len(simulated_samples(123, 20)), 20)

    def test_invalid_sample_inputs(self):
        with self.assertRaises(ValueError):
            simulated_samples(-1)
        with self.assertRaises(ValueError):
            simulated_samples(100, 0)

    def test_telemetry_never_claims_physical_transfer(self):
        data = snapshot()
        self.assertEqual(data["mode"], "SYNTHETIC")
        self.assertFalse(data["hardware_connected"])
        self.assertFalse(data["physical_transfer_verified"])
        self.assertIn("NO OBJECT TELEPORTATION", data["disclaimer"])

    def test_missing_files_not_invented_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(inventory(Path(tmp))["sources"])
            self.assertEqual(literature(Path(tmp)), [])

    def test_export_guard_and_no_manifest_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            with self.assertRaises(ValueError):
                export_demo(path / "REAL_run.json", 15)
            target = path / "SYNTHETIC_test.json"
            export_demo(target, 15)
            payload = json.loads(target.read_text())
            self.assertEqual(payload["telemetry"]["mode"], "SYNTHETIC")
            self.assertIn("NOT RESEARCH EVIDENCE", payload["provenance"])
            self.assertEqual(list(path.glob("*")), [target])


if __name__ == "__main__":
    unittest.main()
