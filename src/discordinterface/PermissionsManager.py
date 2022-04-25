

class PermissionsManager:

    def __init__(self, permissions_database, logger):
        self._logger = logger
        self._database = permissions_database
        self._logger.info("initialized")
        
    def addEventPermissionsForGroup(self, event, id):
        self._logger.debug(f"addEventPermissionsForGroup called. event: {event}, id: {id}")
        if not self.doesGroupIdHavePermissionsForEvent(event, id):
            self._database[event]['group'].insert({'id' : id})
        else:
            self._logger.debug(f"group {id} already has permissions. ignoring request.")
            
    def removeEventPermissionsForGroup(self, event, id):
        self._logger.debug(f"addEventPermissionsForGroup called. event: {event}, id: {id}")
        if self.doesGroupIdHavePermissionsForEvent(event, id):
            self._database[event]['group'].remove({'id' : id})
        else:
            self._logger.debug(f"group {id} does not have permissions. ignoring request.")
        
    def doesGroupIdHavePermissionsForEvent(self, event, id):
        result = self._isEventTriggerableByAUser(event)
        if result:
            count = self._database[event]['group'].count({'id' : id})
            result = count > 0
        self._logger.debug(f"doesGroupIdHavePermissionsForEvent called. event: {event}, id: {id}, result: {result}")
        return result
        
    def addEventPermissionsForUser(self, event, id):
        self._logger.debug(f"addEventPermissionsForUser called. event: {event}, id: {id}")
        if not self.doesUserIdHavePermissionsForEvent(event, id):
            self._database[event]['user'].insert({'id' : id})
        else:
            self._logger.debug(f"user {id} already has permissions. ignoring request.")
            
    def removeEventPermissionsForUser(self, event, id):
        self._logger.debug(f"removeEventPermissionsForUser called. event: {event}, id: {id}")
        if self.doesUserIdHavePermissionsForEvent(event, id):
            self._database[event]['user'].remove({'id' : id})
        else:
            self._logger.debug(f"user {id} does not have permissions. ignoring request.")

    def doesUserIdHavePermissionsForEvent(self, event, id):
        result = self._isEventTriggerableByAUser(event)
        if result:
            self._logger.debug("event is triggerable by user. checking permissions database.")
            count = self._database[event]['user'].count({'id' : id})
            result = count > 0
        self._logger.debug(f"doesUserIdHavePermissionsForEvent called. event: {event}, id: {id}, result: {result}")
        return result
        
    def _isEventTriggerableByAUser(self, event):
        return event == "start" or event == "stop" or event == "restart" or event == "status" or event == "add" or event == "remove"