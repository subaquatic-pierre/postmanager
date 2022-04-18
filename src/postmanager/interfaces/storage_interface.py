from typing import List
from abc import ABC, abstractmethod


class StorageInterface(ABC):
    @abstractmethod
    def get_json(self, filename: str) -> dict[str, str]:
        pass

    @abstractmethod
    def save_json(self, body: dict[str, str], filename: str) -> None:
        pass

    @abstractmethod
    def save_bytes(self, bytes: bytes, filename: str) -> None:
        pass

    @abstractmethod
    def get_bytes(self, filename: str) -> bytes:
        pass

    @abstractmethod
    def delete_file(self, filename: str) -> None:
        pass

    @abstractmethod
    def list_files(self) -> List[str]:
        pass
