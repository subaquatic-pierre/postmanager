from postmanager.interfaces import StorageProxy
from postmanager.storage_adapter import StorageAdapter


class MetaData(StorageAdapter):
    def __init__(self, storage_proxy: StorageProxy, id, attrs) -> None:
        super().__init__(storage_proxy)

        self.id = id
        self._attrs_list = []
        self._init_attrs(attrs)

    def to_json(self):
        data = {}
        for attr in self._attrs_list:
            value = getattr(self, attr)
            data[attr] = value

        return data

    def save(self):
        self.save_json(self.to_json(), "meta_data.json")

    def update(self, meta_dict: dict):
        for key, value in meta_dict.items():
            # Never update id
            if key == "id":
                continue
            setattr(self, key, value)

        self._update_attrs_list(meta_dict)

    def _update_attrs_list(self, meta_dict):
        for key in meta_dict.keys():
            if key not in self._attrs_list:
                self._attrs_list.append(key)

    def _init_attrs(self, meta_dict):
        self._update_attrs_list(meta_dict)

        for key, value in meta_dict.items():
            if key == "id":
                continue
            else:
                setattr(self, key, value)

    @staticmethod
    def from_json(storage_proxy, meta_dict: dict):
        assert meta_dict.get("id") != None, "meta_dict object must contain an ID key"

        post_meta = MetaData(storage_proxy, meta_dict.get("id"), meta_dict)

        return post_meta
