from .Message import Message


class EventMessage(Message):

    TYPE = {
        'user_input' : "user_input",
        'components_loaded' : "components_loaded",
        'shutdown' : "shutdown",
        'restart' : "restart",
        'database_status' : "database_status",
        'invalid' : "invalid"
    }
    
    def __init__(self):
        super().__init__()
        self._message.pop('target')
        self.setEventType(EventMessage.TYPE['invalid'])
        
    def setEventType(self, type):
        if type in EventMessage.TYPE:
            self.setParameter('event_type', type)
        
    def getEventType(self):
        return self.getParameter('event_type')
        

class DatabaseStatusEvent(EventMessage):

    STATUS = {
        'online' : "online",
        'offline' : "offline",
        'invalid' : "invalid"
    }

    def __init__(self):
        super().__init__()
        self.setEventType(EventMessage.TYPE['database_status'])
        self.setStatus(DatabaseStatusEvent.STATUS['invalid'])
        
    def setStatus(self, status):
        if status in DatabaseStatusEvent.STATUS:
            self.setParameter('status', status)
            
    def setStatusToOnline(self):
        self.setStatus(DatabaseStatusEvent.STATUS['online'])
        
    def setStatusToOffline(self):
        self.setStatus(DatabaseStatusEvent.STATUS['offline'])
            
    def getStatus(self):
        return self.getParameter('status')