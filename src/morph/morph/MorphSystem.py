from morph import EventConstants
from morph.MainComponent import MainComponent

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
        self._loadDiscordInterface()
        self._fireComponentsLoadedEvent()

    def _loadBatchFileManager(self):
        import backend.batchfilemanager
        self._loaded_components['backend'].append('batchfilemanager')

    def _loadDiscordInterface(self):
        import interface.discordinterface
        self._loaded_components['interface'].append('discordinterface')
    
    def _fireComponentsLoadedEvent(self):
        event = {
            'type' : EventConstants.TYPES['components_loaded'],
            'parameters' : {
                'loaded_components' : self._loaded_components
            }
        }
        self._environment.fireEvent(event)
