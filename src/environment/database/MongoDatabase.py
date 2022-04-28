from .Database import Database

from pymongo import MongoClient, CursorType


class MongoDatabase(Database):

    class Slice(Database.Slice):
        def __init__(self, database, logger):
            self._logger = logger
            self._database = database
            self._logger.debug("initialized")
            
        def __getitem__(self, key):
            return MongoDatabase.Slice(self._database[key], self._logger)
            
        def count(self, filter):
            return self._database.count_documents(filter)
            
        def insert(self, item):
            if isinstance(item, list):
                self._insertList(item)
            elif isinstance(item, dict):
                self._insertDictionary(item)
            else:
                self._logger.warning(f"Ignoring insert for unrecognized item type {type(item)}.")
                
        def remove(self, filter):
            self._database.delete_many(filter)
            
        def query(self, filter = None):
            query_result = []
            cursor = self._database.find(filter = filter, cursor_type = CursorType.EXHAUST)
            for document in cursor:
                query_result.append(document)
            return query_result
            
        def update(self, filter, updated_item):
            result = self._database.find_one_and_update(filter, updated_item)
            if result is None:
                self._logger.warning(f"no item found with filter: {filter}. update request ignored.")
                
        def _insertList(self, item_list):
            self._logger.debug(f"_insertList called. item: {item_list}")
            self._database.insert_many(item_list)
        
        def _insertDictionary(self, item):
            self._logger.debug(f"_insertDictionary called. item: {item}")
            self._database.insert_one(item)
        

    def __init__(self, **params):
        self._database = MongoClient('localhost', params["port"])
        super().__init__(
            MongoDatabase.Slice(self._database[params["name"]], params["logger"].getChild("Slice")), 
            **params)
        self._logger.debug("initialized")
