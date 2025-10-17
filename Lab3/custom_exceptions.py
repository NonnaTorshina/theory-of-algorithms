"""Модуль пользовательских исключений для трекера сна"""

class SleepTrackerError(Exception):
    pass

# Вызывается, когда продолжительность сна неккоректна (<= 0 или большая)
class InvalidDurationError(SleepTrackerError):
    pass

# Вызывается, когда дата сна некорректна (из будущего)
class InvalidDateError(SleepTrackerError):
    pass

# Вызывается, когда оценка сна качества не в диапазоне 1-10
class InvalidQualityError(SleepTrackerError):
    pass