# pnogo_api

Pnogo API

## Requirements

This project uses [uv](https://github.com/astral-sh/uv) to handle dependencies. To install them in a virtual environment, simply run:

```bash
uv sync
```

## Usage

To start the API run this command:

```bash
uv run -m flask --app pnogo_api/run run --debug
```

## Style

This project uses [ruff](https://github.com/astral-sh/ruff) for code formatting, and it's installed in the virtual environment automatically. 

To format your code, simply run:

```bash
ruff format
```

To run the linter for any errors or issues:

```bash
ruff check
```
