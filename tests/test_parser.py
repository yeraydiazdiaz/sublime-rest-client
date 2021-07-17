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


@pytest.mark.parametrize("sep", ("\n", "\r\n"))
@pytest.mark.parametrize("pos,expected_request", [
    (5, Request(url="https://example.org", method="POST")),
    (32, Request(url="https://example.com", method="GET")),
])
def test_multiple_lines(pos, expected_request, sep):
    contents = "\n".join([
        "POST https://example.org",
        "###",
        "https://example.com",
    ])

    req = parser.parse(contents, pos)

    assert req == expected_request


def test_query_args_on_same_line():
    contents = "\n".join([
        "https://example.org?foo=bar&fizz=buzz",
    ])

    req = parser.parse(contents, 0)

    assert req == Request(url="https://example.org?foo=bar&fizz=buzz")


@pytest.mark.parametrize("sep", ("\n", "\r\n"))
def test_query_args_on_following_line(sep):
    contents = sep.join([
        "https://example.org",
        "    ?foo=bar",
        "    &fizz=buzz",
    ])

    req = parser.parse(contents, 0)

    assert req == Request(url="https://example.org?foo=bar&fizz=buzz")


@pytest.mark.parametrize("sep", ("\n", "\r\n"))
def test_headers(sep):
    contents = sep.join([
        "https://example.org",
        "?foo=bar",
        "&fizz=buzz",
        "",
        "content-type: application/json",
        "authentication: bearer 123",
    ])

    req = parser.parse(contents, 0)

    assert req == Request(
        url="https://example.org?foo=bar&fizz=buzz",
        headers={"authentication": "bearer 123", "content-type": "application/json"}
    )
