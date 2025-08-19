import json
from pathlib import Path
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QListWidget, QMessageBox)
from PyQt6.QtCore import pyqtSignal, QSize
from PyQt6.QtGui import QIcon
from ..localization.manager import get_string


def get_resource_path(relative_path):
    """Get the absolute path to a resource file within the package."""
    base_path = Path(__file__).parent.parent  # mockachu package root
    return str(base_path / relative_path)


class SaveConfigurationDialog(QDialog):

    configuration_saved = pyqtSignal(str, dict)

    def __init__(self, parent=None, fields=None, row_count=100, saved_configurations=None):
        super().__init__(parent)
        self.fields = fields or []
        self.row_count = row_count
        self.saved_configurations = saved_configurations or {}

        self.setWindowTitle(get_string("dialogs.save_config.title"))
        self.setModal(True)
        self.resize(400, 150)

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(get_string("dialogs.save_config.instruction")))

        self.name_input = QLineEdit()
        self.name_input.setText(
            get_string("dialogs.save_config.default_name", len(self.saved_configurations) + 1))
        self.name_input.selectAll()
        layout.addWidget(self.name_input)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.save_btn = QPushButton()
        self.save_btn.setFixedSize(35, 35)
        self.save_btn.setIcon(
            QIcon(get_resource_path("ui/res/icons8-done-100.png")))
        self.save_btn.setIconSize(QSize(20, 20))
        self.save_btn.setToolTip(get_string("ui.tooltips.save_config"))

        self.cancel_btn = QPushButton()
        self.cancel_btn.setFixedSize(35, 35)
        self.cancel_btn.setIcon(
            QIcon(get_resource_path("ui/res/icons8-close-100.png")))
        self.cancel_btn.setIconSize(QSize(20, 20))
        self.cancel_btn.setToolTip(get_string("ui.buttons.cancel"))

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        layout.addLayout(button_layout)

    def connect_signals(self):

        self.save_btn.clicked.connect(self.save_config)
        self.cancel_btn.clicked.connect(self.reject)
        self.name_input.returnPressed.connect(self.save_config)

    def save_config(self):

        name = self.name_input.text().strip()
        if not name:
            # Use default name if empty instead of showing warning
            name = self.name_input.text(
            ) or get_string("dialogs.save_config.default_name", len(self.saved_configurations) + 1)

        field_configs = []
        for field_widget in self.fields:
            field_configs.append(field_widget.get_field_config())

        config_data = {
            "fields": field_configs,
            "timestamp": json.dumps({"saved_at": "now"}),
            "row_count": self.row_count
        }

        self.configuration_saved.emit(name, config_data)

        self.accept()


class LoadConfigurationDialog(QDialog):

    configuration_loaded = pyqtSignal(str, dict)
    configuration_deleted = pyqtSignal(str)

    def __init__(self, parent=None, saved_configurations=None):
        super().__init__(parent)
        self.saved_configurations = saved_configurations or {}

        self.setWindowTitle(get_string("dialogs.load_config.title"))
        self.setModal(True)
        self.resize(400, 300)

        self.setup_ui()
        self.connect_signals()
        self.populate_list()

    def setup_ui(self):

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(get_string("dialogs.load_config.instruction")))

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.load_btn = QPushButton()
        self.load_btn.setFixedSize(35, 35)
        self.load_btn.setIcon(
            QIcon(get_resource_path("ui/res/icons8-done-100.png")))
        self.load_btn.setIconSize(QSize(20, 20))
        self.load_btn.setToolTip(get_string(
            "ui.tooltips.load_selected_config"))

        self.cancel_btn = QPushButton()
        self.cancel_btn.setFixedSize(35, 35)
        self.cancel_btn.setIcon(
            QIcon(get_resource_path("ui/res/icons8-close-100.png")))
        self.cancel_btn.setIconSize(QSize(20, 20))
        self.cancel_btn.setToolTip(get_string("ui.buttons.cancel"))

        self.delete_btn = QPushButton()
        self.delete_btn.setFixedSize(35, 35)
        self.delete_btn.setIcon(QIcon(get_resource_path(
            "ui/res/icons8-horizontal-line-100.png")))
        self.delete_btn.setIconSize(QSize(20, 20))
        self.delete_btn.setToolTip(get_string(
            "ui.tooltips.delete_selected_config"))

        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.load_btn)
        layout.addLayout(button_layout)

    def connect_signals(self):

        self.load_btn.clicked.connect(self.load_selected)
        self.cancel_btn.clicked.connect(self.reject)
        self.delete_btn.clicked.connect(self.delete_selected)
        self.list_widget.itemDoubleClicked.connect(self.load_selected)

    def populate_list(self):

        self.list_widget.clear()
        for name in self.saved_configurations.keys():
            self.list_widget.addItem(name)

    def load_selected(self):

        current_item = self.list_widget.currentItem()
        if current_item:
            config_name = current_item.text()
            config_data = self.saved_configurations[config_name]
            self.configuration_loaded.emit(config_name, config_data)
            self.accept()
        else:
            QMessageBox.warning(self, get_string("dialogs.warning_title"),
                                get_string("dialogs.load_config.no_selection"))

    def delete_selected(self):

        current_item = self.list_widget.currentItem()
        if current_item:
            config_name = current_item.text()
            self.list_widget.takeItem(self.list_widget.row(current_item))
            self.configuration_deleted.emit(config_name)

    def update_configurations(self, saved_configurations):

        self.saved_configurations = saved_configurations
        self.populate_list()
