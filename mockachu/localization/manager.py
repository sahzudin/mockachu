"""
Localization manager for the Mockachu application.
Provides a centralized way to handle all UI strings and support multiple languages.
"""
import json
import os
from typing import Dict, Any
from PyQt6.QtCore import QSettings


class LocalizationManager:

    _instance = None
    _current_language = "en"
    _strings = {}
    _localization_dir = os.path.join(os.path.dirname(__file__), "strings")

    def __new__(cls):

        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):

        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.settings = QSettings("Mockachu", "Settings")
            self.load_language("en")

    def load_language(self, language_code: str) -> bool:

        try:
            language_file = os.path.join(
                self._localization_dir, f"{language_code}.json")

            if not os.path.exists(language_file):
                language_file = os.path.join(self._localization_dir, "en.json")
                language_code = "en"

            with open(language_file, 'r', encoding='utf-8') as f:
                self._strings = json.load(f)
                self._current_language = language_code
                return True

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading language {language_code}: {e}")
            self._load_default_strings()
            return False

    def _load_default_strings(self):

        self._strings = {
            "app": {
                "title": "Mockachu",
                "ready": "Ready to generate data"
            },
            "errors": {
                "validation_title": "Validation Error",
                "no_fields": "Please add at least one field before generating data.",
                "no_format": "Please select at least one output format.",
                "no_field_name": "Please provide a name for all fields.",
                "invalid_field": "Please complete the configuration for field '{}'.",
                "no_fields_to_save": "No fields to save. Please add at least one field.",
                "no_saved_configs": "No saved configurations found."
            }
        }

    def get_string(self, key: str, *args, **kwargs) -> str:
        """
        Get a localized string by key.

        Args:
            key: Dot-separated key path (e.g., "app.title" or "errors.no_fields")
            *args: Positional arguments for string formatting
            **kwargs: Keyword arguments for string formatting

        Returns:
            Localized string with formatting applied
        """
        try:
            keys = key.split('.')
            value = self._strings

            for k in keys:
                value = value[k]

            if args or kwargs:
                return value.format(*args, **kwargs)
            return value

        except (KeyError, TypeError):
            return f"[MISSING: {key}]"

    def get_current_language(self) -> str:

        return self._current_language

    def get_available_languages(self) -> list:

        try:
            languages = []
            for file in os.listdir(self._localization_dir):
                if file.endswith('.json'):
                    languages.append(file[:-5])  # Remove .json extension
            return sorted(languages)
        except FileNotFoundError:
            return ["en"]

    def set_language(self, language_code: str) -> bool:

        if self.load_language(language_code):
            self.settings.setValue("language", language_code)
            return True
        return False


_localization = LocalizationManager()


def get_string(key: str, *args, **kwargs) -> str:
    """
    Global function to get localized strings.

    Usage:
        from ..localization.manager import get_string
        title = get_string("app.title")
        error = get_string("errors.invalid_field", field_name)
    """
    return _localization.get_string(key, *args, **kwargs)


def set_language(language_code: str) -> bool:

    return _localization.set_language(language_code)


def get_current_language() -> str:

    return _localization.get_current_language()


def get_available_languages() -> list:

    return _localization.get_available_languages()
