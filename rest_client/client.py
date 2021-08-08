import certifi
import urllib3

from .request import Request

http = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=certifi.where())


def request(request: Request):
    print(f"Requesting {request.method} {request.url}")
    response = http.request(request.method, request.url)
    return response.status, response.headers, response.data.decode("utf-8")
