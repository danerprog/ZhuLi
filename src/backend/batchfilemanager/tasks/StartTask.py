from backend.batchfilemanager import MessageTemplates
from morph.Message import Message
import morph.Task


class StartTask(morph.Task.Task):
    def __init__(self, **context):
        super().__init__(**context)
        self._bot_list = context['bot_list']
        self._bot_name = self._arguments.token(1)
        self._findBot()
        self._logger.debug(f"instantiated. bot_list: {self._bot_list}, bot_name: {self._bot_name}")

    async def run(self):
        message = {'title' : "start"}
        if self._bot is not None:
            if self._bot.start():
                message['description'] = MessageTemplates.MESSAGE['start_successful'].format(self._bot_name)
                message['level'] = "info"
            else:
                message['description'] = MessageTemplates.MESSAGE['already_running'].format(self._bot_name)
                message['level'] = "warning"
        elif self._bot_name is not None:
            message['description'] = MessageTemplates.MESSAGE['bot_not_found'].format(self._bot_name)
            message['level'] = "warning"
        else:
            message['description'] = MessageTemplates.MESSAGE['no_name_provided']
            message['level'] = "warning"
        self._sendMessage(message)
            
    def _findBot(self):
        self._bot = None
        for bot in self._bot_list:
            if self._bot_name == bot.getName():
                self._bot = bot
                break

    def _sendMessage(self, message_to_user):
        message_to_component = Message()
        message_to_component['target'] = self._message['sender']
        message_to_component['parameters'] = {
            'command' : "send",
            'message' : message_to_user,
            'channel_id' : self._message['parameters']['channel_id']
        }
        self._environment.sendMessage(message_to_component)