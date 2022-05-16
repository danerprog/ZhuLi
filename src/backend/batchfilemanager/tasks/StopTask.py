from backend.batchfilemanager import MessageTemplates
import morph.Task


class StopTask(morph.Task.Task):
    def __init__(self, **context):
        super().__init__(**context)
        self._bot_list = context['bot_list']
        self._bot_name = self._arguments.token(1)
        self._findBot()
        self._logger.debug(f"instantiated. bot_list: {self._bot_list}, bot_name: {self._bot_name}")

    async def run(self):
        message = {'title' : "stop"}
        if self._bot is not None:
            if self._bot.stop():
                message['description'] = MessageTemplates.MESSAGE['stop_successful'].format(self._bot_name)
                message['level'] = "info"
            else:
                message['description'] = MessageTemplates.MESSAGE['not_running'].format(self._bot_name)
                message['level'] = "warning"
        elif self._bot_name is not None:
            message['description'] = MessageTemplates.MESSAGE['bot_not_found'].format(self._bot_name)
            message['level'] = "warning"
        else:
            message['description'] = MessageTemplates.MESSAGE['no_name_provided']
            message['level'] = "warning"
        self._reply = message
            
    def _findBot(self):
        self._bot = None
        for bot in self._bot_list:
            if self._bot_name == bot.getName():
                self._bot = bot
                break
        

