from .MessageProcessor import MessageProcessor
from .PermissionsManager import PermissionsManager
from morph import EventConstants
from morph.MainComponent import MainComponent
from morph.messages.CommandMessage import CommandMessage

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
        self._updateCommandSet(['add', 'remove', 'list'])
        asyncio.create_task(self.start(self._environment.getStartupConfiguration()["token"]))
        self._logger.debug("instantiated")
        
    async def on_ready(self):
        self._logger.info("on_ready called")
        self._ready_flags['is_discord_client_ready'] = True
 
    async def on_message(self, message):
        self._logger.info("on_message called. message.content: " + message.content)
        if self._isComponentReadyToReceiveMessages():
            self._message_processor.process(message)
        elif message.author.id != self.user.id:
            self._logger.warning(f"not yet ready to receive messages! dropping discord message. ready_flags: {self._ready_flags}")
            self._sendNotReadyToReceiveMessageToUser(message.channel.id)
        
    async def processMessage(self, received_message):
        was_message_processed = await super().processMessage(received_message)
        if was_message_processed:
            parameters = received_message['parameters']
            self._processCommand(parameters)

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
            asyncio.create_task(self.sendMessageToUser(**parameters))
        elif parameters['command'] == 'command_set_response':
            self._updateCommandSet(parameters['command_set'])
        else:
            self._logger.info(f"Unrecognized command '{parameters['command']}'!")
            
    def _isComponentReadyToReceiveMessages(self):
        return False not in self._ready_flags.values()

    def _prepareOwnerPermissionsIfNeeded(self):
        id = int(self._environment.getStartupConfiguration()["ownerid"])
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
            
    def _sendNotReadyToReceiveMessageToUser(self, channel_id):
        message = {
            'title' : "Message Dropped",
            'description' : "Bot is not yet ready to receive messages.",
            'level' : "warning",
            'fields' : self._getReadyCheckFields()
        }
        kwargs = {
            'message' : message,
            'channel_id' : channel_id
        }
        asyncio.create_task(self.sendMessageToUser(**kwargs))
        
    def _getReadyCheckFields(self):
        ready_check_names = {
            'name' : "Ready checks",
            'value' : "",
            'inline' : True
        }
        ready_check_values = {
            'name' : "Value",
            'value' : "",
            'inline' : True
        }
        for name, value in self._ready_flags.items():
            ready_check_names['value'] = f"{ready_check_names['value']}\n{name}"
            ready_check_values['value'] = f"{ready_check_values['value']}\n{value}"
        return [ready_check_names, ready_check_values]
        
    def _onSetDatabase(self, new_database):
        super()._onSetDatabase(new_database)
        self._ready_flags['is_database_ready'] = new_database is not None
        if self._ready_flags['is_database_ready']:
            self._finishInitializationIfNotYetDone()
            self._prepareOwnerPermissionsIfNeeded()
            
    def _onComponentsLoaded(self, loaded_components):
        super()._onComponentsLoaded(loaded_components)
        for backend_component_name in loaded_components['backend']:
            self._sendCommandListRequestMessage(backend_component_name)
            
    def _sendCommandListRequestMessage(self, backend_component_name):
        message = CommandMessage()
        message['target'] = {
            'component_level' : "backend",
            'component_name' : backend_component_name
        }
        message.setCommand("command_set_request")
        self._environment.sendMessage(message)
        
    def _updateCommandSet(self, iterable_of_commands):
        self._environment.getRuntimeConfiguration()['command_set'].update(iterable_of_commands)
            
        
    