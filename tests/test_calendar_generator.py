#!/usr/bin/env python3
"""
Detailed unit tests for the CalendarGenerator class.
Tests date, time, and datetime generation with various formats.
"""

import pytest
import re
from datetime import datetime, date, time
from mockachu.generators.calendar_generator import CalendarGenerator
from mockachu.generators.generator import GeneratorActions


class TestCalendarGeneratorDetailed:
    """Detailed test cases for CalendarGenerator"""

    def setup_method(self):
        self.generator = CalendarGenerator()

    def test_date_generation_types(self):
        """Test different types of date generation"""
        for _ in range(20):
            generated_date = self.generator.generate(
                GeneratorActions.RANDOM_DATE)

            # Should be either string or date object
            assert isinstance(generated_date, (str, date))

            if isinstance(generated_date, str):
                # Test common date formats
                date_patterns = [
                    r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                    r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
                    r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
                    r'\d{1,2}/\d{1,2}/\d{4}',  # M/D/YYYY
                ]

                assert any(re.match(pattern, generated_date)
                           for pattern in date_patterns)

            elif isinstance(generated_date, date):
                # Date object validation
                assert 1900 <= generated_date.year <= 2100
                assert 1 <= generated_date.month <= 12
                assert 1 <= generated_date.day <= 31

    def test_time_generation_formats(self):
        """Test time generation formats"""
        for _ in range(30):
            time_str = self.generator.generate(GeneratorActions.RANDOM_TIME)
            assert isinstance(time_str, str)

            # Test common time formats
            time_patterns = [
                r'\d{1,2}:\d{2}',          # H:MM or HH:MM
                r'\d{1,2}:\d{2}:\d{2}',    # H:MM:SS or HH:MM:SS
                r'\d{1,2}:\d{2} [AP]M',    # H:MM AM/PM
                r'\d{1,2}:\d{2}:\d{2} [AP]M',  # H:MM:SS AM/PM
            ]

            assert any(re.match(pattern, time_str)
                       for pattern in time_patterns)

    def test_datetime_generation(self):
        """Test datetime generation"""
        for _ in range(20):
            dt = self.generator.generate(GeneratorActions.RANDOM_DATE_TIME)

            assert isinstance(dt, (str, datetime))

            if isinstance(dt, datetime):
                assert 1900 <= dt.year <= 2100
                assert 1 <= dt.month <= 12
                assert 1 <= dt.day <= 31
                assert 0 <= dt.hour <= 23
                assert 0 <= dt.minute <= 59
                assert 0 <= dt.second <= 59

    def test_timestamp_generation(self):
        """Test unix timestamp generation"""
        for _ in range(30):
            timestamp = self.generator.generate(
                GeneratorActions.RANDOM_UNIX_TIMESTAMP)

            # Should be numeric
            assert isinstance(timestamp, (int, float))
            assert timestamp > 0
            assert timestamp < 2147483647  # Unix timestamp max for 32-bit

    def test_date_with_format(self):
        """Test date generation with custom format"""
        custom_format = "%d/%m/%Y"
        date_str = self.generator.generate(
            GeneratorActions.RANDOM_DATE, None, None, custom_format)

        # Should match the custom format pattern
        assert isinstance(date_str, str)
        import re
        assert re.match(r'\d{2}/\d{2}/\d{4}', date_str)

    def test_time_with_format(self):
        """Test time generation with custom format"""
        custom_format = "%I:%M %p"  # 12-hour format with AM/PM
        time_str = self.generator.generate(
            GeneratorActions.RANDOM_TIME, None, None, custom_format)

        assert isinstance(time_str, str)
        import re
        assert re.match(r'\d{2}:\d{2} (AM|PM)', time_str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
