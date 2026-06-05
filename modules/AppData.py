from PySide6.QtCore import QObject, Signal


class AppData(QObject):
    data_changed = Signal(object)

    def __init__(self):
        super().__init__()
        self._data = None

    def get_data(self):
        return self._data

    def set_data(self, value):
        self._data = value
        self.data_changed.emit(value)

    data = property(get_data, set_data)


class AppState(QObject):
    data_changed = Signal(object)

    def __init__(self):
        super().__init__()
        self.project_name = AppData()
        self.style_state = AppData()
        self.class_name = AppData()
        self.element_state = AppData()
        self.inserting_element = AppData()
        self.text_content = AppData()
        self.fetched_css = AppData()
        self.saved = AppData()
        self.img_src = AppData()
        self.export_code = AppData()

"""
class ElementState(QObject):
    data_changed = Signal(object)

    def __init__(self):
        super().__init__()
        self._editing_element_name = None

    def get_data(self):
        return self._editing_element_name

    def set_data(self,value):
        if self._editing_element_name != value:
            self._editing_element_name = value
            self.data_changed.emit(value)

    editing_element_name = property(get_data,set_data)
    
"""
