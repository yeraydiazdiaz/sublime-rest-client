import certifi
import urllib3

from sublime_rest import Request

http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())


def request(request: Request):
    print("Requesting {} {}".format(request.method, request.url))
    response = http.request(request.method, request.url)
    return response.status, response.headers, response.data.decode("utf-8")
