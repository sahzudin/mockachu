from pathlib import Path
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QComboBox, QPushButton, QSpinBox,
                             QGroupBox, QFormLayout,
                             QSizePolicy, QSlider, QTextEdit, QWidget, QFileDialog, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon
from ..generators.generator import GeneratorActionParameters, GeneratorActions, Generators
from ..generators.generator_identifier import GeneratorIdentifier
from ..localization.manager import get_string
from datetime import datetime
import re


def get_resource_path(relative_path):
    """Get the absolute path to a resource file within the package."""
    base_path = Path(__file__).parent.parent  # mockachu package root
    return str(base_path / relative_path)


class CustomListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(
            get_string("ui.placeholders.custom_list_items"))
        self.text_edit.setMinimumHeight(100)
        self.text_edit.setMaximumHeight(150)
        self.text_edit.setToolTip(
            get_string("ui.tooltips.import_list_items"))

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(8)

        button_layout.addStretch()

        self.import_button = QPushButton("")
        self.import_button.setObjectName("importButton")
        self.import_button.setToolTip(
            get_string("ui.tooltips.import_list_items"))
        self.import_button.setIcon(
            QIcon(get_resource_path("ui/res/icons8-import-100.png")))
        self.import_button.setIconSize(QSize(15, 15))
        self.import_button.setFixedSize(25, 25)
        self.import_button.clicked.connect(self.import_from_file)

        self.clear_button = QPushButton("")
        self.clear_button.setObjectName("clearButton")
        self.clear_button.setToolTip(
            get_string("ui.tooltips.clear_custom_list"))
        self.clear_button.setIcon(
            QIcon(get_resource_path("ui/res/icons8-remove-100.png")))
        self.clear_button.setIconSize(QSize(15, 15))
        self.clear_button.setFixedSize(25, 25)
        self.clear_button.clicked.connect(self.clear_list)

        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.clear_button)

        layout.addWidget(self.text_edit)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def import_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            get_string("dialogs.import_custom_list"),
            "",
            get_string("dialogs.file_filter")
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read().strip()
                    if content:
                        existing_content = self.text_edit.toPlainText().strip()
                        if existing_content:
                            self.text_edit.setPlainText(content)
                        else:
                            self.text_edit.setPlainText(content)
                    else:
                        self.text_edit.setPlainText("")
            except Exception as e:
                print(get_string("errors.importing_file").format(e))

    def clear_list(self):
        self.text_edit.clear()

    def toPlainText(self):
        return self.text_edit.toPlainText()

    def setPlainText(self, text):
        self.text_edit.setPlainText(text)

    def textChanged(self):
        return self.text_edit.textChanged


class CountriesListWidget(QWidget):
    selectionChanged = pyqtSignal()

    def __init__(self, generator_identifier=None):
        super().__init__()
        self.generator_identifier = generator_identifier
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.countries_list = QListWidget()
        self.countries_list.setSelectionMode(
            QListWidget.SelectionMode.MultiSelection)
        self.countries_list.setMaximumHeight(120)
        self.countries_list.setToolTip(
            get_string("ui.tooltips.select_multiple_countries"))

        self.countries_list.itemSelectionChanged.connect(
            self.selectionChanged.emit)

        self.populate_countries()

        layout.addWidget(self.countries_list)

        self.setLayout(layout)

    def populate_countries(self):
        if self.generator_identifier:
            try:
                from ..generators.generator import Generators
                geo_enum = Generators.GEO_GENERATOR
                geo_generator = self.generator_identifier.get_generator_by_identifier(
                    geo_enum)

                if geo_generator and hasattr(geo_generator, 'get_available_countries'):
                    countries = geo_generator.get_available_countries()
                    for country in countries:
                        item = QListWidgetItem(country)
                        self.countries_list.addItem(item)
            except Exception:
                common_countries = get_string("countries.fallback")
                for country in common_countries:
                    item = QListWidgetItem(country)
                    self.countries_list.addItem(item)

    def select_all_countries(self):
        for i in range(self.countries_list.count()):
            item = self.countries_list.item(i)
            item.setSelected(True)
        self.selectionChanged.emit()

    def clear_selection(self):
        self.countries_list.clearSelection()
        self.selectionChanged.emit()

    def get_selected_countries(self):
        selected_items = self.countries_list.selectedItems()
        return [item.text() for item in selected_items]

    def set_selected_countries(self, countries):
        self.countries_list.clearSelection()
        if isinstance(countries, str):
            countries = [c.strip() for c in countries.split(',') if c.strip()]

        for i in range(self.countries_list.count()):
            item = self.countries_list.item(i)
            if item.text() in countries:
                item.setSelected(True)

    def toPlainText(self):
        return ', '.join(self.get_selected_countries())

    def setPlainText(self, text):
        self.set_selected_countries(text)


