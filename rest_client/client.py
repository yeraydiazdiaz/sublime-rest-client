from dataclasses import dataclass
from typing import Dict

import certifi  # type: ignore
import urllib3

from .request import Request

http = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=certifi.where())


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
