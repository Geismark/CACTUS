# ============ DO NOT MOVE ============
import logging

TRACE = 1
logging.addLevelName(TRACE, "TRACE")
logging.TRACE = TRACE

DETAIL = 5
logging.addLevelName(DETAIL, "DETAIL")
logging.DETAIL = DETAIL
# ============ DO NOT MOVE ============

import os
from datetime import datetime

try:
    from src.logger.logger_settings import LoggerSettings
    import src.logger.__init__ as log_init
except ModuleNotFoundError:
    from logger_settings import LoggerSettings
    import __init__ as log_init


def get_logger(name, settings=None):
    if not settings:
        settings = LoggerSettings()

    logger = logging.getLogger(name)
    min_level_in_settings = min(
        settings.FILE_LOG_LEVEL_RANGE_MIN, settings.CONSOLE_LOG_LEVEL
    )
    logger.setLevel(min_level_in_settings)

    if settings.CONSOLE_LOG_ENABLED:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(settings.CONSOLE_LOG_LEVEL)
        console_handler.setFormatter(
            logging.Formatter(
                settings.CONSOLE_MESSAGE_FORMAT, settings.CONSOLE_TIME_FORMAT
            )
        )
        logger.addHandler(console_handler)

    if settings.FILE_LOG_ENABLED:
        os.makedirs(settings.LOG_FOLDER, exist_ok=True)
        file_path = get_logger_file_path(settings)

        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(settings.FILE_LOG_LEVEL_RANGE_MIN)
        file_handler.addFilter(
            lambda record: record.levelno <= settings.FILE_LOG_LEVEL_RANGE_MAX
        )
        file_handler.setFormatter(
            logging.Formatter(settings.FILE_MESSAGE_FORMAT, settings.FILE_TIME_FORMAT)
        )
        logger.addHandler(file_handler)

    # Set up custom level functions
    if hasattr(logging, "TRACE") and hasattr(logging, "DETAIL"):
        logger.trace = lambda msg, *args, **kwargs: logger.log(
            TRACE, msg, *args, **kwargs
        )
        logger.detail = lambda msg, *args, **kwargs: logger.log(
            DETAIL, msg, *args, **kwargs
        )
    else:
        raise AttributeError(
            f"logging Trace/Detail not found: {logging.TRACE=} {logging.DETAIL=}"
        )

    return logger


def get_logger_file_path(settings):
    if not (file_name := log_init.custom_file_name):
        file_name_current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{log_init.custom_file_name_start}log-{file_name_current_time}-[{settings.FILE_LOG_LEVEL_RANGE_MIN}-{settings.FILE_LOG_LEVEL_RANGE_MAX}].log"
    file_path = os.path.join(settings.LOG_FOLDER, file_name)
    return file_path


def test_logger(log):
    log.info("Testing logger levels")
    log.trace(f"TRACE: {logging.TRACE}")
    log.detail(f"DETAIL: {logging.DETAIL}")
    log.debug(f"DEBUG: {logging.DEBUG}")
    log.info(f"INFO: {logging.INFO}")
    log.warning(f"WARNING: {logging.WARNING}")
    log.error(f"ERROR: {logging.ERROR}")
    log.critical(f"CRITICAL: {logging.CRITICAL}")


# logger manual check
if __name__ == "__main__":
    from logger_settings import LoggerSettings

    log_init.custom_file_name_start = "LoggerTest_"
    settings = LoggerSettings()
    settings.FILE_LOG_LEVEL_RANGE_MIN = logging.TRACE
    settings.FILE_LOG_LEVEL_RANGE_MAX = logging.CRITICAL
    settings.CONSOLE_LOG_LEVEL = logging.TRACE
    logger = get_logger("CustomLoggerMain", settings=settings)
    test_logger(logger)
