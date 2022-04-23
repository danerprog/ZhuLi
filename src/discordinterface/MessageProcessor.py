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

    def __init__(self, permissions_manager, logger):
        self._permissions_manager = permissions_manager
        self._logger = logger
        self._environment = Environment.instance()
        self._discord_configuration = self._environment.configuration()["main"]["Discord"]
        self._command_character = self._discord_configuration["commandcharacter"]
        self._logger.debug("initialized. command_character: " + self._command_character)
        
    def process(self, message):
        self._logger.debug("process called. message.content: " + message.content)
        preprocessed_message = MessageProcessor.PreprocessedMessage(message)
        if self._shouldMessageBeProcessed(preprocessed_message):
            self._logger.debug("processing message")
            self._processMessage(preprocessed_message)
        else:
            self._logger.debug("ignoring message")
        
    def _shouldMessageBeProcessed(self, preprocessed_message):
        result = False
        first_token = preprocessed_message.token(0)
        debug_message = "_shouldMessageBeProcessed called. "
        isFirstTokenACommandForThisBot = False if len(first_token) <= 0 else first_token[0] == self._command_character
        debug_message += f", isFirstTokenACommandForThisBot: {isFirstTokenACommandForThisBot} "
        if isFirstTokenACommandForThisBot:
            doesSenderHavePermissionsToTriggerEvent = False if first_token is None else self._doesSenderHavePermissionsToTriggerEvent(preprocessed_message)
            debug_message += f"doesSenderHavePermissionsToTriggerEvent: {doesSenderHavePermissionsToTriggerEvent} "
            result = doesSenderHavePermissionsToTriggerEvent
        self._logger.debug(debug_message)
        return result
        
    def _doesSenderHavePermissionsToTriggerEvent(self, preprocessed_message):
        event = preprocessed_message.token(0)[1:]
        raw_message = preprocessed_message.raw()
        doesSenderHavePermissionsToTriggerEventAsAUser = self._permissions_manager.doesUserIdHavePermissionsForEvent(event, raw_message.author.id)
        doesSenderHavePermissionsToTriggerEventAsAGroupMember = self._permissions_manager.doesGroupIdHavePermissionsForEvent(event, raw_message.author.top_role.id)
        self._logger.debug(f"_doesSenderHavePermissionsToTriggerEvent called. " + 
            f"event: {event}, " + 
            f"raw_message: {raw_message}, " +
            f"doesSenderHavePermissionsToTriggerEventAsAUser: {doesSenderHavePermissionsToTriggerEventAsAUser}, " +
            f"doesSenderHavePermissionsToTriggerEventAsAGroupMember: {doesSenderHavePermissionsToTriggerEventAsAGroupMember}")
        return doesSenderHavePermissionsToTriggerEventAsAUser or doesSenderHavePermissionsToTriggerEventAsAGroupMember
  
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
        
        