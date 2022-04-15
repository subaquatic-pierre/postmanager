from postmanager.interfaces import StorageInterface, StorageProxy


class MockStorageInterface(StorageInterface):
    def get_json(self, filename: str):
        pass

    def save_json(self, body: dict, filename: str):
        pass

    def save_bytes(self, bytes: bytes, filename: str):
        pass

    def get_bytes(self, filename: str):
        pass

    def delete_file(self, filename: str):
        pass

    def list_files(self):
        pass


class MockStorageProxyInterface(StorageProxy):
    def __init__(self, client) -> None:
        super().__init__(client)

    def get_json(self, filename: str):
        pass

    def save_json(self, body: dict, filename: str):
        pass

    def save_bytes(self, bytes: bytes, filename: str):
        pass

    def get_bytes(self, filename: str):
        pass

    def delete_file(self, filename: str):
        pass

    def list_files(self):
        pass
