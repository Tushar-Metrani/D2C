import json

from PySide6.QtWidgets import QWidget,QHBoxLayout, QLabel, QLineEdit, QFormLayout, QComboBox, QToolButton, QSizePolicy
from PySide6.QtGui import QIcon

from modules import GLOBAL
from modules.custom_inputs import ImageInput
from modules.custom_inputs.UnitInput import *
from modules.custom_inputs.ColorInput import ColorInputWidget

styling_struct = GLOBAL.styling_struct_file_path

icon = QIcon(str(GLOBAL.assets_path / "schema" / "styling_icons" / "align_center.svg"))

text_elements = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "a"]


class Property(QWidget):

    def __init__(self, state):
        super().__init__()

        self.style = ""
        self.class_name = None
        self.style_dict = {}
        self.widgets = []

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )

        self.form_layout = QFormLayout()
        self.form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        #self.form_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)

        self.setLayout(self.form_layout)

        self.state = state

        self.element_name_label = QLabel("None")

        self.element_name_label.setObjectName("elementName")

        self.form_layout.addRow(self.element_name_label)

        # class

        self.selector = QLineEdit(self.state.class_name.data)
        self.selector.textChanged.connect(self.update_class_name)

        self.form_layout.addRow(QLabel("style selector"), self.selector)

        # text content

        self.text_content = QLineEdit(self.state.text_content.data)
        self.text_content.textChanged.connect(self.update_text_content)
        self.text_content_label = QLabel("Text")
        self.form_layout.addRow(self.text_content_label)
        self.form_layout.addRow(self.text_content)

        if self.element_name_label.text() not in text_elements:
            self.text_content.hide()
            self.text_content_label.hide()

        # image

        self.select_image_label = QLabel("Image")
        self.select_image = ImageInput.ImageInput()
        self.select_image.data_changed.connect(self.set_image)

        self.form_layout.addRow(self.select_image_label)
        self.form_layout.addRow(self.select_image)

        if self.element_name_label.text() != "img":
            self.select_image.hide()
            self.select_image_label.hide()

        # Displaying common styling struct

        with open(str(styling_struct), "r") as f:
            data = json.load(f)

        for i, j in data.items():
            category_label = QLabel(i)
            category_label.setObjectName("categoryTitle")
            self.form_layout.addRow(category_label)
            for row in j:
                label = QLabel(row["name"])

                if row["input_type"] == "combo":
                    dropdown = QComboBox()
                    dropdown.setProperty("style_name", row["name"])
                    dropdown.setProperty("input_type", row["input_type"])
                    dropdown.addItems(row["options"])
                    dropdown.setCurrentIndex(-1)
                    dropdown.currentTextChanged.connect(self.update_style)
                    self.widgets.append(dropdown)
                    self.form_layout.addRow(label, dropdown)

                if row["input_type"] == "lineedit":
                    text_input = QLineEdit(row["value"])
                    text_input.setProperty("style_name", row["name"])
                    text_input.setProperty("input_type", row["input_type"])
                    text_input.textChanged.connect(self.update_style)
                    self.widgets.append(text_input)
                    self.form_layout.addRow(label, text_input)

                """
                if row["input_type"] == "color":
                    color_input = ColorButton()
                    color_input.label.setText(label.text())
                    color_input.setProperty("style_name", row["name"])
                    color_input.setProperty("input_type", row["input_type"])
                    color_input.colorUpdated.connect(self.update_style)
                    self.widgets.append(color_input)
                    self.form_layout.addRow(color_input)
                """

                if row["input_type"] == "color":
                    color_input = ColorInputWidget()
                    color_input.clear()
                    color_input.setProperty("style_name", row["name"])
                    color_input.setProperty("input_type", row["input_type"])
                    color_input.textChanged.connect(self.update_style)
                    self.widgets.append(color_input)
                    self.form_layout.addRow(label)
                    self.form_layout.addRow(color_input)

                if row["input_type"] == "image":
                    image_input = ImageInput.ImageInput(url=True)
                    image_input.setProperty("style_name", row["name"])
                    image_input.setProperty("input_type", row["input_type"])
                    image_input.data_changed.connect(self.update_style)
                    self.widgets.append(image_input)
                    self.form_layout.addRow(label)
                    self.form_layout.addRow(image_input)

                if row["input_type"] == "btn-group":
                    buttons = QHBoxLayout()
                    self.form_layout.addRow(label)
                    for option in row["options"]:
                        btn = QToolButton()
                        btn.setProperty("style_name", row["name"])
                        btn.setProperty("style_value", option)
                        btn.setIcon(icon)
                        btn.setCheckable(True)
                        buttons.addWidget(btn)
                    self.form_layout.addRow(buttons)

                if row["input_type"] == "unitinput":
                    unit_input = UnitInput(["px", "pt", "%"])
                    self.form_layout.addRow(label, unit_input)

        self.state.element_state.data_changed.connect(self.update_element_name)
        self.state.class_name.data_changed.connect(self.fetch_class_name)
        self.state.fetched_css.data_changed.connect(self.fetch_css)
        self.state.text_content.data_changed.connect(self.fetch_text_content)
        self.state.project_name.data_changed.connect(self.refresh_widget)

    def update_element_name(self, value):
        self.element_name_label.setText(value)
        #print(self.element_name_label.text())
        #print(self.state.style_state.data)
        if self.element_name_label.text() in text_elements:
            self.text_content.show()
            self.text_content_label.show()
        else:
            self.text_content.hide()
            self.text_content_label.hide()

        if self.element_name_label.text() == "img":
            self.select_image_label.show()
            self.select_image.show()

        else:
            self.select_image_label.hide()
            self.select_image.hide()

    def update_class_name(self, value):
        self.state.class_name.data = value

    def fetch_class_name(self):
        self.selector.setText(self.state.class_name.data)

    def set_image(self, value):
        #print(value)
        self.state.img_src.data = value

    def update_style(self, value=None):
        """
        if self.state.class_name.data == "" or None:
            widget = self.sender()
            if widget.property("input_type") == "lineedit":
                widget.setText("")
            if widget.property("input_type") == "combo":
                widget.setCurrentIndex(-1)
            if widget.property("input_type") == "color":
                widget.setText("")
                # widget.picker.set_color("")

            return
        """

        self.style_dict[self.sender().property('style_name')] = str(value)
        # print(self.style_dict)

        style = ""
        for i in self.style_dict:
            style = style + i + ":" + self.style_dict[i] + ";"

        self.state.style_state.data = style



    def update_text_content(self, value):
        self.state.text_content.data = value

    def fetch_text_content(self):
        self.text_content.setText(self.state.text_content.data)

    def fetch_css(self, value):
        # self.state.style_state.data = None

        if isinstance(value, dict) and value:
            for widget in self.widgets:
                for style in value:
                    if widget.property("style_name") == style:
                        # print("set", widget.property("style_name"))
                        if widget.property("input_type") == "lineedit":
                            widget.setText(value[style])
                        if widget.property("input_type") == "combo":
                            widget.setCurrentText(value[style])
                        if widget.property("input_type") == "color":
                            widget.setText(value[style])
                            # widget.picker.set_color(value[style])
                            # print(value[style])
                        if widget.property("input_type") == "image":
                            #print(value[style])
                            widget.set_img((value[style]).replace('"', "'"))
                            #print(self.style_dict)
                            #print(self.state.style_state.data)

                        break

                    else:
                        # print("clear", widget.property("style_name"))
                        if widget.property("input_type") == "lineedit":
                            widget.setText("")
                        if widget.property("input_type") == "combo":
                            widget.setCurrentIndex(-1)
                        if widget.property("input_type") == "color":
                            widget.setText("")
                            # widget.picker.set_color("")
                        if widget.property("input_type") == "image":
                            widget.clear_image()

        else:
            for widget in self.widgets:
                if widget.property("input_type") == "lineedit":
                    widget.setText("")
                if widget.property("input_type") == "combo":
                    widget.setCurrentIndex(-1)
                if widget.property("input_type") == "color":
                    widget.setText("")
                    # widget.picker.set_color("")
                if widget.property("input_type") == "image":
                    widget.clear_image()
                    widget.refresh_widget()
                    widget.display_images()

    def refresh_widget(self):
        self.state.class_name.data = ""
        self.state.element_state.data = ""
        self.state.class_name.data = ""
        self.state.fetched_css.data = None
        self.state.text_content.data = ""

        #print(self.state.style_state.data)
        #print(self.style_dict)
