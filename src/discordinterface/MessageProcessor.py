from .PermissionsManager import PermissionsManager
from environment.Environment import Environment


class MessageProcessor:

    class PreprocessedMessage:
        def __init__(self, message):
            self._tokens = message.content.split(" ")
            self._first_token = self._tokens[0]
            self._message = message
            
        def token(self, index):
            return None if len(self._tokens) <= index else self._tokens[index]
            
        def raw(self):
            return self._message

    def __init__(self, logger):
        self._logger = logger
        self._environment = Environment.instance()
        self._discord_configuration = self._environment.configuration()["main"]["Discord"]
        self._command_character = self._discord_configuration["commandcharacter"]
        self._permissions_manager = PermissionsManager(
            self._environment.database()['discordinterface']['permissions'],
            self._logger.getChild("PermissionsManager")
        )
        self._logger.debug("initialized. command_character: " + self._command_character)
        
    def process(self, message):
        self._logger.debug("process called")
        preprocessed_message = MessageProcessor.PreprocessedMessage(message)
        if self._shouldMessageBeProcessed(preprocessed_message):
            self._logger.debug("processing message")
            self._processMessage(preprocessed_message)
        else:
            self._logger.debug("ignoring message")
        
    def _shouldMessageBeProcessed(self, preprocessed_message):
        first_token = preprocessed_message.token(0)
        isFirstTokenACommandForThisBot = first_token[0] == self._command_character
        doesSenderHavePermissionsToTriggerEvent = self._doesSenderHavePermissionsToTriggerEvent(preprocessed_message)
        self._logger.debug("_shouldMessageBeProcessed called. isFirstTokenACommandForThisBot: {}, doesSenderHavePermissionsToTriggerEvent: {}".format(
            str(isFirstTokenACommandForThisBot),
            str(doesSenderHavePermissionsToTriggerEvent)
        ))
        return isFirstTokenACommandForThisBot and doesSenderHavePermissionsToTriggerEvent
        
    def _doesSenderHavePermissionsToTriggerEvent(self, preprocessed_message):
        event = preprocessed_message.token(0)[1:]
        raw_message = preprocessed_message.raw()
        user_id = raw_message.author.id
        top_role_id = raw_message.author.top_role.id
        isSenderTheOwner = user_id == int(self._discord_configuration["ownerid"])
        doesSenderHavePermissionsToTriggerEvent = self._permissions_manager.doesGroupIdHavePermissionsForEvent(event, top_role_id)
        self._logger.debug("_doesSenderHavePermissionsToTriggerEvent called. user_id: {}, top_role_id: {}, isSenderTheOwner: {}, doesSenderHavePermissionsToTriggerEvent: {}".format(
            str(user_id),
            str(top_role_id),
            str(isSenderTheOwner),
            str(doesSenderHavePermissionsToTriggerEvent)
        ))
        return isSenderTheOwner or doesSenderHavePermissionsToTriggerEvent
        
    def _processMessage(self, preprocessed_message):
        self._logger.debug("_processMessage called")
        
        event = preprocessed_message.token(0).replace(self._command_character, "", 1)
        kwargs = {
            "bot_name" : preprocessed_message.token(1),
            "channel_id" : str(preprocessed_message.raw().channel.id)
        }
        
        self._logger.info("firing event {}. kwargs: {}".format(
            event,
            str(kwargs)
        ))
        self._environment.fireEvent(event, **kwargs)
        
        