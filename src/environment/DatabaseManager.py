
class DatabaseManager:

    def __init__(self, logger, **database_configuration):
        self._logger = logger
        self._initializeDatabase(**database_configuration)
        self._logger.info("initialized")
        
    def _initializeDatabase(self, **database_configuration):
        self._logger.debug("_initializeDatabase called. database_configuration: " + str(database_configuration))
        if database_configuration['program'] == 'mongo':
            self._initializeMongoDatabase(database_configuration)
        
    def _initializeMongoDatabase(self, params):
        self._logger.debug("_initializeMongoDatabase called. params: {}".format(str(params)))
        from .database.MongoDatabase import MongoDatabase
        self._database = MongoDatabase(
            params['name'],
            int(params['port']),
            self._logger.getChild('MongoDatabase')
        )

    def get(self):
        return self._database