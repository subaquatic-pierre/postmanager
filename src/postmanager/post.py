import json
from postmanager.proxy import BucketProxyBase
from postmanager.meta import PostMeta


class Post:
    def __init__(
        self, bucket_proxy: BucketProxyBase, meta_data: PostMeta, content="", image=None
    ) -> None:
        self.id = meta_data.id
        self.bucket_proxy = bucket_proxy
        self.meta_data = meta_data
        self._content = content
        self.image = image

    @property
    def title(self):
        return self.meta_data.title

    @title.setter
    def title(self, title):
        self.meta_data.title = title

    @property
    def content(self):
        try:
            self._content = self.bucket_proxy.get_json("content.json")
            return self._content
        except Exception:
            return "No content found"

    @content.setter
    def content(self, content):
        self._content = content

    def save(self):
        # Save content
        self.bucket_proxy.save_json("", "images/")
        # Save meta
        self.bucket_proxy.save_json(self.meta_data.to_json(), "meta.json")
        self.bucket_proxy.save_json(self._content, "content.json")

        # Save images, for image in images
        if self.image != None:
            self.bucket_proxy.save_bytes(self.image, f"images/template.jpg")

    def list_image_urls(self):
        image_keys = self.bucket_proxy.list_dir(f"images/")
        urls = [f"{self._base_image_url()}{image_key}" for image_key in image_keys]
        return urls

    def list_files(self):
        return self.bucket_proxy.list_dir()

    def to_json(self):
        return {"meta_data": self.meta_data.to_json(), "content": self.content}

    def _base_image_url(self):
        return f"https://{self.bucket_proxy.bucket_name}.s3.amazonaws.com/"

    def __str__(self):
        return json.dumps(self.meta_data.to_json(), indent=2)
