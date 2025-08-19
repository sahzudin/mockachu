#!/usr/bin/env python3
"""
Fixed comprehensive unit tests for the FieldBuilderGenerator class.
Tests field joining and pattern replacement functionality.
"""

import pytest
from mockachu.generators.field_builder_generator import FieldBuilderGenerator
from mockachu.generators.generator import GeneratorActions, GeneratorActionParameters


class TestFieldBuilderGeneratorFixed:
    """Fixed test cases for FieldBuilderGenerator"""

    def setup_method(self):
        self.generator = FieldBuilderGenerator()

    def test_get_actions(self):
        """Test that get_actions returns the expected actions"""
        actions = self.generator.get_actions()
        assert isinstance(actions, list)
        assert GeneratorActions.FIELD_JOIN in actions

    def test_get_parameters(self):
        """Test parameter requirements for actions"""
        params = self.generator.get_parameters(GeneratorActions.FIELD_JOIN)
        assert 'PATTERN' in params

    def test_get_pattern_example(self):
        """Test the pattern example"""
        example = self.generator.get_pattern_example(
            GeneratorActions.FIELD_JOIN)
        assert isinstance(example, str)
        assert "{" in example and "}" in example

    def test_basic_field_join(self):
        """Test basic field joining functionality"""
        pattern = "{first_name}.{last_name}@example.com"
        field_values = {
            "first_name": "John",
            "last_name": "Doe"
        }

        result = self.generator._FieldBuilderGenerator__generate_field_join(
            pattern, **field_values)
        assert result == "John.Doe@example.com"

    def test_missing_field_handling(self):
        """Test handling of missing fields"""
        pattern = "{first_name}.{missing_field}@example.com"
        field_values = {
            "first_name": "John"
        }

        result = self.generator._FieldBuilderGenerator__generate_field_join(
            pattern, **field_values)
        assert "John" in result
        assert "{missing:missing_field}" in result

    def test_empty_pattern(self):
        """Test handling of empty pattern"""
        result = self.generator._FieldBuilderGenerator__generate_field_join("")
        assert result == ""

    def test_pattern_without_fields(self):
        """Test pattern without field placeholders"""
        pattern = "static-text-only"
        result = self.generator._FieldBuilderGenerator__generate_field_join(
            pattern)
        assert result == pattern

    def test_formatting_specifications(self):
        """Test field formatting specifications"""
        pattern = "{id:05d}"
        field_values = {
            "id": "123"
        }

        result = self.generator._FieldBuilderGenerator__generate_field_join(
            pattern, **field_values)
        assert "00123" in result  # Should be zero-padded

    def test_multiple_field_replacements(self):
        """Test multiple field replacements in one pattern"""
        pattern = "{prefix}-{middle}-{suffix}"
        field_values = {
            "prefix": "A",
            "middle": "B",
            "suffix": "C"
        }

        result = self.generator._FieldBuilderGenerator__generate_field_join(
            pattern, **field_values)
        assert result == "A-B-C"

    def test_complex_pattern(self):
        """Test complex pattern with mixed content"""
        pattern = "User: {username} | Email: {first_name}.{last_name}@domain.com | ID: {id:04d}"
        field_values = {
            "username": "johndoe",
            "first_name": "John",
            "last_name": "Doe",
            "id": "42"
        }

        result = self.generator._FieldBuilderGenerator__generate_field_join(
            pattern, **field_values)
        assert "User: johndoe" in result
        assert "Email: John.Doe@domain.com" in result
        assert "ID: 0042" in result

    def test_generate_method(self):
        """Test the main generate method"""
        result = self.generator.generate(GeneratorActions.FIELD_JOIN, "{test}")
        # Without field values provided, should return the pattern as-is
        assert "{test}" in result

    def test_generate_with_context(self):
        """Test generate_with_context method"""
        pattern = "{name}-{number}"
        row_data = {
            "name": "test",
            "number": "123"
        }

        result = self.generator.generate_with_context(
            GeneratorActions.FIELD_JOIN, row_data, pattern)
        assert result == "test-123"

    def test_set_current_row_data(self):
        """Test setting current row data"""
        row_data = {"test": "value"}
        self.generator.set_current_row_data(row_data)
        assert hasattr(self.generator, 'current_row_data')
        assert self.generator.current_row_data == row_data

    def test_invalid_formatting(self):
        """Test handling of invalid formatting specifications"""
        pattern = "{id:invalid_format}"
        field_values = {
            "id": "123"
        }

        result = self.generator._FieldBuilderGenerator__generate_field_join(
            pattern, **field_values)
        # Should handle invalid format gracefully
        assert "123" in result

    def test_none_field_values(self):
        """Test handling of None field values"""
        pattern = "{field1}.{field2}"
        field_values = {
            "field1": None,
            "field2": "value"
        }

        result = self.generator._FieldBuilderGenerator__generate_field_join(
            pattern, **field_values)
        assert "value" in result
        assert "{missing:field1}" in result

    def test_numeric_field_values(self):
        """Test handling of numeric field values"""
        pattern = "{number1}+{number2}={result}"
        field_values = {
            "number1": 5,
            "number2": 10,
            "result": 15
        }

        result = self.generator._FieldBuilderGenerator__generate_field_join(
            pattern, **field_values)
        assert result == "5+10=15"

    def test_edge_case_patterns(self):
        """Test edge case patterns"""
        # Pattern with repeated field references
        pattern = "{name} {name} {name}"
        field_values = {"name": "test"}

        result = self.generator._FieldBuilderGenerator__generate_field_join(
            pattern, **field_values)
        assert result == "test test test"

        # Pattern with no fields
        pattern = "no fields here"
        result = self.generator._FieldBuilderGenerator__generate_field_join(
            pattern, **field_values)
        assert result == pattern
