from typing import List
from postmanager.interfaces import StorageProxy
from postmanager.storage_adapter import StorageAdapter


class MetaData(StorageAdapter):
    """Main MetaData class used to manage all meta data associated with a post.

    Attributes:
        storage_proxy (StorageProxy): Storage proxy used to communicate with storage backend.
        id (int): ID of the associated post.
    """

    def __init__(self, storage_proxy: StorageProxy, id, attrs) -> None:
        """
        Args:
            storage_proxy (StorageProxy): Storage proxy used
             to communicate with storage system.

        """
        super().__init__(storage_proxy)

        self.id = id
        self._attrs_list: List[str] = []
        self._init_attrs(attrs)

    def to_json(self) -> dict[str, str]:
        """Get JSON representation of the meta data.

        Returns:
            dict: JSON representation of the meta data.

        """
        data = {}
        for attr in self._attrs_list:
            value = getattr(self, attr)
            data[attr] = value

        return data

    def save(self) -> None:
        """Save the meta data to disk.

        Returns:
            None: Nothing returned

        """
        self.save_json(self.to_json(), "meta_data.json")

    def update(self, meta_dict: dict[str, str]) -> None:
        """Update meta data.

        Args:
            meta_dict (dict):  New meta data used to update old meta data object.

        Returns:
            None: Nothing returned

        """
        for key, value in meta_dict.items():
            # Never update id
            if key == "id":
                continue
            setattr(self, key, value)

        self._update_attrs_list(meta_dict)

    # -----
    # Private methods
    # -----

    def _update_attrs_list(self, meta_dict: dict[str, str]) -> None:
        """Update attribute list.

        Args:
            meta_dict (dict):  New meta data used to update old attrs_list.

        Returns:
            None: Nothing returned

        """
        for key in meta_dict.keys():
            if key not in self._attrs_list:
                self._attrs_list.append(key)

    def _init_attrs(self, meta_dict: dict[str, str]) -> None:
        """Initialize attributes, assign each key in meta_dict to attribute on MetaData object.

        Args:
            meta_dict (dict):  New meta data used create new attributes on object.

        Returns:
            None: Nothing returned

        """
        self._update_attrs_list(meta_dict)

        for key, value in meta_dict.items():
            if key == "id":
                continue
            else:
                setattr(self, key, value)

    @staticmethod
    def from_json(storage_proxy, meta_dict: dict[str, str]):
        """Build new MetaData object from JSON object.

        Args:
            meta_dict (dict):  New meta data used to create new object, must contain `id` key.

        Returns:
            MetaData: New MetaData object created

        """
        if meta_dict.get("id") is None:
            raise Exception("meta_dict object must contain an ID key")

        post_meta = MetaData(storage_proxy, meta_dict.get("id"), meta_dict)

        return post_meta
