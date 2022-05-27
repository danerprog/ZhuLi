from morph.messages.CommandMessage import CommandMessage
from morph.tasks.Task import Task

import aiohttp


class ArchiveUrlTask(Task):

    def __init__(self, **context):
        super().__init__(**context)
        self._archiver = "https://web.archive.org/save/"
        self._url_to_archive = self._arguments.token(1)
        self._tags = self._getTags()
        self._archive_manager = self._environment.getRuntimeConfiguration()['archive_manager']
        self._logger.debug(f"instantiated. archiver: {self._archiver}, url_to_archive: {self._url_to_archive}, tags: {self._tags}")
        
    async def run(self):
        link = f"{self._archiver}{self._url_to_archive}"
        self._logger.debug(f"run called. link: {link}")
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                if response.status == 200:
                    self._processSuccessfulResponse(response)
                else:
                    self._processUnsuccessfulResponse(response)
                
    def _processSuccessfulResponse(self, response):
        self._logger.debug(f"_processSuccessfulResponse called. response_links: {response.links}")
        self._addUrlToArchives(response)
        self._sendArchiveSuccessfulMessageToUser(response)
    
    def _processUnsuccessfulResponse(self, response):
        self._logger.warning(f"_processNonSuccessfulResponse called. status: {response.status}, reason: {response.reason}")
        self._sendArchiveUnsuccessfulMessageToUser(response)
        
    def _addUrlToArchives(self, response):
        original_link = response.links['original']['url']
        self._logger.debug(f"_addUrlToArchives called. original_link: {original_link}, tags: {self._tags}")
        self._archive_manager.addUrlToArchives(str(original_link), self._tags)
       
    def _sendArchiveSuccessfulMessageToUser(self, response):
        original_link = response.links['original']['url']
        memento_link = response.links['memento']['url']
        message = {
            'title' : "archive",
            'description' : f"archive links for {self._url_to_archive}. tags: {self._tags}",
            'level' : "info",
            'fields' : [{
                'name' : "original",
                'value' : original_link,
                'inline' : False
            },
            {
                'name' : "web.archive.org",
                'value' : memento_link,
                'inline' : False
            }]
        }
        self._sendMessage(message)
        
    def _sendArchiveUnsuccessfulMessageToUser(self, response):
        message = {
            'title' : "archive",
            'description' : f"Failed to archive url.",
            'level' : "warning",
            'fields' : [{
                'name' : "Http Status Code",
                'value' : response.status,
                'inline' : False
            },
            {
                'name' : "Reason",
                'value' : response.reason,
                'inline' : False
            }]
        }
        self._sendMessage(message)
        
    def _sendMessage(self, message_to_user):
        message_to_component = CommandMessage()
        message_to_component['target'] = self._message['sender']
        message_to_component.setCommand("send")
        message_to_component.setParameter('message', message_to_user)
        message_to_component.setParameter('channel_id', self._message['parameters']['channel_id'])
        self._environment.sendMessage(message_to_component)
        
    def _getTags(self):
        tags_to_return = []
        tags_argument = self._arguments.token(2)
        if tags_argument is not None:
            tags_to_return = tags_argument.split(',')
        return tags_to_return