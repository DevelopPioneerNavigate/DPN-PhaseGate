"""PG-01 Optical Evidence Lab — native, consent-gated dual USB-camera workstation.

Frames can only arrive after an explicit operator click. Captures are user-
initiated and never added to the scientific run manifest. No remote connection.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox,
    QMessageBox, QFileDialog
)

from desktop.widgets import Surface, panel_layout, text_label
from desktop.window_helpers import button
from desktop.aurora import LabBanner
from desktop.optical import TimebaseHealth, compare_receive_cadence, verify_optical_bench, OpticalError
from desktop.camera_worker import CameraWorker


class OpticalLab(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.workers={}
        self.cameras={}
        self.device_select={}
        self.preview_labels={}
        self.state_labels={}
        self.record_labels={}
        self.record_start={}
        self.record_stop={}
        self.clock={"A":TimebaseHealth(8),"B":TimebaseHealth(8)}
        self._build()
        self.timer=QTimer(self)
        self.timer.setInterval(900)
        self.timer.timeout.connect(self.update_health)
        self.timer.start()

    def _build(self):
        col=QVBoxLayout(self)
        col.setContentsMargins(30,23,30,30)
        col.setSpacing(14)
        col.addWidget(text_label("PG-01  /  INDEPENDENT OPTICAL BENCH  /  CONSENT REQUIRED",
                                 10,"cyan",True))
        col.addWidget(text_label("OPTICAL EVIDENCE LAB",28,"text",True))
        col.addWidget(LabBanner(
            "DUAL CAMERA MONITORING // v1.0",
            "Two independently chosen local cameras. No automatic access, cloud upload, audio or physical transfer claims.",
            "#76E1F3"))
        warn=Surface("opticalWarning")
        box=panel_layout(warn,14,6)
        box.addWidget(text_label("PRIVATE LOCAL CAPTURE  •  UNVERIFIED BENCH EVIDENCE",13,"amber",True))
        box.addWidget(text_label(
            "Camera access requires your direct approval. Recording is a second, separate action. "
            "Camera frames have host POST-READ receipt timestamps only; physical exposure times and "
            "inter-station synchronization are UNKNOWN. Keep faces and private surroundings out of view.",11))
        col.addWidget(warn)
        pair=QHBoxLayout()
        pair.setSpacing(13)
        for station in ("A","B"):
            card=Surface("cameraStation"+station)
            c=panel_layout(card,15,9)
            top=QHBoxLayout()
            top.addWidget(text_label("OPTICAL STATION "+station,16,
                                     "cyan" if station=="A" else "violet",True))
            top.addStretch()
            status=text_label("●  OFFLINE",10,"amber",True)
            self.state_labels[station]=status
            top.addWidget(status)
            c.addLayout(top)
            choices=QComboBox()
            choices.setMinimumHeight(36)
            for idx in range(8):
                choices.addItem(f"Local camera index {idx} • manually verify identity",idx)
            if station=="B":choices.setCurrentIndex(1)
            self.device_select[station]=choices
            c.addWidget(choices)
            screen=QLabel("NO CAMERA ACCESS\n\nCHOOSE CAMERA → OPEN PREVIEW")
            screen.setAlignment(Qt.AlignmentFlag.AlignCenter)
            screen.setWordWrap(True)
            screen.setMinimumHeight(165)
            screen.setObjectName("cameraPreview")
            screen.setStyleSheet(
                "background:#0C1528;border:1px solid #4C6089;border-radius:12px;"
                "font-size:12px;font-weight:700;color:#8199B9")
            self.preview_labels[station]=screen
            c.addWidget(screen,1)
            row=QHBoxLayout()
            open_cam=button("▶  OPEN PREVIEW",False)
            open_cam.clicked.connect(lambda checked=False,s=station:self.open_camera(s))
            close_cam=button("■  CLOSE",True)
            close_cam.clicked.connect(lambda checked=False,s=station:self.close_camera(s))
            row.addWidget(open_cam)
            row.addWidget(close_cam)
            c.addLayout(row)
            record_row=QHBoxLayout()
            start=button("●  RECORD STILLS",False)
            start.setEnabled(False)
            start.clicked.connect(lambda checked=False,s=station:self.start_record(s))
            stop=button("■  STOP / HASH",True)
            stop.setEnabled(False)
            stop.clicked.connect(lambda checked=False,s=station:self.stop_record(s))
            self.record_start[station]=start
            self.record_stop[station]=stop
            record_row.addWidget(start)
            record_row.addWidget(stop)
            c.addLayout(record_row)
            detail=text_label("CAPTURE INACTIVE • STILL JPEG ONLY • NO AUDIO",10,"muted")
            detail.setWordWrap(True)
            c.addWidget(detail)
            self.record_labels[station]=detail
            pair.addWidget(card,1)
        col.addLayout(pair)
        health=Surface("opticalTiming")
        hb=panel_layout(health,15,9)
        heading=QHBoxLayout()
        heading.addWidget(text_label("HOST TIMEBASE / ARRIVAL-INTERVAL DIAGNOSTICS",13,"cyan",True))
        heading.addStretch()
        heading.addWidget(text_label("NOT SYNCHRONIZED",10,"amber",True))
        hb.addLayout(heading)
        self.quality=text_label("A: no camera frames | B: no camera frames | Camera exposure offset: UNKNOWN",
                                11,"muted")
        hb.addWidget(self.quality)
        hb.addWidget(text_label(
            "Measurements use the host clock AFTER camera.read(); driver buffering and exposure delay are unknown. "
            "Neither equal USB receipt timestamps nor low jitter prove simultaneous capture or object transit.",11))
        controls=QHBoxLayout()
        verify=button("VERIFY EXISTING BENCH FOLDER",True)
        verify.clicked.connect(self.verify_folder)
        controls.addWidget(verify)
        controls.addStretch()
        hb.addLayout(controls)
        col.addWidget(health)
        col.addStretch()

    def open_camera(self,station):
        if station in self.workers and self.workers[station].isRunning():
            QMessageBox.information(self,"Camera already opened","Disconnect it before changing cameras.")
            return
        index=self.device_select[station].currentData()
        for other,assigned in self.cameras.items():
            if other!=station and assigned==index:
                QMessageBox.warning(self,"Camera already assigned",
                                    "Use independent physical USB camera indices for Stations A and B.")
                return
        approval=QMessageBox.question(
            self,"Permit local camera preview?",
            f"Allow PhaseGate to open local camera #{index} for Station {station}?\n\n"
            "The camera will remain local. Previewing does NOT record frames, audio, or upload anything. "
            "Only open a camera you own or have permission to view.",
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
        if approval!=QMessageBox.StandardButton.Yes:
            return
        self.close_camera(station)
        self.clock[station]=TimebaseHealth(8)
        worker=CameraWorker(station,index,"Operator (camera preview)",self)
        worker.preview.connect(self.new_preview)
        worker.state.connect(self.new_state)
        worker.record_state.connect(self.new_record_state)
        worker.finished.connect(lambda s=station,w=worker:self.worker_finished(s,w))
        self.workers[station]=worker
        self.cameras[station]=index
        self.device_select[station].setEnabled(False)
        self.state_labels[station].setText("STARTING / CONSENTED PREVIEW")
        worker.start()

    def new_state(self,station,detail):
        self.state_labels[station].setText(detail[:95])
        active=station in self.workers and self.workers[station].isRunning()
        if detail.startswith("CAMERA OPEN"):
            self.record_start[station].setEnabled(True)
        elif "OFFLINE" in detail or "CLOSED" in detail:
            self.record_start[station].setEnabled(False)

    def new_preview(self,station,data,host_ns):
        self.clock[station].note(host_ns)
        pic=QPixmap()
        if not pic.loadFromData(data,"JPG"):
            self.state_labels[station].setText("FRAME DECODE FAILURE")
            return
        area=self.preview_labels[station]
        area.setPixmap(pic.scaled(area.size(),Qt.AspectRatioMode.KeepAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation))

    def close_camera(self,station):
        worker=self.workers.get(station)
        if worker:
            worker.halt()
            worker.requestInterruption()
            if not worker.wait(2500):
                self.state_labels[station].setText("CAMERA SHUTDOWN PENDING; INSPECT DEVICE")
                return
        self.workers.pop(station,None)
        self.cameras.pop(station,None)
        self.device_select[station].setEnabled(True)
        self.record_start[station].setEnabled(False)
        self.record_stop[station].setEnabled(False)
        self.state_labels[station].setText("●  OFFLINE")
        screen=self.preview_labels[station]
        screen.clear()
        screen.setText("CAMERA CLOSED\nNO BACKGROUND ACCESS")

    def worker_finished(self,station,worker):
        if self.workers.get(station) is worker:
            self.workers.pop(station,None)
            self.cameras.pop(station,None)
            self.device_select[station].setEnabled(True)
            self.record_start[station].setEnabled(False)
            self.record_stop[station].setEnabled(False)

    def start_record(self,station):
        worker=self.workers.get(station)
        if not worker or not worker.isRunning():
            QMessageBox.warning(self,"No camera","Open an authorized local camera preview first.")
            return
        ok=QMessageBox.question(self,"Confirm private local bench capture",
            "Record still JPEG frames for unverified BENCH evidence?\n\n"
            "A new directory will contain saved frames, per-frame hashes, and a local manifest. "
            "No audio, cloud upload, object tracking, or scientific approval is implied. "
            "Confirm all persons/locations may be recorded.",
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
        if ok!=QMessageBox.StandardButton.Yes:return
        folder=QFileDialog.getExistingDirectory(self,"Choose a private local parent folder for BENCH still frames",
                                                str(Path.home()/"Documents"))
        if not folder:return
        dest=Path(folder)/("BENCH_OPTICAL_"+station+"_"+
                           datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
        try:
            worker.request_record(dest)
        except Exception as exc:
            QMessageBox.warning(self,"Cannot request recording",str(exc))
            return
        self.record_start[station].setEnabled(False)
        self.record_labels[station].setText("RECORDING REQUESTED • WAITING FOR CAPTURE WORKER")

    def stop_record(self,station):
        worker=self.workers.get(station)
        if worker and worker.isRunning():
            worker.request_stop_record()
            self.record_stop[station].setEnabled(False)
            self.record_labels[station].setText("FINISHING MANIFEST + FRAME HASHES...")

    def new_record_state(self,station,active,message):
        self.record_labels[station].setText(message[:240])
        self.record_start[station].setEnabled(
            not active and station in self.workers and self.workers[station].isRunning())
        self.record_stop[station].setEnabled(active)

    def verify_folder(self):
        source=QFileDialog.getExistingDirectory(self,"Select existing BENCH_OPTICAL_ directory",
                                                str(Path.home()/"Documents"))
        if not source:return
        try:
            report=verify_optical_bench(source)
        except (OSError,ValueError,OpticalError) as exc:
            QMessageBox.warning(self,"Optical bench integrity failure",str(exc))
            return
        QMessageBox.information(self,"Unverified bench integrity",
            f"Station {report['station']}: {report['frames']} original JPEG files match manifest checksums.\n\n"
            "This does NOT establish sensor exposure timing, scene authenticity, or physical-object transfer.")

    def update_health(self):
        status=compare_receive_cadence(self.clock["A"],self.clock["B"])
        parts=[]
        for station,attr in (("A","station_a"),("B","station_b")):
            h=status[attr]
            if h["host_arrival_jitter_ms"] is None:
                parts.append(station+": INSUFFICIENT CAMERA FRAMES")
            else:
                parts.append(f"{station}: arrival jitter {h['host_arrival_jitter_ms']:.1f} ms "
                             f"/ delayed intervals {h['delayed_intervals']}")
        self.quality.setText("  |  ".join(parts)+"\nEXPOSURE OFFSET UNKNOWN • NO CROSS-CAMERA SYNC VALIDATED")

    def shutdown(self):
        self.timer.stop()
        for station in ("A","B"):
            self.close_camera(station)
