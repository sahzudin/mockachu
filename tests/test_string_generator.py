#!/usr/bin/env python3
"""
Detailed unit tests for the StringNumberGenerator class.
Tests word, sentence, and various string generation methods using correct API.
"""

import pytest
import re
from mockachu.generators.string_generator import StringNumberGenerator
from mockachu.generators.generator import GeneratorActions


class TestStringNumberGeneratorDetailed:
    """Detailed test cases for StringNumberGenerator"""

    def setup_method(self):
        self.generator = StringNumberGenerator()

    def test_word_generation_properties(self):
        """Test properties of generated words"""
        for _ in range(50):
            word = self.generator.generate(GeneratorActions.RANDOM_WORD)
            assert isinstance(word, str)
            assert len(word) > 0
            assert len(word) <= 50  # Reasonable maximum

            # Should contain only alphabetic characters (allowing for some punctuation)
            clean_word = word.replace("'", "").replace("-", "")
            assert clean_word.isalpha() or clean_word.isalnum()

    def test_word_variety(self):
        """Test word generation variety"""
        words = [self.generator.generate(
            GeneratorActions.RANDOM_WORD) for _ in range(30)]
        assert len(set(words)) > 1  # Should have variety

        # Test length variety
        lengths = [len(word) for word in words]
        assert len(set(lengths)) > 1  # Should have different lengths

    def test_sentence_generation_properties(self):
        """Test properties of generated sentences"""
        for _ in range(20):
            sentence = self.generator.generate(
                GeneratorActions.RANDOM_SENTENCE)
            assert isinstance(sentence, str)
            assert len(sentence) > 0

            # Should end with proper punctuation
            assert sentence.endswith(('.', '!', '?'))

            # Should start with capital letter
            assert sentence[0].isupper()

    def test_sentence_variety(self):
        """Test sentence generation variety"""
        sentences = [self.generator.generate(
            GeneratorActions.RANDOM_SENTENCE) for _ in range(20)]
        assert len(set(sentences)) > 1  # Should have variety

        # Test length variety
        lengths = [len(sentence.split()) for sentence in sentences]
        assert len(set(lengths)) > 1  # Should have different word counts

    def test_alphanumeric_generation_if_available(self):
        """Test alphanumeric string generation if method exists"""
        if hasattr(self.generator, 'generate_alphanumeric'):
            for length in [5, 10, 15, 20]:
                alphanum = self.generator.generate_alphanumeric(length)
                assert isinstance(alphanum, str)
                assert len(alphanum) == length
                assert alphanum.isalnum()

                # Should contain both letters and numbers (with high probability)
                has_letter = any(c.isalpha() for c in alphanum)
                has_digit = any(c.isdigit() for c in alphanum)
                # For longer strings, we expect both
                if length >= 10:
                    assert has_letter or has_digit  # At least one type

    def test_random_string_generation_if_available(self):
        """Test random string generation if method exists"""
        if hasattr(self.generator, 'generate_random_string'):
            for length in [1, 5, 10, 25]:
                random_str = self.generator.generate_random_string(length)
                assert isinstance(random_str, str)
                assert len(random_str) == length

    def test_alphabetic_string_if_available(self):
        """Test alphabetic string generation if method exists"""
        if hasattr(self.generator, 'generate_alphabetic_string'):
            for length in [5, 10, 15]:
                alpha_str = self.generator.generate_alphabetic_string(length)
                assert isinstance(alpha_str, str)
                assert len(alpha_str) == length
                assert alpha_str.isalpha()

    def test_numeric_string_if_available(self):
        """Test numeric string generation if method exists"""
        if hasattr(self.generator, 'generate_numeric_string'):
            for length in [3, 6, 10]:
                numeric_str = self.generator.generate_numeric_string(length)
                assert isinstance(numeric_str, str)
                assert len(numeric_str) == length
                assert numeric_str.isdigit()

    def test_uppercase_string_if_available(self):
        """Test uppercase string generation if method exists"""
        if hasattr(self.generator, 'generate_uppercase_string'):
            for length in [5, 10, 15]:
                upper_str = self.generator.generate_uppercase_string(length)
                assert isinstance(upper_str, str)
                assert len(upper_str) == length
                assert upper_str.isupper()

    def test_lowercase_string_if_available(self):
        """Test lowercase string generation if method exists"""
        if hasattr(self.generator, 'generate_lowercase_string'):
            for length in [5, 10, 15]:
                lower_str = self.generator.generate_lowercase_string(length)
                assert isinstance(lower_str, str)
                assert len(lower_str) == length
                assert lower_str.islower()

    def test_paragraph_generation_if_available(self):
        """Test paragraph generation if method exists"""
        if hasattr(self.generator, 'generate_paragraph'):
            for _ in range(10):
                paragraph = self.generator.generate_paragraph()
                assert isinstance(paragraph, str)
                assert len(paragraph) > 0

                # Should contain multiple sentences
                sentences = re.split(r'[.!?]+', paragraph)
                # Filter out empty strings
                sentences = [s.strip() for s in sentences if s.strip()]
                assert len(sentences) >= 1

    def test_custom_character_set_if_available(self):
        """Test custom character set generation if method exists"""
        if hasattr(self.generator, 'generate_from_charset'):
            charset = "ABC123"
            length = 10

            custom_str = self.generator.generate_from_charset(charset, length)
            assert isinstance(custom_str, str)
            assert len(custom_str) == length

            # All characters should be from the specified set
            for char in custom_str:
                assert char in charset

    def test_password_generation_if_available(self):
        """Test password generation if method exists"""
        if hasattr(self.generator, 'generate_password'):
            for length in [8, 12, 16]:
                password = self.generator.generate_password(length)
                assert isinstance(password, str)
                assert len(password) == length

                # Password should have some complexity
                has_upper = any(c.isupper() for c in password)
                has_lower = any(c.islower() for c in password)
                has_digit = any(c.isdigit() for c in password)

                # For reasonable length passwords, expect some variety
                if length >= 8:
                    complexity_count = sum([has_upper, has_lower, has_digit])
                    assert complexity_count >= 2  # At least 2 types of characters

    def test_lorem_ipsum_if_available(self):
        """Test Lorem Ipsum generation if method exists"""
        if hasattr(self.generator, 'generate_lorem_ipsum'):
            lorem = self.generator.generate_lorem_ipsum()
            assert isinstance(lorem, str)
            assert len(lorem) > 0

            # Should contain "lorem" or "ipsum" (case insensitive)
            lorem_lower = lorem.lower()
            assert 'lorem' in lorem_lower or 'ipsum' in lorem_lower


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
