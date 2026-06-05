from PySide6.QtWidgets import QWidget,QVBoxLayout,QScrollArea,QFrame,QTabWidget
from PySide6.QtGui import Qt

from modules import Components
from modules import AssetManager


class CustomScroll(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)


class LeftPanel(QWidget):
    def __init__(self,state):
        super().__init__()

        #self.setVisible(True)
        self.setObjectName("LeftPanel")
        self.state = state

        self.main_layout = QVBoxLayout()

        tab_switch = QTabWidget()

        component_list = Components.Components(state)
        asset_manager = AssetManager.AssetManager(state)

        self.scroll_area = CustomScroll()
        self.scroll_area_2 = CustomScroll()

        self.scroll_area.setWidget(component_list)
        self.scroll_area_2.setWidget(asset_manager)

        tab_switch.addTab(self.scroll_area, "Component")
        tab_switch.addTab(self.scroll_area_2, "Assets")

        self.main_layout.addWidget(tab_switch)
        self.setLayout(self.main_layout)





