#!/usr/bin/env python3
"""
Fixed unit tests for the DataGenerator service class.
Tests data generation with proper field structure including nullable_percentage.
"""

import pytest
from mockachu.services.data_generator import DataGenerator
from mockachu.generators.generator import GeneratorActions, GeneratorFormats, Generators


class TestDataGeneratorFixed:
    """Fixed test cases for DataGenerator service"""

    def setup_method(self):
        self.data_generator = DataGenerator()

    def test_reset_generators(self):
        """Test resetting generators"""
        # This should not raise an exception
        self.data_generator.reset_generators()

        # Test that we can still generate data after reset
        request = {
            "fields": [
                {
                    "name": "test_field",
                    "generator": "PERSON_GENERATOR",
                    "action": "RANDOM_PERSON_FIRST_NAME",
                    "parameters": [],
                    "nullable_percentage": 0
                }
            ],
            "rows": 2,
            "format": "JSON"
        }
        result = self.data_generator.generate(request)
        assert len(result) == 2

    def test_basic_data_generation(self):
        """Test basic data generation functionality"""
        request = {
            "fields": [
                {
                    "name": "first_name",
                    "generator": "PERSON_GENERATOR",
                    "action": "RANDOM_PERSON_FIRST_NAME",
                    "parameters": [],
                    "nullable_percentage": 0
                }
            ],
            "rows": 3,
            "format": "JSON"
        }
        result = self.data_generator.generate(request)

        assert len(result) == 3
        for row in result:
            assert "first_name" in row
            assert isinstance(row["first_name"], str)
            assert len(row["first_name"]) > 0

    def test_sequence_generator(self):
        """Test sequence generator functionality"""
        request = {
            "fields": [
                {
                    "name": "sequence_id",
                    "generator": "SEQUENCE_GENERATOR",
                    "action": "SEQUENTIAL_NUMBER",
                    "parameters": ["1", "1"],
                    "nullable_percentage": 0
                }
            ],
            "rows": 3,
            "format": "JSON"
        }
        result = self.data_generator.generate(request)

        assert len(result) == 3
        for row in result:
            assert "sequence_id" in row
            assert row["sequence_id"] is not None

    def test_multiple_fields(self):
        """Test generation with multiple fields"""
        request = {
            "fields": [
                {
                    "name": "name",
                    "generator": "PERSON_GENERATOR",
                    "action": "RANDOM_PERSON_FIRST_NAME",
                    "parameters": [],
                    "nullable_percentage": 0
                },
                {
                    "name": "animal",
                    "generator": "BIOLOGY_GENERATOR",
                    "action": "RANDOM_ANIMAL",
                    "parameters": [],
                    "nullable_percentage": 0
                }
            ],
            "rows": 2,
            "format": "JSON"
        }
        result = self.data_generator.generate(request)

        assert len(result) == 2
        for row in result:
            assert "name" in row
            assert "animal" in row

    def test_large_dataset(self):
        """Test generation of larger datasets"""
        request = {
            "fields": [
                {
                    "name": "id",
                    "generator": "SEQUENCE_GENERATOR",
                    "action": "SEQUENTIAL_NUMBER",
                    "parameters": ["1", "1"],
                    "nullable_percentage": 0
                }
            ],
            "rows": 100,
            "format": "JSON"
        }
        result = self.data_generator.generate(request)

        assert len(result) == 100
        for row in result:
            assert "id" in row
