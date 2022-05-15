from morph import EventConstants
from morph.MainComponent import MainComponent


class UrlArchiver(MainComponent):
    def __init__(self):
        super().__init__()
        self._environment.getRuntimeConfiguration()['command_set'].update(['archive'])

    async def processEvent(self, event):
        was_event_processed = await super().processEvent(event)
        if was_event_processed:
            self._continueProcessingEvent(received_message)
            
    def _continueProcessingEvent(self, event):
        if event['type'] == EventConstants.TYPES['user_input']:
            self._processUserInput(event['parameters'])
        
    def _processUserInput(self, parameters):
        command = None if 'command' not in parameters else parameters['command']
        if command == 'archive':
            pass
        else:
            self._logger.warning(f"Unrecognized command '{command}'! parameters: {parameters}")