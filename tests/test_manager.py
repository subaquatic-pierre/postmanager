from pathlib import Path
import pytest
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from postmanager.post import Post
from postmanager.http import Event
from postmanager.manager import PostManager
from postmanager.meta_data import MetaData
from postmanager.storage_proxy_local import StorageProxyLocal
from postmanager.exception import StorageProxyException, PostManagerException

from tests.utils.setup_objects import (
    setup_mock_meta,
    setup_mock_post,
    setup_manager,
)

META_DICT_1 = {"id": 1, "title": "Cool Title", "template": "post"}
META_DICT_3 = {"id": 3, "title": "Post Number Three", "template": "post"}
POST_CONTENT = {"Header": "Cool Header Content"}
INDEX_JSON = [
    {"id": 1, "title": "First Post", "template": "post"},
    {"id": 2, "title": "Second Post", "template": "post"},
]


def test_index(manager):
    manager.storage_proxy.get_json.return_value = INDEX_JSON

    # Call
    index = manager.index

    # Assert
    manager.storage_proxy.get_json.assert_called()
    assert len(index) == 2
    assert index[0]["title"] == "First Post"


def test_update_index(manager):
    # Call
    manager.update_index(INDEX_JSON)

    # Assert
    manager.storage_proxy.save_json.assert_called_with(INDEX_JSON, "index.json")


def test_get_by_id(manager):
    meta_index = [
        {"id": 1, "title": "First Post", "template": "post"},
        {"id": 2, "title": "Second Post", "template": "post"},
    ]
    manager.storage_proxy.get_json.return_value = meta_index
    manager._verify_meta = MagicMock()
    manager._build_meta_data = MagicMock()
    manager._build_post = MagicMock(
        return_value=setup_mock_post(1, META_DICT_1, POST_CONTENT)
    )

    # Call
    post = manager.get_by_id(1)

    # Assert
    manager.storage_proxy.get_json.assert_called()
    manager._verify_meta.assert_called()
    assert isinstance(post, Post)
    assert post.id == 1


def test_build_meta_data(manager):
    meta_dict = {"id": 1, "title": "Cool Title"}

    # Call
    meta_data = manager._build_meta_data(meta_dict)

    # Assert
    assert isinstance(meta_data, MetaData)
    assert meta_data.title == "Cool Title"
    assert meta_data.id == 1


def test_build_post(manager):

    meta_data = setup_mock_meta(1, META_DICT_1)

    # Call
    post = manager._build_post(meta_data, POST_CONTENT)

    # Assert
    assert post.id == 1
    assert post.content == POST_CONTENT


def test_title_to_id(manager):
    manager._verify_meta = MagicMock()
    manager.storage_proxy.get_json.return_value = INDEX_JSON

    # Call
    post_id = manager.title_to_id("First Post")

    # Assert
    assert post_id == 1


def test_get_post_content(manager):

    POST_CONTENT = {"Cool": "Content"}
    manager.storage_proxy.get_json.return_value = POST_CONTENT

    # Call
    content = manager.get_post_content(1)

    # Assert
    assert content == POST_CONTENT


def test_new_post_id(manager):

    manager.storage_proxy.get_json.return_value = {"latest_id": 0}

    # Call
    new_id = manager.new_post_id()

    # Assert
    assert new_id == 0


def test_new_meta_data_with_id(manager):

    manager.new_post_id = MagicMock()
    meta_dict = {"id": 1, "title": "Awesome Title"}

    # Call
    meta = manager.new_meta_data(meta_dict)

    # Assert
    manager.new_post_id.assert_not_called()
    manager.storage_proxy.get_json.assert_called()
    assert meta.title == meta_dict.get("title")


def test_new_meta_data_without_id(manager):
    manager.new_post_id = MagicMock(return_value=0)
    meta_dict = {"title": "Awesome Title"}

    # Call
    meta_data = manager.new_meta_data(meta_dict)

    # Assert
    manager.new_post_id.assert_called()
    assert meta_data.title == meta_dict.get("title")
    assert meta_data.id == 0


