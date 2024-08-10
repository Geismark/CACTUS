import logging, os


class LoggerSettings:
    def __init__(self):
        # =============== User-Configurable Settings ===============
        self.CONSOLE_LOG_ENABLED = True
        self.CONSOLE_LOG_LEVEL = logging.DEBUG
        self.CONSOLE_MESSAGE_FORMAT = (
            f"%(asctime)s %(levelname)8s %(name)s: %(message)s"
        )
        self.CONSOLE_TIME_FORMAT = "%H:%M:%S"

        self.FILE_LOG_ENABLED = True
        self.FILE_LOG_LEVEL_RANGE_MIN = logging.DETAIL
        self.FILE_LOG_LEVEL_RANGE_MAX = logging.CRITICAL
        self.LOG_FOLDER = "\\".join(
            os.path.dirname(os.path.abspath(__file__)).split("\\")[:-2] + ["logs"]
        )
        self.FILE_MESSAGE_FORMAT = (
            "%(asctime)s - %(name)11s - %(levelname)8s - %(message)s"
        )
        self.FILE_TIME_FORMAT = "%Y/%m/%d %H:%M:%S"
        # =============== User-Configurable Settings ===============
