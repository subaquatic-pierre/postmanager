import json
from typing import List

from postmanager.exception import StorageProxyException
from postmanager.interfaces import StorageProxy


class StorageProxyS3(StorageProxy):
    def __init__(self, bucket_name, root_dir, client) -> None:
        super().__init__(client)

        self.root_dir = root_dir
        self.bucket_name = bucket_name

        self._verify_root_dir()

    def get_json(self, filename):
        try:
            object = self.client.get_object(
                Bucket=self.bucket_name, Key=f"{self.root_dir}{filename}"
            )

            object_json = json.loads(object["Body"].read())
            return object_json

        except Exception as e:
            raise StorageProxyException(f"Error fething JSON from bucket. {str(e)}")

    def save_json(self, body: dict, filename: str):
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=f"{self.root_dir}{filename}",
                Body=json.dumps(body),
            )

        except Exception as e:
            raise StorageProxyException(f"Error saving JSON to bucket. {str(e)}")

    def save_bytes(self, bytes: bytes, filename: str) -> None:
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=f"{self.root_dir}{filename}",
                Body=bytes,
            )

        except Exception as e:
            raise StorageProxyException(f"Error saving Bytes to bucket. {str(e)}")

    def get_bytes(self, filename: str) -> bytes:
        try:
            object = self.client.get_object(
                Bucket=self.bucket_name, Key=f"{self.root_dir}{filename}"
            )

            object_bytes = object["Body"].read()
            return object_bytes

        except Exception as e:
            raise StorageProxyException(f"Error fething Bytes from bucket. {str(e)}")

    def delete_file(self, filename: str) -> None:
        try:
            self.client.delete_object(
                Bucket=self.bucket_name, Key=f"{self.root_dir}{filename}"
            )

        except Exception as e:
            raise StorageProxyException(f"Error deleting object from bucket. {str(e)}")

    def list_files(self) -> List[dict]:
        try:
            list_response = self.client.list_objects_v2(
                Prefix=self.root_dir, Bucket=self.bucket_name
            )
            contents = list_response.get("Contents")
            object_keys = [data["Key"] for data in contents]
            return object_keys

        except Exception as e:
            raise StorageProxyException(f"Error listing files from bucket. {str(e)}")

    def _verify_root_dir(self) -> None:
        try:
            assert self.root_dir.endswith("/")
        except:
            self.root_dir = f"{self.root_dir}/"
