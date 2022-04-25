from .AddEventTask import AddEventTask
from .MessageTask import MessageTask
from .ShouldMessageBeProcessedTask import ShouldMessageBeProcessedTask


class ProcessMessageTask(MessageTask):
    def __init__(self, **context):
        super().__init__(**context)
        self._logger = self._context['parent_logger'].getChild(__name__)
        self._logger.debug("initialized")
        
    def run(self):
        self._logger.debug("running")
        should_message_be_processed_task = ShouldMessageBeProcessedTask(**self._context)
        should_message_be_processed_task.run()
        if should_message_be_processed_task.result():
            self._processMessage()
        else:
            should_message_be_processed_task.passResultsTo(self)
            self._is_complete = True

    def _processMessage(self):
        event = self._context['preprocessed_message'].event()
        if event == "add":
            add_event_task = AddEventTask(**self._context)
            add_event_task.run()
            add_event_task.passResultsTo(self)
        else:
            self._is_complete = True
            self._reply = None
            self._fireEvent(event)
            
            
    def _fireEvent(self, event):
        self._logger.info(f"firing '{event}'.")
        kwargs = {
            "bot_name" : self._context['preprocessed_message'].token(1),
            "channel_id" : self._context['preprocessed_message'].raw().channel.id
        }
        self._context['environment'].fireEvent(event, **kwargs)
