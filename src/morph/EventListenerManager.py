import asyncio

class EventListenerManager:
    
    def __init__(self, logger):
        self._listeners = {}
        self._logger = logger.getChild(self.__class__.__name__)
        
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

    def _createListenerListIfNeeded(self, event):
        if not self._doesEventHaveAList(event):
            self._listeners[event] = []
            
    def _doesEventHaveAList(self, event):
        return event in self._listeners
