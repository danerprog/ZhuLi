
class AddEventProcessor:

    def __init__(self, **params):
        self._environment = params['environment']
        self._logger = params['logger']
        self._preprocessed_message = params['preprocessed_message']
        self._permissions_manager = params['permissions_manager']
        self._logger.debug("initialized")
        
        self._initializeEventArgs()
        self._processAddEventIfPossible()
        
    def _initializeEventArgs(self):
        self._subcommand = self._preprocessed_message.token(1)
        self._event_to_add_permissions = self._preprocessed_message.token(2)
        self._logger.debug(f"_initializeEventArgs called. subcommand: {self._subcommand}, event_to_add_permissions: {self._event_to_add_permissions}")

    def _processAddEventIfPossible(self):
        if self._subcommand is None:
            self._logger.info("tried to trigger add event with no subcommand. ignoring message.")
            self._triggerSendEvent(
                "Tried to add without subcommand! Usage: add <subcommand> <args>",
                "add",
                "error")
        elif self._subcommand == "permissions":
            self._processAddPermissionsEventIfPossible()
            
    def _processAddPermissionsEventIfPossible(self):
        if self._event_to_add_permissions is None:
            self._logger.info("tried to add permissions without providing event. ignoring message.")
            self._triggerSendEvent(
                "Tried to add permissions without providing command! Usage: add permissions <command_to_add_permissions> <mentions>",
                "add permissions",
                "error")
        else:
            self._processAddPermissionsEvent()
            
    def _processAddPermissionsEvent(self):
        raw_message = self._preprocessed_message.raw()
        wasAUserAdded = self._addPermissionsForUsers(raw_message.mentions)
        wasARoleAdded = self._addPermissionsForRoles(raw_message.role_mentions)
        if wasAUserAdded or wasARoleAdded:
            self._sendSuccessfullyAddedPermissionsMessage()
        else:
            self._sendNoPermissionsAddedMessage()
        
    def _addPermissionsForUsers(self, users):
        willAtLeastOneIdBeAdded = len(users) > 0
        self._logger.debug(f"_addPermissionsForUsers called. users: {users}")
        for user in users:
            id = user.id
            self._logger.debug(f"adding permissions for id: {id}, event_to_add_permissions: {self._event_to_add_permissions}")
            self._permissions_manager.addEventPermissionsForUser(self._event_to_add_permissions, id)
        return willAtLeastOneIdBeAdded
            
    def _addPermissionsForRoles(self, roles):
        willAtLeastOneIdBeAdded = len(roles) > 0
        self._logger.debug(f"_addPermissionsForRoles called. roles: {roles}")
        for role in roles:
            id = role.id
            self._logger.debug(f"adding permissions for id: {id}, event_to_add_permissions: {self._event_to_add_permissions}")
            self._permissions_manager.addEventPermissionsForGroup(self._event_to_add_permissions, id)
        return willAtLeastOneIdBeAdded
        
    def _sendNoPermissionsAddedMessage(self):
        message_to_send = f"No users or roles tagged!"
        self._logger.debug(f"{message_to_send} ignoring message.")
        send_params = {}
        send_params["channel_id"] = self._preprocessed_message.raw().channel.id
        send_params["message"] = {
            "title" : "add permissions",
            "description" : message_to_send,
            "level" : "warning"
        }
        self._environment.fireEvent("send", **send_params)

    def _sendSuccessfullyAddedPermissionsMessage(self):
        send_params = {}
        send_params["channel_id"] = self._preprocessed_message.raw().channel.id
        send_params["message"] = {
            "title" : f"add {self._event_to_add_permissions}",
            "description" : f"Successfully added '{self._event_to_add_permissions}' permissions",
            "level" : "info"
        }
        fields = []
        added_users_string = self._getAddedUsersInString()
        if added_users_string != "":
            fields.append({
                "name" : "Users",
                "value" : added_users_string,
                "inline" : True
            })
        added_roles_string = self._getAddedRolesInString()
        if added_roles_string != "":
            fields.append({
                "name" : "Roles",
                "value" : added_roles_string,
                "inline" : True
            })
        send_params["message"]["fields"] = fields
        self._environment.fireEvent("send", **send_params)
        
    def _getAddedUsersInString(self):
        added_users_string = ""
        raw_message = self._preprocessed_message.raw()
        for user in raw_message.mentions:
            added_users_string += f"{user.name}\n"
        return added_users_string
        
    def _getAddedRolesInString(self):
        added_roles_string = ""
        raw_message = self._preprocessed_message.raw()
        for role in raw_message.role_mentions:
            added_roles_string += f"{role.name}\n"
        return added_roles_string
        
        