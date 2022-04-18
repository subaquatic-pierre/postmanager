from typing import List, Union, Any
from postmanager.interfaces import StorageProxy
from postmanager.storage_adapter import StorageAdapter
from postmanager.exception import StorageProxyException
from base64 import b64decode, b64encode


class MediaData(StorageAdapter):
    """Main MediaData class used to manage all media data associated with a post.

    Attributes:
        storage_proxy (StorageProxy): Storage proxy used to communicate with storage backend.
    """

    def __init__(self, storage_proxy: StorageProxy) -> None:
        """
        Args:
            storage_proxy (StorageProxy): Storage proxy used
             to communicate with storage system.
        """
        super().__init__(storage_proxy)

        self._unsaved_media: dict[str, Any] = {}
        self._undeleted_media: List[str] = []
        self.media_index: dict[str, Any] = {}

        self._init_media_index()

    def save(self) -> None:
        """Save all unsaved data to disk.

        Returns:
            None: Nothing returned

        """
        updated = False
        # Save unsaved images
        if self._unsaved_media:
            updated = True
            self._save_media()

        if self._undeleted_media:
            updated = True
            self._delete_media()

        # Update media_index
        if updated:
            self._save_media_index()

    def add_media(
        self, media_data, media_name, media_data_format="data_url", overwrite=True
    ) -> None:
        """Add media to be saved.

        Args:
            media_data (str):  Byte64 encoded string in DataURL format.
            media_name (str): Name of media used to reference media bytes stored.
            media_data_format (str,optional): Media format being passed to method.
            overwrite (bool, optional): OVerwrite existing media data with same name.

        Returns:
            None: Nothing returned

        """
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

    def remove_media(self, media_name) -> Union[None, str]:
        """Remove media that has not yet been saved to disk.

        Args:
            media_name (str): Name of media data to remove.

        Returns:
            None: Nothing returned

        """
        try:
            del self._unsaved_media[media_name]
            return None
        except:
            return "Image does not exist"

    def delete_media(self, media_name) -> None:
        """Delete media that is stored on disk.

        Args:
            media_name (str): Name of media data to be deleted.

        Returns:
            None: Nothing returned

        """
        self._undeleted_media.append(media_name)

    def get_media(self, media_name, return_format="data_url") -> Union[str, bytes]:
        """Get bytes for media data.

        Args:
            media_name (str): Name of media data to be retrieved.
            media_data_format (str,optional): Media format to be returned.


        Returns:
            str: byte64 encoded str in DataURL format.

        """
        try:
            media_data = self.media_index[media_name]
            filename = media_data["filename"]

            image_bytes = self.get_bytes(filename)

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

        except Exception as e:
            return f"Error getting media. {str(e)}"

    # -----
    # Private methods
    # -----

    def _delete_media(self):
        for media_name in self._undeleted_media:
            try:
                media_data = self.media_index[media_name]

                # Delete image
                self.delete_file(media_data["filename"])

                # Update self image map
                del self.media_index[media_name]

            except Exception:
                pass

        # Reset undeleted media
        self._undeleted_media = []

    def _save_media(self):
        for media_name, media_data in self._unsaved_media.items():

            # First remove media if exists
            if media_name in self.media_index:
                # Get old media data
                old_media_data = self.media_index[media_name]
                old_media_ext = self._get_media_file_ext(old_media_data["file_type"])
                old_filename = f"{media_name}.{old_media_ext}"
                self.delete_file(old_filename)

            file_ext = self._get_media_file_ext(media_data["file_type"])
            filename = f"{media_name}.{file_ext}"

            # Save media
            media_bytes: bytes = media_data["bytes"]
            self.save_bytes(media_bytes, filename)

            # Remove bytes from media_data
            new_media_data: dict[str, str] = {
                "file_type": media_data["file_type"],
                "filename": filename,
            }

            # Update media index with new media_data
            self.media_index[media_name] = new_media_data

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
        self.save_json(self.media_index, "media_index.json")

    def _init_media_index(self):
        try:
            data = self.get_json(f"media_index.json")
            self.media_index = data

        except StorageProxyException:
            self.media_index = {}
