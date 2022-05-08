from .MessageTask import MessageTask


class ModifyPermissionsTask(MessageTask):
    
    def __init__(self, modify_type = None, **context):
        super().__init__(**context)
        self._modify_type = modify_type
        self._set_of_possible_commands = context['environment'].getRuntimeConfiguration()['command_set']
        self._initializeMemberVariables()
        self._initializePermissionModifiers()
        self._logger.debug("initialized")
        
    async def run(self):
        if self._modify_type == "add" or self._modify_type == "remove":
            self._modifyPermissionsIfPossible()
        else:
            self._reply = {
                "title" : self._getMessageTitle(),
                "description" : f"Cannot '{self._modify_type}' permissions!",
                "level" : "error"
            }
            self._logger.warning(f"unknown modify_type: {self._modify_type}")
        self._is_complete = True
            
    def _initializeMemberVariables(self):
        self._preprocessed_message = self._context['preprocessed_message']
        self._permissions_manager = self._context['permissions_manager']
        self._raw_message = self._preprocessed_message.raw()
        self._subcommand = self._preprocessed_message.token(1)
        self._command_to_modify_permissions = self._preprocessed_message.token(2)
        self._guild_id = self._raw_message.guild.id
        
    def _initializePermissionModifiers(self):
        if self._modify_type == "add":
            self._modifyPermissionsForUser = self._permissions_manager.addEventPermissionsForUser
            self._modifyPermissionsForRole = self._permissions_manager.addEventPermissionsForRole
        elif self._modify_type == "remove":
            self._modifyPermissionsForUser = self._permissions_manager.removeEventPermissionsForUser
            self._modifyPermissionsForRole = self._permissions_manager.removeEventPermissionsForRole
        else:
            self._logger.warning(f"no permission modifiers set for modify_type: {self._modify_type}!")
            
    def _modifyPermissionsIfPossible(self):
        if self._command_to_modify_permissions is None:
            self._reply = {
                "title" : self._getMessageTitle(),
                "description" : f"Tried to {self._modify_type} permissions without providing command! " + 
                    f"Usage: {self._modify_type} permissions <command_to_add_permissions> <mentions>",
                "level" : "error"
            }
            self._logger.debug("no command to modify permissions. ignoring message.")
        elif self._command_to_modify_permissions not in self._set_of_possible_commands:
            self._reply = {
                "title" : self._getMessageTitle(),
                "description" : f"Tried to {self._modify_type} permissions for an unsupported command {self._command_to_modify_permissions}!",
                "level" : "error"
            }
            self._logger.debug("unsupported command {self._command_to_modify_permissions}. ignoring message.")
        else:
            self._modifyPermissions()

    def _modifyPermissions(self):
        raw_message = self._preprocessed_message.raw()
        affected_users = self._modifyPermissionsForUsers(raw_message.mentions)
        affected_roles = self._modifyPermissionsForRoles(raw_message.role_mentions)
        self._generateResults(affected_users, affected_roles) 

    def _modifyPermissionsForUsers(self, users):
        affected_users = []
        self._logger.debug(f"_modifyPermissionsForUsers called. users: {users}, modify_type: {self._modify_type}")
        for user in users:
            id = user.id
            self._logger.debug(f"modifying permissions for id: {id}, event: {self._command_to_modify_permissions}")
            if self._modifyPermissionsForUser(self._command_to_modify_permissions, id, self._guild_id):
                affected_users.append(user.name)
        return affected_users
            
    def _modifyPermissionsForRoles(self, roles):
        affected_roles = []
        self._logger.debug(f"_modifyPermissionsForRoles called. roles: {roles}, modify_type: {self._modify_type}")
        for role in roles:
            id = role.id
            self._logger.debug(f"modifying permissions for id: {id}, event: {self._command_to_modify_permissions}")
            if self._modifyPermissionsForRole(self._command_to_modify_permissions, id, self._guild_id):
                affected_roles.append(role.name)
        return affected_roles
        
    def _generateResults(self, affected_users, affected_roles):
        if len(affected_users) == 0 and len(affected_roles) == 0:
            self._reply = {
                "title" : self._getMessageTitle(),
                "description" : "No users or roles mentioned! " +
                    f"Usage: {self._modify_type} permissions <command_to_add_permissions> <mentions>",
                "level" : "error"
            }
        else:
            self._reply = {
                "title" : self._getMessageTitle(),
                "description" : f"{self._modify_type} permissions for command '{self._command_to_modify_permissions}' successful!",
                "level" : "info",
                "fields" : []
            }
            if len(affected_users) > 0:
                self._reply["fields"].append({
                    "name" : "Users",
                    "value" : "\n".join(affected_users),
                    "inline" : True
                })
            if len(affected_roles) > 0:
                self._reply["fields"].append({
                    "name" : "Users",
                    "value" : "\n".join(affected_roles),
                    "inline" : True
                })
       
    def _getMessageTitle(self):
        return f"{self._modify_type} permissions"
        