class CreditCardBrandsWidget(QWidget):
    selectionChanged = pyqtSignal()

    def __init__(self, generator_identifier=None):
        super().__init__()
        self.generator_identifier = generator_identifier

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.brands_list = QListWidget()
        self.brands_list.setSelectionMode(
            # Single selection for credit card brands
            QListWidget.SelectionMode.SingleSelection)
        self.brands_list.setMaximumHeight(120)
        self.brands_list.setToolTip(
            get_string("parameters.display_names.CARD_BRAND"))

        self.brands_list.itemSelectionChanged.connect(
            self.selectionChanged.emit)

        self.populate_credit_card_brands()

        layout.addWidget(self.brands_list)

        self.setLayout(layout)

    def populate_credit_card_brands(self):
        if self.generator_identifier:
            try:
                from ..generators.generator import Generators
                money_enum = Generators.MONEY_GENERATOR
                money_generator = self.generator_identifier.get_generator_by_identifier(
                    money_enum)

                if money_generator and hasattr(money_generator, 'get_available_credit_card_brands'):
                    brands = money_generator.get_available_credit_card_brands()
                    for brand in brands:
                        item = QListWidgetItem(brand)
                        self.brands_list.addItem(item)
            except Exception:
                fallback_brands = get_string("credit_card_brands.fallback")
                for brand in fallback_brands:
                    item = QListWidgetItem(brand)
                    self.brands_list.addItem(item)

    def clear_selection(self):
        self.brands_list.clearSelection()
        self.selectionChanged.emit()

    def get_selected_brand(self):
        selected_items = self.brands_list.selectedItems()
        return selected_items[0].text() if selected_items else ""

    def set_selected_brand(self, brand):
        self.brands_list.clearSelection()
        if brand:
            for i in range(self.brands_list.count()):
                item = self.brands_list.item(i)
                if item.text() == brand.strip():
                    item.setSelected(True)
                    break

    def toPlainText(self):
        return self.get_selected_brand()

    def setPlainText(self, text):
        self.set_selected_brand(text)


