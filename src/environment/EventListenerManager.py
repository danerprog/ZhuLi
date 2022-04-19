import asyncio

class EventListenerManager:

    class NoLogger:
        def debug(self, string):
            pass
            
        def info(self, string):
            pass

    INSTANCE = None
    
    def __init__(self):
        self._listeners = {}
        self._logger = EventListenerManager.NoLogger()
        
    def register(self, event, callback):
        self._logger.info("registered event '{}' with callback: {}".format(
            event,
            str(callback)
        ))
        self._createListenerListIfNeeded(event)
        self._listeners[event].append(callback)
        
    def fire(self, event, *args, **kwargs):
        self._logger.info("firing event '{}' with args: {}, kwargs: {}".format(
            event,
            str(args),
            str(kwargs)
        ))
        if self._doesEventHaveAList(event):
            for callback in self._listeners[event]:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(*args, **kwargs))
                else:
                    callback(*args, **kwargs)
                    
    def setLogger(self, logger):
        self._logger = logger

    def _createListenerListIfNeeded(self, event):
        if not self._doesEventHaveAList(event):
            self._listeners[event] = []
            
    def _doesEventHaveAList(self, event):
        return event in self._listeners
        
    def instance():
        if EventListenerManager.INSTANCE is None:
            EventListenerManager.INSTANCE = EventListenerManager()
        return EventListenerManager.INSTANCE