# Sublime REST

An HTTP REST client plugin for Sublime Text 4 inspired by the amazing
[REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)
extension for VSCode.

## Development

1. Install the plugin creating a symlink in
$HOME/Library/Application Support/Sublime Text 3/Packages
to the root of this repo.

1. Run the `REST: Send request` command, or via the console
`window.run_command("rest_request")`

To start developing:

1. Install Python 3.8.8 which is the version in ST4 we use
1. Create a virtual environment and activate it
  - Note: using pyenv-virtualenv creates a `.python-version` file which conflicts
  with Sublime Text and causes it to ignore the plugin completely, a work around
  is to create a virtual environment normally and create a symlink in
  `.pyenv/versions` with the name `3.8`
1. `make install-dev`
1. Install [`direnv`](https://direnv.net/) and run `direnv allow` to add the
`PYTHONPATH` appropriately.
  - This is a work around to packaging `sublime_rest` as it there can only be
  one Python file at the root of plugins.

The plugin vendors [urllib3](https://urllib3.readthedocs.io/en/latest/) and makes
use of [certifi](https://pypi.org/project/certifi/) which is bundled with Sublime
Text.

To update the version of `urllib3` edit `main.txt` and run `make upgrade-deps`.

## Alternatives

https://packagecontrol.io/search/http

