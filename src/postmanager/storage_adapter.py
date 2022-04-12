from typing import List

from postmanager.storage_base import StorageBase


class StorageAdapter(StorageBase):
    def __init__(self, storage_proxy: StorageBase) -> None:
        self.storage_proxy = storage_proxy

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

    # TODO: Update delete files algorithm
    # Delete files algorithm needs to change
    def delete_files(self, filenames) -> None:
        self.storage_proxy.delete_files(filenames)

    def delete_file(self, filename) -> None:
        self.storage_proxy.delete_file(filename)

    def new_storage_proxy(self, new_root: str, mock_config={}) -> StorageBase:

        # Import storage proxies
        from postmanager.storage_proxy_s3 import (
            StorageProxyS3,
            MockStorageProxyS3,
        )
        from postmanager.storage_proxy_local import StorageProxyLocal

        # New root dir for child object
        root_dir = f"{self.root_dir}{new_root}"

        if self.storage_proxy_class_name == "MockStorageProxyS3":
            return MockStorageProxyS3(
                self.storage_proxy.bucket_name, root_dir, mock_config=mock_config
            )

        elif self.storage_proxy_class_name == "StorageProxyS3":
            return StorageProxyS3(self.storage_proxy.bucket_name, root_dir)

        elif self.storage_proxy_class_name == "StorageProxyLocal":
            return StorageProxyLocal(root_dir)

        else:
            raise Exception("No storage proxy could be found")
