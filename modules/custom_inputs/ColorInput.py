"""
ColorInputWidget — A modern, drop-in PySide6 color picker widget.

API mirrors QLineEdit:
  .text()                  → returns current hex color string e.g. "#ff6b35"
  .setText(hex_str)        → sets color from hex string
  .setPlaceholderText(txt) → sets placeholder shown when no color selected
  .setReadOnly(bool)       → disables interaction
  .clear()                 → resets to no color (placeholder state)
  .setColor(QColor)        → set color from a QColor object
  .color()                 → returns current QColor object

Signals:
  .textChanged(str)        → emitted when color changes, passes hex string
  .colorChanged(QColor)    → emitted when color changes, passes QColor

Usage:
    from color_input import ColorInputWidget

    widget = ColorInputWidget()
    widget.setText("#e74c3c")
    widget.textChanged.connect(lambda hex_val: print("New color:", hex_val))
"""

import sys
import math
from PySide6.QtWidgets import (
    QWidget, QApplication, QHBoxLayout, QVBoxLayout,
    QLineEdit, QFrame, QLabel, QSizePolicy, QGraphicsDropShadowEffect,
    QSlider, QMainWindow
)
from PySide6.QtCore import (
    Qt, Signal, QPoint, QRect, QSize, QPropertyAnimation,
    QEasingCurve, Property, QObject, QTimer
)
from PySide6.QtGui import (
    QColor, QPainter, QLinearGradient, QConicalGradient,
    QRadialGradient, QBrush, QPen, QPixmap, QCursor,
    QMouseEvent, QPaintEvent, QFont, QFontDatabase, QKeyEvent
)


# ─────────────────────────────────────────────
#  Saturation / Brightness canvas
# ─────────────────────────────────────────────
class _SBCanvas(QWidget):
    colorPicked = Signal(float, float)   # saturation, brightness  (0-1)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 160)
        self._hue = 0.0          # 0-360
        self._sat = 1.0
        self._bri = 1.0
        self._dragging = False
        self.setCursor(Qt.CrossCursor)

    def setHue(self, hue: float):
        self._hue = hue
        self.update()

    def setSB(self, sat: float, bri: float):
        self._sat = sat
        self._bri = bri
        self.update()

    def paintEvent(self, event: QPaintEvent):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()

        # White → Hue gradient (horizontal)
        hue_color = QColor.fromHsvF(self._hue / 360.0, 1.0, 1.0)
        hg = QLinearGradient(rect.topLeft(), rect.topRight())
        hg.setColorAt(0, QColor(255, 255, 255))
        hg.setColorAt(1, hue_color)
        p.fillRect(rect, hg)

        # Transparent → Black gradient (vertical)
        vg = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        vg.setColorAt(0, QColor(0, 0, 0, 0))
        vg.setColorAt(1, QColor(0, 0, 0, 255))
        p.fillRect(rect, vg)

        # Cursor circle
        cx = int(self._sat * rect.width())
        cy = int((1.0 - self._bri) * rect.height())
        p.setPen(QPen(Qt.white, 2))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPoint(cx, cy), 6, 6)
        p.setPen(QPen(QColor(0, 0, 0, 80), 1))
        p.drawEllipse(QPoint(cx, cy), 7, 7)

    def _pick(self, pos: QPoint):
        w, h = self.width(), self.height()
        s = max(0.0, min(1.0, pos.x() / w))
        b = max(0.0, min(1.0, 1.0 - pos.y() / h))
        self._sat = s
        self._bri = b
        self.update()
        self.colorPicked.emit(s, b)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._dragging = True
            self._pick(e.position().toPoint())

    def mouseMoveEvent(self, e: QMouseEvent):
        if self._dragging:
            self._pick(e.position().toPoint())

    def mouseReleaseEvent(self, e: QMouseEvent):
        self._dragging = False


