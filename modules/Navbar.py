import json
import sys
import os

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QMenuBar, QWidget, QVBoxLayout
from PySide6.QtGui import QAction

from modules import CreateNewProject
from modules import GLOBAL
from modules.FolderBrowser import StaticFolderBrowser


MENU_DATA = GLOBAL.APPDATA / "menu.json"


def open_documentation():
    pass


def close_app():
    sys.exit()


def new_project(state, parent=None):
    #print("action")
    dialog = CreateNewProject.CreateProjectDialog(parent, state)

    if dialog.exec():
        print("dialog Opened")

    else:
        print("dialog cancelled")


def open_project(state, parent=None):
    open_project_window = StaticFolderBrowser(root_path=GLOBAL.USER_DIR, parent=parent)

    def handle_selection(selected_path):
        # Extract just the folder name from the full path
        folder_name = os.path.basename(selected_path)

        # Print only the folder name
        #print(f"User confirmed selection: {folder_name}")

        GLOBAL.open_project(folder_name)
        state.project_name.data = folder_name
        print(state.project_name)

    open_project_window.folder_selected.connect(handle_selection)

    open_project_window.show()


def open_local_html():
    file_path = GLOBAL.USER_DIR / GLOBAL.open_project_name() / "index.html"
    print(file_path)
    url = QUrl.fromLocalFile(file_path)
    QDesktopServices.openUrl(url)


def export_code(state):
    state.export_code.data = True


class Navbar(QWidget):
    def __init__(self, state, parent=None):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        menubar = QMenuBar()
        layout.addWidget(menubar)

        self.setLayout(layout)
        with open(MENU_DATA, "r") as f:
            data = json.load(f)

        for item in data["menu"]:
            menu = menubar.addMenu(item["label"])
            for option in item["options"]:
                action = QAction(option, self)
                menu.addAction(action)
                # print(option)
                if option == "New Project":
                    #print(option)
                    action.triggered.connect(lambda: new_project(state, parent))
                if option == "Open Project":
                    #print(option)
                    action.triggered.connect(lambda: open_project(state, parent))
                if option == "Close":
                    action.triggered.connect(close_app)
                if option == "Open in Browser":
                    action.triggered.connect(open_local_html)
                if option == "Export Code":
                    action.triggered.connect(lambda: export_code(state))

        """
        # Create menus
        file_menu = menubar.addMenu("File")
        edit_menu = menubar.addMenu("Edit")
        view_menu = menubar.addMenu("View")
        help_menu = menubar.addMenu("Help")

        # File menu actions
        new_action = QAction("New File", self)
        open_action = QAction("Open", self)
        save_action = QAction("Save", self)
        exit_action = QAction("Exit", self)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)

        # Submenu
        export_sub = file_menu.addMenu("Export")
        export_sub.addAction("Export as PDF")
        export_sub.addAction("Export as Image")

        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Edit menu actions
        edit_menu.addAction("Undo")
        edit_menu.addAction("Redo")
        edit_menu.addSeparator()
        edit_menu.addAction("Cut")
        edit_menu.addAction("Copy")
        edit_menu.addAction("Paste")

        # View menu actions
        view_menu.addAction("Toggle Sidebar")
        view_menu.addAction("Toggle Fullscreen")

        # Help menu actions
        help_menu.addAction("About")
        doc_action = QAction("Documentation", self)
        help_menu.addAction(doc_action)

        doc_action.triggered.connect(open_documentation)
        """
