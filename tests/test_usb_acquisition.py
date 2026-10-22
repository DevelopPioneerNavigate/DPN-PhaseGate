"""PG-01 parser, hostile input, fake-device, and bench integrity tests."""
import hashlib
import json
import queue
import tempfile
import threading
import time
import unittest
from pathlib import Path

from desktop.hardware import (
    AcquisitionEvent, BenchRecorder, FrameError, SerialReader,
    MAX_FRAME_BYTES, make_frame, parse_frame,
)


class ProtocolTests(unittest.TestCase):
    def test_two_stations_and_sign_conversion(self):
        for station in ("A", "B"):
            for raw in (-8388608, -1, 0, 11, 8388607):
                data = parse_frame(make_frame(station, 42, 12345, raw), station)
                self.assertEqual((data.station, data.sequence, data.raw_counts),
                                 (station, 42, raw))

    def test_corruption_and_mismatched_station_rejected(self):
        message = make_frame("A", 5, 123, -11)
        with self.assertRaises(FrameError):
            parse_frame(message, "B")
        with self.assertRaises(FrameError):
            parse_frame(message.replace(b"-11", b"-12"), "A")
        with self.assertRaises(FrameError):
            parse_frame(message[:-1], "A")
        with self.assertRaises(FrameError):
            parse_frame(message + b"\0", "A")
        with self.assertRaises(FrameError):
            parse_frame(b"X"*(MAX_FRAME_BYTES+1), "A")
        with self.assertRaises(FrameError):
            parse_frame(b"PG1|A|x|0|1|RAW|00\n", "A")

    def test_build_rejects_out_of_range_counts(self):
        with self.assertRaises(ValueError):
            make_frame("A", 1, 10, 8388608)
        with self.assertRaises(ValueError):
            make_frame("B", 1, 10, -8388609)


class FakePort:
    def __init__(self, chunks):
        self.chunks = list(chunks)
        self.closed = False

    def read(self, size):
        if self.chunks:
            return self.chunks.pop(0)
        time.sleep(.01)
        return b""

    def close(self):
        self.closed = True


class ReaderTests(unittest.TestCase):
    def test_mock_port_and_sample(self):
        events = queue.Queue(maxsize=100)
        stream = make_frame("A",0,123,125)+make_frame("A",1,240,126)
        fake=FakePort([stream[:12], stream[12:]])
        reader=SerialReader("A","COM_TEST",events,serial_factory=lambda *a,**kw:fake)
        reader.start()
        limit=time.monotonic()+2
        while reader.last_frame is None or reader.last_frame.sequence != 1:
            if time.monotonic()>limit:
                self.fail("reader did not accept fake port samples")
            time.sleep(.01)
        reader.stop()
        kinds=[]
        while not events.empty():
            kinds.append(events.get().kind)
        self.assertEqual(kinds.count("sample"),2)
        self.assertTrue(fake.closed)

    def test_sequence_gap_detected(self):
        events=queue.Queue(maxsize=100)
        fake=FakePort([make_frame("A",0,10,10)+make_frame("A",3,300,11)])
        reader=SerialReader("A","COM_FAKE",events,serial_factory=lambda *a,**kw:fake)
        reader.start()
        timeout=time.monotonic()+2
        while reader.last_frame is None or reader.last_frame.sequence!=3:
            if time.monotonic()>timeout:
                self.fail("no second sample")
            time.sleep(.01)
        reader.stop()
        self.assertEqual(reader.gaps,2)
        self.assertTrue(any(x.kind=="error" for x in list(events.queue)))

    def test_overflow_does_not_deliver_fake_sample(self):
        events=queue.Queue(maxsize=100)
        fake=FakePort([b"Q"*200+b"\n"])
        reader=SerialReader("A","COM_FAKE",events,serial_factory=lambda *a,**kw:fake)
        reader.start()
        time.sleep(.08)
        reader.stop()
        self.assertEqual(reader.last_frame,None)


class RecordingTests(unittest.TestCase):
    def test_exclusive_bench_capture_and_hash(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            path=root/"BENCH_PG01_A.jsonl"
            capture=BenchRecorder(path).open()
            ev=AcquisitionEvent("sample","A","COM42",sample=parse_frame(make_frame("A",2,30,200)),
                                host_utc="2026-10-22T12:00:00.000Z",host_monotonic_ns=123456)
            capture.record(ev)
            digest=capture.close()
            self.assertEqual(digest,hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertIn(digest,path.with_suffix(".sha256").read_text())
            data=[json.loads(x) for x in path.read_text().splitlines()]
            self.assertEqual(data[0]["provenance"],"LIVE_USB_RAW_UNCALIBRATED_NOT_AN_APPROVED_EXPERIMENT")
            self.assertEqual(data[1]["sample"]["raw_counts"],200)
            self.assertTrue(data[-1]["kind"]=="footer")
            with self.assertRaises(FileExistsError):
                BenchRecorder(path).open()

    def test_real_experiment_filename_disallowed(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                BenchRecorder(Path(td)/"PG-20261022-001.json").open()


if __name__=="__main__":
    unittest.main()
