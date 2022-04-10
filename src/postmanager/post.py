import json
import base64
from postmanager.storage_proxy import StorageProxyBase
from postmanager.meta import PostMetaData
from postmanager.exception import StorageProxyException


class Post:
    def __init__(
        self,
        storage_proxy: StorageProxyBase,
        meta_data: PostMetaData,
        content="",
        cover_image="",
    ) -> None:
        self.id = meta_data.id
        self.storage_proxy = storage_proxy
        self.meta_data = meta_data
        self._content = content
        self.cover_image: bytes = cover_image

    @property
    def title(self):
        try:
            return self.meta_data.title
        except:
            return "No title found"

    @title.setter
    def title(self, title):
        try:
            self.meta_data.title = title
        except:
            pass

    @property
    def content(self):
        try:
            self._content = self.storage_proxy.get_json("content.json")
            return self._content
        except Exception:
            return "No content found"

    @content.setter
    def content(self, content):
        self._content = content

    def save(self):
        # Save content
        self.storage_proxy.save_bytes(b"", "images/")
        # Save meta
        self.storage_proxy.save_json(self.meta_data.to_json(), "meta.json")
        self.storage_proxy.save_json(self._content, "content.json")

        # Save images, for image in images
        if self.cover_image:
            self.storage_proxy.save_bytes(self.cover_image, f"images/cover_image.jpg")

    def list_image_urls(self):
        image_keys = self.storage_proxy.list_dir(f"images/")
        urls = [f"{self._base_image_url()}{image_key}" for image_key in image_keys]
        return urls

    def list_files(self):
        return self.storage_proxy.list_dir()

    def to_json(self):

        return {
            "meta_data": self.meta_data.to_json(),
            "content": self.content,
            "images": {"cover_image": self.get_cover_image()},
        }

    def get_cover_image(self, format="str") -> str:
        try:
            byte_str = self.storage_proxy.get_bytes(f"images/cover_image.jpg")
            base64_image = byte_str.decode("utf-8")

            if format == "bytes":
                byte_str

            elif format == "str":
                return base64_image

            return base64_image

        except StorageProxyException:
            return ""

    def _base_image_url(self):
        return f"https://{self.storage_proxy.bucket_name}.s3.amazonaws.com/"

    def __str__(self):
        return json.dumps(self.meta_data.to_json(), indent=2)
