import logging, os
class LoggerSettings:
	# choice to put everything under init
	# ensures obj if something is needed to be added in the future
	def __init__(self):
		# --- User-Configurable Settings ---
		self.CONSOLE_LOG_ENABLED = True
		self.CONSOLE_LOG_LEVEL = logging.DETAIL
		self.CONSOLE_MESSAGE_FORMAT = (
			f"%(asctime)s [{f'%(levelname)s'.center(12, "*")}] %(name)s: %(message)s"
		)
		# self.CONSOLE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
		self.CONSOLE_TIME_FORMAT = "%H:%M:%S"

		self.FILE_LOG_ENABLED = True
		self.FILE_LOG_LEVEL_RANGE = (logging.DETAIL, logging.CRITICAL)
		# must be updated if file no longer found in /project/src/Logger/logger.py
		self.LOG_FOLDER = "\\".join(os.path.dirname(os.path.abspath(__file__)).split("\\")[:-2] + ["logs"])
		self.FILE_MESSAGE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
		self.FILE_TIME_FORMAT = "%Y-%m-%d_%H:%M:%S"
