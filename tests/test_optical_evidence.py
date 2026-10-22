"""PG-01 optical evidence regressions; no cameras, photos of people or cloud access."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from desktop.optical import (
    Arrival, OpticalBenchWriter, OpticalError, TimebaseHealth,
    compare_receive_cadence, verify_optical_bench,
)


def fake_jpeg(value=b"a"):
    """Test-only fake JPEG byte boundaries, not actual captured equipment imagery."""
    return b"\xff\xd8" + value * 64 + b"\xff\xd9"


def arrival(station,ns,index=0):
    return Arrival(station,index,"2026-10-22T11:34:00.000Z",ns)


class CameraEvidenceTests(unittest.TestCase):
    def test_exclusive_local_capture_and_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/"BENCH_OPTICAL_A_TEST"
            recorder=OpticalBenchWriter(folder,"A",0,"Test Operator")
            self.assertTrue(recorder.append(fake_jpeg(),arrival("A",500_000_000)))
            self.assertFalse(recorder.append(fake_jpeg(b"b"),arrival("A",600_000_000)))
            self.assertTrue(recorder.append(fake_jpeg(b"c"),arrival("A",800_000_000)))
            summary=recorder.close()
            self.assertEqual(summary["frame_count"],2)
            self.assertTrue((folder/"frame_00000.jpg").is_file())
            self.assertEqual(verify_optical_bench(folder)["frames"],2)
            self.assertFalse(verify_optical_bench(folder)["camera_exposure_timing_verified"])
            with self.assertRaises(FileExistsError):
                OpticalBenchWriter(folder,"A",0,"Test Operator")
            with self.assertRaises(OpticalError):
                recorder.append(fake_jpeg(),arrival("A",1_200_000_000))

    def test_tampered_frame_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/"BENCH_OPTICAL_B_TEST"
            recorder=OpticalBenchWriter(folder,"B",1,"Test Operator")
            recorder.append(fake_jpeg(),arrival("B",1000,1))
            recorder.close()
            frame=folder/"frame_00000.jpg"
            frame.write_bytes(fake_jpeg(b"q"))
            with self.assertRaises(OpticalError):
                verify_optical_bench(folder)

    def test_tampered_manifest_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/"BENCH_OPTICAL_B_TEST"
            recorder=OpticalBenchWriter(folder,"B",1,"Operator")
            recorder.close()
            (folder/"manifest.json").write_bytes(b"{}")
            with self.assertRaises(OpticalError):
                verify_optical_bench(folder)

    def test_no_silent_overwrite_or_wrong_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/"BENCH_OPTICAL_A"
            recorder=OpticalBenchWriter(folder,"A",2,"Operator")
            with self.assertRaises(OpticalError):
                recorder.append(fake_jpeg(),arrival("B",100,2))
            with self.assertRaises(OpticalError):
                recorder.append(fake_jpeg(),arrival("A",100,1))
            recorder.close()

    def test_reject_bad_camera_parameters(self):
        with tempfile.TemporaryDirectory() as tmp:
            for station,index in (("X",0),("A",8),("A",-1),("A",False)):
                with self.assertRaises(OpticalError):
                    OpticalBenchWriter(Path(tmp)/"BENCH_OPTICAL_FAIL",station,index,"Tester")


class TimingEvidenceTests(unittest.TestCase):
    def test_clock_health_never_claims_sync(self):
        a,b=TimebaseHealth(8),TimebaseHealth(8)
        for ts in [100_000_000,225_000_000,350_000_000,480_000_000]:
            self.assertTrue(a.note(ts))
        for ts in [200_000_000,350_000_000,500_000_000,800_000_000]:
            self.assertTrue(b.note(ts))
        status=compare_receive_cadence(a,b)
        self.assertTrue(status["shared_host_monotonic_clock"])
        self.assertFalse(status["cross_station_synchronized"])
        self.assertIsNone(status["camera_exposure_offset_ns"])
        self.assertEqual(status["station_a"]["state"],"HOST ARRIVALS ONLY")
        self.assertGreater(status["station_b"]["delayed_intervals"],0)

    def test_duplicate_and_reverse_receipts_rejected(self):
        h=TimebaseHealth()
        self.assertTrue(h.note(100))
        self.assertFalse(h.note(99))
        self.assertFalse(h.note(100))
        self.assertEqual(h.faults,2)
        self.assertEqual(h.summary()["state"],"INSUFFICIENT FRAMES")

    def test_invalid_clock_inputs(self):
        h=TimebaseHealth()
        for ts in (-1,1.3,"1"):
            with self.assertRaises(OpticalError):
                h.note(ts)


if __name__=="__main__":
    unittest.main()
