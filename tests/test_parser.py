import pytest

from sublime_rest import Request, parser


def test_single_line_no_method():
    contents = "https://example.com"

    req = parser.parse(contents, 0)

    assert req == Request(url="https://example.com")


def test_single_line_method():
    contents = "POST https://example.org"

    req = parser.parse(contents, 0)

    assert req == Request(url="https://example.org", method="POST")


@pytest.mark.parametrize("pos,expected_request", [
    (5, Request(url="https://example.org", method="POST")),
    (32, Request(url="https://example.com", method="GET")),
])
def test_multiple_lines(pos, expected_request):
    contents = "\n".join([
        "POST https://example.org",
        "###",
        "https://example.com",
    ])

    req = parser.parse(contents, pos)

    assert req == expected_request
