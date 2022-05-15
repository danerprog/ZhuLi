from .DatabaseManager import DatabaseManager
from morph import EventConstants
from morph.Event import Event
from morph.MainComponent import MainComponent
from morph.Message import Message

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
        was_message_processed = await super().processMessage(message)
        if was_message_processed:
            parameters = message['parameters']
            if parameters['command'] == 'request_database':
                self._sendDatabase(message['sender'])

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
        event = Event()
        event['type'] = EventConstants.TYPES['components_loaded']
        event['parameters'] = {
            'loaded_components' : self._loaded_components
        }
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
        event = Event()
        event['type'] = EventConstants.TYPES['database_status']
        event['parameters'] = {
            'status' : "online"
        }
        self._environment.fireEvent(event)
        
    def _onDatabaseOffline(self):
        event = Event()
        event['type'] = EventConstants.TYPES['database_status']
        event['parameters'] = {
            'status' : "offline"
        }
        self._environment.fireEvent(event)

    def _sendDatabase(self, target):
        message = Message()
        message['target'] = target
        message['parameters'] = {
            'command' : 'set_database',
            'database' : self._database_manager.get()[target['component_name']]
        }
        self._environment.sendMessage(message)
