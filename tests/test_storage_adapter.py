from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock

from postmanager.storage_proxy_local import StorageProxyLocal
from postmanager.storage_adapter import StorageAdapter
from postmanager.storage_proxy_s3 import StorageProxyS3

from tests.utils.setup_objects import (
    setup_storage_adapter,
    setup_dummy_proxy,
    setup_storage_proxy_local,
    setup_storage_proxy_s3,
)


JSON_BODY = {"testing": "ok"}
BYTES_BODY = b"SOMEBYTESHERE"


class TestStorageAdapter(TestCase):
    def test_client(self):
        adapter = setup_storage_adapter()

        # Assert
        self.assertIsInstance(adapter.client, MagicMock)

    def test_root_dir(self):
        adapter = setup_storage_adapter(root_dir="test/")

        # Assert
        self.assertEqual(adapter.root_dir, "test/")

    def test_save_json(self):
        adapter = setup_storage_adapter()
        filename = "file.json"

        # Call
        adapter.save_json(JSON_BODY, filename)

        # Assert
        adapter.storage_proxy.save_json.assert_called_with(JSON_BODY, filename)

    def test_get_json(self):
        adapter = setup_storage_adapter()
        filename = "file.json"
        adapter.storage_proxy.get_json.return_value = JSON_BODY

        # Call
        data = adapter.get_json(filename)

        # Assert
        self.assertEqual(JSON_BODY, data)
        adapter.storage_proxy.get_json.assert_called_with(filename)

    def test_save_bytes(self):
        adapter = setup_storage_adapter()
        filename = "file.jpeg"

        # Call
        adapter.save_bytes(BYTES_BODY, filename)

        # Assert
        adapter.storage_proxy.save_bytes.assert_called_with(BYTES_BODY, filename)

    def test_get_bytes(self):
        adapter = setup_storage_adapter()
        filename = "file.jpeg"
        adapter.storage_proxy.get_bytes.return_value = BYTES_BODY

        # Call
        data = adapter.get_bytes(filename)

        # Assert
        self.assertEqual(BYTES_BODY, data)
        adapter.storage_proxy.get_bytes.assert_called_with(filename)

    def test_list_files(self):
        adapter = setup_storage_adapter()
        expected_return_value = ["root/file1.txt", "root/file2.txt"]
        adapter.storage_proxy.list_files.return_value = expected_return_value

        # Call
        files = adapter.list_files()

        # Assert
        self.assertEqual(files, expected_return_value)
        adapter.storage_proxy.list_files.assert_called_once()

    def test_delete_file(self):
        adapter = setup_storage_adapter()
        filename = "file.json"

        # Call
        adapter.delete_file(filename)

        # Assert
        adapter.storage_proxy.delete_file.assert_called_with(filename)

    def test_build_new_route(self):
        new_root = "post1/"
        expected_path = f"post/{new_root}"
        adapter = setup_storage_adapter(root_dir="post/")

        # Call
        new_root = adapter._build_new_root(new_root)

        # Assert
        self.assertEqual(expected_path, new_root)

    def test_build_new_root_local_storage_proxy(self):
        root_dir = "post/"
        new_root = "post1/"
        proxy = StorageProxyLocal(root_dir, MagicMock())
        adapter = StorageAdapter(proxy)
        expected_path = Path(Path().home(), ".postmanager", "data", root_dir, new_root)

        # Call
        new_root = adapter._build_new_root(new_root)

        # Assert
        self.assertEqual(expected_path, new_root)

    def test_new_storage_proxy_s3(self):
        root_dir = "test/"
        new_root = "post1/"
        proxy = setup_storage_proxy_s3("bucket-name", root_dir)
        expected_path = f"{root_dir}{new_root}"
        adapter = StorageAdapter(proxy)

        # Call
        new_proxy = adapter.new_storage_proxy(new_root)

        # Assert
        self.assertEqual(new_proxy.root_dir, expected_path)
        self.assertIsInstance(new_proxy, StorageProxyS3)

    def test_new_storage_proxy_local(self):
        root_dir = "test/"
        new_root = "post1/"
        proxy = setup_storage_proxy_local(root_dir)
        expected_path = Path(Path().home(), ".postmanager", "data", root_dir, new_root)
        adapter = StorageAdapter(proxy)

        # Call
        new_proxy = adapter.new_storage_proxy(new_root)

        # Assert
        self.assertEqual(new_proxy.root_dir, expected_path)
        self.assertIsInstance(new_proxy, StorageProxyLocal)

    def test_new_storage_proxy(self):
        new_root = "post1/"
        adapter = setup_storage_adapter("test/")

        # Call
        new_proxy = adapter.new_storage_proxy(new_root)

        # Assert
        self.assertIsInstance(new_proxy, MagicMock)

    def test_new_storage_proxy_error(self):
        new_root = "test/"
        proxy = setup_dummy_proxy(new_root)
        adapter = StorageAdapter(proxy)

        # Assert
        with self.assertRaises(Exception) as e:
            adapter.new_storage_proxy(new_root)

        self.assertIn("No storage proxy could be found", str(e.exception))
