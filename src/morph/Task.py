from abc import ABC, abstractmethod

class Task(ABC):
    class Arguments:
        def __init__(self, argument_string):
            self._argument_string = argument_string
            self._tokens = argument_string.split(" ")
            self._first_token = self.token(0)
            
        def raw(self):
            return self._argument_string
            
        def token(self, index):
            return None if self.token_count() <= index else self._tokens[index]
            
        def tokens(self):
            return None if self.token_count() <= 0 else self._tokens
            
        def token_count(self):
            return len(self._tokens)
   
        def command(self):
            return None if self._first_token is None else self._first_token[1:]
            
        def first_character(self):
            return None if self._first_token is None else self._first_token[0]
    
    def __init__(self, **context):
        self._context = context
        self._environment = self._context['environment']
        self._logger = self._context['parent_logger'].getChild(self.__class__.__name__)
        self._initializeArguments()
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
        
    def _initializeArguments(self, **context):
        if 'arguments' in context:
            self._arguments = context['arguments']
        elif 'argument_string' in context:
            self._arguments = Task.Arguments(context['argument_string'])
        else:
            self._arguments = Task.Arguments("")
            self._logger.warning("Important keys not initialized!")
