from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

import certifi  # type: ignore
import urllib3

from .request import Request


class Manager:
    _default_pool: Optional[urllib3.PoolManager] = None
    pools_per_host: Dict[str, urllib3.HTTPSConnectionPool] = {}

    def __init__(self) -> None:
        self._default_pool = urllib3.PoolManager(
            cert_reqs="CERT_REQUIRED", ca_certs=certifi.where()
        )

    @property
    def default_pool(self) -> urllib3.PoolManager:
        assert (
            self._default_pool is not None
        ), "Attempted to access default pool before initialization"
        return self._default_pool

    def configure(self, settings: Dict[str, Any]) -> None:
        for host_with_port, host_settings in settings.get("host_settings", {}).items():
            kwargs = self._settings_to_kw(host_settings)
            host = host_with_port
            port = None
            if ":" in host_with_port:
                host, port = host_with_port.split(":", maxsplit=1)

            self.pools_per_host[host_with_port] = urllib3.HTTPSConnectionPool(
                host, int(port) if port is not None else None, **kwargs
            )

    def get_pool(
        self, host: str
    ) -> Union[urllib3.HTTPSConnectionPool, urllib3.PoolManager]:
        pool = self.pools_per_host.get(host)
        return pool if pool is not None else self.default_pool

    def _settings_to_kw(self, host_settings: Dict[str, Any]) -> Dict[str, Any]:
        kwargs = {}
        for setting, value in host_settings.items():
            if setting == "disable_ssl_validation" and value:
                kwargs["cert_reqs"] = "CERT_NONE"
        return kwargs


@dataclass
class Response:
    status: int
    headers: Dict[str, str]
    data: str


def request(request: Request) -> Response:
    print(f"Requesting {request.method} {request.url}: {request.body}")
    pool = manager.get_pool(request.host)
    response = pool.request(
        request.method,
        request.url,
        headers=request.headers,
        body=request.body.encode("utf-8") if request.body is not None else None,
    )
    return Response(
        status=response.status,
        headers=dict(response.headers),
        data=response.data.decode("utf-8"),
    )


manager = Manager()
