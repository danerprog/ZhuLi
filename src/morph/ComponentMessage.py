
class ComponentMessage:

    def __init__(self, logger):
        self._message = {
            'id' : 0,
            'status' : 0,
            'sender' : {},
            'target' : {},
            'args' : [],
            'kwargs' : {}
        }
        self._logger = logger.getChild(self.__class__.__name__)
        
    def __getitem__(self, key):
        item = None
        if key in self._message:
            item = self._message[key]
        else:
            self._logger.warning(f"Tried to access an unsupported message field '{key}'!")
        return item
        
    def __setitem__(self, key, value):
        if key in self_message:
            self._message[key] = value
        else:
            self._logger.warning(f"Tried to assign value to an unsupported message field '{key}'!")