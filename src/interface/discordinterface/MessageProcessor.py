from .processmessage.ProcessMessageTask import ProcessMessageTask
from morph.messages.CommandMessage import CommandMessage

import asyncio

class MessageProcessor:

    class PreprocessedMessage:
        def __init__(self, message):
            self._tokens = message.content.split(" ")
            self._first_token = self.token(0)
            self._message = message
            
        def token(self, index):
            return None if self.token_count() <= index else self._tokens[index]
            
        def tokens(self):
            return None if self.token_count() <= 0 else self._tokens
            
        def token_count(self):
            return len(self._tokens)
            
        def raw(self):
            return self._message
            
        def event(self):
            return None if self._first_token is None else self._first_token[1:]
            
        def first_character(self):
            return None if self._first_token is None else self._first_token[0]

    def __init__(self, permissions_manager, environment, logger):
        self._permissions_manager = permissions_manager
        self._logger = logger.getChild(self.__class__.__name__)
        self._environment = environment
        self._discord_configuration = self._environment.getStartupConfiguration()
        self._command_character = self._discord_configuration["commandcharacter"]
        self._logger.debug("initialized. command_character: " + self._command_character)
        
    def process(self, message):
        self._logger.debug("process called. message.content: " + message.content)
        process_message_task = ProcessMessageTask(**{
            "discord_configuration" : self._discord_configuration,
            "environment" : self._environment,
            "parent_logger" : self._logger,
            "permissions_manager" : self._permissions_manager,
            "preprocessed_message" : MessageProcessor.PreprocessedMessage(message)
        })
        asyncio.create_task(self._runTask(process_message_task, message.channel.id))
        
    async def _runTask(self, task, channel_id):
        self._logger.info("running task...")
        await task.run()
        self._logger.info("task complete. sending reply if needed.")
        reply = task.reply()
        if reply is not None:
            if isinstance(reply, dict):
                self._sendMessageToSelfIfNeeded(reply, channel_id)
            elif isinstance(reply, list):
                for reply_message in reply:
                    self._sendMessageToSelfIfNeeded(reply_message, channel_id)
            else:
                self._logger.warning(f"unrecognized reply type: {type(reply)}. no reply will be sent")
        
    async def _processMessageReply(self, message_task, channel_id):
        while not message_task.isComplete():
            self._logger.debug("task not yet complete. sleeping...")
            await asyncio.sleep(1)

    def _sendMessageToSelfIfNeeded(self, message_to_user, channel_id):
        if message_to_user is not None:
            message_to_self = CommandMessage()
            message_to_self['target'] = self._environment.getComponentInfo()
            message_to_self.setCommand("send")
            message_to_self.setParameter('message', message_to_user)
            message_to_self.setParameter('channel_id', channel_id)
            self._environment.sendMessage(message_to_self)
        


        
        