import json
from pathlib import Path

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QToolButton, QGridLayout
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from modules import GLOBAL

img_path = Path(__file__).resolve().parent.parent / "assets" / "schema" / "html_elements"


class ElementButton(QToolButton):
    def __init__(self, label, icon):
        super().__init__()

        self.setText(label)
        self.setIcon(QIcon(icon))
        self.setIconSize(QSize(50, 50))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setFixedSize(80, 80)


class Components(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.element_button_group = []

        main_layout = QVBoxLayout()

        elements_json_data = GLOBAL.elements_data_file_path

        with open(elements_json_data, "r") as f:
            elements_data = json.load(f)

        for category in elements_data:
            label = QLabel(category["category"])
            label.setObjectName("categoryTitle")
            main_layout.addWidget(label)
            grid_layout = QGridLayout()
            button_layout = []

            for element in category["elements"]:
                icon_path = img_path / element["thumbnail"]
                btn = ElementButton(element["name"], str(icon_path))
                btn.setCheckable(True)
                btn.setProperty("markup", element["markup"])
                btn.clicked.connect(self.handle_click)
                button_layout.append(btn)
                self.element_button_group.append(btn)

            cols = 2
            for i, widget in enumerate(button_layout):
                row = i // cols
                col = i % cols
                grid_layout.addWidget(widget, row, col)

            main_layout.addLayout(grid_layout)

        self.setLayout(main_layout)

        self.state.inserting_element.data_changed.connect(self.uncheck_all_buttons)

    def uncheck_all_buttons(self, value):
        if value is None:
            for button in self.element_button_group:
                button.setChecked(False)

    def uncheck_buttons(self, btn):
        if btn.isChecked():
            #print("uncheck others")
            for button in self.element_button_group:
                if button is not btn:
                    button.setChecked(False)

        else:
            #print("uncheck all")
            self.abort_inserting()

    def handle_click(self):
        btn = self.sender()
        #print(btn)
        #print(self.sender().property("markup"))
        self.state.inserting_element.data = self.sender().property("markup")
        self.uncheck_buttons(btn)

    def abort_inserting(self):
        self.state.inserting_element.data = None
        #print(self.state.inserting_element.data)
