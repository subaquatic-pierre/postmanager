from unittest import TestCase
from unittest.mock import MagicMock

from postmanager.meta_data import MetaData

from tests.utils.setup_objects import setup_mock_meta

META_DICT = {"title": "Cool Post", "template": "post"}
POST_ID = 1


class TestMetaData(TestCase):
    def test_init(self):
        # Call
        meta_data = setup_mock_meta(POST_ID, META_DICT)

        # Assert
        self.assertEqual(meta_data.id, POST_ID)
        self.assertEqual(meta_data._attrs_list, ["title", "template", "id"])
        self.assertIsInstance(meta_data.storage_proxy, MagicMock)

    def test_to_json(self):
        meta_data = setup_mock_meta(POST_ID, META_DICT)
        expected_value = {**META_DICT, "id": POST_ID}

        # Call
        meta_data_json = meta_data.to_json()

        # Assert
        self.assertEqual(meta_data_json, expected_value)

    def test_save(self):
        meta_data = setup_mock_meta(POST_ID, META_DICT)
        expected_value = {**META_DICT, "id": POST_ID}

        # Call
        meta_data.save()

        # Assert
        meta_data.storage_proxy.save_json.assert_called_with(
            expected_value, "meta_data.json"
        )

    def test_update(self):
        meta_data = setup_mock_meta(POST_ID, META_DICT)
        new_meta_dict = {
            "id": POST_ID,
            "title": "UPDATED Post",
            "template": "UPDATED post",
            "new_attr": "UPDATED",
        }

        # Call
        meta_data.update(new_meta_dict)

        # Assert
        self.assertEqual(meta_data.title, "UPDATED Post")
        self.assertEqual(meta_data.id, POST_ID)
        self.assertEqual(meta_data.template, "UPDATED post")
        self.assertEqual(meta_data.new_attr, "UPDATED")
        self.assertEqual(meta_data._attrs_list, ["title", "template", "id", "new_attr"])

    def test_update_attrs_list(self):
        meta_data = setup_mock_meta(POST_ID, META_DICT)
        new_meta_dict = {"new_attr": "Something", "new_attr": "Overwrite"}

        # Call
        meta_data._update_attrs_list(new_meta_dict)
        self.assertEqual(meta_data._attrs_list, ["title", "template", "id", "new_attr"])

    def test_init_attrs(self):
        meta_data = setup_mock_meta(POST_ID, META_DICT)
        new_meta_dict = {"new_attr": "Something", "new_attr": "Overwrite"}

        # Call
        meta_data._init_attrs(new_meta_dict)

        # Assert
        self.assertEqual(meta_data.new_attr, "Overwrite")
        self.assertEqual(meta_data._attrs_list, ["title", "template", "id", "new_attr"])

    def test_from_json(self):
        new_dict = {**META_DICT, "id": POST_ID}

        # Call
        meta_data = MetaData.from_json(MagicMock(), new_dict)

        # Assert
        self.assertEqual(meta_data.id, POST_ID)
        self.assertEqual(meta_data.title, META_DICT["title"])
        self.assertEqual(meta_data.template, META_DICT["template"])

    def test_from_json_error(self):
        # Assert
        with self.assertRaises(Exception) as e:
            MetaData.from_json(MagicMock(), META_DICT)

        self.assertIn("meta_dict object must contain an ID key", str(e.exception))
