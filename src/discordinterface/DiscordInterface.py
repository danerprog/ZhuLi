from environment.Environment import Environment

import discord


class DiscordInterface(discord.Client):

    def __init__(self):
        super().__init__()
        self._environment = Environment.instance()
        self._logger = self._environment.getLogger("DiscordInterface")
        self._registerCallbacks()
 
    async def on_message(self, message):
        message_string = message.content
        self._logger.debug("on_message called. message_string: " + message_string)
        message_tokens = message_string.split(" ")
        shouldMessageBeProcessedByBot = self._shouldMessageBeParsedByBot(message.author, message_tokens[0])
        if shouldMessageBeProcessedByBot:
            self._logger.info("processing message.")
            self._processingMessage(message_tokens, message.channel.id)
            
    async def sendMessage(self, *args, **kwargs):
        self._logger.info("sending message. args: {}, kwargs: {}".format(
            str(args),
            str(kwargs)
        ))
        message = kwargs["message"]
        channel = self.get_channel(int(kwargs["channel_id"]))
        await channel.send(embed = self._convertToEmbed(message))
        
    def _shouldMessageBeParsedByBot(self, sender, first_token):
        self._logger.debug("_shouldMessageBeParsedByBot called. sender_id : {}, first_token: {}".format(
            str(sender.id),
            first_token
        ))
        return self.user != sender and first_token[0] == "!"
        
    def _processingMessage(self, message_tokens, channel_id):
        event = message_tokens[0][1:]
        self._logger.info("firing event {}. message_tokens: {}".format(
            event,
            str(message_tokens)
        ))
        kwargs = {
            "bot_name" : None if len(message_tokens) <= 1 else message_tokens[1],
            "channel_id" : str(channel_id)
        }
        self._environment.fireEvent(event, **kwargs)
        
    def _convertToEmbed(self, message):
        embed = discord.Embed()
        embed.title = message["title"]
        embed.description = message["description"]
        for field in message["fields"]:
            embed.add_field(name = field["name"], value = field["value"], inline = field["inline"])
        return embed
        
    def _registerCallbacks(self):
        self._environment.registerCallback("send", self.sendMessage)