"""Regression tests for PG-01 station calibrations and witness custody."""
import hashlib
import json
import tempfile
import unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path

from desktop.calibration import (
    CalibrationError, estimate, fit, load_profile, parse_worksheet,
    save_profile, validate_profile,
)
from desktop.witness import (
    WitnessError, inventory_source, save_inventory, verify_inventory,
)


def records():
    # Synthetic numerical example only — no actual reference masses were measured.
    return [(0,1000),(0,1003),(50,501010),(50,500990),
            (100,1001050),(100,1000970)]


class CalibrationTests(unittest.TestCase):
    def fitted(self,at=None):
        return fit(records(),"A",0.01,"SYNTHETIC-REF-NOT-CERTIFIED",
                   "Synthetic Unit Test",at=at)

    def test_valid_fit_and_estimate(self):
        p=self.fitted()
        self.assertEqual(p["stage"],"BENCH_ESTIMATE_UNREVIEWED")
        self.assertEqual(p["sample_count"],6)
        self.assertGreater(p["fit_r_squared"],.999)
        v=estimate(p,501000,"A")
        self.assertAlmostEqual(v["estimate_g"],50,delta=.1)
        self.assertIn("NOT CERTIFIED",v["label"])

    def test_station_mismatch_and_no_extrapolation(self):
        p=self.fitted()
        with self.assertRaises(CalibrationError):
            estimate(p,501000,"B")
        with self.assertRaises(CalibrationError):
            estimate(p,5000000,"A")

    def test_expiration_future_and_checksum(self):
        past=datetime.now(timezone.utc)-timedelta(days=90)
        p=self.fitted(at=past)
        with self.assertRaises(CalibrationError):
            validate_profile(p)
        current=self.fitted()
        current["offset_g"]+=25
        with self.assertRaises(CalibrationError):
            validate_profile(current)

    def test_replicated_three_mass_gate(self):
        with self.assertRaises(CalibrationError):
            fit([(0,10),(0,11),(50,1000),(100,3000),(100,3001),(100,3002)],
                "A",.1,"CERT-1234","Research Operator")
        with self.assertRaises(CalibrationError):
            fit([(0,10)]*6,"A",.1,"CERT-1234","Research Operator")

    def test_finite_and_signed_24bit_gate(self):
        with self.assertRaises(CalibrationError):
            fit([(mass, float("nan")) for mass,_ in records()],
                "A",.1,"CERT-1234","Research Operator")
        with self.assertRaises(CalibrationError):
            fit(records(),"A",0,"CERT-1234","Research Operator")

    def test_profile_file_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"BENCH_CAL_A.json"
            save_profile(self.fitted(),path)
            self.assertEqual(load_profile(path,"A")["station"],"A")
            with self.assertRaises(FileExistsError):
                save_profile(self.fitted(),path)

    def test_csv_roundtrip_and_hash(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"SYNTHETIC_worksheet.csv"
            p.write_text("reference_g,raw_counts\n"+ "".join(
                f"{mass},{raw}\n" for mass,raw in records()),encoding="utf-8")
            rows,h=parse_worksheet(p)
            self.assertEqual(rows,[(float(a),b) for a,b in records()])
            self.assertEqual(h,hashlib.sha256(p.read_bytes()).hexdigest())


class WitnessTests(unittest.TestCase):
    def test_witness_hash_without_copy(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            source=root/"witness_cam.jpg"
            source.write_bytes(b"synthetic witness bytes for unit test")
            entry=inventory_source(source,"B","Test Operator",
                    "Synthetic visual sample, unknown device time",
                    consent_confirmed=True)
            self.assertFalse(entry["recording_time_verified"])
            self.assertFalse(entry["contents_copied"])
            target=root/"BENCH_WITNESS_station_b.json"
            save_inventory(entry,target)
            self.assertTrue(verify_inventory(target,source)["source_media_verified_again"])
            source.write_bytes(b"tampered footage")
            with self.assertRaises(WitnessError):
                verify_inventory(target,source)

    def test_consent_is_required_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            source=root/"sample.png"
            source.write_bytes(b"sample")
            with self.assertRaises(WitnessError):
                inventory_source(source,"A","Test Operator",
                                 "Unknown recording time and origin",False)
            entry=inventory_source(source,"A","Test Operator",
                                   "Synthetic demo without known time",True)
            target=root/"BENCH_WITNESS_evidence.json"
            save_inventory(entry,target)
            with self.assertRaises(FileExistsError):
                save_inventory(entry,target)

    def test_manifest_tampering_detected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            source=root/"test.jpg"
            source.write_bytes(b"test")
            entry=inventory_source(source,"A","Test Operator",
                                   "Local sample, unknown camera clock",True)
            target=root/"BENCH_WITNESS_audit.json"
            save_inventory(entry,target)
            target.write_text(target.read_text()+"\n",encoding="utf-8")
            with self.assertRaises(WitnessError):
                verify_inventory(target)


if __name__=="__main__":
    unittest.main()
