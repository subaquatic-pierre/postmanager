from time import time
from postmanager.meta import PostMeta
from postmanager.post import Post
from postmanager.event import Event
from postmanager.proxy import BucketProxy, MockBucketProxy, BucketProxyBase
from postmanager.exception import BucketProxyException, PostManagerException
from postmanager.utils import BUCKET_NAME


class PostManager:
    def __init__(self, bucket_proxy: BucketProxyBase, template_name: str) -> None:
        self.bucket_proxy = bucket_proxy
        self.template_name = template_name
        self._init_bucket()

    @property
    def index(self):
        obj_json = self.bucket_proxy.get_json("index.json")
        return obj_json

    def list_all_files(self):
        return self.bucket_proxy.list_dir()

    def get_json(self, filename):
        return self.bucket_proxy.get_json(filename)

    def get_by_id(self, id) -> Post:
        id = int(id)

        meta = [meta_data for meta_data in self.index if meta_data["id"] == id]
        self._verify_meta(meta, "No blog with that ID found")
        post_meta = PostMeta.from_json(
            {
                "id": id,
                "title": meta[0]["title"],
                "timestamp": meta[0]["timestamp"],
                "template_name": self.template_name,
            }
        )

        content = self._get_post_content(post_meta.id)
        post = self.create_post(post_meta, content)

        return post

    def title_to_id(self, title: str) -> int:
        meta = [blog_meta for blog_meta in self.index if blog_meta["title"] == title]
        self._verify_meta(meta, "No blog with that title found")
        return meta[0]["id"]

    def create_meta(self, title: str) -> PostMeta:
        template_name = self.template_name
        timestamp = int(time())
        new_id = self._get_latest_id()

        post_meta = PostMeta.from_json(
            {
                "id": new_id,
                "title": title,
                "timestamp": timestamp,
                "template_name": template_name,
            }
        )

        return post_meta

    def create_post(self, post_meta: PostMeta, content) -> Post:
        post_root_dir = f"{self.bucket_proxy.root_dir}{post_meta.id}/"

        post_bucket_proxy = self._create_post_bucket_proxy(post_root_dir)

        post = Post(post_bucket_proxy, post_meta, content)

        return post

    def save_post(self, post: Post):
        # Update index and save post
        try:
            new_index = [meta for meta in self.index]

            is_new_post = True
            for index, meta_json in enumerate(self.index):
                # Mathing meta found in index
                meta = PostMeta.from_json(meta_json)
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
        post_files.append(post.bucket_proxy.root_dir)
        self.bucket_proxy.delete_files(post_files)

        # Update index
        new_index = [meta for meta in self.index if meta["id"] != id]
        self._update_index(new_index)

    def get_meta(self, post_id):
        for index_meta in self.index:
            meta = PostMeta.from_json(index_meta)
            if meta.id == int(post_id):
                return meta

        raise PostManagerException("Meta data not found")

    # Private methods
    def _get_post_content(self, post_id):
        return self.bucket_proxy.get_json(f"{post_id}/content.json")

    def _create_post_bucket_proxy(self, post_root_dir, mock_config={}):
        if self.bucket_proxy.__class__.__name__ == "MockBucketProxy":
            return MockBucketProxy(
                self.bucket_proxy.bucket_name, post_root_dir, mock_config=mock_config
            )
        else:
            return BucketProxy(self.bucket_proxy.bucket_name, post_root_dir)

    def _get_latest_id(self):
        return len(self.index)

    def _update_index(self, new_index: list):
        self.bucket_proxy.save_json(new_index, "index.json")

    def _init_bucket(self):
        try:
            self.bucket_proxy.get_json("index.json")

        except BucketProxyException:
            self.bucket_proxy.save_json([], "index.json")

    def _verify_meta(self, meta, error_message):
        if len(meta) > 1:
            raise PostManagerException("More than one blog with that ID found")
        elif len(meta) == 0:
            raise PostManagerException(error_message)

    # Static methods
    def setup_api_post_manager(event: Event):
        path = event.path
        testing = event.testing
        mock_config = event.mock_config
        template_str = path.split("/")[1]
        template_name = template_str.capitalize()

        if testing:
            bucket_proxy = MockBucketProxy(
                bucket_name=BUCKET_NAME,
                root_dir=f"{template_str}/",
                mock_config=mock_config,
            )
        else:
            bucket_proxy = BucketProxy(
                bucket_name=BUCKET_NAME,
                root_dir=f"{template_str}/",
            )

        post_manager = PostManager(bucket_proxy, template_name)

        return post_manager