# ─────────────────────────────────────────────
#  Hue strip
# ─────────────────────────────────────────────
class _HueStrip(QWidget):
    hueChanged = Signal(float)   # 0-360

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 14)
        self._hue = 0.0
        self._dragging = False
        self.setCursor(Qt.SizeHorCursor)

    def setHue(self, hue: float):
        self._hue = hue
        self.update()

    def paintEvent(self, event: QPaintEvent):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        r = 7

        # Rainbow gradient
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        for i in range(7):
            gradient.setColorAt(i / 6, QColor.fromHsvF(i / 6, 1.0, 1.0))
        p.setBrush(gradient)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(rect, r, r)

        # Thumb
        tx = int(self._hue / 360.0 * rect.width())
        tx = max(7, min(rect.width() - 7, tx))
        p.setBrush(Qt.white)
        p.setPen(QPen(QColor(0, 0, 0, 60), 1))
        p.drawEllipse(QPoint(tx, rect.height() // 2), 6, 6)

    def _pick(self, pos: QPoint):
        hue = max(0.0, min(360.0, pos.x() / self.width() * 360.0))
        self._hue = hue
        self.update()
        self.hueChanged.emit(hue)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._dragging = True
            self._pick(e.position().toPoint())

    def mouseMoveEvent(self, e: QMouseEvent):
        if self._dragging:
            self._pick(e.position().toPoint())

    def mouseReleaseEvent(self, e: QMouseEvent):
        self._dragging = False


# ─────────────────────────────────────────────
#  Alpha strip
# ─────────────────────────────────────────────
class _AlphaStrip(QWidget):
    alphaChanged = Signal(float)   # 0-1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 14)
        self._alpha = 1.0
        self._color = QColor(255, 0, 0)
        self._dragging = False
        self.setCursor(Qt.SizeHorCursor)

    def setColor(self, color: QColor):
        self._color = color
        self.update()

    def setAlpha(self, alpha: float):
        self._alpha = alpha
        self.update()

    def paintEvent(self, event: QPaintEvent):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        r = 7

        # Checker
        checker_size = 5
        for row in range(self.height() // checker_size + 1):
            for col in range(self.width() // checker_size + 1):
                if (row + col) % 2 == 0:
                    p.fillRect(col * checker_size, row * checker_size,
                               checker_size, checker_size, QColor(200, 200, 200))
                else:
                    p.fillRect(col * checker_size, row * checker_size,
                               checker_size, checker_size, QColor(255, 255, 255))

        # Color-to-transparent gradient
        c_opaque = QColor(self._color)
        c_opaque.setAlpha(255)
        c_trans = QColor(self._color)
        c_trans.setAlpha(0)
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        gradient.setColorAt(0, c_trans)
        gradient.setColorAt(1, c_opaque)
        p.setBrush(gradient)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(rect, r, r)

        # Thumb
        tx = int(self._alpha * rect.width())
        tx = max(7, min(rect.width() - 7, tx))
        p.setBrush(Qt.white)
        p.setPen(QPen(QColor(0, 0, 0, 60), 1))
        p.drawEllipse(QPoint(tx, rect.height() // 2), 6, 6)

    def _pick(self, pos: QPoint):
        a = max(0.0, min(1.0, pos.x() / self.width()))
        self._alpha = a
        self.update()
        self.alphaChanged.emit(a)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._dragging = True
            self._pick(e.position().toPoint())

    def mouseMoveEvent(self, e: QMouseEvent):
        if self._dragging:
            self._pick(e.position().toPoint())

    def mouseReleaseEvent(self, e: QMouseEvent):
        self._dragging = False


# ─────────────────────────────────────────────
#  Popup panel
# ─────────────────────────────────────────────
class _ColorPopup(QFrame):
    colorChanged = Signal(QColor)

    SWATCHES = [
        "#e74c3c", "#e67e22", "#f1c40f", "#2ecc71",
        "#1abc9c", "#3498db", "#9b59b6", "#34495e",
        "#ff6b9d", "#ff9f43", "#feca57", "#48dbfb",
        "#ff6b6b", "#a29bfe", "#fd79a8", "#636e72",
        "#ffffff", "#d4d4d4", "#888888", "#222222",
    ]

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._color = QColor("#ff6b35")
        self._building = False
        self._setup_ui()
        self._apply_color(self._color, emit=False)

    def _setup_ui(self):
        self.setFixedWidth(252)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame(self)
        card.setObjectName("card")
        card.setStyleSheet("""
            QFrame#card {
                background: #1e1e2e;
                border: 1px solid #313244;
                border-radius: 12px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 140))
        card.setGraphicsEffect(shadow)

        outer.addWidget(card)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(10)

        # ── SB Canvas ──
        self._sb = _SBCanvas()
        self._sb.colorPicked.connect(self._on_sb)
        lay.addWidget(self._sb)

        # ── Hue strip ──
        self._hue_strip = _HueStrip()
        self._hue_strip.hueChanged.connect(self._on_hue)
        lay.addWidget(self._hue_strip)

        # ── Alpha strip ──
        self._alpha_strip = _AlphaStrip()
        self._alpha_strip.alphaChanged.connect(self._on_alpha)
        lay.addWidget(self._alpha_strip)

        # ── Preview + hex input ──
        row = QHBoxLayout()
        row.setSpacing(8)

        self._preview = QLabel()
        self._preview.setFixedSize(32, 28)
        self._preview.setStyleSheet("border-radius:6px;")
        row.addWidget(self._preview)

        self._hex_edit = QLineEdit()
        self._hex_edit.setPlaceholderText("#rrggbb")
        self._hex_edit.setMaxLength(9)
        self._hex_edit.setStyleSheet("""
            QLineEdit {
                background: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 4px 8px;
                font-family: 'JetBrains Mono', 'Courier New', monospace;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #89b4fa;
            }
        """)
        self._hex_edit.textEdited.connect(self._on_hex_edited)
        row.addWidget(self._hex_edit)
        lay.addLayout(row)



    # ── Internal state ──────────────────────────────────
    def _apply_color(self, color: QColor, emit=True):
        self._building = True
        self._color = color

        h, s, v, a = color.hsvHueF(), color.hsvSaturationF(), color.valueF(), color.alphaF()
        if h < 0:
            h = 0.0

        self._sb.setHue(h * 360)
        self._sb.setSB(s, v)
        self._hue_strip.setHue(h * 360)
        self._alpha_strip.setColor(color)
        self._alpha_strip.setAlpha(a)

        self._preview.setStyleSheet(
            f"border-radius:6px; background: {color.name(QColor.HexArgb)};"
        )
        self._hex_edit.setText(color.name(QColor.HexArgb if a < 1.0 else QColor.HexRgb))

        self._building = False
        if emit:
            self.colorChanged.emit(color)

    def setColor(self, color: QColor):
        self._apply_color(color, emit=False)

    def getColor(self) -> QColor:
        return self._color

    # ── Slot handlers ────────────────────────────────────
    def _on_sb(self, s, v):
        if self._building:
            return
        h = self._color.hsvHueF()
        if h < 0:
            h = 0.0
        a = self._color.alphaF()
        c = QColor.fromHsvF(h, s, v, a)
        self._apply_color(c)

    def _on_hue(self, hue):
        if self._building:
            return
        s = self._color.hsvSaturationF()
        v = self._color.valueF()
        a = self._color.alphaF()
        c = QColor.fromHsvF(hue / 360.0, s, v, a)
        self._apply_color(c)

    def _on_alpha(self, alpha):
        if self._building:
            return
        c = QColor(self._color)
        c.setAlphaF(alpha)
        self._apply_color(c)

    def _on_hex_edited(self, text: str):
        if self._building:
            return
        text = text.strip()
        if not text.startswith("#"):
            text = "#" + text
        c = QColor(text)
        if c.isValid():
            self._apply_color(c)

    def _on_swatch(self, hex_val: str):
        self._apply_color(QColor(hex_val))


class _SwatchButton(QWidget):
    clicked_color = Signal(str)

    def __init__(self, hex_color: str, parent=None):
        super().__init__(parent)
        self._color = hex_color
        self.setFixedSize(34, 22)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(hex_color)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor(self._color))
        p.setPen(QPen(QColor(255, 255, 255, 30), 1))
        p.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 4, 4)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked_color.emit(self._color)


# ─────────────────────────────────────────────
#  Main public widget
# ─────────────────────────────────────────────
class ColorInputWidget(QWidget):
    """
    A QLineEdit-style color input widget for PySide6.

    Displays a compact color swatch + hex value.
    Clicking opens a floating color picker popup.

    Signals:
        textChanged(str)   — hex string of current color
        colorChanged(QColor) — QColor of current color
    """

    textChanged = Signal(str)
    colorChanged = Signal(QColor)

    def __init__(self, parent=None, color: str = "#4f9cf9"):
        super().__init__(parent)
        self._color: QColor = QColor(color)
        self._placeholder = "Pick a color…"
        self._read_only = False
        self._has_color = True
        self._popup: _ColorPopup | None = None
        self._setup_ui()
        self._refresh()

    # ── UI setup ─────────────────────────────────────────
    def _setup_ui(self):
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)

        self.setStyleSheet("""
            ColorInputWidget {
                background: transparent;
            }
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._frame = QFrame()
        self._frame.setObjectName("ci_frame")
        lay.addWidget(self._frame)

        inner = QHBoxLayout(self._frame)
        inner.setContentsMargins(6, 6, 10, 6)
        inner.setSpacing(8)

        # Color swatch
        self._swatch = QLabel()
        self._swatch.setFixedSize(24, 24)
        inner.addWidget(self._swatch)

        # Hex / placeholder label
        self._label = QLabel()
        self._label.setFont(QFont("JetBrains Mono", 11) if
                            QFontDatabase.families() else QFont("Courier New", 11))
        inner.addWidget(self._label, 1)

        # Chevron icon
        self._chevron = QLabel("⌄")
        self._chevron.setStyleSheet("color: #6c7086; font-size: 14px;")
        inner.addWidget(self._chevron)

        self._apply_frame_style()

    def _apply_frame_style(self):
        self._frame.setStyleSheet("""
            QFrame#ci_frame {
                background: #1e1e2e;
                border: 1.5px solid #313244;
                border-radius: 10px;
            }
            QFrame#ci_frame:hover {
                border: 1.5px solid #89b4fa;
            }
        """)
        self._label.setStyleSheet("color: #cdd6f4; font-size: 12px;")

    def _refresh(self):
        if not self._has_color:
            self._swatch.setStyleSheet(
                "background: #313244; border-radius: 5px; border: 1px dashed #45475a;"
            )
            self._label.setText(self._placeholder)
            self._label.setStyleSheet("color: #6c7086; font-size: 12px;")
            self._chevron.show()
            return

        hex_str = self._color.name(
            QColor.HexArgb if self._color.alphaF() < 1.0 else QColor.HexRgb
        )
        self._swatch.setStyleSheet(
            f"background: {hex_str}; border-radius: 5px;"
        )
        self._label.setText(hex_str.upper())
        self._label.setStyleSheet("color: #cdd6f4; font-size: 12px;")

    # ── Event handling ───────────────────────────────────
    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton and not self._read_only:
            self._open_popup()

    def _open_popup(self):
        if self._popup is None:
            self._popup = _ColorPopup()
            self._popup.colorChanged.connect(self._on_popup_color)

        if self._has_color:
            self._popup.setColor(self._color)

        # Position below widget, shifted further left
        popup_w = self._popup.sizeHint().width() or 252
        offset_x = max(0, (popup_w - self.width()) // 2) + 60
        pos = self.mapToGlobal(QPoint(-offset_x, self.height() + 4))
        self._popup.move(pos)
        self._popup.show()
        self._popup.raise_()

    def _on_popup_color(self, color: QColor):
        self._color = color
        self._has_color = True
        self._refresh()
        hex_str = color.name(
            QColor.HexArgb if color.alphaF() < 1.0 else QColor.HexRgb
        )
        self.textChanged.emit(hex_str)
        self.colorChanged.emit(color)

    # ── Public API  (mirrors QLineEdit) ─────────────────
    def text(self) -> str:
        """Returns the current hex color string, e.g. '#ff6b35'."""
        if not self._has_color:
            return ""
        return self._color.name(
            QColor.HexArgb if self._color.alphaF() < 1.0 else QColor.HexRgb
        )

    @staticmethod
    def _parse_color(text: str) -> QColor:
        """
        Parse a color from multiple string formats:
          - "#rrggbb" / "#aarrggbb"
          - "rgb(r, g, b)"
          - "rgba(r, g, b, a)"   — alpha 0-255 or 0.0-1.0
          - Any format QColor natively understands
        Returns a valid QColor or an invalid QColor() on failure.
        """
        import re
        text = text.strip()

        # rgb(r, g, b)  or  rgba(r, g, b, a)
        m = re.fullmatch(
            r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)'
            r'(?:\s*,\s*([\d.]+))?\s*\)',
            text, re.IGNORECASE
        )
        if m:
            r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
            a_raw = m.group(4)
            if a_raw is not None:
                a_val = float(a_raw)
                # Treat values > 1 as 0-255 range, otherwise 0.0-1.0
                a = int(a_val) if a_val > 1 else int(a_val * 255)
            else:
                a = 255
            return QColor(r, g, b, a)

        # Fallback: let Qt try (handles #hex, named colors, etc.)
        return QColor(text)

    def setText(self, color_str: str):
        """
        Sets the color from a string. Supports:
          '#rrggbb', '#aarrggbb', 'rgb(r,g,b)', 'rgba(r,g,b,a)',
          and any format Qt's QColor understands.
        Emits textChanged.
        """
        if not color_str:
            self.clear()
            return
        c = self._parse_color(color_str)
        if c.isValid():
            self._color = c
            self._has_color = True
            self._refresh()
            self.textChanged.emit(self.text())
            self.colorChanged.emit(self._color)

    def setPlaceholderText(self, text: str):
        """Sets the placeholder text shown when no color is selected."""
        self._placeholder = text
        if not self._has_color:
            self._label.setText(text)

    def setReadOnly(self, read_only: bool):
        """Disables/enables color picker interaction."""
        self._read_only = read_only
        self.setCursor(Qt.ArrowCursor if read_only else Qt.PointingHandCursor)
        self._chevron.setVisible(not read_only)

    def clear(self):
        """Resets to no-color (placeholder) state."""
        self._has_color = False
        self._refresh()
        self.textChanged.emit("")

    def setColor(self, color: QColor):
        """Sets the color from a QColor object."""
        if color.isValid():
            self._color = color
            self._has_color = True
            self._refresh()
            self.textChanged.emit(self.text())
            self.colorChanged.emit(self._color)

    def color(self) -> QColor:
        """Returns the current QColor."""
        return QColor(self._color) if self._has_color else QColor()

    def isReadOnly(self) -> bool:
        return self._read_only


# ─────────────────────────────────────────────
#  Demo window
# ─────────────────────────────────────────────
class DemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ColorInputWidget — Demo")
        self.setMinimumSize(480, 400)
        self.setStyleSheet("""
            QMainWindow, QWidget#central {
                background: #11111b;
            }
            QLabel {
                color: #cdd6f4;
            }
        """)

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        main = QVBoxLayout(central)
        main.setContentsMargins(40, 40, 40, 40)
        main.setSpacing(24)

        title = QLabel("Color Input Widget")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #cdd6f4;")
        main.addWidget(title)

        subtitle = QLabel("A drop-in PySide6 color picker with QLineEdit-compatible API")
        subtitle.setStyleSheet("font-size: 13px; color: #6c7086;")
        main.addWidget(subtitle)

        # Widget 1 — default
        self._add_section(main, "Default", ColorInputWidget(color="#4f9cf9"))

        # Widget 2 — preset red
        w2 = ColorInputWidget(color="#e74c3c")
        self._add_section(main, "Preset color (#e74c3c)", w2)

        # Widget 3 — read-only
        w3 = ColorInputWidget(color="#2ecc71")
        w3.setReadOnly(True)
        self._add_section(main, "Read-only", w3)

        # Widget 4 — empty with custom placeholder
        w4 = ColorInputWidget()
        w4.clear()
        w4.setPlaceholderText("Choose background color…")
        self._status = QLabel("No color selected")
        self._status.setStyleSheet("font-size: 12px; color: #a6adc8; padding-left: 2px;")
        w4.textChanged.connect(lambda h: self._status.setText(f"textChanged → {h}"))
        section = self._add_section(main, "Custom placeholder + textChanged signal", w4)
        section.addWidget(self._status)

        main.addStretch()

    def _add_section(self, parent_layout, label_text, widget):
        lbl = QLabel(label_text)
        lbl.setStyleSheet("font-size: 11px; font-weight: 600; color: #7f849c; letter-spacing: 1px;")
        parent_layout.addWidget(lbl)
        parent_layout.addWidget(widget)
        return parent_layout


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = DemoWindow()
    win.show()
    sys.exit(app.exec())