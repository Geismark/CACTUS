import unittest, pytest
from unittest.mock import patch
import logging
import os

from src.logger.logger import get_logger
from src.logger.logger_settings import LoggerSettings


class Test:
    # ========================= Setup, Teardown, and Utilities =========================

    def setup_method(self, test_method):
        self.settings = LoggerSettings()
        self.settings.CONSOLE_LOG_ENABLED = True
        self.settings.CONSOLE_LOG_LEVEL = 1
        self.settings.FILE_LOG_ENABLED = True
        self.settings.FILE_LOG_LEVEL_RANGE_MIN = 1
        self.settings.FILE_LOG_LEVEL_RANGE_MAX = 50
        self.settings.FILE_NAME = "test.log"
        self.temp_log_file = os.path.join(
            self.settings.LOG_FOLDER, self.settings.FILE_NAME
        )

    def teardown_method(self, test_method):
        self.close_logger(self.log)
        if os.path.exists(self.temp_log_file):
            os.remove(self.temp_log_file)
        self.settings = None

    def setup_logger(self, console_enabled, file_enabled):
        self.settings.CONSOLE_LOG_ENABLED = console_enabled
        self.settings.FILE_LOG_ENABLED = file_enabled
        self.log = get_logger(__name__, self.settings)

    # ========================= Setup, Teardown, and Utilities =========================

    # ========================= Testing levels in file & console =========================

    def test_custom_log_levels_exist(self):
        self.setup_logger(console_enabled=True, file_enabled=False)
        assert logging.TRACE == 1
        assert logging.DETAIL == 5
        assert logging.DEBUG == 10
        assert logging.INFO == 20
        assert logging.WARNING == 30
        assert logging.ERROR == 40
        assert logging.CRITICAL == 50
        self.log.trace("trace")
        self.log.detail("detail")

    # @pytest.mark.usefixtures("caplog")
    # def test_all_console_logging_levels(self, caplog):
    #     self.setup_logger(console_enabled=True, file_enabled=False)
    #     self.func_test_all_console_logging_levels(caplog)

    # @pytest.mark.usefixtures("caplog")
    # def test_all_file_logging_levels(self, caplog):
    #     self.setup_logger(console_enabled=False, file_enabled=True)
    #     self.func_test_all_console_logging_levels(caplog)

    # @pytest.mark.usefixtures("caplog")
    # def test_all_logging_levels_file_and_console(self, caplog):
    #     self.setup_logger(console_enabled=True, file_enabled=True)
    #     self.func_test_all_console_logging_levels(caplog)

    # not called directly, used by 3 tests above - DRY
    def func_test_all_console_logging_levels(self, caplog):
        self.log.trace("trace")
        self.log.detail("detail")
        self.log.debug("debug")
        self.log.info("info")
        self.log.warning("warning")
        self.log.error("error")
        self.log.critical("critical")
        name_level_message_tuples = caplog.record_tuples
        assert len(name_level_message_tuples) == 7
        assert name_level_message_tuples[0] == (__name__, 1, "trace")
        assert name_level_message_tuples[1] == (__name__, 5, "detail")
        assert name_level_message_tuples[2] == (__name__, 10, "debug")
        assert name_level_message_tuples[3] == (__name__, 20, "info")
        assert name_level_message_tuples[4] == (__name__, 30, "warning")
        assert name_level_message_tuples[5] == (__name__, 40, "error")
        assert name_level_message_tuples[6] == (__name__, 50, "critical")

    # ========================= Testing levels in file & console =========================

    # test get default settings class if none provided
    # test custom file name start
    # logger set level (completely ignores calls if below level of both console and file)
    # test set levels (console, and file range)
    # enable and disable console and file logging
    # test FILE_NAME
    # console and file message format

    @staticmethod
    def close_logger(logger):
        for handler in logger.handlers:
            logger.removeHandler(handler)
            handler.close()
        logging.shutdown()


if __name__ == "__main__":
    unittest.main()
