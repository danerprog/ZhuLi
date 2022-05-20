from morph.messages.Message import Message

import asyncio


class MessageProcessor:

    def __init__(self, logger):
        self._parent_logger = logger
        self._logger = self._parent_logger.getChild(self.__class__.__name__)
        self._message_processors = []

    async def processMessage(self, message):
        self._logger.debug(f"Processing message: {message}")
        message_to_pass = None
        if isinstance(message, Message):
            self._passMessageToProcessors(message)
            message_to_pass = message
        else:
            self._logger.warning(f"Received message is not an instance of {Message.__name__}.")
        return message_to_pass
        
    def addMessageProcessor(self, message_processor):
        if isinstance(message_processor, MessageProcessor):
            self._message_processors.append(message_processor)
            self._logger.info(f"message processor added. message_processor: {message_processor}")
        else:
            self._logger.warning(f"attempted to add a non-MessageProcessor object. type: {type(message_processor)}")
            
    def _passMessageToProcessors(self, message):
        self._logger.debug(f"passing message to processors. message_processors: {self._message_processors}")
        for message_processor in self._message_processors:
            self._logger.debug(f"passing to processor: {message_processor}")
            asyncio.create_task(message_processor.processMessage(message))