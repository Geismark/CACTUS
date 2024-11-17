import os, pytest
from src.logger.logger_settings import LoggerSettings


def test_LoggerSettings_correct_log_folder():
    settings = LoggerSettings()
    expected_log_dir = "\\".join(
        os.path.dirname(os.path.abspath(__file__)).split("\\")[:-3] + ["logs"]
    )
    assert settings.LOG_FOLDER == expected_log_dir


expected_attributes = [
    "CONSOLE_LOG_ENABLED",
    "CONSOLE_LOG_LEVEL",
    "CONSOLE_MESSAGE_FORMAT",
    "CONSOLE_TIME_FORMAT",
    "FILE_LOG_ENABLED",
    "FILE_LOG_LEVEL_RANGE_MIN",
    "FILE_LOG_LEVEL_RANGE_MAX",
    "LOG_FOLDER",
    "FILE_MESSAGE_FORMAT",
    "FILE_TIME_FORMAT",
]


def test_LoggerSettings_must_be_instantiated():
    for attribute in expected_attributes:
        with pytest.raises(AttributeError):
            getattr(LoggerSettings, attribute)


def test_LoggerSettings_has_correct_number_of_attributes():
    settings = LoggerSettings()
    assert len(expected_attributes) == len(settings.__dict__)


def test_LoggerSettings_has_correct_attributes():
    settings = LoggerSettings()
    for attribute in expected_attributes:
        assert hasattr(settings, attribute)
