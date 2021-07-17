from sublime_rest import Request

BOUNDARY = "###"


def parse(contents: str, pos: int) -> Request:
    block = _get_request_block(contents, pos)
    method = "GET"
    url = block
    if " " in url:
        method, url = block.split()
    return Request(url=url, method=method)


def _get_request_block(contents: str, pos: int) -> str:
    top = contents.find(BOUNDARY, 0, pos)
    bottom = contents.find(BOUNDARY, pos)
    start = top if top != -1 else 0
    end = bottom if bottom != -1 else None
    block = contents[start:end].strip()
    if block.startswith(BOUNDARY):
        block = block[block.rfind("\n") + 1:]
    return block
