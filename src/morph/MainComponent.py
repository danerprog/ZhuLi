from .Environment import Environment


class MainComponent:

    def __init__(self):
        self._initializeComponentMetadata()
        self._initializeEnvironment()
        self._logger.info(f"Main component {self._main_component_name} initialized.")
        
    def _initializeComponentMetadata(self):
        tokens = self.__module__.split('.', 3)
        self._component_level = tokens[0]
        self._component_module_name = tokens[1]
        self._main_component_name = tokens[2]
        Environment.instance().getLogger().info(
            f"Component module initialized. component_level: {self._component_level}, " +
            f"component_module_name: {self._component_module_name}, " + 
            f"main_component_name: {self._main_component_name}")
            
    def _initializeEnvironment(self):
        Environment.Shard.initialize(self._component_module_name, self._component_level)
        self._environment = Environment.shard(self._component_module_name)
        self._logger = self._environment.getLogger(self._main_component_name)
       