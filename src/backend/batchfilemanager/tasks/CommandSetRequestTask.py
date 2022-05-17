from backend.batchfilemanager import MessageTemplates
from morph.Message import Message
import morph.Task


class CommandSetRequestTask(morph.Task.Task):
    def __init__(self, **context):
        super().__init__(**context)
        self._logger.debug(f"instantiated.")

    async def run(self):
        self._setCommandListResponseAsReply()

    def _setCommandListResponseAsReply(self):
        message = Message()
        message['target'] = self._message['sender']
        message['parameters'] = {
            'command' : "command_set_response",
            'command_set' : self._environment.getRuntimeConfiguration()['command_set']
        }
        self._environment.sendMessage(message)

