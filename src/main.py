from morph.morph.MorphSystem import MorphSystem

import asyncio


class Main:

    def __init__(self, config_directory):
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
        
    async def _bootMorphSystem(self):
        self._morph_system = MorphSystem()

    def _startEventLoop(self):
        self._loop = None
        try:
            self._loop = asyncio.new_event_loop()
            self._loop.run_until_complete(self._bootMorphSystem())
            self._loop.run_forever()
        except KeyboardInterrupt:
            self._loop.stop()
        finally:
            self._loop.close()

if __name__ == "__main__":
    import sys
    main = Main(sys.argv[1])