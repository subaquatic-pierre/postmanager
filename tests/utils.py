import json


BUCKET_NAME = "serverless-blog-contents"
BUCKET_ROOT_DIR = "blog/"


def print_response(response, method=False):
    body = json.loads(response["body"])
    text = json.dumps(body, indent=4)
    if method:
        print(f"---- Method: {method.__name__} ----\n{text}\n--------")
    else:
        print(text)


def create_event_and_context(path, body={}, mock_bucket=True, mock_config={}):
    event = {
        "path": path,
        "body": json.dumps(body),
        "test_api": mock_bucket,
        "mock_config": mock_config,
    }
    context = {}
    return event, context


def set_get_object_return_value(return_value):
    class StreamingBodyMock:
        def __init__(self, return_value) -> None:
            self.return_value = return_value

        def read(self):
            return json.dumps(self.return_value)

    return {"Body": StreamingBodyMock(return_value)}
