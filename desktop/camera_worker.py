"""Operator-gated local USB camera worker. No camera opened without user action.

Runs OpenCV capture away from the Qt GUI. No internet requests, audio,
face recognition, background webcam access or automatic experimental logging.
"""
from __future__ import annotations

import queue
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from desktop.optical import Arrival, OpticalBenchWriter, OpticalError


class CameraWorker(QThread):
    preview = Signal(str, bytes, int)   # station, compressed JPEG, post-read monotonic ns
    state = Signal(str, str)            # station, explicit state text
    record_state = Signal(str, bool, str) # station, enabled, detail

    def __init__(self, station: str, index: int, operator: str, parent=None):
        super().__init__(parent)
        self.station=station
        self.index=index
        self.operator=operator
        self.commands=queue.Queue(maxsize=10)
        self._running=True

    def request_record(self, directory: Path):
        self.commands.put_nowait(("start",str(directory)))

    def request_stop_record(self):
        self.commands.put_nowait(("stop",""))

    def halt(self):
        self._running=False

    def run(self):
        writer=None
        cap=None
        last_publish=0.0
        try:
            import cv2
            cap=cv2.VideoCapture(
                self.index, cv2.CAP_DSHOW if sys.platform=="win32" else cv2.CAP_ANY
            )
            if not cap.isOpened():
                raise OpticalError("camera could not be opened: check USB index and OS privacy permission")
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
            self.state.emit(self.station,"CAMERA OPEN / PREVIEW ONLY")
            while self._running and not self.isInterruptionRequested():
                # Processing control commands exclusively on capture worker thread
                # avoids races with the last image / manifest close.
                while True:
                    try:
                        verb,directory=self.commands.get_nowait()
                    except queue.Empty:
                        break
                    if verb=="start":
                        if writer is not None:
                            self.record_state.emit(self.station,True,"Already recording")
                            continue
                        try:
                            writer=OpticalBenchWriter(directory,self.station,self.index,self.operator)
                            self.record_state.emit(self.station,True,
                                "BENCH STILL-FRAME CAPTURE • NO AUDIO • NOT AN EXPERIMENT")
                        except (OSError,ValueError,OpticalError) as exc:
                            self.record_state.emit(self.station,False,"Could not start recording: "+str(exc)[:130])
                    if verb=="stop" and writer is not None:
                        try:
                            report=writer.close()
                            self.record_state.emit(self.station,False,
                                f"BENCH CAPTURE CLOSED: {report['frame_count']} frames. "
                                f"Manifest SHA-256 {report['manifest_sha256'][:16]}...")
                        except (OSError,OpticalError) as exc:
                            self.record_state.emit(self.station,False,"CAPTURE FINALIZE ERROR: "+str(exc)[:130])
                        writer=None
                ok,frame=cap.read()
                observed_ns=time.monotonic_ns()  # AFTER read; not sensor exposure time
                observed_utc=datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00","Z")
                if not ok or frame is None:
                    self.state.emit(self.station,"CAMERA FRAME LOST / RECHECK USB")
                    time.sleep(.25)
                    continue
                valid,jpeg=cv2.imencode(".jpg",frame,[int(cv2.IMWRITE_JPEG_QUALITY),77])
                if not valid:
                    self.state.emit(self.station,"JPEG ENCODER FAILURE")
                    continue
                data=jpeg.tobytes()
                if writer is not None:
                    try:
                        stored=writer.append(data,Arrival(self.station,self.index,observed_utc,observed_ns))
                        if len(writer.frames)>=1200:
                            report=writer.close("MAX_FRAME_COUNT")
                            writer=None
                            self.record_state.emit(self.station,False,
                              "MAX BENCH FRAMES REACHED • HASHED MANIFEST")
                    except (OSError,ValueError,OpticalError) as exc:
                        try:
                            writer.close("ERROR_CAPTURE_STOP")
                        except Exception:
                            pass
                        writer=None
                        self.record_state.emit(self.station,False,
                            "CAPTURE ERROR — INSPECT PARTIAL RECORDING: "+str(exc)[:120])
                if time.monotonic()-last_publish>=.105:
                    self.preview.emit(self.station,data,observed_ns)
                    last_publish=time.monotonic()
                time.sleep(.03)
        except Exception as exc:
            self.state.emit(self.station,"OPTICAL OFFLINE: "+type(exc).__name__+": "+str(exc)[:130])
        finally:
            if writer is not None:
                try:
                    report=writer.close("DEVICE_DISCONNECTED")
                    self.record_state.emit(self.station,False,
                        "CAPTURE CLOSED BY CAMERA SHUTDOWN; CHECK FRAME COMPLETENESS")
                except (OSError,OpticalError) as exc:
                    self.record_state.emit(self.station,False,
                        "INCOMPLETE EVIDENCE • CHECK MANIFEST: "+str(exc)[:90])
            if cap is not None:
                try:cap.release()
                except Exception:pass
            self.state.emit(self.station,"CAMERA CLOSED — NO BACKGROUND ACCESS")
