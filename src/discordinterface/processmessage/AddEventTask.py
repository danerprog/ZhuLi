from .MessageTask import MessageTask
from .ModifyPermissionsTask import ModifyPermissionsTask


class AddEventTask(MessageTask):
    
    def __init__(self, **context):
        super().__init__(**context)
        self._initializeMemberVariables()
        self._logger.debug("initialized")
        
    async def run(self):
        if self._subcommand is None:
            self._setErrorReply("Tried to add without subcommand! Usage: add <subcommand> <args>")
        elif self._subcommand == "permissions":
            modify_permissions_task = ModifyPermissionsTask(
                modify_type = "add",
                **self._context
            )
            await modify_permissions_task.run()
            modify_permissions_task.passResultsTo(self)
        else:
            self._setErrorReply(f"Unsupported subcommand '{self._subcommand}'!")

        
    def _initializeMemberVariables(self):
        self._preprocessed_message = self._context['preprocessed_message']
        self._raw_message = self._preprocessed_message.raw()
        self._subcommand = self._preprocessed_message.token(1)
    
    def _setErrorReply(self, message):
        self._logger.debug(f"_setErrorReply called. message: {message}")
        self._reply = {
            "title" : "add",
            "description" : message,
            "level" : "error",
            "fields" : [{
                "name" : "Supported subcommands",
                "value" : self._getSupportedSubcommandsString(),
                "inline" : True
            }]
        }
        
    def _getSupportedSubcommandsString(self):
        return "permissions"
        
    