def test_new_post(manager):
    POST_CONTENT = {"blocks": "Cool post content"}
    meta_dict = {"title": "Awesome Title"}
    manager.storage_proxy.root_dir = "test/"
    manager.new_post_id = MagicMock(return_value=0)

    # Call
    post = manager.new_post(meta_dict, POST_CONTENT)

    # Assert
    assert post.meta_data.title == meta_dict["title"]
    assert post.content == POST_CONTENT


def test_save_post_new(manager):
    new_post = setup_mock_post(3, META_DICT_1, POST_CONTENT)
    new_post.save = MagicMock()
    manager.update_index = MagicMock()
    manager.storage_proxy.get_json.return_value = INDEX_JSON

    # Call
    returned_post = manager.save_post(new_post)

    # Assert
    manager_index_copy = [item for item in INDEX_JSON]
    manager_index_copy.append(new_post.meta_data.to_json())
    manager.update_index.assert_called_with(manager_index_copy)
    new_post.save.assert_called_once()
    assert returned_post == new_post


def test_save_post_update(manager):

    updated_post_meta = {"id": 1, "title": "Awesome New Title", "template": "post"}
    updated_INDEX_JSON = [
        updated_post_meta,
        {"id": 2, "title": "Second Post", "template": "post"},
    ]

    post = setup_mock_post(1, updated_post_meta, POST_CONTENT)
    post.save = MagicMock()
    manager.update_index = MagicMock()
    manager.storage_proxy.get_json.return_value = INDEX_JSON

    # Call
    returned_post = manager.save_post(post)

    # Assert
    manager.update_index.assert_called_with(updated_INDEX_JSON)
    assert updated_post_meta == returned_post.meta_data.to_json()


def test_save_post_error(manager):
    new_post = setup_mock_post(1, META_DICT_1, POST_CONTENT)
    new_post.save = MagicMock(side_effect=Exception)
    manager.update_index = MagicMock()
    manager.storage_proxy.get_json.return_value = INDEX_JSON

    # Call
    # Assert
    with pytest.raises(PostManagerException) as e:
        manager.save_post(new_post)

    manager.update_index.assert_not_called()
    assert f"Post could not be saved, " in str(e.value)


def test_delete_post_local_proxy(manager):
    manager.storage_proxy = StorageProxyLocal("test", MagicMock())
    manager.storage_proxy.get_json = MagicMock(return_value=INDEX_JSON)
    manager.storage_proxy.delete_directory = MagicMock()
    manager.update_index = MagicMock()

    # Call
    manager.delete_post(1)

    # Assert
    manager.storage_proxy.delete_directory.assert_called_once()
    manager.update_index.assert_called_once()


def test_delete_post(manager):
    post = setup_mock_post(1, META_DICT_1, POST_CONTENT)
    post.list_files = MagicMock(return_value=["first.txt"])
    post.storage_proxy.root_dir = "test"
    post.delete_file = MagicMock()
    manager.get_by_id = MagicMock(return_value=post)
    manager.delete_file = MagicMock()

    # Call
    manager.delete_post(1)

    # Assert
    post.delete_file.assert_called_once()
    manager.delete_file.assert_called_once()


def test_get_meta_data(manager):
    manager.storage_proxy.get_json.return_value = INDEX_JSON

    # Call
    meta_data = manager.get_meta_data(1)

    # Assert
    assert meta_data.id == 1
    assert isinstance(meta_data, MetaData)


def test_get_meta_data_error(manager):

    manager.storage_proxy.get_json.return_value = INDEX_JSON

    # Call
    # Assert
    with pytest.raises(PostManagerException) as e:
        manager.get_meta_data(5)

    assert "Meta data not found" in str(e)