class FieldConfigWidget(QGroupBox):
    field_changed = pyqtSignal()
    field_name_changed = pyqtSignal(str, str)
    field_data_changed = pyqtSignal(object)
    field_duplicate_requested = pyqtSignal(object)
    request_preview_refresh = pyqtSignal()

    def __init__(self, available_generators, field_number, remove_callback, duplicate_callback=None, move_up_callback=None, move_down_callback=None):
        super().__init__()
        self.available_generators = available_generators
        self.field_number = field_number  # Unique field number (never changes)
        self.remove_callback = remove_callback
        self.duplicate_callback = duplicate_callback
        self.move_up_callback = move_up_callback
        self.move_down_callback = move_down_callback
        self.previous_field_name = get_string(
            "field_defaults.name_template", field_number)

        self.generator_identifier = GeneratorIdentifier()

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.setObjectName("groupBox")

        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Fixed)

        field_name = get_string(
            "field_defaults.name_template", self.field_number)
        self.setTitle(get_string("field_defaults.title_template").format(
            self.field_number, field_name))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self.name_edit = QLineEdit()
        self.name_edit.setText(get_string(
            "field_defaults.name_template", self.field_number))
        self.name_edit.setPlaceholderText(
            get_string("ui.placeholders.field_name"))
        self.name_edit.setMinimumWidth(150)
        self.name_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        form_layout.addRow(get_string("ui.labels.name"), self.name_edit)

        self.generator_combo = QComboBox()
        self.generator_combo.setMinimumWidth(150)
        self.generator_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.generator_combo.setMinimumContentsLength(20)
        for i, generator in enumerate(self.available_generators["generators"]):
            display_name = generator.get("display_name", generator["name"])
            self.generator_combo.addItem(display_name, generator["name"])
            # Set tooltip for generator
            try:
                tooltip = get_string(
                    f"generators.descriptions.{generator['name']}")
                self.generator_combo.setItemData(
                    i, tooltip, Qt.ItemDataRole.ToolTipRole)
            except:
                pass  # No tooltip if description not found
        form_layout.addRow(get_string("ui.labels.generator"),
                           self.generator_combo)

        self.action_combo = QComboBox()
        self.action_combo.setMinimumWidth(150)
        self.action_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.action_combo.setMinimumContentsLength(20)
        form_layout.addRow(get_string("ui.labels.action"), self.action_combo)

        self.main_form_layout = form_layout

        nullable_layout = QHBoxLayout()

        self.nullable_slider = QSlider(Qt.Orientation.Horizontal)
        self.nullable_slider.setRange(0, 100)
        self.nullable_slider.setValue(0)
        self.nullable_slider.setMinimumWidth(100)
        self.nullable_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.nullable_slider.setTickInterval(25)
        nullable_layout.addWidget(self.nullable_slider)

        self.nullable_value_label = QLabel("0%")
        self.nullable_value_label.setMinimumWidth(30)
        nullable_layout.addWidget(self.nullable_value_label)

        nullable_layout.addStretch()

        self.move_up_btn = QPushButton("")
        self.move_up_btn.setObjectName("moveUpButton")
        self.move_up_btn.setToolTip(get_string("ui.tooltips.move_up"))
        self.move_up_btn.setIcon(
            QIcon(get_resource_path("ui/res/icons8-up-100.png")))
        self.move_up_btn.setIconSize(QSize(15, 15))
        self.move_up_btn.setFixedSize(25, 25)
        self.move_up_btn.clicked.connect(lambda: self.move_up_callback(
            self) if self.move_up_callback else None)
        nullable_layout.addWidget(self.move_up_btn)

        self.move_down_btn = QPushButton("")
        self.move_down_btn.setObjectName("moveDownButton")
        self.move_down_btn.setToolTip(get_string("ui.tooltips.move_down"))
        self.move_down_btn.setIcon(
            QIcon(get_resource_path("ui/res/icons8-down-100.png")))
        self.move_down_btn.setIconSize(QSize(15, 15))
        self.move_down_btn.setFixedSize(25, 25)
        self.move_down_btn.clicked.connect(lambda: self.move_down_callback(
            self) if self.move_down_callback else None)
        nullable_layout.addWidget(self.move_down_btn)

        self.duplicate_btn = QPushButton()
        self.duplicate_btn.setObjectName("duplicateButton")
        self.duplicate_btn.setToolTip(get_string("ui.tooltips.duplicate"))
        self.duplicate_btn.setIcon(
            QIcon(get_resource_path("ui/res/icons8-duplicate-100.png")))
        self.duplicate_btn.setIconSize(QSize(17, 17))
        self.duplicate_btn.setFixedSize(25, 25)
        self.duplicate_btn.clicked.connect(lambda: self.duplicate_callback(
            self) if self.duplicate_callback else None)
        nullable_layout.addWidget(self.duplicate_btn)

        self.remove_btn = QPushButton("")
        self.remove_btn.setObjectName("removeButton")
        self.remove_btn.setToolTip(get_string("ui.tooltips.remove_field"))
        self.remove_btn.setIcon(QIcon(get_resource_path(
            "ui/res/icons8-horizontal-line-100.png")))
        self.remove_btn.setIconSize(QSize(13, 15))
        self.remove_btn.setFixedSize(25, 25)
        self.remove_btn.clicked.connect(lambda: self.remove_callback(self))
        nullable_layout.addWidget(self.remove_btn)

        form_layout.addRow(get_string(
            "ui.labels.nullable_percentage"), nullable_layout)

        layout.addLayout(form_layout)

        self.update_actions()

        self.update_field_label()

    def setup_connections(self):
        self.generator_combo.currentTextChanged.connect(self.update_actions)
        self.action_combo.currentTextChanged.connect(self.update_parameters)
        self.nullable_slider.valueChanged.connect(self.update_nullable_label)
        self.name_edit.textChanged.connect(self.update_field_label)
        self.name_edit.textChanged.connect(self.on_field_name_changed)

        self.generator_combo.currentTextChanged.connect(
            lambda: self.field_changed.emit())
        self.action_combo.currentTextChanged.connect(
            lambda: self.field_changed.emit())

        self.generator_combo.currentTextChanged.connect(
            lambda: self.field_data_changed.emit(self))
        self.action_combo.currentTextChanged.connect(
            lambda: self.field_data_changed.emit(self))
        self.nullable_slider.valueChanged.connect(
            lambda: self.field_data_changed.emit(self))

    def update_nullable_label(self):
        value = self.nullable_slider.value()
        self.nullable_value_label.setText(f"{value}%")

    def update_field_label(self):
        try:
            if hasattr(self, 'name_edit') and self.name_edit is not None:
                name = self.name_edit.text().strip()
                if name:
                    self.setTitle(get_string("field_defaults.title_template").format(
                        self.field_number, name))
                else:
                    self.setTitle(
                        f"#{self.field_number} | field_{self.field_number}")
        except RuntimeError:
            pass

    def on_field_name_changed(self):
        current_name = self.get_field_name()
        if current_name != self.previous_field_name:
            self.field_name_changed.emit(
                self.previous_field_name, current_name)
            self.previous_field_name = current_name

    def on_field_builder_pattern_changed(self, text):
        import re

        field_pattern = r'\{([^}:]+)(?::([^}]*))?\}'
        matches = re.findall(field_pattern, text)

        if matches:
            self.request_preview_refresh.emit()

    def update_actions(self):
        self.action_combo.clear()

        current_index = self.generator_combo.currentIndex()
        if current_index >= 0:
            generator_name = self.generator_combo.itemData(current_index)
            for generator in self.available_generators["generators"]:
                if generator["name"] == generator_name:
                    for i, action in enumerate(generator["actions"]):
                        display_name = action.get(
                            "display_name", action["name"])
                        self.action_combo.addItem(display_name, action["name"])
                        # Set tooltip for action
                        try:
                            tooltip = get_string(
                                f"actions.descriptions.{action['name']}")
                            self.action_combo.setItemData(
                                i, tooltip, Qt.ItemDataRole.ToolTipRole)
                        except:
                            pass  # No tooltip if description not found
                    break

        self.update_parameters()

    def update_parameters(self):
        if hasattr(self, 'parameter_widgets'):
            for widget in self.parameter_widgets.values():
                if widget.parent():
                    for i in range(self.main_form_layout.rowCount()):
                        field_item = self.main_form_layout.itemAt(
                            i, QFormLayout.ItemRole.FieldRole)
                        if field_item and field_item.widget() == widget:
                            label_item = self.main_form_layout.itemAt(
                                i, QFormLayout.ItemRole.LabelRole)
                            if label_item and label_item.widget():
                                label_item.widget().deleteLater()
                            widget.deleteLater()
                            break

        generator_index = self.generator_combo.currentIndex()
        action_index = self.action_combo.currentIndex()

        if generator_index >= 0 and action_index >= 0:
            generator_name = self.generator_combo.itemData(generator_index)
            action_name = self.action_combo.itemData(action_index)
        else:
            return  # No valid selection

        parameters = []
        for generator in self.available_generators["generators"]:
            if generator["name"] == generator_name:
                for action in generator["actions"]:
                    if action["name"] == action_name:
                        parameters = action.get("parameters", [])
                        break
                break

        self.parameter_widgets = {}

        action_row = -1
        for i in range(self.main_form_layout.rowCount()):
            field_item = self.main_form_layout.itemAt(
                i, QFormLayout.ItemRole.FieldRole)
            if field_item and field_item.widget() == self.action_combo:
                action_row = i
                break

        insert_position = action_row + 1

        for param in parameters:
            widget = None
            label_text = ""

            if param == GeneratorActionParameters.LENGTH.name:
                widget = QSpinBox()
                widget.setRange(1, 1000)
                widget.setValue(10)
                widget.setMinimumWidth(150)
                label_text = get_string("ui.labels.length")

            elif param == GeneratorActionParameters.PATTERN.name:
                widget = QLineEdit()

                label_text = get_string("ui.labels.pattern")
                pattern_example = ""
                try:
                    generator_enum = Generators[generator_name]
                    generator_instance = self.generator_identifier.get_generator_by_identifier(
                        generator_enum)
                    action_enum = GeneratorActions[action_name]
                    if generator_instance and hasattr(generator_instance, 'get_pattern_example'):
                        pattern_example = generator_instance.get_pattern_example(
                            action_enum)
                except (KeyError, AttributeError):
                    pass  # Fall back to empty if any errors occur

                if pattern_example and pattern_example != "Enter pattern...":
                    widget.setText(pattern_example)  # Set as default value
                    # Also set as placeholder
                    widget.setPlaceholderText(pattern_example)
                else:
                    widget.setPlaceholderText(get_string(
                        "ui.placeholders.pattern_input"))

                if generator_name == "FIELD_BUILDER_GENERATOR":
                    widget.textChanged.connect(
                        self.on_field_builder_pattern_changed)

                widget.setMinimumWidth(150)
                label_text = get_string("ui.labels.pattern")

            elif param in [GeneratorActionParameters.START_DATE.name, GeneratorActionParameters.END_DATE.name]:
                action_index = self.action_combo.currentIndex()
                action_name = ""
                if action_index >= 0:
                    action_name = self.action_combo.itemData(
                        action_index) or ""

                if action_name == "RANDOM_DATE_TIME":
                    widget = QLineEdit()
                    widget.setPlaceholderText(get_string(
                        "ui.placeholders.datetime_format"))
                    widget.setMinimumWidth(200)
                    if param == GeneratorActionParameters.START_DATE.name:
                        label_text = get_string("ui.labels.start")
                        widget.setText("2000-01-01 00:00:00")  # Default start
                    else:
                        label_text = get_string("ui.labels.end")
                        now = datetime.now()
                        widget.setText(f"{now.strftime('%Y-%m-%d')} 23:59:59")
                    widget.setInputMask("9999-99-99 99:99:99")
                    widget.textChanged.connect(
                        lambda text, p=param: self.validate_datetime_parameter(p, text))
                else:
                    widget = QLineEdit()
                    widget.setPlaceholderText(
                        get_string("ui.placeholders.date_format"))
                    widget.setMinimumWidth(150)
                    label_text = f"{param.lower().replace('_', ' ').title()}:"
                    if param == GeneratorActionParameters.START_DATE.name:
                        label_text = get_string("ui.labels.start")
                        widget.setText("2000-01-01")  # Default start date
                    else:
                        label_text = get_string("ui.labels.end")
                        widget.setText(datetime.now().strftime(
                            '%Y-%m-%d'))  # Default end date
                    widget.setInputMask("9999-99-99")
                    widget.textChanged.connect(
                        lambda text, p=param: self.validate_date_time_parameter(p, text))

            elif param in [GeneratorActionParameters.START_TIME.name, GeneratorActionParameters.END_TIME.name]:
                action_index = self.action_combo.currentIndex()
                action_name = ""
                if action_index >= 0:
                    action_name = self.action_combo.itemData(
                        action_index) or ""

                if action_name == "RANDOM_DATE_TIME":
                    continue  # Skip separate time inputs for datetime action

                widget = QLineEdit()
                widget.setPlaceholderText(
                    get_string("ui.placeholders.time_format"))
                widget.setMinimumWidth(150)
                label_text = f"{param.lower().replace('_', ' ').title()}:"
                if param == GeneratorActionParameters.START_TIME.name:
                    label_text = get_string("ui.labels.start")
                    widget.setText("00:00:00")  # Default start time
                else:
                    label_text = get_string("ui.labels.end")
                    widget.setText("23:59:59")  # Default end time
                widget.setInputMask("99:99:99")
                widget.textChanged.connect(
                    lambda text, p=param: self.validate_date_time_parameter(p, text))

            elif param in [GeneratorActionParameters.START_TIMESTAMP.name, GeneratorActionParameters.END_TIMESTAMP.name]:
                widget = QSpinBox()
                widget.setRange(0, 2147483647)  # Max timestamp
                widget.setValue(1640995200)  # 2022-01-01
                widget.setMinimumWidth(150)
                label_text = get_string("ui.labels.start")
                widget.valueChanged.connect(
                    lambda value, p=param: self.validate_timestamp_range(p, value))

            elif param in [GeneratorActionParameters.COUNTRY.name, GeneratorActionParameters.ISO_CODE_2.name, GeneratorActionParameters.ISO_CODE_3.name]:
                widget = QLineEdit()
                widget.setPlaceholderText(
                    f"Enter {param.lower().replace('_', ' ')}...")
                widget.setMinimumWidth(150)
                label_text = f"{param.lower().replace('_', ' ').title()}:"

            elif param in [GeneratorActionParameters.START_RANGE.name, GeneratorActionParameters.END_RANGE.name]:
                widget = QSpinBox()
                # Allow negative values for number generation
                widget.setRange(-1000000, 1000000)
                if "START" in param:
                    widget.setValue(0)  # Default start value is 0
                else:
                    widget.setValue(1000)  # Default end value is 1000
                widget.setMinimumWidth(150)
                label_text = get_string(
                    "ui.labels.start") if "START" in param else get_string("ui.labels.end")

            elif param == GeneratorActionParameters.PRECISION.name:
                widget = QSpinBox()
                widget.setRange(0, 10)  # 0 to 10 decimal places
                widget.setValue(2)  # Default precision
                widget.setMinimumWidth(150)
                label_text = get_string("parameters.display_names.PRECISION")

            elif param == GeneratorActionParameters.START_SEQUENCE.name:
                widget = QSpinBox()
                widget.setRange(1, 1000000)
                widget.setValue(1)
                widget.setMinimumWidth(150)
                label_text = get_string("ui.labels.start")

            elif param == GeneratorActionParameters.INTERVAL_SEQUENCE.name:
                widget = QSpinBox()
                widget.setRange(-1000, 1000)
                widget.setValue(1)
                widget.setMinimumWidth(150)
                label_text = get_string("ui.labels.interval")

            elif param == GeneratorActionParameters.DATE_FORMAT.name:
                widget = QLineEdit()
                widget.setPlaceholderText("%Y-%m-%d")
                widget.setText("%Y-%m-%d")  # Default date format
                widget.setMinimumWidth(150)
                widget.setToolTip(
                    get_string("ui.tooltips.date_format_tooltip"))
                label_text = get_string("ui.labels.format")

            elif param == GeneratorActionParameters.TIME_FORMAT.name:
                widget = QLineEdit()
                widget.setPlaceholderText("%H:%M:%S")
                widget.setText("%H:%M:%S")  # Default time format
                widget.setMinimumWidth(150)
                widget.setToolTip(
                    get_string("ui.tooltips.time_format_tooltip"))
                label_text = get_string("ui.labels.format")

            elif param == GeneratorActionParameters.DATETIME_FORMAT.name:
                widget = QLineEdit()
                widget.setPlaceholderText("%Y-%m-%d %H:%M:%S")
                widget.setText("%Y-%m-%d %H:%M:%S")  # Default datetime format
                widget.setMinimumWidth(200)
                widget.setToolTip(
                    get_string("ui.tooltips.datetime_format_tooltip"))
                label_text = get_string("ui.labels.format")

            elif param == GeneratorActionParameters.CUSTOM_LIST.name:
                widget = CustomListWidget()
                widget.setMinimumWidth(250)
                label_text = get_string("ui.labels.custom_list")

            elif param == GeneratorActionParameters.COUNTRIES_LIST.name:
                widget = CountriesListWidget(self.generator_identifier)
                widget.setMinimumWidth(250)
                label_text = get_string("ui.labels.countries")

            elif param == GeneratorActionParameters.CARD_BRAND.name:
                widget = CreditCardBrandsWidget(self.generator_identifier)
                widget.setMinimumWidth(250)
                label_text = get_string("parameters.display_names.CARD_BRAND")

            if widget:
                widget.setSizePolicy(
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                self.main_form_layout.insertRow(
                    insert_position, label_text, widget)
                self.parameter_widgets[param] = widget

                is_date_time_param = param in [
                    GeneratorActionParameters.START_DATE.name,
                    GeneratorActionParameters.END_DATE.name,
                    GeneratorActionParameters.START_TIME.name,
                    GeneratorActionParameters.END_TIME.name
                ]

                if not is_date_time_param:
                    if hasattr(widget, 'textChanged') and not isinstance(widget, CustomListWidget):
                        widget.textChanged.connect(
                            lambda: self.field_data_changed.emit(self))
                    elif hasattr(widget, 'valueChanged'):
                        widget.valueChanged.connect(
                            lambda: self.field_data_changed.emit(self))
                    elif hasattr(widget, 'currentTextChanged'):  # For QComboBox
                        widget.currentTextChanged.connect(
                            lambda: self.field_data_changed.emit(self))
                    elif isinstance(widget, CustomListWidget):  # For CustomListWidget
                        widget.textChanged().connect(
                            lambda: self.field_data_changed.emit(self))
                    elif isinstance(widget, CountriesListWidget):  # For CountriesListWidget
                        widget.selectionChanged.connect(
                            lambda: self.field_data_changed.emit(self))
                    # For CreditCardBrandsWidget
                    elif isinstance(widget, CreditCardBrandsWidget):
                        widget.selectionChanged.connect(
                            lambda: self.field_data_changed.emit(self))

                insert_position += 1

    def set_remove_button_enabled(self, enabled):
        try:
            if hasattr(self, 'remove_btn') and self.remove_btn is not None:
                self.remove_btn.setEnabled(enabled)
        except RuntimeError:
            pass

    def set_move_buttons_enabled(self, move_up_enabled, move_down_enabled):
        try:
            if hasattr(self, 'move_up_btn') and self.move_up_btn is not None:
                self.move_up_btn.setEnabled(move_up_enabled)
            if hasattr(self, 'move_down_btn') and self.move_down_btn is not None:
                self.move_down_btn.setEnabled(move_down_enabled)
        except RuntimeError:
            pass

    def get_field_name(self):
        try:
            if hasattr(self, 'name_edit') and self.name_edit is not None:
                return self.name_edit.text().strip() or f"field_{self.field_number}"
            else:
                return f"field_{self.field_number}"
        except RuntimeError:
            return f"field_{self.field_number}"

    def get_field_number(self):
        return self.field_number

    def is_valid(self):
        return bool(self.name_edit.text().strip())

    def validate_date_time_parameter(self, param_name, text):
        if param_name not in self.parameter_widgets:
            return

        widget = self.parameter_widgets[param_name]
        if not isinstance(widget, QLineEdit):
            return

        widget.setStyleSheet("")

        if param_name in [GeneratorActionParameters.START_DATE.name, GeneratorActionParameters.END_DATE.name]:
            if not text or len(text) != 10:
                return  # Incomplete, don't validate yet

            import re
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', text):
                widget.setStyleSheet("border: 2px solid red;")
                return

            try:
                datetime.strptime(text, "%Y-%m-%d")
                is_valid = True
            except ValueError:
                is_valid = False
                widget.setStyleSheet("border: 2px solid red;")

        elif param_name in [GeneratorActionParameters.START_TIME.name, GeneratorActionParameters.END_TIME.name]:
            if not text or len(text) != 8:
                return  # Incomplete, don't validate yet

            import re
            if not re.match(r'^\d{2}:\d{2}:\d{2}$', text):
                widget.setStyleSheet("border: 2px solid red;")
                return

            try:
                datetime.strptime(text, "%H:%M:%S")
                is_valid = True
            except ValueError:
                is_valid = False
                widget.setStyleSheet("border: 2px solid red;")
        else:
            return

        if is_valid:
            widget.setStyleSheet("")
            range_valid = self.validate_date_time_range()
            if range_valid:
                self.clear_range_validation_errors()
                self.field_data_changed.emit(self)
            else:
                self.show_range_validation_error()

    def validate_datetime_parameter(self, param_name, text):
        if param_name not in self.parameter_widgets:
            return

        widget = self.parameter_widgets[param_name]
        if not isinstance(widget, QLineEdit):
            return

        widget.setStyleSheet("")

        if not text or len(text) != 19:
            return  # Incomplete, don't validate yet

        if not re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', text):
            widget.setStyleSheet("border: 2px solid red;")
            return

        try:
            datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
            is_valid = True
        except ValueError:
            is_valid = False
            widget.setStyleSheet("border: 2px solid red;")

        if is_valid:
            widget.setStyleSheet("")
            range_valid = self.validate_datetime_range()
            if range_valid:
                self.clear_datetime_range_validation_errors()
                self.field_data_changed.emit(self)
            else:
                self.show_datetime_range_validation_error()

    def validate_date_time_range(self):
        if not hasattr(self, 'parameter_widgets'):
            return True

        start_date_widget = self.parameter_widgets.get(
            GeneratorActionParameters.START_DATE.name)
        end_date_widget = self.parameter_widgets.get(
            GeneratorActionParameters.END_DATE.name)

        if start_date_widget and end_date_widget:
            start_text = start_date_widget.text().strip()
            end_text = end_date_widget.text().strip()

            if start_text and end_text:
                try:
                    start_date = datetime.strptime(start_text, "%Y-%m-%d")
                    end_date = datetime.strptime(end_text, "%Y-%m-%d")
                    if end_date < start_date:
                        return False
                except ValueError:
                    return False

        start_time_widget = self.parameter_widgets.get(
            GeneratorActionParameters.START_TIME.name)
        end_time_widget = self.parameter_widgets.get(
            GeneratorActionParameters.END_TIME.name)

        if start_time_widget and end_time_widget:
            start_text = start_time_widget.text().strip()
            end_text = end_time_widget.text().strip()

            if start_text and end_text:
                try:
                    start_time = datetime.strptime(start_text, "%H:%M:%S")
                    end_time = datetime.strptime(end_text, "%H:%M:%S")
                    if end_time < start_time:
                        return False
                except ValueError:
                    return False

        return True

    def validate_datetime_range(self):
        if not hasattr(self, 'parameter_widgets'):
            return True

        start_datetime_widget = self.parameter_widgets.get(
            GeneratorActionParameters.START_DATE.name)
        end_datetime_widget = self.parameter_widgets.get(
            GeneratorActionParameters.END_DATE.name)

        if start_datetime_widget and end_datetime_widget:
            start_text = start_datetime_widget.text().strip()
            end_text = end_datetime_widget.text().strip()

            if start_text and end_text and len(start_text) == 19 and len(end_text) == 19:
                try:
                    start_dt = datetime.strptime(
                        start_text, "%Y-%m-%d %H:%M:%S")
                    end_dt = datetime.strptime(end_text, "%Y-%m-%d %H:%M:%S")
                    if end_dt < start_dt:
                        return False
                except ValueError:
                    return False

        return True

    def show_datetime_range_validation_error(self):
        if not hasattr(self, 'parameter_widgets'):
            return

        start_datetime_widget = self.parameter_widgets.get(
            GeneratorActionParameters.START_DATE.name)
        end_datetime_widget = self.parameter_widgets.get(
            GeneratorActionParameters.END_DATE.name)

        if start_datetime_widget and end_datetime_widget:
            start_text = start_datetime_widget.text().strip()
            end_text = end_datetime_widget.text().strip()

            if start_text and end_text and len(start_text) == 19 and len(end_text) == 19:
                try:
                    start_dt = datetime.strptime(
                        start_text, "%Y-%m-%d %H:%M:%S")
                    end_dt = datetime.strptime(end_text, "%Y-%m-%d %H:%M:%S")
                    if end_dt < start_dt:
                        end_datetime_widget.setStyleSheet(
                            "border: 2px solid red;")
                        end_datetime_widget.setToolTip(
                            get_string("errors.datetime_validation.end_before_start_datetime"))
                    else:
                        end_datetime_widget.setStyleSheet("")
                        end_datetime_widget.setToolTip("")
                except ValueError:
                    pass

    def show_range_validation_error(self):
        if not hasattr(self, 'parameter_widgets'):
            return

        start_date_widget = self.parameter_widgets.get(
            GeneratorActionParameters.START_DATE.name)
        end_date_widget = self.parameter_widgets.get(
            GeneratorActionParameters.END_DATE.name)

        if start_date_widget and end_date_widget:
            start_text = start_date_widget.text().strip()
            end_text = end_date_widget.text().strip()

            if start_text and end_text:
                try:
                    start_date = datetime.strptime(start_text, "%Y-%m-%d")
                    end_date = datetime.strptime(end_text, "%Y-%m-%d")
                    if end_date < start_date:
                        end_date_widget.setStyleSheet("border: 2px solid red;")
                        end_date_widget.setToolTip(
                            get_string("errors.datetime_validation.end_before_start_date"))
                    else:
                        end_date_widget.setStyleSheet("")
                        end_date_widget.setToolTip("")
                except ValueError:
                    pass

        start_time_widget = self.parameter_widgets.get(
            GeneratorActionParameters.START_TIME.name)
        end_time_widget = self.parameter_widgets.get(
            GeneratorActionParameters.END_TIME.name)

        if start_time_widget and end_time_widget:
            start_text = start_time_widget.text().strip()
            end_text = end_time_widget.text().strip()

            if start_text and end_text:
                try:
                    start_time = datetime.strptime(start_text, "%H:%M:%S")
                    end_time = datetime.strptime(end_text, "%H:%M:%S")
                    if end_time < start_time:
                        end_time_widget.setStyleSheet("border: 2px solid red;")
                        end_time_widget.setToolTip(
                            get_string("errors.datetime_validation.end_before_start_time"))
                    else:
                        end_time_widget.setStyleSheet("")
                        end_time_widget.setToolTip("")
                except ValueError:
                    pass

    def clear_range_validation_errors(self):
        if not hasattr(self, 'parameter_widgets'):
            return

        for param_name in [GeneratorActionParameters.START_DATE.name, GeneratorActionParameters.END_DATE.name,
                           GeneratorActionParameters.START_TIME.name, GeneratorActionParameters.END_TIME.name,
                           GeneratorActionParameters.START_TIMESTAMP.name, GeneratorActionParameters.END_TIMESTAMP.name]:
            widget = self.parameter_widgets.get(param_name)
            if widget:
                widget.setStyleSheet("")
                widget.setToolTip("")

    def clear_datetime_range_validation_errors(self):
        if not hasattr(self, 'parameter_widgets'):
            return

        start_datetime_widget = self.parameter_widgets.get(
            GeneratorActionParameters.START_DATE.name)
        end_datetime_widget = self.parameter_widgets.get(
            GeneratorActionParameters.END_DATE.name)

        if start_datetime_widget:
            start_datetime_widget.setStyleSheet("")
            start_datetime_widget.setToolTip("")
        if end_datetime_widget:
            end_datetime_widget.setStyleSheet("")
            end_datetime_widget.setToolTip("")

    def validate_timestamp_range(self, param_name, value):
        if not hasattr(self, 'parameter_widgets'):
            return

        start_timestamp_widget = self.parameter_widgets.get(
            GeneratorActionParameters.START_TIMESTAMP.name)
        end_timestamp_widget = self.parameter_widgets.get(
            GeneratorActionParameters.END_TIMESTAMP.name)

        if start_timestamp_widget and end_timestamp_widget:
            start_value = start_timestamp_widget.value()
            end_value = end_timestamp_widget.value()

            start_timestamp_widget.setStyleSheet("")
            start_timestamp_widget.setToolTip("")
            end_timestamp_widget.setStyleSheet("")
            end_timestamp_widget.setToolTip("")

            if end_value < start_value:
                if param_name == GeneratorActionParameters.START_TIMESTAMP.name:
                    start_timestamp_widget.setStyleSheet(
                        "border: 2px solid red;")
                    start_timestamp_widget.setToolTip(
                        get_string("errors.datetime_validation.invalid_timestamp_start"))
                else:
                    end_timestamp_widget.setStyleSheet(
                        "border: 2px solid red;")
                    end_timestamp_widget.setToolTip(
                        get_string("errors.datetime_validation.invalid_timestamp_end"))
            else:
                self.field_data_changed.emit(self)

    def is_valid_date(self, date_text):
        if not date_text or len(date_text) != 10:
            return False

        import re
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_text):
            return False

        try:
            datetime.strptime(date_text, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def is_valid_time(self, time_text):
        if not time_text or len(time_text) != 8:
            return False

        import re
        if not re.match(r'^\d{2}:\d{2}:\d{2}$', time_text):
            return False

        try:
            datetime.strptime(time_text, "%H:%M:%S")
            return True
        except ValueError:
            return False

    def is_valid_datetime(self, datetime_text):
        if not datetime_text or len(datetime_text) != 19:
            return False

        import re
        if not re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', datetime_text):
            return False

        try:
            datetime.strptime(datetime_text, "%Y-%m-%d %H:%M:%S")
            return True
        except ValueError:
            return False

    def get_field_config(self):
        generator_index = self.generator_combo.currentIndex()
        action_index = self.action_combo.currentIndex()

        generator_name = ""
        action_name = ""

        if generator_index >= 0:
            generator_name = self.generator_combo.itemData(
                generator_index) or ""
        if action_index >= 0:
            action_name = self.action_combo.itemData(action_index) or ""

        config = {
            "name": self.get_field_name(),
            "generator": generator_name,
            "action": action_name,
            "nullable_percentage": self.nullable_slider.value()
        }

        parameters = []
        if hasattr(self, 'parameter_widgets'):
            action_index = self.action_combo.currentIndex()
            action_name = ""
            if action_index >= 0:
                action_name = self.action_combo.itemData(action_index) or ""

            if action_name in ["RANDOM_DATE", "RANDOM_TIME", "RANDOM_DATE_TIME", "RANDOM_UNIX_TIMESTAMP", "RANDOM_NUMBER", "RANDOM_DECIMAL_NUMBER"]:
                if action_name == "RANDOM_DATE_TIME":
                    start_datetime_widget = self.parameter_widgets.get(
                        GeneratorActionParameters.START_DATE.name)
                    end_datetime_widget = self.parameter_widgets.get(
                        GeneratorActionParameters.END_DATE.name)

                    if start_datetime_widget and end_datetime_widget:
                        start_text = start_datetime_widget.text().strip()
                        end_text = end_datetime_widget.text().strip()

                        if start_text and self.is_valid_datetime(start_text):
                            start_date, start_time = start_text.split(' ')
                            parameters.extend([start_date, end_text.split(' ')[0] if end_text and self.is_valid_datetime(end_text) else "",
                                               start_time, end_text.split(' ')[1] if end_text and self.is_valid_datetime(end_text) else ""])
                        else:
                            parameters.extend(["", "", "", ""])

                    datetime_format_widget = self.parameter_widgets.get(
                        GeneratorActionParameters.DATETIME_FORMAT.name)

                    datetime_format = datetime_format_widget.text(
                    ).strip() if datetime_format_widget else ""

                    parameters.append(datetime_format)
                else:
                    param_names = self.get_current_action_parameters()
                    for param_name in param_names:
                        if param_name in self.parameter_widgets:
                            widget = self.parameter_widgets[param_name]
                            if isinstance(widget, QSpinBox):
                                parameters.append(widget.value())
                            elif isinstance(widget, QLineEdit):
                                text = widget.text().strip()
                                if param_name in [GeneratorActionParameters.START_DATE.name, GeneratorActionParameters.END_DATE.name]:
                                    if text and self.is_valid_date(text):
                                        parameters.append(text)
                                    else:
                                        parameters.append("")
                                elif param_name in [GeneratorActionParameters.START_TIME.name, GeneratorActionParameters.END_TIME.name]:
                                    if text and self.is_valid_time(text):
                                        parameters.append(text)
                                    else:
                                        parameters.append("")
                                else:
                                    parameters.append(text)
                        else:
                            parameters.append("")
            else:
                for param_name, widget in self.parameter_widgets.items():
                    if isinstance(widget, QSpinBox):
                        value = widget.value()
                        if value > 0:  # Only add non-zero values
                            parameters.append(value)
                    elif isinstance(widget, QLineEdit):
                        text = widget.text().strip()
                        if text:
                            parameters.append(text)
                    elif isinstance(widget, QTextEdit):  # Support for QTextEdit
                        text = widget.toPlainText().strip()
                        if text:
                            parameters.append(text)
                    elif isinstance(widget, CustomListWidget):
                        text = widget.toPlainText().strip()
                        if text:
                            parameters.append(text)
                    elif isinstance(widget, CountriesListWidget):
                        selected_countries = widget.get_selected_countries()
                        if selected_countries:
                            parameters.append(selected_countries)

        if parameters:
            config["parameters"] = parameters

        return config

    def get_current_action_parameters(self):
        try:
            generator_index = self.generator_combo.currentIndex()
            action_index = self.action_combo.currentIndex()

            if generator_index >= 0 and action_index >= 0:
                generator_name = self.generator_combo.itemData(generator_index)
                action_name = self.action_combo.itemData(action_index)

                if generator_name and action_name:
                    generator_identifier = GeneratorIdentifier()
                    generator_enum = Generators[generator_name]
                    action_enum = GeneratorActions[action_name]
                    generator = generator_identifier.get_generator_by_identifier(
                        generator_enum)

                    if generator:
                        return generator.get_parameters(action_enum)
        except Exception as e:
            print(get_string("errors.generation_error_title") + f": {e}")

        return []

    def refresh_ui_text(self):
        try:
            field_name = self.get_field_name() or get_string(
                "field_defaults.name_template").format(self.field_number)
            self.setTitle(get_string("field_defaults.title_template").format(
                self.field_number, field_name))

            if hasattr(self, 'remove_btn'):
                self.remove_btn.setToolTip(
                    get_string("ui.tooltips.remove_field"))

            if hasattr(self, 'name_input'):
                current_placeholder = self.name_input.placeholderText()
                if "Enter field name" in current_placeholder or "campo" in current_placeholder:
                    self.name_input.setPlaceholderText(
                        get_string("ui.placeholders.field_name"))

            if hasattr(self, 'parameter_widgets'):
                for param_name, widget in self.parameter_widgets.items():
                    if isinstance(widget, QLineEdit):
                        current_placeholder = widget.placeholderText()
                        if "Enter pattern" in current_placeholder or "patrón" in current_placeholder:
                            widget.setPlaceholderText(get_string(
                                "ui.placeholders.pattern_input"))

        except Exception as e:
            print(get_string("errors.generation_error_title") + f": {e}")
