from backend.batchfilemanager import MessageTemplates
from morph.messages.CommandMessage import CommandMessage
from morph.tasks.Task import Task


class CommandSetRequestTask(Task):
    def __init__(self, **context):
        super().__init__(**context)
        self._logger.debug(f"instantiated.")

    async def run(self):
        self._setCommandListResponseAsReply()

    def _setCommandListResponseAsReply(self):
        message = CommandMessage()
        message['target'] = self._message['sender']
        message.setCommand("command_set_response")
        message.setParameter('command_set', self._environment.getRuntimeConfiguration()['command_set'])
        self._environment.sendMessage(message)
