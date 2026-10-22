"""UI button helper shared by the native window and Hardware Lab."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton


def button(label: str, secondary: bool = False):
    widget = QPushButton(label)
    widget.setMinimumHeight(39)
    widget.setCursor(Qt.CursorShape.PointingHandCursor)
    widget.setProperty("variant", "secondary" if secondary else "primary")
    return widget
