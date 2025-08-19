import os
import re
import sys
import json
import platform
import subprocess
import threading
import webbrowser
from .styles.theme_manager import get_theme_manager
from .field_config_widget import FieldConfigWidget
from .data_generation_thread import DataGenerationThread
from .configuration_dialogs import SaveConfigurationDialog, LoadConfigurationDialog
from .dataset_warning_dialog import DatasetWarningDialog
from ..services.gui_file_writer import write_for_gui, get_default_export_directory
from ..generators.generator import GeneratorFormats
from ..services.available_generators import get_available_generators
from ..services.data_generator import DataGenerator
from ..localization.manager import get_string, set_language, get_current_language, get_available_languages
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QSpinBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QGroupBox, QCheckBox,
                             QLineEdit, QTextEdit, QSplitter, QScrollArea,
                             QMessageBox, QTabWidget, QApplication, QFileDialog,
                             QInputDialog, QListWidget, QDialog, QMenuBar)
from PyQt6.QtCore import Qt, QTimer, QSize, QProcess
from PyQt6.QtGui import QFont, QIcon, QAction, QKeySequence, QPixmap


def get_resource_path(relative_path):
    """Get the absolute path to a resource file within the package."""
    base_path = Path(
        __file__).parent.parent  # mockachu package root
    return str(base_path / relative_path)


