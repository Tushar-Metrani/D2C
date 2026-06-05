from PySide6.QtWidgets import \
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QApplication, QSizePolicy
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from pathlib import Path
from modules import GLOBAL
import math


class AssetListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._cols = 2
        self._icon_size = 80
        self._spacing = 4

        grid_w = self._icon_size + self._spacing * 2
        grid_h = self._icon_size + 20

        self.setViewMode(QListWidget.IconMode)
        self.setFlow(QListWidget.LeftToRight)
        self.setWrapping(True)
        self.setResizeMode(QListWidget.Fixed)
        self.setUniformItemSizes(True)
        self.setSpacing(self._spacing)
        self.setGridSize(QSize(grid_w, grid_h))
        self.setIconSize(QSize(self._icon_size, self._icon_size))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._fixed_width = 0
        self._update_width()

    def _update_width(self):
        grid_w = self._icon_size + self._spacing * 2
        frame = self.frameWidth() * 2
        self._fixed_width = self._cols * grid_w + self._spacing + frame
        self.setFixedWidth(self._fixed_width)

    # call after widget is shown, frame metrics are only accurate then
    def showEvent(self, event):
        super().showEvent(event)
        self._update_width()
        self.updateGeometry()

    def sizeHint(self):
        count = self.count()
        rows = max(1, math.ceil(count / self._cols))
        grid_h = self.gridSize().height()
        frame = self.frameWidth() * 2
        height = rows * (grid_h + self._spacing) + self._spacing + frame
        return QSize(self._fixed_width, height)

    def minimumSizeHint(self):
        return self.sizeHint()


class ImageInput(QWidget):
    data_changed = Signal(object)

    def __init__(self, url=False):
        super().__init__()
        self.assets_path = GLOBAL.default_save_path() / GLOBAL.open_project_name() / "assets"
        self.image_name = None
        self.with_url = url

        self.main_layout = QVBoxLayout()

        self.select_image_btn = QPushButton("Select Image")
        self.remove_image_btn = QPushButton("Remove")

        self.btn_layout = QVBoxLayout()
        self.btn_layout.addWidget(self.select_image_btn)
        self.btn_layout.addWidget(self.remove_image_btn)

        self.select_image_btn.clicked.connect(self.show_list)
        self.remove_image_btn.clicked.connect(self.clear_image)

        ICON_SIZE = 80
        SPACING = 4
        PADDING = 8

        COLS = 2
        GRID_W = ICON_SIZE + SPACING * 2
        GRID_H = ICON_SIZE + 20

        total_width = COLS * GRID_W + PADDING * 2

        self.list_widget = AssetListWidget()

        """
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
        
        """

        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.display_images()
        self.list_widget.hide()

        self.main_layout.addLayout(self.btn_layout)
        self.main_layout.addWidget(self.list_widget)

        self.setLayout(self.main_layout)

    def on_item_clicked(self, item):
        self.image_name = item.text()
        if self.with_url:
            url_form = f"url('assets/{self.image_name}')"
            self.data_changed.emit(url_form)
        else:
            self.data_changed.emit(self.image_name)
        # print(self.image_name)
        if self.parent():
            self.parent().adjustSize()
        self.list_widget.hide()

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
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                # item.setCheckState(Qt.Unchecked)
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

    def clear_image(self):
        self.image_name = ""
        self.data_changed.emit(self.image_name)

    def refresh_widget(self):
        self.assets_path = GLOBAL.default_save_path() / GLOBAL.open_project_name() / "assets"

    def set_img(self, value):
        if self.image_name != value:
            self.image_name = value
            self.data_changed.emit(value)

    def show_list(self):
        self.display_images()
        self.list_widget.show()
        if self.parent():
            self.parent().adjustSize()

"""
app = QApplication([])

main = QWidget()

widget = ImageInput()

layout = QVBoxLayout()
layout.addWidget(widget)

main.setLayout(layout)

main.show()

app.exec()
"""
