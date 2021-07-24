import typing as tp

from .request import Request

BOUNDARY = "###"


def parse(contents: str, pos: int) -> Request:
    """
    Constructs a Request object from the contents of the view and the position
    of the cursor in it.

    Query params can be set on the same line as the method and URL or in the
    lines immediatetly following.

    Request headers can be set leaving a blank line after the initial method,
    URL and query params block.

    The request body can be defined by again leaving a blank line after the
    headers block. Note a Content-Type header must but defined.

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
    block = _get_request_block(contents, pos)
    return _parse_request_block(block)


def _get_request_block(contents: str, pos: int) -> str:
    top = contents.find(BOUNDARY, 0, pos)
    bottom = contents.find(BOUNDARY, pos)
    start = top if top != -1 else 0
    end = bottom if bottom != -1 else None
    block = contents[start:end].strip()
    lines = [
        line.strip() for line in block.splitlines() if not line.startswith(BOUNDARY)
    ]
    return "\n".join(lines).strip()


def _parse_request_block(block: str) -> Request:
    [url_section, *sections] = block.split("\n\n", 3)
    method, url = _parse_url_section(url_section)
    request = Request(url=url, method=method)

    if sections:
        headers_section = sections.pop(0)
        headers = _parse_headers_section(headers_section)
        request.headers = headers

    return request


def _parse_url_section(url_section: str) -> tp.Tuple[str, str]:
    method = "GET"
    [url, *query_param_lines] = [line.strip() for line in url_section.splitlines()]
    if " " in url:
        method, url = url.split(maxsplit=2)

    url += "".join(query_param_lines)
    return method, url


def _parse_headers_section(headers_section: str) -> tp.Mapping[str, str]:
    headers = {}
    for line in headers_section.splitlines():
        key, value = line.split(":", maxsplit=2)
        headers[key.strip()] = value.strip()

    return headers
