from typing import Generator

import sublime
from unittesting import DeferrableTestCase

from . import utils


class TestRestClient(DeferrableTestCase):
    def setUp(self) -> None:
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        settings = sublime.load_settings("Preferences.sublime-settings")
        settings.set("close_windows_when_empty", False)

    def tearDown(self) -> None:
        if self.view:
            self.view.set_scratch(True)
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")

    def test_simple_get(self) -> Generator[int, None, None]:
        utils.set_text_on_view(self.view, "https://httpbin.org/get")
        self.window.run_command("rest_request")
        yield 1000
        response_view = self.window.active_view()
        status, headers, body = utils.parse_response(
            utils.get_contents_of_view(response_view)
        )
        self.assertEqual(status, "GET https://httpbin.org/get 200 OK")
        self.assertIn("Date", headers)
        self.assertIn("url", body)
