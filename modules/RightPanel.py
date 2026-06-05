from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from PySide6.QtCore import Qt

from modules import Property


class RightPanel(QWidget):

    def __init__(self, state):
        super().__init__()

        self.setObjectName("RightPanel")
        self.main_layout = QVBoxLayout()

        self.property_tab = Property.Property(state)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        self.scroll_area.setWidget(self.property_tab)

        self.main_layout.addWidget(self.scroll_area)

        self.setLayout(self.main_layout)



