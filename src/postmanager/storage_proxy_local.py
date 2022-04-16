import json
import os
import shutil

from typing import List
from pathlib import Path

from postmanager.exception import StorageProxyException
from postmanager.interfaces import StorageProxy


class StorageProxyLocal(StorageProxy):
    def __init__(self, root_dir: str, client, config={}) -> None:
        super().__init__(client)
        self.config = config

        self._init_root_dir(root_dir)

    def get_json(self, filename: str) -> dict:
        try:
            file = self.client(self.root_dir, filename)
            object_json = json.loads(file.read_text())

            return object_json
        except Exception as e:
            raise StorageProxyException(f"Error fething JSON from directory. {str(e)}")

    def save_json(self, body: dict, filename: str) -> None:
        try:
            file = self.client(self.root_dir, filename)
            file.write_text(json.dumps(body, indent=4))

        except Exception as e:
            raise StorageProxyException(f"Error saving JSON to directory. {str(e)}")

    def save_bytes(self, bytes: bytes, filename: str) -> None:
        try:
            file = self.client(self.root_dir, filename)
            file.write_bytes(bytes)

        except Exception as e:
            raise StorageProxyException(f"Error saving bytes to directory. {str(e)}")

    def get_bytes(self, filename: str) -> bytes:
        try:
            file = self.client(self.root_dir, filename)
            bytes = file.read_bytes()

            return bytes

        except Exception as e:
            raise StorageProxyException(f"Error getting bytes from directory. {str(e)}")

    def delete_file(self, filename: str) -> None:
        try:
            file = self.client(self.root_dir, filename)
            file.unlink(missing_ok=True)

        except Exception as e:
            raise StorageProxyException(f"Error deleting file from directory. {str(e)}")

    def delete_directory(self, directory: str) -> None:
        shutil.rmtree(directory, ignore_errors=True)

    def list_files(self) -> List[dict]:
        try:
            filepath = self.client(self.root_dir)
            paths = []
            for currentpath, _, files in os.walk(filepath):
                # Add current path to paths
                paths.append(currentpath)

                for file in files:
                    filepath = f"{currentpath}/{file}"
                    paths.append(filepath)

            return paths

        except Exception as e:
            raise StorageProxyException(f"Error listing files from directory. {str(e)}")

    def _init_root_dir(self, root_dir: str):
        config_home_dir = self.config.get("home_dir", False)
        sys_home_dir = Path.home()

        if config_home_dir:
            root_dir_path = Path(config_home_dir, root_dir)

        else:
            default_root_dir = Path(sys_home_dir, ".postmanager", "data", root_dir)
            root_dir_path = Path(default_root_dir)

        root_dir_path.mkdir(parents=True, exist_ok=True)
        self.root_dir = root_dir_path
