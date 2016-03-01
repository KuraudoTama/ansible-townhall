from logging.handlers import RotatingFileHandler
import logging
import common.settings as settings

LOG_FILE = settings.get_log_file_path()
LOG_FILE_SIZE = 10 * 1024 * 1024
LOG_FILE_COUNT = 3
LOG_FORMAT = "%(asctime)s::%(name)s::%(filename)s::%(funcName)s::[line:%(lineno)d]-%(message)s"
LOGGER_NAME = "ansible-townhall"

file_handler = RotatingFileHandler(LOG_FILE, mode="a", maxBytes=LOG_FILE_SIZE, backupCount=LOG_FILE_COUNT)
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(LOG_FORMAT)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
