import os.path
import sys
import typing as tp
from http import HTTPStatus

# Import dependencies
sys.path.append(os.path.dirname(__file__) + "/deps")

import sublime
import sublime_plugin

from .sublime_rest import client, parser
from .sublime_rest.request import Request


class RestRequestCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def run(self, *args) -> None:
        print("Running Sublime REST", args)
        self.request_view = self.window.active_view()

        contents, pos = self.get_request_text_from_selection()
        if contents == "":
            self.log_to_status("Invalid request text: `{}`".format(contents))
            return

        self.log_to_status("Sending request for: `{}`".format(contents))

        request = parser.parse(contents, pos)
        status, headers, body = client.request(request)
        response_text = self.get_response_content(request, status, headers, body)

        response_view = self.window.new_file()
        response_view.run_command("rest_replace_view_text", {"text": response_text})
        self.log_to_status(status)

    def log_to_status(self, msg: str) -> None:
        """Displays the message in the status bar of the view."""
        self.request_view.set_status("rest", "REST: {}".format(msg))

    def get_request_text_from_selection(self) -> str:
        """Expands the selection to the boundaries of the request."""
        selections = self.request_view.sel()
        pos = selections[0].a
        contents = self.request_view.substr(sublime.Region(0, self.request_view.size()))
        return contents, pos

    def get_response_content(
        self, request: Request, status: int, headers: tp.Dict[str, str], body: str
    ):
        """Combine request and response elements into a string for the response view."""
        headers_text = "\n".join(
            f"{header}: {value}" for header, value in headers.items()
        )
        http_status = HTTPStatus(status)
        return "\n\n".join(
            [
                f"{request.method} {request.url} {status} {http_status.name}",
                headers_text,
                body,
            ]
        )


class RestReplaceViewTextCommand(sublime_plugin.TextCommand):
    """Replaces the text in a view.

    Usage:
    >>> view.run_command("rest_replace_view_text", {"text": "Hello, World!"})

    """

    def run(self, edit, text, point=None):
        self.view.set_scratch(True)
        self.view.erase(edit, sublime.Region(0, self.view.size()))
        self.view.insert(edit, 0, text)
        if point is not None:
            self.view.sel().clear()
            self.view.sel().add(sublime.Region(point))
