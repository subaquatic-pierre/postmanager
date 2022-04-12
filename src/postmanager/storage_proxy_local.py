from typing import List
import os
from pathlib import Path

from postmanager.storage_base import StorageBase


class StorageProxyLocal(StorageBase):
    def __init__(self, root_dir: str, config={}) -> None:
        self.config = config

        self._init_root_dir(root_dir)

    def get_json(self, filename: str) -> dict:
        pass

    def save_json(self, body: dict, filename: str) -> None:
        pass

    def save_bytes(self, bytes: bytes, filename: str) -> None:
        pass

    def get_bytes(self, filename: str) -> bytes:
        pass

    def delete_files(self, filenames: List[str]) -> None:
        pass

    def delete_file(self, filename: str) -> None:
        pass

    def list_files(self, filename: str) -> List[dict]:
        pass

    def _init_root_dir(self, root_dir: str):
        config_home_dir = self.config.get("home_dir", False)
        sys_home_dir = str(Path.home())

        # Check if home dirrectory specified in config object
        # config home directory must exist
        if config_home_dir:
            if config_home_dir.endswith("/"):
                config_root_dir = f"{config_home_dir}{root_dir}"
            else:
                config_root_dir = f"{config_home_dir}/{root_dir}"

            root_dir_path = Path(config_root_dir)

        # No home dir configured, use default
        else:
            default_root_dir = f"{sys_home_dir}/.postmanager/data/{root_dir}"
            root_dir_path = Path(default_root_dir)

        root_dir_path.mkdir(parents=True, exist_ok=True)
        self.root_dir = default_root_dir