class MainWindow(QMainWindow):
    BUTTON_SIZE = (35, 35)
    ICON_SIZE = QSize(20, 20)
    SMALL_ICON_SIZE = QSize(18, 18)
    LARGE_DATASET_THRESHOLD = 1000000
    MAX_ROWS_LIMIT = 1000000000
    DEFAULT_PREVIEW_ROWS = 100
    TIMER_INTERVALS = {
        'ready_message': 3500,
        'loading_animation': 500,
        'initial_ready': 1000,
        'status_message': 3000,
        'copy_status': 5000
    }

    SPLITTER_SIZES = [400, 1000]
    MAX_PREVIEW_ROWS = 1000
    SQL_BATCH_LIMITS = (1, 10000, 50)  # min, max, default

    ERROR_MESSAGES = {
        'no_fields': "errors.no_fields",
        'no_format': "errors.no_format",
        'no_field_name': "errors.no_field_name",
        'invalid_field': "errors.invalid_field",
        'no_fields_to_save': "errors.no_fields_to_save",
        'no_saved_configs': "errors.no_saved_configs"
    }

    def __init__(self):
        super().__init__()
        self.data_generator = DataGenerator()
        self.fields = []
        self.field_number_counter = 1
        self.available_generators = get_available_generators()
        self.current_preview_data = []
        self.original_preview_data = []
        self.last_preview_row_count = self.DEFAULT_PREVIEW_ROWS

        self.config_file_path = self.get_config_file_path()
        self.saved_configurations = self.load_configurations_from_disk()

        # API Server management
        self.api_server_process = None
        self.api_server_instance = None
        self.api_server_port = 8843
        self.api_server_host = "localhost"

        self.setWindowTitle(get_string("app.title"))
        icon_paths = [
            get_resource_path("ui/res/logo_app.png"),
            get_resource_path("ui/res/logo_rounded_1024x1024.png"),
            get_resource_path("ui/res/logo_rounded_512x512.png"),
            get_resource_path("ui/res/logo_rounded_256x256.png"),
            get_resource_path("ui/res/logo_rounded_128x128.png"),
            get_resource_path("ui/res/logo_rounded_64x64.png"),
            get_resource_path("ui/res/logo_rounded_32x32.png"),
            get_resource_path("ui/res/logo_rounded_16x16.png")
        ]

        window_icon = QIcon()
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                window_icon.addFile(icon_path)

        if not window_icon.isNull():
            self.setWindowIcon(window_icon)
        self.setGeometry(100, 100, 1400, 900)
        self.showMaximized()

        self.theme_manager = get_theme_manager(QApplication.instance())
        self.theme_manager.apply_theme()

        self.setup_ui()
        self.setup_connections()

        # Start API server automatically on startup
        self.start_api_server_on_startup()

        self.add_field()

        self.update_generate_button_state()

        self.on_preview_tab_changed()

        self._ready_message_timer = QTimer()
        self._ready_message_timer.timeout.connect(self._update_ready_message)
        self._is_ready_message_active = False
        self._last_temporary_message = ""

        QTimer.singleShot(
            self.TIMER_INTERVALS['initial_ready'], self._start_ready_message)

    def get_monospace_font(self, size=12):
        """Get a cross-platform monospace font with proper fallbacks."""
        system = platform.system()

        if system == "Darwin":  # macOS
            font_families = ["Monaco", "Menlo", "Consolas", "monospace"]
        elif system == "Windows":
            font_families = ["Consolas", "Courier New", "monospace"]
        else:  # Linux and others
            font_families = ["DejaVu Sans Mono",
                             "Liberation Mono", "Consolas", "monospace"]

        # Try each font family until we find one that exists
        for font_family in font_families:
            font = QFont(font_family, size)
            font.setStyleHint(QFont.StyleHint.Monospace)
            if font.exactMatch() or font_family == "monospace":
                return font

        # Fallback to system default monospace
        font = QFont()
        font.setFamily("monospace")
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setPointSize(size)
        return font

    def _create_styled_button(self, icon_path, tooltip, size=None, icon_size=None, min_height=None):

        button = QPushButton()
        button.setIcon(QIcon(icon_path))
        button.setToolTip(tooltip)

        if size:
            if isinstance(size, tuple) and len(size) == 2:
                width, height = size
                if width is None and height is None:
                    pass
                elif width is None:
                    button.setFixedHeight(height)
                elif height is None:
                    button.setFixedWidth(width)
                else:
                    button.setFixedSize(width, height)
            else:
                button.setFixedSize(*self.BUTTON_SIZE)
        else:
            button.setFixedSize(*self.BUTTON_SIZE)

        if min_height:
            button.setMinimumHeight(min_height)

        icon_size = icon_size or self.ICON_SIZE
        button.setIconSize(icon_size)

        return button

    def _schedule_ready_message(self, delay=None):

        delay = delay or self.TIMER_INTERVALS['ready_message']
        QTimer.singleShot(delay, self._start_ready_message)

    def _show_validation_warning(self, message_key, *args):

        message = get_string(self.ERROR_MESSAGES[message_key], *args)
        QMessageBox.warning(self, get_string(
            "errors.validation_title"), message)

    def _create_spinbox(self, min_val, max_val, value, width=None):

        spinbox = QSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(value)
        if width:
            spinbox.setMinimumWidth(width)
        return spinbox

    def setup_ui(self):
        # Setup menu bar first
        self.setup_menu_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        self.setup_left_panel(splitter)

        self.setup_right_panel(splitter)

        splitter.setSizes(self.SPLITTER_SIZES)

        self.setup_status_bar()

    def setup_menu_bar(self):
        """Setup the application menu bar with About dialog."""
        menubar = self.menuBar()

        # Create app menu (will show as app name on macOS)
        app_menu = menubar.addMenu(get_string("app.title"))

        # Add About action
        about_action = QAction(get_string("menu.about"), self)
        # macOS will handle this specially
        about_action.setMenuRole(QAction.MenuRole.AboutRole)
        about_action.triggered.connect(self.show_about_dialog)
        app_menu.addAction(about_action)

        # Add separator
        app_menu.addSeparator()

        # Add Quit action
        quit_action = QAction(get_string("menu.quit"), self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        # macOS will handle this specially
        quit_action.setMenuRole(QAction.MenuRole.QuitRole)
        quit_action.triggered.connect(self.close)
        app_menu.addAction(quit_action)

    def show_about_dialog(self):
        """Show the About dialog with app information and credits."""
        from ..version import __version__

        about_text = f"""
<h2>{get_string("app.title")}</h2>
<p><strong>{get_string("about.version")}:</strong> {__version__}</p>
<p><strong>{get_string("about.description")}:</strong></p>
<p>{get_string("about.app_description")}</p>

<p><strong>{get_string("about.features")}:</strong></p>
<ul>
<li>{get_string("about.feature_gui")}</li>
<li>{get_string("about.feature_api")}</li>
<li>{get_string("about.feature_formats")}</li>
<li>{get_string("about.feature_generators")}</li>
</ul>

<p><strong>{get_string("about.credits")}:</strong></p>
<p>{get_string("about.icons_credit")}: <a href="https://icons8.com">Icons8</a></p>
<p>{get_string("about.license")}: MIT License</p>

<p><strong>{get_string("about.links")}:</strong></p>
<p>• <a href="https://github.com/sahzudin/mock-data-generator">GitHub Repository</a></p>
<p>• <a href="http://localhost:8843/">API Documentation</a></p>
        """

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(get_string("about.title"))
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(about_text)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        # Set icon if available
        icon_path = get_resource_path("res/icon.png")
        if os.path.exists(icon_path):
            msg_box.setIconPixmap(QPixmap(icon_path).scaled(
                64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        msg_box.exec()

    def setup_left_panel(self, parent):

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(8)

        self.settings_group = QGroupBox(
            get_string("ui.groups.generation_settings"))
        self.settings_group.setObjectName("groupBox")
        settings_layout = QVBoxLayout(self.settings_group)

        settings_row = QHBoxLayout()
        settings_row.setSpacing(8)

        self.rows_label = QLabel(get_string("ui.labels.rows"))
        settings_row.addWidget(self.rows_label)
        self.rows_spinbox = self._create_spinbox(
            1, self.MAX_ROWS_LIMIT, self.DEFAULT_PREVIEW_ROWS, 100)
        settings_row.addWidget(self.rows_spinbox)

        settings_row.addSpacing(8)

        self.zip_checkbox = QCheckBox(get_string("ui.checkboxes.zip"))
        self.zip_checkbox.setToolTip(get_string("ui.tooltips.zip"))
        settings_row.addWidget(self.zip_checkbox)

        settings_row.addStretch()  # Push everything to the left
        settings_layout.addLayout(settings_row)

        format_row = QHBoxLayout()
        format_row.setSpacing(12)
        self.formats_label = QLabel(get_string("ui.labels.formats"))
        format_row.addWidget(self.formats_label)

        self.json_checkbox = QCheckBox(get_string("ui.checkboxes.json"))
        format_row.addWidget(self.json_checkbox)

        self.csv_checkbox = QCheckBox(get_string("ui.checkboxes.csv"))
        format_row.addWidget(self.csv_checkbox)

        self.xml_checkbox = QCheckBox(get_string("ui.checkboxes.xml"))
        format_row.addWidget(self.xml_checkbox)

        self.html_checkbox = QCheckBox(get_string("ui.checkboxes.html"))
        format_row.addWidget(self.html_checkbox)

        sql_container = QHBoxLayout()
        sql_container.setContentsMargins(0, 0, 0, 0)
        self.sql_checkbox = QCheckBox(get_string("ui.checkboxes.sql"))
        sql_container.addWidget(self.sql_checkbox)

        self.sql_batch_spinbox = self._create_spinbox(
            *self.SQL_BATCH_LIMITS, 60)
        self.sql_batch_spinbox.setMaximumWidth(80)
        self.sql_batch_spinbox.setEnabled(False)
        self.sql_batch_spinbox.setToolTip(
            get_string("ui.tooltips.sql_batch_size"))
        sql_container.addWidget(self.sql_batch_spinbox)

        sql_widget = QWidget()
        sql_widget.setLayout(sql_container)
        format_row.addWidget(sql_widget)

        format_row.addStretch()  # Push everything to the left
        settings_layout.addLayout(format_row)

        left_layout.addWidget(self.settings_group)

        self.fields_group = QGroupBox(
            get_string("ui.groups.fields_configuration"))
        self.fields_group.setObjectName("groupBox")
        fields_layout = QVBoxLayout(self.fields_group)
        fields_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        self.add_field_btn = self._create_styled_button(
            get_resource_path("ui/res/icons8-plus-math-100.png"),
            get_string("ui.buttons.add_field"),
            size=(None, 35)
        )
        self.add_field_btn.setObjectName("primaryButton")
        self.add_field_btn.clicked.connect(self.add_field)
        buttons_layout.addWidget(self.add_field_btn, 45)

        config_layout = QHBoxLayout()

        save_config_btn = self._create_styled_button(
            get_resource_path("ui/res/icons8-add-to-favorites-100.png"),
            get_string("ui.tooltips.save_config")
        )
        save_config_btn.setObjectName("configButton")
        save_config_btn.clicked.connect(self.save_configuration)
        config_layout.addWidget(save_config_btn)

        load_config_btn = self._create_styled_button(
            get_resource_path("ui/res/icons8-star-100.png"),
            get_string("ui.tooltips.load_config")
        )
        load_config_btn.setObjectName("configButton")
        load_config_btn.clicked.connect(self.load_configuration)
        config_layout.addWidget(load_config_btn)

        import_config_btn = self._create_styled_button(
            get_resource_path("ui/res/icons8-import-100.png"),
            get_string("ui.tooltips.import_config"),
            icon_size=self.SMALL_ICON_SIZE
        )
        import_config_btn.setObjectName("configButton")
        import_config_btn.clicked.connect(self.import_configuration)
        config_layout.addWidget(import_config_btn)

        export_config_btn = self._create_styled_button(
            get_resource_path("ui/res/icons8-export-100.png"),
            get_string("ui.tooltips.export_config"),
            icon_size=self.SMALL_ICON_SIZE
        )
        export_config_btn.setObjectName("configButton")
        export_config_btn.clicked.connect(self.export_configuration)
        config_layout.addWidget(export_config_btn)

        # Add API documentation button
        api_docs_btn = self._create_styled_button(
            get_resource_path("ui/res/icons8-text-100.png"),
            "Open API Documentation (Swagger)",
            icon_size=self.SMALL_ICON_SIZE
        )
        api_docs_btn.setObjectName("configButton")
        api_docs_btn.clicked.connect(self.open_api_documentation)
        config_layout.addWidget(api_docs_btn)

        buttons_layout.addLayout(config_layout, 45)  # 45% stretch factor

        remove_all_btn = self._create_styled_button(
            get_resource_path("ui/res/icons8-trash-can-100.png"),
            get_string("ui.tooltips.remove_all_fields")
        )
        remove_all_btn.setObjectName("removeButton")
        remove_all_btn.clicked.connect(self.remove_all_fields)
        buttons_layout.addWidget(remove_all_btn, 10)

        fields_layout.addLayout(buttons_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        self.fields_widget = QWidget()
        self.fields_layout = QVBoxLayout(self.fields_widget)
        self.fields_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.fields_layout.setContentsMargins(0, 0, 8, 0)  # Remove margins
        self.fields_layout.setSpacing(8)

        scroll_area.setWidget(self.fields_widget)
        fields_layout.addWidget(scroll_area)

        left_layout.addWidget(self.fields_group)

        generation_layout = QHBoxLayout()
        generation_layout.setSpacing(8)  # Set spacing to 8px

        self.generate_btn = self._create_styled_button(
            get_resource_path("ui/res/icons8-play-100.png"),
            get_string("ui.tooltips.generate_mock_data"),
            size=(None, None),
            min_height=35
        )
        self.generate_btn.setObjectName("generateButton")
        self.generate_btn.clicked.connect(self.generate_data)
        generation_layout.addWidget(self.generate_btn, 9)

        # API Copy button
        copy_api_btn = self._create_styled_button(
            get_resource_path("ui/res/icons8-clipboard-100.png"),
            get_string("ui.tooltips.copy_api_request")
        )
        copy_api_btn.setObjectName("secondaryButton")
        copy_api_btn.clicked.connect(self.copy_api_request_to_clipboard)
        generation_layout.addWidget(copy_api_btn, 1)

        change_dir_btn = self._create_styled_button(
            get_resource_path("ui/res/icons8-folder-100.png"),
            get_string("ui.tooltips.change_save_directory")
        )
        change_dir_btn.setObjectName("secondaryButton")
        change_dir_btn.clicked.connect(self.change_export_directory)
        generation_layout.addWidget(change_dir_btn, 1)

        left_layout.addLayout(generation_layout)

        self.export_dir_label = QLabel()
        self.export_dir_label.setVisible(False)  # Hidden from UI

        self.update_export_directory_display()

        parent.addWidget(left_panel)

    def setup_right_panel(self, parent):

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(8)

        self.preview_tabs = QTabWidget()

        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        # Make table read-only
        self.data_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.data_table.setStyleSheet("QTableWidget { border: none; }")

        self.text_previews = {}
        self.text_previews["JSON"] = QTextEdit()
        self.text_previews["CSV"] = QTextEdit()
        self.text_previews["XML"] = QTextEdit()
        self.text_previews["HTML"] = QTextEdit()
        self.text_previews["SQL"] = QTextEdit()

        for format_name, text_edit in self.text_previews.items():
            text_edit.setReadOnly(True)
            # Use cross-platform monospace font
            text_edit.setFont(self.get_monospace_font())
            text_edit.setVisible(False)
            text_edit.setStyleSheet("QTextEdit { border: none; }")

        self.preview_tabs.addTab(self.data_table, get_string("ui.tabs.table"))
        self.preview_tabs.addTab(
            self.text_previews["JSON"], get_string("ui.tabs.json"))
        self.preview_tabs.addTab(
            self.text_previews["CSV"], get_string("ui.tabs.csv"))
        self.preview_tabs.addTab(
            self.text_previews["XML"], get_string("ui.tabs.xml"))
        self.preview_tabs.addTab(
            self.text_previews["HTML"], get_string("ui.tabs.html"))
        self.preview_tabs.addTab(
            self.text_previews["SQL"], get_string("ui.tabs.sql"))

        self.format_tabs = {
            "JSON": self.text_previews["JSON"],
            "CSV": self.text_previews["CSV"],
            "XML": self.text_previews["XML"],
            "HTML": self.text_previews["HTML"],
            "SQL": self.text_previews["SQL"]
        }

        self.preview_tabs.currentChanged.connect(self.on_preview_tab_changed)

        right_layout.addWidget(self.preview_tabs)

        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 3, 0, 0)

        left_controls = QHBoxLayout()
        left_controls.setSpacing(8)

        self.refresh_btn = self._create_styled_button(
            get_resource_path("ui/res/icons8-refresh-100.png"),
            get_string("ui.tooltips.refresh_preview")
        )
        self.refresh_btn.clicked.connect(self.refresh_preview)
        left_controls.addWidget(self.refresh_btn)

        self.copy_btn = self._create_styled_button(
            get_resource_path("ui/res/icons8-clipboard-100.png"),
            get_string("ui.tooltips.copy_preview_data")
        )
        self.copy_btn.clicked.connect(self.copy_current_preview_to_clipboard)
        left_controls.addWidget(self.copy_btn)

        controls_layout.addLayout(left_controls)
        controls_layout.addStretch()

        right_controls = QHBoxLayout()
        self.preview_rows_label = QLabel(get_string("ui.labels.rows"))
        right_controls.addWidget(self.preview_rows_label)
        self.preview_rows_spinbox = self._create_spinbox(
            1, self.MAX_PREVIEW_ROWS, self.DEFAULT_PREVIEW_ROWS, 80)
        self.preview_rows_spinbox.setToolTip(
            f"Number of rows to preview, max {self.MAX_PREVIEW_ROWS}")
        self.preview_rows_spinbox.valueChanged.connect(
            self.on_preview_rows_changed)
        right_controls.addWidget(self.preview_rows_spinbox)

        controls_layout.addLayout(right_controls)
        right_layout.addLayout(controls_layout)

        parent.addWidget(right_panel)

    def setup_status_bar(self):

        self.status_bar = self.statusBar()

        self.footer_file_label = QLabel()
        from PyQt6.QtCore import Qt
        self.footer_file_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.footer_file_label.setVisible(False)
        self.footer_file_label.mousePressEvent = self.open_file_location
        self.status_bar.addPermanentWidget(self.footer_file_label)

    def setup_connections(self):

        self.json_checkbox.stateChanged.connect(self.on_format_changed)
        self.csv_checkbox.stateChanged.connect(self.on_format_changed)
        self.xml_checkbox.stateChanged.connect(self.on_format_changed)
        self.html_checkbox.stateChanged.connect(self.on_format_changed)
        self.sql_checkbox.stateChanged.connect(self.on_format_changed)
        self.sql_checkbox.stateChanged.connect(self.on_sql_checkbox_changed)

        self.sql_batch_spinbox.valueChanged.connect(self.on_sql_batch_changed)

    def on_sql_checkbox_changed(self):

        self.sql_batch_spinbox.setEnabled(self.sql_checkbox.isChecked())

    def on_sql_batch_changed(self):

        if self.sql_checkbox.isChecked() and self.current_preview_data:
            if "SQL" in self.text_previews:
                formatted_text = self.format_data_for_preview(
                    self.current_preview_data, "SQL")
                self.text_previews["SQL"].setPlainText(formatted_text)

    def on_preview_tab_changed(self):

        current_tab_index = self.preview_tabs.currentIndex()
        if current_tab_index < 0:
            self.copy_btn.setEnabled(False)
            self.copy_btn.setToolTip(get_string("ui.tooltips.no_preview"))
            return

        current_tab_text = self.preview_tabs.tabText(current_tab_index)

        is_table_view = current_tab_text == get_string("ui.tabs.table")
        self.copy_btn.setEnabled(not is_table_view)

        if is_table_view:
            self.copy_btn.setToolTip(get_string(
                "ui.tooltips.copy_not_available"))
        else:
            self.copy_btn.setToolTip(
                f"Copy {current_tab_text} preview to clipboard")

    def get_selected_formats(self):

        formats = []
        if self.json_checkbox.isChecked():
            formats.append("JSON")
        if self.csv_checkbox.isChecked():
            formats.append("CSV")
        if self.xml_checkbox.isChecked():
            formats.append("XML")
        if self.html_checkbox.isChecked():
            formats.append("HTML")
        if self.sql_checkbox.isChecked():
            formats.append("SQL")
        return formats

    def get_selected_format(self):

        formats = self.get_selected_formats()
        return formats[0] if formats else "JSON"

    def add_field(self):

        field_widget = FieldConfigWidget(
            self.available_generators,
            self.field_number_counter,
            self.remove_field,
            self.duplicate_field,
            self.move_field_up,
            self.move_field_down
        )
        self.field_number_counter += 1  # Increment counter for next field
        self.fields.append(field_widget)
        self.fields_layout.addWidget(field_widget)

        field_widget.field_changed.connect(self.on_field_modified)
        field_widget.field_name_changed.connect(
            self.update_field_name_in_preview)
        field_widget.field_data_changed.connect(self.update_single_field_data)
        field_widget.request_preview_refresh.connect(self.refresh_preview)
        field_widget.name_edit.textChanged.connect(
            self.update_generate_button_state)

        self.update_remove_button_states()

        QTimer.singleShot(
            50, lambda: self.focus_and_scroll_to_field(field_widget))

        self.add_field_to_preview(field_widget)

    def add_field_to_preview(self, field_widget):

        if not self.current_preview_data or not field_widget.is_valid():
            self.refresh_preview()  # Full refresh if no data or invalid field
            return

        try:
            field_name = field_widget.get_field_name()

            field_config = field_widget.get_field_config()
            original_config = field_config.copy()
            original_config["nullable_percentage"] = 0  # No nulls in original

            request = {
                "fields": [original_config],
                "rows": len(self.current_preview_data),
                "format": "JSON",
                "zip": False
            }

            new_field_original_data = self.data_generator.generate(request)

            for i, row in enumerate(self.original_preview_data):
                if i < len(new_field_original_data):
                    row[field_name] = new_field_original_data[i][field_name]

            for i, row in enumerate(self.current_preview_data):
                if i < len(new_field_original_data):
                    row[field_name] = new_field_original_data[i][field_name]

            self.apply_nullability_to_field(
                field_widget, self.current_preview_data)

            field_widget._last_config = field_config.copy()

            self.update_preview_display()

        except Exception as e:
            print(f"Error adding field to preview: {e}")
            self.refresh_preview()  # Fallback to full refresh

    def apply_nullability_to_field(self, field_widget, data_rows):

        import random

        field_name = field_widget.get_field_name()
        nullable_percentage = field_widget.nullable_slider.value()

        if nullable_percentage == 0:
            return
        elif nullable_percentage == 100:
            for row in data_rows:
                if field_name in row:
                    row[field_name] = None
        else:
            for row in data_rows:
                if field_name in row:
                    if random.randint(1, 100) <= nullable_percentage:
                        row[field_name] = None

    def update_single_field_data(self, field_widget):

        if not self.current_preview_data or not field_widget.is_valid():
            return

        field_name = field_widget.get_field_name()

        field_exists_in_original = any(
            field_name in row for row in self.original_preview_data) if self.original_preview_data else False

        if field_exists_in_original and hasattr(field_widget, '_last_config'):
            current_config = field_widget.get_field_config()
            last_config = field_widget._last_config

            config_without_nullable = {
                k: v for k, v in current_config.items() if k != 'nullable_percentage'}
            last_config_without_nullable = {
                k: v for k, v in last_config.items() if k != 'nullable_percentage'}

            if config_without_nullable == last_config_without_nullable:
                try:
                    for i, (original_row, current_row) in enumerate(zip(self.original_preview_data, self.current_preview_data)):
                        if field_name in original_row:
                            current_row[field_name] = original_row[field_name]

                    self.apply_nullability_to_field(
                        field_widget, self.current_preview_data)

                    field_widget._last_config = current_config.copy()

                    self.update_preview_display()
                    return

                except Exception as e:
                    print(f"Error applying nullability: {e}")

        try:
            field_config = field_widget.get_field_config()
            field_config_no_null = field_config.copy()
            field_config_no_null["nullable_percentage"] = 0

            request = {
                "fields": [field_config_no_null],
                "rows": len(self.current_preview_data),
                "format": "JSON",
                "zip": False
            }

            new_field_data = self.data_generator.generate(request)

            for i, row in enumerate(self.current_preview_data):
                if i < len(new_field_data) and field_name in new_field_data[i]:
                    if i < len(self.original_preview_data):
                        self.original_preview_data[i][field_name] = new_field_data[i][field_name]
                    row[field_name] = new_field_data[i][field_name]

            self.apply_nullability_to_field(
                field_widget, self.current_preview_data)

            field_widget._last_config = field_config.copy()

            self.update_preview_display()

        except Exception as e:
            print(f"Error updating single field data: {e}")
            self.refresh_preview()

    def on_field_modified(self):

        self.refresh_preview()

    def update_field_name_in_preview(self, old_name, new_name):

        if not self.current_preview_data or old_name == new_name:
            return

        try:
            for row in self.current_preview_data:
                if old_name in row:
                    new_row = {}
                    for key, value in row.items():
                        if key == old_name:
                            new_row[new_name] = value
                        else:
                            new_row[key] = value
                    row.clear()
                    row.update(new_row)

            for row in self.original_preview_data:
                if old_name in row:
                    new_row = {}
                    for key, value in row.items():
                        if key == old_name:
                            new_row[new_name] = value
                        else:
                            new_row[key] = value
                    row.clear()
                    row.update(new_row)

            self.update_preview_display()

        except Exception as e:
            print(f"Error updating field name in preview: {e}")

    def focus_and_scroll_to_field(self, field_widget):

        field_widget.name_edit.setFocus()
        field_widget.name_edit.selectAll()

        self.scroll_to_widget(field_widget)

    def scroll_to_widget(self, widget):

        scroll_area = self.fields_widget.parent()
        if hasattr(scroll_area, 'ensureWidgetVisible'):
            scroll_area.ensureWidgetVisible(widget)

    def scroll_to_bottom(self):

        scroll_area = self.fields_widget.parent()
        if hasattr(scroll_area, 'verticalScrollBar'):
            scroll_area.verticalScrollBar().setValue(
                scroll_area.verticalScrollBar().maximum()
            )

    def remove_field(self, field_widget):

        if field_widget in self.fields:
            try:
                field_name = field_widget.get_field_name()
            except RuntimeError:
                field_name = f"field_{len(self.fields)}"

            self.fields.remove(field_widget)
            try:
                if field_widget is not None:
                    field_widget.setParent(None)
                    field_widget.deleteLater()
            except RuntimeError:
                pass

            self.update_remove_button_states()

            self.remove_field_from_preview(field_name)

    def duplicate_field(self, field_widget):

        if not self.is_widget_valid(field_widget):
            if field_widget in self.fields:
                self.fields.remove(field_widget)
            return

        if field_widget in self.fields:
            field_config = field_widget.get_field_config()

            new_field_widget = FieldConfigWidget(
                self.available_generators,
                self.field_number_counter,
                self.remove_field,
                self.duplicate_field,
                self.move_field_up,
                self.move_field_down
            )
            self.field_number_counter += 1  # Increment counter for next field
            self.fields.append(new_field_widget)
            self.fields_layout.addWidget(new_field_widget)

            new_field_widget.field_changed.connect(self.on_field_modified)
            new_field_widget.field_name_changed.connect(
                self.update_field_name_in_preview)
            new_field_widget.field_data_changed.connect(
                self.update_single_field_data)
            new_field_widget.request_preview_refresh.connect(
                self.refresh_preview)
            new_field_widget.name_edit.textChanged.connect(
                self.update_generate_button_state)

            self.apply_field_configuration(new_field_widget, field_config)

            original_name = field_config.get(
                'name', f'field_{len(self.fields)}')
            new_name = self.generate_unique_field_name(original_name)
            new_field_widget.name_edit.setText(new_name)
            new_field_widget.update_field_label()

            self.update_remove_button_states()

            QTimer.singleShot(
                50, lambda: self.focus_and_scroll_to_field(new_field_widget))

            self.add_field_to_preview(new_field_widget)

    def move_field_up(self, field_widget):

        if not self.is_widget_valid(field_widget):
            if field_widget in self.fields:
                self.fields.remove(field_widget)
            return

        if field_widget not in self.fields:
            return

        current_index = self.fields.index(field_widget)
        if current_index == 0:
            return  # Already at the top

        self.fields[current_index], self.fields[current_index - 1] = \
            self.fields[current_index - 1], self.fields[current_index]

        self.reorder_fields_in_layout()

        self.update_move_button_states()

        self.reorder_preview_data()

    def move_field_down(self, field_widget):

        if not self.is_widget_valid(field_widget):
            if field_widget in self.fields:
                self.fields.remove(field_widget)
            return

        if field_widget not in self.fields:
            return

        current_index = self.fields.index(field_widget)
        if current_index == len(self.fields) - 1:
            return  # Already at the bottom

        self.fields[current_index], self.fields[current_index + 1] = \
            self.fields[current_index + 1], self.fields[current_index]

        self.reorder_fields_in_layout()

        self.update_move_button_states()

        self.reorder_preview_data()

    def reorder_preview_data(self):

        if not self.current_preview_data or not self.fields:
            return

        new_field_order = [field.get_field_name() for field in self.fields]

        self.current_preview_data = self.reorder_data_columns(
            self.current_preview_data, new_field_order)
        self.original_preview_data = self.reorder_data_columns(
            self.original_preview_data, new_field_order)

        self.update_preview_display()

    def reorder_data_columns(self, data, field_order):

        if not data:
            return data

        reordered_data = []
        for row in data:
            reordered_row = {}
            for field_name in field_order:
                if field_name in row:
                    reordered_row[field_name] = row[field_name]

            for key, value in row.items():
                if key not in reordered_row:
                    reordered_row[key] = value

            reordered_data.append(reordered_row)

        return reordered_data

    def reorder_fields_in_layout(self):

        self.cleanup_deleted_widgets()

        for i in reversed(range(self.fields_layout.count())):
            item = self.fields_layout.takeAt(i)
            if item and item.widget():
                item.widget().setParent(None)

        self.fields = [
            widget for widget in self.fields if self.is_widget_valid(widget)]

        for index, field_widget in enumerate(self.fields):
            try:
                if self.is_widget_valid(field_widget):
                    self.fields_layout.addWidget(field_widget)
            except RuntimeError:
                if field_widget in self.fields:
                    self.fields.remove(field_widget)

    def is_widget_valid(self, widget):

        try:
            if widget is None:
                return False
            _ = widget.objectName()
            return True
        except RuntimeError:
            return False

    def cleanup_deleted_widgets(self):

        self.fields = [
            widget for widget in self.fields if self.is_widget_valid(widget)]

    def update_move_button_states(self):

        for i, field_widget in enumerate(self.fields[:]):
            try:
                if field_widget is not None:
                    move_up_enabled = i > 0
                    move_down_enabled = i < len(self.fields) - 1
                    field_widget.set_move_buttons_enabled(
                        move_up_enabled, move_down_enabled)
            except RuntimeError:
                if field_widget in self.fields:
                    self.fields.remove(field_widget)

    def generate_unique_field_name(self, base_name):

        existing_names = [field.get_field_name() for field in self.fields]

        if base_name not in existing_names:
            return base_name

        counter = 1
        while f"{base_name}_copy_{counter}" in existing_names:
            counter += 1

        return f"{base_name}_copy_{counter}"

    def apply_field_configuration(self, field_widget, config):

        try:
            if 'generator' in config:
                generator_index = -1
                for i in range(field_widget.generator_combo.count()):
                    if field_widget.generator_combo.itemData(i) == config['generator']:
                        generator_index = i
                        break
                if generator_index >= 0:
                    field_widget.generator_combo.setCurrentIndex(
                        generator_index)
                    field_widget.update_actions()

            if 'action' in config:
                action_index = -1
                for i in range(field_widget.action_combo.count()):
                    if field_widget.action_combo.itemData(i) == config['action']:
                        action_index = i
                        break
                if action_index >= 0:
                    field_widget.action_combo.setCurrentIndex(action_index)
                    field_widget.update_parameters()

            if 'nullable_percentage' in config:
                field_widget.nullable_slider.setValue(
                    config['nullable_percentage'])

            if 'parameters' in config and hasattr(field_widget, 'parameter_widgets'):
                parameters = config['parameters']

                current_generator_name = config.get('generator', '')
                current_action_name = config.get('action', '')

                if current_generator_name and current_action_name:
                    try:
                        from ..services.available_generators import AvailableGenerators
                        available_gen = AvailableGenerators()
                        generator_instance = available_gen.get_generator_by_name(
                            current_generator_name)

                        if generator_instance:
                            from ..generators.generator import GeneratorActions
                            action_enum = GeneratorActions[current_action_name]
                            param_names = generator_instance.get_parameters(
                                action_enum)

                            for i, param_name in enumerate(param_names):
                                if i < len(parameters) and param_name in field_widget.parameter_widgets:
                                    widget = field_widget.parameter_widgets[param_name]
                                    param_value = parameters[i]

                                    if isinstance(widget, QSpinBox):
                                        widget.setValue(
                                            int(param_value) if param_value else 0)
                                    elif isinstance(widget, QLineEdit):
                                        widget.setText(
                                            str(param_value) if param_value else "")
                    except Exception as e:
                        param_widgets = list(
                            field_widget.parameter_widgets.values())
                        for i, param_value in enumerate(parameters):
                            if i < len(param_widgets):
                                widget = param_widgets[i]
                                if isinstance(widget, QSpinBox):
                                    widget.setValue(
                                        int(param_value) if param_value else 0)
                                elif isinstance(widget, QLineEdit):
                                    widget.setText(
                                        str(param_value) if param_value else "")

        except Exception as e:
            self.show_status_message(
                get_string("status.failed_to_apply_config").format(str(e)))

    def remove_all_fields(self):

        if not self.fields:
            return

        for field_widget in self.fields[:]:
            try:
                if field_widget is not None:
                    field_widget.setParent(None)
                    field_widget.deleteLater()
            except RuntimeError:
                pass

        self.fields.clear()

        self.field_number_counter = 1

        self.current_preview_data = []
        self.original_preview_data = []
        self.update_preview_display()

        self.update_remove_button_states()

    def remove_field_from_preview(self, field_name):

        if not self.current_preview_data:
            return

        try:
            for row in self.current_preview_data:
                if field_name in row:
                    del row[field_name]

            for row in self.original_preview_data:
                if field_name in row:
                    del row[field_name]

            self.update_preview_display()

        except Exception as e:
            print(f"Error removing field from preview: {e}")
            self.refresh_preview()  # Fallback to full refresh

    def update_remove_button_states(self):

        for field in self.fields[:]:  # Create a copy to avoid issues with deletion
            try:
                if field is not None:
                    field.set_remove_button_enabled(True)
            except RuntimeError:
                if field in self.fields:
                    self.fields.remove(field)

        self.update_move_button_states()

        self.update_generate_button_state()

    def update_generate_button_state(self):

        if hasattr(self, '_generate_button_loading') and self._generate_button_loading:
            return

        has_valid_fields = len(self.fields) > 0 and all(
            field.get_field_name().strip() != "" for field in self.fields
        )
        self.generate_btn.setEnabled(has_valid_fields)

    def set_generate_button_loading(self, loading):

        self._generate_button_loading = loading

        if loading:
            self.generate_btn.setEnabled(False)
            self.generate_btn.setText(get_string("ui.buttons.generating"))
            self.generate_btn.setToolTip(get_string(
                "ui.tooltips.generation_in_progress"))
            try:
                self.generate_btn.setIcon(
                    QIcon(get_resource_path("ui/res/loading-spinner.png")))
            except:
                pass
        else:
            self.generate_btn.setText("")
            self.generate_btn.setToolTip(
                get_string("ui.tooltips.generate_mock_data"))
            self.generate_btn.setIcon(
                QIcon(get_resource_path("ui/res/icons8-play-100.png")))
            self.update_generate_button_state()

    def on_settings_changed(self):

        self.refresh_preview()

    def on_preview_rows_changed(self):

        value = self.preview_rows_spinbox.value()

        self.adjust_preview_data_size(value)

    def adjust_preview_data_size(self, new_count):

        if not self.fields or not any(field.is_valid() for field in self.fields):
            self.current_preview_data = []
            self.original_preview_data = []
            self.update_preview_display()
            return

        current_count = len(self.current_preview_data)

        if new_count > current_count:
            additional_rows = new_count - current_count
            try:
                original_configs = []
                for field in self.fields:
                    if field.is_valid():
                        config = field.get_field_config()
                        original_config = config.copy()
                        original_config["nullable_percentage"] = 0
                        original_configs.append(original_config)

                request = {
                    "fields": original_configs,
                    "rows": additional_rows,
                    "format": "JSON",
                    "zip": False
                }

                additional_original_data = self.data_generator.generate(
                    request)
                self.original_preview_data.extend(additional_original_data)

                additional_current_data = [row.copy()
                                           for row in additional_original_data]

                for field_widget in self.fields:
                    if field_widget.is_valid():
                        self.apply_nullability_to_field(
                            field_widget, additional_current_data)

                self.current_preview_data.extend(additional_current_data)

            except Exception as e:
                print(f"Error appending preview data: {e}")

        elif new_count < current_count:
            self.current_preview_data = self.current_preview_data[:new_count]
            self.original_preview_data = self.original_preview_data[:new_count]

        self.last_preview_row_count = new_count
        self.update_preview_display()

    def on_format_changed(self):

        self.update_format_tabs()
        self.update_preview_display()

    def update_format_tabs(self):

        selected_formats = self.get_selected_formats()

        if selected_formats:
            first_format = selected_formats[0]
            target_index = -1

            for i in range(self.preview_tabs.count()):
                if self.preview_tabs.tabText(i) == first_format:
                    target_index = i
                    break

            if target_index >= 0 and self.preview_tabs.currentIndex() != target_index:
                self.preview_tabs.setCurrentIndex(target_index)

        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setToolTip(get_string("ui.tooltips.refresh_preview"))

        current_tab_index = self.preview_tabs.currentIndex()
        if current_tab_index >= 0:
            current_tab_text = self.preview_tabs.tabText(current_tab_index)
            is_table_view = current_tab_text == get_string("ui.tabs.table")
            self.copy_btn.setEnabled(not is_table_view)
        else:
            self.copy_btn.setEnabled(False)

    def generate_data(self):

        if not self.fields:
            self._show_validation_warning('no_fields')
            return

        selected_formats = self.get_selected_formats()
        if not selected_formats:
            self._show_validation_warning('no_format')
            return

        for field in self.fields:
            field_name = field.get_field_name().strip()
            if not field_name:
                self._show_validation_warning('no_field_name')
                return
            if not field.is_valid():
                self._show_validation_warning('invalid_field', field_name)
                return

        # Check for large dataset warning
        rows_count = self.rows_spinbox.value()
        if rows_count > self.LARGE_DATASET_THRESHOLD:
            # Create and show warning dialog
            dialog = DatasetWarningDialog(
                parent=self,
                rows_count=rows_count
            )

            result = dialog.exec()
            if result != QDialog.DialogCode.Accepted:
                return

        request = {
            "fields": [field.get_field_config() for field in self.fields],
            "rows": self.rows_spinbox.value(),
            "format": self.get_selected_format(),
            "zip": False
        }

        self.generation_thread = DataGenerationThread(
            self.data_generator, request)
        self.generation_thread.finished.connect(self.on_generation_finished)
        self.generation_thread.error.connect(self.on_generation_error)

        from datetime import datetime
        self.generation_start_time = datetime.now()

        self.total_rows_to_generate = self.rows_spinbox.value()

        self.set_generate_button_loading(True)
        self.status_bar.showMessage(get_string(
            "status.data_generation_in_progress"))

        rows = self.rows_spinbox.value()
        selected_formats = self.get_selected_formats()
        format_names = ", ".join(selected_formats)
        self.generation_thread.start()

    def on_generation_finished(self, data):

        self.generated_data = data

        try:
            self.auto_generate_file(data)
        except Exception as e:
            print(f"Auto-file generation error: {e}")

        self.set_generate_button_loading(False)

        from datetime import datetime
        if hasattr(self, 'generation_start_time'):
            generation_time = datetime.now() - self.generation_start_time
            time_seconds = generation_time.total_seconds()
            if time_seconds < 60:
                time_str = f"{time_seconds:.3f}s"
            else:
                minutes = int(time_seconds // 60)
                seconds = time_seconds % 60
                time_str = f"{minutes}m {seconds:.3f}s"
        else:
            time_str = "unknown"

        rows_count = len(data)

        if hasattr(self, 'last_auto_generated_files') and self.last_auto_generated_files:
            file_count = len(self.last_auto_generated_files)
            if file_count == 1:
                file_name = Path(self.last_auto_generated_files[0]).name
                file_ext = file_name.split('.')[-1].upper()
                if file_ext == 'ZIP':
                    self.status_bar.showMessage(
                        get_string("status.generation_complete_with_file").format(rows_count, time_str, "ZIP archive"))
                else:
                    self.status_bar.showMessage(
                        get_string("status.generation_complete_with_file").format(rows_count, time_str, f"{file_ext} file"))
            else:
                self.status_bar.showMessage(
                    get_string("status.generation_complete_with_files").format(rows_count, time_str, file_count))
        else:
            self.status_bar.showMessage(
                get_string("status.generation_complete_simple").format(rows_count, time_str))

        if hasattr(self, 'last_auto_generated_files') and self.last_auto_generated_files:
            if len(self.last_auto_generated_files) == 1:
                file_name = Path(self.last_auto_generated_files[0]).name
            else:
                file_names = [
                    Path(f).name for f in self.last_auto_generated_files]
                file_list = ", ".join(file_names)

        if hasattr(self, 'last_auto_generated_file'):
            file_name = Path(self.last_auto_generated_file).name
            self.footer_file_label.setText(f"{file_name}")
            self.footer_file_label.setToolTip(get_string(
                "ui.tooltips.click_to_open_file_location"))
            self.footer_file_label.setVisible(True)

    def auto_generate_file(self, data):

        try:
            selected_formats = self.get_selected_formats()
            zip_file = self.zip_checkbox.isChecked()
            batch_size = self.sql_batch_spinbox.value()

            default_dir = get_default_export_directory()

            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            rows_count = len(data)

            exported_files = []

            self.status_bar.showMessage(get_string("status.writing_files"))

            for i, format_name in enumerate(selected_formats):
                self.status_bar.showMessage(
                    f"Writing {format_name} file ({i+1}/{len(selected_formats)})...")

                format_enum = GeneratorFormats[format_name]
                file_extension = format_name.lower()
                filename = f"mock_data_{rows_count}rows_{timestamp}.{file_extension}"
                file_path = str(Path(default_dir) / filename)

                if format_name == "SQL":
                    exported_file = write_for_gui(
                        data, format_enum, False, file_path, batch_size  # Always False for individual ZIP
                    )
                else:
                    exported_file = write_for_gui(
                        data, format_enum, False, file_path  # Always False for individual ZIP
                    )

                exported_files.append(exported_file)

            if zip_file and exported_files:
                self.status_bar.showMessage(get_string("status.creating_zip"))

                from ..services.gui_file_writer import _compress_multiple_files
                zip_filename = f"mock_data_{rows_count}rows_{timestamp}.zip"
                zip_path = str(Path(default_dir) / zip_filename)

                _compress_multiple_files(exported_files, zip_path)

                for file_path in exported_files:
                    Path(file_path).unlink()

                exported_files = [zip_path]
                self.status_bar.showMessage(
                    "ZIP archive created successfully")
            else:
                file_count = len(exported_files)
                self.status_bar.showMessage(
                    f"{file_count} file{'s' if file_count > 1 else ''} generated successfully")

            if exported_files:
                self.last_auto_generated_file = exported_files[0]
                self.last_auto_generated_files = exported_files

            self.update_export_directory_display()

            print(f"Auto-generated files: {exported_files}")

        except Exception as e:
            self.status_bar.showMessage(
                get_string("status.file_generation_failed"))
            print(f"Failed to auto-generate files: {e}")
            raise

    def on_generation_error(self, error_message):

        self.set_generate_button_loading(False)

        if hasattr(self, 'generation_start_time'):
            from datetime import datetime
            generation_time = datetime.now() - self.generation_start_time
            time_seconds = generation_time.total_seconds()
            if time_seconds < 60:
                time_str = f" (after {time_seconds:.3f}s)"
            else:
                minutes = int(time_seconds // 60)
                seconds = time_seconds % 60
                time_str = f" (after {minutes}m {seconds:.3f}s)"
        else:
            time_str = ""

        self.status_bar.showMessage(get_string(
            "status.generation_failed").format(time_str))

        QMessageBox.critical(self, get_string("errors.generation_error_title"),
                             f"Failed to generate data:\n{error_message}")

    def open_file_location(self, event):

        if hasattr(self, 'last_auto_generated_file'):
            import subprocess
            import platform

            file_path = self.last_auto_generated_file

            try:
                if platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", "-R", file_path])
                elif platform.system() == "Windows":  # Windows
                    subprocess.run(["explorer", "/select,", file_path])
                else:  # Linux and others
                    subprocess.run(["xdg-open", str(Path(file_path).parent)])
            except Exception as e:
                QMessageBox.information(self, get_string("dialogs.file_location_title"),
                                        f"Generated file location:\n{file_path}\n\nCould not open file manager: {e}")

    def refresh_preview(self):

        if not self.fields:
            self.current_preview_data = []
            self.original_preview_data = []
            self.data_table.clear()
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(0)
            for text_edit in self.text_previews.values():
                text_edit.clear()
            return

        try:
            preview_count = self.preview_rows_spinbox.value()

            field_configs = [field.get_field_config()
                             for field in self.fields if field.is_valid()]

            if not field_configs:
                self.current_preview_data = []
                self.original_preview_data = []
                self.update_preview_display()
                return

            original_configs = []
            for config in field_configs:
                original_config = config.copy()
                original_config["nullable_percentage"] = 0
                original_configs.append(original_config)

            request = {
                "fields": original_configs,
                "rows": preview_count,
                "format": "JSON",
                "zip": False
            }

            original_data = self.data_generator.generate(request)
            self.original_preview_data = original_data.copy()  # Store original

            self.current_preview_data = [row.copy() for row in original_data]

            for field_widget in self.fields:
                if field_widget.is_valid():
                    self.apply_nullability_to_field(
                        field_widget, self.current_preview_data)
                    field_widget._last_config = field_widget.get_field_config().copy()

            self.last_preview_row_count = preview_count  # Update row count tracker
            self.update_preview_display()  # Update the display

        except Exception as e:
            print(f"Preview error: {e}")
            self.current_preview_data = []
            self.original_preview_data = []
            self.update_preview_display()

    def update_preview_display(self):

        data = self.current_preview_data
        if not data:
            self.data_table.clear()
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(0)
            for text_edit in self.text_previews.values():
                text_edit.clear()
            return

        self.data_table.setRowCount(len(data))
        if data:
            columns = list(data[0].keys())
            self.data_table.setColumnCount(len(columns))
            self.data_table.setHorizontalHeaderLabels(columns)

            for row_idx, row_data in enumerate(data):
                for col_idx, (key, value) in enumerate(row_data.items()):
                    item = QTableWidgetItem(
                        str(value) if value is not None else "")
                    self.data_table.setItem(row_idx, col_idx, item)

        self.data_table.resizeColumnsToContents()

        all_formats = ["JSON", "CSV", "XML", "HTML", "SQL"]

        for format_name in all_formats:
            if format_name in self.text_previews:
                formatted_text = self.format_data_for_preview(
                    data, format_name)
                self.text_previews[format_name].setPlainText(formatted_text)

    def format_data_for_preview(self, data, format_name):

        if format_name == "JSON":
            import json
            return json.dumps(data, indent=2, ensure_ascii=False)
        elif format_name == "CSV":
            import csv
            import io
            output = io.StringIO()
            if data:
                fieldnames = list(data[0].keys())
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return output.getvalue()
        elif format_name == "XML":
            formatted_text = "<root>\n"
            for i, row in enumerate(data):
                formatted_text += f"  <row id=\"{i+1}\">\n"
                for key, value in row.items():
                    formatted_text += f"    <{key}>{value}</{key}>\n"
                formatted_text += "  </row>\n"
            formatted_text += "</root>"
            return formatted_text
        elif format_name == "HTML":
            if data:
                formatted_text = "<!DOCTYPE html>\n<html>\n<head>\n"
                formatted_text += "<title>Mock Data</title>\n"
                formatted_text += "<style>\n"
                formatted_text += "table { border-collapse: collapse; width: 100%; }\n"
                formatted_text += "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }\n"
                formatted_text += "th { background-color: #f2f2f2; font-weight: bold; }\n"
                formatted_text += "tr:nth-child(even) { background-color: #f9f9f9; }\n"
                formatted_text += "</style>\n</head>\n<body>\n"
                formatted_text += "<h2>Mock Data Table</h2>\n"
                formatted_text += "<table>\n"

                columns = list(data[0].keys())
                formatted_text += "  <thead>\n    <tr>\n"
                for col in columns:
                    formatted_text += f"      <th>{col}</th>\n"
                formatted_text += "    </tr>\n  </thead>\n"

                formatted_text += "  <tbody>\n"
                for row in data:
                    formatted_text += "    <tr>\n"
                    for col in columns:
                        value = row.get(col)
                        cell_value = str(value) if value is not None else ""
                        cell_value = cell_value.replace("&", "&amp;").replace(
                            "<", "&lt;").replace(">", "&gt;")
                        formatted_text += f"      <td>{cell_value}</td>\n"
                    formatted_text += "    </tr>\n"
                formatted_text += "  </tbody>\n</table>\n</body>\n</html>"
                return formatted_text
            else:
                return "<!-- No data to display -->"
        elif format_name == "SQL":
            if data:
                batch_size = self.sql_batch_spinbox.value()
                columns = list(data[0].keys())
                column_names = ", ".join(f"`{col}`" for col in columns)
                formatted_text = ""

                for batch_start in range(0, len(data), batch_size):
                    batch_end = min(batch_start + batch_size, len(data))
                    batch_data = data[batch_start:batch_end]

                    formatted_text += f"INSERT INTO `mock_data` ({column_names}) VALUES\n"

                    for i, row in enumerate(batch_data):
                        values = []
                        for col in columns:
                            value = row.get(col)
                            if value is None:
                                values.append("NULL")
                            elif isinstance(value, str):
                                escaped_value = value.replace("'", "''")
                                values.append(f"'{escaped_value}'")
                            else:
                                values.append(f"'{value}'")

                        value_str = f"  ({', '.join(values)})"
                        if i == len(batch_data) - 1:
                            formatted_text += f"{value_str};\n\n"
                        else:
                            formatted_text += f"{value_str},\n"

                return formatted_text.rstrip()
            else:
                return "-- No data to display"
        else:
            return str(data)

    def copy_current_preview_to_clipboard(self):

        if not self.current_preview_data:
            QMessageBox.information(
                self, "No Data", "No preview data to copy.")
            return

        try:
            current_tab_index = self.preview_tabs.currentIndex()
            current_tab_text = self.preview_tabs.tabText(current_tab_index)

            data = self.current_preview_data

            format_name = current_tab_text
            if current_tab_text == get_string("ui.tabs.table"):
                import json
                formatted_text = json.dumps(data, indent=2, ensure_ascii=False)
                format_name = "JSON"
            else:
                formatted_text = self.format_data_for_preview(
                    data, format_name)

            clipboard = QApplication.clipboard()
            clipboard.setText(formatted_text)

            current_message = self.status_bar.currentMessage()
            self.status_bar.showMessage(
                f"Preview data copied to clipboard as {format_name}", self.TIMER_INTERVALS['status_message'])

            QTimer.singleShot(
                self.TIMER_INTERVALS['status_message'], lambda: self.status_bar.showMessage(current_message))

        except Exception as e:
            QMessageBox.critical(
                self, "Copy Error", f"Failed to copy data to clipboard:\n{str(e)}")

    def copy_preview_to_clipboard(self):

        if not self.current_preview_data:
            QMessageBox.information(
                self, "No Data", "No preview data to copy.")
            return

        try:
            format_name = self.get_selected_format()
            data = self.current_preview_data

            if format_name == "JSON":
                import json
                formatted_text = json.dumps(data, indent=2, ensure_ascii=False)
            elif format_name == "CSV":
                import csv
                import io
                output = io.StringIO()
                if data:
                    fieldnames = list(data[0].keys())
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
                formatted_text = output.getvalue()
            elif format_name == "XML":
                formatted_text = "<root>\n"
                for i, row in enumerate(data):
                    formatted_text += f"  <row id=\"{i+1}\">\n"
                    for key, value in row.items():
                        formatted_text += f"    <{key}>{value}</{key}>\n"
                    formatted_text += "  </row>\n"
                formatted_text += "</root>"
            elif format_name == "SQL":
                if data:
                    columns = list(data[0].keys())
                    column_names = ", ".join(f"`{col}`" for col in columns)
                    formatted_text = f"-- Mock Data SQL Export\n"
                    formatted_text += f"-- Record count: {len(data)}\n\n"
                    formatted_text += f"INSERT INTO `mock_data` ({column_names}) VALUES\n"

                    for i, row in enumerate(data):
                        values = []
                        for col in columns:
                            value = row.get(col)
                            if value is None:
                                values.append("NULL")
                            elif isinstance(value, str):
                                escaped_value = value.replace("'", "''")
                                values.append(f"'{escaped_value}'")
                            else:
                                values.append(f"'{value}'")

                        value_str = f"  ({', '.join(values)})"
                        if i == len(data) - 1:
                            formatted_text += f"{value_str};\n"
                        else:
                            formatted_text += f"{value_str},\n"
                else:
                    formatted_text = "-- No data to display"
            else:
                formatted_text = str(data)

            clipboard = QApplication.clipboard()
            clipboard.setText(formatted_text)

            current_message = self.status_bar.currentMessage()
            self.status_bar.showMessage(
                f"Preview data copied to clipboard as {format_name}", self.TIMER_INTERVALS['copy_status'])

            QTimer.singleShot(
                self.TIMER_INTERVALS['copy_status'], lambda: self.status_bar.showMessage(current_message))

        except Exception as e:
            QMessageBox.critical(
                self, "Copy Error", f"Failed to copy data to clipboard:\n{str(e)}")

    def change_export_directory(self):

        current_dir = get_default_export_directory()

        new_dir = QFileDialog.getExistingDirectory(
            self,
            get_string("dialogs.choose_save_directory"),
            current_dir
        )

        if new_dir:
            self.export_dir_label.setText(str(Path(new_dir).name))
            self.export_dir_label.setToolTip(new_dir)

    def copy_api_request_to_clipboard(self):
        """Copy field configuration as API request body to clipboard"""
        try:
            if not self.fields:
                QMessageBox.information(
                    self, "No Fields", "No fields configured to copy.")
                return

            # Check for multiple format selection and show warning
            selected_formats = self.get_selected_formats()
            if len(selected_formats) > 1:
                QMessageBox.warning(
                    self, "Multiple Formats Selected",
                    "Only one export format can be used with API requests.\n"
                    "Please select only one format before copying the API request."
                )
                return
            elif len(selected_formats) == 0:
                # Default to JSON if no format is selected
                output_format = "JSON"
            else:
                output_format = selected_formats[0]

            # Build the API request structure
            api_request = {
                "fields": [],
                "rows": self.rows_spinbox.value(),
                "format": output_format
            }

            # Add field configurations
            for field in self.fields:
                if field.is_valid():
                    field_config = field.get_field_config()

                    # Handle generator name (could be enum or string)
                    generator = field_config["generator"]
                    generator_name = generator.name if hasattr(
                        generator, 'name') else str(generator)

                    # Handle action name (could be enum or string)
                    action = field_config["action"]
                    action_name = action.name if hasattr(
                        action, 'name') else str(action)

                    api_field = {
                        "name": field_config["name"],
                        "generator": generator_name,
                        "action": action_name
                    }

                    # Add nullable percentage if not zero
                    if field_config.get("nullable_percentage", 0) > 0:
                        api_field["nullable_percentage"] = field_config["nullable_percentage"]

                    # Add parameters if present
                    if field_config.get("parameters"):
                        api_field["parameters"] = field_config["parameters"]

                    api_request["fields"].append(api_field)

            # Convert to JSON
            import json
            json_request = json.dumps(api_request, indent=2)

            # Copy to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setText(json_request)

            # Show success message
            self.status_bar.showMessage(
                f"API request copied to clipboard for {output_format} format",
                self.TIMER_INTERVALS['status_message']
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Copy Error", f"Failed to copy API request:\n{str(e)}"
            )

    def update_export_directory_display(self):

        export_dir = get_default_export_directory()

        if hasattr(self, 'last_auto_generated_file'):
            file_name = Path(self.last_auto_generated_file).name
            self.export_dir_label.setText(file_name)
            self.export_dir_label.setToolTip(self.last_auto_generated_file)
        else:
            dir_name = Path(export_dir).name
            self.export_dir_label.setText(dir_name)
            self.export_dir_label.setToolTip(export_dir)

    def start_api_server_on_startup(self):
        """Start the full API server automatically when the application starts"""
        try:
            print("🚀 Starting embedded API server with Swagger...")

            # Import the full API module
            from ..api import app as api_app

            self.api_flask_app = api_app

            # Start server using simple threading
            import threading
            from werkzeug.serving import run_simple

            def run_server():
                try:
                    run_simple(
                        self.api_server_host,
                        self.api_server_port,
                        self.api_flask_app,
                        use_debugger=False,
                        use_reloader=False,
                        threaded=True
                    )
                except Exception as e:
                    print(f"❌ API server error: {e}")

            # Start in daemon thread
            self.api_thread = threading.Thread(target=run_server, daemon=True)
            self.api_thread.start()

            print(
                f"✅ Embedded API server with Swagger started on http://{self.api_server_host}:{self.api_server_port}")
            print(
                f"📋 Swagger UI available at: http://{self.api_server_host}:{self.api_server_port}/")

        except Exception as e:
            print(f"❌ Failed to start API server: {str(e)}")
            # Fallback to minimal server if full API fails
            self._start_minimal_api_server()

    def _start_minimal_api_server(self):
        """Fallback minimal API server if full API fails"""
        try:
            print("🔄 Starting minimal API server as fallback...")

            # Create minimal Flask app for PyInstaller compatibility
            from flask import Flask, jsonify

            self.api_flask_app = Flask(__name__)
            self.api_flask_app.config['DEBUG'] = False

            @self.api_flask_app.route('/health')
            def health():
                return jsonify({'status': 'healthy', 'message': 'API server is running'})

            @self.api_flask_app.route('/')
            def root():
                return jsonify({
                    'name': 'Mockachu API',
                    'version': '1.0.0',
                    'status': 'running',
                    'endpoints': ['/health', '/']
                })

            # Start server using simple threading
            import threading
            from werkzeug.serving import run_simple

            def run_server():
                try:
                    run_simple(
                        self.api_server_host,
                        self.api_server_port,
                        self.api_flask_app,
                        use_debugger=False,
                        use_reloader=False,
                        threaded=True
                    )
                except Exception as e:
                    print(f"❌ Minimal API server error: {e}")

            # Start in daemon thread
            self.api_thread = threading.Thread(target=run_server, daemon=True)
            self.api_thread.start()

            print(
                f"✅ Minimal API server started on http://{self.api_server_host}:{self.api_server_port}")

        except Exception as e:
            print(f"❌ Failed to start minimal API server: {str(e)}")
            # Don't crash the app if API server fails
            pass

    def on_api_server_finished(self, exit_code):
        """Handle API server process finished"""
        if exit_code != 0:
            # Get error output
            error_output = ""
            if hasattr(self.api_server_process, 'readAllStandardError'):
                error_bytes = self.api_server_process.readAllStandardError()
                error_output = bytes(error_bytes).decode('utf-8').strip()

            print(
                f"⚠️ API server stopped unexpectedly (exit code: {exit_code})")
            if error_output:
                print(f"Error output: {error_output}")

            # Also check standard output for any messages
            if hasattr(self.api_server_process, 'readAllStandardOutput'):
                output_bytes = self.api_server_process.readAllStandardOutput()
                output = bytes(output_bytes).decode('utf-8').strip()
                if output:
                    print(f"Server output: {output}")

    def open_api_documentation(self):
        """Open the API Swagger documentation in the default web browser"""
        try:
            api_url = f"http://{self.api_server_host}:{self.api_server_port}/swagger/"
            webbrowser.open(api_url)
            print(f"🌐 Opening API documentation: {api_url}")
        except Exception as e:
            print(f"❌ Failed to open API documentation: {str(e)}")
            QMessageBox.warning(
                self,
                "API Documentation",
                f"Could not open API documentation.\n"
                f"Please manually navigate to: http://{self.api_server_host}:{self.api_server_port}/swagger/\n\n"
                f"Error: {str(e)}"
            )

    def closeEvent(self, event):
        """Handle application close event"""
        print("🛑 Shutting down application...")
        super().closeEvent(event)

    def refresh_ui_text(self):

        try:
            self.setWindowTitle(get_string("app.title"))

            if hasattr(self, 'settings_group'):
                self.settings_group.setTitle(
                    get_string("ui.groups.generation_settings"))
            if hasattr(self, 'fields_group'):
                self.fields_group.setTitle(get_string(
                    "ui.groups.fields_configuration"))

            if hasattr(self, 'zip_checkbox'):
                self.zip_checkbox.setText(get_string("ui.checkboxes.zip"))
                self.zip_checkbox.setToolTip(get_string("ui.tooltips.zip"))
            if hasattr(self, 'json_checkbox'):
                self.json_checkbox.setText(get_string("ui.checkboxes.json"))
            if hasattr(self, 'csv_checkbox'):
                self.csv_checkbox.setText(get_string("ui.checkboxes.csv"))
            if hasattr(self, 'xml_checkbox'):
                self.xml_checkbox.setText(get_string("ui.checkboxes.xml"))
            if hasattr(self, 'html_checkbox'):
                self.html_checkbox.setText(get_string("ui.checkboxes.html"))
            if hasattr(self, 'sql_checkbox'):
                self.sql_checkbox.setText(get_string("ui.checkboxes.sql"))

            if hasattr(self, 'sql_batch_spinbox'):
                self.sql_batch_spinbox.setToolTip(
                    get_string("ui.tooltips.sql_batch_size"))
            if hasattr(self, 'generate_btn'):
                self.generate_btn.setToolTip(
                    get_string("ui.tooltips.generate_mock_data"))
            if hasattr(self, 'refresh_btn'):
                self.refresh_btn.setToolTip(
                    get_string("ui.tooltips.refresh_preview"))
            if hasattr(self, 'copy_btn'):
                if self.copy_btn.isEnabled():
                    self.copy_btn.setToolTip(get_string(
                        "ui.tooltips.copy_preview_data"))
                else:
                    self.copy_btn.setToolTip(get_string(
                        "ui.tooltips.copy_not_available"))
            if hasattr(self, 'footer_file_label'):
                self.footer_file_label.setToolTip(get_string(
                    "ui.tooltips.click_to_open_file_location"))

            if hasattr(self, 'add_field_btn'):
                self.add_field_btn.setText(get_string("ui.buttons.add_field"))

            if hasattr(self, 'preview_rows_label'):
                self.preview_rows_label.setText(get_string("ui.labels.rows"))
            if hasattr(self, 'rows_label'):
                self.rows_label.setText(get_string("ui.labels.rows"))
            if hasattr(self, 'formats_label'):
                self.formats_label.setText(get_string("ui.labels.formats"))

            for label in self.findChildren(QLabel):
                if label.text() == get_string("ui.labels.rows"):
                    label.setText(get_string("ui.labels.rows"))
                elif label.text() == get_string("ui.labels.formats"):
                    label.setText(get_string("ui.labels.formats"))

            if hasattr(self, 'field_widgets'):
                for field_widget in self.field_widgets:
                    if hasattr(field_widget, 'refresh_ui_text'):
                        field_widget.refresh_ui_text()

        except Exception as e:
            print(f"Error refreshing UI text: {e}")

    def save_configuration(self):

        if not self.fields:
            self.show_status_message(self.ERROR_MESSAGES['no_fields_to_save'])
            return

        # Create and show save dialog
        dialog = SaveConfigurationDialog(
            parent=self,
            fields=self.fields,
            row_count=self.rows_spinbox.value(),
            saved_configurations=self.saved_configurations
        )

        # Connect signal to handle saving
        dialog.configuration_saved.connect(self.on_configuration_saved)

        # Show dialog
        dialog.exec()

    def on_configuration_saved(self, name, config_data):

        # Save configuration
        self.saved_configurations[name] = config_data

        # Save to disk
        if self.save_configurations_to_disk():
            self.show_status_message(
                f"Configuration '{name}' saved successfully")
        else:
            self.show_status_message(
                f"Configuration '{name}' saved to memory (disk save failed)")

        self._schedule_ready_message()

    def load_configuration(self):

        if not self.saved_configurations:
            self.show_status_message(self.ERROR_MESSAGES['no_saved_configs'])
            return

        # Create and show load dialog
        dialog = LoadConfigurationDialog(
            parent=self,
            saved_configurations=self.saved_configurations
        )

        # Connect signals to handle loading and deletion
        dialog.configuration_loaded.connect(self.on_configuration_loaded)
        dialog.configuration_deleted.connect(self.on_configuration_deleted)

        # Show dialog
        dialog.exec()

    def on_configuration_loaded(self, config_name, config_data):

        self._load_configuration_data(config_data)
        self.show_status_message(
            f"Configuration '{config_name}' loaded successfully")

        self._schedule_ready_message()

    def on_configuration_deleted(self, config_name):

        if config_name in self.saved_configurations:
            del self.saved_configurations[config_name]
            # Save to disk after deletion
            self.save_configurations_to_disk()
            self.show_status_message(
                f"Configuration '{config_name}' deleted")

            self._schedule_ready_message()

    def export_configuration(self):

        if not self.fields:
            self.show_status_message(
                get_string("status.no_fields_to_export"))
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            get_string("dialogs.export_configuration"),
            "field_configuration.json",
            get_string("dialogs.json_file_filter")
        )

        if file_path:
            try:
                # Get current field configurations
                field_configs = []
                for field_widget in self.fields:
                    field_configs.append(field_widget.get_field_config())

                # Prepare export data
                export_data = {
                    "version": "1.0",
                    "app": "Mockachu",
                    "fields": field_configs,
                    "row_count": self.rows_spinbox.value(),
                    "exported_at": "now"  # Simple timestamp placeholder
                }

                # Write to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)

                filename = Path(file_path).name
                self.show_status_message(
                    get_string("status.export_success").format(filename))

                self._schedule_ready_message()

            except Exception as e:
                self.show_status_message(get_string(
                    "status.export_failed").format(str(e)))

    def import_configuration(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            get_string("dialogs.import_configuration"),
            "",
            get_string("dialogs.json_file_filter")
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    import_data = json.load(f)

                # Validate the import data
                if not isinstance(import_data, dict) or 'fields' not in import_data:
                    self.show_status_message(
                        get_string("status.invalid_config_format"))
                    return

                # Load the configuration
                self._load_configuration_data(import_data)

                filename = Path(file_path).name
                self.show_status_message(
                    get_string("status.import_success").format(filename))

                self._schedule_ready_message()

            except json.JSONDecodeError:
                self.show_status_message(
                    get_string("status.invalid_json_format"))
            except Exception as e:
                self.show_status_message(get_string(
                    "status.import_failed").format(str(e)))

    def _load_configuration_data(self, config_data):

        try:
            # Clear existing fields without confirmation
            if self.fields:
                # Create a copy of the list to avoid modification during iteration
                for field_widget in self.fields[:]:
                    field_widget.setParent(None)
                    field_widget.deleteLater()

                # Clear the fields list
                self.fields.clear()

                # Update the fields layout to remove any remaining widgets
                if hasattr(self, 'fields_layout'):
                    # Clear all widgets from the layout
                    while self.fields_layout.count():
                        child = self.fields_layout.takeAt(0)
                        if child.widget():
                            child.widget().deleteLater()

                # Update preview
                self.update_preview_display()

            # Load row count if available
            if 'row_count' in config_data:
                self.rows_spinbox.setValue(config_data['row_count'])

            # Load fields
            fields_data = config_data.get('fields', [])
            for field_config in fields_data:
                # Add a new field
                self.add_field()

                # Get the last added field widget
                if self.fields:
                    field_widget = self.fields[-1]

                    # Set field name
                    if 'name' in field_config:
                        field_widget.name_edit.setText(field_config['name'])
                        field_widget.update_field_label()

                    # Set generator
                    if 'generator' in field_config:
                        # Use findData to find by actual enum name, not display text
                        generator_index = -1
                        for i in range(field_widget.generator_combo.count()):
                            if field_widget.generator_combo.itemData(i) == field_config['generator']:
                                generator_index = i
                                break

                        if generator_index >= 0:
                            field_widget.generator_combo.setCurrentIndex(
                                generator_index)
                            field_widget.update_actions()

                    # Set action
                    if 'action' in field_config:
                        # Use findData to find by actual enum name, not display text
                        action_index = -1
                        for i in range(field_widget.action_combo.count()):
                            if field_widget.action_combo.itemData(i) == field_config['action']:
                                action_index = i
                                break

                        if action_index >= 0:
                            field_widget.action_combo.setCurrentIndex(
                                action_index)
                            field_widget.update_parameters()

                    # Set nullable percentage
                    if 'nullable_percentage' in field_config:
                        field_widget.nullable_slider.setValue(
                            field_config['nullable_percentage'])

                    # Set parameters if available
                    if 'parameters' in field_config and hasattr(field_widget, 'parameter_widgets'):
                        parameters = field_config['parameters']
                        param_widgets = list(
                            field_widget.parameter_widgets.values())

                        for i, param_value in enumerate(parameters):
                            if i < len(param_widgets):
                                widget = param_widgets[i]
                                if isinstance(widget, QSpinBox):
                                    widget.setValue(int(param_value))
                                elif isinstance(widget, QLineEdit):
                                    widget.setText(str(param_value))

            # Update preview if fields were loaded
            if self.fields:
                self.update_preview_display()

            # Update UI state
            self.update_remove_button_states()
            self.update_generate_button_state()

        except Exception as e:
            self.show_status_message(get_string(
                "status.failed_to_load_config").format(str(e)))

    def get_config_file_path(self):

        # Try to use application data directory first
        try:
            if platform.system() == "Windows":
                config_dir = Path(os.environ.get(
                    'APPDATA', '')) / "Mockachu"
            elif platform.system() == "Darwin":  # macOS
                config_dir = Path.home() / "Library" / "Application Support" / "Mockachu"
            else:  # Linux and others
                config_dir = Path.home() / ".config" / "Mockachu"

            # Create directory if it doesn't exist
            config_dir.mkdir(parents=True, exist_ok=True)
            return config_dir / "configurations.json"

        except Exception:
            # Fallback to application directory
            app_dir = Path(__file__).parent.parent
            return app_dir / "configurations.json"

    def load_configurations_from_disk(self):

        try:
            if self.config_file_path.exists():
                with open(self.config_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Warning: Could not load configurations from disk: {e}")
            return {}

    def save_configurations_to_disk(self):

        try:
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.saved_configurations, f,
                          indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Warning: Could not save configurations to disk: {e}")
            return False

    def show_status_message(self, message, timeout=None):

        timeout = timeout or self.TIMER_INTERVALS['status_message']
        # Stop ready message animation when showing other messages
        self._stop_ready_message()

        # Show the message
        self.status_bar.showMessage(message, timeout)

        # Start ready message animation after timeout (if timeout > 0)
        if timeout > 0:
            QTimer.singleShot(timeout, self._start_ready_message)

    def _start_ready_message(self):

        if not self._is_ready_message_active:
            self._is_ready_message_active = True
            # Show ready message immediately without animation
            self._update_ready_message()

    def _stop_ready_message(self):

        if self._is_ready_message_active:
            self._is_ready_message_active = False
            # No timer to stop since we're not animating anymore

    def _update_ready_message(self):

        if not self._is_ready_message_active:
            return

        # Only show ready message if status bar is empty or showing previous ready message
        current_message = self.status_bar.currentMessage()
        if current_message and not current_message.startswith(get_string("status.ready_to_generate")):
            # There's another message showing, stop animation
            self._stop_ready_message()
            return

        # Show simple ready message without loading dots
        message = get_string("status.ready_to_generate")
        self.status_bar.showMessage(message)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Mockachu")
    app.setOrganizationName("Mockachu")
    app.setOrganizationDomain("mockachu.app")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
