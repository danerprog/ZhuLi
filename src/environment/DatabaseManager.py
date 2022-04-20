import pymongo


class DatabaseManager:

    def __init__(self, port, logger):
        self._logger = logger
        self._port = port
        self._logger.info("initialized. port: {}".format(
            port
        ))