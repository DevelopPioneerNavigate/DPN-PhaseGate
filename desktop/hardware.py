"""PG-01 USB bench acquisition: read-only uncalibrated observations.

No serial writes, instrument actuation, experiment automation or portal claims.
The station/port pairing is manually selected by the operator.
"""
from __future__ import annotations

import hashlib
import json
import queue
import re
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

PREFIX = "PG1"
MAX_FRAME_BYTES = 160
RAW_MIN, RAW_MAX = -(1 << 23), (1 << 23) - 1
DEVICE_ID = re.compile(r"^[AB]$")
NUMBER = re.compile(r"^(0|[1-9][0-9]{0,9})$")
RAW = re.compile(r"^-?(0|[1-9][0-9]{0,7})$")
STATUS = "RAW"
BAUDRATE = 115200
STALE_AFTER_SEC = 2.5


class FrameError(ValueError):
    """Reject invalid and accidentally corrupted input before display."""


def xor_checksum(data: str) -> int:
    """Basic corruption check, NOT authentication or tamper-proof evidence."""
    result = 0
    for byte in data.encode("ascii"):
        result ^= byte
    return result


@dataclass(frozen=True)
class Frame:
    station: str
    sequence: int
    device_uptime_ms: int
    raw_counts: int

    def __post_init__(self):
        if self.station not in ("A", "B"):
            raise ValueError("invalid station")
        if self.sequence < 0 or self.device_uptime_ms < 0:
            raise ValueError("negative sequence or uptime")
        if not RAW_MIN <= self.raw_counts <= RAW_MAX:
            raise ValueError("raw counts outside signed 24-bit range")


def make_frame(station: str, sequence: int, uptime_ms: int, raw_counts: int) -> bytes:
    frame = Frame(station, sequence, uptime_ms, raw_counts)
    body = f"{PREFIX}|{frame.station}|{frame.sequence}|{frame.device_uptime_ms}|{frame.raw_counts}|{STATUS}"
    return (f"{body}|{xor_checksum(body):02X}\n").encode("ascii")


def parse_frame(line: bytes, expected_station: str | None = None) -> Frame:
    if not isinstance(line, bytes) or not 1 <= len(line) <= MAX_FRAME_BYTES:
        raise FrameError("invalid frame size")
    if not line.endswith(b"\n"):
        raise FrameError("incomplete frame")
    try:
        s = line.rstrip(b"\r\n").decode("ascii")
    except UnicodeDecodeError as exc:
        raise FrameError("non-ASCII payload") from exc
    parts = s.split("|")
    if len(parts) != 7 or parts[0] != PREFIX or parts[5] != STATUS:
        raise FrameError("invalid protocol or status")
    if not DEVICE_ID.fullmatch(parts[1]):
        raise FrameError("invalid station identifier")
    if expected_station is not None and parts[1] != expected_station:
        raise FrameError("station mismatch: inspect USB-to-station assignment")
    if not NUMBER.fullmatch(parts[2]) or not NUMBER.fullmatch(parts[3]):
        raise FrameError("invalid sequence or device timestamp")
    if not RAW.fullmatch(parts[4]):
        raise FrameError("invalid signed sensor value")
    if not re.fullmatch(r"[0-9A-F]{2}", parts[6]):
        raise FrameError("invalid checksum representation")
    body = "|".join(parts[:6])
    if xor_checksum(body) != int(parts[6], 16):
        raise FrameError("corrupt checksum (XOR is not security)")
    sequence, uptime, raw = int(parts[2]), int(parts[3]), int(parts[4])
    if sequence > 2_147_483_647 or uptime > 2_147_483_647:
        raise FrameError("out-of-range sequence or timestamp")
    try:
        return Frame(parts[1], sequence, uptime, raw)
    except ValueError as exc:
        raise FrameError(str(exc)) from exc


