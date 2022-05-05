

class PermissionsManager:

    def __init__(self, environment, logger):
        self._logger = logger.getChild(self.__class__.__name__)
        self._environment = environment
        self._database = self._environment.database()['discordinterface']
        self._list_of_possible_events = ['start', 'stop', 'restart', 'status', 'add', 'remove', 'list']
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
        
    def addUserAsOwner(self, user_id):
        if not self.isUserAnOwner(user_id):
            self._database['owner']['users'].insert({
                'id' : user_id
            })
            self._logger.info(f"user {user_id} is added as an owner.")
        
    def removeOwners(self):
        owners = self._database['owner']['users'].query()
        for owner in owners:
            self._database['owner']['users'].remove({
                'id' : owner['id']
            })
            self._logger.info(f"user {owner['id']} is removed as an owner")
            
    def isUserAnOwner(self, user_id):
        return self._doesUserIdExistInDatabase(user_id, 'owner')
        
    def _isEventTriggerableByAUser(self, event):
        return event in self._list_of_possible_events
        
    def _doesRoleIdExistInDatabase(self, role_id, guild_id):
        return self._database[str(guild_id)]['roles'].count({'id': role_id}) > 0
        
    def _doesUserIdExistInDatabase(self, user_id, guild_id):
        return self._database[str(guild_id)]['users'].count({'id': user_id}) > 0
            