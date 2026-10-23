"""DPN-native premium instrument visualizations, built with Qt painting (no web engine)."""
from __future__ import annotations
import math
from PySide6.QtCore import Qt, QRectF, QPointF, QTimer, QSize
from PySide6.QtGui import QColor, QPen, QBrush, QPainter, QFont, QConicalGradient, QRadialGradient, QLinearGradient
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QSizePolicy


C = {"bg": "#07101B", "surface": "#111E32", "surface2": "#1A2A43",
     "border": "#344B68", "violet": "#C399FF", "cyan": "#6FE2F0",
     "text": "#F4F7FF", "muted": "#AEC0D7", "amber": "#FFCA94",
     "green": "#65EBCB"}


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
        self.setStyleSheet("#%s {background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                           "stop:0 #172740, stop:1 #101B2F); "
                           "border:1px solid #3A5270;border-radius:13px;}" % name)


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


from desktop.nexus import NexusStage


class OrbitalGate(NexusStage):
    """Premium, native 3D-style concept scene reused on the station matrix."""
    def __init__(self, station="A", compact=False, parent=None):
        super().__init__(parent)
        self.station=station
        self.scene_label="STATION "+station+" / CONCEPT"
        self.compact=compact
        self.setMinimumSize(260,245 if not compact else 180)



class Station(Surface):
    def __init__(self, name, label):
        super().__init__("station")
        self.name = name
        self.setMinimumHeight(365)
        col=panel_layout(self,20,7)
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
        col.addWidget(text_label("SCENE MODE  /  SYNTHETIC CONCEPT VISUALIZATION",10,"amber",True))
        col.addWidget(text_label("No portal mechanism, live feed or physical transfer in this view.",10,"muted"))


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
        background=QLinearGradient(0,0,w,h)
        background.setColorAt(0,color("#121F36"))
        background.setColorAt(1,color("#1B2343"))
        p.fillRect(self.rect(),QBrush(background))
        plot=QRectF(56,32,max(60,w-80),max(80,h-65))
        p.setPen(QPen(color("#334660",90),1))
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
                p.setPen(QPen(color(col,60),7.0))
                # outer line glow underlays the crisp real sample trace
                # introduced as a separate painter pass below
                p.setPen(QPen(color(col),2.5))
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

