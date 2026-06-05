"""
import json

from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QPushButton



class AppSettings(QWidget):
    def __init__(self):
        super().__init__()
        self.setVisible(True)
        self.main_layout = QVBoxLayout()

        self.main_layout.addWidget(QLabel("Settings"))

        with open(GLOBAL.app_settings_file_path) as f:
            settings_data = json.load(f)

        for setting , value in settings_data.items():
            field = QHBoxLayout()
            field.addWidget(QLabel(setting))
            field.addWidget(QLineEdit(value))

            self.main_layout.addLayout(field)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(QPushButton("Save"))

        self.main_layout.addLayout(btn_layout)

"""


import json
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QCheckBox, QSpinBox, QDoubleSpinBox,
    QPushButton, QFileDialog, QScrollArea, QComboBox,
    QMessageBox, QFrame, QListWidget, QListWidgetItem, QSplitter
)
from PySide6.QtCore import Qt

from modules import GLOBAL


class SettingsGUI(QMainWindow):
    def __init__(self, json_file_path):
        super().__init__()
        self.json_file_path = json_file_path
        self.settings_data = {}
        self.widgets = {}
        self.current_section = None

        self.setWindowTitle("Settings")
        self.setMinimumSize(900, 650)

        self.apply_vscode_style()
        self.init_ui()
        self.load_settings()

    def apply_vscode_style(self):
        """Apply VS Code-inspired styling"""
        style = """
        QMainWindow {
            background-color: #1e1e1e;
        }

        QWidget {
            background-color: #1e1e1e;
            color: #cccccc;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
        }

        /* Sidebar */
        QListWidget {
            background-color: #252526;
            border: none;
            outline: none;
            padding: 8px 0;
        }

        QListWidget::item {
            padding: 10px 20px;
            color: #cccccc;
            border-left: 2px solid transparent;
        }

        QListWidget::item:hover {
            background-color: #2a2d2e;
        }

        QListWidget::item:selected {
            background-color: #37373d;
            border-left: 2px solid #007acc;
            color: #ffffff;
        }

        /* Search bar */
        QLineEdit#searchBar {
            background-color: #3c3c3c;
            border: 1px solid #3c3c3c;
            border-radius: 4px;
            padding: 8px 12px;
            color: #cccccc;
            font-size: 13px;
        }

        QLineEdit#searchBar:focus {
            border: 1px solid #007acc;
            background-color: #404040;
        }

        /* Regular input fields */
        QLineEdit {
            background-color: #3c3c3c;
            border: 1px solid #3c3c3c;
            padding: 6px 8px;
            color: #cccccc;
            border-radius: 2px;
        }

        QLineEdit:focus {
            border: 1px solid #007acc;
        }

        QLineEdit:hover {
            border: 1px solid #505050;
        }

        /* SpinBox */
        QSpinBox, QDoubleSpinBox {
            background-color: #3c3c3c;
            border: 1px solid #3c3c3c;
            padding: 6px 8px;
            color: #cccccc;
            border-radius: 2px;
        }

        QSpinBox:focus, QDoubleSpinBox:focus {
            border: 1px solid #007acc;
        }

        QSpinBox:hover, QDoubleSpinBox:hover {
            border: 1px solid #505050;
        }

        QSpinBox::up-button, QDoubleSpinBox::up-button,
        QSpinBox::down-button, QDoubleSpinBox::down-button {
            background-color: transparent;
            border: none;
            width: 16px;
        }

        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
            background-color: #505050;
        }

        /* ComboBox */
        QComboBox {
            background-color: #3c3c3c;
            border: 1px solid #3c3c3c;
            padding: 6px 8px;
            color: #cccccc;
            border-radius: 2px;
            min-width: 150px;
        }

        QComboBox:focus {
            border: 1px solid #007acc;
        }

        QComboBox:hover {
            border: 1px solid #505050;
        }

        QComboBox::drop-down {
            border: none;
            width: 20px;
        }

        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid #cccccc;
            margin-right: 6px;
        }

        QComboBox QAbstractItemView {
            background-color: #3c3c3c;
            border: 1px solid #454545;
            selection-background-color: #094771;
            selection-color: #ffffff;
            outline: none;
        }

        /* CheckBox */
        QCheckBox {
            spacing: 8px;
            color: #cccccc;
        }

        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            background-color: #3c3c3c;
            border: 1px solid #3c3c3c;
            border-radius: 2px;
        }

        QCheckBox::indicator:hover {
            border: 1px solid #505050;
            background-color: #404040;
        }

        QCheckBox::indicator:checked {
            background-color: #007acc;
            border: 1px solid #007acc;
        }

        QCheckBox::indicator:checked:hover {
            background-color: #005a9e;
            border: 1px solid #005a9e;
        }

        /* Buttons */
        QPushButton {
            background-color: #0e639c;
            color: #ffffff;
            border: none;
            padding: 8px 16px;
            border-radius: 2px;
            font-weight: 500;
        }

        QPushButton:hover {
            background-color: #1177bb;
        }

        QPushButton:pressed {
            background-color: #005a9e;
        }

        QPushButton#browseButton {
            background-color: #3c3c3c;
            color: #cccccc;
            padding: 6px 12px;
            border: 1px solid #3c3c3c;
        }

        QPushButton#browseButton:hover {
            background-color: #505050;
            border: 1px solid #505050;
        }

        QPushButton#browseButton:pressed {
            background-color: #404040;
        }

        /* Labels */
        QLabel {
            color: #cccccc;
        }

        QLabel#sectionTitle {
            color: #ffffff;
            font-size: 20px;
            font-weight: 600;
        }

        QLabel#settingLabel {
            color: #cccccc;
            font-size: 13px;
        }

        QLabel#settingDescription {
            color: #858585;
            font-size: 12px;
        }

        /* ScrollArea */
        QScrollArea {
            border: none;
            background-color: #1e1e1e;
        }

        QScrollBar:vertical {
            background-color: #1e1e1e;
            width: 14px;
            border: none;
        }

        QScrollBar::handle:vertical {
            background-color: #424242;
            min-height: 30px;
            border-radius: 7px;
            margin: 2px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #4f4f4f;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }

        /* Splitter */
        QSplitter::handle {
            background-color: #2d2d30;
            width: 1px;
        }

        /* Separator line */
        QFrame#separator {
            background-color: #2d2d30;
            max-height: 1px;
        }
        """

        self.setStyleSheet(style)

    def init_ui(self):
        """Initialize the VS Code-style UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top search bar
        search_container = QWidget()
        search_container.setStyleSheet("background-color: #252526; padding: 12px 20px;")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(20, 12, 20, 12)

        self.search_box = QLineEdit()
        self.search_box.setObjectName("searchBar")
        self.search_box.setPlaceholderText("Search settings")
        self.search_box.textChanged.connect(self.filter_settings)
        search_layout.addWidget(self.search_box)

        #main_layout.addWidget(search_container)

        # Splitter for sidebar and content
        splitter = QSplitter(Qt.Horizontal)

        # Left sidebar - categories
        self.category_list = QListWidget()
        self.category_list.setMaximumWidth(250)
        self.category_list.setMinimumWidth(200)
        self.category_list.currentRowChanged.connect(self.on_category_changed)

        splitter.addWidget(self.category_list)

        # Right content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.settings_container = QWidget()
        self.settings_layout = QVBoxLayout(self.settings_container)
        self.settings_layout.setContentsMargins(40, 30, 40, 30)
        self.settings_layout.setSpacing(20)

        scroll.setWidget(self.settings_container)
        content_layout.addWidget(scroll)

        # Bottom save button
        button_container = QWidget()
        button_container.setStyleSheet("background-color: #252526; border-top: 1px solid #2d2d30;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(40, 12, 40, 12)

        button_layout.addStretch()
        self.save_button = QPushButton("Save Settings")
        self.save_button.setMinimumWidth(120)
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)

        content_layout.addWidget(button_container)

        splitter.addWidget(content_widget)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

    def load_settings(self):
        """Load settings from JSON file"""
        try:
            with open(self.json_file_path, 'r') as f:
                self.settings_data = json.load(f)
            self.populate_categories()
            if self.settings_data:
                self.category_list.setCurrentRow(0)
        except FileNotFoundError:
            QMessageBox.warning(self, "Error", f"File not found: {self.json_file_path}")
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Error", "Invalid JSON file")

    def populate_categories(self):
        """Populate the category sidebar"""
        self.category_list.clear()
        for section_name in self.settings_data.keys():
            item = QListWidgetItem(section_name.replace('_', ' ').title())
            item.setData(Qt.UserRole, section_name)
            self.category_list.addItem(item)

    def on_category_changed(self, index):
        """Handle category selection change"""
        if index < 0:
            return

        item = self.category_list.item(index)
        section_name = item.data(Qt.UserRole)
        self.current_section = section_name
        self.display_section(section_name)

    def display_section(self, section_name):
        """Display settings for a specific section"""
        # Clear existing widgets
        for i in reversed(range(self.settings_layout.count())):
            widget = self.settings_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if section_name not in self.settings_data:
            return

        # Section title
        title = QLabel(section_name.replace('_', ' ').title())
        title.setObjectName("sectionTitle")
        self.settings_layout.addWidget(title)

        # Add spacing
        self.settings_layout.addSpacing(10)

        # Add settings
        section_data = self.settings_data[section_name]
        for key, value in section_data.items():
            setting_widget = self.create_setting_row(section_name, key, value)
            if setting_widget:
                self.settings_layout.addWidget(setting_widget)

                # Add separator
                separator = QFrame()
                separator.setObjectName("separator")
                separator.setFrameShape(QFrame.HLine)
                self.settings_layout.addWidget(separator)

        self.settings_layout.addStretch()

    def filter_settings(self, text):
        """Filter settings based on search text"""
        # This is a simple implementation - you can enhance it
        search_text = text.lower()

        if not search_text:
            # Show all categories
            for i in range(self.category_list.count()):
                self.category_list.item(i).setHidden(False)
            return

        # Hide/show categories based on search
        for i in range(self.category_list.count()):
            item = self.category_list.item(i)
            section_name = item.data(Qt.UserRole)

            # Check if section name matches
            if search_text in section_name.lower():
                item.setHidden(False)
                continue

            # Check if any setting key matches
            section_data = self.settings_data.get(section_name, {})
            matches = any(search_text in key.lower() for key in section_data.keys())
            item.setHidden(not matches)

    def create_setting_row(self, section, key, value):
        """Create a VS Code-style setting row"""
        row_widget = QWidget()
        row_layout = QVBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 8, 0, 8)
        row_layout.setSpacing(6)

        # Setting name and control layout
        control_layout = QHBoxLayout()
        control_layout.setSpacing(12)

        # Label
        label = QLabel(key.replace('_', ' ').title())
        label.setObjectName("settingLabel")
        label.setMinimumWidth(250)
        control_layout.addWidget(label)

        # Create appropriate widget
        widget = None
        full_key = f"{section}.{key}"

        # Path fields
        if self.is_path_field(key, value):
            widget = self.create_path_widget(value)

        # Boolean
        elif isinstance(value, bool):
            widget = QCheckBox()
            widget.setChecked(value)
            widget.setCursor(Qt.PointingHandCursor)

        # Integer
        elif isinstance(value, int) and not isinstance(value, bool):
            widget = QSpinBox()
            widget.setRange(-999999, 999999)
            widget.setValue(value)
            widget.setMinimumWidth(120)
            widget.setMaximumWidth(200)

        # Float
        elif isinstance(value, float):
            widget = QDoubleSpinBox()
            widget.setRange(-999999.99, 999999.99)
            widget.setValue(value)
            widget.setMinimumWidth(120)
            widget.setMaximumWidth(200)

        # Theme
        elif key == "theme":
            widget = QComboBox()
            widget.addItems(["light", "dark", "auto"])
            widget.setCurrentText(str(value))
            widget.setCursor(Qt.PointingHandCursor)

        # Language
        elif key == "language":
            widget = QComboBox()
            widget.addItems(["en-US", "es-ES", "fr-FR", "de-DE", "zh-CN", "ja-JP"])
            widget.setCurrentText(str(value))
            widget.setEditable(True)
            widget.setCursor(Qt.PointingHandCursor)

        # String
        elif isinstance(value, str):
            widget = QLineEdit()
            widget.setText(value)
            widget.setMaximumWidth(400)

        else:
            widget = QLineEdit()
            widget.setText(str(value))
            widget.setMaximumWidth(400)

        if widget:
            control_layout.addWidget(widget)
            control_layout.addStretch()
            self.widgets[full_key] = widget

        row_layout.addLayout(control_layout)

        # Add description based on key
        description = self.get_setting_description(key, value)
        if description:
            desc_label = QLabel(description)
            desc_label.setObjectName("settingDescription")
            desc_label.setWordWrap(True)
            desc_label.setContentsMargins(0, 0, 0, 0)
            row_layout.addWidget(desc_label)

        return row_widget

    def get_setting_description(self, key, value):
        """Get description for a setting"""
        descriptions = {
            "default_save_dir": "Default directory for saving files",
            "auto_save": "Automatically save changes",
            "auto_save_interval_seconds": "Time interval between auto-saves (in seconds)",
            "backup_enabled": "Create backup copies of files",
            "backup_dir": "Directory where backups are stored",
            "theme": "Color theme for the application",
            "font_size": "Size of the text font",
            "font_family": "Font family to use in the application",
            "compact_mode": "Use compact UI layout",
            "enabled": "Enable notifications",
            "sound": "Play sound with notifications",
            "notify_on_save": "Show notification when files are saved",
            "language": "Application language",
            "start_on_boot": "Launch application when system starts",
            "check_for_updates": "Automatically check for software updates"
        }
        return descriptions.get(key, "")

    def is_path_field(self, key, value):
        """Determine if a field represents a file/directory path"""
        path_keywords = ['dir', 'directory', 'path', 'folder']

        # Check if key contains path-related keywords
        key_lower = key.lower()
        if any(keyword in key_lower for keyword in path_keywords):
            return True

        # Check if value looks like a path
        if isinstance(value, str) and ('\\' in value or '/' in value):
            return True

        return False

    def create_path_widget(self, value):
        """Create a path selector widget with browse button"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        line_edit = QLineEdit()
        line_edit.setText(str(value))
        line_edit.setMaximumWidth(400)
        layout.addWidget(line_edit)

        browse_button = QPushButton("Browse...")
        browse_button.setObjectName("browseButton")
        browse_button.setMaximumWidth(100)
        browse_button.setCursor(Qt.PointingHandCursor)
        browse_button.clicked.connect(lambda: self.browse_path(line_edit))
        layout.addWidget(browse_button)

        # Store the line_edit as the main widget reference
        container.line_edit = line_edit

        return container

    def browse_path(self, line_edit):
        """Open file dialog to browse for directory"""
        current_path = line_edit.text()

        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            current_path if current_path else str(Path.home()),
            QFileDialog.ShowDirsOnly
        )

        if directory:
            line_edit.setText(directory)

    def get_widget_value(self, widget):
        """Get value from widget based on its type"""
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            return widget.value()
        elif isinstance(widget, QLineEdit):
            return widget.text()
        elif isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QWidget) and hasattr(widget, 'line_edit'):
            # Path widget
            return widget.line_edit.text()
        return None

    def save_settings(self):
        """Save current settings back to JSON file"""
        # Update settings_data with current widget values
        for full_key, widget in self.widgets.items():
            section, key = full_key.split('.')
            value = self.get_widget_value(widget)

            # Convert value to appropriate type based on original type
            original_value = self.settings_data[section][key]
            if isinstance(original_value, bool):
                value = bool(value)
            elif isinstance(original_value, int) and not isinstance(original_value, bool):
                value = int(value)
            elif isinstance(original_value, float):
                value = float(value)

            self.settings_data[section][key] = value

        # Write to JSON file
        try:
            with open(self.json_file_path, 'w') as f:
                json.dump(self.settings_data, f, indent=2)

            QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")

        except Exception as e:
            QMessageBox.critical(self, "Error Saving Settings", f"Failed to save settings:\n{str(e)}")


def main():
    app = QApplication(sys.argv)

    # Path to your JSON settings file
    json_file = GLOBAL.app_settings_file_path  # Change this to your file path

    window = SettingsGUI(json_file)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()


