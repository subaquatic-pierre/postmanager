from unittest.mock import MagicMock

from postmanager.post import Post
from postmanager.meta_data import PostMetaData
from postmanager.manager import PostManager

# -----
# Create mocks
# -----
def create_manager_with_mock_proxy():
    storage_proxy = MagicMock()
    post_manager = PostManager(storage_proxy)
    return post_manager


def create_mock_meta(post_id, meta_dict={}):
    if not meta_dict:
        meta_dict = {"id": post_id, "title": "Cool Title"}

    meta_data = PostMetaData(MagicMock(), post_id, meta_dict)
    return meta_data


def create_mock_post(post_id=1, content=""):
    meta_data = create_mock_meta(post_id)

    if not content:
        content = {"Header": "Cool Header Content"}

    post = Post(MagicMock(), meta_data, content)
    return post
