import json
from unittest import TestCase
from postmanager.http_methods import get, list, post
from postmanager.utils import create_event_and_context


class TestHttpMethods(TestCase):
    def test_get_method(self):
        post_id = 0
        event, context = create_event_and_context(f"/blog/{post_id}")
        blog = get(event, context)
        return blog

    def test_list_method(self):
        event, context = create_event_and_context(f"/blog")
        return list(event, context)

    def test_post_method(self):
        post_body = {
            "metaData": {"title": "Gyming Life"},
            "content": {"Heading": "To be the best you have to be the best"},
        }
        event, context = create_event_and_context("/blog", post_body)
        response = post(event, context)
        return response
