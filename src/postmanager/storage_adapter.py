from typing import List, Any
from pathlib import Path
from unittest.mock import MagicMock

from postmanager.interfaces import StorageProxy, StorageInterface

from postmanager.storage_proxy_local import StorageProxyLocal
from postmanager.storage_proxy_s3 import StorageProxyS3


class StorageAdapter(StorageInterface):
    """Storage adapter to serve as interface between object and storage proxy.

    Attributes:
        storage_proxy (StorageProxy): Storage proxy used to read and write data.
    """

    def __init__(self, storage_proxy: StorageProxy) -> None:
        """
        Args:
            storage_proxy (StorageProxy): Storage proxy used to communicate with storage system.
        """
        self.storage_proxy = storage_proxy

    @property
    def client(self):
        """
        Client used to communicate with storage media, ie. `Path`, `S3Client`.
        """
        return self.storage_proxy.client

    @property
    def root_dir(self) -> str:
        """
        Root directory to read and write objects to.
        """
        root_dir: str = self.storage_proxy.root_dir
        return root_dir

    def save_json(self, body: Any, filename: str) -> None:
        """
        Save JSON data to storage.

        Args:
            body (dict): Filename to be used to save object, ie. `index.json`
            filename (str): Name of file, ie. index.json

        Returns:
            None: Raises `StorageProxyException` if error occured.
        """
        self.storage_proxy.save_json(body, filename)

    def get_json(self, filename: str) -> dict[str, str]:
        """
        Fetch JSON data from storage.

        Args:
            filename (str): Name of file, ie. `index.json`

        Returns:
            dict: JSON data requested, raises `StorageProxyException` if not found.
        """
        return self.storage_proxy.get_json(filename)

    def save_bytes(self, bytes: bytes, filename: str) -> None:
        """
        Save bytes data to storage.

        Args:
            body (bytes): Filename to be used to save object, ie. `image.jpeg`
            filename (str): Name of file, ie. `index.json`

        Returns:
            None: Raises `StorageProxyException` if error occured.
        """
        self.storage_proxy.save_bytes(bytes, filename)

    def get_bytes(self, filename: str) -> bytes:
        """
        Fetch bytes data from storage.

        Args:
            filename (str): Name of file, ie. `image.jpeg`

        Returns:
            bytes: bytes data requested, raises `StorageProxyException` if not found.
        """
        return self.storage_proxy.get_bytes(filename)

    def list_files(self) -> List[str]:
        """
        List all files in directory.

        Returns:
            list: List of all paths in directory.
        """
        return self.storage_proxy.list_files()

    def delete_file(self, filename: str) -> None:
        """
        Remove file from storage.

        Args:
            filename (str): Name of file, ie. `image.jpeg`

        Returns:
            None: Raises `StorageProxyException` if error occured.
        """
        self.storage_proxy.delete_file(filename)

    def _build_new_root(self, new_root: str):
        """
        Build new root string for new storage proxy.

        Args:
            new_root (str): New root directory used for new storage proxy object.
        """
        if isinstance(self.storage_proxy, StorageProxyLocal):
            return Path(self.root_dir, new_root)
        else:
            return f"{self.root_dir}{new_root}"

    def new_storage_proxy(self, new_root: str) -> StorageProxy:
        """
        Create new storage proxy for child object.

        Args:
            new_root (str): New root directory

        Returns:
            StorageProxy: New instance of `StorageProxy` with new root directory.
        """
        new_root_dir = self._build_new_root(new_root)

        if isinstance(self.storage_proxy, StorageProxyS3):
            return StorageProxyS3(
                self.storage_proxy.bucket_name, new_root_dir, self.client
            )

        elif isinstance(self.storage_proxy, StorageProxyLocal):
            return StorageProxyLocal(new_root_dir, self.client)

        elif isinstance(self.storage_proxy, MagicMock):
            return MagicMock()

        else:
            raise Exception("No storage proxy could be found")
