"""Native Calibration & Witness workstation (v0.8).

Explicit operator inputs only. No video capture, sensor actuation or automated
research promotion. Calibration fits are unreviewed bench estimates.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QDoubleSpinBox, QSpinBox, QPushButton,
    QFileDialog, QMessageBox, QTextEdit
)

from desktop.widgets import Surface, panel_layout, text_label
from desktop.window_helpers import button
from desktop.calibration import CalibrationError, fit, parse_worksheet, save_profile
from desktop.witness import WitnessError, inventory_source, save_inventory


class WitnessWorker(QThread):
    done = Signal(bool, str)

    def __init__(self, source: Path, destination: Path, station: str,
                 operator: str, note: str):
        super().__init__()
        self.source, self.destination = source, destination
        self.station, self.operator, self.note = station, operator, note

    def run(self):
        try:
            record=inventory_source(self.source,self.station,self.operator,
                                    self.note,consent_confirmed=True)
            digest=save_inventory(record,self.destination)
            self.done.emit(True,"Metadata+SHA-256 inventory saved: "
                           +str(self.destination)+"\nSHA-256 "+digest
                           +"\nRecording content was NOT copied or uploaded.")
        except (WitnessError, OSError, ValueError) as exc:
            self.done.emit(False,str(exc))


class EvidenceLab(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.csv_file: Path | None=None
        self.witness_file: Path | None=None
        self.workers=[]
        self._build()

    def _build(self):
        col=QVBoxLayout(self)
        col.setContentsMargins(35,31,35,35)
        col.setSpacing(18)
        col.addWidget(text_label("PG-01 / MEASUREMENT ASSURANCE / STATION EVIDENCE",11,"cyan",True))
        col.addWidget(text_label("CALIBRATION & WITNESS LAB",30,"text",True))
        col.addWidget(text_label(
            "Prepare station-specific scale regression files and hash independent camera recordings. "
            "Calibration is not certified and video is not a verified physics event.",12))
        w=Surface("evidenceWarning")
        v=panel_layout(w,15,9)
        v.addWidget(text_label("OPERATOR-MANAGED / BENCH ONLY / NOT APPROVED EXPERIMENTS",13,"amber",True))
        v.addWidget(text_label("No camera or USB sensor is activated from this page. "
            "The station diagrams elsewhere remain simulated. Source reference masses, timestamps "
            "and recording authenticity cannot be verified by software alone.",11))
        col.addWidget(w)

        config=Surface("evidenceConfig")
        cv=panel_layout(config,19,13)
        cv.addWidget(text_label("01 / WHO IS RESPONSIBLE?",13,"cyan",True))
        row=QHBoxLayout()
        left=QVBoxLayout()
        left.addWidget(text_label("Operator identifier",11,"muted"))
        self.operator=QLineEdit()
        self.operator.setPlaceholderText("Research operator / initials; don't include secrets")
        self.operator.setMaxLength(120)
        left.addWidget(self.operator)
        row.addLayout(left,3)
        station_col=QVBoxLayout()
        station_col.addWidget(text_label("Station",11,"muted"))
        self.station=QComboBox()
        self.station.addItems(["A","B"])
        station_col.addWidget(self.station)
        row.addLayout(station_col,1)
        cv.addLayout(row)
        col.addWidget(config)

        cal=Surface("calWork")
        form=panel_layout(cal,19,12)
        form.addWidget(text_label("02 / REFERENCE-MASS CALIBRATION WORKSHEET",13,"violet",True))
        form.addWidget(text_label(
            "CSV format: reference_g,raw_counts. Include at least 3 distinct masses "
            "and 2 actual readings at each mass. The program fits a linear model but "
            "does not certify uncertainties, hysteresis or electrical safety.",11))
        self.csv_status=text_label("NO CSV LOADED",11,"muted")
        form.addWidget(self.csv_status)
        choose=button("CHOOSE REFERENCE-MASS CSV",True)
        choose.clicked.connect(self.choose_csv)
        form.addWidget(choose)
        attrs=QHBoxLayout()
        ref_col=QVBoxLayout()
        ref_col.addWidget(text_label("Reference set / certificate identifier",11,"muted"))
        self.reference=QLineEdit()
        self.reference.setPlaceholderText("Record actual reference set; synthetic if testing")
        self.reference.setMaxLength(120)
        ref_col.addWidget(self.reference)
        attrs.addLayout(ref_col,3)
        unc_col=QVBoxLayout()
        unc_col.addWidget(text_label("DECLARED reference uncertainty (g)",11,"muted"))
        self.uncertainty=QDoubleSpinBox()
        self.uncertainty.setRange(0.000001,100.0)
        self.uncertainty.setDecimals(6)
        self.uncertainty.setValue(0.01)
        self.uncertainty.setSingleStep(.001)
        unc_col.addWidget(self.uncertainty)
        attrs.addLayout(unc_col,2)
        expire_col=QVBoxLayout()
        expire_col.addWidget(text_label("Re-check interval (days)",11,"muted"))
        self.expiration=QSpinBox()
        self.expiration.setRange(1,365)
        self.expiration.setValue(30)
        expire_col.addWidget(self.expiration)
        attrs.addLayout(expire_col,1)
        form.addLayout(attrs)
        save=button("FIT + SAVE BENCH CALIBRATION")
        save.clicked.connect(self.create_calibration)
        form.addWidget(save)
        self.cal_status=text_label("No profile created; no instrument has been verified.",11,"amber")
        form.addWidget(self.cal_status)
        col.addWidget(cal)

        witness=Surface("witnessWork")
        wv=panel_layout(witness,19,11)
        wv.addWidget(text_label("03 / WITNESS MEDIA INVENTORY",13,"violet",True))
        wv.addWidget(text_label(
            "Choose a pre-recorded local video, photo or audio file. Record its operator "
            "and acquisition notes; calculate SHA-256 and store a separate BENCH_WITNESS JSON. "
            "We do NOT record cameras, copy media, or upload private videos.",11))
        src=button("CHOOSE EXISTING WITNESS MEDIA",True)
        src.clicked.connect(self.choose_witness)
        wv.addWidget(src)
        self.media_status=text_label("NO WITNESS MEDIA SELECTED",11,"muted")
        wv.addWidget(self.media_status)
        wv.addWidget(text_label("Camera origin, witness angle and timestamp limitations",11,"muted"))
        self.media_note=QTextEdit()
        self.media_note.setMinimumHeight(82)
        self.media_note.setMaximumHeight(110)
        self.media_note.setPlaceholderText(
            "Explain who recorded it, the vantage point, and whether clocks are unsynchronized.")
        wv.addWidget(self.media_note)
        self.add_media=button("INVENTORY MEDIA + SHA-256")
        self.add_media.clicked.connect(self.inventory_media)
        wv.addWidget(self.add_media)
        self.witness_status=text_label("Witness inventory inactive",11,"amber")
        wv.addWidget(self.witness_status)
        col.addWidget(witness)
        col.addStretch()

    def choose_csv(self):
        filename,_=QFileDialog.getOpenFileName(self,"Select station mass worksheet","","CSV (*.csv)")
        if not filename:
            return
        self.csv_file=Path(filename)
        self.csv_status.setText(f"CSV SELECTED: {self.csv_file.name} — not yet validated")

    def create_calibration(self):
        if self.csv_file is None:
            QMessageBox.warning(self,"CSV required","Select an actual calibration worksheet first.")
            return
        try:
            rows,source_sha=parse_worksheet(self.csv_file)
            profile=fit(rows,self.station.currentText(),self.uncertainty.value(),
                        self.reference.text(),self.operator.text(),
                        self.expiration.value(),source_sha256=source_sha)
        except (CalibrationError,OSError,ValueError) as exc:
            QMessageBox.warning(self,"Calibration input failed",str(exc))
            return
        QMessageBox.information(self,"Important limits",
            "This produces an UNREVIEWED BENCH ESTIMATE. The declared reference uncertainty "
            "is not a certified full uncertainty budget. Regression quality does not validate "
            "physical sensors or imply material transportation.")
        default=f"BENCH_CAL_{self.station.currentText()}_"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+".json"
        target,_=QFileDialog.getSaveFileName(self,"Save BENCH calibration profile",
                     str(Path.home()/"Documents"/default),"Calibration JSON (*.json)")
        if not target:
            return
        path=Path(target)
        if not path.name.startswith("BENCH_CAL_"):
            path=path.with_name("BENCH_CAL_"+path.name)
        if path.suffix.lower()!=".json":
            path=path.with_suffix(".json")
        try:
            save_profile(profile,path)
        except (CalibrationError,OSError,ValueError) as exc:
            QMessageBox.warning(self,"Calibration save failed",str(exc))
            return
        self.cal_status.setText("SAVED UNREVIEWED PROFILE: "
            +path.name+"  |  R²="+f"{profile['fit_r_squared']:.5f}"
            +"  |  RMSE="+f"{profile['fit_residual_rmse_g']:.5g} g")
        QMessageBox.information(self,"Profile saved",
            "Bench profile saved separately from real experiments.\n"
            "Open Hardware Lab → Load Profile for the correct station to show labelled estimates.")

    def choose_witness(self):
        file,_=QFileDialog.getOpenFileName(self,"Choose pre-recorded witness media","",
                    "Video/Photo/Audio (*.mp4 *.mov *.avi *.mkv *.jpg *.jpeg *.png *.wav)")
        if not file:
            return
        self.witness_file=Path(file)
        self.media_status.setText("SOURCE SELECTED: "+self.witness_file.name)

    def inventory_media(self):
        if self.witness_file is None:
            QMessageBox.warning(self,"Source missing","Choose a pre-recorded media file first.")
            return
        note=self.media_note.toPlainText().strip()
        operator=self.operator.text().strip()
        if len(operator)<2 or len(note)<12:
            QMessageBox.warning(self,"Witness metadata needed",
                                "Enter your operator identifier and explain capture origin/time limitations.")
            return
        response=QMessageBox.question(self,"Permission and provenance",
                "Confirm you are authorized to handle this video/photo/audio. "
                "Only a hash and metadata will be stored, not the recording itself. "
                "A hash cannot authenticate the original footage.",
                QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
        if response!=QMessageBox.StandardButton.Yes:
            return
        station=self.station.currentText()
        default="BENCH_WITNESS_"+station+"_"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+".json"
        output,_=QFileDialog.getSaveFileName(self,"Save BENCH witness inventory",
                    str(Path.home()/"Documents"/default),"Witness JSON (*.json)")
        if not output:
            return
        dest=Path(output)
        if not dest.name.startswith("BENCH_WITNESS_"):
            dest=dest.with_name("BENCH_WITNESS_"+dest.name)
        if dest.suffix.lower()!=".json":
            dest=dest.with_suffix(".json")
        self.add_media.setEnabled(False)
        self.witness_status.setText("HASHING SELECTED ORIGINAL FILE — NO MEDIA UPLOAD...")
        task=WitnessWorker(self.witness_file,dest,station,operator,note)
        self.workers.append(task)
        task.done.connect(self.complete_witness)
        task.finished.connect(lambda t=task:self._worker_finished(t))
        task.start()

    def complete_witness(self,success,detail):
        self.add_media.setEnabled(True)
        self.witness_status.setText(("SAVED: " if success else "FAILED: ")+detail[:200])
        if not success:
            QMessageBox.warning(self,"Witness inventory failed",detail)

    def _worker_finished(self,task):
        if task in self.workers:
            self.workers.remove(task)
        task.deleteLater()

    def shutdown(self):
        for task in list(self.workers):
            task.wait(5000)
