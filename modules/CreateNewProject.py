import json
import os
import shutil
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
)
from PySide6.QtGui import Qt

from modules import GLOBAL

TEMPLATE_PATH = GLOBAL.APPDATA / "template"


def open_project(project_name):
    data = {
        "is_project_open": True,
        "project_name": project_name,
        "pages": ["index"]
    }

    json_data = json.dumps(data)

    with open(str(GLOBAL.open_project_file_path), "w") as f:
        f.write(json_data)


class CreateProjectDialog(QDialog):
    def __init__(self, parent=None, state=None):
        super().__init__(parent)

        self.state = state

        self.setWindowTitle("Create New Project")
        # self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setFixedWidth(320)
        self.setMaximumHeight(140)

        self.label = QLabel("Enter Project Name : ")
        self.input = QLineEdit(placeholderText="name")
        self.error_label = QLabel()
        self.error_label.setProperty("class", "error text-sm")
        self.error_label.setVisible(False)

        self.submit_button = QPushButton("Create")
        self.submit_button.clicked.connect(self.on_submit)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel)

        main_layout = QVBoxLayout()

        main_layout.addWidget(self.label)
        main_layout.addWidget(self.input)
        main_layout.addWidget(self.error_label)

        button_layout = QHBoxLayout()

        button_layout.addStretch()
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def on_submit(self):
        project_name = self.input.text().strip()

        if not project_name:
            return

        project_dir = Path(GLOBAL.USER_DIR) / project_name
        template_dir = Path(TEMPLATE_PATH)

        try:
            # 1. Copy full template
            shutil.copytree(template_dir, project_dir)

            # 2. Update project metadata file
            now = datetime.now()
            data = {
                "project_name": project_name,
                "date_created": now.strftime("%d-%m-%Y"),
                "pages": ["index"]
            }

            with open(GLOBAL.project_list_file_path, "r") as f:
                current_data = json.load(f)

            current_data.append(data)

            with open(GLOBAL.project_list_file_path, "w") as f:
                json.dump(current_data, f, indent=4)

            # 3. Open project
            open_project(project_name)
            self.state.project_name.data = project_name

            self.accept()

        except FileExistsError:
            # project already exists → just open it
            open_project(project_name)
            self.accept()

        except Exception as e:
            print(e)

            if project_dir.exists():
                shutil.rmtree(project_dir)

            self.error_label.setVisible(True)
            self.error_label.setText("Could not create project")

    def on_cancel(self):
        self.reject()
