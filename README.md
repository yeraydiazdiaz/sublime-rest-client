# Sublime REST Client

An HTTP client plugin for Sublime Text 4 inspired by the amazing
[REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)
extension for VSCode.

Sublime REST Client vendors the excellent
[urllib3](https://urllib3.readthedocs.io/en/latest/) and uses
[certifi](https://pypi.org/project/certifi/) which is bundled with Sublime
Text 4 to ensure secure HTTP requests.

This project is considered **ALPHA** and has only been tested in Mac OS X.

## Installation

Sublime REST Client has not been released to Package Control yet, refer to the
development section below for early testing.

## Usage

Sublime REST Client provides the same simple, declarative way of defining
HTTP requests as REST Client. As simple as:

```
https://httpbin.org/get
```

Invoking "REST: Send request" or using the default keystroke `super+alt+r`
will send the request to the URL and write the response in another tab:

```
GET https://httpbin.org/get 200 OK

Date: Sun, 20 Mar 2022 17:27:11 GMT
Content-Type: application/json
Content-Length: 308
Connection: keep-alive
Server: gunicorn/19.9.0
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true

{
  "args": {},
  "headers": {
    "Accept-Encoding": "identity",
    "Content-Length": "59",
    "Host": "httpbin.org",
    "User-Agent": "python-urllib3/1.26.5",
    "X-Amzn-Trace-Id": "Root=1-623763ef-5339120230225c282d6687b2"
  },
  "origin": "109.181.57.85",
  "url": "https://httpbin.org/get"
}
```

### Query parameters

Query parameters can be added as usual in the first line of the request definition:

```
GET https://httpbin.org/get?hello=world
```

Or the subsequent lines with an indentation:

```
GET https://httpbin.org/get
  ?hello=world
  &client=sublime
```

### Request headers

Request definitions may include the HTTP method and request headers:

```
GET https://httpbin.org/get
user-agent: sublime rest client
```

Which will produce:

```
GET https://httpbin.org/get 200 OK

Date: Sun, 20 Mar 2022 17:35:23 GMT
Content-Type: application/json
Content-Length: 277
Connection: keep-alive
Server: gunicorn/19.9.0
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true

{
  "args": {},
  "headers": {
    "Accept-Encoding": "identity",
    "Host": "httpbin.org",
    "User-Agent": "sublime rest client",
    "X-Amzn-Trace-Id": "Root=1-623765db-0ff407a42748a89733c96bbb"
  },
  "origin": "109.181.57.85",
  "url": "https://httpbin.org/get"
}
```

Request may also include a payload:

```
POST https://httpbin.org/post
content-type: application/json

{
  "hello": "world!"
}
```

And its response:

```
POST https://httpbin.org/post 200 OK

Date: Sun, 20 Mar 2022 17:34:14 GMT
Content-Type: application/json
Content-Length: 465
Connection: keep-alive
Server: gunicorn/19.9.0
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true

{
  "args": {},
  "data": "{\n  \"hello\": \"world!\"\n}",
  "files": {},
  "form": {},
  "headers": {
    "Accept-Encoding": "identity",
    "Content-Length": "23",
    "Content-Type": "application/json",
    "Host": "httpbin.org",
    "User-Agent": "python-urllib3/1.26.5",
    "X-Amzn-Trace-Id": "Root=1-62376596-3d6be5d11f9dd27b26e7a27e"
  },
  "json": {
    "hello": "world!"
  },
  "origin": "109.181.57.85",
  "url": "https://httpbin.org/post"
}
```

### Multiple request files

A single `.rest` file can contain multiple request definitions but they must
be separated by lines starting with `###`, for example:

```
GET https://httpbin.org/get
user-agent: sublime rest client

### maybe some description

POST https://httpbin.org/post
content-type: application/json

{
  "hello": "world!"
}
```

When invoking "Send Request", Sublime REST Client will detect the request definition
the cursor is currently on and send it.

### Variable substitution

It's common to define several requests that make use of the same piece of information,
for example, a JWT token that must be sent on all requests. To avoid having to
duplicate the token on all definitions you can define variables using `@name = value`
and make use of them in the request definitions with `{{name}}`:

```
@token = ABC123

GET https://httpbin.org/get
Authorization: Bearer {{token}}
```

## Development

1. Install the plugin creating a symlink in
$HOME/Library/Application Support/Sublime Text 3/Packages
to the root of this repo.

1. Run the `REST: Send request` command, or via the console
`window.run_command("rest_request")`

To start developing:

1. Install Python 3.8.8 which is the version embedded in ST4
1. Create a virtual environment and activate it
  - Note: if you use pyenv note it relies on a `.python-version` file, which
  Sublime Text also uses with different contents and will cause it to ignore
  the plugin completely. A work around is to create a virtual environment
  normally and create a symlink in `.pyenv/versions` with the name `3.8`.
1. `make install-dev`
1. Install [`direnv`](https://direnv.net/) and run `direnv allow` to add the
`PYTHONPATH` appropriately.
  - This is a work around to packaging `sublime_rest` as it there can only be
  one Python file at the root of plugins.

To update the version of `urllib3` edit `main.txt` and run `make upgrade-deps`.

## Alternatives

[RESTer HTTP Client](https://github.com/pjdietz/rester-sublime-http-client) has
the same philosophy as REST Client, however, its development seems
to have stopped several years ago and thus does not target Sublime Text 4.
Its code also uses the standard library for most of the HTTP request heavy
lifting which seemed unnecessary and a potential security issue when `urllib3`
exists.

There are [other HTTP clients for Sublime Text](https://packagecontrol.io/search/http),
many of which are better maintained and featureful, but don't follow the same
simple, declarative philosophy of REST Client.
