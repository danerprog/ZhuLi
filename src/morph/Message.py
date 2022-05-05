
class Message:
    
    CURRENT_ID_TO_USE = 0
    
    def __init__(self):
        self._message = {
            'id' : Message.CURRENT_ID_TO_USE,
            'sender' : {},
            'target' : {},
            'parameters' : {}
        }
        Message.CURRENT_ID_TO_USE += 1
        
    def __setitem__(self, key, value):
        if key in self._message:
            self._message[key] = value
            
    def __getitem__(self, key):
        item = None
        if key in self._message:
            item = self._message[key]
        return item
        
    def __str__(self):
        return str(self._message)