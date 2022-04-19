import colorlog
from datetime import datetime
import logging
import sys


class LoggingManager:

    def __init__(
        self,
        logs_directory = "logs/",
        main_logger_name = None
    ):
        self._directory = logs_directory
        self._main_logger_name = main_logger_name
        self._main_logger = None
        
    def initialize(self):
        self._initializeRootLogger()
        self._initializeMainLogger()
        
    def getLogger(self, name = None):
        logger_to_return = self._main_logger
        if name is not None:
            logger_to_return = logger_to_return.getChild(name)
        return logger_to_return
        
    def hideLogger(self, name):
        logging.getLogger(name).setLevel(logging.ERROR)

    def _initializeRootLogger(self):
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
    def _initializeMainLogger(self):
        self._main_logger = logging.getLogger(self._main_logger_name)
        self._initializeConsoleLogger(self._main_logger)
        self._initializeFileLogger(self._main_logger)

    def _initializeConsoleLogger(self, logger):
        handler = logging.StreamHandler(stream = sys.stdout)
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s[%(levelname)s][%(name)s] %(message)s",
            reset = True,
            log_colors = {
                "DEBUG" : "cyan",
                "INFO" : "white",
                "WARNING" : "yellow",
                "ERROR" : "bold_red",
                "CRITICAL" : "red"
            }
        )
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        
    def _initializeFileLogger(self, logger):
        filename = self._directory + datetime.now().strftime("%Y%m%d%H%M%S") + ".log"
        handler = logging.FileHandler(filename, mode = "a")
        handler.setFormatter(
            logging.Formatter(
                fmt = "[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
                datefmt = '%D %H:%M:%S')
        )
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)


