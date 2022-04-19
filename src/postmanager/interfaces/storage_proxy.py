from abc import ABC
from postmanager.interfaces import StorageInterface


class StorageProxy(StorageInterface, ABC):
    def __init__(self, root_dir: str, client) -> None:
        self.root_dir = root_dir
        self.client = client
