from unittest import TestCase
from unittest.mock import MagicMock, call

from tests.utils import create_mock_post

from postmanager.manager import PostManager
from postmanager.post import Post
from postmanager.meta_data import PostMetaData

from postmanager.exception import StorageProxyException


class TestPostManagerMockStorageProxy(TestCase):
    """
    Test case with MagicMock as storage_proxy attribute. no storage_proxy attributes tested.
    Tests check validity of expected return values from storage_proxy. Test basic functionality
    of methods
    """

    def setUp(self) -> None:
        super().setUp()

        self.blog_manager = PostManager.setup_mock_proxy()

    def test_get_by_id(self):
        self.blog_manager._verify_meta = MagicMock()
        self.blog_manager.build_meta_data = MagicMock()
        self.blog_manager.build_post = MagicMock(return_value=create_mock_post())

        # Call
        post = self.blog_manager.get_by_id(0)

        # Assert
        self.blog_manager.storage_proxy.get_json.assert_called()
        self.blog_manager._verify_meta.assert_called()
        self.assertIsInstance(post, Post)
        self.assertEqual(post.id, 0)

    def test_new_meta_data_with_id(self):
        self.blog_manager.new_post_id = MagicMock()
        meta_dict = {"id": 1, "title": "Awesome Title"}

        # Call
        meta = self.blog_manager.new_meta_data(meta_dict)

        # Assert
        self.blog_manager.new_post_id.assert_not_called()
        self.blog_manager.storage_proxy.get_json.assert_called()
        self.assertEqual(meta.title, meta_dict.get("title"))

    def test_new_meta_data_without_id(self):
        self.blog_manager.new_post_id = MagicMock(return_value=0)
        meta_dict = {"title": "Awesome Title"}

        # Call
        meta_data = self.blog_manager.new_meta_data(meta_dict)

        # Assert
        self.blog_manager.new_post_id.assert_called()
        self.assertEqual(meta_data.title, meta_dict.get("title"))
        self.assertEqual(meta_data.id, 0)

    def test_new_post_id(self):
        self.blog_manager.storage_proxy.get_json.return_value = {"latest_id": 0}
        new_id = self.blog_manager.new_post_id()

        self.assertEqual(new_id, 0)

    def test_new_post(self):
        post_content = {"blocks": "Cool post content"}
        meta_dict = {"title": "Awesome Title"}

        self.blog_manager.storage_proxy.root_dir = "test/"
        self.blog_manager.new_post_id = MagicMock(return_value=0)
        post = self.blog_manager.new_post(meta_dict, post_content)

        self.assertEqual(post.meta_data.title, meta_dict["title"])
        self.assertEqual(post.content, post_content)

    def test_save_post(self):
        data = {"title": "Coolest"}
        post_meta: PostMetaData = self.blog_manager.new_meta(data)
        post = self.blog_manager.create_post(post_meta, {"data": "Amazing data"})
        post.save = MagicMock()

        self.blog_manager._update_index = MagicMock()

        return_value = self.blog_manager.save_post(post)

        self.blog_manager._update_index.assert_called()
        post.save.assert_called_once()
        self.assertEqual(post, return_value)

    def test_save_post_error(self):
        data = {"title": "Coolest"}
        post_meta: PostMetaData = self.blog_manager.new_meta(data)
        post: Post = self.blog_manager.create_post(post_meta, {"data": "Amazing data"})
        post.save = MagicMock(side_effect=Exception)

        self.blog_manager._update_index = MagicMock()

        with self.assertRaises(Exception) as e:
            self.blog_manager.save_post(post)

        self.blog_manager._update_index.assert_not_called()
        self.assertEqual(str(e.exception), f"Post could not be saved, ")

    def test_delete_post(self):
        data = {"title": "Coolest"}
        post_meta: PostMetaData = self.blog_manager.new_meta(data)
        post: Post = self.blog_manager.create_post(post_meta, {"data": "Amazing data"})


class TestPostManager(TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.storage_proxy = MagicMock()
        self.blog_manager = PostManager(self.storage_proxy)

    def test_manager_init_success(self):
        storage_proxy = MagicMock()
        blog_manager = PostManager(storage_proxy)

        expected_calls = [call("index.json"), call("latest_id.json")]
        call_list = blog_manager.storage_proxy.get_json.call_args_list
        self.assertEqual(call_list, expected_calls)

    def test_manager_init_setup(self):
        storage_proxy = MagicMock()
        storage_proxy.get_json.side_effect = StorageProxyException()
        blog_manager = PostManager(storage_proxy)

        expected_calls = [
            call([], "index.json"),
            call({"latest_id": 0}, "latest_id.json"),
        ]
        call_list = blog_manager.storage_proxy.save_json.call_args_list
        self.assertEqual(call_list, expected_calls)

    def test_get_index(self):
        self.storage_proxy.get_json.return_value = []
        index = self.blog_manager.index
        self.blog_manager.storage_proxy.get_json.assert_called_with("index.json")
        self.assertIsInstance(index, list)

    def test_list_all_files(self):
        self.storage_proxy.list_files.return_value = []
        all_posts = self.blog_manager.list_files()

        self.assertTrue(self.blog_manager.storage_proxy.list_files.called)
        self.assertIsInstance(all_posts, list)

    def test_new_post_id(self):
        self.storage_proxy.get_json.return_value = {"latest_id": 42}
        latest_id = self.blog_manager.new_post_id()

        self.storage_proxy.get_json.assert_called_with("latest_id.json")
        self.assertEqual(latest_id, 42)

    def test_get_json(self):
        filename = "filename.txt"
        self.storage_proxy.get_json.return_value = {}
        json_res = self.blog_manager.get_json(filename)

        self.assertIsInstance(json_res, dict)
        self.storage_proxy.get_json.assert_called_with(filename)

    def test_get_by_id_error(self):
        post_id = 0
        self.storage_proxy.get_json.return_value = [
            {"id": "noid", "title": "Sometitle", "timestamp": 000}
        ]
        with self.assertRaises(Exception) as e:
            self.blog_manager.get_by_id(post_id)

        self.assertEqual(str(e.exception), "No blog with that ID found")

    def test_title_to_id(self):
        post_id = 0
        post_title = "Sometitle"
        self.storage_proxy.get_json.return_value = [
            {"id": post_id, "title": post_title, "timestamp": 000}
        ]

        post_id = self.blog_manager.title_to_id(post_title)

        self.blog_manager.storage_proxy.get_json.assert_called_with("index.json")
        self.assertIsInstance(post_id, int)

    def test_title_to_id_error(self):
        post_id = 0
        self.storage_proxy.get_json.return_value = [
            {"id": "noid", "title": "Sometitle", "timestamp": 000}
        ]
        with self.assertRaises(Exception) as e:
            self.blog_manager.title_to_id(post_id)

        self.assertEqual(str(e.exception), "No blog with that title found")
