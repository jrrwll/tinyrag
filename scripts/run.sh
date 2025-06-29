#!/usr/bin/env bash

set -e
set -x

uv run uvicorn app.main:app --reload --host 0.0.0.0 --log-level debug
