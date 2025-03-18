import json
import os
import random
import shutil
from PyQt6.QtCore import Qt, QStandardPaths, QSize
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QClipboard, QIcon
from PyQt6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QVBoxLayout, QPushButton, QScrollArea,
    QWidget, QHBoxLayout, QTextEdit, QSplitter, QStackedWidget, QComboBox, QMessageBox, QFileDialog
)

def resource_path(relative_path):
    """ Get the absolute path to a resource, works for dev and for PyInstaller. """
    if getattr(sys, "frozen", False):  # If the app is frozen when packaged with PyInstaller
        base_path = sys._MEIPASS  # Temporary directory used by PyInstaller
    else:
        base_path = os.path.abspath(".")  # Base path for development
    return os.path.join(base_path, relative_path)

class HtmlEditor(QMainWindow):
    SETTINGS_FILE = "app_settings.json"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edytor opisów długich Moto-Toura 2025")
        self.setGeometry(100, 100, 1000, 600)

        self.light_mode = False
        self.section_direction = True
        self.sections = []
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.settings = self.load_settings()

        if self.settings is None:
            self.show_starting_page()
        else:
            self.light_mode = self.settings.get("light_mode", False)
            self.show_main_pages()
            self.apply_styles()

    def load_settings(self):
        if os.path.exists(HtmlEditor.SETTINGS_FILE):
            with open(HtmlEditor.SETTINGS_FILE, "r") as file:
                return json.load(file)
        return None

    def save_settings(self):
        with open(HtmlEditor.SETTINGS_FILE, "w") as file:
            json.dump({"light_mode": self.light_mode}, file)

    def show_starting_page(self):
        self.starting_page = QWidget()
        self.starting_layout = QVBoxLayout()
        self.starting_page.setLayout(self.starting_layout)

        self.welcome_label = QLabel("<h1>Witaj w Edytor opisów długich Moto-Toura!</h1>")
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.starting_layout.addWidget(self.welcome_label)

        self.theme_label = QLabel("<h3>Wybierz motyw:<h3>")
        self.theme_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.starting_layout.addWidget(self.theme_label)

        self.theme_buttons_layout = QHBoxLayout()

        self.dark_theme_button = QPushButton()
        self.dark_theme_button.setIcon(QIcon(QPixmap(resource_path("images/darkmode.png"))))
        self.dark_theme_button.setIconSize(QSize(450, 450))
        self.dark_theme_button.setStyleSheet("border: 3px solid gray;")
        self.dark_theme_button.clicked.connect(lambda: self.select_theme(False))
        self.theme_buttons_layout.addWidget(self.dark_theme_button)

        self.light_theme_button = QPushButton()
        self.light_theme_button.setIcon(QIcon(QPixmap(resource_path("images/lightmode.png"))))
        self.light_theme_button.setIconSize(QSize(450, 450))
        self.light_theme_button.setStyleSheet("border: 3px solid gray;")
        self.light_theme_button.clicked.connect(lambda: self.select_theme(True))
        self.theme_buttons_layout.addWidget(self.light_theme_button)

        self.starting_layout.addLayout(self.theme_buttons_layout)

        self.continue_button = QPushButton("Wybierz i przejdź dalej")
        self.continue_button.setStyleSheet(
            "background-color: lightgray; color: gray; padding: 10px; border-radius: 5px;")
        self.continue_button.setDisabled(True)
        self.continue_button.clicked.connect(self.proceed_to_main)
        self.starting_layout.addWidget(self.continue_button)

        self.stack.addWidget(self.starting_page)

    def select_theme(self, is_light):
        self.light_mode = is_light
        self.dark_theme_button.setStyleSheet("border: 3px solid gray;")
        self.light_theme_button.setStyleSheet("border: 3px solid gray;")
        if is_light:
            self.light_theme_button.setStyleSheet("border: 3px solid blue;")
        else:
            self.dark_theme_button.setStyleSheet("border: 3px solid blue;")
        self.continue_button.setStyleSheet(
            "background-color: #0A74DA; color: white; padding: 10px; border-radius: 5px;")
        self.continue_button.setEnabled(True)

    def proceed_to_main(self):
        self.save_settings()
        self.show_main_pages()
        self.apply_styles()

    def show_main_pages(self):
        self.welcome_page = QWidget()
        self.welcome_layout = QVBoxLayout()
        self.welcome_page.setLayout(self.welcome_layout)

        self.welcome_label = QLabel(
            "<h1>Witaj w edytorze długich opisów Moto-Toura!</h1>"
            "<h2>Smacznej kawusi i miłego dnia!</h2>")
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcome_layout.addWidget(self.welcome_label)

        self.start_button = QPushButton("Kliknij aby rozpocząć budowanie nowego opisu :)")
        self.start_button.clicked.connect(self.show_editor_page)
        self.welcome_layout.addWidget(self.start_button)

        self.stack.addWidget(self.welcome_page)
        self.stack.setCurrentWidget(self.welcome_page)

        self.editor_page = QWidget()
        self.editor_layout = QVBoxLayout()
        self.editor_page.setLayout(self.editor_layout)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.editor_layout.addWidget(self.splitter)
        self.splitter.setStretchFactor(0, 7)
        self.splitter.setStretchFactor(1, 3)

        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout()
        self.left_widget.setLayout(self.left_layout)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_content.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_content)
        self.left_layout.addWidget(self.scroll_area)

        self.add_section_button = QPushButton("+ Dodaj Sekcję")
        self.add_section_button.clicked.connect(self.add_section)
        self.left_layout.addWidget(self.add_section_button)

        self.add_header_button = QPushButton("+ Dodaj Nagłówek")
        self.add_header_button.clicked.connect(self.add_header)
        self.left_layout.addWidget(self.add_header_button)

        self.splitter.addWidget(self.left_widget)

        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_widget.setLayout(self.right_layout)

        self.html_edit = QTextEdit()
        self.html_edit.setReadOnly(False)
        self.right_layout.addWidget(self.html_edit)

        self.copy_html_button = QPushButton("Skopiuj kod HTML")
        self.right_layout.addWidget(self.copy_html_button)

        self.splitter.addWidget(self.right_widget)
        self.splitter.setSizes([700, 300])

        self.stack.addWidget(self.editor_page)

    def show_editor_page(self):
        self.stack.setCurrentWidget(self.editor_page)

    def toggle_light_mode(self):
        self.light_mode = not self.light_mode
        self.apply_styles()

    def apply_styles(self):
        # Global app styles
        if self.light_mode:
            self.setStyleSheet("background-color: white; color: black;")
        else:
            self.setStyleSheet("background-color: #2b2b2b; color: white;")

        # Start button style
        if hasattr(self, 'start_button'):
            self.start_button.setStyleSheet("""
                background-color: #6395ED; 
                color: black; 
                padding: 10px; 
                border-radius: 5px;
            """ if self.light_mode else """
                background-color: #4567BB; 
                color: white; 
                padding: 10px; 
                border-radius: 5px;
            """)

        # Add section button style
        if hasattr(self, 'add_section_button'):
            self.add_section_button.setStyleSheet("""
                background-color: #198754; 
                color: black; 
                padding: 10px; 
                border-radius: 6px; 
                font-size: 14px;
            """ if self.light_mode else """
                background-color: #28a745; 
                color: white; 
                padding: 10px; 
                border-radius: 6px; 
                font-size: 14px;
            """)

        # Add header button style
        if hasattr(self, 'add_header_button'):
            self.add_header_button.setStyleSheet("""
                background-color: #6395ED; 
                color: black; 
                padding: 10px; 
                border-radius: 6px; 
                font-size: 14px;
            """ if self.light_mode else """
                background-color: #4567BB; 
                color: white; 
                padding: 10px; 
                border-radius: 6px; 
                font-size: 14px;
            """)

        # HTML editor style
        if hasattr(self, 'html_edit'):
            self.html_edit.setStyleSheet("""
                background-color: #e9ecef; 
                color: black; 
                border-radius: 5px; 
                padding: 5px;
            """ if self.light_mode else """
                background-color: #222; 
                color: white; 
                border-radius: 5px; 
                padding: 5px;
            """)

        # Copy HTML button style
        if hasattr(self, 'copy_html_button'):
            self.copy_html_button.setStyleSheet("""
                background-color: #6395ED; 
                color: black; 
                padding: 10px; 
                border-radius: 6px; 
                font-size: 14px;
            """ if self.light_mode else """
                background-color: #4567BB; 
                color: white; 
                padding: 10px; 
                border-radius: 6px; 
                font-size: 14px;
            """)

        # Update dynamic sections and buttons
        self.update_buttons_theme()

    def update_buttons_theme(self):
        for section in self.sections:
            if section[1] == "section":
                _, _, _, text_edit, buttons_widget, _ = section

                # Update TextEdit style for sections
                text_edit.setStyleSheet("""
                    background-color: #e9ecef; 
                    color: black; 
                    border-radius: 5px; 
                    padding: 5px;
                """ if self.light_mode else """
                    background-color: #222; 
                    color: white; 
                    border-radius: 5px; 
                    padding: 5px;
                """)

                # Update QPushButtons inside each section
                for button in buttons_widget.findChildren(QPushButton):
                    button.setStyleSheet("""
                        background-color: #FFC107; 
                        color: black; 
                        padding: 10px; 
                        border-radius: 5px;
                    """ if self.light_mode else """
                        background-color: #FF4C4C; 
                        color: white; 
                        padding: 10px; 
                        border-radius: 5px;
                    """)

    def swap_section_direction(self, section_layout):
        for i, section in enumerate(self.sections):
            if section[0] == section_layout:
                layout, section_type, image_label, text_edit, buttons_widget, direction = section

                for j in reversed(range(section_layout.count())):
                    item = section_layout.itemAt(j)
                    widget = item.widget()
                    if widget and widget != buttons_widget:
                        widget.setParent(None)

                if direction:
                    section_layout.insertWidget(0, text_edit)
                    section_layout.insertWidget(1, image_label)
                else:
                    section_layout.insertWidget(0, image_label)
                    section_layout.insertWidget(1, text_edit)

                section_layout.addWidget(buttons_widget)
                self.sections[i] = (section_layout, section_type, image_label, text_edit, buttons_widget, not direction)

                self.update_html()
                break

    def add_section(self):
        section_layout = QHBoxLayout()

        image_label = self.DraggableLabel(editor=self)
        image_label.setStyleSheet(
            "background-color: #f0f0f0; border: 1px solid #ccc;" if self.light_mode else
            "background-color: #333; border: 1px solid #444;"
        )

        text_edit = QTextEdit()
        text_edit.setPlaceholderText("Wpisz treść paragrafu...")
        text_edit.textChanged.connect(self.update_html)
        text_edit.setStyleSheet(
            "background-color: #e9ecef; color: black; border-radius: 5px; padding: 5px;" if self.light_mode else
            "background-color: #222; color: white; border-radius: 5px; padding: 5px;"
        )

        delete_button = QPushButton("Usuń")
        delete_button.setStyleSheet(
            "background-color: #FF4C4C; color: black; padding: 5px; border-radius: 5px;" if self.light_mode else
            "background-color: #FF4C4C; color: white; padding: 5px; border-radius: 5px;"
        )
        delete_button.clicked.connect(lambda: self.delete_section(section_layout))

        swap_button = QPushButton("Zamień")
        swap_button.setStyleSheet(
            "background-color: #FFC107; color: black; padding: 5px; border-radius: 5px;" if self.light_mode else
            "background-color: #FFC107; color: black; padding: 5px; border-radius: 5px;"
        )
        swap_button.clicked.connect(lambda: self.swap_section_direction(section_layout))

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(swap_button)
        buttons_layout.addWidget(delete_button)

        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)

        if self.section_direction:
            section_layout.addWidget(image_label)
            section_layout.addWidget(text_edit)
        else:
            section_layout.addWidget(text_edit)
            section_layout.addWidget(image_label)

        section_layout.addWidget(buttons_widget)
        self.scroll_layout.addLayout(section_layout)

        self.sections.append(
            (section_layout, "section", image_label, text_edit, buttons_widget, self.section_direction))
        self.section_direction = not self.section_direction
        self.update_html()

    def add_header(self):
        header_layout = QHBoxLayout()
        header_types = ["h1", "h2", "h3"]

        header_combobox = QComboBox()
        header_combobox.addItems(header_types)
        header_combobox.setStyleSheet(
            "background-color: #e9ecef; color: black; padding: 10px; font-size: 14px;" if self.light_mode else
            "background-color: #222; color: white; padding: 10px; font-size: 14px;"
        )

        header_text_edit = QTextEdit()
        header_text_edit.setPlaceholderText("Wpisz tekst nagłówka...")
        header_text_edit.setStyleSheet(
            "background-color: #e9ecef; color: black; border-radius: 5px; padding: 5px;" if self.light_mode else
            "background-color: #222; color: white; border-radius: 5px; padding: 5px;"
        )

        header_text_edit.textChanged.connect(self.update_html)
        header_combobox.currentTextChanged.connect(self.update_html)

        delete_button = QPushButton("Usuń")
        delete_button.setStyleSheet(
            "background-color: #FF4C4C; color: black; padding: 5px; border-radius: 5px;" if self.light_mode else
            "background-color: #FF4C4C; color: white; padding: 5px; border-radius: 5px;"
        )
        delete_button.clicked.connect(lambda: self.delete_section(header_layout))

        header_layout.addWidget(header_combobox)
        header_layout.addWidget(header_text_edit)
        header_layout.addWidget(delete_button)
        self.scroll_layout.addLayout(header_layout)

        self.sections.append((header_layout, "header", header_combobox, header_text_edit))
        self.update_html()

    def delete_section(self, section_layout):
        for section in self.sections:
            if section[0] == section_layout:
                if section[1] == "section":
                    image_label = section[2]
                    if image_label.image_path and os.path.isfile(image_label.image_path):
                        os.remove(image_label.image_path)
                self.sections.remove(section)
                break

        while section_layout.count():
            item = section_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.update_html()

    def update_html(self):
        html_content = """<html>
        <head>
            <style>
                .longdescription__template { width: 100%; }
                .row { display: flex; align-items: center; margin-bottom: 20px; }
                .longdescription__template__col.--photo img { max-width: 100%; height: auto; }
                .longdescription__template__col.--text { padding: 10px; }
            </style>
        </head>
        <body>
            <div class="longdescription__template">"""

        for section in self.sections:
            if section[1] == "section":
                image_label, text_edit, direction = section[2], section[3], section[5]

                text_content = text_edit.toPlainText()
                text_html = f"""<div class="longdescription__template__col --text">
                    <p>{text_content}</p>
                </div>"""

                if image_label.image_path and os.path.isfile(image_label.image_path):
                    file_name = os.path.basename(image_label.image_path)
                    image_html = f"""<div class="longdescription__template__col --photo">
                        <img src="/data/include/cms/img-longdescription/{file_name}" alt="Obraz">
                    </div>"""
                else:
                    image_html = ""

                if direction:
                    html_content += f"""
                        <div class="row">
                            {image_html}
                            {text_html}
                        </div>"""
                else:
                    html_content += f"""
                        <div class="row">
                            {text_html}
                            {image_html}
                        </div>"""

            elif section[1] == "header":
                header_combobox, header_text_edit = section[2], section[3]
                header_type = header_combobox.currentText()
                header_content = header_text_edit.toPlainText()
                html_content += f"""
                    <{header_type}>{header_content}</{header_type}>"""

        html_content += """
            </div>
        </body>
        </html>"""

        self.html_edit.setPlainText(html_content)

    class DraggableLabel(QLabel):
        def __init__(self, editor=None):
            super().__init__(editor)
            self.editor = editor
            self.setText("Przeciągnij obraz tutaj lub kliknij, aby wybrać plik")
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setStyleSheet("border: 2px dashed gray; padding: 20px; background-color: #444; color: white;")
            self.setAcceptDrops(True)
            self.image_path = ""
            self.target_directory = self.create_directory_on_start()
            self.confirmation_mode = False
            self.show_red_x = False

        def create_directory_on_start(self):
            desktop_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
            directory_name = "Zdjecia Opisow Dlugich"
            target_directory = os.path.join(desktop_path, directory_name)
            if not os.path.exists(target_directory):
                os.makedirs(target_directory)
            return target_directory

        def dragEnterEvent(self, event):
            if event.mimeData().hasUrls():
                event.acceptProposedAction()

        def dropEvent(self, event):
            try:
                urls = event.mimeData().urls()
                if urls:
                    self.image_path = urls[0].toLocalFile()
                    self.copy_and_display_image(self.image_path)
            except Exception as e:
                print(f"Error during dropEvent: {e}")

        def mousePressEvent(self, event):
            if event.button() == Qt.MouseButton.LeftButton:
                if self.image_path and self.confirmation_mode:
                    self.delete_image()
                elif self.image_path and not self.confirmation_mode:
                    self.confirmation_mode = True
                    self.update()  # Trigger a repaint to show the confirmation text
                else:
                    file_dialog = QFileDialog()
                    desktop_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
                    file_dialog.setDirectory(desktop_path)  # Start file dialog at desktop
                    file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")
                    if file_dialog.exec():
                        selected_file = file_dialog.selectedFiles()
                        if selected_file:
                            self.copy_and_display_image(selected_file[0])

        def delete_image(self):
            try:
                if not self.image_path or not os.path.isfile(self.image_path):
                    return
                os.remove(self.image_path)
                self.image_path = ""
                self.confirmation_mode = False
                self.show_red_x = False  # Reset hover effect flag
                self.setPixmap(QPixmap())  # Reset to no image
                self.setText("Przeciągnij obraz tutaj lub kliknij, aby wybrać plik")
                self.setStyleSheet("border: 2px dashed gray; padding: 20px; background-color: #444; color: white;")
                if self.editor and hasattr(self.editor, "update_html"):
                    self.editor.update_html()
            except Exception as e:
                print(f"Error during delete_image: {e}")

        def copy_and_display_image(self, source_path):
            try:
                if not os.path.isfile(source_path):
                    return
                original_name = os.path.basename(source_path)
                random_digits = random.randint(1000, 9999)
                new_file_name = f"{os.path.splitext(original_name)[0]}_{random_digits}.jpg"
                destination_path = os.path.join(self.target_directory, new_file_name)
                shutil.copy(source_path, destination_path)
                self.image_path = destination_path
                self.setPixmap(QPixmap(self.image_path).scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio))
                self.show_red_x = False  # Reset hover effect when new image is added
                self.confirmation_mode = False  # Reset confirmation mode
                if self.editor and hasattr(self.editor, "update_html"):
                    self.editor.update_html()
            except Exception as e:
                print(f"Error during copy_and_display_image: {e}")

        def enterEvent(self, event):
            if self.image_path:
                self.show_red_x = True
                self.update()

        def leaveEvent(self, event):
            if self.image_path:
                self.show_red_x = False
                self.update()

        def paintEvent(self, event):
            super().paintEvent(event)
            if self.image_path:
                painter = QPainter(self)
                if self.show_red_x:
                    painter.setPen(QColor(255, 0, 0))
                    painter.setBrush(QColor(255, 0, 0, 100))
                    painter.drawRect(0, 0, self.width(), self.height())
                    font = QFont("Arial", 36, QFont.Weight.Bold)
                    painter.setFont(font)
                    painter.setPen(QColor(255, 255, 255))
                    painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "X")
                if self.confirmation_mode:
                    painter.setPen(QColor(255, 255, 255))
                    painter.setBrush(QColor(0, 0, 0, 200))
                    painter.drawRect(0, 0, self.width(), self.height())
                    font = QFont("Arial", 16, QFont.Weight.Bold)
                    painter.setFont(font)
                    painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                                     "Czy na pewno chcesz usunąć?\nKliknij aby potwierdzić")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = HtmlEditor()
    window.show()
    sys.exit(app.exec())