from morph.messages.CommandMessage import CommandMessage
from morph.processors.MessageProcessor import MessageProcessor

from abc import abstractmethod
import asyncio


class CommandMessageToTaskProcessor:

    def __init__(self, command_to_task_dictionary):
        self._command_to_task_dictionary = command_to_task_dictionary
        
    def __call__(self, class_to_decorate):
        can_class_be_decorated = self._canClassBeDecorated(class_to_decorate)
        if can_class_be_decorated:
            self._decorateClass(class_to_decorate)
        return class_to_decorate

    def _canClassBeDecorated(self, class_to_decorate):
        can_class_be_decorated = False
        if issubclass(class_to_decorate, MessageProcessor):
            can_class_be_decorated = True
        return can_class_be_decorated
    
    def _decorateClass(self, class_to_decorate):
        originalProcessMessage = None if not hasattr(class_to_decorate, 'processMessage') else class_to_decorate.processMessage
        originalGetTask = None if not hasattr(class_to_decorate, '_getTask') else class_to_decorate._getTask
    
        async def processMessage(self, message):
            message_to_process = await originalProcessMessage(self, message)
            if message_to_process is not None and isinstance(message, CommandMessage):
                task = self._getTask(message)
                if task is not None:
                    asyncio.create_task(self._runTask(task))
            return message_to_process
             
        def _getTask(self, message):
            task_to_return = None
            if originalGetTask is not None:
                task_to_return = originalGetTask(self, message)
            if task_to_return is None:
                command = message.getCommand()
                if command in self.__class__._command_to_task_dictionary.keys():
                    context = self._getTaskContext()
                    context['message'] = message
                    context['arguments_string'] = None if 'arguments_string' not in message['parameters'] else message['parameters']['arguments_string']
                    task_to_return = self.__class__._command_to_task_dictionary[command](**context)
            return task_to_return
            
        async def _runTask(self, task):
            self._logger.info("running task...")
            await task.run()
            self._logger.info("task complete.")
            
        @abstractmethod
        def _getTaskContext(self):
            pass
            
        setattr(class_to_decorate, 'processMessage', processMessage)
        setattr(class_to_decorate, '_getTask', _getTask)
        if not hasattr(class_to_decorate, '_runTask'):
            setattr(class_to_decorate, '_runTask', _runTask)
        if not hasattr(class_to_decorate, '_getTaskContext'):
            class_to_decorate._getTaskContext = _getTaskContext
        if not hasattr(class_to_decorate, '_command_to_task_dictionary'):
            setattr(class_to_decorate, '_command_to_task_dictionary', {})
        for command, task_class in self._command_to_task_dictionary.items():
            class_to_decorate._command_to_task_dictionary[command] = task_class
            
        return class_to_decorate