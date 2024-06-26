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


def test_manager_configure_with_no_hosts() -> None:
    client.manager.configure({})
    assert client.manager.pools_per_host == {}


def test_manager_configure_creates_connection_pools() -> None:
    client.manager.configure(
        {"host_settings": {"localhost:8080": {"disable_ssl_validation": True}}}
    )
    pool = client.manager.pools_per_host.get("localhost:8080")
    assert pool is not None
    assert pool.host == "localhost"
    assert pool.port == 8080
    assert pool.cert_reqs == "CERT_NONE"
