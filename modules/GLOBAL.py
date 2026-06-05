import os
import sys
import json
from pathlib import Path


def get_base_dir():
    # If running as EXE (PyInstaller)
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)

    # Normal Python run → project root
    return Path(__file__).resolve().parent.parent

#USER_DIR = Path(os.getenv("APPDATA")) / "DesignToCode"

BASE_DIR = get_base_dir()
USER_DIR = BASE_DIR / "userdata"
ASSETS = BASE_DIR / "assets"
SCHEMA = BASE_DIR / "schema"
STYLE = BASE_DIR / "style"
APPDATA = BASE_DIR / "appdata"


# all json files abs path
# or
# only some frequently needed data
def open_project_data():
    with open(open_project_file_path, "r") as f:
        data = json.load(f)
    return data


app_data_path = BASE_DIR / "appdata"

assets_path = BASE_DIR / "assets"

project_list_file_path = app_data_path / "projectlist.json"

open_project_file_path = app_data_path / "openprojectdata.json"

app_settings_file_path = app_data_path / "settings.json"

elements_data_file_path = app_data_path / "elements_data.json"

styling_struct_file_path = app_data_path / "styling_struct.json"

html_markup = """

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title></title>
    <link rel="stylesheet" href="style.css">
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <style></style>
</head>
<body>
    <script src="script.js"></script>
</body>
</html>

"""


def default_save_path():
    with open(app_settings_file_path, "r") as f:
        data = json.load(f)
        # print(data['default_project_dir'])
        return Path(data["default_project_dir"])


def open_project_name():
    with open(open_project_file_path, "r") as f:
        data = json.load(f)
        return data["project_name"]


def open_project(project_name):
    data = {
        "is_project_open": True,
        "project_name": project_name,
        "pages": ["index"]
    }

    json_data = json.dumps(data)

    with open(str(open_project_file_path), "w") as f:
        f.write(json_data)


def open_project_pages():
    with open(project_list_file_path, "r") as f:
        data = json.load(f)

    for item in data:
        if item["project_name"] == open_project_name():
            return item["pages"]


def save_page(html_content):
    project_name = open_project_name()

    project_dir = str(USER_DIR) + "\\" + project_name
    try:
        with open(project_dir + "\\index.html", "w") as f:
            f.write(html_content)

    except Exception as e:
        print("save failed")


folder_path = USER_DIR / open_project_name() / "assets"

