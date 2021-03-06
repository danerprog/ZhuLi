from .DatabaseManager import DatabaseManager
from morph.MainComponent import MainComponent
from morph.messages.CommandMessage import CommandMessage
from morph.messages.EventMessage import ComponentsLoadedEvent, DatabaseStatusEvent

import asyncio


class MorphSystem(MainComponent):
    
    def __init__(self):
        super().__init__()
        self._loaded_components = {
            'backend' : [],
            'interface' : []
        }
        asyncio.create_task(self._loadComponents())
        
    async def _loadComponents(self):
        self._loadBatchFileManager()
        self._loadUrlArchiver()
        self._loadDiscordInterface()
        self._fireComponentsLoadedEvent()
        self._loadDatabase()
        
    async def processMessage(self, message):
        message_to_process = await super().processMessage(message)
        if message_to_process is not None and isinstance(message_to_process, CommandMessage):
            parameters = message_to_process['parameters']
            if parameters['command'] == 'request_database':
                self._sendDatabase(message_to_process['sender'])

    def _loadBatchFileManager(self):
        import backend.batchfilemanager
        self._loaded_components['backend'].append('batchfilemanager')
        
    def _loadUrlArchiver(self):
        import backend.urlarchiver
        self._loaded_components['backend'].append('urlarchiver')

    def _loadDiscordInterface(self):
        import interface.discordinterface
        self._loaded_components['interface'].append('discordinterface')
    
    def _fireComponentsLoadedEvent(self):
        event = ComponentsLoadedEvent()
        event.addComponents(self._loaded_components)
        self._environment.fireEvent(event)
        
    def _loadDatabase(self):
        configuration = self._environment.getStartupConfiguration()
        database_configuration = {
            'program' : configuration['database'],
            'port' : configuration['port'],
            'name' : self._environment.getAppName()
        }
        self._database_manager = DatabaseManager(
            self._logger,
            **database_configuration
        )
        self._database_manager.setCallbackOnDatabaseOnline(
            self._onDatabaseOnline
        )
        self._database_manager.setCallbackOnDatabaseOffline(
            self._onDatabaseOffline
        )
        
    def _onDatabaseOnline(self):
        event = DatabaseStatusEvent()
        event.setStatusToOnline()
        self._environment.fireEvent(event)
        
    def _onDatabaseOffline(self):
        event = DatabaseStatusEvent()
        event.setStatusToOffline()
        self._environment.fireEvent(event)

    def _sendDatabase(self, target):
        message = CommandMessage()
        message['target'] = target
        message.setCommand("set_database")
        message.setParameter('database', self._database_manager.get()[target['component_name']])
        self._environment.sendMessage(message)
