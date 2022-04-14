from unittest.mock import MagicMock

from postmanager.post import Post
from postmanager.meta_data import PostMetaData
from postmanager.manager import PostManager

# -----
# Create Manager Mocks
# -----


def mock_setup_client():
    return MagicMock()


def create_manager_with_mock_proxy():
    storage_proxy = MagicMock()
    post_manager = PostManager(storage_proxy)
    return post_manager


def create_mock_meta(post_id, meta_dict):
    if not "id" in meta_dict:
        meta_dict["id"] = post_id

    meta_data = PostMetaData(MagicMock(), post_id, meta_dict)
    return meta_data


def create_mock_post(post_id, meta_dict, content):
    meta_data = create_mock_meta(post_id, meta_dict)

    post = Post(MagicMock(), meta_data, content)
    return post


# -----
# Create Storage Proxy Mocks
# -----
