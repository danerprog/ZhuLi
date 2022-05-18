from .Message import Message


class CommandMessage(Message):
    
    def __init__(self):
        super().__init__()
        self.setCommand("")
        
    def setCommand(self, command):
        self.setParameter('command', command)
        
    def getCommand(self):
        return self.getParameter('command')