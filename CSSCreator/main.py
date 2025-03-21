import json
import os
import random
import shutil
from PyQt6.QtCore import Qt, QStandardPaths, QSize, QTimer, QPropertyAnimation, QRect
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QClipboard, QIcon
from PyQt6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QVBoxLayout, QPushButton, QScrollArea,
    QWidget, QHBoxLayout, QTextEdit, QSplitter, QStackedWidget, QComboBox, QMessageBox, QFileDialog, QLineEdit, QLayout
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
        
        icon_path = resource_path("ikona.ico")
        self.setWindowIcon(QIcon(icon_path))

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

        self.add_header_button = QPushButton("+ Dodaj Nagłówek")
        self.add_header_button.clicked.connect(self.add_header)

        self.add_ul_button = QPushButton("+ Dodaj Listę")
        self.add_ul_button.setStyleSheet(
            "background-color: #870501; color: white; padding: 10px; border-radius: 6px; font-size: 14px;"
        )
        self.add_ul_button.clicked.connect(lambda: self.add_list("ul"))

        self.add_youtube_button = QPushButton("+ Dodaj Film YouTube")
        self.add_youtube_button.setStyleSheet(
            "background-color: #d38235; color: white; padding: 10px; border-radius: 6px; font-size: 14px;"
        )
        self.add_youtube_button.clicked.connect(self.add_youtube_video)

        self.dark_mode_toggle_button = QPushButton("")
        self.dark_mode_toggle_button.setFixedSize(30, 90)
        self.dark_mode_toggle_button.clicked.connect(self.toggle_light_mode)
        if self.light_mode:
            self.dark_mode_toggle_button.setStyleSheet("""
                                QPushButton {
                                    background-color: #555555;
                                    color: white;
                                    border: none;
                                    border-radius: 15px;
    
                                    font-size: 20px;
                                }
                                QPushButton:hover {
                                    background-color: #444444;
                                }
                            """)
            self.dark_mode_toggle_button.setText("🌙")
        else:
            self.dark_mode_toggle_button.setStyleSheet("""
                                QPushButton {
                                    background-color: #cccccc;
                                    color: black;
                                    border: none;
                                    border-radius: 15px;

                                    font-size: 20px;
                                }
                                QPushButton:hover {
                                    background-color: #e6e6e6;
                                }
                            """)
            self.dark_mode_toggle_button.setText("☀️")

        self.is_dark_mode = False

        self.slider_animation = QPropertyAnimation(self.dark_mode_toggle_button, b"geometry")
        self.slider_animation.setDuration(300)

        box = QHBoxLayout()

        zero = QVBoxLayout()
        zero.addWidget(self.dark_mode_toggle_button)

        first = QVBoxLayout()
        first.addWidget(self.add_section_button)
        first.addWidget(self.add_header_button)

        second = QVBoxLayout()
        second.addWidget(self.add_ul_button)
        second.addWidget(self.add_youtube_button)

        box.addLayout(zero)
        box.addLayout(first)
        box.addLayout(second)

        self.left_layout.addLayout(box)

        self.splitter.addWidget(self.left_widget)

        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_widget.setLayout(self.right_layout)

        self.html_edit = QTextEdit()
        self.html_edit.setReadOnly(False)
        self.right_layout.addWidget(self.html_edit)

        self.copy_html_button = QPushButton("Skopiuj kod HTML")
        self.right_layout.addWidget(self.copy_html_button)
        self.copy_html_button.clicked.connect(self.copy_html)

        self.splitter.addWidget(self.right_widget)
        self.splitter.setSizes([700, 300])

        self.stack.addWidget(self.editor_page)

    def show_editor_page(self):
        self.stack.setCurrentWidget(self.editor_page)

    def toggle_light_mode(self):
        self.light_mode = not self.light_mode
        self.apply_styles()
        self.save_settings()

        if self.light_mode:
            self.dark_mode_toggle_button.setStyleSheet("""
                    QPushButton {
                        background-color: #555555;
                        color: white;
                        border: none;
                        border-radius: 15px;
                        
                        font-size: 20px;
                    }
                    QPushButton:hover {
                        background-color: #444444;
                    }
                """)
            self.dark_mode_toggle_button.setText("🌙")
            self.slider_animation.setStartValue(self.dark_mode_toggle_button.geometry())

        else:
            self.dark_mode_toggle_button.setStyleSheet("""
                    QPushButton {
                        background-color: #cccccc;
                        color: black;
                        border: none;
                        border-radius: 15px;
                        
                        font-size: 20px;
                    }
                    QPushButton:hover {
                        background-color: #e6e6e6;
                    }
                """)
            self.dark_mode_toggle_button.setText("☀️")
            self.slider_animation.setStartValue(self.dark_mode_toggle_button.geometry())

        self.slider_animation.start()

    def apply_styles(self):
        # Apply global styles for the main window
        if self.light_mode:
            self.setStyleSheet("background-color: white; color: black;")
        else:
            self.setStyleSheet("background-color: #2b2b2b; color: white;")

        # Update individual buttons
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

        if hasattr(self, 'add_ul_button'):
            self.add_ul_button.setStyleSheet("""
                background-color: orange; 
                color: black; 
                padding: 10px; 
                border-radius: 6px; 
                font-size: 14px;
            """ if self.light_mode else """
                background-color: #e67c00; 
                color: white; 
                padding: 10px; 
                border-radius: 6px; 
                font-size: 14px;
            """)

        if hasattr(self, 'add_youtube_button'):
            self.add_youtube_button.setStyleSheet("""
                background-color: red; 
                color: black; 
                padding: 10px; 
                border-radius: 6px; 
                font-size: 14px;
            """ if self.light_mode else """
                background-color: #d32f2f; 
                color: white; 
                padding: 10px; 
                border-radius: 6px; 
                font-size: 14px;
            """)

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

        # Update all sections
        self.update_buttons_theme()

    def copy_html(self):
        html_content = self.html_edit.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText(html_content, mode=QClipboard.Mode.Clipboard)

        # Change the style and text of the button
        self.copy_html_button.setStyleSheet("background-color: green; color: white; padding: 10px; border-radius: 5px;")
        self.copy_html_button.setText("Skopiowano!")

        # Reset the button after a delay
        QTimer.singleShot(2000, self.reset_copy_button)

    def reset_copy_button(self):
        # Reset button style and text to the default
        self.copy_html_button.setStyleSheet(
            "background-color: #6395ED; color: white; padding: 10px; border-radius: 5px;"
        )
        self.copy_html_button.setText("Skopiuj kod HTML")

    def update_buttons_theme(self):
        for section in self.sections:
            if section[1] == "section":
                # Unpack section layout
                _, _, label, text_edit, buttons_widget, _ = section

                # Update styles for QTextEdit
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

                # Update draggable label color
                label.setStyleSheet("""
                    background-color: #f0f0f0; 
                    border: 1px solid #ccc;
                """ if self.light_mode else """
                    background-color: #333; 
                    border: 1px solid #444;
                """)

                # Update styles for buttons inside section
                for button in buttons_widget.findChildren(QPushButton):
                    if button.text() == "Usuń Sekcję":
                        button.setStyleSheet("""
                            background-color: #FF4C4C; 
                            color: black; 
                            padding: 5px; 
                            border-radius: 5px;
                        """ if self.light_mode else """
                            background-color: #FF4C4C; 
                            color: white; 
                            padding: 5px; 
                            border-radius: 5px;
                        """)
                    elif button.text() == "Zamień Kolejność":
                        button.setStyleSheet("""
                            background-color: #FFC107; 
                            color: black; 
                            padding: 5px; 
                            border-radius: 5px;
                        """ if self.light_mode else """
                            background-color: #FFC107; 
                            color: black; 
                            padding: 5px; 
                            border-radius: 5px;
                        """)
                    elif button.text() == "↑":
                        button.setStyleSheet("""
                            background-color: #6395ED; 
                            color: black; 
                            font-weight: bold;
                            padding: 5px; 
                            border-radius: 5px;
                        """ if self.light_mode else """
                            background-color: #4567BB; 
                            color: white; 
                            font-weight: bold;
                            padding: 5px; 
                            border-radius: 5px;
                        """)
                    elif button.text() == "↓":
                        button.setStyleSheet("""
                            background-color: #6395ED; 
                            color: black; 
                            font-weight: bold;
                            padding: 5px; 
                            border-radius: 5px;
                        """ if self.light_mode else """
                            background-color: #4567BB; 
                            color: white; 
                            font-weight: bold;
                            padding: 5px; 
                            border-radius: 5px;
                        """)

            elif section[1] == "header":
                combobox, text_edit = section[2], section[3]

                # Header text field style
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

                # Combobox style (header dropdown like H1, H2, etc.)
                combobox.setStyleSheet("""
                                    QComboBox {
                                        background-color: #e9ecef; 
                                        color: black; 

                                        padding: 10px; 
                                        font-size: 14px;
                                    }
                                    QComboBox QAbstractItemView {
                                        background-color: white; 
                                        color: black; 
                                        selection-background-color: #f0f0f0; 
                                        selection-color: black;
                                    }

                                """ if self.light_mode else """
                                    QComboBox {
                                        background-color: #222; 
                                        color: white; 

                                        padding: 10px; 
                                        font-size: 14px;
                                    }
                                    QComboBox QAbstractItemView {
                                        background-color: #2b2b2b; 
                                        color: white; 
                                        selection-background-color: #444; 
                                        selection-color: white;
                                    }

                                """)

            elif section[1] == "youtube":
                video_edit, thumbnail_url_edit, alt_text_edit = section[2:]

                # YouTube video fields
                for field in [video_edit, thumbnail_url_edit, alt_text_edit]:
                    field.setStyleSheet("""
                        background-color: #e9ecef; 
                        color: black; 
                        padding: 5px; 
                        border-radius: 5px;
                    """ if self.light_mode else """
                        background-color: #222; 
                        color: white; 
                        padding: 5px; 
                        border-radius: 5px;
                    """)

            elif section[1] == "list":
                combobox, text_edit = section[2], section[3]

                # List text edit
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

                # Combobox (dropdown list style)
                combobox.setStyleSheet("""
                    QComboBox {
                        background-color: #e9ecef; 
                        color: black; 
                        
                        padding: 10px; 
                        font-size: 14px;
                    }
                    QComboBox QAbstractItemView {
                        background-color: white; 
                        color: black; 
                        selection-background-color: #f0f0f0; 
                        selection-color: black;
                    }

                """ if self.light_mode else """
                    QComboBox {
                        background-color: #222; 
                        color: white; 
                        
                        padding: 10px; 
                        font-size: 14px;
                    }
                    QComboBox QAbstractItemView {
                        background-color: #2b2b2b; 
                        color: white; 
                        selection-background-color: #444; 
                        selection-color: white;
                    }

                """)


            elif section[1] == "youtube":
                video_id_edit, thumbnail_url_edit, alt_text_edit = section[2], section[3], section[4]

                video_id_edit.setStyleSheet("""
                    background-color: #e9ecef; 
                    color: black; 
                    padding: 5px;
                """ if self.light_mode else """
                    background-color: #222; 
                    color: white; 
                    padding: 5px;
                """)

                thumbnail_url_edit.setStyleSheet("""
                    background-color: #e9ecef; 
                    color: black; 
                    padding: 5px;
                """ if self.light_mode else """
                    background-color: #222; 
                    color: white; 
                    padding: 5px;
                """)

                alt_text_edit.setStyleSheet("""
                    background-color: #e9ecef; 
                    color: black; 
                    padding: 5px;
                """ if self.light_mode else """
                    background-color: #222; 
                    color: white; 
                    padding: 5px;
                """)

            elif section[1] == "list":
                combobox, text_edit = section[2], section[3]

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

                combobox.setStyleSheet("""
                    background-color: #f0f0f0; 
                    color: black; 
                    border: 1px solid #ccc;
                """ if self.light_mode else """
                    background-color: #444; 
                    color: white; 
                    border: 1px solid #666;
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
        text_edit.setStyleSheet("""
            background-color: #e9ecef; color: black; border-radius: 5px; padding: 5px;
        """ if self.light_mode else """
            background-color: #222; color: white; border-radius: 5px; padding: 5px;
        """)

        delete_button = QPushButton("Usuń Sekcję")
        delete_button.setStyleSheet("""
            background-color: #FF4C4C; color: black; padding: 5px; border-radius: 5px;
        """ if self.light_mode else """
            background-color: #FF4C4C; color: white; padding: 5px; border-radius: 5px;
        """)
        delete_button.clicked.connect(lambda: self.delete_section(section_layout))

        swap_button = QPushButton("Zamień Kolejność")
        swap_button.setStyleSheet("""
            background-color: #FFC107; color: black; padding: 5px; border-radius: 5px;
        """ if self.light_mode else """
            background-color: #FFC107; color: black; padding: 5px; border-radius: 5px;
        """)
        swap_button.clicked.connect(lambda: self.swap_section_direction(section_layout))

        move_up_button = QPushButton("↑")
        move_up_button.setStyleSheet("""
            background-color: #6395ED; color: black; padding: 5px; border-radius: 5px; font-weight: bold;
        """ if self.light_mode else """
            background-color: #4567BB; color: white; padding: 5px; border-radius: 5px; font-weight: bold;
        """)
        move_up_button.clicked.connect(lambda: self.move_section(section_layout, -1))

        move_down_button = QPushButton("↓")
        move_down_button.setStyleSheet("""
            background-color: #6395ED; color: black; padding: 5px; border-radius: 5px; font-weight: bold;
        """ if self.light_mode else """
            background-color: #4567BB; color: white; padding: 5px; border-radius: 5px; font-weight: bold;
        """)
        move_down_button.clicked.connect(lambda: self.move_section(section_layout, 1))

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(swap_button)
        buttons_layout.addWidget(delete_button)
        buttons_layout.addWidget(move_up_button)
        buttons_layout.addWidget(move_down_button)
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

        delete_button = QPushButton("Usuń Sekcję")
        delete_button.setStyleSheet(
            "background-color: #FF4C4C; color: black; padding: 5px; border-radius: 5px;" if self.light_mode else
            "background-color: #FF4C4C; color: white; padding: 5px; border-radius: 5px;"
        )
        delete_button.clicked.connect(lambda: self.delete_section(header_layout))

        move_up_button = QPushButton("↑")
        move_up_button.setStyleSheet(
            "background-color: #6395ED; color: black; padding: 5px; border-radius: 5px; font-weight: bold;" if self.light_mode else
            "background-color: #4567BB; color: white; padding: 5px; border-radius: 5px; font-weight: bold;"
        )
        move_up_button.clicked.connect(lambda: self.move_section(header_layout, -1))  # Move up

        move_down_button = QPushButton("↓")
        move_down_button.setStyleSheet(
            "background-color: #6395ED; color: black; padding: 5px; border-radius: 5px; font-weight: bold;" if self.light_mode else
            "background-color: #4567BB; color: white; padding: 5px; border-radius: 5px; font-weight: bold;"
        )
        move_down_button.clicked.connect(lambda: self.move_section(header_layout, 1))  # Move down

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(move_up_button)
        buttons_layout.addWidget(move_down_button)
        buttons_layout.addWidget(delete_button)

        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)

        header_layout.addWidget(header_combobox)
        header_layout.addWidget(header_text_edit)
        header_layout.addWidget(buttons_widget)
        self.scroll_layout.addLayout(header_layout)

        self.sections.append((header_layout, "header", header_combobox, header_text_edit))
        self.update_html()

    def add_youtube_video(self):
        youtube_layout = QHBoxLayout()

        video_id_edit = QLineEdit()
        video_id_edit.setPlaceholderText("Wpisz URL filmu")
        video_id_edit.setStyleSheet(
            "background-color: #e9ecef; color: black; padding: 5px; border-radius: 5px;" if self.light_mode else
            "background-color: #222; color: white; padding: 5px; border-radius: 5px;"
        )
        thumbnail_url_edit = QLineEdit()
        thumbnail_url_edit.setPlaceholderText("Wpisz URL miniaturki (maxresdefault)")
        thumbnail_url_edit.setStyleSheet(
            "background-color: #e9ecef; color: black; padding: 5px; border-radius: 5px;" if self.light_mode else
            "background-color: #222; color: white; padding: 5px; border-radius: 5px;"
        )
        alt_text_edit = QLineEdit()
        alt_text_edit.setPlaceholderText("Wpisz tekst zastępczy")
        alt_text_edit.setStyleSheet(
            "background-color: #e9ecef; color: black; padding: 5px; border-radius: 5px;" if self.light_mode else
            "background-color: #222; color: white; padding: 5px; border-radius: 5px;"
        )

        delete_button = QPushButton("Usuń Sekcję")
        delete_button.setStyleSheet(
            "background-color: #FF4C4C; color: white; padding: 5px; border-radius: 5px;" if self.light_mode else
            "background-color: #FF4C4C; color: white; padding: 5px; border-radius: 5px;"
        )

        delete_button.clicked.connect(lambda: self.delete_section(youtube_layout))

        move_up_button = QPushButton("↑")
        move_up_button.setStyleSheet(
            "background-color: #6395ED; color: black; padding: 5px; border-radius: 5px; font-weight: bold;" if self.light_mode else
            "background-color: #4567BB; color: white; padding: 5px; border-radius: 5px; font-weight: bold;"
        )
        move_up_button.clicked.connect(lambda: self.move_section(youtube_layout, -1))  # Move up

        move_down_button = QPushButton("↓")
        move_down_button.setStyleSheet(
            "background-color: #6395ED; color: black; padding: 5px; border-radius: 5px; font-weight: bold;" if self.light_mode else
            "background-color: #4567BB; color: white; padding: 5px; border-radius: 5px; font-weight: bold;"
        )
        move_down_button.clicked.connect(lambda: self.move_section(youtube_layout, 1))  # Move down

        youtube_layout.addWidget(video_id_edit)
        youtube_layout.addWidget(thumbnail_url_edit)
        youtube_layout.addWidget(alt_text_edit)

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(move_up_button)
        buttons_layout.addWidget(move_down_button)
        buttons_layout.addWidget(delete_button)

        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        youtube_layout.addWidget(buttons_widget)

        video_id_edit.textChanged.connect(lambda: self.process_youtube_url(video_id_edit))
        thumbnail_url_edit.textChanged.connect(self.update_html)
        alt_text_edit.textChanged.connect(self.update_html)

        self.scroll_layout.addLayout(youtube_layout)
        self.sections.append((youtube_layout, "youtube", video_id_edit, thumbnail_url_edit, alt_text_edit))

        self.update_html()

    def process_youtube_url(self, video_id_edit):
        full_url = video_id_edit.text()
        import re
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", full_url)
        video_id = match.group(1) if match else full_url.strip()
        video_id_edit.setText(video_id)
        self.update_html()

    def add_list(self, list_type):
        list_layout = QHBoxLayout()

        list_combobox = QComboBox()
        list_combobox.addItems(["ul", "ol"])  # Allow switching between UL and OL
        list_combobox.setCurrentText(list_type)
        list_combobox.setStyleSheet(
            "background-color: #e9ecef; color: black; padding: 10px; font-size: 14px;" if self.light_mode else
            "background-color: #222; color: white; padding: 10px; font-size: 14px;"
        )

        list_combobox.currentTextChanged.connect(self.update_html)

        list_text_edit = QTextEdit()
        list_text_edit.setPlaceholderText("Wpisz elementy listy, każdy w nowej linii...")
        list_text_edit.textChanged.connect(lambda: self.update_html())  # Auto-update HTML on item addition
        list_text_edit.setStyleSheet(
            "background-color: #e9ecef; color: black; border-radius: 5px; padding: 5px;" if self.light_mode else
            "background-color: #222; color: white; border-radius: 5px; padding: 5px;"
        )

        delete_button = QPushButton("Usuń Sekcję")
        delete_button.setStyleSheet(
            "background-color: #FF4C4C; color: black; padding: 5px; border-radius: 5px; " if self.light_mode else
            "background-color: #FF4C4C; color: white; padding: 5px; border-radius: 5px;"
        )
        delete_button.clicked.connect(lambda: self.delete_section(list_layout))

        move_up_button = QPushButton("↑")
        move_up_button.setStyleSheet(
            "background-color: #6395ED; color: black; padding: 5px; border-radius: 5px;" if self.light_mode else
            "background-color: #4567BB; color: white; padding: 5px; border-radius: 5px;"
        )
        move_up_button.clicked.connect(lambda: self.move_section(list_layout, -1))  # Move up

        move_down_button = QPushButton("↓")
        move_down_button.setStyleSheet(
            "background-color: #6395ED; color: black; padding: 5px; border-radius: 5px;" if self.light_mode else
            "background-color: #4567BB; color: white; padding: 5px; border-radius: 5px;"
        )
        move_down_button.clicked.connect(lambda: self.move_section(list_layout, 1))  # Move down

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(move_up_button)
        buttons_layout.addWidget(move_down_button)
        buttons_layout.addWidget(delete_button)
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)

        list_layout.addWidget(list_combobox)
        list_layout.addWidget(list_text_edit)
        list_layout.addWidget(buttons_widget)

        self.scroll_layout.addLayout(list_layout)

        # Save section info for tracking
        self.sections.append((list_layout, "list", list_combobox, list_text_edit))
        self.update_html()

    def move_section(self, section_layout, direction):
        current_index = None
        for i, section in enumerate(self.sections):
            if section[0] == section_layout:
                current_index = i
                break

        if current_index is None:
            return

        new_index = current_index + direction

        if 0 <= new_index < len(self.sections):
            self.sections.insert(new_index, self.sections.pop(current_index))

            layout_item = self.scroll_layout.takeAt(current_index)
            widget_to_move = layout_item.layout()
            self.scroll_layout.insertLayout(new_index, widget_to_move)

            self.update_html()

    def delete_section(self, section_layout):
        for i, section in enumerate(self.sections):
            if section[0] == section_layout:
                self.sections.pop(i)
                break

        for i in range(self.scroll_layout.count()):
            item = self.scroll_layout.itemAt(i)
            if item.layout() == section_layout:
                layout_item = self.scroll_layout.takeAt(i)
                while section_layout.count():
                    item = section_layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
                del layout_item
                break

        self.update_html()

    def update_html(self):
        html_content = """
                        <div class="longdescription__template">
                            <div class="longdescription__template__row --layout-photo-text">
                        """

        for section in self.sections:
            if section[1] == "section":
                image_label, text_edit, direction = section[2], section[3], section[5]

                text_content = text_edit.toPlainText()
                text_html = f"""
                    <div class="longdescription__template__col --text">
                        <p>{text_content}</p>
                    </div>
                """

                if image_label.image_path and os.path.isfile(image_label.image_path):
                    file_name = os.path.basename(image_label.image_path)
                    image_html = f"""
                        <div class="longdescription__template__col --photo">
                            <img src="/data/include/cms/img-longdescription/{file_name}" alt="Obraz">
                        </div>
                    """
                else:
                    image_html = ""

                if direction:
                    html_content += f"""
                        <div class="row">
                            {image_html}
                            {text_html}
                        </div>
                    """
                else:
                    html_content += f"""
                        <div class="row">
                            {text_html}
                            {image_html}
                        </div>
                    """

            elif section[1] == "header":
                header_combobox, header_text_edit = section[2], section[3]

                header_type = header_combobox.currentText()
                header_content = header_text_edit.toPlainText()

                html_content += f"""
                    <{header_type}>{header_content}</{header_type}>
                """

            elif section[1] == "youtube":
                video_id_edit, thumbnail_url_edit, alt_text_edit = section[2], section[3], section[4]

                video_id = video_id_edit.text().strip()
                thumbnail_url = thumbnail_url_edit.text().strip()
                alt_text = alt_text_edit.text().strip()

                if video_id and thumbnail_url and alt_text:
                    youtube_html = f"""
                    <div class="longdescription__template__row --video">
                        <div class="youtube-player">
                            <div data-id="{video_id}" data-type="youtube-video">
                                <img src="{thumbnail_url}" alt="{alt_text}">
                                <span class="youtube-player__button">
                                    <svg xmlns="http://www.w3.org/2000/svg" height="40px" viewBox="0 -960 960 960" width="40px" fill="#e3e3e3"><path d="m380-300 280-180-280-180v360ZM480-80q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z"/></svg>
                                </span>
                            </div>
                        </div>
                    </div>
                    """
                    html_content += youtube_html

            elif section[1] == "list":
                list_combobox, list_text_edit = section[2], section[3]

                list_type = list_combobox.currentText()
                list_items = list_text_edit.toPlainText().split("\n")

                list_html = f"""
                    <div class="list_item__col --text">
                        <{list_type} class="list_item__list">
                """

                for item in list_items:
                    if item.strip():
                        list_html += f"""
                            <li>{item.strip()}</li>
                        """

                list_html += f"""
                        </{list_type}>
                    </div>
                """
                html_content += list_html

        html_content += """
            </div>
        </div>
        """

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
                # os.remove(self.image_path)
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