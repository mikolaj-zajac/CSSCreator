import json
import os
import random
import shutil
from PyQt6.QtCore import Qt, QStandardPaths, QSize, QTimer, QPropertyAnimation, QRect, QEvent, QUrl
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QClipboard, QIcon, QTextCursor, QShortcut, QKeySequence, \
    QTextCharFormat
from PyQt6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QVBoxLayout, QPushButton, QScrollArea,
    QWidget, QHBoxLayout, QTextEdit, QSplitter, QStackedWidget, QComboBox, QMessageBox, QFileDialog, QLineEdit, QLayout,
    QDialog
)
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False
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
        self.editors = []
        self.current_editor = None
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

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Uwaga!",
            "Czy napewno chcesz zamknąć aplikacje?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

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

        self.preview_button = QPushButton("Podgląd HTML")
        self.preview_button.setStyleSheet("""
                background-color: #6c757d; 
                color: white; 
                padding: 10px; 
                border-radius: 5px;
            """)
        self.preview_button.clicked.connect(self.show_html_preview)
        self.right_layout.addWidget(self.preview_button)

        self.right_widget.setLayout(self.right_layout)

        self.html_edit = QTextEdit()
        self.html_edit.setReadOnly(True)
        self.right_layout.addWidget(self.html_edit)

        self.copy_html_button = QPushButton("Skopiuj kod HTML")
        self.right_layout.addWidget(self.copy_html_button)
        self.copy_html_button.clicked.connect(self.copy_html)

        self.splitter.addWidget(self.right_widget)
        self.splitter.setSizes([700, 300])

        self.stack.addWidget(self.editor_page)

    def show_html_preview(self):
        self.preview_dialog = QDialog(self)
        self.preview_dialog.setWindowTitle("Podgląd HTML")
        self.preview_dialog.resize(1920, 1080)

        layout = QVBoxLayout()

        try:
            from PyQt6.QtWebEngineWidgets import QWebEngineView
            self.web_view = QWebEngineView()
            html_content = self.html_edit.toPlainText()

            style = """
            <style>
            .longdescription__template__col.--text,
                .list_item__col.--text,
                .longdescription__headline,
                .longdescription__template__headline {
                  word-break: break-word; 
                  overflow-wrap: break-word; 
                  hyphens: auto; 
                }
            body {
              max-width: 1920px;
              margin: 0 auto; 
              width: 90%;
              
            }
            .longdescription {
              display: flex;
              flex-direction: column;
              align-items: center;
              
              padding-top: 4.8rem;
              scroll-margin-top: 11.2rem;
            }
            .longdescription__template,
                .longdescription__template__row.--layout-photo-text {
                  max-width: 100%; 
                }
            @media (min-width: 1024px) {
              .longdescription {
                padding-top: 10.2rem;
                scroll-margin-top: initial;
              }
            }
            .longdescription__template__col img,
                .longdescription__template__col video {
                  max-width: 90%;
                  height: auto;
                  display: block;
                }
                
            .longdescription.cm {
              margin-bottom: 0;
              overflow: initial;
            }
            
            .longdescription > * {
              width: 100%;
            }
            
            .longdescription > .longdescription__row {
              order: -2;
            }
            
            .longdescription__headline {
              font-size: 2.4rem;
              line-height: 2.4rem;
              margin-bottom: 3.2rem;
              text-transform: uppercase;
              font-weight: 700;
            }
            
            .longdescription__return_info {
              display: flex;
              margin-top: 3.2rem;
            }
            
            .longdescription__return_msg {
              border: 1px solid #ccc;
              border-radius: 8px;
              padding: 1.5rem;
            }
            
            .longdescription__template {
              display: grid;
              gap: 1.6rem;
            }
            
            @media (min-width: 1024px) {
              .longdescription__template {
                gap: 10.2rem;
                max-width: 1920px;
              }
            }
            
            .longdescription__template__row.--layout-photo-text {
              display: grid;
              gap: 1.6rem;
            }
            
            @media (min-width: 1024px) {
              .longdescription__template__row.--layout-photo-text {
                row-gap: 10.2rem;
              }
            
              .longdescription__template__row.--layout-photo-text .row {
                display: flex;
                align-items: center;
                gap: 1.6rem;
                margin: 0;
                flex-wrap: wrap;
              }
            
              
            
              .longdescription__template__row.--layout-photo-text .row > * {
                flex: 0 0 calc(50% - 0.8rem);
                max-width: calc(50% - 0.8rem);
                 box-sizing: border-box;
              }
            }
            
            .longdescription__template__col {
              display: flex;
              justify-content: center;
              align-items: center;
            }
            
            .longdescription__template__col img[alt] {
              background-color: #ccc;
              padding: 5.6rem;
              padding-left: 15.6rem;
              padding-right: 15.6rem;
              border: 3px dotted #444;
              color: #white;
            }
            
            .longdescription__template__col.--text {
              flex-direction: column;
              align-items: flex-start;
              justify-content: center;
              padding: 4.8rem;
              gap: 1.6rem;
              font-size: 1.6rem;
              line-height: 1.8;
              text-wrap: wrap;
            }
            
            .longdescription__template__col.--text .col__headline {
              font-size: 1.8rem;
              font-weight: 600;
              line-height: 1.3;
              text-transform: uppercase;
            }
            
            .longdescription__template__col.--text p {
              margin: 0;
              line-height: 1.8;
            }
            
            .longdescription__template__headline {
              font-size: 2.4rem;
              font-weight: 600;
              text-align: center;
              text-transform: uppercase;
            }
            
            .longdescription__template__list {
              list-style: none;
              padding-left: 0 !important;
            }
            
            .longdescription__template__list_item {
              border-top: 1px solid #ccc;
              margin-top: 3.2rem;
              padding-top: 3.2rem;
            }
            
            .list_item__row {
              display: grid;
              gap: 1.6rem;
              grid-template-columns: minmax(0, 1fr);
            }
            
            @media (min-width: 1024px) {
              .list_item__row {
                gap: 7.2rem;
                grid-template-columns: auto minmax(0, 1fr);
              }
            }
            
            .list_item__col.--text {
              display: grid;
              gap: 1.6rem;
            }
            
            .list_item__headline {
              font-size: 1.8rem;
              font-weight: 600;
              line-height: 1.8rem;
              text-transform: uppercase;
            }
            
            .list_item__list {
              list-style: none;
              padding: 0;
            }
            
            .list_item__list li {
              display: flex;
              align-items: flex-start;
              justify-content: flex-start;
            }
            
            .list_item__list li::before {
              content: '•';
              flex: 0 0 3.2rem;
              text-align: center;
            }

            </style>
            """
            if "</head>" in html_content:
                html_content = html_content.replace("</head>", style + "</head>")
            else:
                html_content = style + html_content

            self.web_view.setHtml(html_content)
            layout.addWidget(self.web_view)
        except ImportError:
            error_label = QLabel("Podgląd wymaga zainstalowanego PyQt6-WebEngine")
            layout.addWidget(error_label)

        close_button = QPushButton("Zamknij")

        close_button.clicked.connect(self.preview_dialog.close)
        layout.addWidget(close_button)

        self.preview_dialog.setLayout(layout)
        self.preview_dialog.exec()

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

        if hasattr(self, 'preview_button'):
            self.preview_button.setStyleSheet("""
                    background-color: #6c757d; 
                    color: white; 
                    padding: 10px; 
                    border-radius: 5px;
                """ if self.light_mode else """
                    background-color: #495057; 
                    color: white; 
                    padding: 10px; 
                    border-radius: 5px;
                """)

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
                    border: 2px dashed gray; padding: 20px; background-color: #e9ecef; color: black;
                """ if self.light_mode else """
                    border: 2px dashed gray; padding: 20px; background-color: #444; color: white;
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


            # elif section[1] == "youtube":
            #     video_id_edit, thumbnail_url_edit, alt_text_edit = section[2], section[3], section[4]
            #
            #     video_id_edit.setStyleSheet("""
            #         background-color: #e9ecef;
            #         color: black;
            #         padding: 5px;
            #     """ if self.light_mode else """
            #         background-color: #222;
            #         color: white;
            #         padding: 5px;
            #     """)
            #
            #     thumbnail_url_edit.setStyleSheet("""
            #         background-color: #e9ecef;
            #         color: black;
            #         padding: 5px;
            #     """ if self.light_mode else """
            #         background-color: #222;
            #         color: white;
            #         padding: 5px;
            #     """)
            #
            #     alt_text_edit.setStyleSheet("""
            #         background-color: #e9ecef;
            #         color: black;
            #         padding: 5px;
            #     """ if self.light_mode else """
            #         background-color: #222;
            #         color: white;
            #         padding: 5px;
            #     """)

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
            "border: 2px dashed gray; padding: 20px; background-color: #e9ecef; color: black;" if self.light_mode else
            "border: 2px dashed gray; padding: 20px; background-color: #444; color: white;"
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

        def handle_key_press(event):
            cursor = text_edit.textCursor()

            if event.key() == Qt.Key.Key_Tab:
                current_line = cursor.block().text()
                cursor_pos_in_block = cursor.positionInBlock()

                if cursor_pos_in_block == 0 or (cursor_pos_in_block > 0 and current_line[
                                                                            :cursor_pos_in_block].strip() == "⤷" * cursor_pos_in_block):

                    red_format = QTextCharFormat()
                    red_format.setForeground(QColor("red"))
                    cursor.insertText("⤷", red_format)
                    cursor.setCharFormat(QTextCharFormat())
                    text_edit.setTextCursor(cursor)
                else:
                    cursor.insertText("    ")
                return True

            return False

        text_edit.installEventFilter(self)

        def eventFilter(obj, event):
            if obj == text_edit and event.type() == QEvent.Type.KeyPress:
                if handle_key_press(event):
                    return True
            return super(type(self), self).eventFilter(obj, event)

        self.eventFilter = eventFilter

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
        # thumbnail_url_edit = QLineEdit()
        # thumbnail_url_edit.setPlaceholderText("Wpisz URL miniaturki (maxresdefault)")
        # thumbnail_url_edit.setStyleSheet(
        #     "background-color: #e9ecef; color: black; padding: 5px; border-radius: 5px;" if self.light_mode else
        #     "background-color: #222; color: white; padding: 5px; border-radius: 5px;"
        # )
        # alt_text_edit = QLineEdit()
        # alt_text_edit.setPlaceholderText("Wpisz tekst zastępczy")
        # alt_text_edit.setStyleSheet(
        #     "background-color: #e9ecef; color: black; padding: 5px; border-radius: 5px;" if self.light_mode else
        #     "background-color: #222; color: white; padding: 5px; border-radius: 5px;"
        # )

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
        # youtube_layout.addWidget(thumbnail_url_edit)
        # youtube_layout.addWidget(alt_text_edit)

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(move_up_button)
        buttons_layout.addWidget(move_down_button)
        buttons_layout.addWidget(delete_button)

        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        youtube_layout.addWidget(buttons_widget)
        thumbnail_url = ""
        alt_text = "Film Youtube"
        video_id_edit.textChanged.connect(lambda: self.process_youtube_url(video_id_edit, thumbnail_url))
        # thumbnail_url_edit.textChanged.connect(self.update_html)
        # alt_text_edit.textChanged.connect(self.update_html)

        self.scroll_layout.addLayout(youtube_layout)
        self.sections.append((youtube_layout, "youtube", video_id_edit, thumbnail_url, alt_text))

        self.update_html()

    def process_youtube_url(self, video_id_edit, thumbnail_url):
        full_url = video_id_edit.text()
        import re
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", full_url)
        video_id = match.group(1) if match else full_url.strip()

        thumbnail_url = f'https://www.youtube.com/embed/{video_id}?vq=hd1080'
        self.update_html()


    def add_list(self, list_type):
        list_layout = QHBoxLayout()

        list_combobox = QComboBox()
        list_combobox.addItems(["ul", "ol"])
        list_combobox.setCurrentText(list_type)
        list_combobox.setStyleSheet(
            "background-color: #e9ecef; color: black; padding: 10px; font-size: 14px;" if self.light_mode else
            "background-color: #222; color: white; padding: 10px; font-size: 14px;"
        )
        list_combobox.currentTextChanged.connect(self.update_html)

        list_text_edit = QTextEdit()
        list_text_edit.setPlaceholderText("Wpisz elementy listy, każdy w nowej linii...")
        list_text_edit.textChanged.connect(self.update_html)
        list_text_edit.setStyleSheet(
            "background-color: #e9ecef; color: black; border-radius: 5px; padding: 5px;" if self.light_mode else
            "background-color: #222; color: white; border-radius: 5px; padding: 5px;"
        )

        def handle_key_press(event):
            cursor = list_text_edit.textCursor()

            if event.key() == Qt.Key.Key_Tab:
                current_line = cursor.block().text()
                cursor_pos_in_block = cursor.positionInBlock()

                if cursor_pos_in_block == 0 or (cursor_pos_in_block > 0 and current_line[:cursor_pos_in_block].strip() == "⤷" * cursor_pos_in_block):

                    red_format = QTextCharFormat()
                    red_format.setForeground(QColor("red"))
                    cursor.insertText("⤷", red_format)
                    cursor.setCharFormat(QTextCharFormat())
                    list_text_edit.setTextCursor(cursor)
                else:
                    cursor.insertText("    ")
                return True

            return False

        list_text_edit.installEventFilter(self)

        def eventFilter(obj, event):
            if obj == list_text_edit and event.type() == QEvent.Type.KeyPress:
                if handle_key_press(event):
                    return True
            return super(type(self), self).eventFilter(obj, event)

        self.eventFilter = eventFilter

        delete_button = QPushButton("Usuń Sekcję")
        delete_button.setStyleSheet(
            "background-color: #FF4C4C; color: black; padding: 5px; border-radius: 5px;" if self.light_mode else
            "background-color: #FF4C4C; color: white; padding: 5px; border-radius: 5px;"
        )
        delete_button.clicked.connect(lambda: self.delete_section(list_layout))

        move_up_button = QPushButton("↑")
        move_up_button.setStyleSheet(
            "background-color: #6395ED; color: black; padding: 5px; border-radius: 5px;" if self.light_mode else
            "background-color: #4567BB; color: white; padding: 5px; border-radius: 5px;"
        )
        move_up_button.clicked.connect(lambda: self.move_section(list_layout, -1))

        move_down_button = QPushButton("↓")
        move_down_button.setStyleSheet(
            "background-color: #6395ED; color: black; padding: 5px; border-radius: 5px;" if self.light_mode else
            "background-color: #4567BB; color: white; padding: 5px; border-radius: 5px;"
        )
        move_down_button.clicked.connect(lambda: self.move_section(list_layout, 1))

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
        index_to_remove = None
        for i, section in enumerate(self.sections):
            if section[0] == section_layout:
                index_to_remove = i
                section_widgets = []
                for j in range(section_layout.count()):
                    item = section_layout.itemAt(j)
                    widget = item.widget()
                    if widget:
                        section_widgets.append(widget)
                        widget.hide()

                confirmation_layout = QVBoxLayout()
                confirmation_label = QLabel("Czy na pewno chcesz usunąć tą sekcję?")
                confirmation_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
                confirmation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                confirmation_layout.addWidget(confirmation_label)

                button_layout = QHBoxLayout()
                yes_button = QPushButton("Tak")
                no_button = QPushButton("Nie")

                yes_button.setStyleSheet(
                    "background-color: #FF4C4C; color: white; padding: 10px; font-size: 14px; border-radius: 5px;")
                no_button.setStyleSheet(
                    "background-color: #4CAF50; color: white; padding: 10px; font-size: 14px; border-radius: 5px;")

                button_layout.addWidget(yes_button)
                button_layout.addWidget(no_button)
                confirmation_layout.addLayout(button_layout)

                confirmation_widget = QWidget()
                confirmation_widget.setLayout(confirmation_layout)
                confirmation_widget.setStyleSheet("background-color: #8f2f2f; padding: 10px; border-radius: 5px;")

                parent_layout = section_layout.parentWidget().layout()
                if parent_layout:
                    confirmation_index = -1
                    for j in range(parent_layout.count()):
                        if parent_layout.itemAt(j).layout() == section_layout:
                            confirmation_index = j
                            break
                    if confirmation_index >= 0:
                        parent_layout.insertWidget(confirmation_index + 1, confirmation_widget)

                def confirm_delete():
                    if index_to_remove is not None:
                        self.sections.pop(index_to_remove)
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
                    confirmation_widget.deleteLater()
                    self.update_html()

                def cancel_delete():
                    confirmation_widget.deleteLater()
                    for widget in section_widgets:
                        widget.show()

                yes_button.clicked.connect(confirm_delete)
                no_button.clicked.connect(cancel_delete)
                return

    def _get_focused_text_edit(self):
        try:
            widget = QApplication.focusWidget()
            if isinstance(widget, QTextEdit) and widget != self.html_edit:
                return widget
            return None
        except:
            return None

    def _safe_toggle_bold(self):
        if editor := self._get_focused_text_edit():
            cursor = editor.textCursor()
            fmt = cursor.charFormat()
            fmt.setFontWeight(QFont.Weight.Bold if fmt.fontWeight() != QFont.Weight.Bold
                              else QFont.Weight.Normal)
            cursor.mergeCharFormat(fmt)

    def _safe_toggle_italic(self):
        if editor := self._get_focused_text_edit():
            cursor = editor.textCursor()
            fmt = cursor.charFormat()
            fmt.setFontItalic(not fmt.fontItalic())
            cursor.mergeCharFormat(fmt)

    def _safe_toggle_underline(self):
        if editor := self._get_focused_text_edit():
            cursor = editor.textCursor()
            fmt = cursor.charFormat()
            fmt.setFontUnderline(not fmt.fontUnderline())
            cursor.mergeCharFormat(fmt)

    def _safe_paste_plain_text(self):
        if editor := self._get_focused_text_edit():
            editor.insertPlainText(QApplication.clipboard().text())

    def register_shortcuts(self):
        # Keep Ctrl+Z as is
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.undo_action)

        # Formatting shortcuts - will work on any focused QTextEdit that isn't html_edit
        QShortcut(QKeySequence("Ctrl+B"), self).activated.connect(
            self._safe_toggle_bold
        )
        QShortcut(QKeySequence("Ctrl+I"), self).activated.connect(
            self._safe_toggle_italic
        )
        QShortcut(QKeySequence("Ctrl+U"), self).activated.connect(
            self._safe_toggle_underline
        )
        QShortcut(QKeySequence("Ctrl+Shift+V"), self).activated.connect(
            self._safe_paste_plain_text
        )

    def paste_plain_text_to_focused_widget(self):
        focused_widget = QApplication.focusWidget()
        if isinstance(focused_widget, (QTextEdit, QLineEdit)):
            clipboard = QApplication.clipboard()
            plain_text = clipboard.text(QClipboard.Mode.Clipboard)
            focused_widget.insertPlainText(plain_text)

    def _toggle_text_format(self, editor, format_type):
        if editor is None:
            return

        cursor = editor.textCursor()
        fmt = cursor.charFormat()

        if format_type == "bold":
            fmt.setFontWeight(QFont.Weight.Bold if fmt.fontWeight() != QFont.Weight.Bold
                              else QFont.Weight.Normal)
        elif format_type == "italic":
            fmt.setFontItalic(not fmt.fontItalic())
        elif format_type == "underline":
            fmt.setFontUnderline(not fmt.fontUnderline())

        cursor.mergeCharFormat(fmt)
        editor.setCurrentCharFormat(fmt)

    def _paste_plain_text(self, editor):
        if editor is None:
            return

        clipboard = QApplication.clipboard()
        editor.insertPlainText(clipboard.text())

    def _paste_to_focused(self):
        focused = QApplication.focusWidget()
        if isinstance(focused, (QTextEdit, QLineEdit)) and focused != self.html_edit:  # Only for editable fields
            clipboard = QApplication.clipboard()
            focused.insertPlainText(clipboard.text())

    def undo_action(self):
        self.html_edit.undo()

    def update_html(self):
        html_content = """
                        <div class="longdescription__template">
                            <div class="longdescription__template__row --layout-photo-text">
                        """

        for section in self.sections:
            if section[1] == "section":
                image_label, text_edit, direction = section[2], section[3], section[5]

                text_content = text_edit.toPlainText()
                lines = text_content.split('\n')
                html_lines = []
                current_depth = 0
                in_paragraph = False
                paragraph_lines = []

                for line in lines:
                    line = line.rstrip()
                    arrows = len(line) - len(line.lstrip('⤷'))
                    content = line.lstrip('⤷').strip()

                    if arrows > 0:
                        if paragraph_lines:
                            html_lines.append(f"<p>{'<br>'.join(paragraph_lines)}</p>")
                            paragraph_lines = []
                            in_paragraph = False

                        while current_depth > arrows:
                            html_lines.append("</ul>")
                            current_depth -= 1

                        while current_depth < arrows:
                            html_lines.append("<ul>")
                            current_depth += 1

                        html_lines.append(f"<li>{content}</li>")
                    else:
                        if current_depth > 0:
                            html_lines.append("</ul>" * current_depth)
                            current_depth = 0
                        paragraph_lines.append(line)
                        in_paragraph = True

                if paragraph_lines:
                    html_lines.append(f"<p>{'<br>'.join(paragraph_lines)}</p>")
                elif current_depth > 0:
                    html_lines.append("</ul>" * current_depth)

                text_html = f"""<div class="longdescription__template__col --text">
                {''.join(html_lines)}
                </div>"""

                text_html = f"""<div class="longdescription__template__col --text">
                {''.join(html_lines)}
                </div>"""

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
                video_id_edit, thumbnail_url, alt_text = section[2], section[3], section[4]

                video_id = video_id_edit.text().strip()
                # thumbnail_url = thumbnail_url_edit.text().strip()
                # alt_text = alt_text_edit.text().strip()

                if video_id :
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

                list_html = f"<div class=\"list_item__col --text\">\n"

                previous_depth = 0

                for item in list_items:

                    stripped_item = item.strip()

                    current_depth = stripped_item.count("⤷")

                    if stripped_item:

                        stripped_item = stripped_item.replace("⤷", "").strip()

                        if current_depth == 0:

                            if previous_depth > 0:
                                list_html += f"{' ' * (4 * previous_depth)}</{list_type}>\n" * previous_depth

                                previous_depth = 0

                            list_html += f"<p>{stripped_item}</p>\n"


                        else:

                            if previous_depth == 0:

                                list_html += f"<{list_type} class=\"list_item__list\">\n"

                            elif current_depth > previous_depth:

                                list_html += f"{' ' * (4 * previous_depth)}<{list_type}>\n" * (
                                            current_depth - previous_depth)

                            elif current_depth < previous_depth:

                                list_html += f"{' ' * (4 * (current_depth + 1))}</{list_type}>\n" * (
                                            previous_depth - current_depth)

                            list_html += f"{' ' * (4 * current_depth)}<li>{stripped_item}</li>\n"

                            previous_depth = current_depth

                if previous_depth > 0:
                    list_html += f"{' ' * (4 * previous_depth)}</{list_type}>\n" * previous_depth

                list_html += "</div>\n"

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
            self.confirmation_widget = None
            self.show_red_x = False

        def create_directory_on_start(self):
            desktop_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
            directory_name = "Zdjecia Opisow Dlugich"
            target_directory = os.path.join(desktop_path, directory_name)
            if not os.path.exists(target_directory):
                os.makedirs(target_directory)
            return target_directory

        def mousePressEvent(self, event):
            if self.confirmation_mode:
                return

            if event.button() == Qt.MouseButton.LeftButton:
                if self.image_path:
                    self.enable_confirmation_mode()
                else:
                    file_dialog = QFileDialog()
                    desktop_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
                    file_dialog.setDirectory(desktop_path)
                    file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)")
                    if file_dialog.exec():
                        selected_file = file_dialog.selectedFiles()
                        if selected_file:
                            self.copy_and_display_image(selected_file[0])

        def enable_confirmation_mode(self):
            if not self.confirmation_widget:
                self.confirmation_widget = QWidget(self)
                self.confirmation_widget.setStyleSheet("background-color: rgba(125, 0, 0, 180);")
                self.confirmation_widget_layout = QVBoxLayout(self.confirmation_widget)
                self.confirmation_widget_layout.setContentsMargins(10, 10, 10, 10)

                message_label = QLabel("Czy na pewno chcesz usunąć?")
                message_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
                message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.confirmation_widget_layout.addWidget(message_label)

                button_layout = QHBoxLayout()
                yes_button = QPushButton("Tak")
                no_button = QPushButton("Nie")
                yes_button.setStyleSheet("background-color: #FF4C4C; color: white; border-radius: 5px; padding: 10px;")
                no_button.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 5px; padding: 10px;")

                yes_button.clicked.connect(self.delete_image)
                no_button.clicked.connect(self.cancel_confirmation_mode)

                button_layout.addWidget(yes_button)
                button_layout.addWidget(no_button)
                self.confirmation_widget_layout.addLayout(button_layout)

            self.show_red_x = False
            self.update()
            self.confirmation_widget.setGeometry(self.rect())
            self.confirmation_mode = True
            self.confirmation_widget.show()

        def cancel_confirmation_mode(self):
            if self.confirmation_widget:
                self.confirmation_widget.hide()
            self.confirmation_mode = False

        def delete_image(self):
            try:
                if not self.image_path or not os.path.isfile(self.image_path):
                    return
                self.image_path = ""
                self.setPixmap(QPixmap())
                self.setText("Przeciągnij obraz tutaj lub kliknij, aby wybrać plik")
                self.setStyleSheet("border: 2px dashed gray; padding: 20px; background-color: #444; color: white;")
                self.cancel_confirmation_mode()
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
                new_file_name = f"{os.path.splitext(original_name)[0]}_{random_digits}.webp"
                custom_folder = os.path.join("data", "include", "cms", "img-longdescription")
                os.makedirs(custom_folder, exist_ok=True)
                destination_path = os.path.join(custom_folder, new_file_name)
                shutil.copy(source_path, destination_path)
                destination_path = os.path.join(self.target_directory, new_file_name)
                shutil.copy(source_path, destination_path)
                self.image_path = destination_path
                self.setPixmap(QPixmap(self.image_path).scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio))
                self.show_red_x = False
                self.confirmation_mode = False
                if self.editor and hasattr(self.editor, "update_html"):
                    self.editor.update_html()
            except Exception as e:
                print(f"Error during copy_and_display_image: {e}")

        def enterEvent(self, event):
            if self.image_path and not self.confirmation_mode:
                self.show_red_x = True
                self.update()

        def leaveEvent(self, event):
            if self.image_path and not self.confirmation_mode:
                self.show_red_x = False
                self.update()

        def resizeEvent(self, event):
            super().resizeEvent(event)
            if self.confirmation_widget:
                self.confirmation_widget.setGeometry(self.rect())

        def paintEvent(self, event):
            super().paintEvent(event)
            if self.show_red_x:
                painter = QPainter(self)
                painter.setPen(QColor(255, 0, 0))
                painter.setBrush(QColor(255, 0, 0, 100))
                painter.drawRect(0, 0, self.width(), self.height())
                font = QFont("Arial", 36, QFont.Weight.Bold)
                painter.setFont(font)
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "X")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = HtmlEditor()
    window.show()
    sys.exit(app.exec())