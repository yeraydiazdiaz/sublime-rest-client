from sublime_rest import Request, client


def test_request(httpserver):
    httpserver.expect_request("/").respond_with_json({"foo": "bar"})
    req = Request(url=httpserver.url_for("/"))
    assert client.request(req)
