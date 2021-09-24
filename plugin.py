import os.path
import sys
import typing as tp
from http import HTTPStatus
import threading
import traceback
from time import perf_counter

# Import dependencies
sys.path.append(os.path.dirname(__file__) + "/deps")

import sublime
import sublime_plugin

from .rest_client import client, parser
from .rest_client.request import Request


class HttpRequestThread(threading.Thread):
    def __init__(self, request):
        super().__init__()
        self.request = request
        self.success = None

    def run(self):
        self._start = perf_counter()
        try:
            self.result = client.request(self.request)
            self.success = True
        except Exception:
            self.success = False
            self.result = traceback.format_exc()
        finally:
            self._end = perf_counter()
            self.elapsed = self._end - self._start

    def get_result(self):
        return self.result


class RestRequestCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._tick = 0

    def run(self, *args) -> None:
        print("Running Sublime REST", args)
        self.request_view = self.window.active_view()

        contents, pos = self.get_request_text_from_selection()
        if contents == "":
            self.log_to_status("Invalid request text: `{}`".format(contents))
            return

        self.log_to_status("Sending request for: `{}`".format(contents))

        request = parser.parse(contents, pos)

        thread = HttpRequestThread(request)
        thread.start()
        self.handle_thread(thread)

    def handle_thread(self, thread: HttpRequestThread) -> None:
        if thread.is_alive():
            dots = "".join("." if j != self._tick % 3 else " " for j in range(3))
            self.log_to_status(f"Waiting for response {dots}")
            self._tick += 1
            sublime.set_timeout_async(lambda: self.handle_thread(thread), 100)
        elif thread.success:
            self.on_success(thread)
        else:
            self.on_error(thread)

    def on_success(self, thread: HttpRequestThread) -> None:
        msg = f"Response received in {thread.elapsed:.3f} seconds"
        self.log_to_status(msg)
        status, headers, body = thread.get_result()
        response_text = self.get_response_content(thread.request, status, headers, body)

        response_view = self.window.new_file()
        response_view.run_command("rest_replace_view_text", {"text": response_text})
        self.log_to_status(msg, response_view)

    def on_error(self, thread: HttpRequestThread) -> None:
        self.log_to_status("Unexpected error on request, please see logs")
        print(thread.result)

    def log_to_status(self, msg: str, view: sublime.View = None) -> None:
        """Displays the message in the status bar of the view."""
        view = view or self.request_view
        view.set_status("rest", "REST: {}".format(msg))

    def get_request_text_from_selection(self) -> tp.Tuple[str, int]:
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
        self.view.assign_syntax("scope:source.http-response")
        self.view.insert(edit, 0, text)
        if point is not None:
            self.view.sel().clear()
            self.view.sel().add(sublime.Region(point))
