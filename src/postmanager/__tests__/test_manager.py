from unittest import TestCase
from unittest.mock import MagicMock, call

from postmanager.manager import PostManager
from postmanager.post import Post
from postmanager.meta import PostMetaData
from postmanager.exception import StorageProxyException


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
        self.storage_proxy.list_dir.return_value = []
        all_posts = self.blog_manager.list_all_files()

        self.assertTrue(self.blog_manager.storage_proxy.list_dir.called)
        self.assertIsInstance(all_posts, list)

    def test_get_new_id(self):
        self.storage_proxy.get_json.return_value = {"latest_id": 42}
        latest_id = self.blog_manager.get_new_id()

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


class TestPostManagerWithPost(TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.storage_proxy = MagicMock()
        self.blog_manager = PostManager(self.storage_proxy)
        self.post_title = "Amazing Post"
        self.post_content = {"blocks": "Cool post content"}

    def test_get_by_id(self):
        post_id = 0
        self.storage_proxy.get_json.return_value = [
            {"id": post_id, "title": "Sometitle", "timestamp": 000}
        ]

        post = self.blog_manager.get_by_id(post_id)

        self.blog_manager.storage_proxy.get_json.assert_called()
        self.assertIsInstance(post, Post)
        self.assertEqual(post.id, post_id)

    def test_create_meta_from_json(self):
        meta_dict = {"title": "Awesome Title"}
        meta = self.blog_manager.create_meta(meta_dict)

        self.assertEqual(meta.title, meta_dict.get("title"))

    def test_create_post(self):
        meta_dict = {"title": "Awesome Title"}
        post_meta = self.blog_manager.create_meta(meta_dict)
        post = self.blog_manager.create_post(post_meta, self.post_content)

        post_root_dir = f"{self.blog_manager.storage_proxy.root_dir}{post.id}/"

        self.storage_proxy.get_json.return_value = self.post_content

        self.assertEqual(post.title, meta_dict["title"])
        self.assertEqual(post.content, "No content found")
        self.assertTrue(post.storage_proxy.root_dir.endswith("/"))
        self.assertEqual(post.storage_proxy.root_dir, post_root_dir)

    def test_save_post(self):
        data = {"title": "Coolest"}
        post_meta: PostMetaData = self.blog_manager.create_meta(data)
        post = self.blog_manager.create_post(post_meta, {"data": "Amazing data"})
        post.save = MagicMock()

        self.blog_manager._update_index = MagicMock()

        return_value = self.blog_manager.save_post(post)

        self.blog_manager._update_index.assert_called()
        post.save.assert_called_once()
        self.assertEqual(post, return_value)

    def test_save_post_error(self):
        data = {"title": "Coolest"}
        post_meta: PostMetaData = self.blog_manager.create_meta(data)
        post: Post = self.blog_manager.create_post(post_meta, {"data": "Amazing data"})
        post.save = MagicMock(side_effect=Exception)

        self.blog_manager._update_index = MagicMock()

        with self.assertRaises(Exception) as e:
            self.blog_manager.save_post(post)

        self.blog_manager._update_index.assert_not_called()
        self.assertEqual(str(e.exception), f"Post could not be saved, ")

    def test_delete_post(self):
        data = {"title": "Coolest"}
        post_meta: PostMetaData = self.blog_manager.create_meta(data)
        post: Post = self.blog_manager.create_post(post_meta, {"data": "Amazing data"})
