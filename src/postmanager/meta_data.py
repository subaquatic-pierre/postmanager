from postmanager.storage_base import StorageBase, ModelStorage


class PostMetaData(ModelStorage):
    def __init__(self, storage_proxy: StorageBase, id, attrs) -> None:
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
        self.save_json(self.to_json(), "meta.json")

    def update(self, meta_dict: dict):
        for key, value in meta_dict.items():
            # Never update id
            if key == "id":
                continue
            setattr(self, key, value)

    def _init_attrs(self, attrs):
        for key in attrs.keys():
            self._attrs_list.append(key)

        for key, value in attrs.items():
            if key == "id":
                continue
            else:
                setattr(self, key, value)

    @staticmethod
    def from_json(storage_proxy, meta_dict: dict):
        assert meta_dict.get("id") != None, "meta_dict object must contain an ID key"

        post_meta = PostMetaData(storage_proxy, meta_dict.get("id"), meta_dict)

        return post_meta
