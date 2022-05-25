from .MessageProcessor import MessageProcessor
from .PermissionsManager import PermissionsManager
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
        self._ready_flags['is_discord_client_ready'] = True
        self._logger.debug(f"on_ready called. ready_flags: {self._ready_flags}")
 
    async def on_message(self, message):
        self._logger.info("on_message called. message.content: " + message.content)
        if self._isComponentReadyToReceiveMessages():
            self._message_processor.process(message)
        elif message.author.id != self.user.id:
            self._logger.warning(f"not yet ready to receive messages! dropping discord message. ready_flags: {self._ready_flags}")
            self._sendNotReadyToReceiveMessageToUser(message.channel.id)
        
    async def processMessage(self, received_message):
        message_to_process = await super().processMessage(received_message)
        if message_to_process is not None:
            self._continueProcessingMessage(message_to_process)

    async def sendMessageToUser(self, message_to_user, channel_id):
        self._logger.info(f"sending message. message_to_user: {message_to_user}, channel_id: {channel_id}")
        channel = self.get_channel(channel_id)
        await channel.send(embed = self._convertToEmbed(message_to_user))
        
    def _continueProcessingMessage(self, message_to_process):
        if isinstance(message_to_process, CommandMessage):
            command = message_to_process.getCommand()
            if command == "send":
                asyncio.create_task(self.sendMessageToUser(
                    message_to_process.getParameter('message'),
                    int(message_to_process.getParameter('channel_id'))))
            elif command == "command_set_response":
                self._updateCommandSet(message_to_process.getParameter('command_set'))
            
    def _isComponentReadyToReceiveMessages(self):
        self._logger.debug(f"_isComponentReadyToReceiveMessages called. ready_flags: {self._ready_flags}")
        return False not in self._ready_flags.values()

    def _prepareOwnerPermissionsIfNeeded(self):
        id = int(self._environment.getStartupConfiguration()["ownerid"])
        if not self._ready_flags['are_owner_permissions_set'] and not self._permissions_manager.isUserAnOwner(id):
            self._permissions_manager.removeOwners()
            self._permissions_manager.addUserAsOwner(id)
        self._ready_flags['are_owner_permissions_set'] = True
        self._logger.debug(f"_prepareOwnerPermissionsIfNeeded called. ready_flags: {self._ready_flags}")
        
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
        self._logger.debug(f"_finishInitializationIfNotYetDone called. ready_flags: {self._ready_flags}")

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
        asyncio.create_task(self.sendMessageToUser(message, channel_id))
        
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
        self._logger.debug(f"_onSetDatabase called. new_database: {new_database}, ready_flags: {self._ready_flags}")
            
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
            
        
    