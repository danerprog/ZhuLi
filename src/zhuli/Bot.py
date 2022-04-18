from environment.Environment import Environment

from datetime import datetime
import os
from pathlib import Path
import psutil
import signal
import subprocess


class Bot:
    
    def __init__(self, name, batch_file, logger):
        self._name = name
        self._batch_file = batch_file
        self._timestamp_started = None
        self._logger = logger
        self._process = None

        self._logger.info("bot initialized. name: {}, batch_file: {}, timestamp_started: {}".format(
            name,
            batch_file,
            str(self._timestamp_started)
        ))
        
    def start(self):
        self._logger.info("starting...")
        return self._runBatchFileIfAllowed()
        
    def stop(self):
        self._logger.info("stopping...")
        return self._stopBotProcessIfAllowed()

    def restart(self):
        self._logger.info("restarting...")
        self.stop()
        self.start()
        
    def isRunning(self):
        self._logger.debug("isRunning called.")
        return self._process is not None
        
    def getName(self):
        self._logger.debug("_name called.")
        return self._name
        
    def getTimestampStarted(self):
        self._logger.debug("getTimestampStarted called.")
        return None if self._timestamp_started is None else self._timestamp_started.strftime("%m-%d-%Y %H:%M:%S")
        
    def getTimestampUptime(self):
        timestamp_in_string = None
        if self._timestamp_started is not None:
            uptime = datetime.now() - self._timestamp_started
            total_seconds = uptime.total_seconds()
            self._logger.debug("getTimestampUptime called. total_seconds: " + str(total_seconds))
            timestamp_in_string = "{}:{}:{}".format(
                str(total_seconds // 3600),
                str(total_seconds % 3600 // 60),
                str(total_seconds % 60 // 1)
            )
        return timestamp_in_string
        
    def _runBatchFileIfAllowed(self):
        self._logger.debug("_runBatchFileIfAllowed called.")
        isBotCurrentlyRunning = self.isRunning()
        if not isBotCurrentlyRunning:
            self._runBatchFile()
        else:
            self._logger.warning("i am currently running!")
        return isBotCurrentlyRunning

    def _runBatchFile(self):
        self._logger.info("starting batch file: " + self._batch_file)
        self._process = subprocess.Popen(
            str(Path(self._batch_file).resolve()),
            creationflags = subprocess.CREATE_NEW_CONSOLE
        )
        self._timestamp_started = datetime.now()
        self._logger.debug("process created with PID " + str(self._process.pid))
        
    def _stopBotProcessIfAllowed(self):
        self._logger.debug("_stopBotProcessIfAllowed called.")
        isBotCurrentlyRunning = self.isRunning()
        if isBotCurrentlyRunning:
            self._stopBotProcess()
        else:
            self._logger.warning("i am not running!")
        return isBotCurrentlyRunning
        
    def _stopBotProcess(self):
        self._logger.info("stopping bot...  ")
        process_id = self._process.pid
        process = psutil.Process(process_id)
        self._logger.debug(
            "killing existing subprocess. process_id: " + str(process_id))
        for child_process in process.children(recursive = True):
            self._logger.debug("killing child process. child_process.pid: " + str(child_process.pid))
            child_process.kill()
        try: 
            process.kill()
        except psutil.NoSuchProcess:
            pass
        self._process = None
        self._timestamp_started = None

