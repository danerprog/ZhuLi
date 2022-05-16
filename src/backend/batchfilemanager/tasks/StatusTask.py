from backend.batchfilemanager import MessageTemplates
import morph.Task


class StatusTask(morph.Task.Task):
    def __init__(self, **context):
        super().__init__(**context)
        self._bot_list = context['bot_list']
        self._bot_name = self._arguments.token(1)
        self._findBot()
        self._logger.debug(f"instantiated. bot_list: {self._bot_list}, bot_name: {self._bot_name}")

    async def run(self):
        self._reply = {'title' : "status"}
        if self._bot is not None:
            self._setBotStatusAsReply()
        elif self._bot_name is not None:
            self._reply['description'] = MessageTemplates.MESSAGE['bot_not_found'].format(self._bot_name)
            self._reply['level'] = "warning"
        else:
            self._setOwnStatusAsReply()
        
    def _setOwnStatusAsReply(self):
        self._reply['description'] = self._environment.getAppName()
        self._reply['fields'] = []
        message_field_value = ""
        for bot in self._bot_list:
            message_field_value += "{}: {}\n".format(
                bot.getName(),
                "Running" if bot.isRunning() else "Down"
            )
        self._reply['fields'].append({
            'name' : "Status",
            'value' : message_field_value,
            'inline' : False
        })
        self._reply['level'] = "info"

    def _setBotStatusAsReply(self):
        isBotRunning = self._bot.isRunning()
        self._reply['title'] = "status"
        self._reply['description'] = self._bot.getName()
        self._reply['fields'] = []
        self._reply['fields'].append({
            'name' : "Status",
            'value' : "Running" if isBotRunning else "Down",
            'inline' : False
        })
        if isBotRunning:
            self._reply['fields'].append({
                'name' : "Started",
                'value' : self._bot.getTimestampStarted(),
                'inline' : False
            })
            self._reply['fields'].append({
                'name' : "Uptime",
                'value' : self._bot.getTimestampUptime(),
                'inline' : False
            })
        self._reply['level'] = "info"
            
    def _findBot(self):
        self._bot = None
        for bot in self._bot_list:
            if self._bot_name == bot.getName():
                self._bot = bot
                break
        

