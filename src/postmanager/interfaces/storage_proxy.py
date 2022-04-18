from abc import ABC
from postmanager.interfaces import StorageInterface


class StorageProxy(StorageInterface, ABC):
    def __init__(self, client) -> None:
        self.client = client
