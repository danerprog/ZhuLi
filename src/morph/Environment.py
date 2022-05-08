from .manager.ComponentManager import ComponentManager
from .manager.ConfigurationManager import ConfigurationManager
from .manager.LoggingManager import LoggingManager

import logging


class Environment:

    class Shard:
        
        def __init__(self, **parameters):
            self._component_id = parameters['component_id']
            self._component_name = parameters['component_name']
            self._component_level = parameters['component_level']
            self._parent = parameters['parent_environment']
            self._logger = self._parent.getLogger(f"{self.__class__.__name__}[{self._component_name}]")
            self._component_manager = self._parent.getComponentManager()
            self.setDatabase(None)
            self._runtime_configuration = {
                'command_set' : set()
            }
            self._app_name = self._parent.configuration()["main"]["App"]["name"]
            self._logger.info("Environment shard created.")

        def database(self):
            return self._database
            
        def logger(self):
            return self._parent.logger()
            
        def register(self, component):
            self._component_manager.register(component)
            
        def setDatabase(self, database):
            self._database = database
            
        def getAppName(self):
            return self._app_name

        def getLogger(self, logger_name = None):
            return self._parent.getLogger(logger_name)
            
        def getRuntimeConfiguration(self):
            return self._runtime_configuration
            
        def getStartupConfiguration(self):
            return self._parent.getConfiguration("main")[self._component_name]
            
        def getComponentInfo(self):
            return {
                'component_id' : self._component_id,
                'component_name' : self._component_name,
                'component_level' : self._component_level
            }

        def sendMessage(self, message):
            message['sender'] = self.getComponentInfo()
            self._component_manager.sendMessage(message)

        def fireEvent(self, event):
            event['origin'] = self.getComponentInfo()
            self._parent.fireEvent(event)

        def initialize(component_id, component_name, component_level):
            environment = Environment.instance()
            if environment is None:
                print(">>> No environment instance found! No shard will be created.")
            else:
                if component_name in Environment.SHARDS:
                    print(f">>> Reinitializing shard. component_id: {component_id}, component_name: {component_name}, component_level: {component_level}")
                Environment.SHARDS[component_name] = Environment.Shard(**{
                    'component_id' : component_id,
                    'component_name' : component_name,
                    'component_level' : component_level,
                    'parent_environment' : environment
                })


    INSTANCE = None
    SHARDS = {}
    
    def __init__(self, config_directory = None):
        print(f">>> Initializing environment. config_directory: {config_directory}")
        self._database = None
        self._initializeConfigurationManager(config_directory)
        self._initializeLoggingManager()
        self._initializeComponentManager()

    def configuration(self):
        return self._configuration_manager
        
    def database(self):
        return self._database
        
    def logger(self):
        return self._logging_manager

    def getComponentManager(self):
        return self._component_manager

    def getLogger(self, name = None):
        return self._logging_manager.getLogger(name)
        
    def getConfiguration(self, name):
        return self.configuration().getConfiguration(name)
        
    def fireEvent(self, event):
        self._component_manager.fireEvent(event)

    def _initializeConfigurationManager(self, config_directory):
        self._configuration_manager = ConfigurationManager.instance(config_directory)
        self._configuration_manager.parseFile("main")
    
    def _initializeComponentManager(self):
        self._component_manager = ComponentManager(self.getLogger())

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
        
    
       