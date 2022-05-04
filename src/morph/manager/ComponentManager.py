import asyncio


class ComponentManager:

    def __init__(self, logger):
        self._logger = logger.getChild(self.__class__.__name__)
        self._components = []
        self._logger.info("initialized.")
        
    def register(self, component):
        from morph.MainComponent import MainComponent
        if isinstance(component, MainComponent):
            self._components.append(component)
            self._logger.info(f"Registered component: {component}")
        else:
            self._logger.warning(f"Attempted to register an object that is not a MainComponent! type: {type(component)}")
    
    def sendMessage(self, message):
        self._logger.info(f"Message sent. message: {message}")
        for component in self._components:
            if component == message['target']:
                asyncio.create_task(component.processMessage(message))
        
    def fireEvent(self, event):
        self._logger.info(f"Event fired: event: {event}")
        for component in self._components:
            asyncio.create_task(component.processEvent(event))
        