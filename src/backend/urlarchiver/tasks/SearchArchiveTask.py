from morph.messages.CommandMessage import CommandMessage
from morph.tasks.Task import Task


class SearchArchiveTask(Task):

    def __init__(self, **context):
        super().__init__(**context)
        self._timegate = "https://web.archive.org/web/"
        self._subcommand = self._arguments.token(1)
        self._search_parameters = self._arguments.token(2)
        self._archive_manager = self._environment.getRuntimeConfiguration()['archive_manager']
        self._logger.debug(f"instantiated. timegate: {self._timegate}, subcommand: {self._subcommand}, search_parameters: {self._search_parameters}")
       
    async def run(self):
        if self._subcommand == "archive":
            self._searchArchiveIfAllowed()
            
    def _searchArchiveIfAllowed(self):
        if self._search_parameters is None:
            self._sendNoSearchParametersProvidedMessageToUser()
        else:
            search_parameters = self._search_parameters.split(':')
            if len(search_parameters) < 2:
                self._sendInvalidSearchParametersMessageToUser()
            else:
                self._searchArchiveUsingParameters(search_parameters)
            
    def _searchArchiveUsingParameters(self, search_parameters):
        type = search_parameters[0]
        keyword = search_parameters[1]
        self._logger.debug(f"_searchArchiveUsingParameters called. search_parameters: {search_parameters}, type: {type}, keyword: {keyword}")
 
        if type == 'tag':
            documents = self._archive_manager.getUrlsWithTag(keyword)
            if len(documents) > 0:
                self._sendTimegateUrlsMessageToUser(documents, keyword)
            else:
                self._sendNoUrlFoundForTagMessageToUser(keyword)    
        else:
            self._logger.warning(f"Unsupported type '{type}.")
            self._sendUnsupportedSearchParameterTypeMessageToUser(type)
            
    def _sendNoSearchParametersProvidedMessageToUser(self):
        message = {
            'title' : "search archive",
            'description' : f"No search parameters provided. Usage: search archive <search_parameters>",
            'level' : "warning"
        }
        self._sendMessage(message)
            
    def _sendInvalidSearchParametersMessageToUser(self):
        message = {
            'title' : "search archive",
            'description' : f"Invalid search parameters provided: {self._search_parameters}. Format: <type>:<keyword>",
            'level' : "warning"
        }
        self._sendMessage(message)
        
    def _sendUnsupportedSearchParameterTypeMessageToUser(self, type):
        message = {
            'title' : "search archive",
            'description' : f"Unsupported search parameter type: {type}",
            'level' : "warning",
            'fields' : [{
                'name' : "Supported types:",
                'value' : "tag",
                'inline' : False
            }]
        }
        self._sendMessage(message)
        
    def _sendTimegateUrlsMessageToUser(self, documents, tag):
        message = {
            'title' : "search archive",
            'description' : f"List of timegates for urls with the tag: {tag}",
            'level' : "info",
            'fields' : [{
                'name' : "Timegate Urls",
                'value' : self._getTimegateUrls(documents),
                'inline' : False
            }]
        }
        self._sendMessage(message)

    def _sendNoUrlFoundForTagMessageToUser(self, tag):
        message = {
            'title' : "search archive",
            'description' : f"No urls found with the given tag: {tag}",
            'level' : "info"
        }
        self._sendMessage(message)
        
    def _getTimegateUrls(self, documents):
        url_string = ""
        for document in documents:
            url_to_append = f"{self._timegate}{document['url']}"
            url_string = f"{url_string}{url_to_append}\n"
        return url_string

    def _sendMessage(self, message_to_user):
        message_to_component = CommandMessage()
        message_to_component['target'] = self._message['sender']
        message_to_component.setCommand("send")
        message_to_component.setParameter('message', message_to_user)
        message_to_component.setParameter('channel_id', self._message['parameters']['channel_id'])
        self._environment.sendMessage(message_to_component)