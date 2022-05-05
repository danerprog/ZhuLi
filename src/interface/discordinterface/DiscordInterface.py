from .MessageProcessor import MessageProcessor
from .PermissionsManager import PermissionsManager
from morph import EventConstants
from morph.MainComponent import MainComponent

import asyncio
import discord


class DiscordInterface(discord.Client, MainComponent):

    def __init__(self):
        discord.Client.__init__(self)
        MainComponent.__init__(self)
        self._ready_flags = {
            'is_discord_client_ready' : False,
            'is_database_ready' : False,
            'are_owner_permissions_set' : False,
            'is_interface_fully_initialized' : False
        }
        asyncio.create_task(self.start(self._environment.configuration()["main"]["Discord"]["token"]))
        self._logger.debug("instantiated")
        
    async def on_ready(self):
        self._logger.info("on_ready called")
        self._ready_flags['is_discord_client_ready'] = True
 
    async def on_message(self, message):
        self._logger.info("on_message called. message.content: " + message.content)
        if self._isComponentReadyToReceiveMessages():
            self._message_processor.process(message)
        else:
            self._logger.warning(f"not yet ready to receive messages! dropping discord message. ready_flags: {self._ready_flags}")
        
    async def processMessage(self, received_message):
        was_message_processed = await super().processMessage(received_message)
        if was_message_processed:
            parameters = received_message['parameters']
            if self._isComponentReadyToReceiveMessages():
                self._processCommand(parameters)
            else:
                self._logger.warning(f"not yet ready to receive messages! dropping morph message. ready_flags: {self._ready_flags}")
      
    async def sendMessageToUser(self, *args, **kwargs):
        self._logger.info("sending message. args: {}, kwargs: {}".format(
            str(args),
            str(kwargs)
        ))
        message = kwargs["message"]
        channel = self.get_channel(int(kwargs["channel_id"]))
        await channel.send(embed = self._convertToEmbed(message))
        
    def _processCommand(self, parameters):
        if parameters['command'] == 'send':
            asyncio.create_task(self.sendMessageToUser(**parameters['kwargs']))
        else:
            self._logger.warning(f"Unrecognized command '{parameters['command']}'!")
            
    def _isComponentReadyToReceiveMessages(self):
        return False not in self._ready_flags.values()

    def _prepareOwnerPermissionsIfNeeded(self):
        id = int(self._environment.getConfiguration("main")["Discord"]["ownerid"])
        if not self._ready_flags['are_owner_permissions_set'] and not self._permissions_manager.isUserAnOwner(id):
            self._permissions_manager.removeOwners()
            self._permissions_manager.addUserAsOwner(id)
        self._ready_flags['are_owner_permissions_set'] = True
        
    def _finishInitializationIfNotYetDone(self):
        if not self._ready_flags['is_interface_fully_initialized']:
            self._permissions_manager = PermissionsManager(
                self._environment,
                self._environment.database(),
                self._logger
            )
            self._message_processor = MessageProcessor(
                self._permissions_manager,
                self._environment,
                self._logger
            )
            self._ready_flags['is_interface_fully_initialized'] = True

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
    
    def _onSetDatabase(self, new_database):
        super()._onSetDatabase(new_database)
        self._ready_flags['is_database_ready'] = new_database is not None
        if self._ready_flags['is_database_ready']:
            self._finishInitializationIfNotYetDone()
            self._prepareOwnerPermissionsIfNeeded()

            
        
    