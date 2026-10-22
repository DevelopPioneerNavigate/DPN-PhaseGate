"""DPN-native premium instrument visualizations, built with Qt painting (no web engine)."""
from __future__ import annotations
import math
from PySide6.QtCore import Qt, QRectF, QPointF, QTimer, QSize
from PySide6.QtGui import QColor, QPen, QBrush, QPainter, QFont, QConicalGradient, QRadialGradient, QLinearGradient
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QSizePolicy


C = {"bg": "#090E1B", "surface": "#111C30", "surface2": "#192741",
     "border": "#253853", "violet": "#B282FF", "cyan": "#4EDBEE",
     "text": "#EAF4FF", "muted": "#8BA4C0", "amber": "#FFBE84",
     "green": "#56DBB3"}


def color(hexval, alpha=None):
    x = QColor(hexval)
    if alpha is not None:
        x.setAlpha(alpha)
    return x


def text_label(content, size=12, hexval="muted", bold=False):
    l = QLabel(content)
    l.setWordWrap(True)
    l.setStyleSheet("color: %s; font-size: %dpx; font-weight: %s; background: transparent;"
                    % (C.get(hexval, hexval), size, "750" if bold else "400"))
    return l


def panel_layout(frame, margin=20, spacing=12):
    col = QVBoxLayout(frame)
    col.setContentsMargins(margin, margin, margin, margin)
    col.setSpacing(spacing)
    return col


class Surface(QFrame):
    def __init__(self, name="surface", parent=None):
        super().__init__(parent)
        self.setObjectName(name)
        self.setStyleSheet("#%s {background: %s; border: 1px solid %s; border-radius: 17px;}"
                           % (name, C["surface"], C["border"]))


class Metric(Surface):
    def __init__(self, eyebrow, value, caption, accent="cyan"):
        super().__init__("metric")
        self.setMinimumHeight(129)
        col = panel_layout(self, 17, 6)
        col.addWidget(text_label(eyebrow.upper(), 10, "muted", True))
        self.value = text_label(value, 27, accent, True)
        self.value.setWordWrap(False)
        col.addWidget(self.value)
        col.addWidget(text_label(caption, 10))
        col.addStretch()


