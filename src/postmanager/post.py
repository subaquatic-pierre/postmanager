import json
from base64 import b64decode, b64encode

import re
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
        self._undeleted_images = []

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
            self._save_images()

        if self._undeleted_images:
            self._delete_images()

        # Update image_index
        self.storage_proxy.save_json(self.image_map, "images/image_index.json")

    def add_image(self, image_uri, image_name):
        header, encoded_image = image_uri.split(",", 1)

        index1 = header.find("/") + 1
        index2 = header.find(";")
        file_format = header[index1:index2]

        self._unsaved_images[image_name] = {
            "bytes": b64decode(encoded_image),
            "format": file_format,
        }

    def remove_image(self, image_name):
        try:
            del self._unsaved_images[image_name]
        except:
            return "Image does not exist"

    def delete_image(self, image_name):
        self._undeleted_images.append(image_name)

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

    def get_image(self, image_name, format="web"):
        try:
            filename = self.image_map[image_name]

            image_bytes = self.storage_proxy.get_bytes(filename)

            image_bytes_base64 = b64encode(image_bytes)

            file_format = filename.split(".")[1]

            image_web_format = (
                f"data:image/{file_format};base64," + image_bytes_base64.decode("utf-8")
            )

            if format == "web":
                return image_web_format

            elif format == "str":
                return image_bytes_base64.decode("utf-8")

            elif format == "byte":
                return image_bytes

            elif format == "byte64":
                return image_bytes_base64

            return image_web_format

        except StorageProxyException:
            return ""

    def _delete_images(self):
        for image_name in self._undeleted_images:
            try:
                image_key = f"images/{image_name}.jpg"

                # Delete image
                self.storage_proxy.delete_object(image_key)

                # Update self image map
                del self.image_map[image_name]

            except:
                pass

        # Reset to empty array
        self._undeleted_images = []

    def _save_images(self):
        for image_name, image_data in self._unsaved_images.items():
            filename = f"images/{image_name}.{image_data['format']}"

            # Save image
            self.storage_proxy.save_bytes(image_data["bytes"], filename)

            # Update self image map
            self.image_map[image_name] = filename

        # Reset unsaved images
        self._unsaved_images = {}

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
