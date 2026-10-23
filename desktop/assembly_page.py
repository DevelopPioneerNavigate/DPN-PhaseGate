"""Interactive, entirely native PG-01 Assembly Studio.

Draws engineering bounds, not a simulated physical portal or measured hardware.
Every part can be selected, shown/hidden by subsystem, exploded, and inspected.
No browser/WebGL/service or device commands are used.
"""
from __future__ import annotations
import math
from PySide6.QtCore import Qt, Signal, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF, QFont, QRadialGradient, QLinearGradient
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QCheckBox, QSlider, QComboBox, QSizePolicy, QSplitter
)
from desktop.assembly_model import read_assembly, fit_checks, component_detail
from desktop.build_plan import read_manifest
from desktop.widgets import text_label, Surface, panel_layout

PALETTE={
 "STRUCTURE":"#9F83E8","MOTION":"#53D6F1","OPTICS":"#FFC78A",
 "ROUTING":"#77B3F9","SENSORS":"#8EEAB4","GUARDING":"#F1A69B",
}


def color(hexvalue,opacity=255):
    c=QColor(hexvalue);c.setAlpha(opacity);return c


class AssemblyCanvas(QWidget):
    selected=Signal(str)
    def __init__(self,design,parent=None):
        super().__init__(parent)
        self.design=design
        self.enabled_layers=set(design["view_layers"])
        self.selection="A-RING"
        self.explode=0
        self.orientation="ISOMETRIC"
        self.zoom=100
        self.centers={}
        self.setMinimumSize(455,350)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)
        self.setToolTip("Click a colored component to inspect it in the adjacent pane")

    def set_layers(self,layers):
        self.enabled_layers=set(layers);self.update()
    def set_selection(self,pid):
        self.selection=pid;self.update()
    def set_explode(self,amount):
        self.explode=int(amount);self.update()
    def set_orientation(self,orientation):
        self.orientation=orientation;self.update()
    def set_zoom(self,value):
        self.zoom=int(value);self.update()

    def _xyz(self,part,point):
        x,y,z=point
        if self.explode:
            f=self.explode/100.0
            # Visual staging only: no true machine kinematics implied.
            shifts={
                "STRUCTURE":(0,0,0),
                "MOTION":(0,0,90),
                "SENSORS":(95,0,45),
                "OPTICS":(-85,0,90),
                "ROUTING":(-115,0,65),
                "GUARDING":(130,0,30)
            }
            ax,ay,az=shifts[part["layer"]]
            x+=ax*f;y+=ay*f;z+=az*f
        return (x,y,z)

    def _project(self,xyz):
        x,y,z=xyz
        zoom=self.zoom/100.0
        if self.orientation=="FRONT":
            return QPointF(0.47*self.width()+x*zoom*1.15+y*zoom*.35,
                           self.height()*.77-z*zoom*.88)
        if self.orientation=="TOP":
            return QPointF(0.48*self.width()+x*zoom*1.03+y*zoom*.43,
                           self.height()*.53+y*zoom*.24)
        return QPointF(0.48*self.width()+x*zoom*.84+y*zoom*.39,
                       self.height()*.79-z*zoom*.76+y*zoom*.08)

    def _draw_box(self,p,part):
        x,y,z=self._xyz(part,part["center_mm"])
        wx,wy,wz=part["extent_mm"]
        points=[
          (x-wx/2,y-wy/2,z-wz/2),(x+wx/2,y-wy/2,z-wz/2),
          (x+wx/2,y+wy/2,z-wz/2),(x-wx/2,y+wy/2,z-wz/2),
          (x-wx/2,y-wy/2,z+wz/2),(x+wx/2,y-wy/2,z+wz/2),
          (x+wx/2,y+wy/2,z+wz/2),(x-wx/2,y+wy/2,z+wz/2)]
        v=[self._project(a) for a in points]
        base=PALETTE[part["layer"]];selected=part["id"]==self.selection
        p.setPen(QPen(color(base,248 if selected else 145),2.6 if selected else 1.15))
        for face,alpha in (((0,1,5,4),160),((1,2,6,5),110),((4,5,6,7),185)):
            p.setBrush(color(base,alpha if selected else int(alpha*.53)))
            p.drawPolygon(QPolygonF([v[i] for i in face]))
        return self._project((x,y,z))

    def _draw_ring(self,p,part):
        x,y,z=self._xyz(part,part["center_mm"])
        outer=part["diameter_mm"]/2
        inner=part["clear_diameter_mm"]/2
        main=PALETTE["STRUCTURE"] if part["id"].startswith("B-") else "#60D7F1"
        selected=part["id"]==self.selection
        # Ring lies in XZ plane; use 120 connected actual 3D-projected
        # points rather than a generic 2D ellipse.
        for radius,alpha,width in ((outer,230,9),(inner,205,4)):
            pts=[]
            for i in range(121):
                theta=i*(2*math.pi/120)
                pts.append(self._project((x+radius*math.cos(theta),
                                           y,z+radius*math.sin(theta))))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(color(main,alpha if selected else int(alpha*.74)),
                          width if selected else width*.75))
            p.drawPolyline(QPolygonF(pts))
        # six mechanically meaningful segmentation seams
        for i in range(6):
            t=i*(math.pi/3)
            a=self._project((x+inner*math.cos(t),y,z+inner*math.sin(t)))
            b=self._project((x+outer*math.cos(t),y,z+outer*math.sin(t)))
            p.setPen(QPen(color("#E0D6F9",225 if selected else 140),2))
            p.drawLine(a,b)
        return self._project((x,y,z))

    def _draw_route(self,p,part):
        points=[self._project(self._xyz(part,a)) for a in part["points_mm"]]
        selected=part["id"]==self.selection
        pen=QPen(color(PALETTE["ROUTING"],255 if selected else 160),
                 4.5 if selected else 2.4)
        pen.setStyle(Qt.PenStyle.DashLine)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPolyline(QPolygonF(points))
        return points[len(points)//2]

    def paintEvent(self,event):
        p=QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing,True)
        w,h=self.width(),self.height()
        bg=QLinearGradient(0,0,w,h)
        bg.setColorAt(0,color("#071524"))
        bg.setColorAt(.58,color("#0B1A32"))
        bg.setColorAt(1,color("#231535"))
        p.fillRect(self.rect(),bg)
        p.setPen(QPen(color("#4A6890",41),.8))
        for i in range(0,w,34):
            p.drawLine(i,0,i,h)
        for j in range(0,h,34):
            p.drawLine(0,j,w,j)
        # Assembly datum and the station centers.
        p.setPen(QPen(color("#7B9CBD",90),1.4,Qt.PenStyle.DashLine))
        for y in (-400,400):
            a=self._project((-210,y,0))
            b=self._project((210,y,0))
            p.drawLine(a,b)
        positions={}
        # Far to near by machine-depth coordinate. Avoid nondeterministic painting order.
        parts=sorted(self.design["assemblies"],
                     key=lambda a: a.get("center_mm",[0,0,0])[1] if a["shape"]!="route"
                     else a["points_mm"][0][1],reverse=True)
        for part in parts:
            if part["layer"] not in self.enabled_layers:
                continue
            if part["shape"]=="ring": pt=self._draw_ring(p,part)
            elif part["shape"]=="route": pt=self._draw_route(p,part)
            else:pt=self._draw_box(p,part)
            positions[part["id"]]=pt
            if part["id"]==self.selection:
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.setPen(QPen(color("#E9F8FF",214),1.3,Qt.PenStyle.DashLine))
                p.drawEllipse(pt,14,14)
        self.centers=positions
        p.setFont(QFont("Consolas",9,QFont.Weight.Bold))
        p.setPen(color("#72DBE9"))
        p.drawText(18,24,"PG-01   /   3D ASSEMBLY EXPLORER")
        p.setPen(color("#ABBCD8"))
        p.drawText(18,43,"ENGINEERING ENVELOPES  •  NO POWER / NO PHYSICAL HARDWARE")
        p.setFont(QFont("Consolas",9))
        p.setPen(color("#E8C1FF"))
        p.drawText(18,h-16,
                   f"{self.orientation}   |   EXPLODED {self.explode}%   |   REV v1.5   |   {len(positions)} VISIBLE")
        p.end()

    def mousePressEvent(self,event):
        if event.button()!=Qt.MouseButton.LeftButton:return
        cursor=event.position()
        nearest=None
        distance=38
        for pid,center in self.centers.items():
            d=math.hypot(cursor.x()-center.x(),cursor.y()-center.y())
            if d<distance:
                distance=d;nearest=pid
        if nearest:
            self.selected.emit(nearest)


