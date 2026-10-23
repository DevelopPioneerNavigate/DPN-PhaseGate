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
from desktop.reference_page import ReferenceEventLab
from desktop.aurora import AuroraHero, PipelineRail, CommandPalette
from desktop.nexus import NexusDeck
from desktop.build_page import BuildLab
from desktop.assembly_page import AssemblyStudio


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
        dock_shortcut=QShortcut(QKeySequence("Ctrl+B"),self)
        dock_shortcut.activated.connect(self.toggle_rail)
        self._keyboard_shortcuts.append(dock_shortcut)
        fullscreen=QShortcut(QKeySequence("F11"),self)
        fullscreen.activated.connect(self.toggle_immersive)
        self._keyboard_shortcuts.append(fullscreen)
        for i,name in enumerate(self.pages[:9],1):
            key=QShortcut(QKeySequence("Ctrl+"+str(i)),self)
            key.activated.connect(lambda label=name:self.navigate(label))
            self._keyboard_shortcuts.append(key)
        if len(self.pages)>=10:
            key=QShortcut(QKeySequence("Ctrl+0"),self)
            key.activated.connect(lambda:self.navigate(self.pages[9]))
            self._keyboard_shortcuts.append(key)
 
    def apply_theme(self):
        self.setStyleSheet("""
        QMainWindow {background:#070D19;}
        QWidget {font-family:'Segoe UI';color:#E6EFFC;font-size:12px;}
        QFrame#leftRail {background:#0C1526;border-right:1px solid #263650;}
        QFrame#topBar {background:#0B1424;border-bottom:1px solid #263952;}
        QFrame#systemFooter {background:#0B1524;border-top:1px solid #23344D;}
        QLabel#brandMark {font-family:'Segoe UI';font-size:31px;font-weight:900;color:#E6FAFF;}
        QFrame#nexusOps {background:qlineargradient(x1:0,y1:0,x2:0,y2:1,
           stop:0 #15213A,stop:1 #11172B);border:1px solid #36506F;border-radius:17px;}
        QFrame#nexusEndpoint {background:#0C1B2E;border:1px solid #304C67;border-radius:11px;}
        QFrame#nexusSafetyChip {background:#35271E;border:1px solid #916746;border-radius:10px;}
        QFrame#instrumentReadout {background:#121F33;border:1px solid #364863;border-radius:11px;}
        QFrame#surface,QFrame#metric,QFrame#station {
           background:#122037;border:1px solid #354966;border-radius:12px;}
        QFrame#pipelineRail {background:#101D33;border:1px solid #344963;border-radius:12px;}
        QFrame#missionDock {background:#131F35;border:1px solid #344963;border-radius:12px;}
        QPushButton {border-radius:8px;padding:9px 13px;background:#6541B7;
           border:1px solid #8D6ADD;color:#F5F2FF;font-size:11px;font-weight:800;}
        QPushButton:hover {background:#815BE0;border-color:#C29DFF;}
        QPushButton:pressed {background:#4F3199;}
        QPushButton:disabled {background:#263144;color:#7B89A1;border-color:#37455A;}
        QPushButton[variant="secondary"],QPushButton#nexusSecondary {
           background:#172840;border:1px solid #486385;color:#CDEAF8;}
        QPushButton[variant="secondary"]:hover,QPushButton#nexusSecondary:hover {
           background:#254064;border-color:#70DDEC;}
        QPushButton#nexusPrimary {background:#9866E8;border:1px solid #B18BFA;
           font-weight:800;color:#0A0D1A;}
        QPushButton#nexusPrimary:hover {background:#C19DFF;}
        QPushButton[role="nav"] {background:transparent;border:1px solid transparent;
           border-radius:8px;text-align:left;color:#B1C3DF;font-size:10px;
           font-weight:750;padding:9px 11px;}
        QPushButton[role="nav"]:hover {background:#182943;border-color:#2C4662;}
        QPushButton[role="nav"]:checked {background:#242547;border:1px solid #655293;
           border-left:3px solid #A87FFF;color:#FFFFFF;}
        QScrollArea,QScrollArea > QWidget > QWidget {background:transparent;border:0;}
        QScrollBar:vertical {width:7px;background:#0D1827;}
        QScrollBar::handle:vertical {background:#425D84;border-radius:3px;min-height:25px;}
        QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical {height:0px;}
        QTableWidget {background:#0E1A2D;alternate-background-color:#152540;
           border:1px solid #2D4664;gridline-color:#2D415D;selection-background-color:#413772;}
        QHeaderView::section {background:#1B304E;color:#B6D9F2;border:0;
           padding:9px;font-weight:750;}
        QComboBox,QLineEdit,QTextEdit,QSpinBox,QDoubleSpinBox {
           background:#12233A;color:#EAF6FF;border:1px solid #47617F;
           border-radius:7px;padding:8px;selection-background-color:#8059B8;}
        QComboBox:hover,QLineEdit:hover,QTextEdit:hover {border-color:#7ABCE9;}
        QComboBox QAbstractItemView {background:#132440;selection-background-color:#59438A;}
        QListWidget {background:#0B1C31;color:#DDEAFF;border:1px solid #365574;
          border-radius:8px;outline:none;padding:5px;font-size:11px;}
        QListWidget::item {color:#D7E5F7;background:transparent;padding:6px;
          border-bottom:1px solid #243B54;}
        QListWidget::item:hover {background:#1E3651;color:#FFFFFF;}
        QListWidget::item:selected {background:#3F356A;color:#FFFFFF;
          border-left:3px solid #B18AFF;}
        QCheckBox {spacing:9px;}
        QTabWidget#engineeringTabs::pane {border:1px solid #365775;border-radius:9px;
          background:#0B192D;top:-1px;}
        QTabWidget#engineeringTabs QTabBar::tab {background:#17283E;
          color:#A7C8E2;padding:11px 17px;border:1px solid #2D4967;
          border-bottom:0;min-width:100px;}
        QTabWidget#engineeringTabs QTabBar::tab:hover {background:#294061;color:#ECF7FF;}
        QTabWidget#engineeringTabs QTabBar::tab:selected {background:#243B5A;
          border-top:2px solid #B48BFE;color:#FFFFFF;}
        QTabWidget#engineeringTabs > QWidget {background:#0B192D;}
        QTableWidget {background:#101D31;color:#DCEBFB;border:1px solid #3A5879;}
        QTableWidget::item {background:transparent;color:#D6E5F8;padding:5px;}
        QTableWidget::item:selected {background:#493D79;color:#FFFFFF;}
        QDialog#commandPalette {background:#0F1C30;border:1px solid #8D73CB;}
        QLineEdit#paletteSearch {font-size:16px;padding:14px;}
        QListWidget#paletteList {background:#12223B;font-size:13px;padding:8px;}
        QLabel#heroKicker {color:#8AE5EE;background:#203A55;padding:8px;}
        QLabel#heroHeading {font-size:31px;font-weight:900;color:#F2F7FF;background:transparent;}
        QLabel#heroDescription,QLabel#heroMeta {color:#ADC5E5;background:transparent;}
        """)
        
    def build_ui(self):
        host=QWidget()
        self.setCentralWidget(host)
        root=QHBoxLayout(host)
        root.setContentsMargins(0,0,0,0)
        root.setSpacing(0)
        # New slim mission dock, not the old website-like sidebar.
        self.rail=QFrame()
        self.rail.setObjectName("leftRail")
        self.rail.setFixedWidth(181)
        rail=QVBoxLayout(self.rail)
        rail.setContentsMargins(11,16,11,13)
        rail.setSpacing(5)
        mark=QLabel("DPN  /")
        mark.setObjectName("brandMark")
        rail.addWidget(mark)
        rail.addWidget(text_label("P H A S E G A T E",11,"cyan",True))
        rail.addWidget(text_label("NEXUS  //  RESEARCH OS",9,"violet",True))
        rail.addSpacing(17)
        rail.addWidget(text_label("WORKSPACES",10,"muted",True))
        rail.addWidget(heading_rule())
        nav_widget=QWidget()
        nav=QVBoxLayout(nav_widget)
        nav.setContentsMargins(0,0,2,0)
        nav.setSpacing(2)
        screens=[
            ("Command Center","01","COMMAND\nCENTER"),
            ("Station Matrix","02","STATION\nMATRIX"),
            ("Gate Engineering","03","GATE\nENGINEERING"),
            ("Assembly Studio","04","ASSEMBLY\nSTUDIO"),
            ("Hardware Lab","05","HARDWARE\nLAB"),
            ("Optical Evidence","06","OPTICAL\nEVIDENCE"),
            ("Reference Events","07","REFERENCE\nEVENTS"),
            ("Calibration & Evidence","08","CALIBRATION\n& EVIDENCE"),
            ("Signal Analytics","09","SIGNAL\nANALYTICS"),
            ("Research Vault","10","RESEARCH\nVAULT"),
            ("Experiment Ledger","11","EXPERIMENT\nLEDGER"),
            ("System Diagnostics","12","SYSTEM\nDIAGNOSTICS"),
            ("Preferences","13","PREFERENCES"),
        ]
        for name,n,title in screens:
            btn=QPushButton(n+"  "+title.replace("\n"," "))
            btn.setProperty("role","nav")
            btn.setCheckable(True)
            btn.setMinimumHeight(39)
            btn.setToolTip(name+" • Ctrl+K to search")
            btn.setAccessibleName("Open "+name)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False,s=name:self.navigate(s))
            nav.addWidget(btn)
            self.nav[name]=btn
        nav.addStretch()
        rail_scroll=QScrollArea()
        rail_scroll.setWidgetResizable(True)
        rail_scroll.setFrameShape(QFrame.Shape.NoFrame)
        rail_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        rail_scroll.setWidget(nav_widget)
        rail.addWidget(rail_scroll,1)
        rail.addWidget(heading_rule())
        rail.addWidget(text_label("●  BENCH / RESEARCH",10,"amber",True))
        rail.addWidget(text_label("No verified matter transfer",9,"muted"))
        root.addWidget(self.rail)
        main=QWidget()
        main_col=QVBoxLayout(main)
        main_col.setContentsMargins(0,0,0,0)
        main_col.setSpacing(0)
        bar=QFrame()
        bar.setObjectName("topBar")
        bar.setFixedHeight(61)
        upper=QHBoxLayout(bar)
        upper.setContentsMargins(23,0,21,0)
        upper.setSpacing(13)
        dock=ui_button("☰",True)
        dock.setFixedSize(36,34)
        dock.setToolTip("Toggle mission navigation • Ctrl+B")
        dock.clicked.connect(self.toggle_rail)
        upper.addWidget(dock)
        self.area_label=text_label("01   /   COMMAND CENTER",11,"text",True)
        upper.addWidget(self.area_label)
        upper.addStretch()
        search=ui_button("⌕   QUICK NAVIGATE    Ctrl+K",True)
        search.clicked.connect(self.open_palette)
        upper.addWidget(search)
        upper.addWidget(text_label("●  RESEARCH MODE",10,"cyan",True))
        self.clock=text_label("",10,"muted",True)
        upper.addWidget(self.clock)
        main_col.addWidget(bar)
        self.stack=QStackedWidget()
        main_col.addWidget(self.stack,1)
        footer=QFrame()
        footer.setObjectName("systemFooter")
        footer.setFixedHeight(32)
        foot=QHBoxLayout(footer)
        foot.setContentsMargins(23,0,23,0)
        foot.addWidget(text_label("DPN  //  DEVELOP • PIONEER • NAVIGATE",9,"muted",True))
        foot.addStretch()
        foot.addWidget(text_label("ILLUSTRATIVE FIELD / NO PORTAL VERIFIED",9,"amber",True))
        main_col.addWidget(footer)
        root.addWidget(main,1)
        pages=[
            ("Command Center",self.overview_page()),
            ("Station Matrix",self.stations_page()),
            ("Gate Engineering",self.build_page()),
            ("Assembly Studio",self.assembly_page()),
            ("Hardware Lab",self.hardware_page()),
            ("Optical Evidence",self.optical_page()),
            ("Reference Events",self.reference_page()),
            ("Calibration & Evidence",self.evidence_page()),
            ("Signal Analytics",self.analytics_page()),
            ("Research Vault",self.research_page()),
            ("Experiment Ledger",self.experiments_page()),
            ("System Diagnostics",self.system_page()),
            ("Preferences",self.preferences_page()),
        ]
        for name,page in pages:
            self.stack.addWidget(self.scrolling_page(page))
            self.pages.append(name)
        self.navigate("Command Center")

    def toggle_rail(self):
        self.rail.setVisible(not self.rail.isVisible())

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
        deck=NexusDeck(self.record)
        deck.route.connect(self.navigate)
        self.nexus_deck=deck
        self.gates.append(deck.stage)
        return deck

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

    def build_page(self):
        self.build_lab=BuildLab()
        self.build_lab.open_assembly.connect(lambda:self.navigate("Assembly Studio"))
        return self.build_lab

    def assembly_page(self):
        self.assembly_studio=AssemblyStudio()
        return self.assembly_studio

    def hardware_page(self):
        self.hardware_lab = HardwareLab()
        return self.hardware_lab

    def optical_page(self):
        self.optical_lab=OpticalLab()
        return self.optical_lab

    def reference_page(self):
        self.reference_lab=ReferenceEventLab()
        return self.reference_lab

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
        self.area_label.setText(f"{self.pages.index(name)+1:02d}   /   {name.upper()}")
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
        if hasattr(self,"reference_lab"):
            self.reference_lab.shutdown()
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
