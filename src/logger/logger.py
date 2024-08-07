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
    import src.logger.__init__ as log_init
except ModuleNotFoundError:
    from logger_settings import LoggerSettings
    import __init__ as log_init


def get_logger(name, settings_class=None, custom_file_name_start=None):
    if not settings_class:
        settings = LoggerSettings()
    else:
        settings = settings_class

    # this method is messy, but works for now until I decide for certain what method to use here
    if custom_file_name_start is None:
        custom_file_name_start = ""
        if log_init.server_custom_file_start:
            custom_file_name_start = "server_"

    logger = logging.getLogger(name)
    # logger.setLevel(logging.TRACE)  # Capture everything internally @ value 1 (lowest)
    logger.setLevel(
        min(settings.FILE_LOG_LEVEL_RANGE_MIN, settings.CONSOLE_LOG_LEVEL)
    )  # Capture the minimum level set to the file/console handler

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
        file_name = f"{custom_file_name_start}log-{current_time}-[{settings.FILE_LOG_LEVEL_RANGE_MIN}-{settings.FILE_LOG_LEVEL_RANGE_MAX}].log"
        file_path = os.path.join(settings.LOG_FOLDER, file_name)

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
    from logger_settings import LoggerSettings

    settings = LoggerSettings()
    settings.FILE_LOG_LEVEL_RANGE_MIN = logging.TRACE
    settings.FILE_LOG_LEVEL_RANGE_MAX = logging.CRITICAL
    settings.CONSOLE_LOG_LEVEL = logging.TRACE
    logger = get_logger("CustomLoggerMain", settings_class=settings)
    test_logger()
