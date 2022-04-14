import json
from unittest import TestCase
from unittest.mock import MagicMock, call

from postmanager.exception import StorageProxyException
from postmanager.storage_proxy_s3 import StorageProxyS3

from tests.setup_objects import setup_storage_proxy_s3, setup_streaming_body

BUCKET_NAME = "test-bucket"
TEMPLATE = "test"
JSON_BODY = {"testing": "ok"}
BYTES_BODY = b"SOMEBYTESHERE"


class StorageProxyS3Test(TestCase):
    def test_init(self):
        proxy = setup_storage_proxy_s3(BUCKET_NAME, TEMPLATE)
        self.assertEqual(proxy.root_dir, f"{TEMPLATE}/")
        self.assertEqual(proxy.bucket_name, BUCKET_NAME)

    def test_get_json(self):
        proxy = setup_storage_proxy_s3(BUCKET_NAME, TEMPLATE)
        filename = "file.json"
        root_dir = proxy.root_dir
        object_key = f"{root_dir}{filename}"
        proxy.client.get_object.return_value = setup_streaming_body(JSON_BODY)

        # Call
        data = proxy.get_json(filename)

        # Assert
        proxy.client.get_object.assert_called_with(Bucket=BUCKET_NAME, Key=object_key)
        self.assertEqual(data, JSON_BODY)

    def test_get_json_error(self):
        proxy = setup_storage_proxy_s3(BUCKET_NAME, TEMPLATE)
        filename = "file.json"
        proxy.client.get_object.side_effect = StorageProxyException

        # Call
        with self.assertRaises(StorageProxyException) as e:
            proxy.get_json(filename)

        # Assert
        self.assertIn("Error fething JSON from bucket.", str(e.exception))

    def test_save_json(self):
        proxy = setup_storage_proxy_s3(BUCKET_NAME, TEMPLATE)
        filename = "file.json"
        root_dir = proxy.root_dir
        object_key = f"{root_dir}{filename}"
        body = json.dumps(JSON_BODY)

        # Call
        proxy.save_json(JSON_BODY, filename)

        # Assert
        proxy.client.put_object.assert_called_with(
            Bucket=BUCKET_NAME, Key=object_key, Body=body
        )

    def test_save_json_error(self):
        proxy = setup_storage_proxy_s3(BUCKET_NAME, TEMPLATE)
        filename = "file.json"
        body = json.dumps(JSON_BODY)
        proxy.client.put_object.side_effect = StorageProxyException

        # Call
        with self.assertRaises(StorageProxyException) as e:
            proxy.save_json(body, filename)

        # Assert
        self.assertIn("Error saving JSON to bucket", str(e.exception))

    def test_save_bytes(self):
        proxy = setup_storage_proxy_s3(BUCKET_NAME, TEMPLATE)
        filename = "file.jpeg"
        root_dir = proxy.root_dir
        object_key = f"{root_dir}{filename}"

        # Call
        proxy.save_bytes(BYTES_BODY, filename)

        # Assert
        proxy.client.put_object.assert_called_with(
            Bucket=BUCKET_NAME, Key=object_key, Body=BYTES_BODY
        )

    def test_save_bytes_error(self):
        proxy = setup_storage_proxy_s3(BUCKET_NAME, TEMPLATE)
        filename = "file.jpeg"
        proxy.client.put_object.side_effect = StorageProxyException

        # Call
        with self.assertRaises(StorageProxyException) as e:
            proxy.save_bytes(BYTES_BODY, filename)

        # Assert
        self.assertIn("Error saving Bytes to bucket", str(e.exception))

    def test_get_bytes(self):
        proxy = setup_storage_proxy_s3(BUCKET_NAME, TEMPLATE)
        filename = "file.jpeg"
        root_dir = proxy.root_dir
        object_key = f"{root_dir}{filename}"
        proxy.client.get_object.return_value = setup_streaming_body(
            BYTES_BODY, is_bytes=True
        )

        # Call
        data = proxy.get_bytes(filename)

        # Assert
        proxy.client.get_object.assert_called_with(Bucket=BUCKET_NAME, Key=object_key)
        self.assertEqual(data, BYTES_BODY)

    def test_get_bytes_error(self):
        proxy = setup_storage_proxy_s3(BUCKET_NAME, TEMPLATE)
        filename = "file.jpeg"
        proxy.client.get_object.side_effect = StorageProxyException

        # Call
        with self.assertRaises(StorageProxyException) as e:
            proxy.get_bytes(filename)

        # Assert
        self.assertIn("Error fething Bytes from bucket.", str(e.exception))

    def test_delete_file(self):
        proxy = setup_storage_proxy_s3(BUCKET_NAME, TEMPLATE)
        filename = "file.jpeg"
        root_dir = proxy.root_dir
        object_key = f"{root_dir}{filename}"

        # Call
        proxy.delete_file(filename)

        # Assert
        proxy.client.delete_object.assert_called_with(
            Bucket=BUCKET_NAME, Key=object_key
        )

    def test_delete_file_error(self):
        proxy = setup_storage_proxy_s3(BUCKET_NAME, TEMPLATE)
        filename = "file.jpeg"
        proxy.client.delete_object.side_effect = StorageProxyException

        # Call
        with self.assertRaises(StorageProxyException) as e:
            proxy.delete_file(filename)

        # Assert
        self.assertIn("Error deleting object from bucket.", str(e.exception))

    def test_list_files(self):
        proxy = setup_storage_proxy_s3(BUCKET_NAME, TEMPLATE)
        filelist = [{"Key": "/test/file1.txt"}, {"Key": "/test/file2.txt"}]
        expected_return_value = ["/test/file1.txt", "/test/file2.txt"]
        client_return_value = {"Contents": filelist}
        proxy.client.list_objects_v2.return_value = client_return_value

        # Call
        return_value = proxy.list_files()

        # Assert
        proxy.client.list_objects_v2.assert_called_with(
            Prefix=proxy.root_dir, Bucket=BUCKET_NAME
        )
        self.assertEqual(expected_return_value, return_value)

    def test_list_files_error(self):
        proxy = setup_storage_proxy_s3(BUCKET_NAME, TEMPLATE)
        proxy.client.list_objects_v2.side_effect = StorageProxyException

        # Call
        with self.assertRaises(StorageProxyException) as e:
            proxy.list_files()

        # Assert
        self.assertIn("Error listing files from bucket.", str(e.exception))

    def test_verify_root_dir(self):
        client = MagicMock()
        proxy = StorageProxyS3(
            bucket_name="test-bucket", root_dir=f"test", client=client
        )

        self.assertEqual(proxy.root_dir, "test/")
