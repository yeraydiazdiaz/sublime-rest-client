import os.path
import sys

# Import dependencies
sys.path.append(os.path.dirname(__file__) + "/deps")

import sublime
import sublime_plugin

from .sublime_rest import client, parser


class RestRequestCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def run(self, *args) -> None:
        print("Running Sublime REST", args)
        self.request_view = self.window.active_view()

        request_text = self.get_request_text_from_selection()
        if request_text == "":
            self.log_to_status("Invalid request text: `{}`".format(request_text))
            return

        self.log_to_status("Sending request for: `{}`".format(request_text))
        status, _headers, body = client.request(request_text)
        response_view = self.window.new_file()
        response_view.run_command(
            "rest_replace_view_text", {"text": "\n".join([str(status), body])}
        )
        self.log_to_status(status)

    def log_to_status(self, msg: str) -> None:
        """Displays the message in the status bar of the view."""
        self.request_view.set_status("rest", "REST: {}".format(msg))

    def get_request_text_from_selection(self) -> str:
        """Expands the selection to the boundaries of the request."""
        # TODO: this is more an exercise of how to retrieve selections of text
        # in sublime, but we probably will have to take the whole view soon
        selections = self.request_view.sel()
        pos = self.request_view.rowcol(selections[0].a)
        contents = self.view.substr(sublime.Region(0, self.view.size()))
        return contents, pos


class RestReplaceViewTextCommand(sublime_plugin.TextCommand):
    """Replaces the text in a view.

    Usage:
    >>> view.run_command("rest_replace_view_text", {"text": "Hello, World!"})

    """

    def run(self, edit, text, point=None):
        self.view.erase(edit, sublime.Region(0, self.view.size()))
        self.view.insert(edit, 0, text)
        if point is not None:
            self.view.sel().clear()
            self.view.sel().add(sublime.Region(point))
