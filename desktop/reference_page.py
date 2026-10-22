"""DPN PhaseGate Reference Event Lab — native offline analytical workstation.

This page NEVER opens a camera, receives USB raw data, or edits the scientific
experiment registry. It analyzes ONLY existing unverified BENCH_OPTICAL files,
with their exact source bytes hash-checked before any plotting.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QFileDialog,
    QMessageBox, QLabel, QSpinBox, QFrame, QCheckBox
)
from desktop.aurora import LabBanner
from desktop.widgets import Surface, panel_layout, text_label
from desktop.window_helpers import button
from desktop.reference_event import (
    ReferenceError, build_review, save_review, REGIONS
)


class ReferenceWorker(QThread):
    done=Signal(object, str)

    def __init__(self,a,b,region_a,region_b,contrast,same_epoch,parent=None):
        super().__init__(parent)
        self.args=(a,b,region_a,region_b,float(contrast),bool(same_epoch))

    def run(self):
        try:
            result=build_review(*self.args)
            self.done.emit(result,"")
        except (OSError, ValueError, ReferenceError) as exc:
            self.done.emit(None,str(exc)[:240])


class LuminancePlot(QWidget):
    """Native grayscale brightness plot; no misleading physical time axes."""
    def __init__(self):
        super().__init__()
        self.series=None
        self.setMinimumHeight(215)

    def set_review(self,review):
        self.series=review
        self.update()

    def paintEvent(self,event):
        p=QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w,h=self.width(),self.height()
        p.fillRect(self.rect(),QColor("#0D182C"))
        left,right,top,bottom=53,24,22,32
        width=max(1,w-left-right)
        height=max(1,h-top-bottom)
        p.setPen(QPen(QColor("#283C5A"),1))
        for i in range(6):
            y=top+i*height/5
            p.drawLine(QPointF(left,y),QPointF(w-right,y))
        p.setFont(QFont("Consolas",9))
        p.setPen(QColor("#869EBF"))
        p.drawText(10,top+11,"255")
        p.drawText(22,top+height-2,"0")
        p.drawText(left,h-11,"CAPTURE FRAME INDEX (NOT EXPOSURE TIME)")
        if self.series is not None:
            for key,paint in (("trace_a","#60DDED"),("trace_b","#C38EFC")):
                data=self.series.get(key,{}).get("frames",[])
                if len(data)<2:
                    continue
                color=QColor(paint)
                p.setPen(QPen(color,2.3))
                prev=None
                for i,point in enumerate(data):
                    x=left+(i/(len(data)-1))*width
                    y=top+height*(1-point["brightness"]/255)
                    pt=QPointF(x,y)
                    if prev is not None:
                        p.drawLine(prev,pt)
                    prev=pt
                flash=self.series["comparison"]["station_"+key[-1]].get("onset")
                if flash:
                    p.setPen(QPen(color,1.2,Qt.PenStyle.DashLine))
                    x=left+(flash["first_bright_index"]/(len(data)-1))*width
                    p.drawLine(QPointF(x,top),QPointF(x,top+height))
        else:
            p.setPen(QColor("#869EBF"))
            p.drawText(QRectF(left+5,top,width-10,height),
                       Qt.AlignmentFlag.AlignCenter,"SELECT TWO VERIFIED BENCH CAPTURES TO PLOT")
        p.end()


class ReferenceEventLab(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.directories={"A":None,"B":None}
        self.worker=None
        self.review=None
        self._build()

    def _build(self):
        col=QVBoxLayout(self)
        col.setContentsMargins(30,22,30,30)
        col.setSpacing(14)
        col.addWidget(text_label("PG-01  /  POST-CAPTURE LIGHT REFERENCE  /  OFFLINE REVIEW",10,"cyan",True))
        col.addWidget(text_label("REFERENCE EVENT LAB",28,"text",True))
        col.addWidget(LabBanner(
            "LIGHT FLASH / TWO-STATION REVIEW",
            "Hash-verified bench frames, contrast transitions and host-receipt intervals. Actual camera exposure time remains unknown.",
            "#73DCF5"))
        warn=Surface("referenceWarning")
        warn_v=panel_layout(warn,15,7)
        warn_v.addWidget(text_label("REFERENCE EVENT ≠ OBJECT TRANSFER",13,"amber",True))
        warn_v.addWidget(text_label(
            "An optical flash can provide a future timebase control, but this tool currently "
            "compares host receipt intervals only. Equal timestamps cannot prove synchronized exposure "
            "or identify transported matter. Never interpret analysis as a verified portal.",11))
        col.addWidget(warn)
        selectors=QHBoxLayout()
        self.regions={}
        self.path_labels={}
        for station in ("A","B"):
            card=Surface("referenceSelect"+station)
            v=panel_layout(card,16,8)
            v.addWidget(text_label("CAMERA "+station+" / BENCH FRAMES",13,
                                    "cyan" if station=="A" else "violet",True))
            choose=button("SELECT BENCH_OPTICAL FOLDER",True)
            choose.clicked.connect(lambda checked=False,s=station:self.pick_folder(s))
            v.addWidget(choose)
            path=text_label("NO CAPTURE SELECTED",11,"muted")
            self.path_labels[station]=path
            v.addWidget(path)
            v.addWidget(text_label("Light measurement region",10,"muted"))
            roi=QComboBox()
            for region in ("CENTER","FULL","TOP","BOTTOM","LEFT","RIGHT"):
                roi.addItem(region,region)
            self.regions[station]=roi
            v.addWidget(roi)
            selectors.addWidget(card,1)
        col.addLayout(selectors)
        setup=Surface("referenceSettings")
        sv=panel_layout(setup,13,9)
        options=QHBoxLayout()
        options.addWidget(text_label("Minimum brightness rise (grayscale levels)",11,"muted"))
        self.contrast=QSpinBox()
        self.contrast.setRange(5,100)
        self.contrast.setValue(22)
        options.addWidget(self.contrast)
        options.addStretch()
        self.analyze=button("◈  ANALYZE TWO BENCH CAPTURES")
        self.analyze.clicked.connect(self.start)
        options.addWidget(self.analyze)
        sv.addLayout(options)
        self.same_epoch=QCheckBox(
            "I confirm both captures used the SAME HOST without reboot and share an "
            "overlapping monotonic clock epoch (operator declaration; not independently verified).")
        self.same_epoch.setChecked(False)
        sv.addWidget(self.same_epoch)
        sv.addWidget(text_label(
            "Unchecked = no B−A time difference reported. A declaration alone never proves "
            "exposure synchronization or shared-flash identity.",11,"amber"))
        col.addWidget(setup)
        graph=Surface("referenceChart")
        gv=panel_layout(graph,16,8)
        gv.addWidget(text_label("LUMINANCE / ORIGINAL FRAME INDEX   •   A CYAN / B VIOLET",
                                12,"cyan",True))
        self.plot=LuminancePlot()
        gv.addWidget(self.plot)
        col.addWidget(graph)
        review=Surface("referenceResult")
        rv=panel_layout(review,14,8)
        rv.addWidget(text_label("SCIENTIFIC INTERPRETATION / BOUNDED CLAIMS",12,"violet",True))
        self.status=text_label("NO INPUT • WAITING FOR LOCAL OPERATOR-SELECTED BENCH RECORDS",
                               12,"amber",True)
        rv.addWidget(self.status)
        self.details=text_label(
            "The resulting interval bounds are for post-read host receipt events only; "
            "unknown USB driver and sensor exposure delays are not bounded by this code.",11)
        rv.addWidget(self.details)
        actions=QHBoxLayout()
        self.export=button("SAVE UNVERIFIED ANALYSIS JSON",True)
        self.export.clicked.connect(self.save)
        self.export.setEnabled(False)
        actions.addWidget(self.export)
        actions.addStretch()
        rv.addLayout(actions)
        col.addWidget(review)
        col.addStretch()

    def pick_folder(self,station):
        folder=QFileDialog.getExistingDirectory(
            self,"Choose existing Station "+station+" BENCH_OPTICAL recording",
            str(Path.home()/"Documents"))
        if not folder:
            return
        name=Path(folder).name
        if not name.startswith("BENCH_OPTICAL_"):
            QMessageBox.warning(self,"Not a bench recording",
                                "Only BENCH_OPTICAL_* directories are supported.")
            return
        self.directories[station]=Path(folder)
        self.path_labels[station].setText(name)
        self.review=None
        self.export.setEnabled(False)
        self.status.setText("CAPTURES SELECTED / ANALYSIS NOT YET VERIFIED")

    def start(self):
        if not all(self.directories.values()):
            QMessageBox.warning(self,"Both stations required",
                                "Select A and B verified BENCH_OPTICAL directories first.")
            return
        if self.worker is not None and self.worker.isRunning():
            return
        self.review=None
        self.plot.set_review(None)
        self.export.setEnabled(False)
        self.analyze.setEnabled(False)
        self.status.setText("HASHING ORIGINAL FRAME FILES / ANALYZING BRIGHTNESS... NO UPLOAD")
        self.worker=ReferenceWorker(
            self.directories["A"],self.directories["B"],
            self.regions["A"].currentData(),self.regions["B"].currentData(),
            self.contrast.value(),self.same_epoch.isChecked(),self)
        self.worker.done.connect(self.finished_analysis)
        self.worker.start()

    def finished_analysis(self,result,error):
        self.analyze.setEnabled(True)
        if error or result is None:
            self.status.setText("ANALYSIS REJECTED / MISSING OR UNSAFE INPUT")
            self.details.setText(error)
            self.export.setEnabled(False)
            return
        self.review=result
        self.plot.set_review(result)
        summary=result["comparison"]
        self.status.setText(summary["state"])
        interval=summary.get("host_receipt_bracket_delta_ms")
        if interval is None:
            explanation="No sustained reference brightness transition at both stations. "
        else:
            explanation=(f"Apparent B minus A HOST RECEIPT bracket: "
                f"[{interval['lower']:.1f}, {interval['upper']:.1f}] ms. ")
        self.details.setText(explanation+
            "This is NOT an exposure-time estimate. Physical flash identity, camera latency "
            "and synchronization remain unknown. No object transfer inferred.")
        self.export.setEnabled(True)

    def save(self):
        if self.review is None:
            return
        filename="BENCH_REFERENCE_"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+".json"
        path,_=QFileDialog.getSaveFileName(
            self,"Save unverified reference review",str(Path.home()/"Documents"/filename),
            "Bench Review JSON (*.json)")
        if not path:
            return
        dest=Path(path)
        if not dest.name.startswith("BENCH_REFERENCE_"):
            dest=dest.with_name("BENCH_REFERENCE_"+dest.name)
        if dest.suffix.lower()!=".json":
            dest=dest.with_suffix(".json")
        try:
            digest=save_review(self.review,dest)
        except (ReferenceError,OSError,ValueError) as exc:
            QMessageBox.warning(self,"Failed to save reference review",str(exc))
            return
        QMessageBox.information(self,"Unverified review exported",
            "Local benchmark review saved with SHA-256. Source frames were not modified.\n"
            "Digest: "+digest+"\n\nThis does NOT prove camera synchronization or transfer.")

    def shutdown(self):
        task=self.worker
        if task is not None and task.isRunning():
            task.wait()  # do not destroy a running QThread during large hash reviews
