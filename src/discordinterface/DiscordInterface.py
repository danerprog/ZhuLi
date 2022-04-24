from .MessageProcessor import MessageProcessor
from .PermissionsManager import PermissionsManager
from environment.Environment import Environment

import discord


class DiscordInterface(discord.Client):

    class NoMessageProcessor:
        def __init__(self, logger):
            self._logger = logger
            
        def process(self, message):
            self._logger.warning(f"ignoring message: {message}")

    def __init__(self):
        super().__init__()
        self._environment = Environment.instance()
        self._logger = self._environment.getLogger("DiscordInterface")
        self._message_processor = DiscordInterface.NoMessageProcessor(self._logger.getChild("NoMessageProcessor"))
        self._permissions_manager = PermissionsManager(
            self._environment.database()['discordinterface']['permissions'],
            self._logger.getChild("PermissionsManager")
        )
        self._message_processor = MessageProcessor(
            self._permissions_manager,
            self._logger.getChild("MessageProcessor")
        )
        self._logger.debug("instantiated")
        
    async def on_ready(self):
        self._logger.info("on_ready called")
        self._prepareOwnerPermissions()
        self._registerCallbacks()
 
    async def on_message(self, message):
        self._logger.info("on_message called. message.content: " + message.content)
        self._message_processor.process(message)
            
    async def sendMessage(self, *args, **kwargs):
        self._logger.info("sending message. args: {}, kwargs: {}".format(
            str(args),
            str(kwargs)
        ))
        message = kwargs["message"]
        channel = self.get_channel(int(kwargs["channel_id"]))
        await channel.send(embed = self._convertToEmbed(message))
        
    def _prepareOwnerPermissions(self):
        id = int(self._environment.getConfiguration("main")["Discord"]["ownerid"])
        self._permissions_manager.addEventPermissionsForUser('start', id)
        self._permissions_manager.addEventPermissionsForUser('stop', id)
        self._permissions_manager.addEventPermissionsForUser('restart', id)
        self._permissions_manager.addEventPermissionsForUser('status', id)
        self._permissions_manager.addEventPermissionsForUser('add', id)
        self._permissions_manager.addEventPermissionsForUser('remove', id)

    def _convertToEmbed(self, message):
        embed = discord.Embed()
        embed.title = message["title"]
        embed.description = message["description"]
        embed.colour = self._getEmbedColourFromMessage(message)
        if "fields" in message:
            for field in message["fields"]:
                embed.add_field(name = field["name"], value = field["value"], inline = field["inline"])
        return embed
        
    def _getEmbedColourFromMessage(self, message):
        value = discord.Colour.darker_gray()
        if "level" in message:
            if message["level"] == "info":
                value = discord.Colour.blue()
            elif message["level"] == "warning":
                value = discord.Colour.orange()
            elif message["level"] == "error":
                value = discord.Colour.red()
        self._logger.debug("_getEmbedColourFromMessage called. value: {}".format(
            str(value)
        ))
        return value
        
    def _registerCallbacks(self):
        self._environment.registerCallback("send", self.sendMessage)