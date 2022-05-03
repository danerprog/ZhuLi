from .manager.ComponentManager import ComponentManager
from .manager.ConfigurationManager import ConfigurationManager
from .manager.DatabaseManager import DatabaseManager
from .manager.EventListenerManager import EventListenerManager
from .manager.LoggingManager import LoggingManager

import logging


class Environment:

    class Shard:
        
        def __init__(self, component_name, component_level, parent_environment):
            self._component_name = component_name
            self._component_level = component_level
            self._parent = parent_environment
            self._logger = self._parent.getLogger(f"{self.__class__.__name__}.{component_name}[{component_level}]")
            self._component_manager = self._parent.getComponentManager()
            self._component_manager.registerComponentAtLevel(component_name, component_level)
            self._event_listener_manager = EventListenerManager(self._logger)
            self._logger.info("Environment shard created.")
            
        def configuration(self):
            return self._parent.configuration()
            
        def database(self):
            return self._parent.database()
            
        def logger(self):
            return self._parent.logger()

        def getLogger(self, logger_name = None):
            return self._parent.getLogger(logger_name)
            
        def getConfiguration(self, configuration_file_name):
            return self._parent.getConfiguration(configuration_file_name)
            
        def getSelfRegisteredEvents(self):
            return self._event_listener_manager.getAllEvents()
            
        def getBackendRegisteredEvents(self):
            return self._parent.getRegisteredEventsOnLevel(ComponentManager.LEVEL['backend'])
            
        def getInterfaceRegisteredEvents(self):
            return self._parent.getRegisteredEventsOnLevel(ComponentManager.LEVEL['interface'])
            
        def registerCallback(self, event, callback):
            self._event_listener_manager.register(event, self._component_level, callback)
            self._parent.registerCallback(event, self._component_level, callback)
  
        def fireEvent(self, event, level, *args, **kwargs):
            if level == "self":
                self._event_listener_manager.fire(event, self._component_level, *args, **kwargs)
            else:
                self._parent.fireEvent(event, level, *args, **kwargs)
                
        def fireEventAtSelf(self, event, *args, **kwargs):
            self.fireEvent(event, 'self', *args, **kwargs)
            
        def fireEventAtBackend(self, event, *args, **kwargs):
            self.fireEvent(event, ComponentManager.LEVEL['backend'], *args, **kwargs)
            
        def fireEventAtInterface(self, event, *args, **kwargs):
            self.fireEvent(event, ComponentManager.LEVEL['interface'], *args, **kwargs)
            
        def initialize(component_name, component_level):
            environment = Environment.instance()
            if environment is None:
                print(">>> No environment instance found! No shard will be created.")
            else:
                if component_name in Environment.SHARDS:
                    print(f">>> Reinitializing shard. component_name: {component_name}, component_level: {component_level}")
                Environment.SHARDS[component_name] = Environment.Shard(component_name, component_level, environment)


    INSTANCE = None
    SHARDS = {}
    
    def __init__(self, config_directory = None):
        print(f">>> Initializing environment. config_directory: {config_directory}")
        self._initializeConfigurationManager(config_directory)
        self._initializeLoggingManager()
        self._initializeEventListenerManager()
        self._initializeDatabaseManager()
        self._initializeComponentManager()

    def configuration(self):
        return self._configuration_manager
        
    def database(self):
        return self._database_manager.get()
        
    def logger(self):
        return self._logging_manager
        
    def getComponentManager(self):
        return self._component_manager

    def getLogger(self, name = None):
        return self._logging_manager.getLogger(name)
        
    def getConfiguration(self, name):
        return self.configuration().getConfiguration(name)
    
    def getRegisteredEventsOnLevel(self, level):
        return self._event_listener_manager.getEventsOnLevel(level)
        
    def registerCallback(self, event, level, callback):
        self._event_listener_manager.register(event, level, callback)
        
    def fireEvent(self, event, level, *args, **kwargs):
        self._event_listener_manager.fire(event, level, *args, **kwargs)
        
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

    def _initializeComponentManager(self):
        self._component_manager = ComponentManager(self.getLogger())
        
    def _initializeEventListenerManager(self):
        self._event_listener_manager = EventListenerManager(self.getLogger())
        
    def _initializeLoggingManager(self):
        main_configuration = self.configuration()["main"]
        self._logging_manager = LoggingManager(
            logger_configuration = main_configuration["Logger"],
            main_logger_name = main_configuration["App"]["name"])
            
    def initialize(config_directory):
        Environment.INSTANCE = Environment(config_directory)
        
    def shard(component_name):
        shard = None
        if component_name not in Environment.SHARDS:
            print(">>> No environment shard found! Initialize a shard using Environment.Shard.initialize()")
        else:
            shard = Environment.SHARDS[component_name]
        return shard
        
    def instance():
        if Environment.INSTANCE is None:
            print(">>> Environment not initialized! Call Environment.initialize() first.")
        return Environment.INSTANCE
        
    
       