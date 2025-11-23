#!/usr/bin/env bash

set -e
set -x

# pyrefly check --summarize-errors
mypy app
ruff check app --fix
ruff format app
