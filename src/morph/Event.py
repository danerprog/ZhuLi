from . import EventConstants


class Event:
    
    CURRENT_ID_TO_USE = 0
    
    def __init__(self):
        self._event = {
            'id' : Event.CURRENT_ID_TO_USE,
            'type' : EventConstants.TYPES['invalid'],
            'origin' : {},
            'parameters' : {}
        }
        Event.CURRENT_ID_TO_USE += 1
        
    def __setitem__(self, key, value):
        if key in self._event:
            self._event[key] = value
            
    def __getitem__(self, key):
        item = None
        if key in self._event:
            item = self._event[key]
        return item
        
    def __str__(self):
        return str(self._event)