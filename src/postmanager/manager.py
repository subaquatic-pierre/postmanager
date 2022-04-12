from postmanager.meta_data import PostMetaData
from postmanager.post import Post
from postmanager.http import Event

from postmanager.exception import StorageProxyException, PostManagerException
from postmanager.storage_base import ModelStorage, StorageProxy
from postmanager.s3_storage_proxy import (
    S3StorageProxy,
    MockS3StorageProxy,
)


class PostManager(ModelStorage):
    def __init__(self, storage_proxy: StorageProxy) -> None:
        super().__init__(storage_proxy)
        self._init_bucket()

    @property
    def index(self):
        obj_json = self.get_json("index.json")
        return obj_json

    def update_index(self, new_index: list):
        self.save_json(new_index, "index.json")

    # Post get methods
    # -----

    def get_by_id(self, id) -> Post:
        id = int(id)

        meta_dict_list = [
            meta_data for meta_data in self.index if meta_data["id"] == id
        ]
        self._verify_meta(meta_dict_list[0], "No blog with that ID found")

        # Build meta
        meta_data = self.build_meta_data(meta_dict_list[0])

        # Build post
        post = self.build_post(meta_data)

        return post

    def build_meta_data(self, meta_dict: dict):
        storage_proxy = self.new_storage_proxy(f"{meta_dict['id']}/")
        post_meta_data = PostMetaData.from_json(storage_proxy, meta_dict)
        return post_meta_data

    def build_post(self, post_meta: PostMetaData, content="") -> Post:
        storage_proxy = self.new_storage_proxy(f"{post_meta.id}/")
        post = Post(storage_proxy, post_meta, content=content)

        return post

    def title_to_id(self, title: str) -> int:
        meta = [blog_meta for blog_meta in self.index if blog_meta["title"] == title]
        self._verify_meta(meta, "No blog with that title found")
        return meta[0]["id"]

    def get_post_content(self, post_id):
        return self.get_json(f"{post_id}/content.json")

    # Post new methods
    # -----

    def new_meta_data(self, meta_dict: dict) -> PostMetaData:
        # Add ID to meta if not exists
        post_id = meta_dict.get("id", False)

        if not post_id:
            new_id = self.new_post_id()
            meta_dict["id"] = new_id

        new_storage_proxy = self.new_storage_proxy(f"{meta_dict['id']}/")
        new_meta_data = PostMetaData.from_json(new_storage_proxy, meta_dict)
        return new_meta_data

    def new_post(self, post_meta: dict, content="") -> Post:
        new_post_meta = self.new_meta_data(post_meta)

        post_storage_proxy = self.new_storage_proxy(f"{new_post_meta.id}/")
        post = Post(post_storage_proxy, new_post_meta, content=content)

        return post

    # Post update methods
    # -----

    def save_post(self, post: Post):
        # Update index and save post
        try:
            new_index = [meta for meta in self.index]

            # Check if post needs to be updated or added to index
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
            self.update_index(new_index)

            return post

        except Exception as e:
            raise Exception(f"Post could not be saved, {str(e)}")

    def delete_post(self, id: int):
        id = int(id)
        post = self.get_by_id(id)
        post_files = post.list_files()

        # Add root dir to filenames
        post_files.append(post.get_root_dir())
        self.delete_files(post_files)

        # Update index
        new_index = [meta for meta in self.index if meta["id"] != id]
        self.update_index(new_index)

    def get_meta_data(self, post_id):
        for index_meta in self.index:
            meta = PostMetaData.from_json(index_meta)
            if meta.id == int(post_id):
                return meta

        raise PostManagerException("Meta data not found")

    def new_post_id(self):
        latest_id_json = self.get_json("latest_id.json")
        latest_id = latest_id_json.get("latest_id")
        new_id = latest_id + 1

        self.save_json({"latest_id": new_id}, "latest_id.json")
        return latest_id

    # Private methods
    # -----

    def _init_bucket(self):
        # Check if index exists
        try:
            self.get_json("index.json")

        except StorageProxyException:
            self.save_json([], "index.json")

        # Check if latest ID exists
        try:
            self.get_json("latest_id.json")

        except StorageProxyException:
            self.save_json({"latest_id": 0}, "latest_id.json")

    def _verify_meta(self, meta, error_message):
        if len(meta) > 1:
            raise PostManagerException("More than one blog with that ID found")
        elif len(meta) == 0:
            raise PostManagerException(error_message)

    # Static methods
    # -----

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
