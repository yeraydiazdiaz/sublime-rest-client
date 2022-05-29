import json
from typing import Dict, Tuple, Union

import sublime


def set_text_on_view(view: sublime.View, string: str) -> None:
    view.run_command("insert", {"characters": string})


def get_row_from_view(view: sublime.View, row: int) -> str:
    return view.substr(view.line(view.text_point(row, 0)))


def get_contents_of_view(view: sublime.View) -> str:
    return view.substr(sublime.Region(0, view.size()))


def parse_response(
    response_text: str, parse_json: bool = True
) -> Tuple[str, Dict, Union[Dict, str]]:
    status, headers, body = response_text.split("\n\n")
    headers_dict = {}
    for header in headers.split("\n"):
        k, v = header.split(": ")
        headers_dict[k] = v

    body = json.loads(body) if parse_json else body
    return status, headers_dict, body
