import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QPushButton, QFrame
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QColor
from modules import GLOBAL


class StaticFolderBrowser(QWidget):
    # Custom signal emitted when a folder is chosen
    folder_selected = Signal(str)

    def __init__(self, root_path: str, parent=None):
        super().__init__(parent)
        self.root_path = root_path
        self.selected_folder = None

        # Hide standard window controls and title bar
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

        self.setup_ui()
        self.load_folders(self.root_path)

    def setup_ui(self):
        self.resize(480, 520)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
            }
            QLabel#title {
                color: #cdd6f4;
                font-size: 18px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            QLabel#subtitle {
                color: #6c7086;
                font-size: 12px;
                margin-top: 5px;
            }
            QListWidget#folder_list {
                background-color: #181825;
                color: #cdd6f4;
                border: 1px solid #313244;
                border-radius: 10px;
                font-size: 14px;
                outline: none;
                padding: 4px;
            }
            QListWidget#folder_list::item {
                padding: 10px 14px;
                border-radius: 6px;
                margin: 2px 4px;
            }
            QListWidget#folder_list::item:hover {
                background-color: #313244;
            }
            QListWidget#folder_list::item:selected {
                background-color: #45475a;
                color: #89b4fa;
            }
            QFrame#separator {
                background-color: #313244;
            }
            QPushButton#select_btn {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#select_btn:hover {
                background-color: #b4befe;
            }
            QPushButton#select_btn:disabled {
                background-color: #313244;
                color: #6c7086;
            }
            QPushButton#cancel_btn {
                background-color: transparent;
                color: #6c7086;
                border: 1px solid #313244;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
            }
            QPushButton#cancel_btn:hover {
                background-color: #313244;
                color: #cdd6f4;
                border-color: #45475a;
            }
        """)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(12)

        # --- Header ---

        title = QLabel(f"📁  Open Project")
        title.setObjectName("title")
        root_layout.addWidget(title)

        # Separator
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFixedHeight(1)
        root_layout.addWidget(sep)

        # --- Folder List ---
        self.folder_list = QListWidget()
        self.folder_list.setObjectName("folder_list")
        self.folder_list.setIconSize(QSize(20, 20))
        self.folder_list.itemSelectionChanged.connect(self.on_selection_changed)
        # Double-clicking still works as a quick-select
        self.folder_list.itemDoubleClicked.connect(self.confirm_selection)
        root_layout.addWidget(self.folder_list, stretch=1)

        # --- Footer Buttons ---
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()  # Pushes buttons to the right

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.setFixedWidth(100)
        self.cancel_btn.clicked.connect(self.close)

        self.select_btn = QPushButton("Select")
        self.select_btn.setObjectName("select_btn")
        self.select_btn.setFixedWidth(120)
        self.select_btn.setEnabled(False)  # Disabled by default
        self.select_btn.clicked.connect(self.confirm_selection)

        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.select_btn)
        root_layout.addLayout(btn_row)

    def load_folders(self, path):
        self.folder_list.clear()
        self.selected_folder = None
        self.select_btn.setEnabled(False)

        try:
            entries = sorted(
                [e for e in os.scandir(path) if e.is_dir()],
                key=lambda e: e.name.lower()
            )
        except PermissionError:
            return

        if not entries:
            item = QListWidgetItem("  (No subfolders found)")
            item.setForeground(QColor("#6c7086"))
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.folder_list.addItem(item)
        else:
            for entry in entries:
                item = QListWidgetItem(f"  📂  {entry.name}")
                item.setData(Qt.UserRole, entry.path)
                self.folder_list.addItem(item)

    def on_selection_changed(self):
        items = self.folder_list.selectedItems()
        if items:
            path = items[0].data(Qt.UserRole)
            if path:
                self.selected_folder = path
                self.select_btn.setEnabled(True)
        else:
            self.selected_folder = None
            self.select_btn.setEnabled(False)

    def confirm_selection(self, item=None):
        # Allow passing an item directly from double-click, or use selected_folder
        path_to_emit = item.data(Qt.UserRole) if item else self.selected_folder

        if path_to_emit:
            self.folder_selected.emit(path_to_emit)
            self.close()

    def keyPressEvent(self, event):
        # Escape key closes the window
        if event.key() == Qt.Key_Escape:
            self.close()
        # Enter key triggers selection if a folder is chosen
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter) and self.selected_folder:
            self.confirm_selection()
        super().keyPressEvent(event)


# --- Example Usage ---
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    target_path = GLOBAL.USER_DIR
    browser = StaticFolderBrowser(root_path=target_path)

    def handle_selection(selected_path):
        print(f"User confirmed selection: {selected_path}")
        app.quit()

    browser.folder_selected.connect(handle_selection)
    browser.destroyed.connect(app.quit)

    browser.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
