from abc import ABC


class Database:

    class Slice(ABC):
        def __init__(self, database, logger):
            def __init__(self, database, logger):
                self._logger = logger
                self._database = database
                self._logger.debug("initialized")
                
            @abstractmethod
            def __getitem__(self, key):
                pass
                
            @abstractmethod
            def count(self, mapping):
                pass
                
            @abstractmethod
            def insert(self, mapping):
                pass
        
    
    def __init__(self, main_slice, **params):
        self._logger = params["logger"]
        self._main_slice = main_slice
        self._logger.debug("initialized")

    def __getitem__(self, key):
        return self._main_slice[key]

    def count(self, mapping):
        return self._main_slice.count(mapping)

    def insert(self, mapping):
        return self._main_slice.insert(mapping)
