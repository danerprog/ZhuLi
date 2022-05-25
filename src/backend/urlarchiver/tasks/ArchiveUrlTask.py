from morph.tasks.Task import Task

import aiohttp


class ArchiveUrlTask(Task):

    def __init__(self, **context):
        super().__init__(**context)
        self._url_to_archive = self._arguments.token(1)
        self._logger.debug(f"instantiated. url_to_archive: {self._url_to_archive}")