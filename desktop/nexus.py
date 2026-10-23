"""PHASEGATE // NEXUS — original, fully native Qt command-deck design.

A replacement application experience, not a CSS recolor or browser embedding.
The cinematic machine illustration is exclusively DPN concept artwork: zero real
portal function; the research registry and instrument data remain authoritative.
"""
from __future__ import annotations

import math
from PySide6.QtCore import Qt, Signal, QPointF, QRectF, QTimer
from PySide6.QtGui import (
    QColor, QPainter, QPen, QBrush, QFont, QPolygonF,
    QLinearGradient, QRadialGradient, QPainterPath
)
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QHBoxLayout, QVBoxLayout,
    QSizePolicy
)


def ink(rgb,alpha=255):
    c=QColor(rgb)
    c.setAlpha(alpha)
    return c


def label(value,size=11,fg="#9CAEC9",bold=False):
    item=QLabel(value)
    item.setWordWrap(True)
    item.setStyleSheet(
        "background:transparent;color:%s;font-size:%dpx;font-weight:%d;"
        %(fg,size,800 if bold else 450))
    return item


def action(value,subtle=False):
    b=QPushButton(value)
    b.setObjectName("nexusSecondary" if subtle else "nexusPrimary")
    b.setMinimumHeight(39)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    return b


