from abc import ABC

from postmanager.storage_base import StorageBase


class StorageProxy(StorageBase, ABC):
    def __init__(self, root_dir) -> None:
        self.root_dir = root_dir

        self._verify_root_dir()

    def _verify_root_dir(self) -> None:
        try:
            assert self.root_dir.endswith("/")
        except:
            self.root_dir = f"{self.root_dir}/"
