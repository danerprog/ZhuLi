from .MessageTask import MessageTask
from .ModifyPermissionsTask import ModifyPermissionsTask


class RemoveEventTask(MessageTask):
    
    def __init__(self, **context):
        super().__init__(**context)
        self._logger = self._context['parent_logger'].getChild(__name__)
        self._initializeMemberVariables()
        self._logger.debug("initialized")
        
    def run(self):
        if self._subcommand is None:
            self._reply = {
                "title" : "remove",
                "description" : "Tried to add without subcommand! Usage: remove <subcommand> <args>",
                "level" : "error"
            }
            self._logger.info("tried to trigger remove event with no subcommand.")
        elif self._subcommand == "permissions":
            modify_permissions_task = ModifyPermissionsTask(
                modify_type = "remove",
                **self._context
            )
            modify_permissions_task.run()
            modify_permissions_task.passResultsTo(self)
        else:
            self._reply = {
                "title" : "remove",
                "description" : f"Unsupported subcommand '{self._subcommand}'!",
                "level" : "error",
                "fields" : [{
                    "name" : "Supported subcommands:",
                    "value" : "permissions",
                    "inline" : True
                }]
            }
        self._is_complete = True
        
    def _initializeMemberVariables(self):
        self._preprocessed_message = self._context['preprocessed_message']
        self._raw_message = self._preprocessed_message.raw()
        self._subcommand = self._preprocessed_message.token(1)