class AssemblyStudio(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.design=read_assembly()
        self.rig=read_manifest()
        self.setObjectName("assemblyStudio")
        self._build()
        self.choose_part("A-RING")

    def _build(self):
        root=QVBoxLayout(self)
        root.setContentsMargins(25,18,25,24)
        root.setSpacing(10)
        root.addWidget(text_label("PG-01    /    CAD-SOURCED GEOMETRY    /    FABRICATION STUDY",10,"cyan",True))
        root.addWidget(text_label("ASSEMBLY STUDIO  /  GATE A + GATE B",25,"text",True))
        root.addWidget(text_label(
            "Explore every physical subsystem, isolate cables or optics and explode the assembly. "
            "All geometry is an unbuilt revision for mechanical review.",11,"muted"))
        row=QHBoxLayout()
        row.setSpacing(12)
        self.view=QComboBox()
        self.view.setFixedWidth(145)
        self.view.addItems(["ISOMETRIC","FRONT","TOP"])
        self.view.currentTextChanged.connect(self.change_view)
        row.addWidget(text_label("VIEW",10,"muted",True))
        row.addWidget(self.view)
        row.addSpacing(6)
        row.addWidget(text_label("EXPLODE",10,"violet",True))
        self.explode=QSlider(Qt.Orientation.Horizontal)
        self.explode.setRange(0,100)
        self.explode.setValue(17)
        row.addWidget(self.explode,1)
        row.addWidget(text_label("ZOOM",10,"cyan",True))
        self.zoom=QSlider(Qt.Orientation.Horizontal)
        self.zoom.setRange(65,120)
        self.zoom.setValue(88)
        self.zoom.setMaximumWidth(125)
        row.addWidget(self.zoom)
        root.addLayout(row)
        visible=QHBoxLayout()
        visible.addWidget(text_label("SYSTEM LAYERS",10,"violet",True))
        self.toggles={}
        for layer in self.design["view_layers"]:
            toggle=QCheckBox(layer)
            toggle.setChecked(True)
            toggle.toggled.connect(self.change_layers)
            visible.addWidget(toggle)
            self.toggles[layer]=toggle
        visible.addStretch()
        root.addLayout(visible)
        split=QSplitter(Qt.Orientation.Horizontal)
        split.setChildrenCollapsible(False)
        self.canvas=AssemblyCanvas(self.design)
        self.canvas.selected.connect(self.choose_part)
        split.addWidget(self.canvas)
        panel=Surface("assemblyInspector")
        right=QVBoxLayout(panel)
        right.setContentsMargins(15,14,15,14)
        right.setSpacing(8)
        right.addWidget(text_label("COMPONENT INSPECTOR  /  SELECT A PART",11,"cyan",True))
        self.parts=QListWidget()
        self.parts.setMinimumWidth(280)
        self.parts.setMinimumHeight(150)
        for part in self.design["assemblies"]:
            self.parts.addItem(part["id"]+"   "+part["name"])
        self.parts.currentRowChanged.connect(self.select_row)
        right.addWidget(self.parts,1)
        self.name=text_label("",15,"text",True)
        right.addWidget(self.name)
        self.details=text_label("",11,"muted")
        right.addWidget(self.details)
        self.review=text_label("",11,"amber")
        right.addWidget(self.review)
        split.addWidget(panel)
        split.setStretchFactor(0,4)
        split.setStretchFactor(1,2)
        root.addWidget(split,1)
        self.explode.valueChanged.connect(self.canvas.set_explode)
        self.zoom.valueChanged.connect(self.canvas.set_zoom)
        self.canvas.set_explode(self.explode.value())
        self.canvas.set_zoom(self.zoom.value())
        statuses=Surface("assemblyFit")
        v=panel_layout(statuses,12,7)
        v.addWidget(text_label("AUTOMATED FIT-CHECK  /  PRELIMINARY NUMERIC ENVELOPES",11,"cyan",True))
        self.checks=text_label("",11,"muted")
        v.addWidget(self.checks)
        root.addWidget(statuses)
        status=fit_checks(self.design,self.rig["dimensions_mm"])
        self.checks.setText("    •    ".join(
            f"{'PASS' if check['passed'] else 'HOLD'} {check['name']}: "
            f"{check['measured']:.1f}mm (goal ≥{check['target']:.1f}mm)"
            for check in status))
        root.addWidget(text_label("PASS = envelope math only. No stress, vibration, load, tolerances or actual "
                                  "assembly verified. Unpowered model; no portal field hardware.",10,"amber"))

    def change_layers(self,_=None):
        active={layer for layer,ctrl in self.toggles.items() if ctrl.isChecked()}
        self.canvas.set_layers(active)

    def change_view(self,view):
        self.canvas.set_orientation(view)

    def select_row(self,row):
        if 0<=row<len(self.design["assemblies"]):
            self.choose_part(self.design["assemblies"][row]["id"],sync=False)

    def choose_part(self,pid,sync=True):
        part=component_detail(self.design,pid)
        self.canvas.set_selection(pid)
        if sync:
            row=next(i for i,p in enumerate(self.design["assemblies"]) if p["id"]==pid)
            self.parts.blockSignals(True)
            self.parts.setCurrentRow(row)
            self.parts.blockSignals(False)
        self.name.setText(part["name"])
        self.details.setText(part["id"]+" • "+part["layer"]+"\n"+part["material"])
        self.review.setText("ENGINEERING HOLD: "+part["review"])
