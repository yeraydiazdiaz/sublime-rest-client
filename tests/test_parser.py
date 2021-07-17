from sublime_rest import Request, parser


def test_single_line():
    contents = "https://example.com"
    pos = (0, 0)

    req = parser.parse(contents, pos)

    assert req == Request(url="https://example.com")
