from abc import ABC, abstractmethod

class MessageTask(ABC):
    
    def __init__(self, **context):
        self._context = context
        self._logger = self._context['parent_logger'].getChild(self.__class__.__name__)
        self._initializeResultVariables()

    @abstractmethod
    async def run(self):
        pass
    
    def reply(self):
        return self._reply
        
    def result(self):
        return self._result

    def _initializeResultVariables(self):
        self._result = None
        self._reply = None
        
    def passResultsTo(self, task):
        task._result = self._result
        task._reply = self._reply

