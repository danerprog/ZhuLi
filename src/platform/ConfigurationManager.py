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
    
    def __getitem__(self, key):
        return self.getConfiguration(key)
        
    def parseFile(self, filename):
        config_parser = configparser.ConfigParser()
        config_file = self._directory + filename + ".ini"
        if not os.path.isfile(config_file):
            print(">>> WARNING: config_file {} is not a file!".format(config_file))
        config_parser.read(config_file)
        self._unpackConfig(filename, config_parser)
        
    def getConfiguration(self, filename):
        return self._config[filename]
        
    def instance(config_directory = None):
        if ConfigurationManager.INSTANCE is None and config_directory is not None:
            ConfigurationManager.INSTANCE = ConfigurationManager(config_directory)
        elif ConfigurationManager.INSTANCE is None and config_directory is None:
            ConfigurationManager.INSTANCE = ConfigurationManager()
        return ConfigurationManager.INSTANCE
        
    def _unpackConfig(self, filename, config_parser):
        self._config[filename] = {}
        for section in config_parser.sections():
            self._config[filename][section] = {}
            for key, value in config_parser.items(section):
                self._config[filename][section][key] = value
        print(">>> Config unpacked for '{}'. config: {}".format(
            filename,
            self._config[filename]
        ))

        
