from sublime_rest import client


def test_request(httpserver):
    httpserver.expect_request("/").respond_with_json({"foo": "bar"})
    assert client.request(httpserver.url_for("/"))