def test_init_storage(manager):

    manager.storage_proxy.get_json.return_value = INDEX_JSON

    # Assert
    call_args = manager.storage_proxy.get_json.call_args_list
    expexted_call_args = [call("index.json"), call("latest_id.json")]
    assert call_args == expexted_call_args


def test_init_storage_error(manager):
    storage_proxy = MagicMock()
    storage_proxy.get_json.side_effect = StorageProxyException
    storage_proxy.save_json = MagicMock()
    manager = PostManager(storage_proxy)

    # Assert
    call_args = manager.storage_proxy.save_json.call_args_list
    expexted_call_args = [
        call([], "index.json"),
        call({"latest_id": 0}, "latest_id.json"),
    ]
    assert call_args == expexted_call_args


def test_verify_meta_more_than_one_found(manager):

    meta_data_list = [
        {"id": 1, "title": "First Post", "template": "post"},
        {"id": 2, "title": "Second Post", "template": "post"},
    ]

    with pytest.raises(PostManagerException) as e:
        manager._verify_meta(meta_data_list)

    assert "More than one blog with that ID found" in str(e.value)


def test_verify_meta_not_found(manager):
    meta_data_list = []
    error_message = "No blog with that ID found"

    with pytest.raises(PostManagerException) as e:
        manager._verify_meta(meta_data_list, error_message)

    assert error_message in str(e.value)


# -----
# Static methods
# -----


@patch("postmanager.manager.setup_s3_client")
def test_setup_s3_with_event(mock_client_setup):
    event_dict = {
        "bucket_name": "bucket-name",
        "path": "path/post",
        "test_api": False,
    }
    event = Event(event_dict)

    # Call
    manager = PostManager.setup_s3_with_event(event)

    # Assert
    assert manager.storage_proxy.root_dir == "post/"
    assert manager.storage_proxy.bucket_name == "bucket-name"
    assert isinstance(manager, PostManager)
    mock_client_setup.assert_called_once()


def test_setup_s3_with_event_testing():
    event_dict = {
        "bucket_name": "bucket-name",
        "path": "path/post",
        "test_api": True,
    }
    event = Event(event_dict)

    # Call
    manager = PostManager.setup_s3_with_event(event)

    # Assert
    assert manager.storage_proxy.root_dir == "post/"
    assert manager.storage_proxy.bucket_name == "bucket-name"
    assert isinstance(manager, PostManager)


@patch("postmanager.manager.setup_s3_client")
def test_setup_setup_s3(mock_client_setup):
    # Call
    manager = PostManager.setup_s3("bucket-name", "blog")

    # Assert
    assert manager.storage_proxy.root_dir == "blog/"
    assert manager.storage_proxy.bucket_name == "bucket-name"
    assert isinstance(manager, PostManager)
    mock_client_setup.assert_called_once()


@patch("postmanager.manager.setup_local_client")
def test_setup_local(mock_client_setup):
    template_name = "blog"
    home_path = Path.home()
    data_path = Path(home_path, ".postmanager", "data", template_name)

    # Call
    manager = PostManager.setup_local(template_name)

    # Assert
    assert manager.storage_proxy.root_dir == data_path
    assert isinstance(manager, PostManager)
    mock_client_setup.assert_called_once()


def test_setup_setup_s3_with_testing():
    # Call
    manager = PostManager.setup_s3("bucket-name", "blog", testing=True)

    # Assert
    assert manager.storage_proxy.root_dir == "blog/"
    assert manager.storage_proxy.bucket_name == "bucket-name"
    assert isinstance(manager, PostManager)


def test_setup_local_with_testing():
    template_name = "blog"
    # Call
    manager = PostManager.setup_local(template_name, testing=True)

    # Assert
    home_path = Path.home()
    data_path = Path(home_path, ".postmanager", "data", template_name)
    assert manager.storage_proxy.root_dir == data_path
    assert isinstance(manager, PostManager)
