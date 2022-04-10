from abc import ABC, abstractmethod
from unittest.mock import MagicMock
import json
from postmanager.config import setup_client


from postmanager.exception import StorageProxyException


class StorageProxyBase(ABC):
    @abstractmethod
    def get_json(self, *args, **kwargs):
        pass

    @abstractmethod
    def save_json(self, *args, **kwargs):
        pass

    @abstractmethod
    def save_bytes(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_bytes(self, *args, **kwargs):
        pass


class S3StorageProxyBase(StorageProxyBase):
    def __init__(self, bucket_name, root_dir) -> None:
        self.bucket_name = bucket_name
        self.root_dir = root_dir
        self._verify_root_dir()

    # Required interface methods

    def get_json(self, filename):
        try:
            object = self.storage_interface.get_object(
                Bucket=self.bucket_name, Key=f"{self.root_dir}{filename}"
            )

            object_json = json.loads(object["Body"].read())
            return object_json
        except Exception as e:
            raise StorageProxyException(f"Error fething JSON from bucket. {str(e)}")

    def save_json(self, body: dict, filename: str):
        try:
            self.storage_interface.put_object(
                Bucket=self.bucket_name,
                Key=f"{self.root_dir}{filename}",
                Body=json.dumps(body),
            )
        except Exception as e:
            raise StorageProxyException(f"Error saving JSON to bucket. {str(e)}")

    def save_bytes(self, body: bytes, filename: str):
        try:
            self.storage_interface.put_object(
                Bucket=self.bucket_name,
                Key=f"{self.root_dir}{filename}",
                Body=body,
            )
        except Exception as e:
            raise StorageProxyException(f"Error saving bytes to bucket. {str(e)}")

    def get_bytes(self, filename: str):
        try:
            object = self.storage_interface.get_object(
                Bucket=self.bucket_name, Key=f"{self.root_dir}{filename}"
            )

            object_bytes = object["Body"].read()
            return object_bytes

        except Exception as e:
            raise StorageProxyException(f"Error fething Bytes from bucket. {str(e)}")

    # Extra S3 specific methods

    def delete_files(self, filenames):
        try:
            if len(filenames) > 0:
                objects = [{"Key": filename} for filename in filenames]
                self.storage_interface.delete_objects(
                    Bucket=self.bucket_name, Delete={"Objects": objects}
                )
        except Exception as e:
            raise StorageProxyException(f"Error deleting files from bucket. {str(e)}")

    def list_dir(self, dir: str = ""):
        try:
            list_response = self.storage_interface.list_objects_v2(
                Bucket=self.bucket_name
            )
            contents = list_response.get("Contents")
            object_keys = [
                obj["Key"]
                for obj in contents
                if obj["Key"].startswith(f"{self.root_dir}{dir}")
                and obj["Key"] != f"{self.root_dir}{dir}"
            ]
            return object_keys
        except Exception as e:
            raise StorageProxyException(f"Error listing files from bucket. {str(e)}")

    # Private methods

    def _verify_root_dir(self):
        try:
            assert self.root_dir.endswith("/")
        except:
            self.root_dir = f"{self.root_dir}/"


class MockS3StorageProxy(S3StorageProxyBase):
    def __init__(self, bucket_name, root_dir, mock_config={}) -> None:
        super().__init__(bucket_name, root_dir)
        self.storage_interface = MagicMock()
        mock_attrs = {"get_object.return_value": self.create_object_mock()}
        self.storage_interface.configure_mock(**mock_attrs)

    def create_object_mock(self):
        class StreamingBodyMock:
            def read(self):
                return json.dumps({"test": "ok"})

        object = {"Body": StreamingBodyMock()}

        return object


class S3StorageProxy(S3StorageProxyBase):
    def __init__(self, bucket_name, root_dir) -> None:
        super().__init__(bucket_name, root_dir)
        self.storage_interface = setup_client()
