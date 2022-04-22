from .database.MongoDatabase import MongoDatabase


class DatabaseManager:

    def __init__(self, logger, **kwargs):
        self._logger = logger
        self._initializeDatabase(**kwargs)
        self._logger.info("initialized")
        
    def _initializeDatabase(self, **kwargs):
        self._logger.debug("_initializeDatabase called. kwargs: " + str(kwargs))
        if 'mongo' in kwargs:
            self._initializeMongoDatabase(kwargs['mongo'])
        
    def _initializeMongoDatabase(self, params):
        self._database = MongoDatabase(
            params['name'],
            params['port'],
            self._logger.getChild('MongoDatabase')
        )
        
    def get(self):
        return self._database