from postmanager.storage_base import StorageBase
from postmanager.storage_proxy import StorageProxy


class MediaData(StorageBase):
    def __init__(self, storage_proxy: StorageProxy) -> None:
        super.__init__(storage_proxy)

        self._unsaved_media = {}
        self._undeleted_media = {}
        self.media_index = {}
        self._init_index()

    def _init_index(self):
        pass