class NexusStage(QWidget):
    """Qt vector/gradient rendering of a hypothetical research structure.

    Every energy field, platform, arc and emission is artwork; none is a
    sensor display or simulated physical-transfer computation.
    """
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setObjectName("nexusStage")
        self.setMinimumSize(380,345)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.phase=0.0
        self.timer=QTimer(self)
        self.timer.setInterval(35)
        self.timer.timeout.connect(self.advance)
        self.timer.start()

    def advance(self):
        self.phase=(self.phase+0.009)%(2*math.pi)
        self.update()

    def set_motion(self,enabled):
        if enabled:
            self.timer.start()
        else:
            self.timer.stop()
        self.update()

    def draw_label(self,p,value,x,y,size=11,color="#C6D8F1",bold=False):
        p.setFont(QFont("Consolas",size,QFont.Weight.Bold if bold else QFont.Weight.Normal))
        p.setPen(ink(color))
        p.drawText(QPointF(x,y),value)

    def paintEvent(self,event):
        p=QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing,True)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform,True)
        w,h=self.width(),self.height()
        sx,sy=w/760.0,h/520.0
        p.scale(sx,sy)
        bg=QLinearGradient(0,0,760,520)
        bg.setColorAt(0,ink("#071521"))
        bg.setColorAt(.47,ink("#101A38"))
        bg.setColorAt(1,ink("#170E2C"))
        rect=QRectF(1,1,758,518)
        path=QPainterPath()
        path.addRoundedRect(rect,18,18)
        p.fillPath(path,bg)
        p.save()
        p.setClipPath(path)
        # Layer 1: a converging hangar grid establishes 3D depth and engineering scale.
        van=QPointF(381,264)
        p.setPen(QPen(ink("#2D4A72",64),.9))
        for i in range(-5,15):
            p.drawLine(van,QPointF(i*95-220,520))
        for y in [305,325,351,388,440,497]:
            p.drawLine(QPointF(0,y),QPointF(760,y))
        for y in [38,75,112,149,186,223]:
            p.drawLine(QPointF(0,y),QPointF(760,y))
        # Layer 2: soft radial scatter around a conceptual toroidal structure.
        halo=QRadialGradient(382,260,276)
        halo.setColorAt(0,ink("#4425A9",120))
        halo.setColorAt(.33,ink("#323FA9",69))
        halo.setColorAt(.72,ink("#193965",35))
        halo.setColorAt(1,ink("#193965",0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(halo)
        p.drawEllipse(QPointF(382,260),276,250)
        # rear gantry structural guides
        p.setPen(QPen(ink("#5A799C",96),4.0))
        p.drawLine(QPointF(220,390),QPointF(262,160))
        p.drawLine(QPointF(533,399),QPointF(498,147))
        p.setPen(QPen(ink("#27395B",186),13))
        p.drawLine(QPointF(196,400),QPointF(560,400))
        # 3D isometric base: multiple overlapping translucent hex platforms.
        polygons=[
            ([QPointF(235,376),QPointF(381,319),QPointF(532,376),QPointF(535,414),QPointF(384,467),QPointF(236,413)],"#162748","#6E7CBB"),
            ([QPointF(260,364),QPointF(380,316),QPointF(510,366),QPointF(382,419)],"#24385B","#638CB9"),
            ([QPointF(301,365),QPointF(381,333),QPointF(461,366),QPointF(381,397)],"#0C253A","#4ED6EC"),
        ]
        for poly,fill,stroke in polygons:
            p.setBrush(ink(fill,231))
            p.setPen(QPen(ink(stroke,190),2.4))
            p.drawPolygon(QPolygonF(poly))
        p.setPen(QPen(ink("#3CE2EB",205),2))
        p.drawLine(QPointF(260,366),QPointF(382,416))
        p.drawLine(QPointF(382,416),QPointF(508,366))
        # conceptual field core and elliptical vertical machine rings
        radial=QRadialGradient(381,240,158)
        radial.setColorAt(0,ink("#0A1831",251))
        radial.setColorAt(.37,ink("#223270",235))
        radial.setColorAt(.72,ink("#6635A8",136))
        radial.setColorAt(1,ink("#8B42B9",0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(radial)
        p.drawEllipse(QPointF(381,238),153,159)
        # dramatic structural struts to distinguish artwork from small concentric circles
        p.setPen(QPen(ink("#142B50",246),18,Qt.PenStyle.SolidLine,Qt.PenCapStyle.RoundCap))
        p.drawArc(QRectF(223,74,316,330),10*16,160*16)
        p.drawArc(QRectF(222,74,316,330),190*16,160*16)
        # fluorescent side-lit coil shells
        for j,(pad,penwidth,base,alpha) in enumerate([
            (0,9,"#4A5AC8",145),(13,4.5,"#A876FF",220),
            (28,3,"#53DCFE",194),(45,1.5,"#A98DFF",135)]):
            r=QRectF(222+pad,76+pad*.72,319-2*pad,328-1.44*pad)
            p.setPen(QPen(ink(base,alpha),penwidth))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(r)
        # Animated luminous arc segments; geometric decorative, no pseudo telemetry.
        t=self.phase*180/math.pi
        for j,(offset,color,wide,theta) in enumerate([
            (10,"#72E6FA",7,32),(26,"#C18BFF",4,48),
            (43,"#57C9F1",3,30),(5,"#A76FFF",3,65)]):
            r=QRectF(222+offset,76+offset*.72,319-2*offset,328-1.44*offset)
            p.setPen(QPen(ink(color,250),wide,cap=Qt.PenCapStyle.RoundCap))
            p.drawArc(r,int((t*(1 if j%2==0 else -.8)+j*85)*16),
                      int(theta*16))
        # vertical voltage-free decorative ribs around the ring
        p.setPen(QPen(ink("#DBB2FF",170),2))
        for j in range(32):
            angle=j*2*math.pi/32
            x=381+157*math.cos(angle)
            y=240+164*math.sin(angle)
            xx=381+177*math.cos(angle)
            yy=240+184*math.sin(angle)
            p.drawLine(QPointF(x,y),QPointF(xx,yy))
        # high-res core etched facets and subtle turning scan lines
        p.setPen(QPen(ink("#5BBEED",76),1.1))
        for j in range(9):
            delta=j*27+self.phase*9
            p.drawLine(QPointF(322,159+delta/6),QPointF(440,174+delta/8))
        p.setPen(QPen(ink("#A6E9FF",135),1.2))
        p.drawLine(QPointF(351,240),QPointF(411,240))
        p.drawLine(QPointF(381,210),QPointF(381,270))
        # 80 independently placed particle points
        p.setPen(Qt.PenStyle.NoPen)
        for i in range(80):
            angle=i*2.39996+self.phase*(.16 if i%3 else -.08)
            distance=175+(i*47)%155
            x=381+math.cos(angle)*distance
            y=243+math.sin(angle)*distance*.67
            p.setBrush(ink("#65E6F9" if i%3 else "#D29CFC",50+(i*31)%130))
            radius=.8+(i%3)*.32
            p.drawEllipse(QPointF(x,y),radius,radius)
        # mechanical overlaid HUD annotation and leader-line accents
        p.setPen(QPen(ink("#4FCDED",148),1.1))
        p.drawLine(QPointF(127,187),QPointF(225,187))
        p.drawLine(QPointF(225,187),QPointF(249,210))
        p.drawLine(QPointF(505,315),QPointF(559,333))
        p.drawLine(QPointF(559,333),QPointF(684,333))
        p.restore()
        p.setPen(QPen(ink("#376080",171),1.3))
        p.drawPath(path)
        # Independent text overlay, no source data passed to artwork.
        self.draw_label(p,"NEXUS / CONCEPT FIELD",25,35,11,"#6EE3F4",True)
        self.draw_label(p,"PROCEDURAL VISUALIZATION   •   NO HARDWARE DRIVE",25,55,8,"#87A6C9")
        self.draw_label(p,"FIELD A",26,181,9,"#86DBF3",True)
        self.draw_label(p,"FIELD B",569,329,9,"#BE95FF",True)
        p.setPen(ink("#D9E8F9"))
        p.setFont(QFont("Consolas",17,QFont.Weight.Bold))
        p.drawText(QRectF(296,223,169,35),Qt.AlignmentFlag.AlignCenter,"PG / 01")
        self.draw_label(p,"01 / SYSTEM CONCEPT",24,481,9,"#D8B8FF",True)
        self.draw_label(p,"REAL MATTER TRANSFER  /  NOT VERIFIED",24,504,9,"#FFC38A")
        self.draw_label(p,"3D VECTOR / QT ENGINE",541,480,9,"#6BC7EB")
        p.end()


class InstrumentReadout(QFrame):
    def __init__(self,kicker,main,sub,color="#70E5FA",parent=None):
        super().__init__(parent)
        self.setObjectName("instrumentReadout")
        self.setMinimumHeight(94)
        col=QVBoxLayout(self)
        col.setContentsMargins(14,11,14,10)
        col.setSpacing(3)
        k=label(kicker,10,color,True)
        col.addWidget(k)
        self.value=label(main,22,"#F2F8FF",True)
        self.value.setWordWrap(False)
        col.addWidget(self.value)
        col.addWidget(label(sub,10,"#97A9C4"))


class SectionLine(QWidget):
    def __init__(self,title,detail):
        super().__init__()
        row=QHBoxLayout(self)
        row.setContentsMargins(2,2,2,2)
        row.setSpacing(9)
        bar=QFrame()
        bar.setFixedSize(3,27)
        bar.setStyleSheet("background:#AD7CFF;border-radius:1px;")
        row.addWidget(bar)
        stack=QVBoxLayout()
        stack.setSpacing(1)
        stack.addWidget(label(title,11,"#EDF4FF",True))
        stack.addWidget(label(detail,9,"#9EADC6"))
        row.addLayout(stack,1)


class NexusDeck(QWidget):
    """Full native mission cockpit, fresh visual hierarchy and real navigation."""
    route=Signal(str)

    def __init__(self,records,parent=None):
        super().__init__(parent)
        self.setObjectName("nexusDeck")
        self.records=records
        root=QVBoxLayout(self)
        root.setContentsMargins(22,18,22,19)
        root.setSpacing(12)
        # Hero typography and clear evidence status in top bar
        top=QHBoxLayout()
        head=QVBoxLayout()
        head.setSpacing(1)
        head.addWidget(label("DPN / RESEARCH SYSTEMS        •        PG-01",11,"#71DBF2",True))
        head.addWidget(label("PHASEGATE  /  NEXUS",34,"#F7F8FF",True))
        head.addWidget(label("Independent instrumentation  /  Controlled observation  /  Verifiable research",11,"#AABAD3"))
        top.addLayout(head,1)
        badge=QFrame()
        badge.setObjectName("nexusSafetyChip")
        chip=QVBoxLayout(badge)
        chip.setContentsMargins(17,10,17,10)
        chip.setSpacing(3)
        chip.addWidget(label("RESEARCH ONLY   ●",10,"#FFCA89",True))
        chip.addWidget(label("NO PORTAL VERIFIED",12,"#F3E6CF",True))
        top.addWidget(badge,0,Qt.AlignmentFlag.AlignVCenter)
        root.addLayout(top)
        # Large cinematic graphic and an actual operator-facing station deck
        mid=QHBoxLayout()
        mid.setSpacing(13)
        self.stage=NexusStage()
        mid.addWidget(self.stage,7)
        controls=QFrame()
        controls.setObjectName("nexusOps")
        cv=QVBoxLayout(controls)
        cv.setContentsMargins(17,17,17,15)
        cv.setSpacing(10)
        cv.addWidget(label("OPERATIONS  /  PG-01",11,"#D5B4FF",True))
        cv.addWidget(label("STATION LINK MAP",20,"#F6F8FF",True))
        cv.addWidget(label("Physical instruments are never connected by this display.",10))
        for station,title,color in (
            ("A","SOURCE / BENCH","#6AE8EF"),
            ("B","DESTINATION / BENCH","#BC8BFF")):
            cell=QFrame()
            cell.setObjectName("nexusEndpoint")
            cr=QHBoxLayout(cell)
            cr.setContentsMargins(12,11,12,11)
            cr.setSpacing(9)
            letter=QLabel(station)
            letter.setAlignment(Qt.AlignmentFlag.AlignCenter)
            letter.setMinimumSize(40,43)
            letter.setMaximumWidth(44)
            letter.setStyleSheet(
                f"font-size:24px;font-weight:900;color:{color};"
                "background:#142840;border:1px solid #476381;border-radius:9px;")
            cr.addWidget(letter)
            contents=QVBoxLayout()
            contents.setSpacing(2)
            contents.addWidget(label(title,11,"#EEF3FF",True))
            contents.addWidget(label("NO AUTO-CONNECTION",9,"#C4A6CB"))
            cr.addLayout(contents,1)
            cv.addWidget(cell)
        cv.addWidget(SectionLine("REAL USB INSTRUMENTS","Choose & connect manually"))
        btn=action("OPEN HARDWARE LAB     ↗")
        btn.clicked.connect(lambda:self.route.emit("Hardware Lab"))
        cv.addWidget(btn)
        cv.addWidget(SectionLine("OPTICAL OBSERVATION","Explicit camera consent required"))
        btn2=action("OPEN OPTICAL LAB     ↗",True)
        btn2.clicked.connect(lambda:self.route.emit("Optical Evidence"))
        cv.addWidget(btn2)
        cv.addStretch()
        cv.addWidget(label("DATA CLASS   /   VISUALIZATION ONLY",9,"#FFCE9E",True))
        mid.addWidget(controls,4)
        root.addLayout(mid,1)
        # Bottom row is not decorative: sourced counts from actual research data
        metrics=QHBoxLayout()
        metrics.setSpacing(12)
        def n(key):
            v=self.records.get(key)
            return str(v) if isinstance(v,int) else "N/A"
        for kicker,value,sub,c in [
            ("PRIMARY LITERATURE",n("sources"),"Indexed references","#66DBEE"),
            ("RESEARCH HYPOTHESES",n("hypotheses"),"Registered questions","#C59BFF"),
            ("RECORDED REAL RUNS",n("experiments"),"Verified registry count","#F1F5FC"),
            ("OBJECT TRANSFER","UNVERIFIED","No physical transfer result","#FFC68B"),
        ]:
            metrics.addWidget(InstrumentReadout(kicker,value,sub,c),1)
        root.addLayout(metrics)
        actions=QHBoxLayout()
        actions.addWidget(label("●  VISUAL FIELD: SYNTHETIC / NOT AN INSTRUMENT READING",
                                10,"#75D8EA",True))
        actions.addStretch()
        more=action("REVIEW EVIDENCE  →",True)
        more.clicked.connect(lambda:self.route.emit("Reference Events"))
        actions.addWidget(more)
        root.addLayout(actions)
