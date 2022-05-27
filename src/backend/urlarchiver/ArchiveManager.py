


class ArchiveManager:

    def __init__(self, database, logger):
        self._logger = logger.getChild(self.__class__.__name__)
        self._database = database
        self._logger.info(f"initialized. database: {self._database}")
        
    def addUrlToArchives(self, url, tags):
        self._logger.debug(f"addUrlToArchives called. url: {url}, tags: {tags}")
        if not self._doesUrlExistInDatabase(url):
            self._database['urls'].insert({
                'url' : url,
                'tags' : tags
            })
        else:
            self._database['urls'].update(
                {'url' : url},
                {'tags' : tags}
            )
            
    def getUrlsWithTag(self, tag):
        self._logger.debug(f"getUrlsWithTag called. tag: {tag}")
        return self._database['urls'].query({'tags': tag})
        
    def _doesUrlExistInDatabase(self, url):
        return self._database['urls'].count({'url': url}) > 0