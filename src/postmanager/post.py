import json

from postmanager.media_data import MediaData
from postmanager.interfaces import StorageProxy
from postmanager.storage_adapter import StorageAdapter
from postmanager.meta_data import MetaData
from postmanager.exception import StorageProxyException


class Post(StorageAdapter):
    """Main Post class used to manager single post operations."""

    def __init__(
        self,
        storage_proxy: StorageProxy,
        meta_data: MetaData,
        content="",
    ) -> None:
        """
        Args:
            storage_proxy (StorageProxy): Storage proxy used
             to communicate with storage system.
            meta_data (obj): MetaData object associated with this post.
            content (obj, optional): JSON parsable object or string.
        """
        super().__init__(storage_proxy)

        # Base data
        self.id = meta_data.id
        self.meta_data = meta_data

        self._init_content(content)
        self._init_media_data()

    def to_json(self) -> dict:
        """Get JSON representation of the post.

        Returns:
            dict: JSON representation of the post.

        """
        return {
            "meta_data": self.meta_data.to_json(),
            "content": self.content,
            "media_index": self.media_index,
        }

    # -----
    # Update methods
    # -----

    def update_meta_data(self, meta_dict: dict) -> None:
        """Update meta data associated with the post.

        Args:
            meta_dict (dict):  New Post object intented to save.

        Returns:
            Post: Post object just saved, raises PostManagerExecption on error.

        """
        self.meta_data.update(meta_dict)

    def update_content(self, content):
        self.content = content

    def save(self):
        # Save content
        self.save_json(self.content, "content.json")

        # Save meta data
        self.meta_data.save()

        # save media data
        self.media_data.save()

    # -----
    # Media methods
    # -----

    @property
    def media_index(self):
        return self.media_data.media_index

    def add_media(self, media_data, media_name, **kwargs):
        self.media_data.add_media(media_data, media_name, **kwargs)

    def remove_media(self, media_name):
        self.media_data.remove_media(media_name)

    def delete_media(self, media_name):
        self.media_data.delete_media(media_name)

    def get_media(self, media_name, **kwargs):
        return self.media_data.get_media(media_name, **kwargs)

    # -----
    # Private methods
    # -----

    def _init_media_data(self):
        media_storage_proxy = self.new_storage_proxy("media/")
        media_data = MediaData(media_storage_proxy)
        self.media_data = media_data

    def _init_content(self, content):
        if content:
            self.content = content
            return

        try:
            data = self.get_json(f"content.json")
            self.content = data

        except StorageProxyException:
            self.content = ""

    def __str__(self):
        return json.dumps(self.meta_data.to_json(), indent=2)
