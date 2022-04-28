


class DataManager:

    def __init__(self, database, logger):
        self._database = database
        self._logger = logger.getChild(__name__)
        self._logger.debug("initialized")
        
    def insertUser(self, user, guild_id):
        guild_id = str(guild_id)
        user_database = self._database[guild_id]['users']
        document = {
            "id" : user.id,
            "name" : user.name,
            "display_name" : user.display_name,
            "tag" : user.discriminator,
            "permissions" : []
        }
        if user_database.count({'id' : user.id}) <= 0:
            self._logger.debug("no document found. inserting info.")
            user_database.insert(document)
        else:
            self._logger.debug("document found. updating info.")
            user_database.update({'id' : user.id}, document)
  
    def getUser(self, user_id, guild_id):
        guild_id = str(guild_id)
        user = None
        query_result = self._database[guild_id]['users'].query({'id' : user_id})
        if len(query_result) > 0:
            user = query_result[0]
        if len(query_result) > 1:
            self._logger.warning(f"query returned more than one user with the same id! query_result: {query_result}")
        return user

    def insertRole(self, role, guild_id):
        pass
        