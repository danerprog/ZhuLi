from .Database import Database

import pymongo


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
                
        def remove(self, filter, fields_to_remove = None):
            self._logger.debug(f"remove called. filter: {filter}, fields_to_remove: {fields_to_remove}")
            if fields_to_remove is None:
                self._logger.debug("deleting all items matching filter.")
                self._database.delete_many(filter)
            else:
                self._logger.debug("removing indicated fields of documents matching the filter.")
                self._database.update_one(filter, self._getRemoveOperationForItem(fields_to_remove))
            
        def query(self, filter = None):
            query_result = []
            cursor = self._database.find(filter = filter, cursor_type = pymongo.CursorType.EXHAUST)
            for document in cursor:
                query_result.append(document)
            return query_result
            
        def update(self, filter, item):
            self._logger.debug(f"update called. filter: {filter}, item: {item}")
            result = self._database.update_one(filter, self._getAddOperationForItem(item))
            if result is None:
                self._logger.warning(f"no item found with filter: {filter}. update request ignored.")
  
        def _insertList(self, item_list):
            self._logger.debug(f"_insertList called. item: {item_list}")
            self._database.insert_many(item_list)
        
        def _insertDictionary(self, item):
            self._logger.debug(f"_insertDictionary called. item: {item}")
            self._database.insert_one(item)
            
        def _getAddOperationForItem(self, item):
            self._logger.debug(f"_getAddOperationForItem called. item: {item}")
            operation = {}
            for key, value in item.items():
                if isinstance(value, list):
                    operation['$addToSet'] = {key: {'$each' : value}}
                else:
                    operation['$set'] = {key: value}
            self._logger.debug(f"_getAddOperationForItem done. operation: {operation}")
            return operation
            
        def _getRemoveOperationForItem(self, item):
            self._logger.debug(f"_getRemoveOperationForItem called. item: {item}")
            operation = {}
            for key, value in item.items():
                if isinstance(value, list):
                    operation['$pullAll'] = {key: value}
                else:
                    operation['$pop'] = {key: value}
            self._logger.debug(f"_getRemoveOperationForItem done. operation: {operation}")
            return operation

    def __init__(self, **params):
        self._database = pymongo.MongoClient('localhost', params["port"], serverSelectionTimeoutMS = 1000)
        super().__init__(
            MongoDatabase.Slice(self._database[params["name"]], params["logger"].getChild("Slice")), 
            **params)
        self._logger.debug("initialized")
        
    def isOnline(self):
        is_online = True
        try:
            self._database.admin.command('ping')
        except pymongo.errors.ServerSelectionTimeoutError:
            is_online = False
        return is_online
            
