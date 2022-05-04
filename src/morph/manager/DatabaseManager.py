
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
        from morph.database.MongoDatabase import MongoDatabase
        params['port'] = int(params['port'])
        params['logger'] = self._logger.getChild('MongoDatabase')
        self._database = MongoDatabase(**params)

    def get(self):
        return self._database