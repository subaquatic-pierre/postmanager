import json
from typing import Any

from postmanager.media_data import MediaData
from postmanager.interfaces import StorageProxy
from postmanager.storage_adapter import StorageAdapter
from postmanager.meta_data import MetaData
from postmanager.exception import StorageProxyException


class Post(StorageAdapter):
    """Main Post class used to manage single post operations.

    Attributes:
        storage_proxy (StorageProxy): Storage proxy used to communicate with storage backend.
        id (int): ID of the post.
        meta_data (MetaData): MetaData object holding all meta data values of the post.
        media_data (MediaData): MediaData object to manage all media data associated with the post.
        content (dict): JSON parsable content associated with the post
    """

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
            meta_data (dict): MetaData object associated with this post.
            content (dict, optional): JSON parsable object or string.
        """
        super().__init__(storage_proxy)

        # Base data
        self.id = meta_data.id
        self.meta_data = meta_data
        self.media_data = self._init_media_data()
        self.content = self._init_content(content)

    def to_json(self) -> dict[str, Any]:
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

    def update_meta_data(self, meta_dict: dict[str, str]) -> None:
        """Update meta data associated with the post.

        Args:
            meta_dict (dict):  New meta data used to update old meta data object.

        Returns:
            None: Nothing returned

        """
        self.meta_data.update(meta_dict)

    def update_content(self, content: dict[str, str]) -> None:
        """Update content associated with the post.

        Args:
            content (dict):  New content used to update old content.

        Returns:
            None: Nothing returned

        """
        self.content = content

    def save(self) -> None:
        """Save the post and all associated data.

        Returns:
            None: Nothing returned

        """
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
        """Get media index JSON of all media data associated with the post."""
        return self.media_data.media_index

    def add_media(self, media_data: str, media_name: str, **kwargs) -> None:
        """Add media to be saved.

        Args:
            media_data (str):  Byte64 encoded string in DataURL format.
            media_name (str): Name of media used to reference media bytes stored.

        Returns:
            None: Nothing returned

        """
        self.media_data.add_media(media_data, media_name, **kwargs)

    def remove_media(self, media_name: str) -> None:
        """Remove media that has not yet been saved to disk.

        Args:
            media_name (str): Name of media data to remove.

        Returns:
            None: Nothing returned

        """

        self.media_data.remove_media(media_name)

    def delete_media(self, media_name):
        """Delete media that is stored on disk.

        Args:
            media_name (str): Name of media data to be deleted.

        Returns:
            None: Nothing returned

        """
        self.media_data.delete_media(media_name)

    def get_media(self, media_name: str, **kwargs) -> str:
        """Get bytes for media data.

        Args:
            media_name (str): Name of media data to be retrieved.

        Returns:
            str: byte64 encoded str in DataURL format.

        """
        data: str = self.media_data.get_media(media_name, **kwargs)
        return data

    # -----
    # Private methods
    # -----

    def _init_media_data(self):
        media_storage_proxy = self.new_storage_proxy("media/")
        media_data = MediaData(media_storage_proxy)
        return media_data

    def _init_content(self, content):
        if content:
            return content

        try:
            data = self.get_json("content.json")
            return data

        except StorageProxyException:
            return ""

    def __str__(self):
        return json.dumps(self.meta_data.to_json(), indent=2)
