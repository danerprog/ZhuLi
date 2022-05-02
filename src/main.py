class Main:

    def __init__(self, config_directory):
        self._initializeEnvironment(config_directory)
        self._initializeLoggers()
        self._initializeBackendComponents()
        self._initializeInterfaceComponents()
        
    def _initializeLoggers(self):
        logging_manager = self._environment.logger()
        logging_manager.hideLogger("discord")
        self._logger = logging_manager.getLogger("Main")
        
    def _initializeEnvironment(self, config_directory):
        from morph.Environment import Environment
        Environment.initialize(config_directory)
        self._environment = Environment.instance();
        
    def _initializeBackendComponents(self):
        import backend.batchfilemanager
    
    def _initializeInterfaceComponents(self):
        import interfaces.discordinterface


if __name__ == "__main__":
    import sys
    main = Main(sys.argv[1])