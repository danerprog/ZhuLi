from .Bot import Bot
from .tasks.RestartTask import RestartTask
from .tasks.StartTask import StartTask
from .tasks.StopTask import StopTask
from .tasks.StatusTask import StatusTask
from morph.MainComponent import MainComponent
from morph.processors.CommandMessageToTaskProcessor import CommandMessageToTaskProcessor

import asyncio
import os


@CommandMessageToTaskProcessor({
    'start' : StartTask,
    'stop' : StopTask,
    'restart' : RestartTask,
    'status' : StatusTask
})
class BatchFileManager(MainComponent):

    def __init__(self):
        super().__init__()
        self._initializeBots()
        self._initializeRuntimeConfiguration()

    def _initializeBots(self):
        self._logger.info("initializing bots...")
        self._bots = []
        batch_file_directory = self._environment.getStartupConfiguration()["directory"]
        for filename in os.listdir(batch_file_directory):
            if filename.endswith(".bat"):
                self._initializeBot(batch_file_directory, filename)
                
    def _initializeRuntimeConfiguration(self):
        runtime_configuration = self._environment.getRuntimeConfiguration()
        runtime_configuration['command_set'].update(['start', 'stop', 'restart', 'status'])
        runtime_configuration['bot_list'] = self._bots
  
    def _initializeBot(self, batch_file_directory, batch_file):
        self._logger.info("initializing bot. batch_file_directory: {}, batch_file: {}".format(
            batch_file_directory,
            batch_file
        ))
        batch_filename = batch_file.split(".", 2)[0]
        self._bots.append(Bot(
            batch_filename,
            batch_file_directory + batch_file,
            self._environment.getLogger("Bot").getChild(batch_filename)
        ))


            
    
   