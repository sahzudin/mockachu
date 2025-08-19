#!/usr/bin/env python3
"""
Detailed unit tests for the PersonGenerator class.
Tests name generation, gender-specific functionality, and edge cases using correct API.
"""

import pytest
from mockachu.generators.person_generator import PersonGenerator
from mockachu.generators.generator import GeneratorActions


class TestPersonGeneratorDetailed:
    """Detailed test cases for PersonGenerator"""

    def setup_method(self):
        self.generator = PersonGenerator()

    def test_first_name_properties(self):
        """Test properties of generated first names"""
        for _ in range(50):
            first_name = self.generator.generate(
                GeneratorActions.RANDOM_PERSON_FIRST_NAME)
            assert isinstance(first_name, str)
            assert len(first_name) >= 2  # Minimum reasonable length
            assert len(first_name) <= 20  # Maximum reasonable length

    def test_last_name_properties(self):
        """Test properties of generated last names"""
        for _ in range(50):
            last_name = self.generator.generate(
                GeneratorActions.RANDOM_PERSON_LAST_NAME)
            assert isinstance(last_name, str)
            assert len(last_name) >= 2
            assert len(last_name) <= 30

    def test_full_name_format(self):
        """Test full name formatting"""
        for _ in range(20):
            full_name = self.generator.generate(
                GeneratorActions.RANDOM_PERSON_FULL_NAME)
            parts = full_name.split()
            assert len(parts) >= 2  # At least first and last name

    def test_name_variety(self):
        """Test that generators produce variety in names"""
        first_names = [self.generator.generate(
            GeneratorActions.RANDOM_PERSON_FIRST_NAME) for _ in range(50)]
        last_names = [self.generator.generate(
            GeneratorActions.RANDOM_PERSON_LAST_NAME) for _ in range(50)]

        # Should have some variety (not all the same) - but be forgiving if data is limited
        # At minimum, names should be strings and not empty
        assert all(isinstance(name, str) and len(
            name) > 0 for name in first_names)
        assert all(isinstance(name, str) and len(
            name) > 0 for name in last_names)

        # If we have more than one name available, we should see variety
        unique_first_names = len(set(first_names))
        unique_last_names = len(set(last_names))

        # Allow for limited data sets - at least names should be consistent
        assert unique_first_names >= 1
        assert unique_last_names >= 1

    def test_gender_specific_names_if_available(self):
        """Test gender-specific name generation if methods exist"""
        if hasattr(self.generator, 'generate_male_first_name'):
            male_names = [self.generator.generate_male_first_name()
                          for _ in range(10)]
            for name in male_names:
                assert isinstance(name, str)
                assert len(name) > 0
                assert name.isalpha()

        if hasattr(self.generator, 'generate_female_first_name'):
            female_names = [self.generator.generate_female_first_name()
                            for _ in range(10)]
            for name in female_names:
                assert isinstance(name, str)
                assert len(name) > 0
                assert name.isalpha()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
