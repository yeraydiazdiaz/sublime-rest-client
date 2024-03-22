from dataclasses import dataclass
from typing import Dict
from threading import Lock

import certifi  # type: ignore
import urllib3

from .request import Request

http = None
http_pool_lock = Lock()
ssl_disabled = False


def setup(settings):
    global http
    global http_pool_lock
    global ssl_disabled
    with http_pool_lock:
        disable_ssl = settings.get("disable_ssl_validation")
        if http is None or disable_ssl != ssl_disabled:
            http = urllib3.PoolManager(
                cert_reqs="CERT_NONE" if disable_ssl else "CERT_REQUIRED",
                ca_certs=certifi.where()
            )
            ssl_disabled = disable_ssl


def get_request_pool() -> urllib3.PoolManager:
    global http
    global http_pool_lock
    with http_pool_lock:
        if http is None:
            raise Exception("no http pool configured")
        return http


@dataclass
class Response:
    status: int
    headers: Dict[str, str]
    data: str


def request(request: Request) -> Response:
    print(f"Requesting {request.method} {request.url}: {request.body}")
    response = http.request(
        request.method,
        request.url,
        headers=request.headers,
        body=request.body.encode("utf-8") if request.body is not None else None,
    )
    return Response(
        status=response.status,
        headers=response.headers,
        data=response.data.decode("utf-8"),
    )
