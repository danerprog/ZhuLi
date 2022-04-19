from .ConfigurationManager import ConfigurationManager
from .EventListenerManager import EventListenerManager
from .LoggingManager import LoggingManager

import logging


class Environment:

    INSTANCE = None
    
    def __init__(self):
        self._initializeConfigurationManager()
        self._initializeLoggingManager()
        self._initializeEventListenerManager()

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
        
    def _initializeConfigurationManager(self):
        self._configuration_manager = ConfigurationManager.instance()
        self._configuration_manager.parseFile("main")
        
    def _initializeEventListenerManager(self):
        self._event_listener_manager = EventListenerManager.instance()
        self._event_listener_manager.setLogger(self.getLogger("EventListenerManager"))
        
    def _initializeLoggingManager(self):
        app_name = self.configuration().getConfiguration("main").get(
            "App", "Name"
        )
        self._logging_manager = LoggingManager(main_logger_name = app_name)
        self._logging_manager.initialize()
        
    def instance():
        if Environment.INSTANCE is None:
            Environment.INSTANCE = Environment()
        return Environment.INSTANCE
        
    
       