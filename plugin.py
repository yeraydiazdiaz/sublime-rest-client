import json
import os.path
import sys
import threading
import traceback
from http import HTTPStatus
from time import perf_counter
from typing import Any, Dict, Optional, Tuple

# Import dependencies
sys.path.append(os.path.dirname(__file__) + "/deps")

import sublime
import sublime_plugin

from .rest_client import Response, client, parser
from .rest_client.request import Request


SETTINGS_FILE = "REST.sublime-settings"
settings = sublime.load_settings(SETTINGS_FILE)


def apply_settings(settings):
    client.setup(settings)


settings.add_on_change("tag", lambda: apply_settings(settings))
apply_settings(settings)


class RestException(Exception):
    pass


class HttpRequestThread(threading.Thread):
    def __init__(self, request: Request) -> None:
        super().__init__()
        self.request = request
        self.success: Optional[bool] = None
        self.response: Optional[Response] = None
        self.error: Optional[Tuple[Exception, str]] = None

    def run(self) -> None:
        self._start = perf_counter()
        try:
            self.response = client.request(self.request)
            self.success = True
        except Exception as exc:
            self.error = (exc, traceback.format_exc())
            self.success = False
        finally:
            self._end = perf_counter()
            self.elapsed = self._end - self._start

    def get_response(self) -> Response:
        if self.success is None or self.response is None:
            raise RestException("Attempted to retrieve response before completion")
        return self.response

    def get_error(self) -> Tuple[Exception, str]:
        if self.success is None or self.error is None:
            raise RestException("Attempted to retrieve error before completion")
        return self.error


class RestRequestCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> None:
        super().__init__(*args, **kwargs)
        self._tick = 0

    def run(self, *args: Tuple[Any]) -> None:
        print("Running Sublime REST", args)
        self.request_view = self.window.active_view()

        contents, pos = self.get_request_text_from_selection()
        if contents == "":
            self.log_to_status("Invalid request text: `{}`".format(contents))
            return

        self.log_to_status("Sending request for: `{}`".format(contents))

        try:
            request = parser.parse(contents, pos)
        except Exception:
            self.log_to_status(
                " ".join(
                    [
                        "Error while parsing REST request.",
                        "Please check the console (View > Show Console)",
                        "and report the error on",
                        "https://github.com/yeraydiazdiaz/sublime-rest-client/issues",
                    ]
                )
            )
        else:
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
        response = thread.get_response()
        response_text = self.get_response_content(
            thread.request, response.status, response.headers, response.data
        )

        response_view = self.window.new_file()
        response_view.run_command("rest_replace_view_text", {"text": response_text})
        self.log_to_status(msg, response_view)

    def on_error(self, thread: HttpRequestThread) -> None:
        msg = f"Error sending request in {thread.elapsed:.3f} seconds"
        self.log_to_status(msg)
        error = thread.get_error()
        error_text = self.get_error_content(thread.request, *error)
        response_view = self.window.new_file()
        response_view.run_command("rest_replace_view_text", {"text": error_text})
        self.log_to_status(msg, response_view)

    def log_to_status(self, msg: str, view: sublime.View = None) -> None:
        """Displays the message in the status bar of the view."""
        view = view or self.request_view
        view.set_status("rest", "REST: {}".format(msg))

    def get_request_text_from_selection(self) -> Tuple[str, int]:
        """Expands the selection to the boundaries of the request."""
        selections = self.request_view.sel()
        pos = selections[0].a
        contents = self.request_view.substr(sublime.Region(0, self.request_view.size()))
        return contents, pos

    def get_response_content(
        self, request: Request, status: int, headers: Dict[str, str], body: str
    ) -> str:
        """Combine request and response elements into a string for the response view."""
        headers_text = "\n".join(
            f"{header}: {value}" for header, value in headers.items()
        )
        http_status = HTTPStatus(status)
        content_type = headers.get("Content-Type")
        if (
            settings["format_json"] is True
            and content_type is not None
            and "application/json" in content_type
        ):
            body = self._format_json(body)

        return "\n\n".join(
            [
                f"{request.method} {request.url} {status} {http_status.name}",
                headers_text,
                body,
            ]
        )

    def _format_json(self, body: str) -> str:
        try:
            payload = json.loads(body)
            return json.dumps(
                payload,
                indent=settings["format_json_indent"],
                sort_keys=settings["format_json_indent"],
            )
        except Exception:
            print("Failed to format JSON payload")
            return body

    def get_error_content(
        self, request: Request, exc: Exception, traceback: str
    ) -> str:
        """Compose error content for the response view."""
        return "\n\n".join(
            [
                f"REST Client: Error on request to {request.url}",
                repr(exc),
                traceback,
            ]
        )


class RestReplaceViewTextCommand(sublime_plugin.TextCommand):
    """Replaces the text in a view.

    Usage:
    >>> view.run_command("rest_replace_view_text", {"text": "Hello, World!"})

    """

    def run(self, edit, text, point=None) -> None:  # type: ignore
        self.view.set_scratch(True)
        self.view.erase(edit, sublime.Region(0, self.view.size()))
        self.view.assign_syntax("scope:source.http-response")
        self.view.insert(edit, 0, text)
        if point is not None:
            self.view.sel().clear()
            self.view.sel().add(sublime.Region(point))
            self.view.sel().clear()
            self.view.sel().add(sublime.Region(point))
