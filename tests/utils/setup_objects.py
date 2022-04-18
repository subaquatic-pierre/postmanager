import json
from unittest.mock import MagicMock

from postmanager.post import Post
from postmanager.meta_data import MetaData
from postmanager.storage_proxy_s3 import StorageProxyS3
from postmanager.storage_proxy_local import StorageProxyLocal
from postmanager.storage_adapter import StorageAdapter
from postmanager.media_data import MediaData
from unittest.mock import MagicMock
from postmanager.manager import PostManager

# -----
# MetaData
# -----


def setup_manager():
    storage_proxy = MagicMock()
    post_manager = PostManager(storage_proxy)
    return post_manager


def setup_mock_meta(post_id, meta_dict):
    if not "id" in meta_dict:
        meta_dict["id"] = post_id

    meta_data = MetaData(MagicMock(), post_id, meta_dict)
    return meta_data


# -----
# Post
# -----


def setup_mock_post(post_id, meta_dict, content):
    meta_data = setup_mock_meta(post_id, meta_dict)

    post = Post(MagicMock(), meta_data, content)
    post.media_data = MagicMock()
    return post


# -----
# Media Data
# -----


def setup_media_data():
    media_data = MediaData(MagicMock())
    return media_data


# -----
# Storage Proxy
# -----


def setup_dummy_proxy(root_dir="test/"):
    class ProxyDummy:
        def __init__(self) -> None:
            self.root_dir = root_dir

    return ProxyDummy()


def setup_storage_proxy_local(root_dir):
    client = MagicMock()
    proxy = StorageProxyLocal(root_dir, client)
    return proxy


def setup_storage_proxy_s3(bucket_name, root_dir):
    client = MagicMock()
    return StorageProxyS3(bucket_name=bucket_name, root_dir=root_dir, client=client)


def setup_streaming_body(return_value, is_bytes=False):
    class StreamingBodyMock:
        def read(self):
            if is_bytes:
                return return_value
            else:
                return json.dumps(return_value)

    object = {"Body": StreamingBodyMock()}

    return object


# -----
# Storage Adapter
# -----


def setup_storage_adapter(root_dir="test/"):
    proxy = MagicMock()
    proxy.root_dir = root_dir
    adapter = StorageAdapter(proxy)

    return adapter
