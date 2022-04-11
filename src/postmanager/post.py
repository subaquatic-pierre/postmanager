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

        self.media_index = {}
        self._unsaved_media = {}
        self._undeleted_media = []

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
        if self._unsaved_media:
            self._save_media()

        if self._undeleted_media:
            self._delete_media()

        # Update image_index
        self._save_media_index()

    def to_json(self):

        return {
            "meta_data": self.meta_data.to_json(),
            "content": self.content,
            "media_index": self.media_index,
        }

    # Media methods
    # -----

    def add_media(
        self, media_data, media_name, media_data_format="data_url", overwrite=True
    ):
        # TODO: Check if media data format is data_url
        # Handle none data_url media format

        # TODO: Check if media_name exists, do not overwrite if overwrite is False

        data_header, encoded_image = media_data.split(",", 1)

        index1 = data_header.find(":") + 1
        index2 = data_header.find(";")

        file_type = data_header[index1:index2]

        self._unsaved_media[media_name] = {
            "bytes": b64decode(encoded_image),
            "file_type": file_type,
        }

    def remove_media(self, media_name):
        try:
            del self._unsaved_media[media_name]
        except:
            return "Image does not exist"

    def delete_media(self, media_name):
        self._undeleted_media.append(media_name)

    def get_media(self, media_name, return_format="data_url"):
        try:
            media_data = self.media_index[media_name]
            filename = media_data["filename"]

            image_bytes = self.storage_proxy.get_bytes(filename)

            image_bytes_base64 = b64encode(image_bytes)

            file_prefix = self._get_media_file_prefix(media_data["file_type"])
            file_ext = self._get_media_file_ext(media_data["file_type"])

            image_data_url = (
                f"data:{file_prefix}/{file_ext};base64,"
                + image_bytes_base64.decode("utf-8")
            )

            if return_format == "byte64":
                return image_bytes_base64

            elif return_format == "byte64_str":
                return image_bytes_base64.decode("utf-8")

            return image_data_url

        except StorageProxyException as e:
            return f"{str(e)}"

    # List files methods
    # -----

    def list_files(self):
        return self.storage_proxy.list_dir()

    # Private methods
    # -----

    def _delete_media(self):
        for media_name in self._undeleted_media:
            try:
                media_data = self.media_index[media_name]

                # Delete image
                self.storage_proxy.delete_object(media_data["filename"])

                # Update self image map
                del self.media_index[media_name]

            except Exception:
                pass

        # Reset undeleted media
        self._undeleted_media = []

    def _save_media(self):
        for media_name, media_data in self._unsaved_media.items():

            file_ext = self._get_media_file_ext(media_data["file_type"])
            filename = f"media/{media_name}.{file_ext}"

            # Save media
            self.storage_proxy.save_bytes(media_data["bytes"], filename)

            # Remove bytes from media_data
            del media_data["bytes"]

            # Add filename to media_data
            media_data["filename"] = filename

            # Update media index with new media_data
            self.media_index[media_name] = media_data

        # Reset unsaved media
        self._unsaved_media = {}

    def _get_media_file_ext(self, file_type):
        file_prefix, file_ext = file_type.split("/")

        if file_prefix == "text":
            return "txt"

        return file_ext

    def _get_media_file_prefix(self, file_type):
        file_prefix, _ = file_type.split("/")
        return file_prefix

    def _save_media_index(self):
        self.storage_proxy.save_json(self.media_index, "media/media_index.json")

    def _init_media(self):
        try:
            data = self.storage_proxy.get_json(f"media/media_index.json")
            self.media_index = data

        except StorageProxyException:
            self.media_index = {}

    def _init_content(self):
        try:
            data = self.storage_proxy.get_json(f"content.json")
            self.content = data

        except StorageProxyException:
            self.content = ""

    def _init_post_data(self):
        self._init_media()

        if not self.content:
            self._init_content()

    def __str__(self):
        return json.dumps(self.meta_data.to_json(), indent=2)
