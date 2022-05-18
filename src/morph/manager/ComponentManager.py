from morph.messages.EventMessage import EventMessage

import asyncio
import traceback

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
                task = asyncio.create_task(component.processMessage(message))
                task.add_done_callback(self._printExceptionIfPossible)
        
    def fireEvent(self, event):
        self._logger.info(f"Event fired: event: {event}")
        for component in self._components:
            if isinstance(event, EventMessage):
                task = asyncio.create_task(component.processMessage(event))
            else:
                task = asyncio.create_task(component.processEvent(event))
            task.add_done_callback(self._printExceptionIfPossible)
            
    def _printExceptionIfPossible(self, task):
        exception_to_print = task.exception()
        if exception_to_print is not None:
            self._logger.error(self._stringifyException(exception_to_print))
            
    def _stringifyException(self, exception_to_stringify):
        opening_message = "Exception caught."
        exception_type = f"type: {type(exception_to_stringify)}"
        exception_message = f"message: {str(exception_to_stringify)}"
        stringified_traceback = "traceback: \n"
        for stringified_stack_frame in traceback.format_tb(exception_to_stringify.__traceback__):
            stringified_traceback = f"{stringified_traceback}>>> {stringified_stack_frame}"
        return "\n".join([opening_message, exception_type, exception_message, stringified_traceback])
        
            
            
    async def _processAndPrintExceptionIfPossible(self, payload, callback):
        await callback(payload)
        
        