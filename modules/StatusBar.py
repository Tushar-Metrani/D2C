from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSpacerItem
from PySide6.QtCore import Qt

from modules import GLOBAL

spacer = QSpacerItem(120, 1)


class StatusBar(QWidget):
    def __init__(self, state):
        super().__init__()

        self.setObjectName("statusbar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.state = state

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(25, 5, 25, 5)
        self.main_layout.setSpacing(8)

        self.project_name = QLabel(GLOBAL.open_project_name())
        self.main_layout.addWidget(self.project_name)
        self.main_layout.addItem(spacer)


        self.pages = GLOBAL.open_project_pages()
        """
        for page in self.pages:
            btn = QPushButton(page)
            btn.setProperty("class", "tab-btn")
            self.main_layout.addWidget(btn)
            
        """

        self.save_page_btn = QPushButton("Save Page")
        self.save_project_btn = QPushButton("Save Project")

        self.save_page_btn.clicked.connect(self.save_page)

        self.main_layout.addStretch()
        self.main_layout.addWidget(self.save_page_btn)
        self.main_layout.addWidget(self.save_project_btn)

        self.setLayout(self.main_layout)

        self.state.project_name.data_changed.connect(self.update_project_name)

    def save_page(self):
        self.state.saved.data = True
        #print("button clicked")
        #print(self.state.saved.data)

    def update_project_name(self,value):
        #print(value)
        self.project_name.setText(value)
