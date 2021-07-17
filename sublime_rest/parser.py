from sublime_rest import Request


def parse(contents, pos):
    row, col = pos
    return Request("https://example.com")
