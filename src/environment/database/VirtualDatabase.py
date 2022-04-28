from .Database import Database


class VirtualDatabase(Database):

    class Slice(Database.Slice):
        def __init__(self, database, logger):
            self._logger = logger
            self._database = database
            self._logger.debug("initialized")
        
        def __getitem__(self, key):
            if key not in self._database:
                self._database[key] = {}
            return VirtualDatabase.Slice(self._database[key], self._logger)
            
        def count(self, filter):
            count = 0
            for filter_key in filter.keys():
                self.logger._debug(f"counting instances of filter: {filter_key}, {filter[filter_key]}")
                for database_key in self._database.keys():
                    if filter_key == database_key and filter[filter_key] == self._database[database_key]:
                        count += 1
                        self.logger.debug(f"incrementing. count: {str(count)}")
            return count
            
        def insert(self, item):
            for key in item.keys():
                self._logger.debug(f"inserting key: {key}, value: {item[key]}")
                self.database[key] = item[key]
                
        def remove(self, filter):
            for key in filter.keys():
                if key in self._database and self._database[key] == filter[key]:
                    self._logger.debug(f"removing key: {key}, value: {filter[key]}")
                    self.database.pop(key)
                
        def query(self, filter):
            query_result = []
            for key in filter.keys():
                if key in self._database == filter[key]:
                    query_result.append({
                        key : self._database[key]
                    })
            return query_result

    def __init__(self, **params):
        name = params["name"]
        self._database = {name: {}}
        super().__init__(
            VirtualDatabase.Slice(self._database[name], params["logger"].getChild("Slice")), 
            **params)
        self._logger.debug("initialized")