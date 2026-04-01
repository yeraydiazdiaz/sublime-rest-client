import os
import sys
import unittest
from typing import Dict, Iterator, Tuple, Union, cast
from time import sleep

import sublime
from unittesting import DeferrableTestCase

from . import utils

TIMEOUT = int(os.getenv("REST_CLIENT_TIMEOUT", 1000))
PANEL_NAME = "REST Client Response"
SETTINGS_FILE = "REST.sublime-settings"


class TestRestClient(DeferrableTestCase):
    def setUp(self) -> None:
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.response_view = None
        self.plugin_settings = sublime.load_settings(SETTINGS_FILE)
        editor_settings = sublime.load_settings("Preferences.sublime-settings")
        editor_settings.set("close_windows_when_empty", False)

    def tearDown(self) -> None:
        # Make sure the UnitTesting panel is showing after the test run
        self.window.run_command("show_panel", {"panel": "output.UnitTesting"})

        if self.response_view:
            if self.plugin_settings.get("response_view") == "panel":
                self.window.destroy_output_panel(PANEL_NAME)
            else:
                self.response_view.window().focus_view(self.response_view)
                self.response_view.window().run_command("close_file")

        if self.view:
            self.view.set_scratch(True)
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")

    def _get_response_view(self) -> sublime.View:
        count = 0
        while self.response_view is None and count <= 10:
            for view in self.window.views():
                if view.name() == PANEL_NAME:
                    self.response_view = view
                    return self.response_view
            count += 1
            sleep(0.1)
        raise RuntimeError("Unable to find response view")

    def _get_response_view_contents(self) -> str:
        if self.plugin_settings.get("response_view") == "panel":
            self.response_view = self.window.find_output_panel(PANEL_NAME)
        else:
            self.response_view = self._get_response_view()

        self.assertIsNotNone(self.response_view, "REST response view not available")
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
        self.plugin_settings.set("response_view", "tab")
        utils.set_text_on_view(self.view, "https://httpbin.org/get")
        self.window.run_command("rest_request")
        yield TIMEOUT
        status, headers, body = self._get_response_json()
        self.assertEqual(status, "GET https://httpbin.org/get 200 OK")
        self.assertIn("Date", headers)
        self.assertIn("url", body)

    def test_get_with_variable(self) -> Iterator[int]:
        self.plugin_settings.set("response_view", "panel")
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

    @unittest.skipIf(
        sys.platform == "win32", "Windows builds fail with 'Timeout: output is frozen.'"
    )
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
