from abc import ABC, abstractmethod
from unittest.mock import MagicMock
import json
from postmanager.config import setup_client


from postmanager.exception import BucketProxyException


class BucketProxyBase(ABC):
    def __init__(self, bucket_name, root_dir) -> None:
        self.bucket_name = bucket_name
        self.root_dir = root_dir

    def get_json(self, filename):
        try:
            object = self.bucket_interface.get_object(
                Bucket=self.bucket_name, Key=f"{self.root_dir}{filename}"
            )

            object_json = json.loads(object["Body"].read())
            return object_json
        except Exception as e:
            raise BucketProxyException(f"Error fething JSON from bucket. {str(e)}")

    def save_json(self, body: dict, filename: str):
        try:
            self.bucket_interface.put_object(Bucket=self.bucket_name, Key=self.root_dir)
            self.bucket_interface.put_object(
                Bucket=self.bucket_name,
                Key=f"{self.root_dir}{filename}",
                Body=json.dumps(body),
            )
        except Exception as e:
            raise BucketProxyException(f"Error saving JSON to bucket. {str(e)}")

    def delete_files(self, filenames):
        try:
            if len(filenames) > 0:
                objects = [{"Key": filename} for filename in filenames]
                self.bucket_interface.delete_objects(
                    Bucket=self.bucket_name, Delete={"Objects": objects}
                )
        except Exception as e:
            raise BucketProxyException(f"Error deleting files from bucket. {str(e)}")

    def list_dir(self, dir: str = ""):
        try:
            list_response = self.bucket_interface.list_objects_v2(
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
            raise BucketProxyException(f"Error listing files from bucket. {str(e)}")

    def save_bytes(self, body: bytes, filename: str):
        try:
            self.bucket_interface.put_object(
                Key=f"{self.root_dir}{filename}",
                Body=body,
            )
        except Exception as e:
            raise BucketProxyException(f"Error saving bytes to bucket. {str(e)}")


class MockBucketProxy(BucketProxyBase):
    def __init__(self, bucket_name, root_dir, mock_config={}) -> None:
        super().__init__(bucket_name, root_dir)
        self.bucket_interface = MagicMock()
        mock_attrs = {"get_object.return_value": self.create_object_mock()}
        self.bucket_interface.configure_mock(**mock_attrs)

    def create_object_mock(self):
        class StreamingBodyMock:
            def read(self):
                return json.dumps({"test": "ok"})

        object = {"Body": StreamingBodyMock()}

        return object


class BucketProxy(BucketProxyBase):
    def __init__(self, bucket_name, root_dir) -> None:
        super().__init__(bucket_name, root_dir)
        self.bucket_interface = setup_client()
