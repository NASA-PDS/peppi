# Peppi

Access planetary datasets from the Planetary Data System (PDS)


## Prerequisites

- Python 3.13 or newer


## User Quickstart

See https://nasa-pds.github.io/peppi/


### Use as an MCP server with an LLM

#### Claude Desktop

[Model Context Protocol](https://modelcontextprotocol.io/docs/getting-started/intro) (MCP) servers enable natural language–based tools (such as [Claude Desktop](https://claude.ai/)) to interact with the PDS Registry through Peppi.

Two commands enable the connection of AI apps with Peppi using the Model Context Protocol (MCP) using the MCP `stdio` transport:

- `pds-peppi-qb-mcp` — a comprehensive MCP server that supports a wide range of query types for accessing PDS data using the Peppi "Query Builder" (QB)
- `pds-peppi-mcp-server` — a proof-of-concept MCP server that provides access to a limited subset of Peppi features (such as searches for instrument hosts and targets). It reuses the docstrings from Peppi methods, which reduces the integration overhead for each method.

Select one command and connect it to your LLM (such as Claude Desktop), for example, as described in [these instructions](https://modelcontextprotocol.io/quickstart/user#installing-the-filesystem-server); for example to connect `pds-peppi-qb-mcp` to Claude Desktop, use a configuration similar to the following:
```json
    {
      "mcpServers": {
        "pds_peppi": {
          "command": "{whereever the package is installed}/bin/pds-peppi-qb-mcp",
          "args": []
         }
      }
    }
```
Once you've started Claude Desktop, you can enter requests like

- "Find Mars data"
- "Find calibrated Mars data"
- "Find Mercury data from the year 2020 only"
- Etc.

👉 **Note:** On macOS, "sandboxing" may interfere with Claude's ability to run either MCP server described above. If Claude's MCP log shows "Operation not permitted", try moving the `peppi` folder or the Python virtual environment to the `$HOME` directory or other location _not_ in `Documents`, `Downloads`, or `Desktop`.


#### Claude code

To use the peppi MCP service with Claude code, you first need to start the MCP server as an HTTP API:

    pds-peppi-qb-mcp --transport http

Then connect it to you claude code configuration, for example for a server started on localhost port 8000, runn the following command:

    claude mcp add --transport http peppi http://127.0.0.1:8000/mcp

Then start your claude session:

    claude

Whenever the PEPPI MCP tool is used, you will get prompted, something like:

`❯ What PDS dataset target the planet Mars ?

⏺ I'll search the Planetary Data System (PDS) for datasets related to Mars.

⏺ peppi - querypdsdata (MCP)(query: "has_target(\"Mars\").as_dataframe(50)")

───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 Tool use

   peppi - querypdsdata(query: "has_target(\"Mars\").as_dataframe(50)") (MCP)
   Query PDS data using natural language.

   This tool allows you to query the Planetary Data System (PDS) using natural language.…

 Do you want to proceed?
 ❯ 1. Yes
   2. Yes, and don't ask again for peppi - querypdsdata commands in /Users/loubrieu/PycharmProjects/updart
   3. No
`
You can say yes to proceed and get the results.

## Code of Conduct

All users and developers of the NASA-PDS software are expected to abide by our [Code of Conduct](https://github.com/NASA-PDS/.github/blob/main/CODE_OF_CONDUCT.md). Please read this to ensure you understand the expectations of our community.


## Development

To develop this project, use your favorite text editor, or an integrated development environment with Python support, such as [PyCharm](https://www.jetbrains.com/pycharm/).


### Contributing

For information on how to contribute to NASA-PDS codebases please take a look at our [Contributing guidelines](https://github.com/NASA-PDS/.github/blob/main/CONTRIBUTING.md).


### Installation

Install in editable mode and with extra developer dependencies into your virtual environment of choice:

    pip install git+https://github.com/NASA-AMMOS/slim-detect-secrets.git@exp
    pip install --editable '.[dev]'

Then, configure the `pre-commit` hooks:

    pre-commit install
    pre-commit install -t pre-push
    pre-commit install -t prepare-commit-msg
    pre-commit install -t commit-msg

These hooks then will check for any future commits that might contain secrets. They also check code formatting, PEP8 compliance, type hints, etc.

👉 **Note:** A one time setup is required both to support `detect-secerts` and in your global Git configuration. See [the wiki entry on Secrets](https://github.com/NASA-PDS/nasa-pds.github.io/wiki/Git-and-Github-Guide#detect-secrets) to learn how.


### Tests

This section describes testing for your package.

A complete "build" including test execution, linting (`mypy`, `black`, `flake8`, etc.), and documentation build is executed via:

    tox


## Build

    pip install build
    python3 -m build .


## Publication

NASA PDS packages can publish automatically using the [Roundup Action](https://github.com/NASA-PDS/roundup-action), which leverages GitHub Actions to perform automated continuous integration and continuous delivery. A default workflow that includes the Roundup is provided in the `.github/workflows/unstable-cicd.yaml` file. (Unstable here means an interim release.)


### Manual Publication

Create the package:

    python3 -m build .

Publish it as a Github release.

Publish on PyPI (you need a PyPI account and configure `$HOME/.pypirc`):

    pip install twine
    twine upload dist/*

Or publish on the Test PyPI (you need a Test PyPI account and configure `$HOME/.pypirc`):

    pip install twine
    twine upload --repository testpypi dist/*
