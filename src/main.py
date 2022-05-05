from morph import EventConstants

import asyncio


class Main:

    def __init__(self, config_directory):
        self._components = {
            'backend' : [],
            'interface' : []
        }
        self._initializeEnvironment(config_directory)
        self._initializeLoggers()
        self._startEventLoop()

    def _initializeLoggers(self):
        logging_manager = self._environment.logger()
        logging_manager.hideLogger("discord")
        self._logger = logging_manager.getLogger("Main")
        
    def _initializeEnvironment(self, config_directory):
        from morph.Environment import Environment
        Environment.initialize(config_directory)
        self._environment = Environment.instance();
        
    async def _loadComponents(self):
        self._loadBatchFileManager()
        self._loadDiscordInterface()
        self._fireComponentsLoadedEvent()

    def _loadBatchFileManager(self):
        import backend.batchfilemanager
        self._components['backend'].append('batchfilemanager')

    def _loadDiscordInterface(self):
        import interface.discordinterface
        self._components['interface'].append('discordinterface')
        
    def _fireComponentsLoadedEvent(self):
        event = {
            'type' : EventConstants.TYPES['components_loaded'],
            'origin' : {
                'component_id' : 0,
                'component_name' : 'morph',
                'component_level' : 'morph'
            },
            'parameters' : {
                'loaded_components' : self._components
            }
        }
        self._environment.fireEvent(event)
        
    def _startEventLoop(self):
        self._loop = None
        try:
            self._loop = asyncio.new_event_loop()
            self._loop.run_until_complete(self._loadComponents())
            self._loop.run_forever()
        except KeyboardInterrupt:
            self._loop.stop()
        finally:
            self._loop.close()

if __name__ == "__main__":
    import sys
    main = Main(sys.argv[1])