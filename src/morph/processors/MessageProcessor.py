from morph.messages.Message import Message

import asyncio


class MessageProcessor:

    async def processMessage(self, message):
        self._logger.debug(f"Processing message: {message}")
        message_to_pass = None
        if isinstance(message, Message):
            message_to_pass = message
        else:
            self._logger.warning(f"Received message is not an instance of {Message.__name__}.")
        return message_to_pass