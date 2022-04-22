

class PermissionsManager:

    def __init__(self, permissions_database, logger):
        self._logger = logger
        self._database = permissions_database
        self._logger.info("initialized")
        
    def addEventPermissionsForGroup(self, event, id):
        self._logger.debug("addEventPermissionsForGroup called. event: {}, id: {}".format(
            event,
            str(id)
        ))
        self._database[event]['group'].insert(
            {'id' : id}
        )
        
    def doesGroupIdHavePermissionsForEvent(self, event, id):
        result = self._database[event]['group'].count(
            {'id' : id}
        )
        self._logger.debug("doesGroupIdHavePermissionsForEvent called. event: {}, id: {}, result: {}".format(
            event,
            str(id),
            str(result)
        ))
        return result > 0