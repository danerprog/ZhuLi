import colorlog
from datetime import datetime
import logging
import sys


class LoggingManager:

    def __init__(
        self,
        logger_configuration = None,
        main_logger_name = None
    ):
        print(f">>> Inititalizing LoggingManager. logger_configuration: {str(logger_configuration)}")
        self._initializeConfiguration(logger_configuration)
        self._main_logger_name = main_logger_name
        self._main_logger = None
        self._initialize()
        
    def getLogger(self, name = None):
        logger_to_return = self._main_logger
        if name is not None:
            logger_to_return = logger_to_return.getChild(name)
        return logger_to_return
        
    def hideLogger(self, name):
        self._main_logger.info(f"hideLogger called. name: {name}")
        logging.getLogger(name).setLevel(logging.ERROR)
        
    def _initialize(self):
        print(">>> initializing loggers...")
        self._initializeRootLogger()
        self._initializeMainLogger()
        self._main_logger.info("Loggers initialized.")
        
    def _initializeConfiguration(self, logger_configuration):
        if logger_configuration is None:
            logger_configuration = {}
        self._configuration = {
            "directory" : "logs/" if "directory" not in logger_configuration else logger_configuration["directory"],
            "file_level" : self._getLoggingLevel(logger_configuration, "filelevel"),
            "console_level" : self._getLoggingLevel(logger_configuration, "consolelevel"),
        }
        print(f">>> _initializeConfiguration called. self._configuration: {str(self._configuration)}")
        
    def _getLoggingLevel(self, logger_configuration, key):
        level = logging.ERROR
        if key in logger_configuration:
            level_in_configuration = logger_configuration[key]
            if level_in_configuration == "debug":
                level = logging.DEBUG
            elif level_in_configuration == "info" :
                level = logging.INFO
            elif level_in_configuration == "warning" :
                level = logging.WARNING
            elif level_in_configuration == "critical" :
                level = logging.CRITICAL
        return level

    def _initializeRootLogger(self):
        print(">>> initializing root logger...")
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
    def _initializeMainLogger(self):
        print(">>> initializing main loggers...")
        self._main_logger = logging.getLogger(self._main_logger_name)
        self._initializeConsoleLogger(self._main_logger)
        self._initializeFileLogger(self._main_logger)

    def _initializeConsoleLogger(self, logger):
        print(">>> initializing console logger...")
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
        handler.setLevel(self._configuration["console_level"])
        logger.addHandler(handler)
        
    def _initializeFileLogger(self, logger):
        print(">>> initializing file logger")
        filename = self._configuration["directory"] + datetime.now().strftime("%Y%m%d%H%M%S") + ".log"
        handler = logging.FileHandler(filename, mode = "a")
        handler.setFormatter(
            logging.Formatter(
                fmt = "[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
                datefmt = '%D %H:%M:%S')
        )
        handler.setLevel(self._configuration["file_level"])
        logger.addHandler(handler)


