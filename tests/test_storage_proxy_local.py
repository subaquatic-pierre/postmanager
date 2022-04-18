import json
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from postmanager.exception import StorageProxyException
from postmanager.storage_proxy_local import StorageProxyLocal

from tests.utils.setup_objects import setup_storage_proxy_local

ROOT_DIR = "test"
JSON_BODY = {"testing": "ok"}
BYTES_BODY = b"SOMEBYTESHERE"


class TestStorageProxyLocal(TestCase):
    def test_get_json(self):
        proxy = setup_storage_proxy_local(ROOT_DIR)
        filename = "file.json"
        file_reader = MagicMock()
        file_reader.read_text.return_value = json.dumps(JSON_BODY)
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
        file_reader = MagicMock()
        proxy.client.return_value = file_reader

        # Call
        proxy.save_json(JSON_BODY, filename)

        # Assert
        proxy.client.assert_called_with(proxy.root_dir, filename)
        file_reader.write_text.assert_called_with(json.dumps(JSON_BODY, indent=4))

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
        file_reader = MagicMock()
        proxy.client.return_value = file_reader

        # Call
        proxy.save_bytes(BYTES_BODY, filename)

        # Assert
        proxy.client.assert_called_with(proxy.root_dir, filename)
        file_reader.write_bytes.assert_called_with(BYTES_BODY)

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
        file_reader = MagicMock()
        file_reader.read_bytes.return_value = BYTES_BODY
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
        file_reader = MagicMock()
        proxy.client.return_value = file_reader

        # Call
        proxy.delete_file(filename)

        # Assert
        proxy.client.assert_called_with(proxy.root_dir, filename)
        file_reader.unlink.assert_called_with(missing_ok=True)

    def test_delete_file_error(self):
        proxy = setup_storage_proxy_local(ROOT_DIR)
        filename = "file.jpeg"
        proxy.client.side_effect = StorageProxyException

        # Call
        with self.assertRaises(StorageProxyException) as e:
            proxy.delete_file(filename)

        # Assert
        self.assertIn("Error deleting file from directory", str(e.exception))

    @patch("shutil.rmtree")
    def test_delete_directory(self, mock_call):
        proxy = setup_storage_proxy_local(ROOT_DIR)
        directory = "/directory/"

        # Call
        proxy.delete_directory(directory)

        # Assert
        mock_call.assert_called_with(directory, ignore_errors=True)

    @patch("os.walk")
    def test_list_files(self, mock_os_walk):
        mock_os_walk.return_value = (
            (
                "cur_dir",
                "child_dir",
                ("file1.txt", "file2.txt"),
            ),
        )
        expected_file_list = [
            str(Path("cur_dir")),
            str(Path("cur_dir", "file1.txt")),
            str(Path("cur_dir", "file2.txt")),
        ]

        proxy = setup_storage_proxy_local(ROOT_DIR)

        # Call
        files = proxy.list_files()

        # Expect
        self.assertEqual(expected_file_list, files)

    def test_list_files_error(self):
        proxy = setup_storage_proxy_local(ROOT_DIR)
        proxy.client.side_effect = StorageProxyException

        # Call
        with self.assertRaises(StorageProxyException) as e:
            proxy.list_files()

        # Assert
        self.assertIn("Error listing files from directory", str(e.exception))

    def test_init_root_dir(self):
        client = MagicMock()
        expected_root_dir = Path(Path.home(), ".postmanager", "data", ROOT_DIR)
        proxy = StorageProxyLocal(ROOT_DIR, client)

        self.assertEqual(proxy.root_dir, expected_root_dir)

    def test_init_root_dir_with_config(self):
        client = MagicMock()
        home_dir_path = Path("some", "home")
        config = {"home_dir": str(home_dir_path)}
        expected_root_dir = Path(home_dir_path, ROOT_DIR)
        proxy = StorageProxyLocal(ROOT_DIR, client, config)

        self.assertEqual(proxy.root_dir, expected_root_dir)
