"""PG-01 Reference Event Lab tests; images are generated arrays, never real footage."""
import json
import tempfile
import unittest
from pathlib import Path

from desktop.optical import Arrival, OpticalBenchWriter
from desktop.reference_event import (
    ReferenceError, inspect_capture, find_flash, compare_reference_events,
    build_review, save_review,
)


def png_like_jpeg(level):
    import cv2
    import numpy as np
    frame=np.full((64,80,3),int(level),dtype=np.uint8)
    ok,out=cv2.imencode(".jpg",frame,[int(cv2.IMWRITE_JPEG_QUALITY),96])
    if not ok:
        raise AssertionError("OpenCV could not encode test fixture")
    return out.tobytes()


def make_capture(root,station,levels,base=2_000_000_000):
    folder=root/("BENCH_OPTICAL_"+station+"_SYNTHETIC_TEST")
    writer=OpticalBenchWriter(folder,station,0 if station=="A" else 1,"Synthetic Unit Test")
    for i,level in enumerate(levels):
        timestamp=base+i*300_000_000
        observed=Arrival(station,0 if station=="A" else 1,
                         "2026-10-22T11:00:00.000Z",timestamp)
        assert writer.append(png_like_jpeg(level),observed)
    writer.close()
    return folder


class ReferenceTests(unittest.TestCase):
    def test_pair_of_synthetic_flashes_only_host_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            a=make_capture(root,"A",[20]*7+[215]*5,2_000_000_000)
            b=make_capture(root,"B",[20]*8+[215]*4,2_000_000_000)
            result=build_review(a,b,region_a="FULL",region_b="FULL")
            comp=result["comparison"]
            self.assertEqual(comp["state"],"PAIR OF UNVERIFIED HOST RECEIPT TRANSITIONS")
            self.assertEqual(comp["station_a"]["onset"]["first_bright_index"],7)
            self.assertEqual(comp["station_b"]["onset"]["first_bright_index"],8)
            self.assertAlmostEqual(comp["host_first_bright_delta_ms"],300)
            self.assertIsNone(comp["actual_exposure_offset_ms"])
            self.assertIsNone(comp["physical_event_time_difference_ms"])
            self.assertFalse(comp["camera_clocks_synchronized"])
            self.assertFalse(comp["declared_shared_light_event_confirmed"])

    def test_flat_or_single_spike_is_inconclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            a=make_capture(root,"A",[24]*6+[242]+[24]*5)
            series=inspect_capture(a)
            result=find_flash(series)
            self.assertEqual(result["state"],"NO SUSTAINED REFERENCE EVENT")
            self.assertIsNone(result["onset"])

    def test_bad_station_pair_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            a=inspect_capture(make_capture(root,"A",[20]*7+[220]*4))
            with self.assertRaises(ReferenceError):
                compare_reference_events(a,a)

    def test_tampered_original_image_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            folder=make_capture(root,"B",[20]*7+[220]*4)
            (folder/"frame_00005.jpg").write_bytes(b"altered")
            with self.assertRaises(ReferenceError):
                inspect_capture(folder)

    def test_export_is_bench_only_and_exclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            a=make_capture(root,"A",[20]*7+[220]*4)
            b=make_capture(root,"B",[20]*7+[220]*4)
            report=build_review(a,b)
            out=root/"BENCH_REFERENCE_SyntheticOnly.json"
            digest=save_review(report,out)
            self.assertEqual(len(digest),64)
            payload=json.loads(out.read_text(encoding="utf8"))
            self.assertIsNone(payload["comparison"]["actual_exposure_offset_ms"])
            self.assertTrue(out.with_suffix(".sha256").is_file())
            with self.assertRaises(FileExistsError):
                save_review(report,out)
            with self.assertRaises(ReferenceError):
                save_review(report,root/"APPROVED_EXPERIMENT.json")

    def test_bad_regions_and_thresholds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            a=make_capture(root,"A",[20]*7+[230]*4)
            with self.assertRaises(ReferenceError):
                inspect_capture(a,"OUTSIDE")
            series=inspect_capture(a)
            with self.assertRaises(ReferenceError):
                find_flash(series,contrast=float("nan"))
            with self.assertRaises(ReferenceError):
                find_flash(series,contrast=101)


if __name__=="__main__":
    unittest.main()
