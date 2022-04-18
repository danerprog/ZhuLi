import configparser


class ConfigurationManager:

    INSTANCE = None
    
    def __init__(
        self, 
        config_directory = "configs/"
    ):
        self._directory = config_directory
        self._config = {}
        
    def parseFile(self, filename):
        config_parser = configparser.ConfigParser()
        config_parser.read(self._directory + filename + ".ini")
        self._config[filename] = config_parser
        
    def getConfiguration(self, filename):
        return self._config[filename]
        
    def instance(config_directory = None):
        if ConfigurationManager.INSTANCE is None and config_directory is not None:
            ConfigurationManager.INSTANCE =  ConfigurationManager(config_directory)
        elif ConfigurationManager.INSTANCE is None and config_directory is None:
            ConfigurationManager.INSTANCE =  ConfigurationManager()
        return ConfigurationManager.INSTANCE
        
        
