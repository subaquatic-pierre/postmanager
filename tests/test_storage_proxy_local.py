import json
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock

from postmanager.exception import StorageProxyException
from postmanager.storage_proxy_local import StorageProxyLocal

from tests.setup_objects import setup_storage_proxy_local, setup_mock_file_reader

ROOT_DIR = "test"
JSON_BODY = {"testing": "ok"}
BYTES_BODY = b"SOMEBYTESHERE"


class TestStorageProxyLocal(TestCase):
    def test_get_json(self):
        proxy = setup_storage_proxy_local(ROOT_DIR)
        filename = "file.json"
        file_reader = setup_mock_file_reader(json.dumps(JSON_BODY))
        proxy.client.return_value = file_reader

        # Call
        data = proxy.get_json(filename)

        # Assert
        proxy.client.assert_called_with(proxy.root_dir, filename)
        self.assertEqual(data, JSON_BODY)

    def test_get_json_error(self):
        proxy = setup_storage_proxy_local(ROOT_DIR)
        filename = "file.json"
        proxy.client.side_effect = StorageProxyException

        # Call
        with self.assertRaises(StorageProxyException) as e:
            proxy.get_json(filename)

        # Assert
        self.assertIn("Error fething JSON from directory", str(e.exception))

    def test_save_json(self):
        proxy = setup_storage_proxy_local(ROOT_DIR)
        filename = "file.json"
        file_reader = setup_mock_file_reader()
        proxy.client.return_value = file_reader

        # Call
        proxy.save_json(JSON_BODY, filename)

        # Assert
        proxy.client.assert_called_with(proxy.root_dir, filename)
        self.assertEqual(file_reader.call_data, json.dumps(JSON_BODY, indent=4))

    def test_save_json_error(self):
        proxy = setup_storage_proxy_local(ROOT_DIR)
        filename = "file.json"
        proxy.client.side_effect = StorageProxyException

        # Call
        with self.assertRaises(StorageProxyException) as e:
            proxy.save_json(JSON_BODY, filename)

        # Assert
        self.assertIn("Error saving JSON to directory", str(e.exception))

    def test_save_bytes(self):
        proxy = setup_storage_proxy_local(ROOT_DIR)
        filename = "file.jpeg"
        file_reader = setup_mock_file_reader()
        proxy.client.return_value = file_reader

        # Call
        proxy.save_bytes(BYTES_BODY, filename)

        # Assert
        proxy.client.assert_called_with(proxy.root_dir, filename)
        self.assertEqual(file_reader.call_data, BYTES_BODY)

    def test_save_bytes_error(self):
        proxy = setup_storage_proxy_local(ROOT_DIR)
        filename = "file.jpeg"
        proxy.client.side_effect = StorageProxyException

        # Call
        with self.assertRaises(StorageProxyException) as e:
            proxy.save_bytes(BYTES_BODY, filename)

        # Assert
        self.assertIn("Error saving bytes to directory", str(e.exception))

    def test_get_bytes(self):
        proxy = setup_storage_proxy_local(ROOT_DIR)
        filename = "file.jpeg"
        file_reader = setup_mock_file_reader(BYTES_BODY)
        proxy.client.return_value = file_reader

        # Call
        data = proxy.get_bytes(filename)

        # Assert
        proxy.client.assert_called_with(proxy.root_dir, filename)
        self.assertEqual(data, BYTES_BODY)

    def test_get_bytes_error(self):
        proxy = setup_storage_proxy_local(ROOT_DIR)
        filename = "file.jpeg"
        proxy.client.side_effect = StorageProxyException

        # Call
        with self.assertRaises(StorageProxyException) as e:
            proxy.get_bytes(filename)

        # Assert
        self.assertIn("Error getting bytes from directory", str(e.exception))

    def test_delete_file(self):
        proxy = setup_storage_proxy_local(ROOT_DIR)
        filename = "file.jpeg"
        file_reader = setup_mock_file_reader()
        proxy.client.return_value = file_reader

        # Call
        proxy.delete_file(filename)

        # Assert
        proxy.client.assert_called_with(proxy.root_dir, filename)
        self.assertIn("unlink", file_reader.method_calls)

    def test_delete_file_error(self):
        proxy = setup_storage_proxy_local(ROOT_DIR)
        filename = "file.jpeg"
        proxy.client.side_effect = StorageProxyException

        # Call
        with self.assertRaises(StorageProxyException) as e:
            proxy.delete_file(filename)

        # Assert
        self.assertIn("Error deleting file from directory", str(e.exception))

    def test_delete_directory(self):
        pass

    def test_delete_directory_error(self):
        pass

    def test_list_files(self):
        pass

    def test_list_files_error(self):
        pass

    def test_init_root_dir(self):
        pass

    def test_init_root_dir_error(self):
        pass
