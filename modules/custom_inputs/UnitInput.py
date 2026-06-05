import sys
import re
from PySide6.QtWidgets import (QLineEdit, QComboBox, QLabel)

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QSlider, QFrame, QPushButton)
from PySide6.QtCore import Qt, Signal, QPoint, QRect, QSize
from PySide6.QtGui import QColor, QPainter, QLinearGradient


class UnitInput(QWidget):
    valueChanged = Signal(float, str)  # emits (value, unit)

    def __init__(self, units=None, parent=None):
        super().__init__(parent)

        if units is None:
            units = ["mm", "cm", "m"]

        self.line_edit = QLineEdit()
        self.combo = QComboBox()
        self.combo.addItems(units)

        self.line_edit.setPlaceholderText("Enter value")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.combo)

        # Connect signals
        self.line_edit.textChanged.connect(self.emit_value)
        self.combo.currentTextChanged.connect(self.emit_value)

    def emit_value(self):
        try:
            value = float(self.line_edit.text())
        except ValueError:
            value = 0.0

        unit = self.combo.currentText()
        self.valueChanged.emit(value, unit)

    def get_value(self):
        try:
            return float(self.line_edit.text()), self.combo.currentText()
        except ValueError:
            return None, self.combo.currentText()


# COLOR INPUT

class SVPanel(QFrame):
    """The 2D Square for picking Saturation and Value."""
    colorChanged = Signal(int, int)  # Saturation, Value

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.hue = 0
        self.sat = 255
        self.val = 255
        self.cursor_pos = QPoint(199, 0)  # Top right (Max Sat, Max Val)

    def set_hue(self, hue):
        self.hue = hue
        self.update()  # Redraw with new base color

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 1. Draw the Base Hue -> White horizontal gradient
        hue_color = QColor.fromHsv(self.hue, 255, 255)
        grad_h = QLinearGradient(0, 0, self.width(), 0)
        grad_h.setColorAt(1, hue_color)
        grad_h.setColorAt(0, Qt.white)
        painter.fillRect(self.rect(), grad_h)

        # 2. Draw the Transparent -> Black vertical gradient
        grad_v = QLinearGradient(0, 0, 0, self.height())
        grad_v.setColorAt(0, Qt.transparent)
        grad_v.setColorAt(1, Qt.black)
        painter.fillRect(self.rect(), grad_v)

        # 3. Draw the selection cursor (a small circle)
        painter.setPen(Qt.white if self.val < 128 else Qt.black)
        painter.drawEllipse(self.cursor_pos, 5, 5)

    def mousePressEvent(self, event):
        self.update_from_mouse(event.pos())

    def mouseMoveEvent(self, event):
        self.update_from_mouse(event.pos())

    def update_from_mouse(self, pos):
        # Constrain cursor to the box
        x = max(0, min(pos.x(), self.width() - 1))
        y = max(0, min(pos.y(), self.height() - 1))
        self.cursor_pos = QPoint(x, y)

        # Map pixels to 0-255 range for HSV
        self.sat = int((x / self.width()) * 255)
        self.val = int(255 - (y / self.height()) * 255)

        self.colorChanged.emit(self.sat, self.val)
        self.update()


class ModernColorPicker(QFrame):
    colorChanged = Signal(QColor)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.current_hue = 0

        layout = QHBoxLayout(self)

        # The 2D SV Plane
        self.sv_panel = SVPanel()
        self.sv_panel.colorChanged.connect(self.update_color)

        # The Hue Slider (Vertical)
        self.hue_slider = QSlider(Qt.Vertical)
        self.hue_slider.setRange(0, 359)
        self.hue_slider.setInvertedAppearance(True)  # Red at top
        self.hue_slider.valueChanged.connect(self.update_hue)
        self.hue_slider.setStyleSheet("width: 20px;")  # Add your rainbow CSS here!
        self.hue_slider.setStyleSheet("""
            QSlider::groove:vertical {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ff0000, stop:0.16 #ffff00, stop:0.33 #00ff00, 
                    stop:0.5 #00ffff, stop:0.66 #0000ff, stop:0.83 #ff00ff, stop:1 #ff0000);
                width: 15px;
            }
            QSlider::handle:vertical {
                background: white; border: 1px solid black; height: 10px; margin: 0 -2px;
            }
        """)

        layout.addWidget(self.sv_panel)
        layout.addWidget(self.hue_slider)

    def update_hue(self, hue):
        self.current_hue = hue
        self.sv_panel.set_hue(hue)
        self.update_color()

    def update_color(self):
        color = QColor.fromHsv(self.current_hue, self.sv_panel.sat, self.sv_panel.val)
        self.colorChanged.emit(color)

    def set_color(self, color_input):
        """
            Sets the picker color dynamically.
            Handles: "#RRGGBB", (R,G,B), and "rgb(R,G,B)"
            """
        new_color = QColor()

        # 1. Handle "rgb(0,0,0)" format
        if isinstance(color_input, str) and color_input.startswith("rgb"):
            # Use regex to find all numbers in the string
            nums = re.findall(r'\d+', color_input)
            if len(nums) >= 3:
                r, g, b = map(int, nums[:3])
                new_color = QColor(r, g, b)

        # 2. Handle Hex string or QColor name
        elif isinstance(color_input, str):
            new_color = QColor(color_input)

        # 3. Handle Tuple/List
        elif isinstance(color_input, (tuple, list)):
            new_color = QColor(*color_input)

        # Validation check
        if not new_color.isValid():
            print(f"Invalid color input: {color_input}")
            self.colorChanged.emit(color_input)
            return

        # --- UI Update Logic (same as before) ---
        h = new_color.hsvHue()
        s = new_color.hsvSaturation()
        v = new_color.value()

        if h < 0: h = 0

        # Update Slider
        self.current_hue = h
        self.hue_slider.blockSignals(True)
        self.hue_slider.setValue(h)
        self.hue_slider.blockSignals(False)

        # Update SV Panel
        self.sv_panel.hue = h
        self.sv_panel.sat = s
        self.sv_panel.val = v

        # Calculate cursor position
        x = int((s / 255) * (self.sv_panel.width() - 1))
        y = int((1 - v / 255) * (self.sv_panel.height() - 1))
        self.sv_panel.cursor_pos = QPoint(x, y)

        self.sv_panel.update()
        # Optional: Emit the signal to let the UI know the update is complete
        self.colorChanged.emit(new_color)


class ColorButton(QWidget):
    colorUpdated = Signal(str)

    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()
        self.label = QLabel()
        self.btn = QPushButton()
        self.btn.setFixedSize(30, 30)
        self.color = QColor()
        self.picker = ModernColorPicker()
        self.btn.clicked.connect(self.show_picker)
        self.picker.colorChanged.connect(self.apply_color)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.btn)

        self.setLayout(self.layout)

    def show_picker(self):
        # Calculate desired position (aligned to button left)
        pos = self.btn.mapToGlobal(self.btn.rect().bottomLeft())

        # Optional: If you want it to explicitly shift left by 100 pixels
        pos.setX(pos.x() - 200)

        # Ensure it doesn't go off the left side of the screen (0)
        final_x = max(0, pos.x())

        self.picker.move(final_x, pos.y())
        self.picker.show()

        # self.picker.move(self.btn.mapToGlobal(self.btn.rect().bottomRight()))
        # self.picker.show()

    def apply_color(self, color):
        self.btn.setStyleSheet(f"background-color: {color.name()}; color: white;")
        self.color.setNamedColor(color.name())
        self.colorUpdated.emit(self.color.name())

    def sizeHint(self):
        return QSize(30, 30)
