from base64 import b64decode, b64encode
from unittest import TestCase
from unittest.mock import MagicMock

from postmanager.exception import StorageProxyException
from postmanager.media_data import MediaData

from tests.utils.setup_objects import setup_media_data

MEDIA_STR = "i0DFGEufuf83324nnmfJFHJD"
MEDIA_BYTES = b64decode(MEDIA_STR)
MEDIA_DATA_URL = "data:image/jpeg;base64," + MEDIA_STR
FILE_TYPE = "image/jpeg"
MEDIA_NAME_1 = "picture"
MEDIA_INDEX = {MEDIA_NAME_1: {"file_type": FILE_TYPE, "filename": "picture.jpeg"}}


class TestMediaData(TestCase):
    def test_init(self):
        media_data = setup_media_data()

        self.assertIsInstance(media_data.storage_proxy, MagicMock)
        self.assertEqual(media_data._unsaved_media, {})
        self.assertEqual(media_data._undeleted_media, [])

    def test_save(self):
        media_data = setup_media_data()
        media_data._delete_media = MagicMock()
        media_data._save_media = MagicMock()
        media_data._save_media_index = MagicMock()
        media_data._unsaved_media = {MEDIA_NAME_1: "data"}
        media_data._undeleted_media = [MEDIA_NAME_1]

        # Call
        media_data.save()

        # Assert
        media_data._save_media.assert_called_once()
        media_data._delete_media.assert_called_once()
        media_data._save_media_index.assert_called_once()

    def test_save_no_data(self):
        media_data = setup_media_data()
        media_data._delete_media = MagicMock()
        media_data._save_media = MagicMock()
        media_data._save_media_index = MagicMock()

        # Call
        media_data.save()

        # Assert
        media_data._save_media.assert_not_called()
        media_data._delete_media.assert_not_called()
        media_data._save_media_index.assert_not_called()

    def test_add_media(self):
        media_data = setup_media_data()
        expected_unsaved_media = {
            MEDIA_NAME_1: {"bytes": b64decode(MEDIA_STR), "file_type": "image/jpeg"}
        }

        # Call
        media_data.add_media(media_data=MEDIA_DATA_URL, media_name=MEDIA_NAME_1)

        # Assert
        self.assertEqual(media_data._unsaved_media, expected_unsaved_media)

    def test_remove_media(self):
        media_data = setup_media_data()
        media_data._unsaved_media = {
            MEDIA_NAME_1: {"bytes": b64decode(MEDIA_STR), "file_type": "image/jpeg"}
        }

        # Call
        media_data.remove_media(MEDIA_NAME_1)

        # Assert
        self.assertEqual(media_data._unsaved_media, {})

    def test_remove_media_error(self):
        media_data = setup_media_data()

        # Call
        # Assert
        value = media_data.remove_media(MEDIA_NAME_1)
        self.assertEqual(value, "Image does not exist")

    def test_delete_media(self):
        media_data = setup_media_data()

        # Call
        media_data.delete_media(MEDIA_NAME_1)

        # Assert
        self.assertIn(MEDIA_NAME_1, media_data._undeleted_media)

    def test_get_media(self):
        media_data = setup_media_data()
        media_data.media_index = MEDIA_INDEX
        media_data.storage_proxy.get_bytes.return_value = MEDIA_BYTES

        # Call
        data = media_data.get_media(MEDIA_NAME_1)

        self.assertEqual(MEDIA_DATA_URL, data)

    def test_get_media_byte64(self):
        media_data = setup_media_data()
        media_data.media_index = MEDIA_INDEX
        media_data.storage_proxy.get_bytes.return_value = MEDIA_BYTES
        expected_value = b64encode(MEDIA_BYTES)

        # Call
        data = media_data.get_media(MEDIA_NAME_1, return_format="byte64")

        self.assertEqual(expected_value, data)

    def test_get_media_byte64_str(self):
        media_data = setup_media_data()
        media_data.media_index = MEDIA_INDEX
        media_data.storage_proxy.get_bytes.return_value = MEDIA_BYTES
        expected_value = b64encode(MEDIA_BYTES).decode("utf-8")

        # Call
        data = media_data.get_media(MEDIA_NAME_1, return_format="byte64_str")

        self.assertEqual(expected_value, data)

    def test_get_media_error(self):
        media_data = setup_media_data()
        media_data.storage_proxy.get_bytes.side_effect = StorageProxyException

        # Call
        data = media_data.get_media(MEDIA_NAME_1)

        # Assert
        self.assertIn("Error getting media", data)

    def test__delete_media(self):
        media_data = setup_media_data()
        media_data.media_index = {**MEDIA_INDEX}
        media_data._undeleted_media = ["picture"]

        # Call
        media_data._delete_media()

        # Assert
        media_data.storage_proxy.delete_file.assert_called_once()
        self.assertEqual(len(media_data.media_index), 0)

    def test__delete_media_no_media(self):
        media_data = setup_media_data()

        # Call
        media_data._delete_media()

        # Assert
        media_data.storage_proxy.delete_file.assert_not_called()

    def test__delete_media_error(self):
        media_data = setup_media_data()
        media_data.media_index = {}
        media_data._undeleted_media = ["picture"]

        # Call
        media_data._delete_media()

        # Assert
        media_data.storage_proxy.delete_file.assert_not_called()

    def test__save_media(self):
        media_data = setup_media_data()
        unsaved_media = {"picture": {"file_type": "image/jpeg", "bytes": MEDIA_BYTES}}
        media_data.media_index = {}
        media_data._unsaved_media = unsaved_media

        # Call
        media_data._save_media()

        # Assert
        media_data.storage_proxy.save_bytes.assert_called_once()
        self.assertEqual(media_data.media_index, MEDIA_INDEX)
        self.assertEqual(media_data._unsaved_media, {})

    def test__save_media_overwrite(self):
        media_data = setup_media_data()
        unsaved_media = {"picture": {"file_type": "image/jpeg", "bytes": MEDIA_BYTES}}
        media_data.media_index = {**MEDIA_INDEX}
        media_data._unsaved_media = unsaved_media

        # Call
        media_data._save_media()

        # Assert
        media_data.storage_proxy.delete_file.assert_called_once()
        media_data.storage_proxy.save_bytes.assert_called_once()
        self.assertEqual(media_data.media_index, MEDIA_INDEX)
        self.assertEqual(media_data._unsaved_media, {})

    def test_get_media_file_ext(self):
        media_data = setup_media_data()

        # Call
        data = media_data._get_media_file_ext(FILE_TYPE)

        # Assert
        self.assertEqual(data, "jpeg")

    def test_get_media_file_ext_with_text(self):
        media_data = setup_media_data()

        # Call
        data = media_data._get_media_file_ext("text/plain")

        # Assert
        self.assertEqual(data, "txt")

    def test_get_media_file_prefix(self):
        media_data = setup_media_data()

        # Call
        data = media_data._get_media_file_prefix(FILE_TYPE)

        # Assert
        self.assertEqual(data, "image")

    def test_save_media_index(self):
        media_data = setup_media_data()
        media_data.media_index = MEDIA_INDEX

        # Call
        media_data._save_media_index()

        # Assert
        media_data.storage_proxy.save_json.assert_called_with(
            MEDIA_INDEX, "media_index.json"
        )

    def test_init_media_index(self):
        proxy = MagicMock()
        proxy.get_json.return_value = MEDIA_INDEX
        media_data = MediaData(proxy)

        # Assert
        self.assertEqual(media_data.media_index, MEDIA_INDEX)

    def test_init_media_index_error(self):
        proxy = MagicMock()
        proxy.get_json.side_effect = StorageProxyException
        media_data = MediaData(proxy)

        # Assert
        self.assertEqual(media_data.media_index, {})
