from .tasks.ArchiveUrlTask import ArchiveUrlTask
from morph.MainComponent import MainComponent
from morph.processors.CommandMessageToTaskProcessor import CommandMessageToTaskProcessor


@CommandMessageToTaskProcessor({
    'archive' : ArchiveUrlTask
})
class UrlArchiver(MainComponent):
    def __init__(self):
        super().__init__()
        self._environment.getRuntimeConfiguration()['command_set'].update(['archive'])
