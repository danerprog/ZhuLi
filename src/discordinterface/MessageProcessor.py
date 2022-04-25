from environment.Environment import Environment
from .processmessage.ProcessMessageTask import ProcessMessageTask


class MessageProcessor:

    class PreprocessedMessage:
        def __init__(self, message):
            self._tokens = message.content.split(" ")
            self._first_token = self.token(0)
            self._message = message
            
        def token(self, index):
            return None if len(self._tokens) <= index else self._tokens[index]
            
        def raw(self):
            return self._message
            
        def event(self):
            return None if self._first_token is None else self._first_token[1:]
            
        def first_character(self):
            return None if self._first_token is None else self._first_token[0]

    def __init__(self, permissions_manager, logger):
        self._permissions_manager = permissions_manager
        self._logger = logger
        self._environment = Environment.instance()
        self._discord_configuration = self._environment.configuration()["main"]["Discord"]
        self._command_character = self._discord_configuration["commandcharacter"]
        self._logger.debug("initialized. command_character: " + self._command_character)
        
    def process(self, message):
        self._logger.debug("process called. message.content: " + message.content)
        process_message_task = ProcessMessageTask(**{
            "discord_configuration" : self._discord_configuration,
            "environment" : self._environment,
            "permissions_manager" : self._permissions_manager,
            "parent_logger" : self._logger,
            "preprocessed_message" : MessageProcessor.PreprocessedMessage(message)
        })
        process_message_task.run()
        reply = process_message_task.reply()
        if reply is not None:
            self._fireSendEventIfNeeded(reply, message.channel.id)
        
    def _fireSendEventIfNeeded(self, message, channel_id):
        if message is not None:
            params = {
                "channel_id" : channel_id,
                "message" : message
            }
            self._environment.fireEvent('send', **params)
        


        
        