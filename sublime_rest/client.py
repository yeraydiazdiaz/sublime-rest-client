import certifi
import urllib3

http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())


def request(url):
    method, url = url.split()
    print("Requesting {} {}".format(method, url))
    response = http.request(method, url)
    return response.status, response.headers, response.data.decode("utf-8")
