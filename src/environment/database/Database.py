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
            def count(self, filter):
                pass
                
            @abstractmethod
            def insert(self, item):
                pass
                
            @abstractmethod
            def remove(self, filter):
                pass
                
            @abstractmethod
            def query(self, filter):
                pass
                
            @abstractmethod
            def update(self, filter, updated_item):
                pass
        
    
    def __init__(self, main_slice, **params):
        self._logger = params["logger"]
        self._main_slice = main_slice
        self._logger.debug("initialized")

    def __getitem__(self, key):
        return self._main_slice[key]

    def count(self, filter):
        return self._main_slice.count(filter)

    def insert(self, item):
        return self._main_slice.insert(item)
        
    def remove(self, filter):
        return self._main_slice.remove(filter)
        
    def query(self, filter):
        return self._main_slice.query(filter)

    def update(self, filter, updated_item):
        return self._main_slice.update(filter, updated_item)