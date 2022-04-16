from typing import List, Optional
from unittest.mock import MagicMock
from postmanager.meta_data import MetaData
from postmanager.post import Post
from postmanager.http import Event

from postmanager.config import setup_s3_client, setup_local_client
from postmanager.exception import StorageProxyException, PostManagerException
from postmanager.interfaces import StorageProxy
from postmanager.storage_adapter import StorageAdapter
from postmanager.storage_proxy_local import StorageProxyLocal
from postmanager.storage_proxy_s3 import StorageProxyS3


class PostManager(StorageAdapter):
    """Main PostManager class used to manager all post operations."""

    def __init__(self, storage_proxy: StorageProxy) -> None:
        """
        Args:
            storage_proxy (StorageProxy): Storage proxy used
             to communicate with storage system.
        """

        super().__init__(storage_proxy)
        self._init_storage()

    @property
    def index(self):
        """
        Get meta data of all posts managed by this manager.
        """
        obj_json = self.get_json("index.json")
        return obj_json

    def update_index(self, new_index: List) -> None:
        """Writes new index to storage.

        Args:
            new_index (List): New index list to be written to storage.

        Returns:
            None: No return value

        """
        self.save_json(new_index, "index.json")

    # Post get methods
    # -----

    def get_by_id(self, post_id: int) -> Post:
        """Fetch an existing post from storage.

        Args:
            new_index (List): New index list to be written to storage.

        Returns:
            Post: Raises PostManagerException if not found.

        """
        post_id = int(post_id)

        meta_dict_list = [
            meta_data for meta_data in self.index if meta_data["id"] == post_id
        ]

        self._verify_meta(meta_dict_list, "No blog with that ID found")

        # Build meta
        meta_data = self._build_meta_data(meta_dict_list[0])

        # Build post
        post = self._build_post(meta_data)

        return post

    def title_to_id(self, title: str) -> int:
        """Get ID number of given post title.

        Args:
            title (str): Title of post.

        Returns:
            int:  Raises PostManagerException if not found.

        """
        meta = [blog_meta for blog_meta in self.index if blog_meta["title"] == title]
        self._verify_meta(meta, "No blog with that title found")
        return meta[0]["id"]

    def get_post_content(self, post_id: int) -> dict:
        """Get content of post with given id.

        Args:
            post_id (int): ID of the post.

        Returns:
            dict:  JSON content of post.

        """
        content = self.get_json(f"{post_id}/content.json")
        return content

    # Post new methods
    # -----

    def new_post_id(self):
        """Get the latest post ID which can be used for a new post.

        Returns:
            int:  New post ID, used to create new post.

        """
        latest_id_json = self.get_json("latest_id.json")
        latest_id = latest_id_json.get("latest_id")
        new_id = latest_id + 1

        self.save_json({"latest_id": new_id}, "latest_id.json")
        return latest_id

    def new_meta_data(self, meta_dict: dict) -> MetaData:
        """Create new MetaData object.

        Args:
            meta_dict (dict):  New post ID, used to create new post.

        Returns:
            MetaData: New MetaData object to be used to create new post.

        """
        # Add ID to meta if not exists
        post_id = meta_dict.get("id", False)

        if not post_id:
            new_id = self.new_post_id()
            meta_dict["id"] = new_id

        new_storage_proxy = self.new_storage_proxy(f"{meta_dict['id']}/")
        new_meta_data = MetaData.from_json(new_storage_proxy, meta_dict)
        return new_meta_data

    def new_post(self, post_meta: dict, content="") -> Post:
        """Create new Post object.

        Args:
            meta_dict (dict):  MetaData object associated with this post.
            content (obj, optional): JSON parsable object or string.

        Returns:
            Post: New Post object.

        """
        new_post_meta = self.new_meta_data(post_meta)

        post_storage_proxy = self.new_storage_proxy(f"{new_post_meta.id}/")
        post = Post(post_storage_proxy, new_post_meta, content=content)

        return post

    # Post update methods
    # -----

    def save_post(self, post: Post) -> Post:
        """Save new Post to storage.

        Args:
            post (Post):  New Post object intented to save.

        Returns:
            Post: Post object just saved, raises PostManagerExecption on error.

        """
        # Update index and save post
        try:
            new_index = [meta for meta in self.index]

            # Check if post needs to be updated or added to index
            is_new_post = True
            for index, meta_json in enumerate(self.index):
                # Mathing meta found in index
                if meta_json["id"] == post.meta_data.id:
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
            raise PostManagerException(f"Post could not be saved, {str(e)}")

    def delete_post(self, post_id: int):
        """Remove post and all corresponding data from storage.

        Args:
            post_id (int):  ID of post to be deleted.

        Returns:
            None: Raises PostManagerExecption on error.

        """
        post_id = int(post_id)
        post = self.get_by_id(post_id)

        if isinstance(self.storage_proxy, StorageProxyLocal):
            self.storage_proxy.delete_directory(post.root_dir)

        else:
            all_post_files = post.list_files()
            file_keys = [
                filename.replace(
                    post.root_dir,
                    "",
                )
                for filename in all_post_files
            ]

            for key in file_keys:
                post.delete_file(key)
            self.delete_file(f"{post.id}/")

        # Update index
        new_index = [meta for meta in self.index if meta["id"] != post_id]
        self.update_index(new_index)

    def get_meta_data(self, post_id: int) -> MetaData:
        """Get MetaData for corresponding post ID.

        Args:
            post_id (int):  ID of post to be deleted.

        Returns:
            MetaData: Raises PostManagerExecption on error.

        """
        for index_meta in self.index:
            new_proxy = self.new_storage_proxy(f"{post_id}/")
            meta = MetaData.from_json(new_proxy, index_meta)
            if meta.id == int(post_id):
                return meta

        raise PostManagerException("Meta data not found")

    # Private methods
    # -----

    def _build_meta_data(self, meta_dict: dict):
        storage_proxy = self.new_storage_proxy(f"{meta_dict['id']}/")
        post_meta_data = MetaData.from_json(storage_proxy, meta_dict)
        return post_meta_data

    def _build_post(self, post_meta: MetaData, content="") -> Post:
        storage_proxy = self.new_storage_proxy(f"{post_meta.id}/")
        post = Post(storage_proxy, post_meta, content=content)

        return post

    def _init_storage(self):
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

    def _verify_meta(self, meta_data_list: List[dict], error_message=""):
        if len(meta_data_list) > 1:
            raise PostManagerException("More than one blog with that ID found")
        elif len(meta_data_list) == 0:
            raise PostManagerException(error_message)

    # -----
    # Static methods
    # -----

    @staticmethod
    def setup_s3_with_event(event: Event):
        """Create new PostManager object for S3 storage with an Event object.

        Args:
            event (Event):  Event object, usually created with Request event.

        Returns:
            PostManager: New instance of PostManager, configured to use with AWS S3.

        """
        bucket_name = event.bucket_name
        path = event.path
        testing = event.testing
        template = path.split("/")[1]

        if testing:
            client = MagicMock()
        else:
            client = setup_s3_client()

        storage_proxy = StorageProxyS3(
            bucket_name=bucket_name, root_dir=f"{template}/", client=client
        )

        post_manager = PostManager(storage_proxy)

        return post_manager

    @staticmethod
    def setup_s3(
        bucket_name: str, template: str = "post", client_config={}, testing=False
    ):
        """Create new PostManager object for AWS S3 storage.

        Args:
            bucket_name (str):  Name of the S3 bucket to use as storage.
            template (str, optional):  Name of template of Post, used as root_dir configuration.
            client_config (obj, optional): Configuration used to configure s3_client
            testing (bool, optional): Weather testing is True will determine client type.

        Returns:
            PostManager: New instance of PostManager, configured to use with AWS S3.

        """

        if testing:
            client = MagicMock()
        else:
            client = setup_s3_client()

        storage_proxy = StorageProxyS3(
            bucket_name=bucket_name, root_dir=f"{template}/", client=client
        )

        post_manager = PostManager(storage_proxy)
        return post_manager

    @staticmethod
    def setup_local(template: str = "post", client_config={}, testing=False):
        """Create new PostManager object for AWS S3 storage.

        Args:
            template (str, optional):  Name of template of Post, used as root_dir configuration.
            client_config (obj, optional): Configuration used to configure local_client
            testing (bool, optional): Weather testing is True will determine client type.

        Returns:
            PostManager: New instance of PostManager, configured to use with local file storage.

        """

        if testing:
            client = MagicMock()
        else:
            client = setup_local_client()

        storage_proxy = StorageProxyLocal(root_dir=f"{template}/", client=client)

        post_manager = PostManager(storage_proxy)
        return post_manager
