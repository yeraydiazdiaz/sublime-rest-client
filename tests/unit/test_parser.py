import pytest

from rest_client import Request, parser


def test_single_line_no_method() -> None:
    contents = "https://example.com"

    req = parser.parse(contents, 0)

    assert req == Request(url="https://example.com")


def test_single_line_method() -> None:
    contents = "POST https://example.org"

    req = parser.parse(contents, 0)

    assert req == Request(url="https://example.org", method="POST")


@pytest.mark.parametrize("sep", ("\n", "\r\n"))
@pytest.mark.parametrize(
    "pos,expected_request",
    [
        (5, Request(url="https://example.org", method="POST")),
        (32, Request(url="https://example.com", method="GET")),
        (60, Request(url="https://another-example.com", method="GET")),
    ],
)
def test_multiple_lines(pos: int, expected_request: Request, sep: str) -> None:
    contents = "\n".join(
        [
            "POST https://example.org",
            "###",
            "\n",
            "https://example.com",
            "###",
            "\n",
            "https://another-example.com",
        ]
    )

    req = parser.parse(contents, pos)

    assert req == expected_request


@pytest.mark.parametrize("sep", ("\n", "\r\n"))
def test_query_args_on_same_line(sep: str) -> None:
    contents = sep.join(
        [
            "https://example.org?foo=bar&fizz=buzz",
        ]
    )

    req = parser.parse(contents, 0)

    assert req == Request(url="https://example.org?foo=bar&fizz=buzz")


@pytest.mark.parametrize("sep", ("\n", "\r\n"))
def test_query_args_on_following_line(sep: str) -> None:
    contents = sep.join(
        [
            "https://example.org",
            "    ?foo=bar",
            "    &fizz=buzz",
        ]
    )

    req = parser.parse(contents, 0)

    assert req == Request(url="https://example.org?foo=bar&fizz=buzz")


@pytest.mark.parametrize("sep", ("\n", "\r\n"))
def test_query_args_must_be_indented(sep: str) -> None:
    contents = sep.join(
        [
            "https://example.org",
            "?foo=bar",
            "&fizz=buzz",
        ]
    )

    with pytest.raises(parser.ParserError):
        _ = parser.parse(contents, 0)


@pytest.mark.parametrize("sep", ("\n", "\r\n"))
def test_headers(sep: str) -> None:
    contents = sep.join(
        [
            "https://example.org",
            "  ?foo=bar",
            "  &fizz=buzz",
            "content-type: application/json",
            "authentication: bearer abc:123",
        ]
    )

    req = parser.parse(contents, 0)

    assert req == Request(
        url="https://example.org?foo=bar&fizz=buzz",
        headers={
            "authentication": "bearer abc:123",
            "content-type": "application/json",
        },
    )


@pytest.mark.parametrize("sep", ("\n", "\r\n"))
def test_headers_must_not_be_mixed_with_query_params(sep: str) -> None:
    contents = sep.join(
        [
            "https://example.org",
            "  ?foo=bar",
            "content-type: application/json",
            "  &fizz=buzz",
            "authentication: bearer 123",
        ]
    )

    with pytest.raises(parser.ParserError):
        _ = parser.parse(contents, 0)


@pytest.mark.parametrize("sep", ("\n", "\r\n"))
def test_variable_substitution(sep: str) -> None:
    contents = sep.join(
        [
            "@token = 1234",
            "@foo=bar",
            "https://example.org",
            "  ?foo={{foo}}",
            "content-type: application/json",
            "authentication: bearer {{token}}",
        ]
    )

    req = parser.parse(contents, 0)

    assert req == Request(
        url="https://example.org?foo=bar",
        headers={"authentication": "bearer 1234", "content-type": "application/json"},
    )


@pytest.mark.parametrize("sep", ("\n", "\r\n"))
def test_variable_substitution_last_name_is_used(sep: str) -> None:
    contents = sep.join(
        [
            "@token = 1234",
            "@foo=bar",
            "@token = 4567",
            "# a comment",
            "https://example.org",
            "  ?foo={{foo}}",
            "content-type: application/json",
            "authentication: bearer {{token}}",
        ]
    )

    req = parser.parse(contents, 0)

    assert req == Request(
        url="https://example.org?foo=bar",
        headers={"authentication": "bearer 4567", "content-type": "application/json"},
    )
