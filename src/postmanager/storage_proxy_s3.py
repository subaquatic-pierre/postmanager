import json
from typing import List

from postmanager.exception import StorageProxyException
from postmanager.interfaces import StorageProxy


class StorageProxyS3(StorageProxy):
    """S3 storage proxy used to communicate with AWS S3 to manage data.

    Attributes:
        root_dir (str): Root directory to read and write objects to.
        bucket_name (str): Name of bucket on AWS.
        client (StorageProxy): Client communicating with storage, ie. Path.
    """

    def __init__(self, bucket_name: str, root_dir: str, client) -> None:
        """
        Args:
            bucket_name (str): Name of bucket on AWS.
            root_dir (str): Root directory to read and write objects to.
            client (StorageProxy): Client communicating with storage, ie. Path.
        """
        self.bucket_name = bucket_name
        super().__init__(root_dir, client)

        self._verify_root_dir()

    def get_json(self, filename: str):
        """
        Fetch JSON data from storage.

        Args:
            filename (str): Name of file, ie. `index.json`

        Returns:
            dict: JSON data requested, raises `StorageProxyException` if not found.
        """
        try:
            object = self.client.get_object(
                Bucket=self.bucket_name, Key=f"{self.root_dir}{filename}"
            )

            object_json: dict[str, str] = json.loads(object["Body"].read())
            return object_json

        except Exception as e:
            raise StorageProxyException(f"Error fething JSON from bucket. {str(e)}")

    def save_json(self, body: dict[str, str], filename: str) -> None:
        """
        Save JSON data to storage.

        Args:
            body (dict): Filename to be used to save object, ie. `index.json`
            filename (str): Name of file, ie. index.json

        Returns:
            None: Raises `StorageProxyException` if error occured.
        """
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=f"{self.root_dir}{filename}",
                Body=json.dumps(body),
            )

        except Exception as e:
            raise StorageProxyException(f"Error saving JSON to bucket. {str(e)}")

    def save_bytes(self, bytes: bytes, filename: str) -> None:
        """
        Save bytes data to storage.

        Args:
            body (bytes): Filename to be used to save object, ie. `image.jpeg`
            filename (str): Name of file, ie. `index.json`

        Returns:
            None: Raises `StorageProxyException` if error occured.
        """
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=f"{self.root_dir}{filename}",
                Body=bytes,
            )

        except Exception as e:
            raise StorageProxyException(f"Error saving Bytes to bucket. {str(e)}")

    def get_bytes(self, filename: str) -> bytes:
        """
        Fetch bytes data from storage.

        Args:
            filename (str): Name of file, ie. `image.jpeg`

        Returns:
            bytes: bytes data requested, raises `StorageProxyException` if not found.
        """
        try:
            object = self.client.get_object(
                Bucket=self.bucket_name, Key=f"{self.root_dir}{filename}"
            )

            object_bytes: bytes = object["Body"].read()
            return object_bytes

        except Exception as e:
            raise StorageProxyException(f"Error fething Bytes from bucket. {str(e)}")

    def delete_file(self, filename: str) -> None:
        """
        Remove file from storage.

        Args:
            filename (str): Name of file, ie. `image.jpeg`

        Returns:
            None: Raises `StorageProxyException` if error occured.
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket_name, Key=f"{self.root_dir}{filename}"
            )

        except Exception as e:
            raise StorageProxyException(f"Error deleting object from bucket. {str(e)}")

    def list_files(
        self,
    ) -> List[str]:
        """
        List all files in directory.

        Returns:
            list: List of all paths in directory.
        """
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
        """Ensure root directory ends with '/'."""
        try:
            assert self.root_dir.endswith("/")
        except Exception:
            self.root_dir = f"{self.root_dir}/"
