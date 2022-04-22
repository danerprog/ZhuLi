from pymongo import MongoClient


class MongoDatabase:

    class Slice:
        def __init__(self, database, logger):
            self._logger = logger
            self._database = database
            self._logger.debug("initialized")
            
        def __getitem__(self, key):
            return MongoDatabase.Slice(self._database[key], self._logger)
            
        def count(self, mapping):
            return self._database.count_documents(mapping)
            
        def insert(self, mapping):
            if isinstance(mapping, list):
                self._insertList(mapping)
            elif isinstance(mapping, dict):
                self._insertDictionary(mapping)
            else:
                self._logger.warning("Ignoring insert for unrecognized mapping type {}.".format(
                    str(type(mapping))
                ))
                
        def _insertList(self, value):
            self._logger.debug("_insertList called. value: " + str(value))
            self._database.insert_many(value)
        
        def _insertDictionary(self, value):
            self._logger.debug("_insertDictionary called. value: " + str(value))
            self._database.insert_one(value)
        

    def __init__(self, name, port, logger):
        self._logger = logger
        self._database = MongoClient('localhost', 27107 if port == 27107 else 27108)
        self._main_slice = MongoDatabase.Slice(self._database[name], self._logger.getChild("Slice"))
        self._logger.debug("initialized")

    def __getitem__(self, key):
        return self._main_slice[key]
        
    def count(self, mapping):
        return self._main_slice.count(mapping)
        
    def insert(self, mapping):
        return self._main_slice.insert(mapping)


        
        