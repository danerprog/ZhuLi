

class PermissionsManager:

    def __init__(self, permissions_database, logger):
        self._logger = logger.getChild(self.__class__.__name__)
        self._database = permissions_database
        self._logger.info("initialized")
        
    def addEventPermissionsForRole(self, event, role_id, guild_id):
        self._logger.debug(f"addEventPermissionsForRole called. event: {event}, role_id: {role_id}, guild_id: {guild_id}")
        if not self._doesRoleIdExistInDatabase(role_id, guild_id):
            self._database[str(guild_id)]['roles'].insert({
                'id' : role_id,
                'permissions' : [event]
            })
        else:
            self._database[str(guild_id)]['roles'].update(
                {'id' : role_id},
                {'permissions' : [event]}
            )
        return True
            
    def removeEventPermissionsForRole(self, event, role_id, guild_id):
        self._logger.debug(f"removeEventPermissionsForRole called. event: {event}, role_id: {role_id}, guild_id: {guild_id}")
        result = False
        if self.doesRoleIdHavePermissionsForEvent(event, role_id, guild_id):
            self._database[str(guild_id)]['roles'].update(
                {'id' : role_id},
                fields_to_remove = {'permissions' : [event]}
            )
            result = True
        else:
            self._logger.debug(f"role {role_id} does not have permissions. ignoring request.")
        return result

    def doesRoleIdHavePermissionsForEvent(self, event, role_id, guild_id):
        result = self._isEventTriggerableByAUser(event)
        if result:
            count = self._database[str(guild_id)]['roles'].count({
                'id' : role_id,
                'permissions' : event
            })
            result = count > 0
        self._logger.debug(f"doesRoleIdHavePermissionsForEvent called. event: {event}, role_id: {role_id}, guild_id: {guild_id}, result: {result}")
        return result
        
    def getRolesWithEventPermissions(self, event, guild_id):
        self._logger.debug(f"getRolesWithEventPermissions called. event: {event}")
        return self._database[str(guild_id)]['roles'].query({'permissions': event})
        
    def addEventPermissionsForUser(self, event, user_id, guild_id):
        self._logger.debug(f"addEventPermissionsForUser called. event: {event}, user_id: {user_id}, guild_id: {guild_id}")
        if not self._doesUserIdExistInDatabase(user_id, guild_id):
            self._database[str(guild_id)]['users'].insert({
                'id' : user_id,
                'permissions' : [event]
            })
        else:
            self._database[str(guild_id)]['users'].update(
                {'id' : user_id},
                {'permissions' : [event]}
            )
        return True
            
    def removeEventPermissionsForUser(self, event, user_id, guild_id):
        self._logger.debug(f"removeEventPermissionsForUser called. event: {event}, user_id: {user_id}, guild_id: {guild_id}")
        result = False
        if self.doesUserIdHavePermissionsForEvent(event, user_id, guild_id):
            self._database[str(guild_id)]['users'].remove(
                {'id' : user_id},
                {'permissions' : [event]}
            )
            result = True
        else:
            self._logger.debug(f"user {user_id} does not have permissions. ignoring request.")
        return result
        
    def doesUserIdHavePermissionsForEvent(self, event, user_id, guild_id):
        result = self._isEventTriggerableByAUser(event)
        if result:
            count = self._database[str(guild_id)]['users'].count({
                'id' : user_id,
                'permissions' : event
            })
            result = count > 0
        self._logger.debug(f"doesUserIdHavePermissionsForEvent called. event: {event}, user_id: {user_id}, guild_id: {guild_id}, result: {result}")
        return result
        
    def getUsersWithEventPermissions(self, event, guild_id):
        self._logger.debug(f"getUsersWithEventPermissions called. event: {event}, guild_id: {guild_id}")
        return self._database[str(guild_id)]['users'].query({'permissions': event})
        
    def _isEventTriggerableByAUser(self, event):
        return event == "start" or event == "stop" or event == "restart" or event == "status" or event == "add" or event == "remove" or event == "list"
        
    def _doesRoleIdExistInDatabase(self, role_id, guild_id):
        return self._database[str(guild_id)]['roles'].count({'id': role_id}) > 0
        
    def _doesUserIdExistInDatabase(self, user_id, guild_id):
        return self._database[str(guild_id)]['users'].count({'id': user_id}) > 0
            