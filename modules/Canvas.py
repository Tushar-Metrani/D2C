import time

from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, QObject, Slot, Signal
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWidgets import QMessageBox

from modules import GLOBAL
from modules.HelperFunctions import handle_create_zip
from modules.AppData import *

index_html = GLOBAL.USER_DIR / GLOBAL.open_project_name() / "index.html"

selected_element = []


class Backend(QObject):
    def __init__(self, state):
        super().__init__()
        self.state = state

    @Slot()
    def test(self):
        print("Hello world")

    @Slot(str)
    def receive(self, label):
        msg = QMessageBox()
        msg.setWindowTitle("Alert")
        msg.setText(label)
        msg.exec()

    @Slot(str, str, str, dict)
    def element_selected(self, element, class_name, text_content, style_dict):
        self.state.element_state.data = element
        self.state.class_name.data = class_name
        self.state.text_content.data = text_content
        self.state.fetched_css.data = self.format_style(style_dict)
        #print(style_dict)
        #print(self.state.fetched_css.data)

    def format_style(self, style_dict):
        map = {
            "display": "display",
            "flexDirection": "flex-direction",
            "flexWrap": "flex-wrap",
            "alignContent": "align-content",
            "justifyContent": "justify-content",
            "alignItems": "align-items",
            "width": "width",
            "height": "height",
            "maxWidth": "max-width",
            "minWidth": "min-width",
            "maxHeight": "max-height",
            "minHeight": "min-height",
            "margin": "margin",
            "padding": "padding",
            "fontSize": "font-size",
            "fontWeight": "font-weight",
            "textAlign": "text-align",
            "color": "color",
            "borderColor": "border-color",
            "borderWidth": "border-width",
            "borderStyle": "border-style",
            "borderRadius": "border-radius",
            "backgroundColor": "background-color",
            "backgroundImage": "background-image"
        }

        formatted_dict = {}

        for row in style_dict:
            style = map[row]
            formatted_dict[style] = style_dict[row]

        return formatted_dict

    @Slot()
    def element_inserted(self):
        self.state.inserting_element.data = None

    @Slot(str)
    def save_page(self, html_content):
        GLOBAL.save_page(html_content)
        self.state.saved.data = False

    @Slot(str, str)
    def export_code(self, html_content,css_content):
        handle_create_zip(self,html_content,css_content)
        self.state.saved.data = False


class Canvas(QWebEngineView):

    def __init__(self, state):
        super().__init__()

        self.channel = QWebChannel(self.page())
        self.backend = Backend(state)
        self.state = state

        self.channel.registerObject("backend", self.backend)
        self.page().setWebChannel(self.channel)
        #self.devtools = QWebEngineView()
        #self.page().setDevToolsPage(self.devtools.page())
        #self.devtools.show()
        self.setUrl(QUrl.fromLocalFile(index_html))
        self.setVisible(True)

        self.state.inserting_element.data_changed.connect(self.inserting_element)

        self.state.class_name.data_changed.connect(self.update_class_name)

        self.state.img_src.data_changed.connect(self.set_img_src)

        self.state.style_state.data_changed.connect(self.update_css)

        self.state.text_content.data_changed.connect(self.update_text)

        self.state.saved.data_changed.connect(self.save_page)

        self.state.project_name.data_changed.connect(self.update_project_name)

        self.state.export_code.data_changed.connect(self.export_code)

    def update_project_name(self):
        time.sleep(1)
        index_html = GLOBAL.USER_DIR / GLOBAL.open_project_name() / "index.html"
        self.setUrl(QUrl.fromLocalFile(index_html))

    def inserting_element(self, value):
        if value is None:
            js = "abort_inserting()"
        else:
            js = f"inserting_element('{value}')"
        self.page().runJavaScript(js)

    def update_class_name(self, value):
        # print(value)
        js = f"update_class_name('{value}')"
        self.page().runJavaScript(js)

    def set_img_src(self, value):
        js = f"set_img_src('{value}')"
        self.page().runJavaScript(js)

    def update_css(self, value):
        class_name = self.state.class_name.data
        style = value

        css_rule = f".{class_name} {{ {style} }}"
        # print(css_rule)

        js = f'apply_css("{css_rule}")'
        self.page().runJavaScript(js)

    def update_text(self, value):
        js = f"set_text('{value}')"
        self.page().runJavaScript(js)

    def save_page(self, value):
        # print(value)
        if not value:
            return
        js = "save_page()"
        self.page().runJavaScript(js)
        print("js running")

    def export_code(self):
        #print(self.state.export_code.data)
        js = "export_code()"
        self.page().runJavaScript(js)
