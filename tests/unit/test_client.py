import json
import os

import pytest
from pytest_httpserver import HTTPServer
import urllib3

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
    client.manager.configure({})
    response = client.request(req)

    assert response.status == 200
    assert json.loads(response.data) == response_body


def test_manager_configure_with_no_hosts() -> None:
    client.manager.configure({})
    assert client.manager.pools_per_host == {}


@pytest.mark.parametrize("env_var_or_setting", ("ENV_VAR", "SETTING", None))
def test_manager_configure_with_proxy(env_var_or_setting: str) -> None:
    if env_var_or_setting == "ENV_VAR":
        os.environ["HTTP_PROXY"] = "http://localhost:3128"
        client.manager.configure({})
        assert isinstance(client.manager.default_pool, urllib3.ProxyManager)
    elif env_var_or_setting == "SETTING":
        client.manager.configure({"proxy_url": "http://localhost:3128"})
        assert isinstance(client.manager.default_pool, urllib3.ProxyManager)
    else:
        client.manager.configure({"proxy_url": "http://localhost:3128"})
        assert isinstance(client.manager.default_pool, urllib3.PoolManager)


def test_manager_configure_creates_connection_pools() -> None:
    client.manager.configure(
        {"host_settings": {"localhost:8080": {"disable_ssl_validation": True}}}
    )
    pool = client.manager.pools_per_host.get("localhost:8080")
    assert pool is not None
    assert pool.host == "localhost"
    assert pool.port == 8080
    assert pool.cert_reqs == "CERT_NONE"
