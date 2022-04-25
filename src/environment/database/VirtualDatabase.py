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
            
        def count(self, mapping):
            count = 0
            for mapping_key in mapping.keys():
                self.logger._debug(f"counting instances of mapping: {mapping_key}, {mapping[mapping_key]}")
                for database_key in self._database.keys():
                    if mapping_key == database_key and mapping[mapping_key] == self._database[database_key]:
                        count += 1
                        self.logger.debug(f"incrementing. count: {str(count)}")
            return count
            
        def insert(self, mapping):
            for key in mapping.keys():
                self._logger.debug(f"inserting key: {key}, value: {mapping[key]}")
                self.database[key] = mapping[key]
                
        def remove(self, mapping):
            for key in mapping.keys():
                self._logger.debug(f"removing key: {key}, value: {mapping[key]}")
                self.database.pop(key)

    def __init__(self, **params):
        name = params["name"]
        self._database = {name: {}}
        super().__init__(
            VirtualDatabase.Slice(self._database[name], params["logger"].getChild("Slice")), 
            **params)
        self._logger.debug("initialized")