import json

from rest_client import Request, client
from pytest_httpserver import HTTPServer


def test_request(httpserver: HTTPServer) -> None:
    headers = {"Content-Type": "application/json"}
    body = {"hello": "world"}
    response_body = {"hello": "back"}
    httpserver.expect_request("/", headers=headers, json=body).respond_with_json(
        response_body
    )

    req = Request(url=httpserver.url_for("/"), headers=headers, body=json.dumps(body))
    response = client.request(req)

    assert response.status == 200
    assert json.loads(response.data) == response_body
