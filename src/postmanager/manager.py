from postmanager.meta import PostMetaData
from postmanager.post import Post
from postmanager.http import Event

from postmanager.storage_proxy import (
    S3StorageProxy,
    MockS3StorageProxy,
    StorageProxyBase,
)
from postmanager.exception import StorageProxyException, PostManagerException


class PostManager:
    def __init__(self, storage_proxy: StorageProxyBase) -> None:
        self.storage_proxy = storage_proxy
        self._init_bucket()

    @property
    def index(self):
        obj_json = self.storage_proxy.get_json("index.json")
        return obj_json

    def list_all_files(self):
        return self.storage_proxy.list_dir()

    def get_json(self, filename):
        return self.storage_proxy.get_json(filename)

    def get_by_id(self, id) -> Post:
        id = int(id)

        meta = [meta_data for meta_data in self.index if meta_data["id"] == id]
        self._verify_meta(meta, "No blog with that ID found")

        post_meta = PostMetaData.from_json(meta[0])

        post = self.create_post(post_meta)

        return post

    def title_to_id(self, title: str) -> int:
        meta = [blog_meta for blog_meta in self.index if blog_meta["title"] == title]
        self._verify_meta(meta, "No blog with that title found")
        return meta[0]["id"]

    def create_meta(self, meta_dict: dict) -> PostMetaData:
        new_id = self.get_new_id()

        meta_dict["id"] = new_id

        post_meta = PostMetaData.from_json(meta_dict)

        return post_meta

    def create_post(self, post_meta: PostMetaData, content="") -> Post:
        post_root_dir = f"{self.storage_proxy.root_dir}{post_meta.id}/"
        post_bucket_proxy = self._create_post_bucket_proxy(post_root_dir)
        post = Post(post_bucket_proxy, post_meta, content=content)

        return post

    def save_post(self, post: Post):
        # Update index and save post
        try:
            new_index = [meta for meta in self.index]

            is_new_post = True
            for index, meta_json in enumerate(self.index):
                # Mathing meta found in index
                meta = PostMetaData.from_json(meta_json)
                if meta.id == post.meta_data.id:
                    # Set new post flag to false
                    is_new_post = False

                    # Update meta at index in place
                    new_index[index] = post.meta_data.to_json()

            if is_new_post:
                new_index.append(post.meta_data.to_json())

            post.save()
            self._update_index(new_index)

            return post

        except Exception as e:
            raise Exception(f"Post could not be saved, {str(e)}")

    def delete_post(self, id: int):
        id = int(id)
        post = self.get_by_id(id)
        post_files = post.list_files()

        # Add root dir to filenames
        post_files.append(post.storage_proxy.root_dir)
        self.storage_proxy.delete_files(post_files)

        # Update index
        new_index = [meta for meta in self.index if meta["id"] != id]
        self._update_index(new_index)

    def get_meta(self, post_id):
        for index_meta in self.index:
            meta = PostMetaData.from_json(index_meta)
            if meta.id == int(post_id):
                return meta

        raise PostManagerException("Meta data not found")

    # Private methods
    def _get_post_content(self, post_id):
        return self.storage_proxy.get_json(f"{post_id}/content.json")

    def _create_post_bucket_proxy(self, post_root_dir, mock_config={}):
        if self.storage_proxy.__class__.__name__ == "MockS3StorageProxy":
            return MockS3StorageProxy(
                self.storage_proxy.bucket_name, post_root_dir, mock_config=mock_config
            )
        else:
            return S3StorageProxy(self.storage_proxy.bucket_name, post_root_dir)

    def get_new_id(self):
        latest_id_json = self.storage_proxy.get_json("latest_id.json")
        latest_id = latest_id_json.get("latest_id")
        new_id = latest_id + 1
        self.storage_proxy.save_json({"latest_id": new_id}, "latest_id.json")
        return latest_id

    def _update_index(self, new_index: list):
        self.storage_proxy.save_json(new_index, "index.json")

    def _init_bucket(self):
        # Check if index exists
        try:
            self.storage_proxy.get_json("index.json")

        except StorageProxyException:
            self.storage_proxy.save_json([], "index.json")

        # Check if latest ID exists
        try:
            self.storage_proxy.get_json("latest_id.json")

        except StorageProxyException:
            self.storage_proxy.save_json({"latest_id": 0}, "latest_id.json")

    def _verify_meta(self, meta, error_message):
        if len(meta) > 1:
            raise PostManagerException("More than one blog with that ID found")
        elif len(meta) == 0:
            raise PostManagerException(error_message)

    # Static methods
    @staticmethod
    def setup_s3_with_event(event: Event):
        bucket_name = event.bucket_name
        path = event.path
        testing = event.testing
        mock_config = event.mock_config
        template = path.split("/")[1]

        if testing:
            storage_proxy = MockS3StorageProxy(
                bucket_name=bucket_name,
                root_dir=f"{template}/",
                mock_config=mock_config,
            )
        else:
            storage_proxy = S3StorageProxy(
                bucket_name=bucket_name,
                root_dir=f"{template}/",
            )

        post_manager = PostManager(storage_proxy)

        return post_manager

    @staticmethod
    def setup_s3(bucket_name: str, template: str = "post"):
        storage_proxy = S3StorageProxy(
            bucket_name=bucket_name,
            root_dir=f"{template}/",
        )

        post_manager = PostManager(storage_proxy)
        return post_manager
