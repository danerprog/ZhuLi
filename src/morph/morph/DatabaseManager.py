import asyncio


class DatabaseManager:

    def __init__(self, logger, **database_configuration):
        self._logger = logger.getChild(self.__class__.__name__)
        self.setCallbackOnDatabaseOnline(self._doNothingCallback)
        self.setCallbackOnDatabaseOffline(self._doNothingCallback)
        self._was_database_online = False
        self._initializeDatabase(**database_configuration)
        asyncio.create_task(self._checkForDatabaseStatusAndRunAppropriateCallback())
        self._logger.info("initialized")
        
    def _initializeDatabase(self, **database_configuration):
        self._logger.debug("_initializeDatabase called. database_configuration: " + str(database_configuration))
        if database_configuration['program'] == 'mongo':
            self._initializeMongoDatabase(database_configuration)
        
    def _initializeMongoDatabase(self, params):
        self._logger.debug("_initializeMongoDatabase called. params: {}".format(str(params)))
        from .databases.MongoDatabase import MongoDatabase
        params['port'] = int(params['port'])
        params['logger'] = self._logger.getChild('MongoDatabase')
        self._database = MongoDatabase(**params)

    def get(self):
        return self._database
        
    def setCallbackOnDatabaseOnline(self, callback):
        self._onDatabaseOnline = callback
        
    def setCallbackOnDatabaseOffline(self, callback):
        self._onDatabaseOffline = callback

    async def _checkForDatabaseStatusAndRunAppropriateCallback(self):
        is_database_online = self._database.isOnline()
        if is_database_online and not self._was_database_online:
            self._onDatabaseOnline()
            self._was_database_online = is_database_online
            self._logger.info("Database online.")
        elif not is_database_online and self._was_database_online:
            self._onDatabaseOffline()
            self._was_database_online = is_database_online
            self._logger.info("Database offline.")
        await asyncio.sleep(5)
        asyncio.create_task(self._checkForDatabaseStatusAndRunAppropriateCallback())
        
    def _doNothingCallback(self):
        pass