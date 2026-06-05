from pathlib import Path
import shutil

from PySide6.QtWidgets import (
    QWidget, QFileDialog, QToolButton, QVBoxLayout, QListWidgetItem,
    QListWidget, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QIcon

from modules import GLOBAL


class SelectImage(QToolButton):
    image_selected = Signal()

    def __init__(self, assets_path):
        super().__init__()
        self.setText("Select Image")
        self.assets_path = assets_path
        # self.setIcon(QIcon(icon))
        # self.setIconSize(QSize(50, 50))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setFixedSize(80, 80)
        self.image_path = None
        self.clicked.connect(self.select_image)

    def select_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )

        if path:
            # print(Path(path).name)
            return Path(path).name


class AssetDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.assets_path = GLOBAL.USER_DIR / GLOBAL.open_project_name() / "assets"
        self.layout = QVBoxLayout()
        self.add_btn = SelectImage(self.assets_path)
        self.add_btn.image_selected.connect(self.display_images)
        self.layout.addWidget(self.add_btn)

        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(80, 80))

        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setFlow(QListWidget.TopToBottom)
        self.list_widget.setWrapping(True)
        self.list_widget.setResizeMode(QListWidget.Adjust)

        self.list_widget.setGridSize(QSize(80, 80))
        self.list_widget.setIconSize(QSize(80, 80))

        self.list_widget.itemClicked.connect(self.on_item_clicked)

        self.layout.addWidget(self.list_widget)

        self.setLayout(self.layout)

        self.display_images()

    def on_item_clicked(self, item):
        print(item.text())

    def display_images(self):
        paths = self.all_images()

        self.list_widget.clear()

        if paths:
            for path in paths:
                pixmap = QPixmap(str(path))

                if pixmap.isNull():
                    continue

                icon = QIcon(pixmap.scaled(80, 80))

                item = QListWidgetItem(icon, path.name)  # cleaner label
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                item.setToolTip(str(path))  # full path on hover
                self.list_widget.addItem(item)

    def all_images(self):
        try:
            folder_path = Path(self.assets_path)

            if not folder_path.exists():
                return []

            image_extensions = {
                ".jpg", ".jpeg", ".png", ".gif",
                ".bmp", ".tiff", ".webp"
            }

            return [
                p for p in folder_path.iterdir()
                if p.suffix.lower() in image_extensions and p.is_file()
            ]

        except Exception as e:
            print("Error loading images:", e)
            return []


class UploadImage(QToolButton):
    images_added = Signal()

    def __init__(self, assets_path):
        super().__init__()
        self.setText("Add Image")
        self.assets_path = assets_path
        # self.setIcon(QIcon(icon))
        # self.setIconSize(QSize(50, 50))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setFixedSize(80, 80)
        self.image_path = None
        self.clicked.connect(self.select_image)

    def select_image(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )

        if paths:  # already a list
            for path in paths:
                print(path)
                self.copy_images(path)

        self.images_added.emit()

    def copy_images(self, path):
        source = Path(path)
        destination_dir = Path(self.assets_path)

        destination_dir.mkdir(parents=True, exist_ok=True)

        shutil.copy(source, destination_dir / source.name)


class AssetManager(QWidget):
    def __init__(self, state):
        super().__init__()
        self.assets_path = GLOBAL.USER_DIR / GLOBAL.open_project_name() / "assets"
        self.state = state
        self.layout = QVBoxLayout()
        self.add_btn = UploadImage(self.assets_path)
        self.add_btn.images_added.connect(self.display_images)
        self.layout.addWidget(self.add_btn)

        ICON_SIZE = 80
        SPACING = 4
        PADDING = 8

        COLS = 2
        GRID_W = ICON_SIZE + SPACING * 2
        GRID_H = ICON_SIZE + 20

        total_width = COLS * GRID_W + PADDING * 2

        self.list_widget = QListWidget()
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setFlow(QListWidget.LeftToRight)
        self.list_widget.setWrapping(True)
        self.list_widget.setResizeMode(QListWidget.Fixed)
        self.list_widget.setUniformItemSizes(True)
        self.list_widget.setSpacing(SPACING)
        self.list_widget.setGridSize(QSize(GRID_W, GRID_H))
        self.list_widget.setIconSize(QSize(ICON_SIZE, ICON_SIZE))

        self.list_widget.setFixedWidth(total_width)
        self.list_widget.setMinimumHeight(GRID_H)  # at least 1 row visible
        self.list_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.layout.addWidget(self.list_widget)

        self.setLayout(self.layout)

        self.display_images()

        self.state.project_name.data_changed.connect(self.update_project_name)

    def on_item_clicked(self, item):
        print(item.text())

    def display_images(self):
        paths = self.all_images()

        self.list_widget.clear()

        if paths:
            for path in paths:
                pixmap = QPixmap(str(path))

                if pixmap.isNull():
                    continue

                icon = QIcon(pixmap.scaled(80, 80))

                item = QListWidgetItem(icon, path.name)  # cleaner label

                item.setToolTip(str(path))  # full path on hover
                item.setFlags(Qt.ItemIsEnabled)
                self.list_widget.addItem(item)

        #self.list_widget.itemClicked.connect(self.on_item_clicked)

    def all_images(self):
        try:
            folder_path = Path(self.assets_path)

            if not folder_path.exists():
                return []

            image_extensions = {
                ".jpg", ".jpeg", ".png", ".gif",
                ".bmp", ".tiff", ".webp"
            }

            return [
                p for p in folder_path.iterdir()
                if p.suffix.lower() in image_extensions and p.is_file()
            ]

        except Exception as e:
            print("Error loading images:", e)
            return []

    def update_project_name(self):
        self.assets_path = GLOBAL.USER_DIR / GLOBAL.open_project_name() / "assets"
        self.display_images()
