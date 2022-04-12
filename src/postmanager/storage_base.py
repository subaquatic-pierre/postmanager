from typing import List

from postmanager.storage_proxy import (
    StorageProxy,
    S3StorageProxy,
    MockS3StorageProxy,
)


class StorageBase:
    def __init__(self, storage_proxy: StorageProxy) -> None:
        self.storage_proxy = storage_proxy

    def save_json(self, body, filename):
        self.storage_proxy.save_json(body, filename)

    def get_json(self, filename):
        return self.storage_proxy.get_json(filename)

    def save_bytes(self, bytes, filename):
        pass

    def get_bytes(self, filename):
        pass

    def list_files(self):
        return self.storage_proxy.list_dir()

    def get_bucket_name(self):
        return self.storage_proxy.bucket_name

    def get_root_dir(self):
        return self.storage_proxy.root_dir

    def delete_files(self, filenames):
        self.storage_proxy.delete_files(filenames)

    def delete_file(self, filename):
        self.storage_proxy.delete_file(filename)

    def new_storage_proxy(self, new_root: str, mock_config={}):
        # New root dir for child object
        root_dir = f"{self.get_root_dir()}{new_root}"

        if self.storage_proxy.__class__.__name__ == "MockS3StorageProxy":
            return MockS3StorageProxy(
                self.get_bucket_name(), root_dir, mock_config=mock_config
            )
        else:
            return S3StorageProxy(self.get_bucket_name(), root_dir)
