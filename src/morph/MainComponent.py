from .Environment import Environment
from .messages.CommandMessage import CommandMessage
from .messages.EventMessage import ComponentsLoadedEvent, DatabaseStatusEvent
from .processors.MessageProcessor import MessageProcessor



class MainComponent(MessageProcessor):

    NEXT_COMPONENT_ID = 1

    def __init__(self):
        self._loaded_components = {}
        self._initializeId()
        self._initializeComponentMetadata()
        self._initializeEnvironment()
        self._environment.register(self)
        self._logger.info(f"Main component {self._main_component_name} initialized.")
        
    def __eq__(self, other):
        is_equal = False
        if isinstance(other, MainComponent):
            is_equal = self._isTheSameComponentAs(other)
        elif isinstance(other, dict):
            is_equal = self._isDescribedByDictionary(other)
        return is_equal
 
    async def processMessage(self, message):
        self._logger.info(f"Message received. message: {message}")
        message_to_process = await super().processMessage(message)
        if message_to_process is not None:
            if isinstance(message, CommandMessage) and message.getCommand() == 'set_database':
                self._onSetDatabase(message.getParameter('database'))
            elif isinstance(message, DatabaseStatusEvent) and message.getStatus() == "online":
                self._sendDatabaseRequest(message['sender'])
            elif isinstance(message, DatabaseStatusEvent) and message.getStatus() == "offline":
                self._onSetDatabase(None)
            elif isinstance(message, ComponentsLoadedEvent):
                self._onComponentsLoaded(message.getComponentSet())
        return message_to_process
        
    def _initializeId(self):
        self._main_component_id = MainComponent.NEXT_COMPONENT_ID
        MainComponent.NEXT_COMPONENT_ID += 1
 
    def _initializeComponentMetadata(self):
        tokens = self.__module__.split('.', 3)
        self._component_level = tokens[0]
        self._component_module_name = tokens[1]
        self._main_component_name = tokens[2]
        Environment.instance().getLogger().info(
            f"Component module initialized. component_level: {self._component_level}, " +
            f"component_module_name: {self._component_module_name}, " + 
            f"main_component_name: {self._main_component_name}")
            
    def _initializeEnvironment(self):
        Environment.Shard.initialize(
            self._main_component_id, 
            self._component_module_name, 
            self._component_level)
        self._environment = Environment.shard(self._component_module_name)
        self._logger = self._environment.getLogger(f"{self._main_component_name}[{self._main_component_id}]")
       
    def _isTheSameComponentAs(self, other):
        self._logger.debug(f"_isTheSameComponentAs called. other: {other}")
        return self._main_component_id == other._main_component_id
        
    def _isDescribedByDictionary(self, dictionary):
        results = []
        if 'component_id' in dictionary:
            results.append(self._main_component_id == dictionary['component_id'])
        if 'component_name' in dictionary:
            results.append(self._component_module_name == dictionary['component_name'])
        if 'component_level' in dictionary:
            results.append(self._component_level == dictionary['component_level'])
        self._logger.debug(f"_isDescribedByDictionary called. results: {results}")
        return len(results) > 0 and False not in results
        
    def _sendDatabaseRequest(self, sender):
        message = CommandMessage()
        message['target'] = sender
        message.setCommand("request_database")
        self._environment.sendMessage(message)
        
    def _onSetDatabase(self, new_database):
        self._environment.setDatabase(new_database)
        
    def _onComponentsLoaded(self, loaded_components):
        pass
         