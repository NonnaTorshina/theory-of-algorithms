""" тесты для приложения отслеживания сна """

import pytest
import os
from datetime import date, timedelta
from model import SleepRecord, SleepTrackerModel
from custom_exceptions import InvalidDurationError, InvalidDateError, InvalidQualityError
from database import DatabaseManager

class TestSleepRecord:

    def test_valid_record_creation(self):
        record = SleepRecord(date.today(), 7.5, 8, "Хороший сон")
        assert record.duration_hours == 7.5
        assert record.quality == 8
        assert record.notes == "Хороший сон"

    def test_valid_record_creation_no_notes(self):
        record = SleepRecord(date.today(), 7.5, 8)
        assert record.notes == ""

    def test_invalid_duration_negative(self):
        with pytest.raises(InvalidDurationError):
            SleepRecord(date.today(), -1, 5)

    def test_invalid_duration_zero(self):
        with pytest.raises(InvalidDurationError):
            SleepRecord(date.today(), 0, 5)

    def test_invalid_duration_too_large(self):
        with pytest.raises(InvalidDurationError):
            SleepRecord(date.today(), 25, 5)

    def test_invalid_date_future(self):
        future_date = date.today() + timedelta(days=1)
        with pytest.raises(InvalidDateError):
            SleepRecord(future_date, 7.5, 5)

    def test_invalid_quality_too_low(self):
        with pytest.raises(InvalidQualityError):
            SleepRecord(date.today(), 7.5, 0)

    def test_invalid_quality_too_high(self):
        with pytest.raises(InvalidQualityError):
            SleepRecord(date.today(), 7.5, 11)

    def test_boundary_quality_values(self):
        record1 = SleepRecord(date.today(), 7.5, 1)
        record2 = SleepRecord(date.today(), 7.5, 10)
        assert record1.quality == 1
        assert record2.quality == 10

    def test_boundary_duration_values(self):

        record1 = SleepRecord(date.today(), 0.1, 5)
        record2 = SleepRecord(date.today(), 24.0, 5)
        assert record1.duration_hours == 0.1
        assert record2.duration_hours == 24.0

    def test_to_list_method(self):
        record = SleepRecord(date(2024, 1, 15), 7.5, 8, "Test")
        result = record.to_list()
        expected = ["2024-01-15", "7.5", "8", "Test"]
        assert result == expected

    def test_to_list_method_no_notes(self):
        """Тест метода to_list() без заметок."""
        record = SleepRecord(date(2024, 1, 15), 7.5, 8)
        result = record.to_list()
        expected = ["2024-01-15", "7.5", "8", ""]
        assert result == expected

    def test_str_representation(self):
        """Тест строкового представления."""
        record = SleepRecord(date(2024, 1, 15), 7.5, 8, "Test")
        result = str(record)
        expected = "SleepRecord(2024-01-15, 7.5ч, качество сна: 8)"
        assert "2024-01-15" in result
        assert "7.5ч" in result
        assert "качество сна: 8" in result
