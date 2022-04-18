import asyncio

class EventListenerManager:

    INSTANCE = None
    
    def __init__(self):
        self._listeners = {}
        
    def register(self, event, callback):
        self._createListenerListIfNeeded(event)
        self._listeners[event].append(callback)
        
    def fire(self, event, *args, **kwargs):
        if self._doesEventHaveAList(event):
            for callback in self._listeners[event]:
                print(str(callback))
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(*args, **kwargs))
                else:
                    callback(*args, **kwargs)
        
    def _createListenerListIfNeeded(self, event):
        if not self._doesEventHaveAList(event):
            self._listeners[event] = []
            
    def _doesEventHaveAList(self, event):
        return event in self._listeners
        
    def instance():
        if EventListenerManager.INSTANCE is None:
            EventListenerManager.INSTANCE = EventListenerManager()
        return EventListenerManager.INSTANCE