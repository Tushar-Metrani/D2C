import os
import zipfile
from PySide6.QtWidgets import QFileDialog
from modules import GLOBAL


def handle_create_zip(self, html_content, css_content):
    # Open folder picker
    folder = QFileDialog.getExistingDirectory()
    if not folder:
        return  # user cancelled

    assets_folder = GLOBAL.USER_DIR / GLOBAL.open_project_name() / "assets"

    zip_path = os.path.join(folder, "website.zip")

    # Create zip
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Write HTML and CSS directly into zip (no temp files on disk)
        zipf.writestr("index.html", html_content)
        zipf.writestr("style.css", css_content)

        # Add assets folder if provided
        if assets_folder and os.path.isdir(assets_folder):
            for root, dirs, files in os.walk(assets_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(assets_folder))
                    zipf.write(file_path, arcname)

    print(f"ZIP created at: {zip_path}")