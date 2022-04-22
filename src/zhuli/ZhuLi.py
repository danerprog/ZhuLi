from .Bot import Bot
from environment.Environment import Environment

import os


class ZhuLi:
    def __init__(self):
        self._environment = Environment.instance()
        self._logger = self._environment.getLogger("ZhuLi")
        self._bots = []
        self._initializeBots()
        self._registerCallbacks()
        
    def start(self, *args, **kwargs):
        self._logger.info("start called. kwargs: " + str(kwargs))
        bot_name = kwargs["bot_name"]
        message = {"title" : "start"}
        
        for bot in self._bots:
            if bot_name == bot.getName():
                result = bot.start()
                if result:
                    message["description"] = bot_name + " was successfully started."
                    message["level"] = "info"
                else:
                    message["description"] = bot_name + " is already running!"
                    message["level"] = "warning"
                    
        self._sendMessage(message, **kwargs)
    
    def stop(self, *args, **kwargs):
        self._logger.info("stop called. kwargs: " + str(kwargs))
        bot_name = kwargs["bot_name"]
        message = {"title" : "stop"}
        
        for bot in self._bots:
            if bot_name == bot.getName():
                result = bot.stop()
                
                if result:
                    message["description"] = bot_name + " was successfully stopped."
                    message["level"] = "info"
                else:
                    message["description"] = bot_name + " is not running!"
                    message["level"] = "warning"
                    
        self._sendMessage(message, **kwargs)
    
    def restart(self, *args, **kwargs):
        self._logger.info("restart called. kwargs: " + str(kwargs))
        bot_name = kwargs["bot_name"]
        message = {"title" : "restart"}
        
        for bot in self._bots:
            if bot_name == bot.getName():
                result = bot.restart()
                
                if result:
                    message["description"] = bot_name + " was successfully restarted."
                    message["level"] = "info"
                else:
                    message["description"] = "Unable to restart {}!".format(bot_name)
                    message["level"] = "warning"
                    
        self._sendMessage(message, **kwargs)
    
    def status(self, *args, **in_kwargs):
        self._logger.info("status called. kwargs: " + str(in_kwargs))
        bot_name = in_kwargs["bot_name"]
        self._sendStatusMessages(bot_name, in_kwargs)
        
    def _sendStatusMessages(self, bot_name, in_kwargs):
        if bot_name is None:
            self._sendOwnStatusMessage(in_kwargs)
        else:
            for bot in self._bots:
                if bot.getName() == bot_name:
                    self._sendBotStatusMessage(bot, in_kwargs)
                    
    def _sendOwnStatusMessage(self, in_kwargs):
        message = {}
        message["title"] = "status"
        message["description"] = self._environment.getConfiguration("main")["App"]["name"]
        message["fields"] = []
        message_field_value = ""
        for bot in self._bots:
            message_field_value += "{}: {}\n".format(
                bot.getName(),
                "Running" if bot.isRunning() else "Down"
            )
        message["fields"].append({
            "name" : "Status",
            "value" : message_field_value,
            "inline" : False
        })
        message["level"] = "info"
        self._sendMessage(message, **in_kwargs)
        
    def _sendBotStatusMessage(self, bot, in_kwargs):
        isBotRunning = bot.isRunning()
        message = {}
        message["title"] = "status"
        message["description"] = bot.getName()
        message["fields"] = []
        message["fields"].append({
            "name" : "Status",
            "value" : "Running" if isBotRunning else "Down",
            "inline" : False
        })
        if isBotRunning:
            message["fields"].append({
                "name" : "Started",
                "value" : bot.getTimestampStarted(),
                "inline" : False
            })
            message["fields"].append({
                "name" : "Uptime",
                "value" : bot.getTimestampUptime(),
                "inline" : False
            })
        message["level"] = "info"
        self._sendMessage(message, **in_kwargs)
        
    def _sendMessage(self, message, **out_kwargs):
        out_kwargs["message"] = message
        self._environment.fireEvent("send", **out_kwargs)

    def _initializeBots(self):
        self._logger.info("initializing bots...")
        batch_file_directory = self._environment.configuration()["main"]["App"]["batchfiledirectory"]
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
        
    def _registerCallbacks(self):
        self._environment.registerCallback("start", self.start)
        self._environment.registerCallback("stop", self.stop)
        self._environment.registerCallback("restart", self.restart)
        self._environment.registerCallback("status", self.status)
        
