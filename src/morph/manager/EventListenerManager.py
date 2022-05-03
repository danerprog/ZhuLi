import asyncio

class EventListenerManager:
    
    def __init__(self, logger):
        self._listeners = {}
        self._logger = logger.getChild(self.__class__.__name__)
        
    def register(self, event, level, callback):
        self._logger.info(f"registered event '{event}' at level '{level}' with callback: {callback}")
        self._createListenerLevelIfNeeded(level)
        self._createListenerListIfNeeded(event, level)
        self._listeners[level][event].append(callback)
        
    def fire(self, event, level, *args, **kwargs):
        self._logger.info(f"firing event '{event}' at level '{level}' with args: {args}, kwargs: {kwargs}")
        if self._doesEventHaveALevel(level) and self._doesEventHaveAList(event, level):
            for callback in self._listeners[level][event]:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(*args, **kwargs))
                else:
                    callback(*args, **kwargs)
                    
    def getEventsOnLevel(self, level):
        events = []
        if level in self._listeners:
            events = self._listeners[level].keys()
        return events
        
    def getAllEvents(self):
        events = set()
        for level in self._listeners.keys():
            events.update(self.getEventsOnLevel(level))
        return events
                    
    def _createListenerLevelIfNeeded(self, level):
        if not self._doesEventHaveALevel(level):
            self._listeners[level] = {}

    def _createListenerListIfNeeded(self, event, level):
        if not self._doesEventHaveAList(event, level):
            self._listeners[level][event] = []
      
    def _doesEventHaveAList(self, event, level):
        return event in self._listeners[level]
        
    def _doesEventHaveALevel(self, level):
        return level in self._listeners
