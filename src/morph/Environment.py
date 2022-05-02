from .ConfigurationManager import ConfigurationManager
from .DatabaseManager import DatabaseManager
from .EventListenerManager import EventListenerManager
from .LoggingManager import LoggingManager

import logging


class Environment:

    class Shard:
        
        def __init__(self, name, parent_environment):
            self._parent = parent_environment
            self._logger = self._parent.getLogger(f"{self.__class__.__name__}.{name}")
            self._event_listener_manager = EventListenerManager(self._logger)
            self._logger.info("Environment shard created.")
            
        def configuration(self):
            return self._parent.configuration()
            
        def database(self):
            return self._parent.database()
            
        def logger(self):
            return self._parent.logger()

        def getLogger(self, name = None):
            return self._parent.getLogger(name)
            
        def getConfiguration(self, name):
            return self._parent.getConfiguration(name)
            
        def registerCallback(self, event, callback):
            self._event_listener_manager.register(event, callback)
            
        def fireEvent(self, event, *args, **kwargs):
            self._event_listener_manager.fire(event, *args, **kwargs)
            
        def fireAndPropagateEvent(self, event, *args, **kwargs):
            self.fireEvent(event, *args, **kwargs)
            self._parent.fireEvent(event, *args, **kwargs)


    INSTANCE = None
    SHARDS = {}
    
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
        self._event_listener_manager = EventListenerManager(self.getLogger())
        
    def _initializeLoggingManager(self):
        main_configuration = self.configuration()["main"]
        self._logging_manager = LoggingManager(
            logger_configuration = main_configuration["Logger"],
            main_logger_name = main_configuration["App"]["name"])
            
    def initialize(config_directory):
        Environment.INSTANCE = Environment(config_directory)
        
    def shard(name):
        environment = Environment.instance()
        if name not in Environment.SHARDS and environment is not None:
            Environment.SHARDS[name] = Shard(name, environment)
        elif environment is None:
            print(">>> No environment instance found! No shard will be created.")
        return Environment.SHARDS[name]
        
    def instance():
        if Environment.INSTANCE is None:
            print(">>> Environment not initialized! Call Environment.initialize() first.")
        return Environment.INSTANCE
        
    
       