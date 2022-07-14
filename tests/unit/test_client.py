import json

from pytest_httpserver import HTTPServer

from rest_client import Request, client


def test_request(httpserver: HTTPServer) -> None:
    headers = {"Content-Type": "application/json"}
    body = '{"hello": "world", "utf8": "is 🚀"}'
    response_body = {"hello": "back"}
    httpserver.expect_request("/", headers=headers, data=body).respond_with_json(
        response_body
    )

    req = Request(
        method="POST",
        url=httpserver.url_for("/"),
        headers=headers,
        body=body,
    )
    response = client.request(req)

    assert response.status == 200
    assert json.loads(response.data) == response_body
