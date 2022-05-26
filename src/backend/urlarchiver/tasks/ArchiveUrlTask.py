from morph.messages.CommandMessage import CommandMessage
from morph.tasks.Task import Task

import aiohttp


class ArchiveUrlTask(Task):

    def __init__(self, **context):
        super().__init__(**context)
        self._archiver = "https://web.archive.org/save/"
        self._url_to_archive = self._arguments.token(1)
        self._logger.debug(f"instantiated. archiver: {self._archiver}, url_to_archive: {self._url_to_archive}")
        
    async def run(self):
        link = f"{self._archiver}{self._url_to_archive}"
        self._logger.debug(f"run called. link: {link}")
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                response_links = response.links
                self._logger.debug(f"response received. response_links: {response_links}")
                self._sendArchiveLinksToUser(response_links)
                
    def _sendArchiveLinksToUser(self, links):
        original_link = links['original']['url']
        memento_link = links['memento']['url']
        message = {
            'title' : "archive",
            'description' : f"archive links for {self._url_to_archive}",
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
        
    def _sendMessage(self, message_to_user):
        message_to_component = CommandMessage()
        message_to_component['target'] = self._message['sender']
        message_to_component.setCommand("send")
        message_to_component.setParameter('message', message_to_user)
        message_to_component.setParameter('channel_id', self._message['parameters']['channel_id'])
        self._environment.sendMessage(message_to_component)