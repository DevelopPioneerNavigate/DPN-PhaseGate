"""PG-01 native USB Hardware Lab.

This page is the ONLY v0.7 native panel that presents live, uncalibrated hardware
readings. Existing animated station graphs remain synthetic demonstrations.
"""
from __future__ import annotations

import queue
import time
from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox,
    QMessageBox, QFileDialog, QPushButton
)

from desktop.widgets import Surface, panel_layout, text_label, C
from desktop.hardware import BenchRecorder, SerialReader, available_ports
from desktop.window_helpers import button


class HardwareLab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.readers: dict[str, SerialReader] = {}
        self.port_assignments: dict[str, str] = {}
        self.events: queue.Queue = queue.Queue(maxsize=4000)
        self.recording: BenchRecorder | None = None
        self.recv = {"A":0, "B":0}
        self.faults = {"A":0, "B":0}
        self.last_message = {"A":"DISCONNECTED", "B":"DISCONNECTED"}
        self.port_select = {}
        self.status_labels = {}
        self.count_labels = {}
        self.details = {}
        self._build()
        self.refresh_ports()
        self.timer=QTimer(self)
        self.timer.setInterval(160)
        self.timer.timeout.connect(self.poll)
        self.timer.start()

    def _build(self):
        col=QVBoxLayout(self)
        col.setContentsMargins(35,31,35,35)
        col.setSpacing(17)
        col.addWidget(text_label("PG-01  /  REAL USB ACQUISITION  /  BENCH ONLY",11,"cyan",True))
        col.addWidget(text_label("HARDWARE LAB",31,"text",True))
        col.addWidget(text_label("Connect approved, independently inspected Pico 2 sensor endpoints."
                                 " Raw counts are uncalibrated measurements, NOT grams or transport events.",12))
        warn=Surface("hardwareWarning")
        v=panel_layout(warn,16,7)
        v.addWidget(text_label("LIVE USB DATA ≠ VERIFIED EXPERIMENT",14,"amber",True))
        v.addWidget(text_label("Firmware must be flashed and wired to actual inspected low-voltage hardware. "
                               "The program never transmits serial commands or operates a portal. "
                               "Digital frames and port names do not authenticate physical identity.",12))
        col.addWidget(warn)
        top=QHBoxLayout()
        top.addWidget(text_label("USB COM PORTS // MANUAL ASSIGNMENT",12,"violet",True))
        top.addStretch()
        refresh=button("↻  REFRESH PORTS",secondary=True)
        refresh.clicked.connect(self.refresh_ports)
        top.addWidget(refresh)
        col.addLayout(top)

        pair=QHBoxLayout()
        for station in ("A","B"):
            card=Surface("hardwareStation"+station)
            box=panel_layout(card,19,12)
            hd=QHBoxLayout()
            hd.addWidget(text_label("STATION "+station,18,"cyan" if station=="A" else "violet",True))
            hd.addStretch()
            status=text_label("OFFLINE",12,"amber",True)
            hd.addWidget(status)
            self.status_labels[station]=status
            box.addLayout(hd)
            box.addWidget(text_label("Choose a dedicated, physically inspected USB sensor port.",11))
            select=QComboBox()
            select.setMinimumHeight(37)
            self.port_select[station]=select
            box.addWidget(select)
            controls=QHBoxLayout()
            connect=button("CONNECT "+station,False)
            connect.clicked.connect(lambda checked=False,s=station:self.connect_station(s))
            disconnect=button("DISCONNECT",True)
            disconnect.clicked.connect(lambda checked=False,s=station:self.disconnect_station(s))
            controls.addWidget(connect)
            controls.addWidget(disconnect)
            box.addLayout(controls)
            box.addWidget(text_label("LATEST ADC OUTPUT // SIGNED 24-BIT",11,"muted",True))
            count=text_label("NO VALID SAMPLE",25,"cyan" if station=="A" else "violet",True)
            box.addWidget(count)
            self.count_labels[station]=count
            d=text_label("No board connected. No calibration. No claim of transfer.",11)
            box.addWidget(d)
            self.details[station]=d
            pair.addWidget(card,1)
        col.addLayout(pair)
        info=Surface("hardwareInfo")
        box=panel_layout(info,18,10)
        box.addWidget(text_label("RELIABILITY & FRAME INTEGRITY",13,"cyan",True))
        self.overview=text_label("A: offline  |  B: offline  |  Queue: idle",12)
        box.addWidget(self.overview)
        box.addWidget(text_label("Stale after 2.5 seconds without valid frames. "
                                "XOR detects some accidental corruption, not tampering. "
                                "Clocks are NOT synchronized between stations.",11))
        col.addWidget(info)
        record_panel=Surface("benchRecord")
        rc=panel_layout(record_panel,18,11)
        rc.addWidget(text_label("RAW BENCH CAPTURE // VOLUNTARY / UNVERIFIED",13,"violet",True))
        rc.addWidget(text_label("Separate evidence-class BENCH JSONL + SHA-256, never an approved PhaseGate experiment. "
                                "A hash does not prove who created a sample or establish a physics discovery.",11))
        actions=QHBoxLayout()
        self.capture_start=button("●  START BENCH RECORDING")
        self.capture_start.clicked.connect(self.start_recording)
        self.capture_stop=button("■  STOP & HASH RECORDING",True)
        self.capture_stop.clicked.connect(self.stop_recording)
        self.capture_stop.setEnabled(False)
        actions.addWidget(self.capture_start)
        actions.addWidget(self.capture_stop)
        actions.addStretch()
        rc.addLayout(actions)
        self.record_label=text_label("CAPTURE INACTIVE",12,"amber",True)
        rc.addWidget(self.record_label)
        col.addWidget(record_panel)
        col.addStretch()

    def refresh_ports(self):
        try:
            ports=available_ports()
        except Exception as exc:
            ports=[]
            self.last_message["A"]=f"Port discovery failed: {type(exc).__name__}"
        for name,combo in self.port_select.items():
            current=combo.currentData()
            combo.clear()
            combo.addItem("SELECT COM PORT — NO AUTO-CONNECT",None)
            for device, description in ports:
                combo.addItem(f"{device} — {description[:55]}",device)
            if current:
                index=combo.findData(current)
                if index>=0:
                    combo.setCurrentIndex(index)

    def connect_station(self,station):
        port=self.port_select[station].currentData()
        if not port:
            QMessageBox.warning(self,"Station not selected",
                "Choose the actual inspected COM port first. No ports are auto-opened.")
            return
        if station in self.readers and self.readers[station].is_alive():
            QMessageBox.information(self,"Station running",
                                    "Disconnect the existing station before changing ports.")
            return
        if port in [p for s,p in self.port_assignments.items() if s != station]:
            QMessageBox.warning(self,"Port already assigned","Each station needs a separate physical COM port.")
            return
        self.disconnect_station(station,quiet=True)
        reader=SerialReader(station,port,self.events)
        self.readers[station]=reader
        self.port_assignments[station]=port
        self.status_labels[station].setText("CONNECTING")
        self.count_labels[station].setText("WAITING")
        self.last_message[station]="Port opening..."
        reader.start()

    def disconnect_station(self,station,quiet=False):
        reader=self.readers.pop(station,None)
        self.port_assignments.pop(station,None)
        if reader is not None:
            reader.stop()
        self.status_labels[station].setText("OFFLINE")
        self.count_labels[station].setText("NO VALID SAMPLE")
        if not quiet:
            self.last_message[station]="Station disconnected by operator"

    def poll(self):
        for _ in range(150):
            try:
                event=self.events.get_nowait()
            except queue.Empty:
                break
            station=event.station
            reader=self.readers.get(station)
            # Ignore queued old-port messages after operator explicitly reconnects a station.
            if reader is None or reader.port!=event.port:
                continue
            if self.recording:
                try:
                    self.recording.record(event)
                except OSError as exc:
                    self.last_message[station]="CAPTURE WRITE FAILED: "+str(exc)[:75]
                    self.stop_recording()
            if event.kind=="sample":
                self.recv[station]+=1
                self.count_labels[station].setText(f"{event.sample.raw_counts:+d} counts")
                self.status_labels[station].setText("LIVE USB / RAW")
                self.last_message[station]=f"Sequence {event.sample.sequence}, Pico uptime {event.sample.device_uptime_ms} ms"
            elif event.kind=="connection":
                self.status_labels[station].setText("PORT OPEN / WAITING")
                self.last_message[station]=event.detail
            elif event.kind=="error":
                self.faults[station]+=1
                self.status_labels[station].setText("FAULT / CHECK DATA")
                self.last_message[station]=event.detail
            elif event.kind=="ended":
                self.status_labels[station].setText("PORT CLOSED")
                self.last_message[station]=event.detail
        for station in ("A","B"):
            reader=self.readers.get(station)
            if reader is not None and reader.is_alive() and reader.is_stale():
                self.status_labels[station].setText("STALE / NOT VERIFIED")
            self.details[station].setText(self.last_message[station][:190])
        a=self.readers.get("A")
        b=self.readers.get("B")
        line="   |   ".join(
            f"{station}: {self.recv[station]} samples, {self.faults[station]} faults, "
            f"{self.readers[station].gaps if station in self.readers else 0} missing"
            for station in ("A","B"))
        self.overview.setText(line+f"   |   pending UI frames: {self.events.qsize()}")

    def start_recording(self):
        if self.recording is not None:
            return
        if not any(x.is_alive() and x.last_frame is not None
                   and not x.is_stale() for x in self.readers.values()):
            QMessageBox.warning(self,"No live sensor",
                                "A valid live USB RAW stream is required to start bench capture.")
            return
        answer=QMessageBox.question(self,"Record unverified bench data",
             "Record REAL USB RAW observations only? This is NOT an approved experiment. "
             "No grams or portal transfer can be inferred. Original files must be safeguarded.")
        if answer!=QMessageBox.StandardButton.Yes:
            return
        name="BENCH_PG01_"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+".jsonl"
        choice,_=QFileDialog.getSaveFileName(self,"New bench recording",str(Path.home()/"Documents"/name),
                                             "PG-01 bench JSONL (*.jsonl)")
        if not choice:
            return
        path=Path(choice)
        if path.suffix.lower()!=".jsonl":
            path=path.with_suffix(".jsonl")
        if not path.name.startswith("BENCH_"):
            path=path.with_name("BENCH_"+path.name)
        try:
            self.recording=BenchRecorder(path).open()
        except (OSError,ValueError) as exc:
            QMessageBox.warning(self,"Cannot start bench recording",str(exc))
            return
        self.capture_start.setEnabled(False)
        self.capture_stop.setEnabled(True)
        self.record_label.setText("● CAPTURING RAW BENCH DATA → "+str(path))
        
    def stop_recording(self):
        rec=self.recording
        if rec is None:
            return
        self.recording=None
        self.capture_start.setEnabled(True)
        self.capture_stop.setEnabled(False)
        try:
            digest=rec.close()
            self.record_label.setText(
                f"CAPTURE CLOSED: {rec.samples} samples. SHA-256 {digest[:16]}... "
                "NOT AN EXPERIMENT.")
        except OSError as exc:
            self.record_label.setText("CAPTURE ERROR / CHECK FILE + HASH: "+str(exc)[:100])

    def shutdown(self):
        self.timer.stop()
        self.stop_recording()
        for station in ("A","B"):
            self.disconnect_station(station,quiet=True)
