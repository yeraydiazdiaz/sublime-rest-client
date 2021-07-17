
from sublime_rest import Request

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
    method = "GET"
    url = block
    if " " in url:
        method, url = block.split()
    url = url.replace("\n", "")
    return Request(url=url, method=method)


def _get_request_block(contents: str, pos: int) -> str:
    top = contents.find(BOUNDARY, 0, pos)
    bottom = contents.find(BOUNDARY, pos)
    start = top if top != -1 else 0
    end = bottom if bottom != -1 else None
    block = contents[start:end].strip()

    lines = [line for line in block.splitlines() if not line.startswith(BOUNDARY)]
    return "\n".join(lines)
