from .MessageProcessor import MessageProcessor
from environment.Environment import Environment

import discord


class DiscordInterface(discord.Client):

    def __init__(self):
        super().__init__()
        self._environment = Environment.instance()
        self._logger = self._environment.getLogger("DiscordInterface")
        self._message_processor = MessageProcessor(
            self._logger.getChild("MessageProcessor")
        )
        self._registerCallbacks()
 
    async def on_message(self, message):
        self._logger.debug("on_message called. message.content: " + message.content)
        self._message_processor.process(message)
            
    async def sendMessage(self, *args, **kwargs):
        self._logger.info("sending message. args: {}, kwargs: {}".format(
            str(args),
            str(kwargs)
        ))
        message = kwargs["message"]
        channel = self.get_channel(int(kwargs["channel_id"]))
        await channel.send(embed = self._convertToEmbed(message))

    def _convertToEmbed(self, message):
        embed = discord.Embed()
        embed.title = message["title"]
        embed.description = message["description"]
        for field in message["fields"]:
            embed.add_field(name = field["name"], value = field["value"], inline = field["inline"])
        return embed
        
    def _registerCallbacks(self):
        self._environment.registerCallback("send", self.sendMessage)