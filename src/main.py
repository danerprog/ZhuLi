from environment.Environment import Environment
from discordinterface.DiscordInterface import DiscordInterface
from zhuli.ZhuLi import ZhuLi

import sys


class Main:

    def __init__(self, config_directory):
        self._environment = Environment.instance(config_directory);
        self._zhu_li = ZhuLi()
        self._initializeLoggers()
        
    def run(self):
        self._logger.debug("run called")
        discord_interface = DiscordInterface()
        discord_interface.run(self._environment.getConfiguration("main").get("Discord", "Token"))
    
    def _initializeLoggers(self):
        logging_manager = Environment.instance().logger()
        logging_manager.hideLogger("discord")
        self._logger = logging_manager.getLogger("Main")


if __name__ == "__main__":
    main = Main(sys.argv[1])
    main.run()