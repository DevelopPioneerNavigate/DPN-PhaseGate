"""PG-01 Build & Engineering Lab: native construction workbench.

Everything starts planned. Progress transitions are manually recorded with a
responsible operator and evidence note, never inferred from a concept image or
automatically marked safe, fabricated or scientifically verified.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QRectF, QPointF, QUrl, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QFont, QBrush, QLinearGradient, QDesktopServices
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QTabWidget, QDialog, QDialogButtonBox, QLineEdit, QLabel,
    QComboBox, QMessageBox, QFileDialog, QPushButton, QAbstractItemView
)

from desktop.build_plan import (
    RigError, read_manifest, read_progress, save_progress, progress_path,
    report_status, task_status, gate_review, export_bom_csv
)
from desktop.widgets import Surface, text_label, panel_layout
from desktop.fabrication import MEASUREMENTS, RECEIVING, prepare, update_receiving, inspect_dimension, fabrication_summary
from desktop.window_helpers import button


class TwinGateDrawing(QWidget):
    """Dimensioned, operator-friendly elevation: geometric design envelope only."""
    def __init__(self,spec,parent=None):
        super().__init__(parent)
        self.spec=spec
        self.setMinimumHeight(295)

    def paintEvent(self,event):
        p=QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w,h=self.width(),self.height()
        back=QLinearGradient(0,0,w,h)
        back.setColorAt(0,QColor("#09172B"))
        back.setColorAt(1,QColor("#181C35"))
        p.fillRect(self.rect(),back)
        p.scale(w/900,h/360)
        d=self.spec["dimensions_mm"]
        p.setPen(QPen(QColor("#2D4261"),.85))
        for x in range(0,901,35):p.drawLine(x,0,x,360)
        for y in range(0,361,35):p.drawLine(0,y,900,y)
        p.setPen(QPen(QColor("#6AAEC5"),2))
        p.drawLine(QPointF(40,281),QPointF(860,281))
        # Manual carriage rail, with an independent neutral center tray.
        p.setPen(QPen(QColor("#7393BD"),8))
        p.drawLine(QPointF(100,269),QPointF(800,269))
        p.setPen(QPen(QColor("#9BE8F1"),1.8))
        p.drawLine(QPointF(100,262),QPointF(800,262))
        p.setPen(QPen(QColor("#7E93B4"),1))
        for x in range(100,801,35):
            p.drawLine(QPointF(x,262),QPointF(x,275))
        p.setBrush(QColor("#345576"))
        p.setPen(QPen(QColor("#6DDDEF"),2))
        p.drawRoundedRect(QRectF(396,245,108,24),5,5)
        # Two concept frames with true ratio OD/ID, not invented coil details.
        ring_out=142
        ring_in=ring_out*d["clear_aperture_diameter"]/d["gate_outer_diameter"]
        for i,cx in enumerate((220,680)):
            p.setPen(QPen(QColor("#788DB3"),17))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QPointF(cx,156),ring_out/2,ring_out/2)
            p.setPen(QPen(QColor("#91C9E3" if i==0 else "#B58CF5"),5.5))
            p.drawEllipse(QPointF(cx,156),ring_in/2,ring_in/2)
            p.setPen(QPen(QColor("#637B98"),3))
            p.drawLine(QPointF(cx-56,222),QPointF(cx-56,281))
            p.drawLine(QPointF(cx+56,222),QPointF(cx+56,281))
            p.drawLine(QPointF(cx-73,281),QPointF(cx+73,281))
            p.setFont(QFont("Consolas",10,QFont.Weight.Bold))
            p.setPen(QColor("#E5F4FE"))
            p.drawText(QRectF(cx-85,305,170,20),Qt.AlignmentFlag.AlignCenter,"GATE "+("A" if i==0 else "B"))
            p.setPen(QPen(QColor("#8EA8CD"),1,Qt.PenStyle.DashLine))
            p.drawLine(QPointF(cx,70),QPointF(cx,260))
            p.drawLine(QPointF(cx-75,156),QPointF(cx+75,156))
        # Label dimension with explicit concept envelope figures.
        p.setPen(QPen(QColor("#84B4DD"),1))
        p.drawLine(QPointF(220,49),QPointF(680,49))
        for x in (220,680):p.drawLine(QPointF(x,42),QPointF(x,57))
        p.setPen(QColor("#BDECFB"))
        p.setFont(QFont("Consolas",11,QFont.Weight.Bold))
        p.drawText(QRectF(302,21,300,22),Qt.AlignmentFlag.AlignCenter,
                   "GATE C/C  "+str(d["gate_centers_separation"])+" mm  /  PROPOSED")
        p.setFont(QFont("Consolas",9))
        p.setPen(QColor("#C9D9F2"))
        p.drawText(QPointF(23,23),"PG-01 / BENCH RIG  •  ELEVATION")
        p.drawText(QPointF(24,337),f"RING  OD {d['gate_outer_diameter']} / CLEAR {d['clear_aperture_diameter']} mm")
        p.drawText(QPointF(488,337),f"MANUAL RAIL {d['rail_length']} mm / NO ACTUATION")
        p.setPen(QPen(QColor("#34577A"),1))
        p.drawRect(QRectF(.5,.5,899,359))
        p.end()


class ProgressDialog(QDialog):
    def __init__(self,package,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log PG-01 engineering work")
        self.setMinimumWidth(485)
        col=QVBoxLayout(self)
        col.addWidget(text_label("MANUAL ENGINEERING WORK LOG",16,"cyan",True))
        col.addWidget(text_label(package["id"]+"  •  "+package["name"],12,"text",True))
        col.addWidget(text_label("This is an operator claim. It does not certify fabrication, electrical "
                                 "safety, engineering approval or a physical research result.",11))
        col.addWidget(text_label("Status",11,"violet",True))
        self.status=QComboBox()
        self.status.addItem("In progress", "in_progress")
        self.status.addItem("Blocked / stop gate", "blocked")
        self.status.addItem("Operator-reported complete (evidence required)", "operator_reported_complete")
        col.addWidget(self.status)
        col.addWidget(text_label("Responsible operator",11,"violet",True))
        self.operator=QLineEdit()
        self.operator.setPlaceholderText("Person reporting the engineering work")
        self.operator.setMaxLength(120)
        col.addWidget(self.operator)
        col.addWidget(text_label("Inspection record / evidence note / file reference",11,"violet",True))
        self.evidence=QLineEdit()
        self.evidence.setPlaceholderText("e.g., measured clearance record + checked assembly photos")
        self.evidence.setMaxLength(400)
        col.addWidget(self.evidence)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|
                                  QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        col.addWidget(buttons)


class BuildLab(QWidget):
    open_assembly=Signal()
    def __init__(self,parent=None):
        super().__init__(parent)
        self.manifest=read_manifest()
        self.progress_error=None
        try:self.progress=read_progress()
        except RigError as exc:
            self.progress_error=str(exc)
            self.progress={"work_packages":{}}
        self._build()
        self.refresh()

    def _build(self):
        col=QVBoxLayout(self)
        col.setContentsMargins(27,22,27,22)
        col.setSpacing(11)
        col.addWidget(text_label("PG-01   /   STRUCTURAL ENGINEERING   /   BUILD REVISION v0.1",10,"cyan",True))
        h=QHBoxLayout()
        title=QVBoxLayout()
        title.addWidget(text_label("GATE ENGINEERING LAB",28,"text",True))
        title.addWidget(text_label(
            "Build the twin-gate rig: real frame geometry, components, stages, CAD and signed assembly work.",11))
        h.addLayout(title,1)
        source=button("OPEN CAD SOURCE ↗",True)
        source.clicked.connect(lambda:QDesktopServices.openUrl(
            QUrl("https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/blob/main/hardware/cad/pg01_bench.scad")))
        h.addWidget(source)
        studio=button("OPEN 3D ASSEMBLY STUDIO   ↗")
        studio.clicked.connect(lambda:self.open_assembly.emit())
        h.addWidget(studio)
        col.addLayout(h)
        cap=Surface("buildDisclaimer")
        cap_col=panel_layout(cap,11,5)
        cap_col.addWidget(text_label("ENGINEERING DESIGN • PARTS NOT PURCHASED • NO POWERED FIELD HARDWARE",12,"amber",True))
        cap_col.addWidget(text_label("Gate A/B frames and a manual payload carriage can be fabricated and tested. "
                                      "The energy-field mechanism is an open research question and cannot be "
                                      "procured or energized from the concept artwork.",11))
        col.addWidget(cap)
        self.drawing=TwinGateDrawing(self.manifest)
        col.addWidget(self.drawing,1)
        stat=QHBoxLayout()
        self.status=text_label("BUILD RECORD: NO REPORTED ASSEMBLY",12,"cyan",True)
        stat.addWidget(self.status)
        stat.addStretch()
        self.gates=text_label("GATES: 0 OPERATOR-REPORTED READY",11,"amber",True)
        stat.addWidget(self.gates)
        col.addLayout(stat)
        self.tabs=QTabWidget()
        self.tabs.setObjectName("engineeringTabs")
        col.addWidget(self.tabs,1)
        self._create_parts_tab()
        self._create_tasks_tab()
        self._create_release_tab()
        self._create_fabrication_tab()

    def _table(self,headers):
        t=QTableWidget()
        t.setColumnCount(len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        t.verticalHeader().setVisible(False)
        t.horizontalHeader().setStretchLastSection(True)
        t.setAlternatingRowColors(True)
        t.setMinimumHeight(190)
        return t

    def _create_parts_tab(self):
        host=QWidget()
        v=QVBoxLayout(host)
        v.setSpacing(8)
        v.addWidget(text_label("PROPOSED BILL OF MATERIALS / NO ITEMS PURCHASED",11,"cyan",True))
        self.parts=self._table(["ID","Component","Qty","Stage","Design requirement"])
        self.parts.setColumnWidth(0,120)
        self.parts.setColumnWidth(1,250)
        self.parts.setColumnWidth(2,50)
        self.parts.setColumnWidth(3,115)
        v.addWidget(self.parts)
        actions=QHBoxLayout()
        export=button("EXPORT ENGINEERING BOM AS CSV",True)
        export.clicked.connect(self.export_bom)
        actions.addWidget(export)
        actions.addStretch()
        v.addLayout(actions)
        self.tabs.addTab(host,"01  PARTS & BOM")

    def _create_tasks_tab(self):
        host=QWidget()
        v=QVBoxLayout(host)
        v.setSpacing(8)
        v.addWidget(text_label("DESIGN → SAFETY → STRUCTURE → SENSORS → CONTROLS",11,"cyan",True))
        self.tasks=self._table(["ID","Work package","Stage","Status","Requirements / acceptance"])
        self.tasks.setColumnWidth(0,90)
        self.tasks.setColumnWidth(1,275)
        self.tasks.setColumnWidth(2,110)
        self.tasks.setColumnWidth(3,180)
        v.addWidget(self.tasks)
        controls=QHBoxLayout()
        report=button("LOG SELECTED WORK PACKAGE")
        report.clicked.connect(self.log_selected)
        controls.addWidget(report)
        controls.addWidget(text_label("Operator + evidence required; dependencies enforced",10,"muted"))
        controls.addStretch()
        v.addLayout(controls)
        self.tabs.addTab(host,"02  ASSEMBLY TRACKER")

    def _create_release_tab(self):
        host=QWidget()
        v=QVBoxLayout(host)
        v.setSpacing(8)
        v.addWidget(text_label("NO AUTOMATIC SIGN-OFF / INDEPENDENT REVIEW REQUIRED",11,"amber",True))
        self.gate_table=self._table(["Gate","Acceptance condition","Operator report","Independent approval"])
        self.gate_table.setColumnWidth(0,65)
        self.gate_table.setColumnWidth(1,310)
        self.gate_table.setColumnWidth(2,185)
        v.addWidget(self.gate_table)
        v.addWidget(text_label("Build logs are stored locally in your Windows user profile. "
                               "This app cannot sign off safety or experimental physics. "
                               "No entries are added to the scientific experiment manifest.",11))
        self.tabs.addTab(host,"03  ACCEPTANCE GATES")

    def _create_fabrication_tab(self):
        host=QWidget()
        v=QVBoxLayout(host)
        v.setSpacing(8)
        v.addWidget(text_label("REV A FABRICATION INSPECTION / UNAPPROVED PROPOSED TOLERANCES",11,"amber",True))
        self.measure_table=self._table(["Dimension","Nominal ± trial mm","Latest mm","Deviation","Evidence status"])
        for i,key in enumerate(MEASUREMENTS):
            self.measure_table.insertRow(i)
            nominal,tol=MEASUREMENTS[key]
            for j,datum in enumerate([key,f"{nominal:.1f} ± {tol:.1f}","NOT MEASURED","—","UNREVIEWED"]):
                self.measure_table.setItem(i,j,self._cell(datum))
        v.addWidget(self.measure_table)
        self.receiving_table=self._table(["Component ID","Name","Receiving / QC state"])
        v.addWidget(self.receiving_table)
        row=QHBoxLayout()
        measure=button("RECORD DIMENSION CHECK")
        measure.clicked.connect(self.record_dimension)
        receive=button("RECORD COMPONENT RECEIPT",True)
        receive.clicked.connect(self.record_receipt)
        row.addWidget(measure)
        row.addWidget(receive)
        row.addStretch()
        v.addLayout(row)
        self.tabs.addTab(host,"04  FIT & RECEIVING")

    def _inspection_dialog(self,title,fields):
        dialog=QDialog(self)
        dialog.setWindowTitle(title)
        layout=QVBoxLayout(dialog)
        controls={}
        for key,placeholder in fields:
            layout.addWidget(text_label(key,11,"cyan",True))
            entry=QLineEdit()
            entry.setPlaceholderText(placeholder)
            entry.setMaxLength(400)
            layout.addWidget(entry)
            controls[key]=entry
        actions=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|
                                  QDialogButtonBox.StandardButton.Cancel)
        actions.accepted.connect(dialog.accept)
        actions.rejected.connect(dialog.reject)
        layout.addWidget(actions)
        return dialog,controls

    def record_dimension(self):
        if self.progress_error:
            QMessageBox.warning(self,"Build ledger invalid","Repair the local build log before writing.")
            return
        row=self.measure_table.currentRow()
        if row<0:
            QMessageBox.information(self,"Select a dimension","Choose an inspection dimension first.")
            return
        key=list(MEASUREMENTS)[row]
        dialog,fields=self._inspection_dialog("Inspect "+key,[
            ("Measured millimeters","Enter actual physical measurement"),
            ("Operator","Who measured it?"),
            ("Evidence reference","Caliper ID / calibration and inspection note")])
        if dialog.exec()!=QDialog.DialogCode.Accepted:return
        try:
            inspect_dimension(self.manifest,self.progress,key,
                float(fields["Measured millimeters"].text()),fields["Operator"].text(),
                fields["Evidence reference"].text())
            save_progress(self.progress)
            self.refresh()
        except (ValueError,OSError,RigError) as exc:
            QMessageBox.warning(self,"Inspection not recorded",str(exc))

    def record_receipt(self):
        if self.progress_error:
            QMessageBox.warning(self,"Build ledger invalid","Repair the local build log before writing.")
            return
        row=self.receiving_table.currentRow()
        if row<0:
            QMessageBox.information(self,"Select an item","Choose a component first.")
            return
        comp=self.manifest["components"][row]
        dialog,fields=self._inspection_dialog("Receive "+comp["id"],[
            ("Receiving state","quoted / ordered / received_uninspected / inspected_accepted / rejected"),
            ("Operator","Who checked the item?"),
            ("Evidence reference","Invoice / inspection photo / receiving record")])
        if dialog.exec()!=QDialog.DialogCode.Accepted:return
        try:
            update_receiving(self.manifest,self.progress,comp["id"],
                fields["Receiving state"].text().strip(),
                fields["Operator"].text(),fields["Evidence reference"].text())
            save_progress(self.progress)
            self.refresh()
        except (ValueError,OSError,RigError) as exc:
            QMessageBox.warning(self,"Receiving record not saved",str(exc))

    @staticmethod
    def _cell(value):
        return QTableWidgetItem(str(value))

    def refresh(self):
        parts=self.manifest["components"]
        self.parts.setRowCount(len(parts))
        for i,p in enumerate(parts):
            for j,value in enumerate([p["id"],p["name"],p["quantity"],p["stage"],
                                      p["specification"]]):
                self.parts.setItem(i,j,self._cell(value))
        tasks=self.manifest["work_packages"]
        self.tasks.setRowCount(len(tasks))
        for i,t in enumerate(tasks):
            status=task_status(t["id"],self.progress)
            label={"planned":"PLANNED","in_progress":"IN PROGRESS",
                   "blocked":"BLOCKED","operator_reported_complete":"REPORTED COMPLETE"}[status]
            for j,value in enumerate([t["id"],t["name"],t["stage"],label,t["acceptance"]]):
                self.tasks.setItem(i,j,self._cell(value))
        gates=gate_review(self.manifest,self.progress)
        self.gate_table.setRowCount(len(gates))
        count=0
        for i,gate in enumerate(gates):
            ready=gate["operator_reported_ready"]
            if ready:count+=1
            for j,value in enumerate([gate["id"],gate["name"],
                                      "REPORTED SATISFIED" if ready else "NOT READY",
                                      "NOT APPROVED / REVIEW NEEDED"]):
                self.gate_table.setItem(i,j,self._cell(value))
        done=sum(task_status(t["id"],self.progress)=="operator_reported_complete"
                 for t in tasks)
        if self.progress_error:
            self.status.setText("BUILD LOG INVALID — REQUIRES MANUAL RECOVERY")
            self.status.setStyleSheet("color:#FFBF9E")
        else:
            self.status.setText(f"WORK PACKAGES: {done}/{len(tasks)} OPERATOR-REPORTED COMPLETE")
        self.gates.setText(f"REVIEW GATES: {count}/{len(gates)} SELF-REPORTED • 0 INDEPENDENTLY APPROVED")
        prepare(self.progress)
        for i,key in enumerate(MEASUREMENTS):
            entries=self.progress["dimensional_inspections"].get(key,{}).get("history",[])
            if entries:
                last=entries[-1]
                self.measure_table.setItem(i,2,self._cell(last["observed_mm"]))
                self.measure_table.setItem(i,3,self._cell(last["deviation_mm"]))
                self.measure_table.setItem(i,4,self._cell(
                    "WITHIN TRIAL RANGE / UNREVIEWED" if last["within_candidate_range"]
                    else "OUTSIDE TRIAL RANGE / REVIEW"))
        self.receiving_table.setRowCount(len(self.manifest["components"]))
        for i,comp in enumerate(self.manifest["components"]):
            state=self.progress["component_receiving"].get(comp["id"],{}).get("status","not_ordered")
            for j,val in enumerate([comp["id"],comp["name"],state.upper()]):
                self.receiving_table.setItem(i,j,self._cell(val))


    def log_selected(self):
        if self.progress_error:
            QMessageBox.warning(self,"Invalid local build ledger",
                "Existing progress data failed integrity checks: "+self.progress_error+
                "\nNo changes will be made until the data are inspected.")
            return
        row=self.tasks.currentRow()
        if row<0:
            QMessageBox.information(self,"Choose work package",
                                    "Select one assembly work package from the table first.")
            return
        task=self.manifest["work_packages"][row]
        dialog=ProgressDialog(task,self)
        if dialog.exec()!=QDialog.DialogCode.Accepted:
            return
        try:
            report_status(self.manifest,self.progress,task["id"],
                          dialog.status.currentData(),dialog.operator.text(),
                          dialog.evidence.text())
            save_progress(self.progress)
        except (RigError,OSError,ValueError) as exc:
            QMessageBox.warning(self,"Engineering record not saved",str(exc))
            return
        self.refresh()

    def export_bom(self):
        destination,_=QFileDialog.getSaveFileName(
            self,"Save proposed component list",str(Path.home()/"Documents"/"PG01_Proposed_BOM.csv"),
            "Comma-separated values (*.csv)")
        if not destination:return
        path=Path(destination)
        try:
            with path.open("x",encoding="utf-8-sig",newline="") as f:
                f.write(export_bom_csv(self.manifest))
        except (RigError,OSError,ValueError) as exc:
            QMessageBox.warning(self,"Cannot export BOM",str(exc))
            return
        QMessageBox.information(self,"Proposed BOM exported",
            "Saved proposed engineering components. All procurement statuses remain NOT PURCHASED.")
