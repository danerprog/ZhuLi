from . import EventConstants
from . import Message

from abc import abstractmethod
import asyncio


class UserInputEventToTaskProcessor:

    def __init__(self, command_to_task_dictionary):
        self._command_to_task_dictionary = command_to_task_dictionary
        
    def __call__(self, class_to_decorate):
        originalProcessEvent = None if not hasattr(class_to_decorate, 'processEvent') else class_to_decorate.processEvent
        originalGetTask = None if not hasattr(class_to_decorate, '_getTask') else class_to_decorate._getTask
    
        async def processEvent(self, event):
            should_event_be_processed = True
            if originalProcessEvent is not None:
                should_event_be_processed = await originalProcessEvent(self, event)
            if should_event_be_processed and event['type'] == EventConstants.TYPES['user_input']:
                task = self._getTask(event)
                if task is not None:
                    asyncio.create_task(self._runTask(task, **event['parameters']))
            return should_event_be_processed
                
        def _getTask(self, message):
            task_to_return = None
            if originalGetTask is not None:
                task_to_return = originalGetTask(self, message)
                if task_to_return is None:
                    command = message['parameters']['command']
                    if command in self.__class__._command_to_task_dictionary.keys():
                        context = self._getTaskContext()
                        context['message'] = message
                        context['arguments_string'] = "" if 'arguments_string' not in message['parameters'] else message['parameters']['arguments_string']
                        task_to_return = self.__class__._command_to_task_dictionary[command](**context)
            return task_to_return
            
        async def _runTask(self, task, **parameters):
            self._logger.info("running task...")
            await task.run()
            self._logger.info("task complete.")
            
        @abstractmethod
        def _getTaskContext(self):
            pass
            
        setattr(class_to_decorate, 'processEvent', processEvent)
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
            
            
class MessageWithCommandToTaskProcessor:

    def __init__(self, command_to_task_dictionary):
        self._command_to_task_dictionary = command_to_task_dictionary
        
    def __call__(self, class_to_decorate):
        originalProcessMessage = None if not hasattr(class_to_decorate, 'processMessage') else class_to_decorate.processMessage
        originalGetTask = None if not hasattr(class_to_decorate, '_getTask') else class_to_decorate._getTask
    
        async def processMessage(self, message):
            should_message_be_processed = True
            if originalProcessMessage is not None:
                should_message_be_processed = await originalProcessMessage(self, message)
            if should_message_be_processed:
                task = self._getTask(message)
                if task is not None:
                    asyncio.create_task(self._runTask(task, **message['parameters']))
            return should_message_be_processed
                
        def _getTask(self, message):
            task_to_return = None
            if originalGetTask is not None:
                task_to_return = originalGetTask(self, message)
                if task_to_return is None:
                    command = message['parameters']['command']
                    if command in self.__class__._command_to_task_dictionary.keys():
                        context = self._getTaskContext()
                        context['message'] = message
                        context['arguments_string'] = None if 'arguments_string' not in message['parameters'] else message['parameters']['arguments_string']
                        task_to_return = self.__class__._command_to_task_dictionary[command](**context)
            return task_to_return
            
        async def _runTask(self, task, **parameters):
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


