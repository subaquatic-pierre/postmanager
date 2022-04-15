from unittest import TestCase
from unittest.mock import MagicMock


from tests.utils.mock_interfaces import MockStorageInterface, MockStorageProxyInterface


class TestStorageInterface(TestCase):
    def setUp(self) -> None:
        self.interface = MockStorageInterface()
        return super().setUp()

    def test_has_get_json(self):
        self.assertTrue(hasattr(self.interface, "get_json"))

    def test_has_save_json(self):
        self.assertTrue(hasattr(self.interface, "save_json"))

    def test_has_save_bytes(self):
        self.assertTrue(hasattr(self.interface, "save_bytes"))

    def test_has_get_bytes(self):
        self.assertTrue(hasattr(self.interface, "get_bytes"))

    def test_has_delete_file(self):
        self.assertTrue(hasattr(self.interface, "delete_file"))

    def test_has_list_files(self):
        self.assertTrue(hasattr(self.interface, "list_files"))


class TestStorageProxyInterface(TestCase):
    def test_proxy_client(self):
        client = MagicMock()
        proxy = MockStorageProxyInterface(client)

        self.assertIsInstance(proxy.client, MagicMock)