class OrbitalGate(QWidget):
    """Original painted portal-shaped measurement emblem, not a hardware depiction."""
    def __init__(self, station="A", compact=False, parent=None):
        super().__init__(parent)
        self.station = station
        self.compact = compact
        self.motion = True
        self.angle = 0
        self.setMinimumHeight(155 if compact else 240)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.timer = QTimer(self)
        self.timer.setInterval(33)
        self.timer.timeout.connect(self.advance)
        self.timer.start()

    def set_motion(self, value: bool):
        self.motion = bool(value)
        if self.motion:
            self.timer.start()
        else:
            self.timer.stop()
        self.update()

    def advance(self):
        self.angle = (self.angle + .47) % 360
        self.update()

    def sizeHint(self):
        return QSize(340, 260)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w,h = self.width(),self.height()
        radius = min(w * .33, h * .40)
        cx,cy = w/2, h/2
        base = C["cyan"] if self.station == "A" else C["violet"]
        glow = color(base, 38)
        radial = QRadialGradient(cx, cy, radius*1.30)
        radial.setColorAt(0,color("#183355" if self.station=="A" else "#2A1D4A",225))
        radial.setColorAt(.65,color(base,17))
        radial.setColorAt(1,color(base,0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(radial)
        p.drawEllipse(QPointF(cx,cy),radius*1.35,radius*1.35)
        for factor,thick,alpha in [(1.12,16,20),(1.045,11,34),(.98,3,185),(.84,1,83)]:
            pen=QPen(color(base,alpha),thick)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QPointF(cx,cy),radius*factor,radius*factor)
        p.save()
        p.translate(cx,cy)
        p.rotate(self.angle)
        pen=QPen(color(base,245),4.4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        for start,span in [(4,54),(95,36),(171,57),(280,31)]:
            rr = radius*.99
            p.drawArc(QRectF(-rr,-rr,rr*2,rr*2),int(start*16),int(span*16))
        p.rotate(-self.angle*1.72)
        p.setPen(QPen(color(base,135),1.3,Qt.PenStyle.DashLine))
        rr=radius*.76
        p.drawEllipse(QPointF(0,0),rr,rr)
        for a in range(8):
            theta=math.pi*a/4
            r=radius*.89
            x,y=math.cos(theta)*r,math.sin(theta)*r
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(color(base,180))
            p.drawEllipse(QPointF(x,y),2.8,2.8)
        p.restore()
        p.setPen(QPen(color("#A3D2FF",90),1))
        p.drawLine(QPointF(cx-radius*.52,cy),QPointF(cx+radius*.52,cy))
        p.drawLine(QPointF(cx,cy-radius*.52),QPointF(cx,cy+radius*.52))
        p.setPen(color(C["text"]))
        font=QFont("Segoe UI",18 if self.compact else 24,QFont.Weight.Bold)
        p.setFont(font)
        p.drawText(QRectF(cx-radius*.45,cy-22,radius*.90,44),Qt.AlignmentFlag.AlignCenter,self.station)
        p.setFont(QFont("Consolas",8,QFont.Weight.DemiBold))
        p.setPen(color(base))
        p.drawText(QRectF(cx-80,cy+radius*.56,160,18),Qt.AlignmentFlag.AlignCenter,"SYNTHETIC // 00")
        p.end()


class Station(Surface):
    def __init__(self, name, label):
        super().__init__("station")
        self.name = name
        self.setMinimumHeight(325)
        col=panel_layout(self,18,3)
        top=QHBoxLayout()
        top.addWidget(text_label("STATION  "+name,13,"text",True))
        top.addStretch()
        top.addWidget(text_label("●  SIMULATION",10,"cyan" if name=="A" else "violet",True))
        col.addLayout(top)
        self.gate=OrbitalGate(name)
        col.addWidget(self.gate,1)
        measure=QHBoxLayout()
        measure.addWidget(text_label(label,11,"muted"))
        measure.addStretch()
        self.mass=text_label("--.---- g",24,"cyan" if name=="A" else "violet",True)
        measure.addWidget(self.mass)
        col.addLayout(measure)
        col.addWidget(text_label("NO DEVICE LINK  •  NOT A MEASUREMENT",10,"muted"))


class TrendChart(QWidget):
    """Native, independent normalized panels so A/B amplitudes are not miscompared."""
    def __init__(self):
        super().__init__()
        self.samples=[]
        self.setMinimumHeight(260)

    def set_samples(self, samples):
        self.samples=list(samples)
        self.update()

    def paintEvent(self, event):
        p=QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w,h=self.width(),self.height()
        p.fillRect(self.rect(),color("#0D172A"))
        plot=QRectF(56,32,max(60,w-80),max(80,h-65))
        p.setPen(QPen(color("#263C59"),1))
        for n in range(6):
            y=plot.top()+n*plot.height()/5
            p.drawLine(QPointF(plot.left(),y),QPointF(plot.right(),y))
        for n in range(11):
            x=plot.left()+n*plot.width()/10
            p.drawLine(QPointF(x,plot.top()),QPointF(x,plot.bottom()))
        p.setFont(QFont("Consolas",9))
        p.setPen(color(C["muted"]))
        p.drawText(QRectF(7,35,47,20),Qt.AlignmentFlag.AlignRight,"A / g")
        p.drawText(QRectF(7,plot.center().y()+35,47,20),Qt.AlignmentFlag.AlignRight,"B / g")
        if len(self.samples)>1:
            half=plot.height()*.5
            for ix,(channel,center,amp,col) in enumerate([
                (0,42.,.7,C["cyan"]), (1,0.,.08,C["violet"])]):
                p.setPen(QPen(color(col),2.4))
                last=None
                for i,points in enumerate(self.samples):
                    value=points[channel]
                    x=plot.left()+i*plot.width()/(len(self.samples)-1)
                    y=plot.top()+half*(ix+.52)-(value-center)/amp*half*.36
                    now=QPointF(x,y)
                    if last:
                        p.drawLine(last,now)
                    last=now
            p.setFont(QFont("Segoe UI",9,QFont.Weight.Bold))
            p.setPen(color(C["cyan"]))
            p.drawText(QRectF(plot.right()-145,plot.top()+7,145,18),Qt.AlignmentFlag.AlignRight,
                       "A 42 g nominal")
            p.setPen(color(C["violet"]))
            p.drawText(QRectF(plot.right()-145,plot.center().y()+9,145,18),
                       Qt.AlignmentFlag.AlignRight,"B 0 g nominal")
        p.setPen(color(C["muted"]))
        p.setFont(QFont("Consolas",9))
        p.drawText(QRectF(plot.left(),plot.bottom()+9,180,19),Qt.AlignmentFlag.AlignLeft,"120 synthetic frames")
        p.drawText(QRectF(plot.right()-195,plot.bottom()+9,195,19),
                   Qt.AlignmentFlag.AlignRight,"NO REAL SENSOR FEED")
        p.end()


class Eyebrow(text_label.__class__ if False else QLabel):
    pass
