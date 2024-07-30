import logging

# Custom Logging Levels
# --- DO NOT MOVE ---
TRACE = 1
logging.addLevelName(TRACE, "TRACE")
logging.TRACE = TRACE

DETAIL = 5
logging.addLevelName(DETAIL, "DETAIL")
logging.DETAIL = DETAIL
# --- DO NOT MOVE ---

import os
from datetime import datetime

try:
    from src.logger.logger_settings import LoggerSettings
except ModuleNotFoundError:
    from logger_settings import LoggerSettings


def get_logger(name, settings_class=None, custom_file_name_start=None):
    if not settings_class:
        settings = LoggerSettings()
    else:
        settings = settings_class
    if custom_file_name_start is None:
        custom_file_name_start = ""

    logger = logging.getLogger(name)
    logger.setLevel(logging.TRACE)  # Capture everything internally @ value 1 (lowest)

    # Console Handler
    if settings.CONSOLE_LOG_ENABLED:
        # print("CONSOLE ENABLED")
        console_handler = logging.StreamHandler()
        console_handler.setLevel(settings.CONSOLE_LOG_LEVEL)
        console_handler.setFormatter(
            logging.Formatter(
                settings.CONSOLE_MESSAGE_FORMAT, settings.CONSOLE_TIME_FORMAT
            )
        )
        logger.addHandler(console_handler)

    # File Handler
    if settings.FILE_LOG_ENABLED:
        os.makedirs(settings.LOG_FOLDER, exist_ok=True)
        # Set log file name (time format NOT what is printed to file)
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{custom_file_name_start}log-{current_time}-[{settings.FILE_LOG_LEVEL_RANGE[0]}-{settings.FILE_LOG_LEVEL_RANGE[1]}].txt"
        file_path = os.path.join(settings.LOG_FOLDER, file_name)

        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(settings.FILE_LOG_LEVEL_RANGE[0])
        file_handler.addFilter(
            lambda record: record.levelno <= settings.FILE_LOG_LEVEL_RANGE[1]
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


def test_logger():
    logger.info("Testing logger levels:\n")
    logger.trace(f"TRACE: {logging.TRACE}")
    logger.detail(f"DETAIL: {logging.DETAIL}")
    logger.debug(f"DEBUG: {logging.DEBUG}")
    logger.info(f"INFO: {logging.INFO}")
    logger.warning(f"WARNING: {logging.WARNING}")
    logger.error(f"ERROR: {logging.ERROR}")
    logger.critical(f"CRITICAL: {logging.CRITICAL}")


# logger manual check
if __name__ == "__main__":
    logger = get_logger("CustomLoggerMain")
    test_logger()
