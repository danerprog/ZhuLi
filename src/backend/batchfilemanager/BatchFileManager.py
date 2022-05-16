from . import MessageTemplates
from .Bot import Bot
from .tasks.RestartTask import RestartTask
from .tasks.StartTask import StartTask
from .tasks.StopTask import StopTask
from .tasks.StatusTask import StatusTask
from morph import EventConstants
from morph.MainComponent import MainComponent
from morph.Message import Message

import asyncio
import os


class BatchFileManager(MainComponent):

    def __init__(self):
        super().__init__()
        self._environment.getRuntimeConfiguration()['command_set'].update(['start', 'stop', 'restart', 'status'])
        self._initializeBots()
        
    async def processMessage(self, received_message):
        was_message_processed = await super().processMessage(received_message)
        if was_message_processed:
            self._continueProcessingMessage(received_message)
        
    async def processEvent(self, event):
        self._logger.info(f"Received event. event: {event}")
        if event['type'] == EventConstants.TYPES['user_input']:
            self._process(event['parameters'])

    def _process(self, parameters):
        task = self._getTask(parameters)
        if task is not None:
            asyncio.create_task(self._runTask(task, **parameters['kwargs']))
        
    def _getTask(self, parameters):
        task_to_return = None
        command = parameters['command']
        context = {
            'environment' : self._environment,
            'parent_logger' : self._logger,
            'arguments_string' : parameters['kwargs']['arguments_string'],
            'bot_list' : self._bots
        }
        if command == 'start':
            task_to_return = StartTask(**context)
        elif command == 'stop':
            task_to_return = StopTask(**context)
        elif command == 'restart':
            task_to_return = RestartTask(**context)
        elif command == 'status':
            task_to_return = StatusTask(**context)
        else:
            self._logger.warning(f"Unrecognized command '{command}'! parameters: {parameters}")
        return task_to_return
        
    async def _runTask(self, task, **kwargs):
        self._logger.info("running task...")
        await task.run()
        self._logger.info("task complete. sending reply if needed.")
        reply = task.reply()
        if reply is not None:
            if isinstance(reply, dict):
                self._sendMessage(reply, **kwargs)
            elif isinstance(reply, list):
                for reply_message in reply:
                    self._sendMessage(reply_message, **kwargs)
            else:
                self._logger.warning(f"unrecognized reply type: {type(reply)}. no reply will be sent")
       
    def _sendStatusMessages(self, bot, kwargs):
        if bot is None:
            self._sendOwnStatusMessage(kwargs)
        else:
            self._sendBotStatusMessage(bot, kwargs)
         
    def _sendMessage(self, message_to_user, **kwargs):
        kwargs["message"] = message_to_user
        message = Message()
        message['target'] = {
            'component_level' : 'interface'
        }
        message['parameters'] = {
            'command' : 'send',
            'kwargs' : kwargs
        }
        self._environment.sendMessage(message)

    def _initializeBots(self):
        self._logger.info("initializing bots...")
        self._bots = []
        batch_file_directory = self._environment.getStartupConfiguration()["directory"]
        for filename in os.listdir(batch_file_directory):
            if filename.endswith(".bat"):
                self._initializeBot(batch_file_directory, filename)
        
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

    def _continueProcessingMessage(self, message):
        command = message['parameters']['command']
        if command == "command_set_request":
            self._sendCommandListResponse(message['sender'])
        else:
            self._logger.info(f"Unrecognized command: {command}")
            
    def _sendCommandListResponse(self, target):
        message = Message()
        message['target'] = target
        message['parameters'] = {
            'command' : "command_set_response",
            'command_set' : self._environment.getRuntimeConfiguration()['command_set']
        }
        self._environment.sendMessage(message)
   