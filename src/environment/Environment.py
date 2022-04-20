from .ConfigurationManager import ConfigurationManager
from .DatabaseManager import DatabaseManager
from .EventListenerManager import EventListenerManager
from .LoggingManager import LoggingManager

import logging


class Environment:

    INSTANCE = None
    
    def __init__(self, config_directory = None):
        print(">>> Initializing environment. config_directory: " + config_directory)
        self._initializeConfigurationManager(config_directory)
        self._initializeLoggingManager()
        self._initializeEventListenerManager()
        self._initializeDatabaseManager()

    def configuration(self):
        return self._configuration_manager
        
    def logger(self):
        return self._logging_manager

    def getLogger(self, name = None):
        return self._logging_manager.getLogger(name)
        
    def getConfiguration(self, name):
        return self.configuration().getConfiguration(name)
        
    def registerCallback(self, event, callback):
        self._event_listener_manager.register(event, callback)
        
    def fireEvent(self, event, *args, **kwargs):
        self._event_listener_manager.fire(event, *args, **kwargs)
        
    def _initializeConfigurationManager(self, config_directory):
        self._configuration_manager = ConfigurationManager.instance(config_directory)
        self._configuration_manager.parseFile("main")
    
    def _initializeDatabaseManager(self):
        self._database_manager = DatabaseManager(
            self.configuration().getConfiguration("main").get("App", "DatabasePort"),
            self.getLogger("DatabaseManager")
        )
        
    def _initializeEventListenerManager(self):
        self._event_listener_manager = EventListenerManager.instance()
        self._event_listener_manager.setLogger(self.getLogger("EventListenerManager"))
        
    def _initializeLoggingManager(self):
        configuration = self.configuration().getConfiguration("main")
        self._logging_manager = LoggingManager(
            logs_directory = configuration.get("App", "LogFileDirectory"),
            main_logger_name = configuration.get("App", "Name"))
        self._logging_manager.initialize()
        
    def instance(config_directory = None):
        if Environment.INSTANCE is None:
            Environment.INSTANCE = Environment(config_directory)
        return Environment.INSTANCE
        
    
       