import json
from typing import List
from pathlib import Path


from postmanager.storage_base import StorageBase
from postmanager.exception import StorageProxyException


class StorageProxyLocal(StorageBase):
    def __init__(self, root_dir: str, config={}) -> None:
        self.config = config

        self._init_root_dir(root_dir)

    def get_json(self, filename: str) -> dict:
        try:
            filepath = Path(self.root_dir, filename)

            with open(filepath, "r") as f:
                object_json = json.loads(f.read())

            return object_json
        except Exception as e:
            raise StorageProxyException(f"Error fething JSON from directory. {str(e)}")

    def save_json(self, body: dict, filename: str) -> None:
        try:
            filepath = Path(self.root_dir, filename)

            with open(filepath, "w") as f:
                f.write(json.dumps(body, indent=4))

        except Exception as e:
            raise StorageProxyException(f"Error saving JSON to directory. {str(e)}")

    def save_bytes(self, bytes: bytes, filename: str) -> None:
        try:
            filepath = Path(self.root_dir, filename)

            with open(filepath, "wb") as f:
                f.write(bytes)

        except Exception as e:
            raise StorageProxyException(f"Error saving bytes to directory. {str(e)}")

    def get_bytes(self, filename: str) -> bytes:
        try:
            filepath = Path(self.root_dir, filename)

            with open(filepath, "rb") as f:
                bytes = f.read()

            return bytes

        except Exception as e:
            raise StorageProxyException(f"Error getting bytes from directory. {str(e)}")

    # TODO: Method needs to be fixed
    # Not currently being used
    # need  to change delete file algorithm
    # in manager
    def delete_files(self, filenames: List[str]) -> None:
        try:
            for filename in filenames:
                filepath = Path(self.root_dir, filename)
                filepath.unlink(missing_ok=True)

        except Exception as e:
            raise StorageProxyException(
                f"Error deleting files from directory. {str(e)}"
            )

    def delete_file(self, filename: str) -> None:
        try:
            filepath = Path(self.root_dir, filename)
            filepath.unlink(missing_ok=True)

        except Exception as e:
            raise StorageProxyException(f"Error deleting file from directory. {str(e)}")

    def list_files(self) -> List[dict]:
        try:
            filepath = Path(self.root_dir)
            paths = []
            for currentpath, folders, files in os.walk(filepath):
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