@dataclass(frozen=True)
class AcquisitionEvent:
    kind: str                 # sample / connection / error / ended
    station: str
    port: str
    detail: str = ""
    sample: Frame | None = None
    host_utc: str = ""
    host_monotonic_ns: int = 0


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class SerialReader:
    """One worker per selected port. No write command is ever sent to hardware."""

    def __init__(self, station: str, port: str, events: queue.Queue,
                 serial_factory=None, monotonic=time.monotonic):
        if station not in ("A", "B"):
            raise ValueError("station must be A or B")
        if not isinstance(port, str) or not 1 <= len(port) <= 160 or any(x in port for x in ("\r", "\n", "\0")):
            raise ValueError("invalid device port")
        self.station, self.port, self.events = station, port, events
        self.serial_factory = serial_factory
        self.monotonic = monotonic
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.last_frame: Frame | None = None
        self.last_received: float | None = None
        self.invalid_count = 0
        self.gaps = 0

    def _publish(self, kind, detail="", frame=None):
        ev = AcquisitionEvent(kind=kind, station=self.station, port=self.port,
                              detail=detail, sample=frame, host_utc=utc_now(),
                              host_monotonic_ns=time.monotonic_ns())
        try:
            self.events.put_nowait(ev)
        except queue.Full:
            # Dropped data means completeness cannot be established.
            self.invalid_count += 1

    def start(self):
        if self._thread is not None:
            raise RuntimeError("serial reader already started")
        self._thread = threading.Thread(target=self.run, name=f"PhaseGate-USB-{self.station}", daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=1.2)

    def run(self):
        serial_port = None
        try:
            factory = self.serial_factory
            if factory is None:
                from serial import Serial
                factory = Serial
            # Opening a USB serial port can reset a microcontroller. This is noted in user docs.
            serial_port = factory(self.port, baudrate=BAUDRATE, timeout=0.25)
            self._publish("connection", "PORT OPEN / WAITING FOR RAW FRAMES")
            pending = bytearray()
            while not self._stop.is_set():
                piece = serial_port.read(80)
                if not piece:
                    continue
                if not isinstance(piece, bytes):
                    self._publish("error", "SERIAL BACKEND RETURNED NON-BYTES")
                    break
                for byte in piece:
                    if byte == 10:  # newline: frame boundary
                        if not pending:
                            continue
                        frame_bytes = bytes(pending) + b"\n"
                        pending.clear()
                        try:
                            frame = parse_frame(frame_bytes, self.station)
                            last = self.last_frame
                            if last is not None:
                                # Pico reset causes sequence / uptime rollback: reject and require reconnect.
                                if frame.sequence <= last.sequence or frame.device_uptime_ms < last.device_uptime_ms:
                                    raise FrameError("sequence/clock rolled backward: reattach sensor after reset")
                                if frame.sequence > last.sequence + 1:
                                    self.gaps += frame.sequence-last.sequence-1
                                    self._publish("error", "GAP IN SERIAL SAMPLE SEQUENCE")
                            self.last_frame = frame
                            self.last_received = self.monotonic()
                            self._publish("sample", frame=frame)
                        except FrameError as exc:
                            self.invalid_count += 1
                            self._publish("error", str(exc)[:180])
                        continue
                    if byte not in (13,) and (byte < 32 or byte > 126):
                        pending.clear()
                        self.invalid_count += 1
                        self._publish("error", "invalid serial control character")
                        continue
                    if byte != 13:
                        pending.append(byte)
                    if len(pending) > MAX_FRAME_BYTES:
                        pending.clear()
                        self.invalid_count += 1
                        self._publish("error", "oversized serial frame discarded")
        except Exception as exc:
            self._publish("error", f"SERIAL LINK FAILED: {type(exc).__name__}: {str(exc)[:110]}")
        finally:
            if serial_port is not None:
                try:
                    serial_port.close()
                except Exception:
                    pass
            self._publish("ended", "PORT CLOSED / NO VALID MEASUREMENT STREAM")

    def is_alive(self) -> bool:
        return bool(self._thread is not None and self._thread.is_alive())

    def is_stale(self) -> bool:
        return self.last_received is None or self.monotonic() - self.last_received > STALE_AFTER_SEC


def available_ports():
    """Enumeration only; do not open or transmit until operator clicks connect."""
    from serial.tools import list_ports
    return [(x.device, x.description or "Unknown serial device") for x in list_ports.comports()]


class BenchRecorder:
    """User initiated raw evidence, separate from approved experiment records.

    Logs host-received uncalibrated samples and status/errors; hashes raw file on close.
    A digest detects later bytes changes but is not source authentication.
    """
    def __init__(self, path: Path):
        self.path = Path(path)
        if not self.path.name.startswith("BENCH_") or self.path.suffix.lower() != ".jsonl":
            raise ValueError("bench capture filename must start BENCH_ and end .jsonl")
        self._file = None
        self.samples = 0
        self.started_utc = utc_now()

    def open(self):
        # Exclusive create: never silently overwrite an earlier physical sensor log.
        self._file = self.path.open("x", encoding="utf-8", newline="\n")
        self.append({"kind":"header","schema":"PG-BENCH-1",
                     "provenance":"LIVE_USB_RAW_UNCALIBRATED_NOT_AN_APPROVED_EXPERIMENT",
                     "started_utc":self.started_utc,
                     "warning":"Host times are not calibrated cross-device synchronization."})
        return self

    def append(self, record):
        if self._file is None:
            raise RuntimeError("capture is not open")
        self._file.write(json.dumps(record, separators=(",", ":"), allow_nan=False)+"\n")
        self._file.flush()

    def record(self, event: AcquisitionEvent):
        if event.kind not in ("sample", "error", "connection", "ended"):
            return
        self.append({"kind":event.kind,"station":event.station,"port":event.port,
                     "host_utc":event.host_utc,"host_monotonic_ns":event.host_monotonic_ns,
                     "detail":event.detail,
                     "sample":asdict(event.sample) if event.sample else None})
        if event.kind == "sample":
            self.samples += 1

    def close(self):
        if self._file is None:
            return None
        self.append({"kind":"footer","ended_utc":utc_now(),"sample_count":self.samples,
                     "warning":"Unverified bench recording: not a teleportation finding."})
        self._file.close()
        self._file = None
        digest = hashlib.sha256(self.path.read_bytes()).hexdigest()
        sidecar = self.path.with_suffix(".sha256")
        # Exclusive: don't rewrite an existing digest.
        with sidecar.open("x", encoding="ascii") as f:
            f.write(f"{digest}  {self.path.name}\n")
        return digest
