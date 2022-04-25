from abc import ABC, abstractmethod

class MessageTask(ABC):
    
    def __init__(self, **context):
        self._context = context
        self._initializeResultVariables()

    @abstractmethod
    def run(self):
        pass
        
    def isComplete(self):
        return self._is_complete
    
    def reply(self):
        return self._reply
        
    def result(self):
        return self._result
        
    def _initializeResultVariables(self):
        self._is_complete = False
        self._result = None
        self._reply = None
        
    def passResultsTo(self, task):
        task._is_complete = self._is_complete
        task._result = self._result
        task._reply = self._reply

