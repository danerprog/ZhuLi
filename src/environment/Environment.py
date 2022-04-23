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
        
    def database(self):
        return self._database_manager.get()
        
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
        main_configuration = self.configuration()["main"]
        database_configuration = main_configuration["Database"]
        database_configuration["name"] = main_configuration["App"]["name"]
        self._database_manager = DatabaseManager(
            self.getLogger("DatabaseManager"),
            **database_configuration
        )
        
    def _initializeEventListenerManager(self):
        self._event_listener_manager = EventListenerManager.instance()
        self._event_listener_manager.setLogger(self.getLogger("EventListenerManager"))
        
    def _initializeLoggingManager(self):
        app_configuration = self.configuration()["main"]["App"]
        self._logging_manager = LoggingManager(
            logs_directory = app_configuration["logfiledirectory"],
            main_logger_name = app_configuration["name"])
        self._logging_manager.initialize()
        
    def instance(config_directory = None):
        if Environment.INSTANCE is None:
            Environment.INSTANCE = Environment(config_directory)
        return Environment.INSTANCE
        
    
       