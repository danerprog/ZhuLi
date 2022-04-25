from .MessageTask import MessageTask

class ShouldMessageBeProcessedTask(MessageTask):

    def __init__(self, **context):
        super().__init__(**context)
        self._logger = self._context['parent_logger'].getChild(__name__)
        self._initializeMemberVariables()
        self._logger.debug("initialized")
        
    def run(self):
        if self._isFirstTokenACommandForThisBot():
            if not self._doesSenderHavePermissionsToTriggerEvent():
                self._logger.info("no permissions found for sender")
                self._result = False
                self._reply = {
                    "title" : self._preprocessed_message.event(),
                    "description" :  f"You do not have permission to trigger '{self._preprocessed_message.event()}'" ,
                    "level" : "error",
                }
            else:
                self._logger.info("message can be processed")
                self._result = True
        self._is_complete = True

    def _initializeMemberVariables(self):
        self._preprocessed_message = self._context['preprocessed_message']
        self._first_token = self._preprocessed_message.token(0)
        self._raw_message = self._preprocessed_message.raw()  
        
    def _isFirstTokenACommandForThisBot(self):
        result = False
        if len(self._first_token) <= 0:
            self._logger.debug("message.content has a length of 0. ignoring message.")
        elif self._preprocessed_message.first_character() != self._context['discord_configuration']['commandcharacter']:
            self._logger.debug("first character of first token is not the command character. ignoring message.")
        else:
            result = True
            self._logger.debug("first character of first token is the command character. proceeding...")
        return result
        
    def _doesSenderHavePermissionsToTriggerEvent(self):
        self._logger.debug("checking permissions of sender as user...")
        result = self._doesSenderHavePermissionsAsAUser()
        if not result:
            self._logger.debug("no permissions as user. checking permissions of sender's top role...")
            result = self._doesSenderHavePermissionsAsARoleMember()
        return result
            
    def _doesSenderHavePermissionsAsAUser(self):
        event = self._preprocessed_message.event()
        result = None
        if self._context['permissions_manager'].doesUserIdHavePermissionsForEvent(event, self._raw_message.author.id):
            result = True
            self._logger.debug(f"user {self._raw_message.author.name}({self._raw_message.author.id}) has permissions as a user.")
        else:
            result = False
            self._logger.debug(f"user {self._raw_message.author.name}({self._raw_message.author.id}) has no permissions as a user.")
        return result
        
    def _doesSenderHavePermissionsAsARoleMember(self):
        event = self._preprocessed_message.event()
        result = None
        if self._context['permissions_manager'].doesGroupIdHavePermissionsForEvent(event, self._raw_message.author.top_role.id):
            result = True
            self._logger.debug(f"user has permissions as a member of top role {self._raw_message.author.top_role.name}({self._raw_message.author.top_role.id})")
        else:
            result = False
            self._logger.debug(f"user has no permissions as a member of top role {self._raw_message.author.top_role.name}({self._raw_message.author.top_role.id})")
        return result
