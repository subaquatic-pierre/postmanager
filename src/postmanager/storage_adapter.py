from typing import List
from pathlib import Path
from unittest.mock import MagicMock

from postmanager.interface import StorageProxy, StorageInterface

from postmanager.storage_proxy_local import StorageProxyLocal
from postmanager.storage_proxy_s3 import StorageProxyS3


class StorageAdapter(StorageInterface):
    def __init__(self, storage_proxy: StorageProxy) -> None:
        self.storage_proxy = storage_proxy

    @property
    def client(self):
        return self.storage_proxy.client

    @property
    def root_dir(self) -> str:
        return self.storage_proxy.root_dir

    @property
    def storage_proxy_class_name(self):
        return self.storage_proxy.__class__.__name__

    def save_json(self, body: dict, filename: str) -> None:
        self.storage_proxy.save_json(body, filename)

    def get_json(self, filename) -> dict:
        return self.storage_proxy.get_json(filename)

    def save_bytes(self, bytes: bytes, filename: str) -> None:
        self.storage_proxy.save_bytes(bytes, filename)

    def get_bytes(self, filename: str) -> bytes:
        return self.storage_proxy.get_bytes(filename)

    def list_files(self) -> List[dict]:
        return self.storage_proxy.list_files()

    def delete_file(self, filename) -> None:
        self.storage_proxy.delete_file(filename)

    def build_new_route(self, new_root):
        if self.storage_proxy_class_name == "StorageProxyLocal":
            return Path(self.root_dir, new_root)
        else:
            return f"{self.root_dir}{new_root}"

    def new_storage_proxy(self, new_root: str) -> StorageProxy:
        new_root_dir = self.build_new_route(new_root)

        if self.storage_proxy_class_name == "StorageProxyS3":
            return StorageProxyS3(
                self.storage_proxy.bucket_name, new_root_dir, self.client
            )

        elif self.storage_proxy_class_name == "StorageProxyLocal":
            return StorageProxyLocal(new_root_dir, self.client)

        elif self.storage_proxy_class_name == "MagicMock":
            return MagicMock()

        else:
            raise Exception("No storage proxy could be found")
