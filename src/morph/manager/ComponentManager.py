

class ComponentManager:
    
    LEVEL = {
        'backend' : 'backend',
        'interface' : 'interface'
    }

    def __init__(self, logger):
        self._logger = logger.getChild(self.__class__.__name__)
        self._components = {
            ComponentManager.LEVEL['backend'] : [],
            ComponentManager.LEVEL['interface'] : []
        }
        self._logger.info("initialized.")
        
    def registerComponentAtLevel(self, component_name, level):
        is_successful = False
        if not self._isLevelSupported(level):
            self._logger.warning(f"Tried to register a component at an unsupported level '{level}'! Register unsuccessful.")
        elif not isinstance(component_name, str):
            self._logger.warning(f"Tried to register a non-string component_name '{component_name}'! Register unsuccessful." )
        else:
            self._components[level].append(component_name)
            is_successful = True
            self._logger.info(f"Successfully registered component '{component_name}'")
        return is_successful
        
    def getComponentsOnLevel(self, level):
        components = []
        if not self._isLevelSupported(level):
            self._logger.warning(f"Tried to get components on an unsupported level '{level}'!. Returning an empty list.")
        else:
            components = self._components[level]
        return components
        
    def _isLevelSupported(self, level):
        return level in self._components