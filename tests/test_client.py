import json

from rest_client import Request, client


def test_request(httpserver):
    headers = {"Content-Type": "application/json"}
    body = {"hello": "world"}
    response_body = {"hello": "back"}
    httpserver.expect_request("/", headers=headers, json=body).respond_with_json(
        response_body
    )

    req = Request(url=httpserver.url_for("/"), headers=headers, body=json.dumps(body))
    status_code, _, body = client.request(req)

    assert status_code == 200
    assert json.loads(body) == response_body
