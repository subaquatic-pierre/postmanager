import json
import inspect
from unittest.mock import MagicMock

from postmanager.post import Post
from postmanager.meta_data import PostMetaData
from postmanager.manager import PostManager
from postmanager.storage_proxy_s3 import StorageProxyS3
from postmanager.storage_proxy_local import StorageProxyLocal

# -----
# Manager Mocks
# -----


def setup_manager():
    storage_proxy = MagicMock()
    post_manager = PostManager(storage_proxy)
    return post_manager


def setup_mock_meta(post_id, meta_dict):
    if not "id" in meta_dict:
        meta_dict["id"] = post_id

    meta_data = PostMetaData(MagicMock(), post_id, meta_dict)
    return meta_data


def setup_mock_post(post_id, meta_dict, content):
    meta_data = setup_mock_meta(post_id, meta_dict)

    post = Post(MagicMock(), meta_data, content)
    return post


# -----
# Storage Proxy
# -----


def setup_storage_proxy_local(root_dir):
    client = MagicMock()
    proxy = StorageProxyLocal(root_dir, client)
    return proxy


def setup_storage_proxy_s3(bucket_name, template):
    client = MagicMock()
    return StorageProxyS3(
        bucket_name=bucket_name, root_dir=f"{template}/", client=client
    )


def setup_streaming_body(return_value, is_bytes=False):
    class StreamingBodyMock:
        def read(self):
            if is_bytes:
                return return_value
            else:
                return json.dumps(return_value)

    object = {"Body": StreamingBodyMock()}

    return object


def setup_mock_file_reader(return_value=""):
    class FileReader:
        def __init__(self) -> None:
            self.call_data = None
            self.method_calls = []

        def read_text(self):
            return return_value

        def read_bytes(self):
            return return_value

        def write_text(self, data):
            self.call_data = data
            return MagicMock()

        def write_bytes(self, data):
            self.call_data = data
            return MagicMock()

        def unlink(self, *args, **kwargs):
            frame = inspect.currentframe()
            self.method_calls.append(inspect.getframeinfo(frame).function)

    return FileReader()
