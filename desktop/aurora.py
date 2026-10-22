"""DPN PhaseGate AURORA visual system.

All art is procedurally painted by native Qt on the user's PC. The glowing
orbital concept is a visual metaphor, not a rendering of a physical portal.
No background network calls, fonts, stock images or external assets required.
"""
from __future__ import annotations

import math
from PySide6.QtCore import Qt, QRectF, QPointF, QTimer, Signal
from PySide6.QtGui import (
    QColor, QPainter, QPen, QBrush, QFont, QRadialGradient,
    QLinearGradient, QConicalGradient, QPainterPath
)
from PySide6.QtWidgets import (
    QFrame, QWidget, QVBoxLayout, QHBoxLayout, QDialog, QLineEdit,
    QListWidget, QLabel
)


def qcolor(value, opacity=255):
    c=QColor(value)
    c.setAlpha(opacity)
    return c


class GateField(QWidget):
    """Animated native QPainter vector installation inspired by a field lab.

    Nothing depicted is evidence of a portal or live hardware. No real input.
    """
    def __init__(self,parent=None):
        super().__init__(parent)
        self.phase=0.
        self.motion=True
        self.setMinimumSize(320,270)
        self.timer=QTimer(self)
        self.timer.setInterval(32)
        self.timer.timeout.connect(self.next_frame)
        self.timer.start()

    def next_frame(self):
        self.phase=(self.phase+.0055)%(2*math.pi)
        self.update()

    def set_motion(self,on):
        self.motion=bool(on)
        if on:self.timer.start()
        else:self.timer.stop()
        self.update()

    def paintEvent(self,event):
        p=QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing,True)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform,True)
        w,h=self.width(),self.height()
        s=min(w/480,h/370)
        p.translate(w/2,h/2+7)
        p.scale(s,s)
        # sci-fi observation field, concentric translucent halos
        halo=QRadialGradient(0,0,220)
        halo.setColorAt(0,qcolor("#7D39C7",58))
        halo.setColorAt(.43,qcolor("#1963AD",30))
        halo.setColorAt(.72,qcolor("#9450F7",20))
        halo.setColorAt(1,qcolor("#161A33",0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(halo)
        p.drawEllipse(QPointF(0,0),230,205)
        # Implied engineering grid, lines are pure illustrative geometry
        p.setPen(QPen(qcolor("#6381B5",32),.65))
        for x in range(-235,260,36):
            p.drawLine(QPointF(x,-151),QPointF(x,151))
        for y in range(-150,155,35):
            p.drawLine(QPointF(-235,y),QPointF(235,y))
        # far/near elliptical rings (perspective tilt)
        p.save()
        p.rotate(-18)
        rings=[
            (180,138,1.2,"#6D50EC",62),
            (169,127,1.6,"#44CDEB",110),
            (151,108,3.0,"#895AFF",160),
            (131,93,1.3,"#59DDEA",92),
            (113,78,5.0,"#AC78FD",185),
            (94,65,1.1,"#91E9FF",100)
        ]
        for rx,ry,stroke,c,alpha in rings:
            p.setPen(QPen(qcolor(c,alpha),stroke))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QPointF(0,0),rx,ry)
        # glass core with true layered transparency
        core=QRadialGradient(0,0,130)
        core.setColorAt(0,qcolor("#071325",252))
        core.setColorAt(.34,qcolor("#112C50",238))
        core.setColorAt(.78,qcolor("#442A7C",155))
        core.setColorAt(1,qcolor("#120D30",0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(core)
        p.drawEllipse(QPointF(0,0),124,86)
        # native vector luminous luminous orbit arcs
        phase_deg=self.phase*180/math.pi
        for j in range(4):
            col=["#60E1F4","#C18BFF","#8B56F4","#4DCCE2"][j]
            theta=phase_deg*(1 if j%2==0 else -1)+j*62
            pen=QPen(qcolor(col,220),4.5 if j<2 else 2.1)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawArc(QRectF(-160+j*12,-117+j*9,(160-j*12)*2,(117-j*9)*2),
                      int(theta*16),int((29+j*7)*16))
        p.restore()
        # eye core diamond / optical marker
        p.setPen(QPen(qcolor("#A7EDFF",190),1.5))
        p.drawLine(QPointF(-28,0),QPointF(28,0))
        p.drawLine(QPointF(0,-28),QPointF(0,28))
        p.setBrush(qcolor("#5DDCED",200))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(0,0),5,5)
        # rotating particle system with structured depth
        for idx in range(78):
            t=idx*2.39996323+self.phase*(.6 if idx%2==0 else -.15)
            rad=110+((idx*71)%98)
            xx=math.cos(t)*rad
            yy=math.sin(t)*rad*.68
            alpha=40+(idx*29)%130
            rr=1.1+(idx%4)*.25
            p.setBrush(qcolor("#A8DDFE" if idx%3 else "#BA83FF",alpha))
            p.drawEllipse(QPointF(xx,yy),rr,rr)
        # sci-fi labels and anchors (physically meaningful labels: visualization only)
        p.setPen(QPen(qcolor("#62CFEA",130),1.2))
        p.drawLine(QPointF(-164,-84),QPointF(-216,-84))
        p.drawLine(QPointF(164,74),QPointF(221,74))
        p.setFont(QFont("Consolas",9,QFont.Weight.DemiBold))
        p.setPen(qcolor("#76DDEA",245))
        p.drawText(QRectF(-228,-111,115,20),Qt.AlignmentFlag.AlignLeft,"NODE  A  /  SIM")
        p.setPen(qcolor("#C39AFF",245))
        p.drawText(QRectF(134,82,102,20),Qt.AlignmentFlag.AlignLeft,"NODE  B  /  SIM")
        p.setPen(qcolor("#E7EFFF",235))
        p.setFont(QFont("Consolas",11,QFont.Weight.Bold))
        p.drawText(QRectF(-96,-14,192,30),Qt.AlignmentFlag.AlignCenter,
                   getattr(self,"scene_label","PG // 01"))
        p.setPen(qcolor("#8EA8D3",245))
        p.setFont(QFont("Consolas",8))
        p.drawText(QRectF(-120,19,240,19),Qt.AlignmentFlag.AlignCenter,
                   "CONCEPT RENDER / NO PORTAL")
        p.end()


class AuroraHero(QFrame):
    """Designed launch panel with bespoke native background and animated visual."""
    station_requested=Signal()
    evidence_requested=Signal()

    def __init__(self,parent=None):
        super().__init__(parent)
        self.setObjectName("auroraHero")
        self.setMinimumHeight(365)
        layout=QHBoxLayout(self)
        layout.setContentsMargins(34,20,14,16)
        layout.setSpacing(5)
        left=QVBoxLayout()
        left.setSpacing(0)
        kicker=QLabel("  R&D DIVISION     /     PHASEGATE SYSTEM     /     PG-01  ")
        kicker.setObjectName("heroKicker")
        left.addWidget(kicker,0,Qt.AlignmentFlag.AlignLeft)
        left.addSpacing(25)
        heading=QLabel("THE NEXT FRONTIER\nSTARTS WITH EVIDENCE.")
        heading.setObjectName("heroHeading")
        heading.setWordWrap(True)
        left.addWidget(heading)
        left.addSpacing(14)
        description=QLabel("An engineered platform for rigorous measurement, "
                          "independent observation and auditable discovery.")
        description.setObjectName("heroDescription")
        description.setWordWrap(True)
        description.setMaximumWidth(500)
        left.addWidget(description)
        left.addSpacing(21)
        actions=QHBoxLayout()
        actions.setSpacing(10)
        from desktop.window_helpers import button
        enter=button("OPEN HARDWARE LAB   →")
        enter.clicked.connect(lambda: self.station_requested.emit())
        research=button("EVIDENCE VAULT   ↗",True)
        research.clicked.connect(lambda: self.evidence_requested.emit())
        actions.addWidget(enter)
        actions.addWidget(research)
        actions.addStretch()
        left.addLayout(actions)
        left.addStretch()
        meta=QLabel("●  RESEARCH ACTIVE          ◌  NO PORTAL VERIFIED          /          v1.0")
        meta.setObjectName("heroMeta")
        left.addWidget(meta)
        layout.addLayout(left,7)
        self.field=GateField()
        layout.addWidget(self.field,6)

    def paintEvent(self,event):
        p=QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing,True)
        r=QRectF(1,1,self.width()-2,self.height()-2)
        path=QPainterPath()
        path.addRoundedRect(r,23,23)
        grad=QLinearGradient(0,0,self.width(),self.height())
        grad.setColorAt(0,qcolor("#182642"))
        grad.setColorAt(.50,qcolor("#141F39"))
        grad.setColorAt(1,qcolor("#271643"))
        p.fillPath(path,grad)
        p.save()
        p.setClipPath(path)
        p.setPen(QPen(qcolor("#6C7CC1",27),1))
        for i in range(-10,20):
            x=i*64
            p.drawLine(x,0,x+160,self.height())
        light=QRadialGradient(self.width()*.82,self.height()*.37,self.height()*.79)
        light.setColorAt(0,qcolor("#6F2BCE",75))
        light.setColorAt(.65,qcolor("#3758C6",24))
        light.setColorAt(1,qcolor("#3641AE",0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(light)
        p.drawEllipse(QPointF(self.width()*.82,self.height()*.37),
                      self.height()*.79,self.height()*.79)
        p.restore()
        p.setPen(QPen(qcolor("#7158B3",155),1.3))
        p.drawPath(path)
        # slim neon top rail introduces strong visual identity
        p.setPen(QPen(qcolor("#B180FD",200),2.6))
        p.drawLine(QPointF(38,2),QPointF(min(self.width()-38,332),2))
        p.end()


class PipelineRail(QFrame):
    """Horizontal mini status track with honest research gates."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("pipelineRail")
        self.setMinimumHeight(86)
        row=QHBoxLayout(self)
        row.setContentsMargins(18,12,18,12)
        row.setSpacing(12)
        items=[
            ("01","RESEARCH","LITERATURE INDEXED","#55E0EA"),
            ("02","INSTRUMENTS","USB LAB OPTIONAL","#B38AF7"),
            ("03","METROLOGY","BENCH / UNREVIEWED","#97A9D8"),
            ("04","VALIDATION","PHYSICAL TRANSFER: NONE","#FFC48C"),
        ]
        for i,(num,title,detail,c) in enumerate(items):
            cell=QWidget()
            v=QVBoxLayout(cell)
            v.setContentsMargins(4,1,4,1)
            v.setSpacing(2)
            h=QLabel(num+"   "+title)
            h.setStyleSheet("color:%s;font-size:11px;font-weight:800;letter-spacing:1px"%c)
            d=QLabel(detail)
            d.setStyleSheet("color:#A5B7D2;font-size:10px;")
            v.addWidget(h)
            v.addWidget(d)
            row.addWidget(cell,1)
            if i!=len(items)-1:
                separator=QFrame()
                separator.setFixedWidth(1)
                separator.setStyleSheet("background:#364263;")
                row.addWidget(separator)


class CommandPalette(QDialog):
    """Keyboard operated local search across pages; never executes code."""
    chosen=Signal(str)

    def __init__(self,items,parent=None):
        super().__init__(parent)
        self.setWindowTitle("PhaseGate / Navigate")
        self.setModal(True)
        self.setMinimumWidth(470)
        self.setObjectName("commandPalette")
        layout=QVBoxLayout(self)
        layout.setSpacing(10)
        layout.addWidget(QLabel("QUICK NAVIGATION     /     CTRL + K"))
        self.search=QLineEdit()
        self.search.setPlaceholderText("Type a destination or keyword…")
        self.search.setObjectName("paletteSearch")
        layout.addWidget(self.search)
        self.list=QListWidget()
        self.list.setObjectName("paletteList")
        layout.addWidget(self.list)
        self.items=list(items)
        self.search.textChanged.connect(self.populate)
        self.search.returnPressed.connect(self.select_current)
        self.list.itemActivated.connect(lambda _:self.select_current())
        self.populate("")
        self.search.setFocus()

    def populate(self,term):
        self.list.clear()
        for name in self.items:
            if term.lower().strip() in name.lower():
                self.list.addItem(name)
        if self.list.count():
            self.list.setCurrentRow(0)

    def select_current(self):
        item=self.list.currentItem()
        if item is not None:
            self.chosen.emit(item.text())
            self.accept()



class LabBanner(QFrame):
    """Compact diagrammatic operations banner shown on technical workstations."""
    def __init__(self,title,subtext,accent="#66DDEA",parent=None):
        super().__init__(parent)
        self.title=title
        self.subtext=subtext
        self.accent=accent
        self.setMinimumHeight(112)
        self.setMaximumHeight(126)
        self.setObjectName("labBanner")

    def paintEvent(self,event):
        p=QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w,h=self.width(),self.height()
        r=QRectF(1,1,w-2,h-2)
        path=QPainterPath()
        path.addRoundedRect(r,16,16)
        background=QLinearGradient(0,0,w,h)
        background.setColorAt(0,qcolor("#1A2A43"))
        background.setColorAt(1,qcolor("#232342"))
        p.fillPath(path,background)
        p.save()
        p.setClipPath(path)
        p.setPen(QPen(qcolor(self.accent,58),1))
        for x in range(0,w,38):
            p.drawLine(x,0,x+75,h)
        # double pulse waves on right: ornamental only, never real instrument data
        p.setPen(QPen(qcolor(self.accent,205),2))
        start=w-295
        for shift in (0,12):
            previous=None
            for x in range(0,276,5):
                y=52+shift+math.sin(x*.10)*11 + math.sin(x*.035)*5
                now=QPointF(start+x,y)
                if previous:
                    p.drawLine(previous,now)
                previous=now
        p.restore()
        p.setPen(QPen(qcolor("#647FA4",220),1))
        p.drawPath(path)
        p.setFont(QFont("Segoe UI",15,QFont.Weight.Bold))
        p.setPen(qcolor("#F1F6FF"))
        p.drawText(QRectF(22,20,max(260,w-315),32),
                   Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter,self.title)
        p.setFont(QFont("Segoe UI",10))
        p.setPen(qcolor("#A9BDD7"))
        p.drawText(QRectF(22,53,max(260,w-310),36),
                   Qt.TextFlag.TextWordWrap|Qt.AlignmentFlag.AlignTop,self.subtext)
        p.setFont(QFont("Consolas",9,QFont.Weight.DemiBold))
        p.setPen(qcolor(self.accent))
        p.drawText(QRectF(w-186,14,161,19),Qt.AlignmentFlag.AlignRight,"DPN / PG-01   v1.0")
        p.end()
