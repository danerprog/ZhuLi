from morph.MainComponent import MainComponent
from morph.messages.CommandMessage import CommandMessage
from morph.processors.MessageProcessor import MessageProcessor

import asyncio


class CommandMessageToTaskProcessor:

    class Implementation(MessageProcessor):
        def __init__(self, command_to_task_dictionary, environment):
            self._command_to_task_dictionary = command_to_task_dictionary
            self._environment = environment
            self._logger = self._environment.getLogger("CommandMessageToTaskProcessor.Implementation")
            self._logger.debug(f"instantiated. command_to_task_dictionary: {command_to_task_dictionary}")

        async def processMessage(self, message_to_process):
            if isinstance(message_to_process, CommandMessage):
                self._logger.debug(f"processing message. message_to_process: {message_to_process}")
                task = self._getTask(message_to_process)
                if task is not None:
                    asyncio.create_task(self._runTask(task))
                    message_to_process = None
            return message_to_process

        def _getTask(self, message):
            task_to_return = None
            command = message.getCommand()
            if command in self._command_to_task_dictionary.keys():
                context = {
                    'environment' : self._environment,
                    'parent_logger' : self._logger,
                    'message' : message,
                    'arguments_string' : "" if 'arguments_string' not in message['parameters'] else message['parameters']['arguments_string']
                }
                task_to_return = self._command_to_task_dictionary[command](**context)
            self._logger.debug(f"_getTask called. message: {message}, task_to_return: {task_to_return}")
            return task_to_return
            
        async def _runTask(self, task):
            self._logger.info("running task...")
            await task.run()
            self._logger.info("task complete.")


    def __init__(self, command_to_task_dictionary):
        self._command_to_task_dictionary = command_to_task_dictionary
     
    def __call__(self, class_to_decorate):
        if issubclass(class_to_decorate, MainComponent):
            self._decorateClass(class_to_decorate)
        return class_to_decorate
        
    def _decorateClass(self, class_to_decorate):
        command_to_task_dictionary = self._command_to_task_dictionary
        originalDunderInit = None if not hasattr(class_to_decorate, '__init__') else class_to_decorate.__init__
        def __init__(self):
            if originalDunderInit is not None:
                originalDunderInit(self)
            message_processor = CommandMessageToTaskProcessor.Implementation(
                command_to_task_dictionary,
                self._environment
            )
            self.addMessageProcessor(message_processor)
        setattr(class_to_decorate, '__init__', __init__)

 