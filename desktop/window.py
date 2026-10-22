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
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap, QDesktopServices
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, QStackedWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QFileDialog, QMessageBox, QComboBox, QCheckBox, QSizePolicy
)
from PySide6.QtCore import qVersion
from desktop.model import VERSION, MODE, DISCLAIMER, DOC_BASE, inventory, literature, simulated_samples, export_demo
from desktop.widgets import C, Surface, Metric, OrbitalGate, Station, TrendChart, text_label, panel_layout


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
        self.resize(1470,920)
        self.setMinimumSize(1080,720)
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

    def apply_theme(self):
        self.setStyleSheet("""
        QMainWindow {background: #080E1A; color: #E8F2FF;}
        QWidget {font-family: 'Segoe UI'; color: #E8F2FF; font-size: 12px;}
        QFrame#leftRail {background: #0D1728; border-right: 1px solid #293952;}
        QFrame#topBar {background: #0C1527; border-bottom: 1px solid #2A3B55;}
        QFrame#hero {background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #182543,stop:.6 #17213D,stop:1 #2A1B44);
                     border: 1px solid #514C83; border-radius: 22px;}
        QFrame#surface, QFrame#metric, QFrame#station {
            background: #131E32; border:1px solid #293B57; border-radius: 17px;
        }
        QFrame#station {background: #142038; border: 1px solid #375471;}
        QPushButton {border-radius: 9px; padding: 9px 15px; font-weight: 700;
                     background: #8F67DD; border: 1px solid #AE85FC;}
        QPushButton:hover {background: #A576FB; border-color: #D7BAFF;}
        QPushButton[variant="secondary"] {background: #1D2A46; border: 1px solid #354967;}
        QPushButton[variant="secondary"]:hover {background:#2A3A5C;border-color:#57CFE5;}
        QPushButton[role="nav"] {background: transparent; border: 1px solid transparent;
                    text-align: left; font-weight: 600; color: #9BB0CC; padding: 12px 16px;}
        QPushButton[role="nav"]:checked {background: #252B50; border: 1px solid #63569B;
                    border-left: 3px solid #B38CFF; color:#F3F7FF;}
        QPushButton[role="nav"]:hover {background: #1E2A45; color: #F3F7FF;}
        QScrollArea, QScrollArea > QWidget > QWidget {background: transparent; border: 0;}
        QScrollBar:vertical {background:#101B2F;width:8px;}
        QScrollBar::handle:vertical {background:#4D5F81;border-radius:4px;min-height:35px;}
        QTableWidget {background:#111E33; alternate-background-color:#17253C;
                      border:1px solid #2E4463;gridline-color:#24334B;selection-background-color:#544478;}
        QHeaderView::section {background:#1C2C49; color:#BBCEE7;border:0;
                              border-right:1px solid #293B56;padding:9px;font-weight:bold;}
        QComboBox {background:#1C2B46; border:1px solid #3B5175; border-radius:7px;padding:8px;}
        QComboBox QAbstractItemView {background:#17233B;color:#ECF3FF;selection-background-color:#55467B;}
        QCheckBox {spacing:12px;font-size:13px;}
        QCheckBox::indicator {width:17px;height:17px;}
        """)

    def build_ui(self):
        host=QWidget()
        self.setCentralWidget(host)
        root=QHBoxLayout(host)
        root.setContentsMargins(0,0,0,0)
        root.setSpacing(0)
        self.rail=QFrame()
        self.rail.setObjectName("leftRail")
        self.rail.setFixedWidth(254)
        rail_col=QVBoxLayout(self.rail)
        rail_col.setContentsMargins(19,28,17,24)
        rail_col.setSpacing(7)
        logo=text_label("◉  DPN",28,"text",True)
        rail_col.addWidget(logo)
        rail_col.addWidget(text_label("DEVELOP  •  PIONEER  •  NAVIGATE",9,"cyan",True))
        rail_col.addSpacing(22)
        rail_col.addWidget(text_label("PHASEGATE / RESEARCH",10,"violet",True))
        rail_col.addWidget(heading_rule())
        rail_col.addSpacing(12)
        for name,ico in [
            ("Command Center","◈"),("Station Matrix","◎"),
            ("Signal Analytics","⌁"),("Research Vault","▣"),
            ("Experiment Ledger","▤"),("System Diagnostics","⚙"),
            ("Preferences","◇"),
        ]:
            btn=QPushButton(f"{ico}     {name}")
            btn.setProperty("role","nav")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, s=name:self.navigate(s))
            rail_col.addWidget(btn)
            self.nav[name]=btn
        rail_col.addStretch()
        rail_col.addWidget(heading_rule())
        rail_col.addWidget(text_label("●  DEMONSTRATION MODE",11,"cyan",True))
        rail_col.addWidget(text_label("Native desktop • no browser\nNo hardware connections\nNo physical matter transfer",10))
        root.addWidget(self.rail)
        body=QWidget()
        body_col=QVBoxLayout(body)
        body_col.setContentsMargins(0,0,0,0)
        body_col.setSpacing(0)
        top=QFrame()
        top.setObjectName("topBar")
        top.setFixedHeight(70)
        row=QHBoxLayout(top)
        row.setContentsMargins(29,0,29,0)
        row.addWidget(text_label("DPN   /   RESEARCH OPERATIONS   /   PHASEGATE",11,"muted",True))
        row.addStretch()
        row.addWidget(text_label("●  SYNTHETIC ONLY",11,"cyan",True))
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
        col.setContentsMargins(35,31,35,35)
        col.setSpacing(19)
        col.addWidget(text_label(kicker,10,"cyan",True))
        col.addWidget(text_label(title,31,"text",True))
        col.addWidget(text_label(subtitle,12,"muted"))
        return host,col

    def warning(self):
        card=Surface()
        row=QHBoxLayout(card)
        row.setContentsMargins(15,11,15,11)
        row.addWidget(text_label("⚠  SYNTHETIC DATA — NO PORTAL OR PHYSICAL EQUIPMENT CONNECTED. "
                                 "NOT AN EXPERIMENT.",11,"amber",True))
        return card

    def overview_page(self):
        host,col=self.page("RESEARCH OPERATIONS // HOME","PHASEGATE / COMMAND CENTER",
                           "A scientific investigation made tangible through precision instrumentation.")
        hero=QFrame()
        hero.setObjectName("hero")
        hero.setMinimumHeight(260)
        row=QHBoxLayout(hero)
        row.setContentsMargins(30,18,16,18)
        left=QVBoxLayout()
        left.setSpacing(11)
        left.addWidget(text_label("PROJECT PG–01   •   RESEARCH STAGE",11,"cyan",True))
        left.addWidget(text_label("ENGINEERING THE\nUNKNOWN.",31,"text",True))
        left.addWidget(text_label("Twin measurement stations. Recorded evidence. "
                                  "Scientific rigor. No unsupported claims.",13))
        buttons=QHBoxLayout()
        first=ui_button("OPEN STATION MATRIX  →")
        first.clicked.connect(lambda:self.navigate("Station Matrix"))
        second=ui_button("RESEARCH VAULT",True)
        second.clicked.connect(lambda:self.navigate("Research Vault"))
        buttons.addWidget(first)
        buttons.addWidget(second)
        left.addLayout(buttons)
        left.addStretch()
        row.addLayout(left,3)
        self.hero_gate=OrbitalGate("PG",compact=False)
        row.addWidget(self.hero_gate,2)
        self.gates.append(self.hero_gate)
        col.addWidget(hero)
        col.addWidget(self.warning())
        stat=QHBoxLayout()
        self.overview_metrics=[
            Metric("REGISTERED SOURCES",self.count_text("sources"),"Research sources","cyan"),
            Metric("HYPOTHESES",self.count_text("hypotheses"),"Research claims","violet"),
            Metric("ACTUAL RUNS",self.count_text("experiments"),"Verified log count","text"),
            Metric("OBJECT TRANSFER","NOT VERIFIED","No observed transport","amber"),
        ]
        for s in self.overview_metrics:
            stat.addWidget(s,1)
        col.addLayout(stat)
        col.addWidget(section_heading("LIVE SYSTEM INTELLIGENCE","Evidence and instrument readiness"))
        lower=QHBoxLayout()
        status=Surface()
        box=panel_layout(status,20,13)
        for title,desc,accent in [
            ("01 / SCIENTIFIC PROGRAM","Physics literature and hypotheses indexed.","cyan"),
            ("02 / PG-01 INSTRUMENTATION","Hardware design only. No sensor connected.","violet"),
            ("03 / QUANTUM INTERPRETATION","Quantum information is not macroscopic matter.","amber")]:
            box.addWidget(text_label(title,12,accent,True))
            box.addWidget(text_label(desc,11))
            box.addWidget(heading_rule())
        box.addStretch()
        lower.addWidget(status,3)
        trend=Surface()
        v=panel_layout(trend,17,6)
        v.addWidget(text_label("SYNTHETIC SENSOR TRACE  //  A / B",12,"cyan",True))
        self.overview_chart=TrendChart()
        self.charts.append(self.overview_chart)
        v.addWidget(self.overview_chart,1)
        lower.addWidget(trend,4)
        col.addLayout(lower)
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
            ("Connected instruments","0"),
            ("Recording / experiment writes","DISABLED"),
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
