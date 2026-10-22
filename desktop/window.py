"""DPN PhaseGate // Native Research Operations desktop interface.

Every page is a working Qt widget. All station values remain synthetic.
"""
from __future__ import annotations
import platform
import sys
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QUrl, QSize
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap, QDesktopServices, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, QStackedWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QFileDialog, QMessageBox, QComboBox, QCheckBox, QSizePolicy
)
from PySide6.QtCore import qVersion
from desktop.model import VERSION, MODE, DISCLAIMER, DOC_BASE, inventory, literature, simulated_samples, export_demo
from desktop.widgets import C, Surface, Metric, OrbitalGate, Station, TrendChart, text_label, panel_layout
from desktop.hardware_page import HardwareLab
from desktop.evidence_page import EvidenceLab
from desktop.optical_page import OpticalLab
from desktop.aurora import AuroraHero, PipelineRail, CommandPalette


def ui_button(text, secondary=False):
    b=QPushButton(text)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setProperty("variant", "secondary" if secondary else "primary")
    b.setMinimumHeight(39)
    return b


def horizontal(*widgets, spacing=12):
    row=QHBoxLayout()
    row.setSpacing(spacing)
    for item in widgets:
        row.addWidget(item)
    return row


def section_heading(kicker, heading):
    block=QWidget()
    col=QVBoxLayout(block)
    col.setContentsMargins(0,0,0,0)
    col.setSpacing(5)
    col.addWidget(text_label(kicker,10,"cyan",True))
    col.addWidget(text_label(heading,22,"text",True))
    return block


def heading_rule():
    line=QFrame()
    line.setFixedHeight(1)
    line.setStyleSheet("background: #2B3E5B; border: 0;")
    return line


class ResearchWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DPN PhaseGate — Research Operations // Native v"+VERSION)
        self.resize(1560,960)
        self.setMinimumSize(1100,750)
        self.setObjectName("ResearchWindow")
        self.frame=180
        self.motion=True
        self.record=inventory()
        self.samples=simulated_samples(self.frame, 120)
        self.gates=[]
        self.charts=[]
        self.nav={}
        self.pages=[]
        self.build_ui()
        self.apply_theme()
        self.timer=QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(1100)
        self.tick()
        self._keyboard_shortcuts=[]
        shortcut=QShortcut(QKeySequence("Ctrl+K"),self)
        shortcut.activated.connect(self.open_palette)
        self._keyboard_shortcuts.append(shortcut)
        fullscreen=QShortcut(QKeySequence("F11"),self)
        fullscreen.activated.connect(self.toggle_immersive)
        self._keyboard_shortcuts.append(fullscreen)
        for i,name in enumerate(self.pages[:9],1):
            key=QShortcut(QKeySequence("Ctrl+"+str(i)),self)
            key.activated.connect(lambda label=name:self.navigate(label))
            self._keyboard_shortcuts.append(key)
        if len(self.pages)==10:
            key=QShortcut(QKeySequence("Ctrl+0"),self)
            key.activated.connect(lambda:self.navigate(self.pages[9]))
            self._keyboard_shortcuts.append(key)
 
    def apply_theme(self):
        self.setStyleSheet("""
        QMainWindow { background:#080E1A; }
        QWidget { font-family:'Segoe UI';color:#EEF3FF;font-size:12px; }
        QFrame#leftRail {background:qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 #0E1527,stop:1 #0B1020); border-right:1px solid #28354D;}
        QFrame#topBar {background:#101729;border-bottom:1px solid #303C56;}
        QFrame#pipelineRail {background:#141E33;border:1px solid #334665;border-radius:13px;}
        QFrame#surface,QFrame#metric,QFrame#station {
            background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #19253D,stop:1 #111B2F);
            border:1px solid #334462; border-radius:16px;}
        QFrame#station {border:1px solid #465E84;}
        QFrame#missionDock {background:#172137;border:1px solid #38496B;border-radius:15px;}
        QPushButton {border-radius:10px;padding:10px 17px;font-size:12px;font-weight:750;
            background:#8362E7;border:1px solid #AB85F4;color:#FBF8FF;}
        QPushButton:hover {background:#9B71F6;border-color:#C4A4FF;}
        QPushButton:pressed {background:#6946BF;}
        QPushButton:disabled {background:#242D42;color:#7787A5;border-color:#364459;}
        QPushButton[variant="secondary"] {background:#232E49;border:1px solid #4B5875;}
        QPushButton[variant="secondary"]:hover {background:#2B3A5B;border-color:#66CFED;}
        QPushButton[role="nav"] {background:transparent;border:1px solid transparent;
           border-radius:10px;text-align:left;color:#96AACC;
           font-size:12px;font-weight:600;padding:11px 17px;}
        QPushButton[role="nav"]:hover {background:#1C2945;color:#ECF5FF;}
        QPushButton[role="nav"]:checked {background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
           stop:0 #352856,stop:1 #222A48);border:1px solid #595180;
           border-left:3px solid #A87CFF;color:#F8F5FF;}
        QScrollArea,QScrollArea > QWidget > QWidget {background:transparent;border:0;}
        QScrollBar:vertical {width:8px;background:#131D30;border:0;}
        QScrollBar::handle:vertical {background:#586A90;border-radius:4px;min-height:38px;}
        QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical {height:0px;}
        QTableWidget {background:#141E32;alternate-background-color:#1B2A43;
           border:1px solid #334A68;gridline-color:#2D3F59;selection-background-color:#514879;}
        QHeaderView::section {background:#212E49;color:#BBD1EC;border:0;
           border-right:1px solid #354966;padding:10px;font-weight:750;}
        QComboBox,QLineEdit,QTextEdit,QSpinBox,QDoubleSpinBox {
           background:#1C2A43;color:#EEF6FF;border:1px solid #435779;border-radius:9px;
           padding:8px;selection-background-color:#7F5AC4;}
        QComboBox:hover,QLineEdit:hover,QTextEdit:hover {border-color:#7B89B7;}
        QComboBox QAbstractItemView {background:#1D2A43;color:#F0F5FF;
           selection-background-color:#645393;}
        QCheckBox {spacing:12px;font-size:12px;}
        QCheckBox::indicator {width:17px;height:17px;}
        QDialog#commandPalette {background:#101B30;border:1px solid #695894;}
        QLineEdit#paletteSearch {padding:14px;font-size:15px;border-color:#7F69C3;}
        QListWidget#paletteList {background:#18243C;border:1px solid #344967;
          font-size:13px;padding:5px;selection-background-color:#443D7A;}
        QLabel#heroKicker {color:#6BE4F3;font-size:10px;font-weight:800;letter-spacing:2px;
            border-radius:8px;background:#203A55;padding:7px 10px;}
        QLabel#heroHeading {font-size:30px;font-weight:900;letter-spacing:-0.7px;color:#F1F6FF;
            background:transparent;}
        QLabel#heroDescription {font-size:13px;line-height:1.35;color:#C3D2EE;background:transparent;}
        QLabel#heroMeta {font-size:10px;color:#94B8D1;font-weight:700;background:transparent;}
        """)
        
    def build_ui(self):
        host=QWidget()
        self.setCentralWidget(host)
        root=QHBoxLayout(host)
        root.setContentsMargins(0,0,0,0)
        root.setSpacing(0)
        self.rail=QFrame()
        self.rail.setObjectName("leftRail")
        self.rail.setFixedWidth(244)
        rail_col=QVBoxLayout(self.rail)
        rail_col.setContentsMargins(15,27,13,20)
        rail_col.setSpacing(5)
        logo=text_label("◈  DPN / 09",25,"text",True)
        rail_col.addWidget(logo)
        rail_col.addWidget(text_label("D E V E L O P   /   P I O N E E R",9,"cyan",True))
        rail_col.addWidget(text_label("N A V I G A T E",9,"violet",True))
        rail_col.addSpacing(21)
        rail_col.addWidget(text_label("WORKSPACE  /  RESEARCH OPERATIONS",10,"violet",True))
        rail_col.addWidget(heading_rule())
        rail_col.addSpacing(12)
        rail_col.addWidget(text_label("  NAVIGATION  /  CTRL + K",10,"muted",True))
        for name,ico in [
            ("Command Center","◈"),("Station Matrix","◎"),("Hardware Lab","▦"),
            ("Optical Evidence","◉"),
            ("Calibration & Evidence","◇"),
            ("Signal Analytics","⌁"),("Research Vault","▣"),
            ("Experiment Ledger","▤"),("System Diagnostics","⚙"),
            ("Preferences","◇"),
        ]:
            if name=="Hardware Lab":
                rail_col.addSpacing(7)
                rail_col.addWidget(text_label("  INSTRUMENTS / EVIDENCE",9,"violet",True))
            elif name=="System Diagnostics":
                rail_col.addSpacing(7)
                rail_col.addWidget(text_label("  SYSTEM & DISPLAY",9,"violet",True))
            btn=QPushButton(f"{ico}     {name}")
            btn.setProperty("role","nav")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, s=name:self.navigate(s))
            rail_col.addWidget(btn)
            self.nav[name]=btn
        rail_col.addStretch()
        rail_col.addWidget(heading_rule())
        rail_col.addWidget(text_label("●  SIM GRAPHS / USB LAB",11,"cyan",True))
        rail_col.addWidget(text_label("Native desktop • no browser\nLive USB RAW only in Hardware Lab\nNo physical matter transfer",10))
        root.addWidget(self.rail)
        body=QWidget()
        body_col=QVBoxLayout(body)
        body_col.setContentsMargins(0,0,0,0)
        body_col.setSpacing(0)
        top=QFrame()
        top.setObjectName("topBar")
        top.setFixedHeight(65)
        row=QHBoxLayout(top)
        row.setContentsMargins(29,0,29,0)
        row.addWidget(text_label("◈   MISSION CONTROL     /     PHASEGATE     /     PG-01",11,"muted",True))
        row.addStretch()
        quick=ui_button("⌕  GO TO…    Ctrl+K",True)
        quick.setMinimumHeight(33)
        quick.clicked.connect(self.open_palette)
        row.addWidget(quick)
        row.addSpacing(12)
        row.addWidget(text_label("●  SIMULATED SCENE  /  RAW DATA ISOLATED",10,"cyan",True))
        self.clock=text_label("",11,"muted",True)
        row.addSpacing(21)
        row.addWidget(self.clock)
        body_col.addWidget(top)
        self.stack=QStackedWidget()
        body_col.addWidget(self.stack)
        root.addWidget(body,1)
        pages=[
            ("Command Center",self.overview_page()),
            ("Station Matrix",self.stations_page()),
            ("Hardware Lab",self.hardware_page()),
            ("Optical Evidence",self.optical_page()),
            ("Calibration & Evidence",self.evidence_page()),
            ("Signal Analytics",self.analytics_page()),
            ("Research Vault",self.research_page()),
            ("Experiment Ledger",self.experiments_page()),
            ("System Diagnostics",self.system_page()),
            ("Preferences",self.preferences_page()),
        ]
        for label,content in pages:
            self.stack.addWidget(self.scrolling_page(content))
            self.pages.append(label)
        self.navigate("Command Center")

    def scrolling_page(self,content):
        scroll=QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(content)
        return scroll

    def page(self,kicker,title,subtitle):
        host=QWidget()
        host.setStyleSheet("background: transparent;")
        col=QVBoxLayout(host)
        col.setContentsMargins(30,22,30,31)
        col.setSpacing(14)
        col.addWidget(text_label(kicker,10,"cyan",True))
        col.addWidget(text_label(title,28,"text",True))
        col.addWidget(text_label(subtitle,12,"muted"))
        return host,col

    def warning(self):
        card=Surface()
        row=QHBoxLayout(card)
        row.setContentsMargins(15,11,15,11)
        row.addWidget(text_label("⚠  DEMO GRAPHS ARE SYNTHETIC. REAL USB RAW COUNTS APPEAR ONLY IN HARDWARE LAB. "
                                 "NO OBJECT TELEPORTATION.",11,"amber",True))
        return card

    def overview_page(self):
        host,col=self.page(
            "MISSION CONTROL  /  DPN SCIENTIFIC OPERATIONS",
            "PHASEGATE  /  OVERVIEW",
            "Precision instrumentation • Evidence integrity • Research readiness"
        )
        # Original cinematic native Qt scene, not a PNG and not browser content.
        self.aurora_hero=AuroraHero()
        self.aurora_hero.station_requested.connect(lambda:self.navigate("Hardware Lab"))
        self.aurora_hero.evidence_requested.connect(lambda:self.navigate("Calibration & Evidence"))
        col.addWidget(self.aurora_hero)
        self.gates.append(self.aurora_hero.field)
        col.addWidget(self.warning())
        timeline=PipelineRail()
        col.addWidget(timeline)
        status_title=QHBoxLayout()
        status_title.addWidget(section_heading("PROGRAM INTELLIGENCE  /  RESEARCH NOT REALITY",
                                               "Research at a glance"))
        status_title.addStretch()
        go=ui_button("EXPLORE ALL SYSTEMS   →",True)
        go.clicked.connect(lambda:self.navigate("Station Matrix"))
        status_title.addWidget(go)
        col.addLayout(status_title)
        stat=QHBoxLayout()
        stat.setSpacing(13)
        self.overview_metrics=[
            Metric("PRIMARY SOURCES",self.count_text("sources"),
                   "Read-only literature index","cyan"),
            Metric("HYPOTHESES",self.count_text("hypotheses"),
                   "Scientific research registry","violet"),
            Metric("REAL RUN RECORDS",self.count_text("experiments"),
                   "Approved experiment manifest","text"),
            Metric("MATTER TRANSFER","NOT VERIFIED",
                   "No demonstrated physical portal","amber"),
        ]
        for widget in self.overview_metrics:
            stat.addWidget(widget,1)
        col.addLayout(stat)
        bottom=QHBoxLayout()
        bottom.setSpacing(13)
        trace=Surface()
        trace_col=panel_layout(trace,20,8)
        head=QHBoxLayout()
        head.addWidget(text_label("SIGNAL INTELLIGENCE",13,"cyan",True))
        head.addStretch()
        head.addWidget(text_label("100% SIMULATED / DEMO",10,"amber",True))
        trace_col.addLayout(head)
        chart=TrendChart()
        self.overview_chart=chart
        self.charts.append(chart)
        trace_col.addWidget(chart,1)
        drill=ui_button("OPEN SIGNAL ANALYTICS",True)
        drill.clicked.connect(lambda:self.navigate("Signal Analytics"))
        trace_col.addWidget(drill,0,Qt.AlignmentFlag.AlignRight)
        bottom.addWidget(trace,7)
        mission=Surface()
        mission_col=panel_layout(mission,20,12)
        mission_col.addWidget(text_label("NEXT RESEARCH GATES",13,"violet",True))
        for name,description,colr in [
            ("01  HARDWARE REVIEW","Unapproved power / GPIO and mounting","amber"),
            ("02  CALIBRATION","Operator estimates • not certified","violet"),
            ("03  WITNESS TIMING","No synchronized device clocks","cyan"),
            ("04  EXPERIMENT","Not authorized or recorded","amber"),
        ]:
            mission_col.addWidget(text_label(name,11,colr,True))
            mission_col.addWidget(text_label(description,11,"muted"))
            mission_col.addWidget(heading_rule())
        mission_col.addStretch()
        bottom.addWidget(mission,5)
        col.addLayout(bottom)
        col.addStretch()
        return host

    def stations_page(self):
        host,col=self.page("INSTRUMENTATION / STATIONS","DUAL STATION MATRIX",
                           "Independent acquisition platforms — visualization-only demo.")
        col.addWidget(self.warning())
        row=QHBoxLayout()
        self.station_a=Station("A","Reference mass (simulated)")
        self.station_b=Station("B","Empty baseline (simulated)")
        self.gates.extend([self.station_a.gate,self.station_b.gate])
        row.addWidget(self.station_a)
        row.addWidget(self.station_b)
        col.addLayout(row)
        card=Surface()
        c=panel_layout(card)
        c.addWidget(text_label("SYSTEM INTERLOCKS  //  NOT ARMED",12,"cyan",True))
        grid=QGridLayout()
        checks=[("CONTROLLER LINKS","NOT CONNECTED"),("CAMERA STREAMS","NOT CONNECTED"),
                ("CALIBRATION","NOT PERFORMED"),("TIMEBASE","SIMULATED"),
                ("SAFETY APPROVAL","REQUIRED"),("MATTER TRANSFER","NOT DEMONSTRATED")]
        for i,(a,b) in enumerate(checks):
            block=Surface("interlock"+str(i))
            box=panel_layout(block,12,3)
            box.addWidget(text_label(a,10))
            box.addWidget(text_label(b,13,"amber",True))
            grid.addWidget(block,i//3,i%3)
        c.addLayout(grid)
        col.addWidget(card)
        col.addStretch()
        return host

    def hardware_page(self):
        self.hardware_lab = HardwareLab()
        return self.hardware_lab

    def optical_page(self):
        self.optical_lab=OpticalLab()
        return self.optical_lab

    def evidence_page(self):
        self.evidence_lab=EvidenceLab()
        return self.evidence_lab

    def analytics_page(self):
        host,col=self.page("DIGITAL SIGNAL INTELLIGENCE","SIGNAL ANALYTICS",
                           "Deterministic demonstration waveforms with no measurement significance.")
        col.addWidget(self.warning())
        card=Surface()
        v=panel_layout(card)
        v.addWidget(text_label("PG-01 SIMULATOR / DUAL MASS TRACE",13,"cyan",True))
        chart=TrendChart()
        chart.setMinimumHeight(350)
        self.charts.append(chart)
        v.addWidget(chart)
        v.addWidget(text_label("Both traces use separately normalized, explicitly labeled display ranges. "
                               "No cross-station mass or object movement is measured.",11))
        col.addWidget(card)
        row=QHBoxLayout()
        self.ana_a=Metric("STATION A / DEMO","--.---- g","Nominal 42 g, generated","cyan")
        self.ana_b=Metric("STATION B / DEMO","--.---- g","Nominal 0 g, generated","violet")
        row.addWidget(self.ana_a)
        row.addWidget(self.ana_b)
        col.addLayout(row)
        col.addStretch()
        return host

    def research_page(self):
        host,col=self.page("SCIENTIFIC INTELLIGENCE / LIBRARY","RESEARCH VAULT",
                           "Source-backed publications and active scientific reasoning.")
        col.addWidget(self.warning())
        card=Surface()
        v=panel_layout(card)
        top=QHBoxLayout()
        top.addWidget(text_label("LITERATURE INDEX // READ-ONLY",13,"cyan",True))
        top.addStretch()
        button=ui_button("OPEN SELECTED SOURCE ↗",True)
        button.clicked.connect(self.open_source)
        top.addWidget(button)
        v.addLayout(top)
        self.sources=literature()
        self.source_table=QTableWidget(len(self.sources),3)
        self.source_table.setHorizontalHeaderLabels(["SOURCE ID","TITLE / RESEARCH","CLASSIFICATION"])
        self.source_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.source_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.source_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.source_table.setAlternatingRowColors(True)
        self.source_table.verticalHeader().setVisible(False)
        self.source_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.ResizeToContents)
        self.source_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch)
        self.source_table.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeMode.ResizeToContents)
        for i,s in enumerate(self.sources):
            for n,key in enumerate(["id","title","type"]):
                self.source_table.setItem(i,n,QTableWidgetItem(s[key]))
        self.source_table.setMinimumHeight(310)
        if self.sources:
            self.source_table.selectRow(0)
        self.source_table.cellDoubleClicked.connect(lambda row,col:self.open_source())
        v.addWidget(self.source_table)
        col.addWidget(card)
        levels=Surface()
        c=panel_layout(levels)
        c.addWidget(text_label("EVIDENCE LADDER // L0 → L5",13,"violet",True))
        for level,explanation in [
            ("L0 / L1", "Concept and theoretical model: not a physical device."),
            ("L2 / L3", "Analogue/simulation or controlled lab effect: still not macroscopic transfer."),
            ("L4", "Independent replication: conclusions require skeptical re-testing."),
            ("L5", "Verified intact object transport: no evidence currently establishes this.")]:
            row=QHBoxLayout()
            row.addWidget(text_label(level,12,"cyan",True))
            row.addStretch()
            row.addWidget(text_label(explanation,11))
            c.addLayout(row)
        col.addWidget(levels)
        col.addStretch()
        return host

    def experiments_page(self):
        host,col=self.page("SCIENTIFIC EVIDENCE / AUDIT","EXPERIMENT LEDGER",
                           "Real results are not invented; this is a read-only register.")
        col.addWidget(self.warning())
        info=Surface()
        v=panel_layout(info,25,13)
        v.addWidget(text_label("REGISTRY STATUS // "+self.count_text("experiments")+" REPORTED RUNS",
                               17,"cyan",True))
        v.addWidget(text_label("PhaseGate has not performed a physical teleportation experiment. "
                               "No synthetic telemetry is permitted in the actual experiment manifest.",14))
        v.addWidget(text_label("NEXT GATE: Qualified safety review → preregistration → real "
                               "instrument calibration → null controls → traceable evidence.",12))
        actions=QHBoxLayout()
        btn=ui_button("VIEW EXPERIMENT PROTOCOL ↗",True)
        btn.clicked.connect(lambda:self.open_docs("docs/protocols/PG-PROT-NULL-001.md"))
        actions.addWidget(btn)
        btn2=ui_button("EVIDENCE RULES ↗",True)
        btn2.clicked.connect(lambda:self.open_docs("data/README.md"))
        actions.addWidget(btn2)
        actions.addStretch()
        v.addLayout(actions)
        col.addWidget(info)
        checklist=Surface()
        k=panel_layout(checklist)
        k.addWidget(text_label("REQUIRED BEFORE REAL EXPERIMENTS",14,"violet",True))
        for n,t in enumerate([
            "Hardware and qualified hazard assessment",
            "Independent witness and sample identity controls",
            "Calibrated instruments and clock error report",
            "Pre-registered sham/null protocol and stop conditions",
            "SHA-256 verified original evidence and independent review"]):
            k.addWidget(text_label(f"0{n+1}   ◌    {t}",12))
            k.addWidget(heading_rule())
        col.addWidget(checklist)
        col.addStretch()
        return host

    def system_page(self):
        host,col=self.page("RUNTIME ENGINEERING / INTERNAL STATUS","SYSTEM DIAGNOSTICS",
                           "Native Qt runtime and science-data validity boundary.")
        facts=[
            ("Application",f"DPN PhaseGate Native Desktop v{VERSION}"),
            ("Rendering","Qt Widgets / QPainter — no browser engine"),
            ("Python runtime",sys.version.split()[0]),
            ("Qt version",qVersion()),
            ("OS",platform.system()+" "+platform.release()),
            ("Execution mode","SYNTHETIC / OFFLINE"),
            ("Network services","None; this desktop app runs without a server"),
            ("Connected instruments","Only manually paired in Hardware Lab"),
            ("Recording / experiment writes","Manual BENCH-only capture; no experiment writes"),
            ("Actual transfer findings","NONE")
        ]
        card=Surface()
        v=panel_layout(card)
        v.addWidget(text_label("RUNTIME DETAIL // TRANSPARENT STATUS",13,"cyan",True))
        for key,value in facts:
            line=QHBoxLayout()
            line.addWidget(text_label(key,12,"muted"))
            line.addStretch()
            line.addWidget(text_label(value,12,"text",True))
            v.addLayout(line)
            v.addWidget(heading_rule())
        col.addWidget(card)
        buttons=QHBoxLayout()
        test=ui_button("RUN INTEGRITY CHECK")
        test.clicked.connect(self.verify_integrity)
        export=ui_button("EXPORT SYNTHETIC DIAGNOSTICS",True)
        export.clicked.connect(self.export)
        buttons.addWidget(test)
        buttons.addWidget(export)
        buttons.addStretch()
        col.addLayout(buttons)
        col.addStretch()
        return host

    def preferences_page(self):
        host,col=self.page("EXPERIENCE / DISPLAY SETTINGS","PREFERENCES",
                           "Adjust display animation and synthetic update frequency.")
        card=Surface()
        v=panel_layout(card)
        v.addWidget(text_label("GRAPHICS ENGINE",14,"cyan",True))
        self.motion_control=QCheckBox("Enable animated portal visualizations")
        self.motion_control.setChecked(True)
        self.motion_control.toggled.connect(self.toggle_motion)
        v.addWidget(self.motion_control)
        v.addWidget(text_label("Motion affects only artwork, not instrumentation, physics or evidence.",11))
        v.addWidget(heading_rule())
        v.addWidget(text_label("SIMULATED FEED UPDATE INTERVAL",12,"cyan",True))
        self.interval=QComboBox()
        for ms,name in [(500,"Fast • 0.5s"),(1100,"Balanced • 1.1s"),(2500,"Slow • 2.5s")]:
            self.interval.addItem(name,ms)
        self.interval.setCurrentIndex(1)
        self.interval.currentIndexChanged.connect(self.change_interval)
        v.addWidget(self.interval)
        v.addWidget(heading_rule())
        v.addWidget(text_label("EXPLICIT SCIENTIFIC DISCLOSURE",12,"amber",True))
        v.addWidget(text_label(DISCLAIMER,12))
        v.addWidget(text_label("These settings apply to the running app only. No hardware or external accounts are altered.",11))
        col.addWidget(card)
        btn=ui_button("EXPORT CURRENT SYNTHETIC SNAPSHOT",True)
        btn.clicked.connect(self.export)
        col.addWidget(btn)
        col.addStretch()
        return host

    def count_text(self,key):
        value=self.record.get(key)
        return str(value) if isinstance(value,int) else "UNAVAILABLE"

    def open_palette(self):
        palette=CommandPalette(self.pages,self)
        palette.chosen.connect(self.navigate)
        palette.exec()

    def toggle_immersive(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def navigate(self,name):
        self.stack.setCurrentIndex(self.pages.index(name))
        for label,button in self.nav.items():
            button.setChecked(label==name)

    def tick(self):
        self.frame+=1
        self.samples=simulated_samples(self.frame,120)
        for chart in self.charts:
            chart.set_samples(self.samples)
        a,b=self.samples[-1]
        self.station_a.mass.setText(f"{a:.4f} g")
        self.station_b.mass.setText(f"{b:.4f} g")
        self.ana_a.value.setText(f"{a:.4f} g")
        self.ana_b.value.setText(f"{b:.4f} g")
        self.clock.setText(datetime.now(timezone.utc).strftime("%H:%M:%S UTC"))

    def toggle_motion(self,enabled):
        for gate in self.gates:
            gate.set_motion(enabled)

    def change_interval(self):
        self.timer.setInterval(int(self.interval.currentData()))

    def open_docs(self,path):
        QDesktopServices.openUrl(QUrl(DOC_BASE+path))

    def open_source(self):
        row=self.source_table.currentRow()
        if row<0 or row>=len(self.sources):
            QMessageBox.information(self,"PhaseGate Research","Select a source first.")
            return
        url=self.sources[row]["url"]
        if not url.startswith("https://"):
            QMessageBox.warning(self,"Invalid source URL","Only HTTPS references may be opened.")
            return
        QDesktopServices.openUrl(QUrl(url))

    def export(self):
        filename,fmt=QFileDialog.getSaveFileName(
            self,"Export SYNTHETIC diagnostics","SYNTHETIC_PhaseGate_Demo.json",
            "Synthetic JSON (*.json)")
        if not filename:
            return
        path=Path(filename)
        if not path.name.startswith("SYNTHETIC_"):
            path=path.with_name("SYNTHETIC_"+path.name)
        if path.suffix.lower()!=".json":
            path=path.with_suffix(".json")
        try:
            export_demo(path,self.frame)
        except (OSError,ValueError) as e:
            QMessageBox.warning(self,"Export failed",str(e))
            return
        QMessageBox.information(self,"Synthetic Export",
            "Saved demonstration data to:\n"+str(path)+
            "\n\nThis is not an actual experimental record.")

    def verify_integrity(self):
        data=inventory()
        missing=[name for name in ("sources","hypotheses","experiments") if data.get(name) is None]
        title="Registry files missing" if missing else "Research inventory readable"
        report="Missing: "+", ".join(missing) if missing else (
            f"Sources: {data['sources']}\nHypotheses: {data['hypotheses']}"
            f"\nActual run records: {data['experiments']}")
        QMessageBox.information(self,"PhaseGate Integrity",title+"\n\n"+report+
                                "\n\nA readable registry does NOT establish a physics result.")


    def closeEvent(self, event):
        if hasattr(self, "hardware_lab"):
            self.hardware_lab.shutdown()
        if hasattr(self,"evidence_lab"):
            self.evidence_lab.shutdown()
        if hasattr(self,"optical_lab"):
            self.optical_lab.shutdown()
        super().closeEvent(event)


def app_icon():
    pix=QPixmap(80,80)
    pix.fill(Qt.GlobalColor.transparent)
    p=QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    from PySide6.QtGui import QPen
    p.setPen(QPen(QColor(C["violet"]),8))
    p.drawEllipse(10,10,60,60)
    p.setPen(QPen(QColor(C["cyan"]),3))
    p.drawEllipse(19,19,42,42)
    p.setBrush(QColor(C["cyan"]))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(36,36,8,8)
    p.end()
    return QIcon(pix)
