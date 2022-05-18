
class Message:
    
    CURRENT_ID_TO_USE = 0
    FLAG = {
        'use_session' : 'use_session'
    }

    def __init__(self):
        self._message = {
            'id' : Message.CURRENT_ID_TO_USE,
            'sender' : {},
            'target' : {},
            'parameters' : {},
            'flags' : set()
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
        
    def addFlag(self, flag):
        if flag in Message.FLAG:
            self._message['flags'].update(Message.FLAG[flag])

    def removeFlag(self, flag):
        self._message['flags'].discard(flag)
        
    def setParameter(self, key, value):
        self._message['parameters'][key] = value
        
    def getParameter(self, key):
        value = None
        if key in self._message['parameters']:
            value = self._message['parameters'][key]
        return value