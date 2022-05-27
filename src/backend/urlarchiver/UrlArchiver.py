from .ArchiveManager import ArchiveManager
from .tasks.ArchiveUrlTask import ArchiveUrlTask
from .tasks.SearchArchiveTask import SearchArchiveTask
from morph.MainComponent import MainComponent
from morph.processors.CommandMessageToTaskProcessor import CommandMessageToTaskProcessor


@CommandMessageToTaskProcessor({
    'archive' : ArchiveUrlTask,
    'search' : SearchArchiveTask
})
class UrlArchiver(MainComponent):
    def __init__(self):
        super().__init__()
        self._runtime_configuration = self._environment.getRuntimeConfiguration()
        self._runtime_configuration['command_set'].update(['archive'])
        self._ready_flags = {
            'is_component_fully_initialized' : False
        }
        self._logger.info(f"initialized. command_set: {self._runtime_configuration['command_set']}, ready_flags: {self._ready_flags}")
        
    def _onSetDatabase(self, database):
        super()._onSetDatabase(database)
        if not self._ready_flags['is_component_fully_initialized']:
            self._runtime_configuration['archive_manager'] = ArchiveManager(
                self._environment.database(),
                self._logger
            )
            self._ready_flags['is_component_fully_initialized'] = True
        self._logger.debug(f"_onSetDatabase called. ready_flags: {self._ready_flags}")
