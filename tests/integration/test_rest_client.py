import os
from typing import Dict, Iterator, Tuple, Union, cast

import sublime
from unittesting import DeferrableTestCase

from . import utils

TIMEOUT = int(os.getenv("REST_CLIENT_TIMEOUT", 500))


class TestRestClient(DeferrableTestCase):
    def setUp(self) -> None:
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.response_view = None
        settings = sublime.load_settings("Preferences.sublime-settings")
        settings.set("close_windows_when_empty", False)

    def tearDown(self) -> None:
        if self.response_view:
            self.response_view.window().focus_view(self.response_view)
            self.response_view.window().run_command("close_file")

        if self.view:
            self.view.set_scratch(True)
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")

    def _get_response_view_contents(self) -> str:
        self.response_view = self.window.active_view()
        return utils.get_contents_of_view(self.response_view)

    def _get_response(
        self, parse_json: bool = True
    ) -> Tuple[str, Dict, Union[Dict, str]]:
        return utils.parse_response(
            self._get_response_view_contents(), parse_json=parse_json
        )

    def _get_response_json(self) -> Tuple[str, Dict, Dict]:
        status, headers, body = self._get_response(parse_json=True)
        return status, headers, cast(Dict, body)

    def _get_response_str(self) -> Tuple[str, Dict, str]:
        status, headers, body = self._get_response(parse_json=False)
        return status, headers, cast(str, body)

    def test_simple_get(self) -> Iterator[int]:
        utils.set_text_on_view(self.view, "https://httpbin.org/get")
        self.window.run_command("rest_request")
        yield TIMEOUT
        status, headers, body = self._get_response_json()
        self.assertEqual(status, "GET https://httpbin.org/get 200 OK")
        self.assertIn("Date", headers)
        self.assertIn("url", body)

    def test_get_with_variable(self) -> Iterator[int]:
        text = "\n".join(
            [
                "@token = ABC123",
                "GET https://httpbin.org/get",
                "Authentication: Bearer {{token}}",
            ]
        )
        utils.set_text_on_view(self.view, text)
        self.window.run_command("rest_request")
        yield TIMEOUT
        status, headers, body = self._get_response_json()
        self.assertEqual(status, "GET https://httpbin.org/get 200 OK")
        self.assertIn("Date", headers)
        self.assertEquals(body["headers"]["Authentication"], "Bearer ABC123")

    def test_post(self) -> Iterator[int]:
        text = "\n".join(
            [
                "POST https://httpbin.org/post",
                "content-type: application/json",
                "\n",
                '{"hello": "world!"}',
            ]
        )
        utils.set_text_on_view(self.view, text)
        self.window.run_command("rest_request")
        yield TIMEOUT
        status, headers, body = self._get_response_str()
        self.assertEqual(status, "POST https://httpbin.org/post 200 OK")
        self.assertIn("Date", headers)
        self.assertIn('"hello": "world!"', body)

    def test_error(self) -> Iterator[int]:
        utils.set_text_on_view(self.view, "http://localhost:9999")
        self.window.run_command("rest_request")
        yield TIMEOUT
        contents = self._get_response_view_contents()
        self.assertTrue(
            contents.startswith(
                "REST Client: Error on request to http://localhost:9999"
            )
        )
