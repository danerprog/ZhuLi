import configparser
import os.path


class ConfigurationManager:

    INSTANCE = None
    
    def __init__(
        self, 
        config_directory = "configs/"
    ):
        print(">>> Initializing ConfigurationManager. config_directory: " + config_directory)
        self._directory = config_directory
        self._config = {}
        
    def parseFile(self, filename):
        config_parser = configparser.ConfigParser()
        config_file = self._directory + filename + ".ini"
        if not os.path.isfile(config_file):
            print(">>> WARNING: config_file {} is not a file!".format(config_file))
        config_parser.read(config_file)
        self._config[filename] = config_parser
        
    def getConfiguration(self, filename):
        return self._config[filename]
        
    def instance(config_directory = None):
        if ConfigurationManager.INSTANCE is None and config_directory is not None:
            ConfigurationManager.INSTANCE = ConfigurationManager(config_directory)
        elif ConfigurationManager.INSTANCE is None and config_directory is None:
            ConfigurationManager.INSTANCE = ConfigurationManager()
        return ConfigurationManager.INSTANCE
        
        
