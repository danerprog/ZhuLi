from .AddEventTask import AddEventTask
from .ListEventTask import ListEventTask
from .MessageTask import MessageTask
from .RemoveEventTask import RemoveEventTask
from .ShouldMessageBeProcessedTask import ShouldMessageBeProcessedTask
from morph.messages.CommandMessage import CommandMessage


class ProcessMessageTask(MessageTask):
    def __init__(self, **context):
        super().__init__(**context)
        self._logger.debug("initialized")
        
    async def run(self):
        self._logger.debug("running")
        should_message_be_processed_task = ShouldMessageBeProcessedTask(**self._context)
        await should_message_be_processed_task.run()
        if should_message_be_processed_task.result():
            await self._processMessage()
        else:
            should_message_be_processed_task.passResultsTo(self)
            self._is_complete = True

    async def _processMessage(self):
        event = self._context['preprocessed_message'].event()
        task = self._getTask(event)
        if task is not None:
            await task.run()
            task.passResultsTo(self)
        else:
            self._reply = None
            self._sendCommandMessage(event)
            
    def _getTask(self, event):
        task_to_return = None
        if event == "add" :
            task_to_return = AddEventTask(**self._context)
        elif event == "remove" :
            task_to_return = RemoveEventTask(**self._context)
        elif event == "list" :
            task_to_return = ListEventTask(**self._context)
        return task_to_return
        
    def _sendCommandMessage(self, command):
        message = CommandMessage()
        message['target'] = {
            'component_level' : "backend"
        }
        message.setCommand(command)
        message.setParameter('arguments_string', self._context['preprocessed_message'].raw().content)
        message.setParameter('channel_id', self._context['preprocessed_message'].raw().channel.id)
        self._context['environment'].sendMessage(message)


