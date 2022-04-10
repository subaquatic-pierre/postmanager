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
    ) -> None:
        self.id = meta_data.id
        self.storage_proxy = storage_proxy
        self.meta_data = meta_data
        self.content = content

        self.image_map = {}
        self._unsaved_images = {}

        # Init data from storage
        self._init_post_data()

    def save(self):
        # Save content
        self.storage_proxy.save_bytes(b"", "images/")

        # Save meta
        self.storage_proxy.save_json(self.meta_data.to_json(), "meta.json")

        # Save content
        self.storage_proxy.save_json(self.content, "content.json")

        # Save unsaved images
        if self._unsaved_images:
            for image_name, byte_str in self._unsaved_images.items():
                image_key = f"images/{image_name}.jpg"

                # Save image
                self.storage_proxy.save_bytes(byte_str, image_key)
                self.image_map[image_name] = image_key

                # Reset unsaved images
                self._unsaved_images = {}

        # Update image_index
        self.storage_proxy.save_json(self.image_map, "images/image_index.json")

    def add_image(self, byte_str, image_name):
        self._unsaved_images[image_name] = byte_str

    def remove_image(self, image_name):
        try:
            del self._unsaved_images[image_name]
        except:
            return "Image does not exist"

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
            "image_map": self.image_map,
        }

    def get_image(self, image_name, format="str"):
        try:
            image_key = self.image_map[image_name]

            byte_str = self.storage_proxy.get_bytes(image_key)
            base64_image = byte_str.decode("utf-8")

            if format == "bytes":
                byte_str

            elif format == "str":
                return base64_image

            return base64_image

        except StorageProxyException:
            return ""

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

    def _init_images(self):
        try:
            data = self.storage_proxy.get_json(f"images/image_index.json")
            self.image_map = data

        except StorageProxyException:
            self.image_map = {}

    def _init_content(self):
        try:
            data = self.storage_proxy.get_json(f"content.json")
            self.content = data

        except StorageProxyException:
            self.content = ""

    def _init_post_data(self):
        self._init_images()

        if not self.content:
            self._init_content()

    def __str__(self):
        return json.dumps(self.meta_data.to_json(), indent=2)
