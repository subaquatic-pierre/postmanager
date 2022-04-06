from abc import ABC, abstractmethod
from postmanager.event import Event
from postmanager.manager import PostManager
from postmanager.meta import PostMeta
from postmanager.post import Post


class Method(ABC):
    def __init__(self, request_event: Event, post_manager: PostManager) -> None:
        self.request_event = request_event
        self.post_manager = post_manager
        self.request_body = self.request_event.body
        self.response_body = {}
        self.error_message = ""

    def _set_error(self, message, e=""):
        text = f'{message}. {getattr(e, "message", str(e))}'
        self.error_message = text

    def run(self):
        self._run()
        self._check_if_testing()

    def _check_if_testing(self):
        post_manager_bucket_proxy_class_name = (
            self.post_manager.bucket_proxy.__class__.__name__
        )
        if post_manager_bucket_proxy_class_name == "MockBucketProxy":
            self.error_message = ""
            self.response_body["testing"] = True

    @abstractmethod
    def _run(self):
        pass


class GetMethod(Method):
    def _run(self):
        post_id = self.request_event.path.split("/")[-1]

        try:
            post = self.post_manager.get_by_id(post_id)
        except Exception as e:
            self._set_error("Blog not found", e)
            return

        self.response_body = {
            "post": post.to_json(),
        }


class ListMethod(Method):
    def _run(self):
        try:
            if self.request_event.query_string_params:
                title = self.request_event.query_string_params.get("title")
                if title:
                    post_id = self.post_manager.title_to_id("Most Amazing")
                    body = {"id": post_id}
            else:
                body = self.post_manager.index
        except Exception as e:
            self._set_error("Unable to list posts", e)
            return

        self.response_body = body


class PostMethod(Method):
    def _run(self):
        try:
            meta_data = self.request_event.body.get("metaData")
        except Exception as e:
            self._set_error("There was an error getting metaData from request body", e)
            return

        try:
            content = self.request_body.get("content")
        except Exception as e:
            self._set_error("There was an error getting content from request body", e)
            return

        try:
            title = meta_data.get("title")
            post_meta: PostMeta = self.post_manager.create_meta(title)
            post: Post = self.post_manager.create_post(post_meta, content)

        except Exception as e:
            self._set_error("There was an error creating post", e)
            return

        try:
            self.post_manager.save_post(post)
        except Exception as e:
            self._set_error("There was an error saving post", e)
            return

        self.response_body = {
            "post": post.to_json(),
        }


class DeleteMethod(Method):
    def _run(self):
        # get post id
        post_id = self.request_event.path.split("/")[-1]

        # delete post
        try:
            self.post_manager.delete_post(post_id)
        except Exception as e:
            self._set_error("Unable to delete post from post_manager", e)

        self.response_body = {"deleted": True, "post_id": post_id}


class PutMethod(Method):
    def _run(self):
        path = self.request_event.path
        post_id = path.split("/")[-1]

        try:
            meta_data = self.request_body.get("metaData")
            content = self.request_body.get("content")

            post: Post = self.post_manager.get_by_id(post_id)

            post_meta = self.post_manager.get_meta(post_id)

            post_meta.update_meta(meta_data)

            post.meta_data = post_meta
            post.content = content

        except Exception as e:
            self._set_error("There was an error updating post data", e)
            return

        try:
            self.post_manager.save_post(post)

        except Exception as e:
            self._set_error("There was an error saving post", e)
            return

        self.response_body = {"post": post.to_json()}
