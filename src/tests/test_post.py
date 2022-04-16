import json
from unittest import TestCase
from unittest.mock import MagicMock

from postmanager.media_data import MediaData
from postmanager.exception import StorageProxyException
from postmanager.post import Post
from tests.utils.setup_objects import setup_mock_post, setup_mock_meta

META_DICT = {"title": "Cool Post", "template": "post"}
POST_ID = 1
CONTENT = {"Header": "Cool Content"}
BYTES_BODY = b"MEDIA_BYTES"


class TestPost(TestCase):
    def test_init(self):
        post = setup_mock_post(POST_ID, META_DICT, CONTENT)

        # Assert
        self.assertEqual(post.id, POST_ID)
        self.assertEqual(post.meta_data.to_json(), {**META_DICT, "id": POST_ID})

    def test_to_json(self):
        post = setup_mock_post(POST_ID, META_DICT, CONTENT)
        post.media_data.media_index = {}
        expected_json = {
            "meta_data": {**META_DICT, "id": POST_ID},
            "content": CONTENT,
            "media_index": {},
        }

        # Call
        post_json = post.to_json()

        # Assert
        self.assertEqual(post_json, expected_json)

    def test_update_meta_data(self):
        post = setup_mock_post(POST_ID, META_DICT, CONTENT)
        new_meta_data = {"title": "New Title"}
        post.meta_data.update = MagicMock()

        # Call
        post.update_meta_data(new_meta_data)

        # Assert
        post.meta_data.update.called_with(new_meta_data)

    def test_update_content(self):
        post = setup_mock_post(POST_ID, META_DICT, CONTENT)
        new_content = {"Header": "Cool Content", "Footer": "The Footer"}

        # Call
        post.update_content(new_content)

        # Assert
        self.assertEqual(post.content, new_content)

    def test_save(self):
        post = setup_mock_post(POST_ID, META_DICT, CONTENT)
        post.meta_data = MagicMock()

        # Call
        post.save()

        # Assert
        post.storage_proxy.save_json.assert_called_with(CONTENT, "content.json")
        post.meta_data.save.assert_called_once()
        post.media_data.save.assert_called_once()

    def test_media_index(self):
        post = setup_mock_post(POST_ID, META_DICT, CONTENT)
        post.media_data.media_index = {"picture": "cool"}

        media_index = post.media_index

        self.assertEqual(media_index, {"picture": "cool"})

    def test_add_media(self):
        filename = "image.jpeg"
        post = setup_mock_post(POST_ID, META_DICT, CONTENT)

        # Call
        post.add_media(BYTES_BODY, filename)

        # Assert
        post.media_data.add_media.assert_called_with(BYTES_BODY, filename)

    def test_remove_media(self):
        media_name = "picture"
        post = setup_mock_post(POST_ID, META_DICT, CONTENT)

        # Call
        post.remove_media(media_name)

        # Assert
        post.media_data.remove_media.assert_called_with(media_name)

    def test_delete_media(self):
        media_name = "picture"
        post = setup_mock_post(POST_ID, META_DICT, CONTENT)

        # Call
        post.delete_media(media_name)

        # Assert
        post.media_data.delete_media.assert_called_with(media_name)

    def test_get_media(self):
        media_name = "picture"
        post = setup_mock_post(POST_ID, META_DICT, CONTENT)

        # Call
        post.get_media(media_name)

        # Assert
        post.media_data.get_media.assert_called_with(media_name)

    def test_init_media_data(self):
        meta_data = setup_mock_meta(POST_ID, META_DICT)
        post = Post(MagicMock(), meta_data, CONTENT)

        # Assert
        self.assertIsInstance(post.media_data, MediaData)

    def test_init_content(self):
        post = setup_mock_post(POST_ID, META_DICT, CONTENT)

        # Assert
        post.content = CONTENT

    def test_init_content_no_content(self):
        post = setup_mock_post(POST_ID, META_DICT, "")

        # Assert
        post.storage_proxy.get_json.assert_called_with("content.json")

    def test_init_content_no_content_error(self):
        # Assert
        proxy = MagicMock()
        proxy.get_json.side_effect = StorageProxyException
        meta_data = setup_mock_meta(POST_ID, META_DICT)
        post = Post(proxy, meta_data, "")

        self.assertEqual(post.content, "")

    def test_string(self):
        post = setup_mock_post(POST_ID, META_DICT, "")
        expected = json.dumps({**META_DICT, "id": POST_ID}, indent=2)

        # Assert
        self.assertEqual(str(post), expected)
