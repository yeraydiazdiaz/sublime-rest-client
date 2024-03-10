# Changelog

## 1.0.0 (2024-03-10)

- Add option to format JSON responses based on settings:
  + If `format_json` is set to `true`, responses with a Content-Type header including
  `application/json` will be formatted.
  + `format_json_indent` controls the number of spaces per indentation level,
  + Set `format_json_sort_keys` to `true` to sort the keys in alphabetical order.

## 0.2.2 (2023-10-15)

- Show message on status bar when an error occurs during parsing of a request block.
- Fix incorrectly parsing headers whose value includes a colon.

## 0.2.1 (2023-08-18)

- Upgrade urllib3 to 2.0.4

## 0.2.0 (2022-07-19)

- Upgrade urllib3 to 1.26.10
- Encode payload as UTF-8: urllib3 will default to encoding payloads as latin-1,
when the payload has characters out of the range urllib3
will raise an error. Encode the payload as utf-8 as suggested.
- Show errors on new tab: Previously errors would print a message to the status bar and
the traceback to the developer console, now message and traceback are printed to a new
tab.

## 0.1.0 (2022-05-04)

- Initial release
