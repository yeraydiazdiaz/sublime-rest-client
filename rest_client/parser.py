import re
import typing as tp

from .request import Request

BOUNDARY = "###"

VARIABLES_RE = re.compile(r"^@(\w+)\s*=\s*(.+)$", re.MULTILINE)


class ParserError(Exception):
    pass


def parse(contents: str, pos: int) -> Request:
    """
    Constructs a Request object from the contents of the view and the position
    of the cursor in it.

    Query params can be set on the same line as the method and URL or in the
    lines immediately following if they are indented.

    Request headers can be set after the initial method, URL and query params block.

    The request body can be defined by leaving a blank line after the first
    URL and headers block. Note a Content-Type header must but defined.

    Example:

    POST https://httpbin.org
      ?foo=bar
      &bar=baz
    Authentication: Bearer some-JWT-token
    Content-Type: application/json

    {
        "key": "value",
        "payload": true
    }

    """
    try:
        variables = _get_variables(contents)
        block = _get_request_block(contents, pos)
        block = _apply_variable_substitution(block, variables)
        return _parse_request_block(block)
    except ValueError as exc:
        raise ParserError("Error parsing request block") from exc


def _get_variables(contents: str) -> tp.Mapping[str, str]:
    return {name: value for name, value in VARIABLES_RE.findall(contents)}


def _get_request_block(contents: str, pos: int) -> str:
    top = contents.rfind(BOUNDARY, 0, pos)
    bottom = contents.find(BOUNDARY, pos)
    start = top if top != -1 else 0
    end = bottom if bottom != -1 else None
    block = contents[start:end].strip()
    lines = (
        line
        for line in block.splitlines()
        if not (line.startswith("#") or line.startswith("@"))
    )
    return "\n".join(lines).strip()


def _parse_request_block(block: str) -> Request:
    [url_section, *body_section] = block.split("\n\n", 2)
    method, url, headers = _parse_url_section(url_section)
    body = body_section[0] if body_section else None
    return Request(url=url, method=method, headers=headers, body=body)


def _parse_url_section(
    url_section: str,
) -> tp.Tuple[str, str, tp.Optional[tp.Mapping[str, str]]]:
    method = "GET"
    headers = None
    [url, *query_params_header_lines] = url_section.splitlines()
    if " " in url:
        method, url = url.split(maxsplit=2)

    header_lines: tp.List[str] = []
    for line in query_params_header_lines:
        if line.startswith(" ") or line.startswith("\t"):
            if not header_lines:
                url += line.strip()
            else:
                raise ParserError("Query parameter lines must follow the URL line")
        else:
            header_lines.append(line)

    headers = _parse_headers_section(header_lines)

    return method, url, headers


def _parse_headers_section(
    headers_section: tp.List[str],
) -> tp.Optional[tp.Mapping[str, str]]:
    headers = {}
    for line in headers_section:
        key, value = line.split(":", maxsplit=2)
        headers[key.strip()] = value.strip()

    return headers if headers else None


def _apply_variable_substitution(block: str, variables: tp.Mapping[str, str]):
    for name, value in variables.items():
        block = block.replace("{{%s}}" % name, value)
    return block
