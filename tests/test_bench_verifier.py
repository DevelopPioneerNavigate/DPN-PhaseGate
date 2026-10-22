"""Offline bench validation checks (no physical devices required)."""
import json
import tempfile
import unittest
from pathlib import Path

from desktop.hardware import AcquisitionEvent, BenchRecorder, make_frame, parse_frame
from tools.verify_bench_capture import verify


class BenchVerifierTests(unittest.TestCase):
    def test_real_bench_file_structure_passes_without_science_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"BENCH_demo.jsonl"
            cap=BenchRecorder(path).open()
            for i in range(3):
                frame=parse_frame(make_frame("B",i,120+i*120,-20+i))
                cap.record(AcquisitionEvent(kind="sample",station="B",port="COM7",
                            session_id="session-1",sample=frame,
                            host_utc="2026-10-22T12:00:00.000Z",host_monotonic_ns=i+1))
            cap.close()
            result=verify(path)
            self.assertEqual(result["B_samples"],3)
            self.assertIn("NOT SCIENTIFIC VALIDATION",result["result"])

    def test_edit_after_hash_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"BENCH_demo.jsonl"
            cap=BenchRecorder(path).open()
            cap.close()
            path.write_bytes(path.read_bytes()+b"tampering\n")
            with self.assertRaises(ValueError):
                verify(path)

    def test_invalid_raw_sequence_rejected_even_with_new_hash(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"BENCH_demo.jsonl"
            cap=BenchRecorder(path).open()
            ev=AcquisitionEvent(kind="sample",station="A",port="COM3",session_id="s",
                    host_utc="2026-10-22T12:00:00.000Z",host_monotonic_ns=1,
                    sample=parse_frame(make_frame("A",1,111,123)))
            cap.record(ev)
            cap.record(ev)
            cap.close()
            with self.assertRaises(ValueError):
                verify(path)


if __name__=="__main__":
    unittest.main()
