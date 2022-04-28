from .ListPermissionsTask import ListPermissionsTask
from .MessageTask import MessageTask


class ListEventTask(MessageTask):
    
    def __init__(self, **context):
        super().__init__(**context)
        self._initializeMemberVariables()
        self._logger.debug("initialized")
        
    async def run(self):
        if self._subcommand is None:
            self._setErrorReply("No subcommand provided. Usage: list <subcommand> <args>")
        elif self._subcommand == "permissions" :
            await self._listPermissions()
        else:
            self._setErrorReply(f"Subcommand '{self._subcommand}' not supported.")
        
    def _initializeMemberVariables(self):
        self._subcommand = self._context['preprocessed_message'].token(1)
        
    async def _listPermissions(self):
        list_permissions_task = ListPermissionsTask(**self._context)
        await list_permissions_task.run()
        list_permissions_task.passResultsTo(self)
        
    def _setErrorReply(self, message):
        self._logger.debug(f"_setErrorReply called. message: {message}")
        self._reply = {
            "title" : "list",
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