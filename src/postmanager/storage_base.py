from typing import List
from abc import ABC, abstractmethod


class StorageBase(ABC):
    @abstractmethod
    def get_json(self, filename: str) -> dict:
        pass

    @abstractmethod
    def save_json(self, body: dict, filename: str) -> None:
        pass

    @abstractmethod
    def save_bytes(self, bytes: bytes, filename: str) -> None:
        pass

    @abstractmethod
    def get_bytes(self, filename: str) -> bytes:
        pass

    @abstractmethod
    def delete_files(self, filename: List[str]):
        pass

    @abstractmethod
    def delete_file(self, filename: str):
        pass

    @abstractmethod
    def list_files(self) -> List[dict]:
        pass


class StorageProxy(StorageBase, ABC):
    def __init__(self, root_dir) -> None:
        self.root_dir = root_dir

        self._verify_root_dir()

    def _verify_root_dir(self) -> None:
        try:
            assert self.root_dir.endswith("/")
        except:
            self.root_dir = f"{self.root_dir}/"


class ModelStorage(StorageBase):
    def __init__(self, storage_proxy: StorageProxy) -> None:
        self.storage_proxy = storage_proxy

    def save_json(self, body: dict, filename: str):
        self.storage_proxy.save_json(body, filename)

    def get_json(self, filename):
        return self.storage_proxy.get_json(filename)

    def save_bytes(self, bytes: bytes, filename: str):
        self.storage_proxy.save_bytes(bytes, filename)

    def get_bytes(self, filename: str):
        self.storage_proxy.save_bytes(filename)

    def list_files(self) -> List[dict]:
        return self.storage_proxy.list_files()

    def delete_files(self, filenames):
        self.storage_proxy.delete_files(filenames)

    def delete_file(self, filename):
        self.storage_proxy.delete_file(filename)

    def get_root_dir(self):
        return self.storage_proxy.root_dir

    def new_storage_proxy(self, new_root: str, mock_config={}):

        # Import storage proxies
        from postmanager.s3_storage_proxy import (
            S3StorageProxy,
            MockS3StorageProxy,
        )
        from postmanager.local_storage_proxy import LocalStorageProxy

        # New root dir for child object
        root_dir = f"{self.get_root_dir()}{new_root}"

        if self.storage_proxy.__class__.__name__ == "MockS3StorageProxy":
            return MockS3StorageProxy(
                self.storage_proxy.bucket_name, root_dir, mock_config=mock_config
            )

        elif self.storage_proxy.__class__.__name__ == "S3StorageProxy":
            return S3StorageProxy(self.storage_proxy.bucket_name, root_dir)

        elif self.storage_proxy.__class__.__name__ == "LocalStorageProxy":
            return LocalStorageProxy()

        else:
            raise Exception("No storage proxy could be found")
