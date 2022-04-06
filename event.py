import json


class Event:
    def __init__(self, event) -> None:
        self.event = event
        self.body = self._parse_body()
        self.path = self._parse_event_param("path", "")
        self.testing = self._parse_event_param("test_api")
        self.mock_config = self._parse_event_param("path")
        self.headers = self._parse_event_param("headers")
        self.query_string_params = self._parse_event_param("queryStringParameters")
        self.error_message = ""

    def _parse_body(self):
        try:
            body = self.event.get("body")
            json_body = json.loads(body)
            return json_body
        except Exception as e:
            self._set_error("There was an error parsing event body", e)

    def _parse_event_param(self, param, default={}):
        try:
            param = self.event.get(param, default)
            return param
        except Exception as e:
            self._set_error(f"An error occured parsing {param} from request event", e)

    def _set_error(self, message, e=""):
        text = f'{message}. {getattr(e, "message", str(e))}'
        self.error_message = text
