from pathlib import Path
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton)
from PyQt6.QtCore import pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont
from ..localization.manager import get_string


def get_resource_path(relative_path):
    """Get the absolute path to a resource file within the package."""
    base_path = Path(__file__).parent.parent  # mockachu package root
    return str(base_path / relative_path)


class DatasetWarningDialog(QDialog):

    generation_confirmed = pyqtSignal()

    def __init__(self, parent=None, rows_count=0):
        super().__init__(parent)
        self.rows_count = rows_count

        self.setWindowTitle(get_string("dialogs.large_dataset.title"))
        self.setModal(True)
        self.resize(500, 300)

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Warning title
        title_label = QLabel(get_string("dialogs.large_dataset.warning_title"))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Main warning message
        warning_text = get_string(
            "dialogs.large_dataset.warning_message", self.rows_count)
        warning_label = QLabel(warning_text)
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)

        tips_label = QLabel(get_string(
            "dialogs.large_dataset.performance_tips_title"))
        tips_font = QFont()
        tips_font.setBold(True)
        tips_label.setFont(tips_font)
        layout.addWidget(tips_label)

        tips_text = "\n".join(get_string(
            "dialogs.large_dataset.performance_tips"))
        tips_details = QLabel(tips_text)
        layout.addWidget(tips_details)

        question_text = get_string(
            "dialogs.large_dataset.question", self.rows_count)
        question_label = QLabel(question_text)
        question_font = QFont()
        question_font.setBold(True)
        question_label.setFont(question_font)
        layout.addWidget(question_label)

        layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.cancel_btn = QPushButton()
        self.cancel_btn.setFixedSize(35, 35)
        self.cancel_btn.setIcon(
            QIcon(get_resource_path("ui/res/icons8-close-100.png")))
        self.cancel_btn.setIconSize(QSize(20, 20))
        self.cancel_btn.setToolTip(get_string("ui.tooltips.cancel_generation"))

        self.proceed_btn = QPushButton()
        self.proceed_btn.setFixedSize(35, 35)
        self.proceed_btn.setIcon(
            QIcon(get_resource_path("ui/res/icons8-done-100.png")))
        self.proceed_btn.setIconSize(QSize(20, 20))
        self.proceed_btn.setToolTip(
            get_string("ui.tooltips.proceed_generation"))

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.proceed_btn)
        layout.addLayout(button_layout)

    def connect_signals(self):

        self.proceed_btn.clicked.connect(self.confirm_generation)
        self.cancel_btn.clicked.connect(self.reject)

    def confirm_generation(self):

        self.generation_confirmed.emit()
        self.accept()
