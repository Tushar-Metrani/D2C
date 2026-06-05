import os
from pathlib import Path

from PySide6.QtWidgets import QApplication,QSplashScreen, QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy
from PySide6.QtGui import QIcon, QPixmap
from modules import AppData

from modules import Navbar
from modules import Canvas
from modules import LeftPanel
from modules import RightPanel
from modules import StatusBar
from modules import GLOBAL

""" USER_DIR = Path(os.getenv("APPDATA")) / "DesignToCode"
USER_DIR.mkdir(parents=True, exist_ok=True) """


USER_DIR = GLOBAL.BASE_DIR / "userdata"




BASE_DIR = GLOBAL.BASE_DIR
QSS_PATH = BASE_DIR / "style" / "modern_purple_theme2.qss"
icon_path = BASE_DIR / "assets" / "icons" / "icon.png"
file_path = BASE_DIR / "schema" / "properties.json"
stylefile_path = BASE_DIR / "schema" / "style.json"


app = QApplication([])
app.setStyle("Fusion")

#Splash Screen

pixmap = QPixmap(str( BASE_DIR / "assets" / "splash" / "splash_screen.png"))
splash = QSplashScreen(pixmap)
splash.show()

app.processEvents()

# Data State
"""
def change_project_name():
    index = 1  # the position you want to replace

    item = hlayout.takeAt(index)
    old_widget = item.widget()

    if old_widget:
        old_widget.deleteLater()

    new_canvas = Canvas.Canvas(state)
    hlayout.replaceWidget(canvas, new_canvas)
    hlayout.insertWidget(index, new_canvas)
"""

state = AppData.AppState()

#state.project_name.data_changed.connect(change_project_name)

window = QWidget()

window.setWindowTitle("DesignToCode")
window.setBaseSize(1080, 700)

spacer = QSpacerItem(10, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

# initializing layout
main_layout = QVBoxLayout()
main_layout.setContentsMargins(0, 0, 0, 0)

hlayout = QHBoxLayout()

# creating instances
navbar = Navbar.Navbar(state, window)
status_bar = StatusBar.StatusBar(state)
left_panel = LeftPanel.LeftPanel(state)
canvas = Canvas.Canvas(state)
right_panel = RightPanel.RightPanel(state)

# adding widgets to layout

main_layout.addWidget(navbar)
main_layout.addWidget(status_bar)
hlayout.addWidget(left_panel, stretch=1)
hlayout.addWidget(canvas, stretch=4)
hlayout.addWidget(right_panel, stretch=1)
# hlayout.addItem(spacer)
main_layout.addLayout(hlayout)

window.setLayout(main_layout)

app.setWindowIcon(QIcon(str(icon_path)))

window.showMaximized()

splash.finish(window)

with open(str(QSS_PATH)) as f:
    app.setStyleSheet(f.read())
    pass

app.exec()
